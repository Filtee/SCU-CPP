import cv2
import numpy as np
import os
import time

class AutoTestDigitRecognizer:
    def __init__(self):
        # 加载预训练模型
        self.model_path = "digits_model.xml"
        self.model = self.load_model()
        
    def load_model(self):
        """加载预训练的KNN模型"""
        if not os.path.exists(self.model_path):
            print("模型文件不存在，正在训练模型...")
            try:
                import train_knn_model
                model = train_knn_model.train_knn_model()
                print("模型训练完成！")
                return model
            except Exception as e:
                print(f"训练模型失败: {e}")
                return None
        
        model = cv2.ml.KNearest_load(self.model_path)
        return model
    
    def preprocess_image(self, img_path):
        """优化的图像预处理"""
        # 读取图像
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            print(f"无法读取图像: {img_path}")
            return None
        
        # 应用高斯模糊降噪
        blurred = cv2.GaussianBlur(img, (5, 5), 0)
        
        # 使用自适应二值化 - 确保与MNIST格式一致（白色背景，黑色数字）
        # 如果图像是黑色背景白色数字，先反转
        if np.mean(img) < 128:  # 黑色背景
            img = 255 - img  # 反转图像
            blurred = 255 - blurred  # 反转模糊图像
        
        binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 11, 2)
        
        # 形态学操作
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 查找轮廓
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            print("未检测到数字轮廓")
            return None
        
        # 找到最大的轮廓
        max_contour = max(contours, key=cv2.contourArea)
        
        # 获取边界框并添加边距
        x, y, w, h = cv2.boundingRect(max_contour)
        margin = 5
        x = max(0, x - margin)
        y = max(0, y - margin)
        w = min(img.shape[1] - x, w + 2*margin)
        h = min(img.shape[0] - y, h + 2*margin)
        
        digit_roi = binary[y:y+h, x:x+w]
        
        # 保持宽高比调整大小
        aspect_ratio = h / w if w != 0 else 1
        if aspect_ratio > 1:
            new_h = 20
            new_w = int(new_h / aspect_ratio)
        else:
            new_w = 20
            new_h = int(new_w * aspect_ratio)
        
        resized = cv2.resize(digit_roi, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # 居中放置在20x20画布上
        canvas = np.zeros((20, 20), dtype=np.uint8)
        offset_x = (20 - new_w) // 2
        offset_y = (20 - new_h) // 2
        canvas[offset_y:offset_y+new_h, offset_x:offset_x+new_w] = resized
        
        # 添加边界，使总大小为28x28
        padded = cv2.copyMakeBorder(canvas, 4, 4, 4, 4, cv2.BORDER_CONSTANT, value=0)
        
        return padded
    
    def recognize_digit(self, img_path):
        """识别数字"""
        if self.model is None:
            print("模型未加载，无法识别数字")
            return None, None
        
        # 预处理图像
        processed_img = self.preprocess_image(img_path)
        
        if processed_img is None:
            return None, None
        
        # 准备输入数据
        flattened = processed_img.reshape(1, -1).astype(np.float32) / 255.0
        
        # 使用KNN模型预测
        _, result, neighbors, distances = self.model.findNearest(flattened, k=3)
        
        digit = str(int(result[0][0]))
        
        # 计算置信度
        if len(distances) > 0 and np.sum(distances) > 0:
            avg_distance = np.mean(distances)
            confidence = max(0, 100 - (avg_distance * 1000))
            confidence = min(100, confidence)
            confidence_percentage = f"{confidence:.2f}%"
        else:
            confidence_percentage = "100%"
        
        return digit, confidence_percentage
    
    def create_test_images(self):
        """创建测试用的数字图像"""
        print("创建测试图像...")
        
        for digit in range(10):
            # 创建一个白色背景的图像（与MNIST格式一致）
            img = np.ones((200, 200), dtype=np.uint8) * 255
            
            # 设置字体和文本
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 8
            thickness = 20
            
            # 计算文本位置
            text_size = cv2.getTextSize(str(digit), font, font_scale, thickness)[0]
            text_x = (img.shape[1] - text_size[0]) // 2
            text_y = (img.shape[0] + text_size[1]) // 2
            
            # 在图像上绘制黑色数字（与MNIST格式一致）
            cv2.putText(img, str(digit), (text_x, text_y), font, font_scale, (0, 0, 0), thickness)
            
            # 添加一些随机噪声和变形，模拟手写效果
            rows, cols = img.shape
            M = np.float32([[1, 0.05, 0], [0.05, 1, 0]])
            img = cv2.warpAffine(img, M, (cols, rows))
            
            # 添加一些随机噪声
            noise = np.random.randint(0, 50, (rows, cols), dtype=np.uint8)
            img = cv2.add(img, noise)
            
            # 确保图像保持白色背景
            img[img > 255] = 255
            
            # 保存图像
            img_path = f"test_digit_{digit}.png"
            cv2.imwrite(img_path, img)
        
        print("测试图像创建完成！")
    
    def run_full_test(self):
        """运行完整的测试流程"""
        print("\n" + "="*60)
        print("        手写数字识别器 - 自动测试报告")
        print("="*60)
        
        # 创建测试图像
        self.create_test_images()
        
        print("\n" + "="*60)
        print("        测试结果")
        print("="*60)
        
        # 测试所有数字
        success_count = 0
        total_count = 10
        
        # 测试不同的K值
        k_values = [3, 5, 7]
        
        for k in k_values:
            print(f"\n--- 使用K值: {k} ---")
            success_count_k = 0
            
            for digit in range(10):
                img_path = f"test_digit_{digit}.png"
                
                # 读取并预处理图像
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                processed_img = self.preprocess_image(img_path)
                
                if processed_img is not None:
                    # 准备输入数据
                    flattened = processed_img.reshape(1, -1).astype(np.float32) / 255.0
                    
                    # 使用KNN模型预测
                    _, result, neighbors, distances = self.model.findNearest(flattened, k=k)
                    
                    recognized_digit = str(int(result[0][0]))
                    is_correct = recognized_digit == str(digit)
                    
                    if is_correct:
                        success_count_k += 1
                        status = "✅"
                    else:
                        status = "❌"
                    
                    # 计算置信度
                    if len(distances) > 0:
                        avg_distance = np.mean(distances)
                        confidence = max(0, 100 - (avg_distance * 1000))
                        confidence = min(100, confidence)
                        confidence_str = f"{confidence:.2f}%"
                    else:
                        confidence_str = "100%"
                    
                    print(f"{status} 数字 {digit}: 识别为 {recognized_digit} (置信度: {confidence_str})")
            
            print(f"K值 {k} 的准确率: {(success_count_k / total_count) * 100:.2f}%")
            
            if k == 3:
                success_count = success_count_k
        
        # 显示总体结果
        print("\n" + "="*60)
        print("        总体评估")
        print("="*60)
        print(f"测试数量: {total_count}")
        print(f"成功数量: {success_count}")
        print(f"最终准确率: {(success_count / total_count) * 100:.2f}%")
        
        # 显示优化点
        print("\n" + "="*60)
        print("        优化功能展示")
        print("="*60)
        print("1. 优化的图像预处理:")
        print("   - 高斯模糊降噪")
        print("   - 自适应二值化")
        print("   - 形态学操作增强轮廓")
        print("   - 数字区域提取和调整")
        print("   - 标准化为28x28像素")
        
        print("\n2. 优化的KNN模型:")
        print("   - 使用MNIST数据集训练")
        print("   - 数据归一化到0-1范围")
        print("   - 可调节的K值参数")
        print("   - 距离加权的置信度计算")
        
        print("\n3. 优化的识别算法:")
        print("   - 预处理与训练保持一致")
        print("   - 改进的置信度计算方法")
        print("   - 调试信息输出")
        
        print("\n" + "="*60)
        print("        测试完成")
        print("="*60)

# 运行自动测试
if __name__ == "__main__":
    start_time = time.time()
    
    test_recognizer = AutoTestDigitRecognizer()
    test_recognizer.run_full_test()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n总运行时间: {total_time:.2f} 秒")
    print("\n您可以通过以下命令运行交互式识别器:")
    print("python command_line_recognizer.py")
    print("\n或通过以下命令运行原始GUI识别器:")
    print("python handwritten_digit_recognizer.py")
