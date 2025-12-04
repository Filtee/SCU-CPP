import cv2
import numpy as np
import os
import time

class CommandLineDigitRecognizer:
    def __init__(self):
        # 加载预训练模型
        self.model_path = "digits_model.xml"
        self.model = self.load_model()
        
    def load_model(self):
        """加载预训练的KNN模型"""
        if not os.path.exists(self.model_path):
            print("模型文件不存在，正在下载MNIST数据集并训练模型...")
            try:
                import train_knn_model
                model = train_knn_model.train_knn_model()
                print("模型训练完成！")
                return model
            except Exception as e:
                print(f"训练模型失败: {e}")
                return None
        
        print("正在加载预训练模型...")
        model = cv2.ml.KNearest_load(self.model_path)
        print("模型加载成功！")
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
        
        # 保存预处理后的图像
        cv2.imwrite("last_processed_digit.png", processed_img)
        
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
    
    def test_recognition(self):
        """使用示例图像测试识别功能"""
        print("\n=== 手写数字识别测试 ===")
        print("使用MNIST数据集训练的KNN模型，优化的预处理算法")
        print("\n测试不同的数字识别...")
        
        # 创建测试图像
        self.create_test_images()
        
        # 测试所有数字
        success_count = 0
        total_count = 10
        
        for digit in range(10):
            img_path = f"test_digit_{digit}.png"
            print(f"\n--- 测试数字: {digit} ---")
            
            # 识别数字
            recognized_digit, confidence = self.recognize_digit(img_path)
            
            if recognized_digit is not None:
                is_correct = recognized_digit == str(digit)
                if is_correct:
                    success_count += 1
                    print(f"✅ 识别成功: {recognized_digit} (置信度: {confidence})")
                else:
                    print(f"❌ 识别失败: 实际数字 {digit}, 识别为 {recognized_digit} (置信度: {confidence})")
            else:
                print("❌ 识别失败: 无法处理图像")
        
        # 显示总体结果
        print(f"\n=== 测试总结 ===")
        print(f"测试数量: {total_count}")
        print(f"成功数量: {success_count}")
        print(f"准确率: {(success_count / total_count) * 100:.2f}%")
    
    def create_test_images(self):
        """创建测试用的数字图像"""
        print("创建测试图像...")
        
        for digit in range(10):
            # 创建一个黑色背景的图像
            img = np.zeros((200, 200), dtype=np.uint8)
            
            # 设置字体和文本
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 8
            thickness = 20
            
            # 计算文本位置
            text_size = cv2.getTextSize(str(digit), font, font_scale, thickness)[0]
            text_x = (img.shape[1] - text_size[0]) // 2
            text_y = (img.shape[0] + text_size[1]) // 2
            
            # 在图像上绘制数字
            cv2.putText(img, str(digit), (text_x, text_y), font, font_scale, (255, 255, 255), thickness)
            
            # 添加一些随机噪声和变形，模拟手写效果
            rows, cols = img.shape
            M = np.float32([[1, 0.05, 0], [0.05, 1, 0]])
            img = cv2.warpAffine(img, M, (cols, rows))
            
            # 添加一些随机噪声
            noise = np.random.randint(0, 50, (rows, cols), dtype=np.uint8)
            img = cv2.add(img, noise)
            
            # 保存图像
            img_path = f"test_digit_{digit}.png"
            cv2.imwrite(img_path, img)
        
        print("测试图像创建完成！")
    
    def run(self):
        """运行命令行识别器"""
        print("\n" + "="*50)
        print("    优化后的手写数字识别器 (命令行版)")
        print("="*50)
        
        while True:
            print("\n请选择操作:")
            print("1. 测试所有数字识别")
            print("2. 识别单个图像文件")
            print("3. 查看预处理示例")
            print("4. 退出程序")
            
            choice = input("\n请输入选项 (1-4): ")
            
            if choice == "1":
                self.test_recognition()
            
            elif choice == "2":
                img_path = input("请输入图像文件路径: ")
                if os.path.exists(img_path):
                    digit, confidence = self.recognize_digit(img_path)
                    if digit is not None:
                        print(f"\n识别结果: {digit} (置信度: {confidence})")
                        print(f"预处理后的图像已保存为: last_processed_digit.png")
                    else:
                        print("识别失败")
                else:
                    print("图像文件不存在")
            
            elif choice == "3":
                print("\n预处理步骤示例:")
                print("1. 读取灰度图像")
                print("2. 高斯模糊降噪")
                print("3. 自适应二值化")
                print("4. 形态学操作增强轮廓")
                print("5. 查找并提取数字区域")
                print("6. 保持宽高比调整大小")
                print("7. 居中放置在28x28画布上")
            
            elif choice == "4":
                print("\n谢谢使用，再见！")
                break
            
            else:
                print("无效选项，请重新输入")

def main():
    # 创建识别器实例
    recognizer = CommandLineDigitRecognizer()
    
    # 运行命令行界面
    recognizer.run()

if __name__ == "__main__":
    main()
