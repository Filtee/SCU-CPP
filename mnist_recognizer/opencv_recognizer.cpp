#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>
#include <string>

using namespace cv;
using namespace std;

// 数字识别函数
int recognizeDigit(const Mat& digitImage) {
    // 确保图像是二值化的
    Mat binary;
    if (digitImage.channels() > 1) {
        cvtColor(digitImage, binary, COLOR_BGR2GRAY);
        threshold(binary, binary, 128, 255, THRESH_BINARY_INV);
    } else {
        binary = digitImage.clone();
        if (mean(binary)[0] > 128) {
            threshold(binary, binary, 128, 255, THRESH_BINARY_INV);
        }
    }

    // 获取图像的宽高
    int height = binary.rows;
    int width = binary.cols;
    double aspectRatio = static_cast<double>(width) / height;

    // 计算像素分布
    int totalPixels = countNonZero(binary);
    int leftPixels = 0, rightPixels = 0, topPixels = 0, bottomPixels = 0;
    int centerX = width / 2;
    int centerY = height / 2;

    // 计算四个象限的像素数
    int q1 = 0, q2 = 0, q3 = 0, q4 = 0;

    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            if (binary.at<uchar>(y, x) == 255) {
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

    // 计算边缘像素比例
    int edgePixels = 0;
    int edgeWidth = max(1, min(width, height) / 5);
    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            if (binary.at<uchar>(y, x) == 255) {
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
    // 读取图片
    Mat image = imread("drawn_digit.png");
    if (image.empty()) {
        cerr << "无法读取图片文件 drawn_digit.png" << endl;
        return 1;
    }

    // 显示原始图片
    namedWindow("原始图片", WINDOW_NORMAL);
    resizeWindow("原始图片", 300, 300);
    imshow("原始图片", image);

    // 预处理图片
    Mat gray, binary;
    cvtColor(image, gray, COLOR_BGR2GRAY);
    threshold(gray, binary, 128, 255, THRESH_BINARY_INV);

    // 寻找轮廓
    vector<vector<Point>> contours;
    findContours(binary, contours, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);

    if (contours.empty()) {
        cerr << "未找到数字轮廓" << endl;
        waitKey(0);
        return 1;
    }

    // 寻找最大轮廓（假设只有一个数字）
    int maxAreaIdx = 0;
    double maxArea = contourArea(contours[0]);
    for (size_t i = 1; i < contours.size(); i++) {
        double area = contourArea(contours[i]);
        if (area > maxArea) {
            maxArea = area;
            maxAreaIdx = i;
        }
    }

    // 获取数字区域的边界框
    Rect boundingBox = boundingRect(contours[maxAreaIdx]);
    Mat digitImage = gray(boundingBox);

    // 显示数字区域
    namedWindow("数字区域", WINDOW_NORMAL);
    resizeWindow("数字区域", 300, 300);
    imshow("数字区域", digitImage);

    // 识别数字
    int recognizedDigit = recognizeDigit(digitImage);

    if (recognizedDigit == -1) {
        cout << "无法识别数字" << endl;
    } else {
        cout << "识别结果: " << recognizedDigit << endl;
    }

    // 等待按键
    waitKey(0);

    return 0;
}