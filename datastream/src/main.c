#include <getopt.h>
#include <lsl_c.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "datasources/file_datasource.h"
#include "datasources/unicorn_datasource.h"
#include "lsl/inlet.h"
#include "unicorn.h"

const char *HELP_STRING = "Usage: unicorn_datastream [options]\n"
                          "Options:\n"
                          "  --help                   Display this information.\n"
                          "  -i, --input <FILE>       Read data from an input file rather than live\n"
                          "                           recording.\n"
                          "  -o, --output <FILE>      If live recording, will save this data to a\n"
                          "                           a binary file. This binary file can be read using\n"
                          "                           `--input`.\n"
                          "  -d, --device <DEVICE_ID> Selects the accompanying unicorn headset.\n"
                          "  -t, --test_signal        If set, will output a square waveform test signal\n"
                          "                           rather than a live measurement.\n";

typedef struct Options {
  char *input;
  char *output;
  int device;
  bool test_signal;
} Options;

const Options DEFAULT_OPTIONS = {
    .input = "data.out",
    .output = "data.out",
    .device = 0,
    .test_signal = false,
};

static char short_options[] = "hti:o:d:";
static struct option long_options[] = {
    {"input", required_argument, NULL, 'i'},  //
    {"output", required_argument, NULL, 'o'}, //
    {"device", required_argument, NULL, 'd'}, //
    {"test_signal", no_argument, NULL, 't'},  //
    {"help", no_argument, NULL, 'h'},         //
    {NULL, 0, NULL, 0},                       //
};

int main(int argc, char *argv[]) {
  char ch;
  Options opt = DEFAULT_OPTIONS;
  while ((ch = getopt_long(argc, argv, short_options, long_options, NULL)) != -1) {
    switch (ch) {
    case 't':
      opt.test_signal = true;
      break;
    case 'h':
      printf("%s", HELP_STRING);
      return 0;
    case 'i':
      opt.input = optarg;
      break;
    case 'o':
      opt.output = optarg;
      break;
    case 'd':
      opt.device = atoi(optarg);
      break;
    }
  }

  // TODO: add arg for live recording
  printf("input: %s, output: %s\n", opt.input, opt.output);
  DataSource *source = malloc(sizeof(DataSource));
  if (strcmp(opt.input, "") != 0) {
    if (create_file_source(source, opt.input) != 0) {
      return 1;
    }
  } else {
    if (create_unicorn_source(source, opt.device, opt.test_signal, opt.output) != 0) {
      return 1;
    }
  }

  printf("Using lsl %d, lsl_library_info: %s\n", lsl_library_version(), lsl_library_info());

  /* declare a new streaminfo (name: SendDataC / argument 1, content type: EEG, 8 channels, 250
   * Hz, float values, some made-up device id (can also be empty) */
  lsl_streaminfo info = lsl_create_streaminfo("unicorn_datastream", "EEG", 8, UNICORN_SAMPLING_RATE, cft_float32, "325wqer4354");

  /* add some meta-data fields to it */
  /* (for more standard fields, see https://github.com/sccn/xdf/wiki/Meta-Data) */
  lsl_xml_ptr desc = lsl_get_desc(info);
  lsl_append_child_value(desc, "manufacturer", "LSL");
  const char *channels[] = {"EEG 1", "EEG 2", "EEG 3", "EEG 4", "EEG 5", "EEG 6", "EEG 7", "EEG 8"};
  lsl_xml_ptr chns = lsl_append_child(desc, "channels");
  for (int c = 0; c < 8; c++) {
    lsl_xml_ptr chn = lsl_append_child(chns, "channel");
    lsl_append_child_value(chn, "label", channels[c]);
    lsl_append_child_value(chn, "unit", "microvolts");
    lsl_append_child_value(chn, "type", "EEG");
  }

  /* make a new outlet (chunking: default, buffering: 360 seconds) */
  lsl_outlet outlet = lsl_create_outlet(info, 0, 360);

  do
    printf("Waiting for consumers\n");
  while (!lsl_wait_for_consumers(outlet, 120));

  printf("Now sending data...\n");

  /* send data until the last consumer has disconnected */
  for (int t = 0; lsl_have_consumers(outlet); t++) {
    if (source->next(source->context) != 0) {
      break;
    }

    lsl_push_sample_f(outlet, source->buffer);
    /* for (int n = 0; n < 100 && source->next(source->context) == 0; n++) { */
    /*   for (size_t i = 0; i < source->buffer_len; i++) { */
    /*     printf("%f,", source->buffer[i]); */
    /*   } */
    /*   printf("\n"); */
    /* } */
    /* float cursample[8]; /\* the current sample *\/ */
    /* cursample[0] = (float)t; */
    /* for (int c = 1; c < 8; c++) */
    /*   cursample[c] = (float)((rand() % 1500) / 500.0 - 1.5); */
  }

  printf("Lost the last consumer, shutting down\n");
  lsl_destroy_outlet(outlet);

  source->close(source->context);
  return 0;

  /* while (source->next(source->context) == 0) { */
  /*   for (size_t i = 0; i < source->buffer_len; i++) { */
  /*     printf("%f,", source->buffer[i]); */
  /*   } */
  /*   printf("\n"); */

  /* } */

  /* source->close(source->context); */
  /* return 0; */
}
