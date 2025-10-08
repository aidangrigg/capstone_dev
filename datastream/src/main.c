#include <getopt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "datasources/file_datasource.h"
#include "datasources/unicorn_datasource.h"

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
static struct option long_options[] = {{"input", required_argument, NULL, 'i'},
                                       {"output", required_argument, NULL, 'o'},
                                       {"device", required_argument, NULL, 'd'},
                                       {"test_signal", no_argument, NULL, 't'},
                                       {"help", no_argument, NULL, 'h'},
                                       {NULL, 0, NULL, 0}};

int main(int argc, char *argv[]) {
  char ch;
  Options opt = DEFAULT_OPTIONS;
  while ((ch = getopt_long(argc, argv, short_options, long_options, NULL)) !=
         -1) {
    switch (ch) {
    case 't':
      opt.test_signal = true;
      break;
    case 'h':
      // TODO: proper help message
      printf("I'm helping!\n");
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

  printf("input: %s, output: %s\n", opt.input, opt.output);
  DataSource *source = malloc(sizeof(DataSource));
  if (strcmp(opt.input, "") != 0) {
    if (create_file_source(source, opt.input) != 0) {
      return 1;
    }
  } else {
    if (create_unicorn_source(source, opt.device, opt.test_signal,
                              opt.output) != 0) {
      return 1;
    }
  }

  for (int n = 0; n < 100 && source->next(source->context) == 0; n++) {
    for (size_t i = 0; i < source->buffer_len; i++) {
      printf("%f,", source->buffer[i]);
    }
    printf("\n");
  }

  printf("End of file reached!\n");

  source->close(source->context);
  return 0;
}
