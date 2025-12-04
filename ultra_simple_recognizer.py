import tkinter as tk
from PIL import Image, ImageDraw
import os

class UltraSimpleDigitRecognizer:
    def __init__(self, root):
        self.root = root
        self.root.title("手写数字识别器")
        
        # 创建画布
        self.canvas_width = 300
        self.canvas_height = 300
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white", cursor="cross")
        self.canvas.pack(pady=20)
        
        # 保存绘制的点
        self.points = []
        
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
        
        self.save_button = tk.Button(button_frame, text="保存图像", command=self.save_image, width=10, height=2)
        self.save_button.grid(row=0, column=2, padx=10)
        
        # 显示结果
        self.result_label = tk.Label(root, text="请在画布上绘制数字", font=('Arial', 16))
        self.result_label.pack(pady=20)
        
        # 设置保存路径
        self.image_path = os.path.join(os.path.dirname(__file__), "drawn_digit.png")
    
    def draw_lines(self, event):
        x, y = event.x, event.y
        self.points.append((x, y))
        self.canvas.create_oval(x-8, y-8, x+8, y+8, fill="black", width=0)
    
    def on_release(self, event):
        # 保存绘制的点
        pass
    
    def clear_canvas(self):
        self.canvas.delete("all")
        self.points = []
        self.result_label.config(text="请在画布上绘制数字")
    
    def save_image(self):
        if not self.points:
            self.result_label.config(text="请先绘制数字")
            return
        
        # 创建一个空白图像
        img = Image.new('RGB', (self.canvas_width, self.canvas_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # 绘制点
        for point in self.points:
            x, y = point
            draw.ellipse([x-8, y-8, x+8, y+8], fill='black')
        
        # 保存图像
        img.save(self.image_path)
        self.result_label.config(text=f"图像已保存为: {self.image_path}")
    
    def calculate_point_density(self, points, x1, y1, x2, y2):
        """计算指定区域内的点密度"""
        count = 0
        for p in points:
            if x1 <= p[0] <= x2 and y1 <= p[1] <= y2:
                count += 1
        return count
    
    def recognize_digit(self):
        if not self.points:
            self.result_label.config(text="请先绘制数字")
            return
        
        points = self.points
        num_points = len(points)
        
        # Calculate point distribution
        x_min = min(p[0] for p in points)
        x_max = max(p[0] for p in points)
        y_min = min(p[1] for p in points)
        y_max = max(p[1] for p in points)
        
        width = x_max - x_min
        height = y_max - y_min
        aspect_ratio = width / height if height != 0 else 0
        
        # Count points in four quadrants
        center_x = (x_min + x_max) // 2
        center_y = (y_min + y_max) // 2
        
        q1 = sum(1 for p in points if p[0] < center_x and p[1] < center_y)
        q2 = sum(1 for p in points if p[0] >= center_x and p[1] < center_y)
        q3 = sum(1 for p in points if p[0] < center_x and p[1] >= center_y)
        q4 = sum(1 for p in points if p[0] >= center_x and p[1] >= center_y)
        
        top_half = sum(1 for p in points if p[1] < center_y)
        bottom_half = num_points - top_half
        left_half = sum(1 for p in points if p[0] < center_x)
        right_half = num_points - left_half
        
        # Calculate edge points
        edge_points = 0
        for p in points:
            if abs(p[0] - x_min) < 15 or abs(p[0] - x_max) < 15 or \
               abs(p[1] - y_min) < 15 or abs(p[1] - y_max) < 15:
                edge_points += 1
        
        # Calculate thirds
        one_third_y = y_min + height // 3
        two_thirds_y = y_min + 2 * height // 3
        one_third_x = x_min + width // 3
        two_thirds_x = x_min + 2 * width // 3
        
        # Calculate point density in different regions
        upper_third = self.calculate_point_density(points, x_min, y_min, x_max, one_third_y)
        middle_third = self.calculate_point_density(points, x_min, one_third_y, x_max, two_thirds_y)
        lower_third = self.calculate_point_density(points, x_min, two_thirds_y, x_max, y_max)
        
        left_third = self.calculate_point_density(points, x_min, y_min, one_third_x, y_max)
        center_third = self.calculate_point_density(points, one_third_x, y_min, two_thirds_x, y_max)
        right_third = self.calculate_point_density(points, two_thirds_x, y_min, x_max, y_max)
        
        # Improved recognition algorithm
        
        # 1. Recognize digit 1: thin vertical line
        if aspect_ratio < 0.4 and height > 90:
            if center_third > num_points * 0.6:
                recognized = '1'
                self.result_label.config(text=f"识别结果: {recognized}")
                return
        
        # 2. Recognize digit 7: top-heavy with right side
        if top_half > bottom_half * 1.4:
            if right_half > left_half * 1.1 and upper_third > middle_third * 2:
                recognized = '7'
                self.result_label.config(text=f"识别结果: {recognized}")
                return
        
        # 3. Recognize digit 0: circular shape with edge points
        if 0.7 < aspect_ratio < 1.3 and height > 60:
            if edge_points > num_points * 0.35 and \
               q1 > num_points * 0.1 and q2 > num_points * 0.1 and \
               q3 > num_points * 0.1 and q4 > num_points * 0.1:
                # Check if center is relatively empty (hollow circle)
                center_density = self.calculate_point_density(points, center_x - 20, center_y - 20, center_x + 20, center_y + 20)
                if center_density < num_points * 0.2:
                    recognized = '0'
                    self.result_label.config(text=f"识别结果: {recognized}")
                    return
        
        # 4. Recognize digit 8: round with many points everywhere
        if num_points > 200 and 0.6 < aspect_ratio < 1.4:
            if upper_third > num_points * 0.25 and lower_third > num_points * 0.25:
                if q1 > num_points * 0.1 and q2 > num_points * 0.1 and \
                   q3 > num_points * 0.1 and q4 > num_points * 0.1:
                    recognized = '8'
                    self.result_label.config(text=f"识别结果: {recognized}")
                    return
        
        # 5. Recognize digit 4: wide with distinct parts
        if width > height * 1.1 and top_half < bottom_half * 1.5:
            if right_half > left_half * 1.05:
                if upper_third > num_points * 0.2 and lower_third > num_points * 0.3:
                    recognized = '4'
                    self.result_label.config(text=f"识别结果: {recognized}")
                    return
        
        # 6. Recognize digit 2: bottom-heavy, right side
        if bottom_half > top_half * 1.2:
            if right_half > left_half * 1.05:
                if lower_third > num_points * 0.4:
                    recognized = '2'
                    self.result_label.config(text=f"识别结果: {recognized}")
                    return
        
        # 7. Recognize digit 3: top-heavy, balanced sides
        if top_half > bottom_half * 1.1:
            if abs(left_half - right_half) < left_half * 0.4:
                if upper_third > num_points * 0.3 and middle_third > num_points * 0.2:
                    recognized = '3'
                    self.result_label.config(text=f"识别结果: {recognized}")
                    return
        
        # 8. Recognize digit 5: bottom-heavy, left side
        if bottom_half > top_half * 1.2:
            if left_half > right_half * 1.05:
                if upper_third > num_points * 0.25 and center_third > num_points * 0.2:
                    recognized = '5'
                    self.result_label.config(text=f"识别结果: {recognized}")
                    return
        
        # 9. Recognize digit 6: left side with curve at bottom
        if left_half > right_half * 1.2:
            if q3 > q1 * 1.1 and lower_third > num_points * 0.35:
                recognized = '6'
                self.result_label.config(text=f"识别结果: {recognized}")
                return
        
        # 10. Recognize digit 9: right side with curve at bottom
        if right_half > left_half * 1.2:
            if q4 > q2 * 1.1 and lower_third > num_points * 0.35:
                recognized = '9'
                self.result_label.config(text=f"识别结果: {recognized}")
                return
        
        # Smart fallback based on point density
        point_density = num_points / (width * height + 1) if (width * height) > 0 else 0
        
        if point_density < 0.015:
            # Low density points
            if aspect_ratio < 0.5:
                recognized = '1'
            elif aspect_ratio > 1.2:
                recognized = '4'
            else:
                recognized = '7'
        elif point_density < 0.03:
            # Medium-low density
            if aspect_ratio < 0.7:
                recognized = '1'
            elif aspect_ratio > 1.3:
                recognized = '4'
            elif top_half > bottom_half * 1.3:
                recognized = '7'
            else:
                recognized = '2'
        elif point_density < 0.05:
            # Medium density
            if aspect_ratio < 0.8:
                recognized = '2'
            elif aspect_ratio > 1.2:
                recognized = '5'
            else:
                recognized = '3'
        else:
            # High density
            if 0.7 < aspect_ratio < 1.3:
                recognized = '8'
            else:
                recognized = '0'
        
        self.result_label.config(text=f"识别结果: {recognized}")

if __name__ == "__main__":
    root = tk.Tk()
    app = UltraSimpleDigitRecognizer(root)
    root.mainloop()