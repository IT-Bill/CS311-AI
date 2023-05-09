cmake_minimum_required(VERSION 3.5)
project(HGA_OCARP)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -O3 -lemon")

set(SOURCE_FILES hga.cpp)
add_executable(HGA_OCARP ${SOURCE_FILES})
