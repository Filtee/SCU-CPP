#include <Windows.h>
#include <gdiplus.h>
#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>

#pragma comment(lib, "gdiplus.lib")

using namespace Gdiplus;
using namespace std;

// 辅助函数：计算指定区域内的点密度
int CalculatePointDensity(const vector<POINT>& points, int xMin, int yMin, int xMax, int yMax) {
    int count = 0;
    for (const POINT& p : points) {
        if (p.x >= xMin && p.x <= xMax && p.y >= yMin && p.y <= yMax) {
            count++;
        }
    }
    return count;
}

// 辅助函数：计算中心矩
double CalculateCentralMoment(const vector<POINT>& points, int centerX, int centerY, int p, int q) {
    double moment = 0.0;
    for (const POINT& point : points) {
        double dx = point.x - centerX;
        double dy = point.y - centerY;
        moment += pow(dx, p) * pow(dy, q);
    }
    return moment;
}

// 辅助函数：将像素点转换为二值化点
vector<POINT> GetPixelPoints(const Bitmap& bitmap) {
    vector<POINT> points;
    Rect rect(0, 0, bitmap.GetWidth(), bitmap.GetHeight());
    BitmapData bitmapData;
    
    if (bitmap.LockBits(&rect, ImageLockModeRead, PixelFormat32bppARGB, &bitmapData) == Ok) {
        BYTE* pixels = static_cast<BYTE*>(bitmapData.Scan0);
        
        for (int y = 0; y < bitmap.GetHeight(); y++) {
            for (int x = 0; x < bitmap.GetWidth(); x++) {
                int index = (y * bitmapData.Stride) + (x * 4);
                BYTE blue = pixels[index];
                BYTE green = pixels[index + 1];
                BYTE red = pixels[index + 2];
                BYTE alpha = pixels[index + 3];
                
                // 检查是否是黑色像素点
                if (red < 100 && green < 100 && blue < 100 && alpha > 100) {
                    POINT p = { x, y };
                    points.push_back(p);
                }
            }
        }
        
        bitmap.UnlockBits(&bitmapData);
    }
    
    return points;
}

