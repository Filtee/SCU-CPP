# 手写数字识别器 (C++版本)

这是一个基于C++开发的手写数字识别程序，有多个版本以适应不同的环境需求。

## 项目结构

```
mnist_recognizer/
├── digit_recognizer.cpp     # 基于Qt的GUI识别程序
├── digit_recognizer.pro     # Qt项目文件
├── opencv_recognizer.cpp    # 基于OpenCV的图片识别程序
├── CMakeLists.txt           # OpenCV版本的CMake构建文件
├── windows_recognizer.cpp   # 基于Windows GDI+的图片识别程序
├── build_run.bat            # Windows GDI+版本的编译运行脚本
└── README.md               # 项目说明文档
```

## 程序版本

### 1. 基于Qt的GUI识别程序
- **功能**：提供绘图界面，可直接绘制并识别数字
- **依赖**：Qt 5.x 或 Qt 6.x
- **优势**：直观易用，支持实时绘制和识别

### 2. 基于OpenCV的图片识别程序
- **功能**：读取图片文件并识别其中的手写数字
- **依赖**：OpenCV库
- **优势**：强大的图像处理能力，识别准确率较高

### 3. 基于Windows GDI+的图片识别程序
- **功能**：读取图片文件并识别其中的手写数字
- **依赖**：Windows GDI+（Windows系统自带）
- **优势**：无需安装额外库，可直接在Windows系统上运行

## 编译和运行

### 基于Qt的GUI识别程序

#### 方法一：使用Qt Creator
1. 安装Qt Creator和Qt库
2. 打开 `digit_recognizer.pro` 项目文件
3. 点击"构建"按钮编译项目
4. 点击"运行"按钮启动程序

#### 方法二：使用命令行
```bash
# 进入项目目录
cd mnist_recognizer

# 使用qmake生成Makefile
qmake

# 编译项目
make

# 运行程序
./DigitRecognizer
```

#### Windows系统
```bash
# 进入项目目录
cd mnist_recognizer

# 使用qmake生成Makefile
qmake

# 使用mingw32-make编译
mingw32-make

# 运行程序
DigitRecognizer.exe
```

### 基于OpenCV的图片识别程序

#### 使用CMake
1. 安装OpenCV和CMake
2. 创建构建目录并进入
3. 运行CMake生成构建文件
4. 编译并运行

```bash
# 进入项目目录
cd mnist_recognizer

# 创建构建目录
mkdir build
cd build

# 运行CMake
cmake ..

# 编译项目
make

# 运行程序
./opencv_recognizer
```

### 基于Windows GDI+的图片识别程序

#### 使用批处理脚本（推荐）
1. 确保已安装Visual Studio 2019或更新版本
2. 双击运行 `build_run.bat` 脚本
3. 脚本将自动编译并运行程序

#### 手动编译
```bash
# 进入项目目录
cd mnist_recognizer

# 使用Visual Studio编译器编译
cl windows_recognizer.cpp /EHsc /DUNICODE /D_UNICODE /link gdiplus.lib

# 运行程序
windows_recognizer.exe
```

## 识别算法改进

1. **修复了原Python版本的问题**：
   - 调整了宽高比阈值，使识别更准确
   - 改进了点分布的判断逻辑
   - 增加了对点数量的检查

2. **增强的识别能力**：
   - 更好地区分细长的1和其他数字
   - 更准确地识别宽扁的4
   - 改进了空心圆(0)的识别
   - 优化了其他数字的判断条件

## 使用方法

### GUI版本
1. 在白色画布上绘制数字
2. 点击"识别"按钮获取识别结果
3. 点击"清空"按钮重新绘制

### 图片识别版本
1. 将手写数字图片命名为 `drawn_digit.png` 并放在项目根目录
2. 运行识别程序
3. 程序将输出识别结果

## 注意事项

1. **图片要求**：
   - 建议使用白色背景的图片
   - 数字应居中且清晰可见
   - 图片格式为PNG

2. **编译环境**：
   - Qt版本：建议使用Qt 5.12或更高版本
   - OpenCV版本：建议使用OpenCV 4.x
   - Visual Studio：建议使用2019或更高版本

3. **性能优化**：
   - 可根据实际需求调整识别算法的参数
   - 对于大量图片识别，可以考虑并行处理

## 许可证

MIT License