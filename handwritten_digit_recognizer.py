import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageDraw, ImageOps

class DigitRecognizer:
    def __init__(self, root):
        self.root = root
        self.root.title("手写数字识别器")
        
        # 创建画布
        self.canvas_width = 400
        self.canvas_height = 400
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white", cursor="cross")
        self.canvas.pack(pady=20)
        
        # 创建图像和绘图对象
        self.image = Image.new("L", (self.canvas_width, self.canvas_height), 255)
        self.draw = ImageDraw.Draw(self.image)
        
        # 绑定鼠标事件
        self.canvas.bind("<B1-Motion>", self.draw_lines)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # 创建按钮
        button_frame = tk.Frame(root)
        button_frame.pack(pady=20)
        
        self.clear_button = tk.Button(button_frame, text="清空", command=self.clear_canvas, width=10, height=2)
        self.clear_button.grid(row=0, column=0, padx=10)
        
        self.recognize_button = tk.Button(button_frame, text="识别", command=self.recognize_digit, width=10, height=2)
        self.recognize_button.grid(row=0, column=1, padx=10)
        
        # 显示结果
        self.result_label = tk.Label(root, text="请在画布上绘制数字", font=('Arial', 16))
        self.result_label.pack(pady=20)
        
        # 加载预训练的手写数字识别模型
        self.model = cv2.ml.KNearest_load("digits_model.xml")
        if self.model is None:
            self.result_label.config(text="模型加载失败，正在使用MNIST数据集训练模型...")
            self.root.update()
            
            # 尝试训练模型
            try:
                import train_knn_model
                self.model = train_knn_model.train_knn_model()
                self.use_simple_method = False  # 确保使用KNN模型
                self.result_label.config(text="模型训练完成，请绘制数字")
                print("模型训练成功，将使用KNN进行识别")
            except Exception as e:
                print(f"训练模型失败: {e}")
                self.result_label.config(text="模型加载/训练失败，将使用简单识别方法")
                self.use_simple_method = True
                print("将使用简单识别方法")
        else:
            self.use_simple_method = False
            print("模型加载成功，将使用KNN进行识别")
    
    def draw_lines(self, event):
        x1, y1 = (event.x - 10), (event.y - 10)
        x2, y2 = (event.x + 10), (event.y + 10)
        self.canvas.create_oval(x1, y1, x2, y2, fill="black", width=15)
        self.draw.ellipse([x1, y1, x2, y2], fill=0, width=15)
    
    def on_release(self, event):
        # 保存绘制的图像
        self.image.save("drawn_digit.png")
    
    def clear_canvas(self):
        self.canvas.delete("all")
        self.image = Image.new("L", (self.canvas_width, self.canvas_height), 255)
        self.draw = ImageDraw.Draw(self.image)
        self.result_label.config(text="请在画布上绘制数字")
    
    def preprocess_image(self, image):
        """预处理图像，确保与MNIST数据集格式一致"""
        print("开始图像预处理")
        
        # 将PIL图像转换为OpenCV格式
        img_cv = np.array(image)
        
        # 如果是彩色图像，转换为灰度图
        if len(img_cv.shape) > 2:
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
        
        # 原始灰度图像不再保存为debug文件
        
        # 检查图像背景
        # MNIST数据集是黑色背景，白色数字
        # 我们的画布是白色背景，黑色数字，所以需要反转
        # 先进行二值化
        _, binary = cv2.threshold(img_cv, 127, 255, cv2.THRESH_BINARY)
        
        # 计算白色像素的比例
        white_pixels = np.sum(binary == 255)
        total_pixels = binary.size
        white_ratio = white_pixels / total_pixels
        print(f"白色像素比例: {white_ratio:.2f}")
        
        # 如果白色像素比例大于50%，说明是白色背景，需要反转
        if white_ratio > 0.5:
            img_cv = 255 - img_cv
            print("图像已反转，变为黑色背景白色数字")
        
        # 阈值处理，确保图像是清晰的二值图像
        _, thresh = cv2.threshold(img_cv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        print("阈值处理完成")
        
        # 寻找轮廓
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print(f"找到轮廓数量: {len(contours)}")
        
        if not contours:
            print("未找到轮廓")
            return None
        
        # 找到最大的轮廓（假设是数字）
        max_contour = max(contours, key=cv2.contourArea)
        
        # 获取数字的边界框
        x, y, w, h = cv2.boundingRect(max_contour)
        
        # 提取数字区域，稍微扩大边界
        margin = 10
        x = max(0, x - margin)
        y = max(0, y - margin)
        w = min(img_cv.shape[1] - x, w + 2 * margin)
        h = min(img_cv.shape[0] - y, h + 2 * margin)
        
        digit_roi = thresh[y:y+h, x:x+w]
        
        # 确保有内容
        if digit_roi.size == 0:
            print("提取的数字区域为空")
            return None
        
        print("数字区域已提取")
        
        # 调整图像大小为20x20，保持宽高比
        aspect_ratio = digit_roi.shape[1] / digit_roi.shape[0]
        if aspect_ratio > 1:
            new_w = 20
            new_h = int(20 / aspect_ratio)
        else:
            new_h = 20
            new_w = int(20 * aspect_ratio)
        
        resized = cv2.resize(digit_roi, (new_w, new_h), interpolation=cv2.INTER_AREA)
        print(f"调整大小为: {new_w}x{new_h}")
        
        # 创建28x28的画布，居中放置数字
        final_img = np.zeros((28, 28), dtype=np.uint8)
        
        # 计算居中位置
        x_offset = (28 - new_w) // 2
        y_offset = (28 - new_h) // 2
        
        # 将数字放置在画布中央
        final_img[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        
        # 保存最终的预处理图像
        print("预处理完成，最终尺寸: 28x28")
        
        return final_img
    
    def recognize_digit(self):
        print(f"开始识别，当前模式: {'简单识别' if self.use_simple_method else 'KNN模型识别'}")
        
        # 原始绘制图像不再保存为debug文件
        
        # 预处理图像
        processed_img = self.preprocess_image(self.image)
        
        if processed_img is None:
            self.result_label.config(text="未检测到数字，请重新绘制")
            return
        
        # 预处理后的图像不再保存为debug文件
        
        if self.use_simple_method:
            # 使用简单的模板匹配方法
            print("使用简单识别方法")
            digit = self.simple_recognition(processed_img)
            confidence = "(简单识别，无置信度)"
        else:
            # 使用KNN模型识别
            print("使用KNN模型识别")
            digit, confidence = self.knn_recognition(processed_img)
        
        self.result_label.config(text=f"识别结果: {digit}")
        print(f"最终识别结果: {digit}")
        print("识别完成")
    
    def simple_recognition(self, img):
        # 简单的基于像素特征的识别方法
        # 计算非零像素的数量和分布
        non_zero_pixels = cv2.countNonZero(img)
        
        # 根据像素数量和分布简单判断数字
        if non_zero_pixels < 50:
            return "0"
        elif non_zero_pixels < 100:
            return "1"
        elif non_zero_pixels < 150:
            return "7"
        elif non_zero_pixels < 200:
            return "4"
        elif non_zero_pixels < 250:
            return "2"
        elif non_zero_pixels < 300:
            return "9"
        elif non_zero_pixels < 350:
            return "5"
        elif non_zero_pixels < 400:
            return "3"
        elif non_zero_pixels < 450:
            return "8"
        else:
            return "6"
    
    def knn_recognition(self, img):
        print("开始KNN模型识别")
        
        # KNN输入图像不再保存为debug文件
        
        # 准备输入数据：归一化到0-1范围（与训练时一致）
        flattened = img.reshape(1, -1).astype(np.float32) / 255.0
        print(f"输入数据形状: {flattened.shape}")
        print(f"输入数据范围: {np.min(flattened):.2f} - {np.max(flattened):.2f}")
        
        try:
            # 使用KNN模型预测，调整k值为5
            _, result, neighbors, distances = self.model.findNearest(flattened, k=5)
            
            digit = str(int(result[0][0]))
            
            # 计算置信度（基于最近邻的距离）
            if len(distances) > 0 and np.sum(distances) > 0:
                # 距离较小表示置信度较高
                avg_distance = np.mean(distances)
                # 将距离转换为0-100%的置信度
                confidence = max(0, 100 - (avg_distance * 1000))
                confidence = min(100, confidence)
                confidence_percentage = f"{confidence:.2f}%"
            else:
                confidence_percentage = "100%"
            
            # 调试信息
            print(f"识别结果: {digit}, 置信度: {confidence_percentage}")
            print(f"最近邻: {[int(n) for n in neighbors[0]]}")
            print(f"距离: {[d for d in distances[0]]}")
            print(f"平均距离: {np.mean(distances):.4f}")
            
            return digit, confidence_percentage
        except Exception as e:
            print(f"KNN模型识别过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return "无法识别", "0%"
    
    def create_simple_model(self):
        # 创建一个简单的模型文件（如果不存在）
        # 这是一个占位符，实际应用中应该使用训练好的模型
        # 创建一个简单的KNN模型
        samples = np.random.randint(0, 100, (100, 784)).astype(np.float32)
        responses = np.random.randint(0, 10, (100, 1)).astype(np.float32)
        
        knn = cv2.ml.KNearest_create()
        knn.train(samples, cv2.ml.ROW_SAMPLE, responses)
        knn.save("digits_model.xml")

if __name__ == "__main__":
    root = tk.Tk()
    app = DigitRecognizer(root)
    
    root.mainloop()