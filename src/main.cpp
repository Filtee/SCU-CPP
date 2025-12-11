// src/main.cpp
#include <chrono>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <vector>

#include "httplib.h"
#include "mnist_loader.hpp"
#include "neural_net.hpp"
#include "utils.hpp"

// 辅助函数：打印头部信息
void print_header() {
  std::cout << "\n========================================" << std::endl;
  std::cout << "      SCU-CPP 手写数字识别系统启动" << std::endl;
  std::cout << "========================================" << std::endl;
}

// 辅助函数：打印配置信息
void print_config(int epochs, double lr, int hidden_nodes,
                  const std::string& model_path) {
  std::cout << "系统配置详情:" << std::endl;
  std::cout << "  - 训练轮数 (Epochs)   : " << epochs << std::endl;
  std::cout << "  - 学习率 (LR)         : " << lr << std::endl;
  std::cout << "  - 隐藏层节点数        : " << hidden_nodes << std::endl;
  std::cout << "  - 模型文件路径        : " << model_path << std::endl;
  std::cout << "========================================\n" << std::endl;
}

int main() {
  // 1. 获取配置
  int epochs = Config::getInt("EPOCHS", 10);
  double lr = Config::getDouble("LEARNING_RATE", 0.1);
  int hidden_nodes = Config::getInt("HIDDEN_NODES", 200);
  std::string model_path =
      Config::getString("MODEL_PATH", "/app/data/model.weights");

  print_header();
  print_config(epochs, lr, hidden_nodes, model_path);

  // 2. 初始化神经网络
  SimpleNN nn(784, hidden_nodes, 10, lr);

  // 3. 模型加载逻辑
  if (!nn.load(model_path)) {
    std::cout << "[警告] 未检测到预训练模型文件。" << std::endl;
    std::cout << "[信息] 准备开始从头训练..." << std::endl;

    std::cout << "[信息] 正在读取 MNIST 数据集... " << std::flush;
    auto train_data = load_mnist("/app/data/train-images-idx3-ubyte",
                                 "/app/data/train-labels-idx1-ubyte");

    if (train_data.images.empty()) {
      std::cerr << "\n[错误] 数据集加载失败！" << std::endl;
      std::cerr << "       请检查 data 目录下文件是否完整。" << std::endl;
      return 1;
    }
    std::cout << "完成！" << std::endl;
    std::cout << "[信息] 数据集样本数量: " << train_data.images.size()
              << " 张\n"
              << std::endl;

    auto total_start = std::chrono::high_resolution_clock::now();
    size_t total_images = train_data.images.size();

    // 设置日志间隔：每 10% 打印一次
    size_t log_interval = total_images / 10;
    if (log_interval == 0) log_interval = 1;

    for (int e = 0; e < epochs; e++) {
      std::cout << "正在执行第 " << (e + 1) << "/" << epochs << " 轮训练..."
                << std::endl;

      auto epoch_start = std::chrono::high_resolution_clock::now();

      for (size_t i = 0; i < total_images; i++) {
        nn.train(train_data.images[i], train_data.labels[i]);

        // 【简单日志】每完成 10% 打印一行
        if ((i + 1) % log_interval == 0) {
          float progress = static_cast<float>(i + 1) / total_images * 100.0;
          std::cout << "[训练] 进度: " << std::fixed << std::setprecision(0)
                    << progress << "% (" << (i + 1) << "/" << total_images
                    << ")" << std::endl;
        }
      }

      // 保存模型
      nn.save(model_path);

      auto epoch_end = std::chrono::high_resolution_clock::now();
      std::chrono::duration<double> elapsed = epoch_end - epoch_start;

      std::cout << "  -> 本轮耗时: " << std::fixed << std::setprecision(2)
                << elapsed.count() << "s"
                << " | 模型已保存" << std::endl;
      std::cout
          << "------------------------------------------------------------"
          << std::endl;
    }

    auto total_end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> total_elapsed = total_end - total_start;

    std::cout << "\n========================================" << std::endl;
    std::cout << "      训练任务圆满完成！" << std::endl;
    std::cout << "  - 总耗时      : " << total_elapsed.count() << " 秒"
              << std::endl;
    std::cout << "  - 最终模型位置: " << model_path << std::endl;
    std::cout << "========================================\n" << std::endl;

  } else {
    std::cout << "[成功] 已加载预训练模型: " << model_path << std::endl;
    std::cout << "[信息] 跳过训练阶段，直接启动推理服务。" << std::endl;
  }

  // 4. 启动 Web 服务
  httplib::Server svr;

  svr.Get("/", [](const httplib::Request&, httplib::Response& res) {
    std::ifstream t("/app/static/index.html");
    std::stringstream buffer;
    buffer << t.rdbuf();
    res.set_content(buffer.str(), "text/html");
  });

  svr.Post("/predict",
           [&](const httplib::Request& req, httplib::Response& res) {
             if (req.body.size() != 784) {
               res.status = 400;
               res.set_content("错误: 数据尺寸不匹配", "text/plain");
               return;
             }

             std::vector<double> input(784);
             for (size_t i = 0; i < 784; i++) {
               input[i] = static_cast<unsigned char>(req.body[i]) / 255.0;
             }

             int digit = nn.predict(input);
             // 简单的访问日志
             // std::cout << "[请求] 识别结果: " << digit << std::endl;
             res.set_content(std::to_string(digit), "text/plain");
           });

  std::cout << "Web 服务已就绪" << std::endl;
  std::cout << "  - 监听地址: http://0.0.0.0:8080" << std::endl;

  svr.listen("0.0.0.0", 8080);

  return 0;
}