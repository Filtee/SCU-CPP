// src/neural_net.cpp
#include "neural_net.hpp"

#include <algorithm>
#include <fstream>
#include <iostream>
#include <random>

SimpleNN::SimpleNN(int input_nodes, int hidden_nodes, int output_nodes,
                   double learning_rate)
    : inodes(input_nodes),
      hnodes(hidden_nodes),
      onodes(output_nodes),
      lr(learning_rate) {
  // 随机初始化权重
  std::random_device rd;
  std::mt19937 gen(rd());
  std::normal_distribution<> d(0, 1.0 / std::sqrt(inodes));

  w_ih.resize(inodes * hnodes);
  for (auto& w : w_ih) w = d(gen);

  w_ho.resize(hnodes * onodes);
  for (auto& w : w_ho) w = d(gen);
}

double SimpleNN::sigmoid(double x) { return 1.0 / (1.0 + std::exp(-x)); }

void SimpleNN::train(const std::vector<double>& inputs, int target_label) {
  // 1. 前向传播 (Forward Pass)

  // Hidden Layer
  std::vector<double> hidden_inputs(hnodes, 0.0);
  std::vector<double> hidden_outputs(hnodes, 0.0);

  for (int h = 0; h < hnodes; h++) {
    for (int i = 0; i < inodes; i++) {
      hidden_inputs[h] += w_ih[i * hnodes + h] * inputs[i];
    }
    hidden_outputs[h] = sigmoid(hidden_inputs[h]);
  }

  // Output Layer
  std::vector<double> final_inputs(onodes, 0.0);
  std::vector<double> final_outputs(onodes, 0.0);

  for (int o = 0; o < onodes; o++) {
    for (int h = 0; h < hnodes; h++) {
      final_inputs[o] += w_ho[h * onodes + o] * hidden_outputs[h];
    }
    final_outputs[o] = sigmoid(final_inputs[o]);
  }

  // 2. 计算误差 (Backpropagation)

  // 目标向量 (One-hot)
  std::vector<double> targets(onodes, 0.01);
  targets[target_label] = 0.99;

  std::vector<double> output_errors(onodes);
  for (int o = 0; o < onodes; o++) {
    output_errors[o] = targets[o] - final_outputs[o];
  }

  // 隐藏层误差
  std::vector<double> hidden_errors(hnodes, 0.0);
  for (int h = 0; h < hnodes; h++) {
    double error = 0.0;
    for (int o = 0; o < onodes; o++) {
      error += w_ho[h * onodes + o] * output_errors[o];
    }
    hidden_errors[h] = error;
  }

  // 3. 更新权重 (Gradient Descent)

  // 更新 Hidden -> Output
  for (int o = 0; o < onodes; o++) {
    for (int h = 0; h < hnodes; h++) {
      w_ho[h * onodes + o] += lr * output_errors[o] * final_outputs[o] *
                              (1.0 - final_outputs[o]) * hidden_outputs[h];
    }
  }

  // 更新 Input -> Hidden
  for (int h = 0; h < hnodes; h++) {
    for (int i = 0; i < inodes; i++) {
      w_ih[i * hnodes + h] += lr * hidden_errors[h] * hidden_outputs[h] *
                              (1.0 - hidden_outputs[h]) * inputs[i];
    }
  }
}

int SimpleNN::predict(const std::vector<double>& inputs) {
  // 仅前向传播
  std::vector<double> hidden_outputs(hnodes, 0.0);
  for (int h = 0; h < hnodes; h++) {
    double sum = 0.0;
    for (int i = 0; i < inodes; i++) {
      sum += w_ih[i * hnodes + h] * inputs[i];
    }
    hidden_outputs[h] = sigmoid(sum);
  }

  std::vector<double> final_outputs(onodes, 0.0);
  int max_idx = 0;
  double max_val = -1.0;

  for (int o = 0; o < onodes; o++) {
    double sum = 0.0;
    for (int h = 0; h < hnodes; h++) {
      sum += w_ho[h * onodes + o] * hidden_outputs[h];
    }
    final_outputs[o] = sigmoid(sum);

    if (final_outputs[o] > max_val) {
      max_val = final_outputs[o];
      max_idx = o;
    }
  }
  return max_idx;
}

void SimpleNN::save(const std::string& filename) {
  std::ofstream out(filename);
  for (double w : w_ih) out << w << " ";
  out << "\n";
  for (double w : w_ho) out << w << " ";
  out.close();
}

bool SimpleNN::load(const std::string& filename) {
  std::ifstream in(filename);
  if (!in.is_open()) return false;
  for (double& w : w_ih) in >> w;
  for (double& w : w_ho) in >> w;
  return true;
}