#ifndef _UNICORN_DATASOURCE_H_
#define _UNICORN_DATASOURCE_H_

#include "datasource.h"
#include "unicorn.h"
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>

typedef struct UnicornContext {
  UNICORN_HANDLE handle;
  FILE *fptr;
  float *buffer;
  size_t buffer_len;
} UnicornContext;

int read_from_unicorn(void *ctx);
void close_unicorn(void *ctx);
int create_unicorn_source(DataSource *source, int device_selection,
                          bool test_signal, char* filename);

#endif /* _UNICORN_DATASOURCE_H_ */
