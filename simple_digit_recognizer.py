import tkinter as tk
from PIL import Image, ImageDraw, ImageOps
import numpy as np

class SimpleDigitRecognizer:
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
        
        # 定义简单的数字特征模板
        self.digit_templates = {
            '0': self.create_template_0(),
            '1': self.create_template_1(),
            '2': self.create_template_2(),
            '3': self.create_template_3(),
            '4': self.create_template_4(),
            '5': self.create_template_5(),
            '6': self.create_template_6(),
            '7': self.create_template_7(),
            '8': self.create_template_8(),
            '9': self.create_template_9()
        }
    
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
        # 调整大小为28x28
        resized = image.resize((28, 28), Image.LANCZOS)
        
        # 转换为numpy数组
        img_array = np.array(resized)
        
        # 二值化
        binary = (img_array < 128).astype(int)
        
        return binary
    
    def recognize_digit(self):
        # 预处理图像
        processed_img = self.preprocess_image(self.image)
        
        # 计算与每个模板的相似度
        similarities = {}
        for digit, template in self.digit_templates.items():
            # 使用简单的相关性作为相似度度量
            similarity = np.sum(processed_img * template) / np.sum(template)
            similarities[digit] = similarity
        
        # 找出最相似的数字
        recognized_digit = max(similarities, key=similarities.get)
        
        self.result_label.config(text=f"识别结果: {recognized_digit}")
    
    def create_template_0(self):
        # 创建数字0的模板
        template = np.zeros((28, 28))
        # 绘制外圈
        template[3:25, 3:25] = 1
        # 绘制内圈（空心）
        template[7:21, 7:21] = 0
        return template
    
    def create_template_1(self):
        # 创建数字1的模板
        template = np.zeros((28, 28))
        # 绘制垂直线
        template[5:23, 12:16] = 1
        return template
    
    def create_template_2(self):
        # 创建数字2的模板
        template = np.zeros((28, 28))
        # 绘制上部
        template[3:7, 3:25] = 1
        # 绘制中部
        template[12:16, 3:25] = 1
        # 绘制下部
        template[20:24, 3:25] = 1
        # 连接部分
        template[7:12, 21:25] = 1
        template[16:20, 3:7] = 1
        return template
    
    def create_template_3(self):
        # 创建数字3的模板
        template = np.zeros((28, 28))
        # 绘制上部
        template[3:7, 3:25] = 1
        # 绘制中部
        template[12:16, 3:25] = 1
        # 绘制下部
        template[20:24, 3:25] = 1
        # 连接部分
        template[7:12, 21:25] = 1
        template[16:20, 21:25] = 1
        return template
    
    def create_template_4(self):
        # 创建数字4的模板
        template = np.zeros((28, 28))
        # 绘制左侧
        template[3:16, 3:7] = 1
        # 绘制中部
        template[12:16, 7:25] = 1
        # 绘制右侧
        template[3:24, 21:25] = 1
        return template
    
    def create_template_5(self):
        # 创建数字5的模板
        template = np.zeros((28, 28))
        # 绘制上部
        template[3:7, 3:25] = 1
        # 绘制中部
        template[12:16, 3:25] = 1
        # 绘制下部
        template[20:24, 3:25] = 1
        # 连接部分
        template[7:12, 3:7] = 1
        template[16:20, 21:25] = 1
        return template
    
    def create_template_6(self):
        # 创建数字6的模板
        template = np.zeros((28, 28))
        # 绘制外圈
        template[3:25, 3:25] = 1
        # 绘制内圈（部分空心）
        template[7:21, 7:21] = 0
        # 绘制中间线
        template[12:16, 3:7] = 1
        template[16:21, 7:14] = 1
        return template
    
    def create_template_7(self):
        # 创建数字7的模板
        template = np.zeros((28, 28))
        # 绘制上部
        template[3:7, 3:25] = 1
        # 绘制斜线
        template[7:24, 21:25] = 1
        return template
    
    def create_template_8(self):
        # 创建数字8的模板
        template = np.zeros((28, 28))
        # 绘制外圈
        template[3:25, 3:25] = 1
        # 绘制内圈
        template[12:16, 7:21] = 1
        template[7:21, 12:16] = 1
        return template
    
    def create_template_9(self):
        # 创建数字9的模板
        template = np.zeros((28, 28))
        # 绘制外圈
        template[3:25, 3:25] = 1
        # 绘制内圈（部分空心）
        template[7:21, 7:21] = 0
        # 绘制中间线
        template[12:16, 21:25] = 1
        template[3:7, 7:14] = 1
        return template

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleDigitRecognizer(root)
    root.mainloop()