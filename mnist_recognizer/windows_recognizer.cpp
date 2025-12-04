#include <windows.h>
#include <gdiplus.h>
#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>

using namespace Gdiplus;
using namespace std;

#pragma comment(lib, "gdiplus.lib")

// 初始化GDI+
int InitializeGDIPlus() {
    GdiplusStartupInput gdiplusStartupInput;
    ULONG_PTR gdiplusToken;
    return GdiplusStartup(&gdiplusToken, &gdiplusStartupInput, NULL);
}

// 关闭GDI+
void ShutdownGDIPlus(ULONG_PTR gdiplusToken) {
    GdiplusShutdown(gdiplusToken);
}

// 读取图片并转换为二值化图像
Bitmap* LoadAndBinarizeImage(const wchar_t* filename) {
    Bitmap* image = new Bitmap(filename);
    if (image->GetLastStatus() != Ok) {
        delete image;
        return NULL;
    }

    // 创建二值化图像
    Bitmap* binaryImage = new Bitmap(image->GetWidth(), image->GetHeight(), PixelFormat24bppRGB);
    Graphics* graphics = Graphics::FromImage(binaryImage);
    graphics->DrawImage(image, 0, 0);

    Color pixelColor;
    for (UINT y = 0; y < binaryImage->GetHeight(); y++) {
        for (UINT x = 0; x < binaryImage->GetWidth(); x++) {
            binaryImage->GetPixel(x, y, &pixelColor);
            int gray = (pixelColor.GetRed() + pixelColor.GetGreen() + pixelColor.GetBlue()) / 3;
            Color newColor = (gray < 128) ? Color(255, 0, 0, 0) : Color(255, 255, 255, 255);
            binaryImage->SetPixel(x, y, newColor);
        }
    }

    delete graphics;
    delete image;
    return binaryImage;
}

// 数字识别函数
int RecognizeDigit(Bitmap* binaryImage) {
    if (!binaryImage) return -1;

    UINT width = binaryImage->GetWidth();
    UINT height = binaryImage->GetHeight();
    double aspectRatio = static_cast<double>(width) / height;

    // 计算像素分布
    int totalPixels = 0;
    int leftPixels = 0, rightPixels = 0, topPixels = 0, bottomPixels = 0;
    int centerX = width / 2;
    int centerY = height / 2;

    // 计算四个象限的像素数
    int q1 = 0, q2 = 0, q3 = 0, q4 = 0;

    Color pixelColor;
    for (UINT y = 0; y < height; y++) {
        for (UINT x = 0; x < width; x++) {
            binaryImage->GetPixel(x, y, &pixelColor);
            if (pixelColor.GetRed() == 0 && pixelColor.GetGreen() == 0 && pixelColor.GetBlue() == 0) {
                totalPixels++;

                // 左右像素计数
                if (x < centerX) leftPixels++;
                else rightPixels++;

                // 上下像素计数
                if (y < centerY) topPixels++;
                else bottomPixels++;

                // 象限计数
                if (x < centerX && y < centerY) q1++;      // 左上
                else if (x >= centerX && y < centerY) q2++; // 右上
                else if (x < centerX && y >= centerY) q3++; // 左下
                else if (x >= centerX && y >= centerY) q4++; // 右下
            }
        }
    }

    if (totalPixels == 0) return -1;

    // 计算边缘像素比例
    int edgePixels = 0;
    int edgeWidth = max(1, static_cast<int>(min(width, height) / 5));
    for (UINT y = 0; y < height; y++) {
        for (UINT x = 0; x < width; x++) {
            binaryImage->GetPixel(x, y, &pixelColor);
            if (pixelColor.GetRed() == 0 && pixelColor.GetGreen() == 0 && pixelColor.GetBlue() == 0) {
                if (x < edgeWidth || x > width - edgeWidth || 
                    y < edgeWidth || y > height - edgeWidth) {
                    edgePixels++;
                }
            }
        }
    }

    double edgeRatio = static_cast<double>(edgePixels) / totalPixels;

    // 数字识别算法
    if (totalPixels < 100) {
        return -1; // 像素太少，无法识别
    } else if (aspectRatio < 0.35 && height > 50) {
        // 细长的数字，可能是1
        return 1;
    } else if (aspectRatio > 1.4 && width > 80) {
        // 宽扁的数字，可能是4
        return 4;
    } else if (edgeRatio > 0.6 && width > 40 && height > 40) {
        // 边缘像素比例高，可能是0
        return 0;
    } else {
        // 根据像素分布识别其他数字
        if (bottomPixels > topPixels * 1.2) {
            // 底部像素多
            if (rightPixels > leftPixels * 1.1) {
                return 2; // 右边像素多，可能是2
            } else if ((q3 + q4) > (q1 + q2) * 1.3) {
                return 8; // 下半部分像素特别多，可能是8
            } else {
                return 5; // 底部像素多但分布均匀，可能是5
            }
        } else if (topPixels > bottomPixels * 1.2) {
            // 顶部像素多
            if (q1 > q2 * 1.3) {
                return 7; // 左上像素多，可能是7
            } else {
                return 3; // 顶部像素分布均匀，可能是3
            }
        } else if (leftPixels > rightPixels * 1.2) {
            // 左边像素多，可能是6
            return 6;
        } else if (rightPixels > leftPixels * 1.2) {
            // 右边像素多，可能是9
            return 9;
        } else if (totalPixels > 3000) {
            // 像素非常多，可能是8
            return 8;
        } else {
            // 综合判断
            if (width > height * 1.1) {
                return 3;
            } else if (height > width * 1.1) {
                return 7;
            } else {
                return 0;
            }
        }
    }
}

int main() {
    // 初始化GDI+
    if (InitializeGDIPlus() != 0) {
        cout << "无法初始化GDI+" << endl;
        return 1;
    }

    // 读取图片
    const wchar_t* filename = L"drawn_digit.png";
    Bitmap* binaryImage = LoadAndBinarizeImage(filename);
    if (!binaryImage) {
        cout << "无法读取图片文件 drawn_digit.png" << endl;
        return 1;
    }

    // 识别数字
    int recognizedDigit = RecognizeDigit(binaryImage);

    if (recognizedDigit == -1) {
        cout << "无法识别数字" << endl;
    } else {
        cout << "识别结果: " << recognizedDigit << endl;
    }

    // 清理资源
    delete binaryImage;

    // 关闭GDI+
    ULONG_PTR gdiplusToken;
    ShutdownGDIPlus(gdiplusToken);

    return 0;
}