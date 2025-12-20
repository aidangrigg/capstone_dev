#include "file_datasource.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int read_from_file(void *ctx) {
  FileContext *context = (FileContext *)ctx;

  usleep(4000); // TODO: send data at specific frequency

  const size_t ret_code = fread(context->buffer, sizeof(float), context->buffer_len, context->fptr);

  if (ret_code == context->buffer_len) {
    return 0;
  } else if (feof(context->fptr)) {
    printf("Seeking to begining of file\n");
    fseek(context->fptr, sizeof(int), SEEK_SET);
    return 0;
  } else {
    printf("An error has occured! %zu bytes read from file when %zu should have been.\n", ret_code,
           context->buffer_len);
    return 1;
  }
}

void close_file(void *ctx) {
  FileContext *context = (FileContext *)ctx;
  fclose(context->fptr);
  free(context->buffer);
  free(context);
}

// TODO: Handle errors
int create_file_source(DataSource *source, char *filename) {
  FILE *fptr = fopen(filename, "rb");

  if (fptr == NULL) {
    printf("Could not open file \"%s\"\n", filename);
    return 1;
  }

  int buff_len;
  if (fread(&buff_len, sizeof(int), 1, fptr) != 1) {
    printf("An error occured when trying to read the channel count. Binary "
           "file is malformed.\n");
    return 1;
  }

  printf("Buffer length is %d\n", buff_len);

  float *buffer = malloc(sizeof(float) * buff_len);
  FileContext *ctx = malloc(sizeof(FileContext));
  ctx->fptr = fptr;
  ctx->buffer = buffer;
  ctx->buffer_len = buff_len;

  source->context = ctx;
  source->buffer = buffer;
  source->buffer_len = buff_len;
  source->next = read_from_file;
  source->close = close_file;
  return 0;
}
