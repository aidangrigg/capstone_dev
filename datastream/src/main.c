#include <stdio.h>
#include <stdlib.h>

#include "datasources/file_datasource.h"
#include "datasources/unicorn_datasource.h"

int main() {
  DataSource *source = malloc(sizeof(DataSource));
  if (create_file_source(source, "data.out") != 0) {
    return 1;
  }
  /* if (create_unicorn_source(source, 0, true, "data.out") != 0) { */
  /*   return -1; */
  /* } */

  while (source->next(source->context) == 0) {
    for (size_t i = 0; i < source->buffer_len; i++) {
      printf("%f,", source->buffer[i]);
    }
    printf("\n");
  }
  printf("End of file reached!\n");

  source->close(source->context);

  return 0;
}
