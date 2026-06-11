#ifndef _DATASOURCE_H_
#define _DATASOURCE_H_

#include <stddef.h>

typedef struct DataSource {
  void *context;
  float *buffer;
  size_t buffer_len;
  int (*next)(void *ctx);
  void (*close)(void *context);
} DataSource;

#endif /* _DATASOURCE_H_ */
