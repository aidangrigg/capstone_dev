#ifndef _FILE_DATASOURCE_H_
#define _FILE_DATASOURCE_H_

#include "datasource.h"
#include <stdio.h>

typedef struct FileContext {
  FILE *fptr;
  float *buffer;
  size_t buffer_len;
} FileContext;

int read_from_file(void *ctx);
void close_file(void *ctx);
int create_file_source(DataSource *source, char *filename);

#endif /* _FILE_DATASOURCE_H_ */
