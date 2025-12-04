cmake_minimum_required(VERSION 3.10)
project(DigitRecognizer)

# 设置C++标准
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找OpenCV库
find_package(OpenCV REQUIRED)

# 添加可执行文件
add_executable(opencv_recognizer opencv_recognizer.cpp)

# 链接OpenCV库
target_link_libraries(opencv_recognizer ${OpenCV_LIBS})

# 复制图片到构建目录
configure_file(${CMAKE_SOURCE_DIR}/../drawn_digit.png ${CMAKE_BINARY_DIR}/drawn_digit.png COPYONLY)