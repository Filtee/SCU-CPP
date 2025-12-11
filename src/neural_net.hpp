// src/neural_net.hpp
#pragma once
#include <cmath>
#include <string>
#include <vector>

class SimpleNN {
 public:
  // 构造函数：输入节点数，隐藏节点数，输出节点数，学习率
  SimpleNN(int input_nodes, int hidden_nodes, int output_nodes,
           double learning_rate);

  // 训练一次
  void train(const std::vector<double>& inputs, int target_label);

  // 预测
  int predict(const std::vector<double>& inputs);

  // 保存/加载权重（简单的文本格式）
  void save(const std::string& filename);
  bool load(const std::string& filename);

 private:
  int inodes, hnodes, onodes;
  double lr;

  // 权重矩阵 (扁平化存储以简化实现)
  std::vector<double> w_ih;  // 输入 -> 隐藏
  std::vector<double> w_ho;  // 隐藏 -> 输出

  // 激活函数 (Sigmoid)
  double sigmoid(double x);
};