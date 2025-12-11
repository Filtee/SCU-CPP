// src/main.cpp
#include <iostream>
#include <sstream>
#include <vector>

#include "httplib.h"
#include "mnist_loader.hpp"
#include "neural_net.hpp"
#include "utils.hpp"  // 引入配置工具

int main() {
  // 1. 从环境变量获取配置
  int epochs = Config::getInt("EPOCHS", 10);
  double lr = Config::getDouble("LEARNING_RATE", 0.1);
  int hidden_nodes = Config::getInt("HIDDEN_NODES", 200);
  std::string model_path =
      Config::getString("MODEL_PATH", "/app/data/model.weights");

  std::cout << "Config Loaded: "
            << "Epochs=" << epochs << ", "
            << "LR=" << lr << ", "
            << "Hidden=" << hidden_nodes << std::endl;

  // 2. 初始化神经网络
  // Input=784 (28x28), Output=10
  SimpleNN nn(784, hidden_nodes, 10, lr);

  if (!nn.load(model_path)) {
    std::cout << "Model not found at " << model_path << ". Training..."
              << std::endl;

    auto train_data = load_mnist("/app/data/train-images-idx3-ubyte",
                                 "/app/data/train-labels-idx1-ubyte");

    if (train_data.images.empty()) {
      std::cerr << "Failed to load MNIST data!" << std::endl;
      return 1;
    }

    for (int e = 0; e < epochs; e++) {
      std::cout << "Epoch " << e + 1 << "/" << epochs << "..." << std::endl;
      for (size_t i = 0; i < train_data.images.size(); i++) {
        nn.train(train_data.images[i], train_data.labels[i]);
      }
      // 每个 Epoch 保存一次，防止中断
      nn.save(model_path);
    }
    std::cout << "Training complete." << std::endl;
  } else {
    std::cout << "Model loaded successfully." << std::endl;
  }

  httplib::Server svr;

  // 静态页面
  svr.Get("/", [](const httplib::Request&, httplib::Response& res) {
    std::ifstream t("/app/static/index.html");
    std::stringstream buffer;
    buffer << t.rdbuf();
    res.set_content(buffer.str(), "text/html");
  });

  // 预测接口
  svr.Post("/predict", [&](const httplib::Request& req,
                           httplib::Response& res) {
    // 现在前端会直接发送 28x28 = 784 字节的数据
    if (req.body.size() != 784) {
      res.status = 400;
      res.set_content("Invalid image size. Expected 784 bytes.", "text/plain");
      return;
    }

    // 转换 raw bytes 到 double vector (0.0 - 1.0)
    std::vector<double> input(784);
    for (size_t i = 0; i < 784; i++) {
      unsigned char pixel = req.body[i];
      // 归一化。前端发来的是 0(黑)-255(白) 或者反过来
      // 神经网络通常希望输入在 0.01 - 1.0 之间
      input[i] = pixel / 255.0;
    }

    int digit = nn.predict(input);
    res.set_content(std::to_string(digit), "text/plain");
  });

  std::cout << "Server starting at 0.0.0.0:8080" << std::endl;
  svr.listen("0.0.0.0", 8080);

  return 0;
}