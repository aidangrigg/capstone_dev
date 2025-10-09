cmake_minimum_required(VERSION 3.10)
project(unicorn_datastream C CXX)

add_compile_options(-Wall -Wextra)

add_executable(unicorn_datastream
        src/main.c
        src/datasources/unicorn_datasource.c
        src/datasources/file_datasource.c)

target_include_directories(unicorn_datastream PRIVATE ${CMAKE_SOURCE_DIR}/lib)

target_link_libraries(unicorn_datastream
    PRIVATE
    ${CMAKE_SOURCE_DIR}/lib/libunicorn.so
    stdc++ # needed by libunicorn
    bluetooth
    lsl
)