// 手写数字识别函数
char RecognizeDigit(const vector<POINT>& points) {
    int numPoints = points.size();
    if (numPoints == 0) return '0';

    // Calculate point distribution
    int xMin = points[0].x;
    int xMax = points[0].x;
    int yMin = points[0].y;
    int yMax = points[0].y;

    for (const POINT& p : points) {
        if (p.x < xMin) xMin = p.x;
        if (p.x > xMax) xMax = p.x;
        if (p.y < yMin) yMin = p.y;
        if (p.y > yMax) yMax = p.y;
    }

    int width = xMax - xMin;
    int height = yMax - yMin;
    double aspectRatio = height != 0 ? static_cast<double>(width) / height : 0;

    // Calculate center
    int centerX = (xMin + xMax) / 2;
    int centerY = (yMin + yMax) / 2;

    // Count points in four quadrants
    int q1 = 0, q2 = 0, q3 = 0, q4 = 0;
    int topHalf = 0, bottomHalf = 0;
    int leftHalf = 0, rightHalf = 0;

    for (const POINT& p : points) {
        if (p.x < centerX && p.y < centerY) q1++;
        if (p.x >= centerX && p.y < centerY) q2++;
        if (p.x < centerX && p.y >= centerY) q3++;
        if (p.x >= centerX && p.y >= centerY) q4++;
        if (p.y < centerY) topHalf++;
        if (p.y >= centerY) bottomHalf++;
        if (p.x < centerX) leftHalf++;
        if (p.x >= centerX) rightHalf++;
    }

    // Calculate edge points (more precise)
    int edgePoints = 0;
    for (const POINT& p : points) {
        if (abs(p.x - xMin) < 15 || abs(p.x - xMax) < 15 ||
            abs(p.y - yMin) < 15 || abs(p.y - yMax) < 15) {
            edgePoints++;
        }
    }
    
    // 计算数字的三分之一和三分之二位置
    int oneThirdY = yMin + height / 3;
    int twoThirdsY = yMin + 2 * height / 3;
    int oneThirdX = xMin + width / 3;
    int twoThirdsX = xMin + 2 * width / 3;
    
    // 计算不同区域的点密度
    int upperThird = CalculatePointDensity(points, xMin, yMin, xMax, oneThirdY);
    int middleThird = CalculatePointDensity(points, xMin, oneThirdY, xMax, twoThirdsY);
    int lowerThird = CalculatePointDensity(points, xMin, twoThirdsY, xMax, yMax);
    
    int leftThird = CalculatePointDensity(points, xMin, yMin, oneThirdX, yMax);
    int centerThird = CalculatePointDensity(points, oneThirdX, yMin, twoThirdsX, yMax);
    int rightThird = CalculatePointDensity(points, twoThirdsX, yMin, xMax, yMax);
    
    // 计算中心矩（简单版本）
    double m00 = numPoints;
    double m01 = CalculateCentralMoment(points, centerX, centerY, 0, 1);
    double m10 = CalculateCentralMoment(points, centerX, centerY, 1, 0);
    double m11 = CalculateCentralMoment(points, centerX, centerY, 1, 1);
    
    // 更精确的识别算法
    
    // 1. 识别数字 1: 细长的垂直线
    if (aspectRatio < 0.4 && height > 90) {
        // 检查是否主要由中间垂直线组成
        if (centerThird > numPoints * 0.6) {
            return '1';
        }
    }
    
    // 2. 识别数字 7: 顶部有横杠，向右下方延伸
    if (topHalf > bottomHalf * 1.4) {
        if (rightHalf > leftHalf * 1.1 && upperThird > middleThird * 2) {
            return '7';
        }
    }
    
    // 3. 识别数字 0: 圆形，边缘有较多点
    if (aspectRatio > 0.7 && aspectRatio < 1.3 && height > 60) {
        if (edgePoints > numPoints * 0.35 && 
            q1 > numPoints * 0.1 && q2 > numPoints * 0.1 &&
            q3 > numPoints * 0.1 && q4 > numPoints * 0.1) {
            // 检查中心是否相对空白（空心圆）
            int centerDensity = CalculatePointDensity(points, centerX - 20, centerY - 20, centerX + 20, centerY + 20);
            if (centerDensity < numPoints * 0.2) {
                return '0';
            }
        }
    }
    
    // 4. 识别数字 8: 圆形，有上下两个环
    if (numPoints > 200 && aspectRatio > 0.6 && aspectRatio < 1.4) {
        if (upperThird > numPoints * 0.25 && lowerThird > numPoints * 0.25) {
            if (q1 > numPoints * 0.1 && q2 > numPoints * 0.1 &&
                q3 > numPoints * 0.1 && q4 > numPoints * 0.1) {
                return '8';
            }
        }
    }
    
    // 5. 识别数字 4: 宽扁，有明显的三个部分
    if (width > height * 1.1 && topHalf < bottomHalf * 1.5) {
        if (rightHalf > leftHalf * 1.05) {
            if (upperThird > numPoints * 0.2 && lowerThird > numPoints * 0.3) {
                return '4';
            }
        }
    }
    
    // 6. 识别数字 2: 底部向右延伸，整体呈曲线
    if (bottomHalf > topHalf * 1.2) {
        if (rightHalf > leftHalf * 1.05) {
            if (lowerThird > numPoints * 0.4) {
                return '2';
            }
        }
    }
    
    // 7. 识别数字 3: 顶部有两个凸起，底部一个凸起
    if (topHalf > bottomHalf * 1.1) {
        if (abs(leftHalf - rightHalf) < leftHalf * 0.4) {
            if (upperThird > numPoints * 0.3 && middleThird > numPoints * 0.2) {
                return '3';
            }
        }
    }
    
    // 8. 识别数字 5: 顶部有横杠，中间有凸起
    if (bottomHalf > topHalf * 1.2) {
        if (leftHalf > rightHalf * 1.05) {
            if (upperThird > numPoints * 0.25 && centerThird > numPoints * 0.2) {
                return '5';
            }
        }
    }
    
    // 9. 识别数字 6: 左下方有曲线，整体向左倾斜
    if (leftHalf > rightHalf * 1.2) {
        if (q3 > q1 * 1.1 && lowerThird > numPoints * 0.35) {
            return '6';
        }
    }
    
    // 10. 识别数字 9: 右下方有曲线，整体向右倾斜
    if (rightHalf > leftHalf * 1.2) {
        if (q4 > q2 * 1.1 && lowerThird > numPoints * 0.35) {
            return '9';
        }
    }
    
    // 更智能的回退策略
    double pointDensity = static_cast<double>(numPoints) / (width * height + 1);
    
    if (pointDensity < 0.015) {
        // 低密度点
        if (aspectRatio < 0.5) return '1';
        else if (aspectRatio > 1.2) return '4';
        else return '7';
    } else if (pointDensity < 0.03) {
        // 中低密度点
        if (aspectRatio < 0.7) return '1';
        else if (aspectRatio > 1.3) return '4';
        else if (topHalf > bottomHalf * 1.3) return '7';
        else return '2';
    } else if (pointDensity < 0.05) {
        // 中密度点
        if (aspectRatio < 0.8) return '2';
        else if (aspectRatio > 1.2) return '5';
        else return '3';
    } else {
        // 高密度点
        if (aspectRatio > 0.7 && aspectRatio < 1.3) return '8';
        else return '0';
    }
    
    return '0'; // 默认值（理论上不会到达这里）
}

int main() {
    // 初始化GDI+
    GdiplusStartupInput gdiplusStartupInput;
    ULONG_PTR gdiplusToken;
    GdiplusStartup(&gdiplusToken, &gdiplusStartupInput, NULL);

    try {
        // 读取PNG文件
        Bitmap bitmap(L"d:\\识别手写数字\\drawn_digit.png");
        
        if (bitmap.GetLastStatus() != Ok) {
            cout << "无法打开图片文件 drawn_digit.png" << endl;
            GdiplusShutdown(gdiplusToken);
            return 1;
        }

        // 获取像素点
        vector<POINT> points = GetPixelPoints(bitmap);
        
        if (points.empty()) {
            cout << "图片中没有检测到黑色像素点" << endl;
            GdiplusShutdown(gdiplusToken);
            return 1;
        }

        // 识别数字
        char result = RecognizeDigit(points);
        
        // 输出结果
        cout << "识别结果: " << result << endl;
        cout << "点数量: " << points.size() << endl;
        
    } catch (const exception& e) {
        cout << "发生错误: " << e.what() << endl;
    }

    // 关闭GDI+
    GdiplusShutdown(gdiplusToken);
    
    // 等待用户输入
    cout << "按Enter键退出..." << endl;
    cin.get();
    
    return 0;
}