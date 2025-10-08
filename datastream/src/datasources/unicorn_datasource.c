#include "unicorn_datasource.h"
#include "unicorn.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void log_unicorn_error(int error_code);

int read_from_unicorn(void *ctx) {
  UnicornContext *context = (UnicornContext *)ctx;
  int error_code = 0;
  printf("Beginning read...\n");
  error_code = UNICORN_GetData(context->handle, 1, context->buffer,
                               context->buffer_len * sizeof(float));
  if (error_code != 0) {
    log_unicorn_error(error_code);
    return error_code;
  }
  printf("Read successful!\n");

  if (context->fptr != NULL) {
    fwrite(context->buffer, sizeof(float), context->buffer_len, context->fptr);

    /* for (size_t i = 0; i < context->buffer_len; i++) { */
    /*   fprintf(context->fptr, "%f,", context->buffer[i]); */
    /* } */
    /* fprintf(context->fptr, "\n"); */
  }
  return 0;
}

void close_unicorn(void *ctx) {
  UnicornContext *context = (UnicornContext *)ctx;
  int error_code = 0;
  printf("Stopping acquisition & disconnecting from device!\n");
  error_code = UNICORN_StopAcquisition(context->handle);
  if (error_code != 0) {
    log_unicorn_error(error_code);
  }
  error_code = UNICORN_CloseDevice(&context->handle);
  if (error_code != 0) {
    log_unicorn_error(error_code);
  }

  printf("Disconnect successful!\n");

  if (context->fptr != NULL) {
    fclose(context->fptr);
  }

  free(context->buffer);
  free(context);
}

int create_unicorn_source(DataSource *source, int device_selection,
                          bool test_signal, char *filename) {
  int error_code = 0;
  unsigned int available_devices_count = 0;
  printf("Searching for available devices...\n");
  error_code =
      UNICORN_GetAvailableDevices(NULL, &available_devices_count, TRUE);
  if (error_code != 0) {
    log_unicorn_error(error_code);
    return error_code;
  }

  if (available_devices_count <= 0) {
    printf("No available devices found...\n");
    return -1;
  } else {
    printf("%d devices found!\n", available_devices_count);
  }

  UNICORN_DEVICE_SERIAL *available_devices =
      malloc(sizeof(UNICORN_DEVICE_SERIAL) * available_devices_count);
  error_code = UNICORN_GetAvailableDevices(available_devices,
                                           &available_devices_count, true);
  if (error_code != 0) {
    log_unicorn_error(error_code);
    return error_code;
  }

  printf("Connecting to device...\n");
  UNICORN_HANDLE handle;
  error_code = UNICORN_OpenDevice(available_devices[device_selection], &handle);
  if (error_code != 0) {
    log_unicorn_error(error_code);
    return error_code;
  }

  printf("Getting acquired channels...\n");
  unsigned int channels;
  error_code = UNICORN_GetNumberOfAcquiredChannels(handle, &channels);
  if (error_code != 0) {
    log_unicorn_error(error_code);
    return error_code;
  }
  printf("%u channels!\n", channels);

  UNICORN_AMPLIFIER_CONFIGURATION configuration;
  error_code = UNICORN_GetConfiguration(handle, &configuration);
  if (error_code != 0) {
    log_unicorn_error(error_code);
    return error_code;
  }

  printf("Starting acquisition!\n");
  error_code = UNICORN_StartAcquisition(handle, test_signal);
  if (error_code != 0) {
    log_unicorn_error(error_code);
    return error_code;
  }

  UnicornContext *ctx = malloc(sizeof(UnicornContext));
  size_t acquisition_buffer_length = channels;
  float *buffer = malloc(sizeof(float) * acquisition_buffer_length);
  ctx->handle = handle;
  ctx->buffer = buffer;
  ctx->buffer_len = acquisition_buffer_length;
  ctx->fptr = NULL;

  if (strcmp(filename, "") != 0) {
    FILE *fptr = fopen(filename, "wb");
    ctx->fptr = fptr;
    fwrite(&acquisition_buffer_length, sizeof(size_t), 1, fptr); // write the buffer length to the start of the binary file
  }

  source->context = ctx;
  source->buffer = buffer;
  source->buffer_len = acquisition_buffer_length;
  source->next = read_from_unicorn;
  source->close = close_unicorn;
  free(available_devices);
  return 0;
}

void log_unicorn_error(int error_code) {
  switch (error_code) {
  case UNICORN_ERROR_INVALID_PARAMETER:
    printf("One of the specified parameters does not contain a valid value.\n");
    break;
  case UNICORN_ERROR_BLUETOOTH_INIT_FAILED:
    printf("The initialization of the Bluetooth adapter failed.\n");
    break;
  case UNICORN_ERROR_BLUETOOTH_SOCKET_FAILED:
    printf("The operation could not be performed because the Bluetooth socket "
           "failed.\n");
    break;
  case UNICORN_ERROR_OPEN_DEVICE_FAILED:
    printf("The device could not be opened.\n");
    break;
  case UNICORN_ERROR_INVALID_CONFIGURATION:
    printf("The configuration is invalid.\n");
    break;
  case UNICORN_ERROR_BUFFER_OVERFLOW:
    printf("The acquisition buffer is full.\n");
    break;
  case UNICORN_ERROR_BUFFER_UNDERFLOW:
    printf("The acquisition buffer is empty.\n");
    break;
  case UNICORN_ERROR_OPERATION_NOT_ALLOWED:
    printf("The operation is not allowed.\n");
    break;
  case UNICORN_ERROR_INVALID_HANDLE:
    printf("The specified connection handle is invalid.\n");
    break;
  case UNICORN_ERROR_GENERAL_ERROR:
    printf("An unspecified error occurred.\n");
    break;
  }
}
