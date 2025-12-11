cmake_minimum_required(VERSION 3.10)
project(ManualDigitRecognizer)

set(CMAKE_CXX_STANDARD 17)

find_package(Threads REQUIRED)

include_directories(src)

# 只编译 main 和 neural_net
add_executable(server src/main.cpp src/neural_net.cpp)
target_link_libraries(server Threads::Threads)