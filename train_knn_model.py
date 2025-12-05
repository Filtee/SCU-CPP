import os
import numpy as np
import cv2
import struct

def load_mnist_images(filename):
    """加载MNIST图像数据"""
    with open(filename, 'rb') as f:
        # 读取文件头
        magic, num_images, rows, cols = struct.unpack('>IIII', f.read(16))
        # 读取图像数据
        images = np.fromfile(f, dtype=np.uint8)
        # 重塑为正确的形状
        images = images.reshape(num_images, rows * cols)
    return images

def load_mnist_labels(filename):
    """加载MNIST标签数据"""
    with open(filename, 'rb') as f:
        # 读取文件头
        magic, num_labels = struct.unpack('>II', f.read(8))
        # 读取标签数据
        labels = np.fromfile(f, dtype=np.uint8)
    return labels

def train_knn_model():
    """训练KNN模型"""
    # 数据文件路径
    data_dir = 'data'
    train_images_file = os.path.join(data_dir, 'train-images-idx3-ubyte')
    train_labels_file = os.path.join(data_dir, 'train-labels-idx1-ubyte')
    
    # 检查数据文件是否存在
    if not all(os.path.exists(f) for f in [train_images_file, train_labels_file]):
        print("MNIST数据文件不存在，正在下载...")
        # 运行下载脚本
        import download_mnist
        download_mnist.main()
    
    # 加载数据
    print("加载训练数据...")
    train_images = load_mnist_images(train_images_file)
    train_labels = load_mnist_labels(train_labels_file)
    
    # 数据预处理：归一化到0-1范围
    print("数据预处理...")
    train_images = train_images.astype(np.float32) / 255.0
    train_labels = train_labels.astype(np.float32)
    
    # 创建KNN模型
    print("创建并训练KNN模型...")
    knn = cv2.ml.KNearest_create()
    
    # 设置KNN参数
    knn.setDefaultK(5)  # 设置默认k值
    knn.setIsClassifier(True)
    
    # 训练模型
    knn.train(train_images, cv2.ml.ROW_SAMPLE, train_labels)
    
    # 保存模型
    model_path = 'digits_model.xml'
    knn.save(model_path)
    print(f"模型已保存到 {model_path}")
    
    # 可选：测试模型准确率
    test_images_file = os.path.join(data_dir, 't10k-images-idx3-ubyte')
    test_labels_file = os.path.join(data_dir, 't10k-labels-idx1-ubyte')
    
    if os.path.exists(test_images_file) and os.path.exists(test_labels_file):
        print("加载测试数据...")
        test_images = load_mnist_images(test_images_file).astype(np.float32) / 255.0
        test_labels = load_mnist_labels(test_labels_file).astype(np.float32)
        
        print("测试模型准确率...")
        correct = 0
        total = 0
        
        # 测试不同的k值
        for k in [3, 5, 7, 9]:
            print(f"\n测试k值: {k}")
            correct = 0
            total = 0
            
            # 分批次测试
            batch_size = 1000
            for i in range(0, len(test_images), batch_size):
                batch_images = test_images[i:i+batch_size]
                batch_labels = test_labels[i:i+batch_size]
                
                _, results, _, _ = knn.findNearest(batch_images, k=k)
                
                # 计算准确率
                correct += np.sum(results[:, 0] == batch_labels)
                total += len(batch_images)
                
                print(f"批次 {i//batch_size+1}/{len(test_images)//batch_size} 准确率: {correct/total:.4f}")
            
            print(f"k={k} 最终测试准确率: {correct/total:.4f}")
    
    return knn

if __name__ == "__main__":
    train_knn_model()
