# SCU-CPP

一个完全从零开始构建的手写数字识别系统。本项目通过 C++ 手动实现一个三层全连接神经网络（MLP），并使用原生 C++ 解析 MNIST 二进制数据集。

项目包含一个现代化的 Web 前端，通过 HTTP 接口与 C++ 后端交互，并使用 Docker Compose 进行一键部署。

## 核心特性

- **纯手写核心引擎**：
  - 手动实现矩阵运算、前向传播（Forward Pass）和反向传播（Backpropagation）。
  - 手动解析 MNIST `.idx3-ubyte` 大端序二进制文件。
  - 不依赖 OpenCV，直接处理原始像素字节流。
- **智能前端预处理**：
  - Web 界面实现了类似 MNIST 数据集的预处理逻辑。
  - 自动计算边界框（Bounding Box），将手写数字裁剪、居中并缩放至 28x28 标准尺寸，大幅提高识别率。
- **现代化架构**：
  - **后端**：C++17 + `cpp-httplib` (HTTP Server)。
  - **前端**：HTML5 Canvas + Fetch API。
  - **部署**：Docker + Docker Compose 多阶段构建（支持数据自动解压）。

## 项目结构

```
.
├── CMakeLists.txt          # C++ 构建配置
├── Dockerfile              # 多阶段构建镜像定义
├── docker-compose.yaml     # 容器编排与参数配置
├── entrypoint.sh           # 容器启动脚本 (负责解压数据)
├── data/                   # MNIST 数据集与模型权重
│   ├── model.weights.example # 预训练模型示例 (可重命名为 model.weights 以跳过训练)
│   ├── *.gz                # 压缩的 MNIST 数据集 (容器启动时自动解压)
│   └── ...
├── src/
│   ├── main.cpp            # HTTP 服务器入口 & 业务逻辑
│   ├── neural_net.cpp      # 神经网络核心实现
│   ├── mnist_loader.hpp    # MNIST 二进制文件解析器
│   └── utils.hpp           # 配置读取工具
└── static/
    └── index.html          # Web 前端界面
```

## 快速开始

### 前置要求

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- **数据准备**：确保 `data/` 目录下包含压缩的 MNIST 数据集文件（`train-images-idx3-ubyte.gz` 等）。无需手动解压，Git 仓库仅保留压缩包。

### 运行项目

只需一行命令即可启动训练和推理服务：

```bash
docker-compose up --build
```

**启动流程说明：**

1. **自动解压**：容器启动时，会自动检查 `data/` 目录，将 `.gz` 文件解压为二进制文件。
2. **模型检查**：
   - **情况 A（默认）**：如果 `data/model.weights` 不存在，C++ 引擎会自动加载数据并开始训练（耗时约 30-60 秒）。
   - **情况 B（使用预训练）**：如果你想跳过训练，请在启动前将 `data/model.weights.example` 重命名为 `data/model.weights`。
3. **服务就绪**：训练或加载完成后，服务将在 `8080` 端口启动。

打开浏览器访问：[http://localhost:8080](https://www.google.com/search?q=http://localhost:8080&authuser=1)

## 配置参数

你可以在 `docker-compose.yaml` 中调整神经网络的超参数：

```yaml
environment:
  - EPOCHS=20              # 训练轮数
  - LEARNING_RATE=0.1      # 学习率
  - HIDDEN_NODES=200       # 隐藏层节点数
  - MODEL_PATH=/app/data/model.weights
```

*注意：修改 `HIDDEN_NODES` 后，必须删除旧的 `model.weights` 文件，否则加载时维度不匹配会导致报错。*

## 技术原理

### 1. 神经网络架构 (MLP)

- **输入层**：784 节点 (对应 28x28 像素)
- **隐藏层**：200 节点 (默认，Sigmoid 激活)
- **输出层**：10 节点 (对应数字 0-9，Sigmoid 激活)
- **优化器**：随机梯度下降 (SGD)

### 2. 数据流

1. **用户绘图**：在 HTML Canvas 上绘制高分辨率数字。
2. **前端处理**：JS 捕捉笔迹 -> 计算最小包围盒 -> 裁剪 -> 缩放至 20x20 -> 居中放置在 28x28 画布 -> 提取红色通道。
3. **网络传输**：前端发送 784 字节的二进制流 (Raw Bytes) 到后端。
4. **后端推理**：C++ 接收字节流 -> 归一化 (0.0-1.0) -> 前向传播 -> 返回预测结果。

## 本地开发 (非 Docker)

如果你想在本地直接编译运行（需手动处理数据解压）：

```bash
# 1. 准备数据
cd data && gzip -d *.gz && cd ..

# 2. 创建构建目录
mkdir build && cd build

# 3. 下载依赖 (httplib 单头文件)
wget https://raw.githubusercontent.com/yhirose/cpp-httplib/master/httplib.h -O ../src/httplib.h

# 4. 编译
cmake ..
make

# 5. 运行
export MODEL_PATH="../data/model.weights"
./server
```