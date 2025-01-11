cmake_minimum_required(VERSION 3.15)

project(textok)

set(CMAKE_CXX_STANDARD 17)

include_directories(${CMAKE_SOURCE_DIR})

add_subdirectory(textok)
add_subdirectory(python)
add_subdirectory(tests/cpp)
