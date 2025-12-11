// src/mnist_loader.hpp
#pragma once
#include <algorithm>
#include <fstream>
#include <iostream>
#include <vector>

// 字节序转换：大端转小端
uint32_t swap_endian(uint32_t val) {
  val = ((val << 8) & 0xFF00FF00) | ((val >> 8) & 0xFF00FF);
  return (val << 16) | (val >> 16);
}

struct MnistData {
  std::vector<std::vector<double>> images;
  std::vector<int> labels;
  int rows = 0;
  int cols = 0;
};

MnistData load_mnist(const std::string& image_path,
                     const std::string& label_path) {
  MnistData data;

  // 读取 Label
  std::ifstream label_file(label_path, std::ios::binary);
  if (label_file.is_open()) {
    uint32_t magic = 0, num_items = 0;
    label_file.read((char*)&magic, 4);
    label_file.read((char*)&num_items, 4);
    num_items = swap_endian(num_items);

    for (uint32_t i = 0; i < num_items; ++i) {
      uint8_t label;
      label_file.read((char*)&label, 1);
      data.labels.push_back((int)label);
    }
  } else {
    std::cerr << "Cannot open label file: " << label_path << std::endl;
  }

  // 读取 Image
  std::ifstream image_file(image_path, std::ios::binary);
  if (image_file.is_open()) {
    uint32_t magic = 0, num_items = 0, rows = 0, cols = 0;
    image_file.read((char*)&magic, 4);
    image_file.read((char*)&num_items, 4);
    image_file.read((char*)&rows, 4);
    image_file.read((char*)&cols, 4);

    data.rows = swap_endian(rows);
    data.cols = swap_endian(cols);
    num_items = swap_endian(num_items);

    int image_size = data.rows * data.cols;

    for (uint32_t i = 0; i < num_items; ++i) {
      std::vector<uint8_t> buffer(image_size);
      std::vector<double> img_double(image_size);
      image_file.read((char*)buffer.data(), image_size);

      // 归一化 0.0 - 1.0
      for (int j = 0; j < image_size; ++j) {
        img_double[j] = buffer[j] / 255.0;
      }
      data.images.push_back(img_double);
    }
  } else {
    std::cerr << "Cannot open image file: " << image_path << std::endl;
  }
  return data;
}