cmake_minimum_required(VERSION 3.10)
project(unicorn_datastream)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_compile_options(-Wall -Wextra)

add_executable(unicorn_datastream src/main.cpp)

target_include_directories(unicorn_datastream PRIVATE ${CMAKE_SOURCE_DIR}/lib)

target_link_libraries(unicorn_datastream
    PRIVATE
    ${CMAKE_SOURCE_DIR}/lib/libunicorn.so
    bluetooth
)
