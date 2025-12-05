#include <QApplication>
#include <QMainWindow>
#include <QWidget>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QPushButton>
#include <QLabel>
#include <QPainter>
#include <QMouseEvent>
#include <QPoint>
#include <vector>
#include <algorithm>
#include <cmath>

class DigitRecognizerWidget : public QWidget {
    Q_OBJECT

public:
    DigitRecognizerWidget(QWidget *parent = nullptr) : QWidget(parent), drawing(false), currentColor(Qt::black) {
        setFixedSize(300, 300);
        setStyleSheet("background-color: white;");
    }

    void clear() {
        points.clear();
        update();
    }

    std::vector<QPoint>& getPoints() {
        return points;
    }

protected:
    void mousePressEvent(QMouseEvent *event) override {
        if (event->button() == Qt::LeftButton) {
            drawing = true;
            points.push_back(event->pos());
        }
    }

    void mouseMoveEvent(QMouseEvent *event) override {
        if (drawing && (event->buttons() & Qt::LeftButton)) {
            points.push_back(event->pos());
            update();
        }
    }

    void mouseReleaseEvent(QMouseEvent *event) override {
        if (event->button() == Qt::LeftButton) {
            drawing = false;
        }
    }

    void paintEvent(QPaintEvent *event) override {
        QPainter painter(this);
        painter.setPen(QPen(currentColor, 16, Qt::SolidLine, Qt::RoundCap, Qt::RoundJoin));

        for (int i = 1; i < points.size(); ++i) {
            painter.drawLine(points[i - 1], points[i]);
        }
    }

private:
    bool drawing;
    QColor currentColor;
    std::vector<QPoint> points;
};

class DigitRecognizer : public QMainWindow {
    Q_OBJECT

public:
    DigitRecognizer(QWidget *parent = nullptr) : QMainWindow(parent) {
        QWidget *centralWidget = new QWidget(this);
        setCentralWidget(centralWidget);

        QVBoxLayout *mainLayout = new QVBoxLayout(centralWidget);

        // Create drawing widget
        digitWidget = new DigitRecognizerWidget(this);
        mainLayout->addWidget(digitWidget);

        // Create buttons
        QHBoxLayout *buttonLayout = new QHBoxLayout();
        clearButton = new QPushButton("清空", this);
        recognizeButton = new QPushButton("识别", this);
        buttonLayout->addWidget(clearButton);
        buttonLayout->addWidget(recognizeButton);
        mainLayout->addLayout(buttonLayout);

        // Create result label
        resultLabel = new QLabel("请在画布上绘制数字", this);
        resultLabel->setAlignment(Qt::AlignCenter);
        mainLayout->addWidget(resultLabel);

        // Connect signals and slots
        connect(clearButton, &QPushButton::clicked, this, &DigitRecognizer::onClearButtonClicked);
        connect(recognizeButton, &QPushButton::clicked, this, &DigitRecognizer::onRecognizeButtonClicked);

        setWindowTitle("手写数字识别器");
        setGeometry(100, 100, 350, 450);
    }

private slots:
    void onClearButtonClicked() {
        digitWidget->clear();
        resultLabel->setText("请在画布上绘制数字");
    }

    void onRecognizeButtonClicked() {
        std::vector<QPoint> points = digitWidget->getPoints();
        if (points.empty()) {
            resultLabel->setText("请先绘制数字");
            return;
        }

        char recognized = recognizeDigit(points);
        resultLabel->setText(QString("识别结果: %1").arg(recognized));
    }

private:
    char recognizeDigit(const std::vector<QPoint>& points) {
        int numPoints = points.size();
        if (numPoints == 0) return '0';

        // Calculate point distribution
        int xMin = points[0].x();
        int xMax = points[0].x();
        int yMin = points[0].y();
        int yMax = points[0].y();

        for (const QPoint& p : points) {
            if (p.x() < xMin) xMin = p.x();
            if (p.x() > xMax) xMax = p.x();
            if (p.y() < yMin) yMin = p.y();
            if (p.y() > yMax) yMax = p.y();
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

        for (const QPoint& p : points) {
            if (p.x() < centerX && p.y() < centerY) q1++;
            if (p.x() >= centerX && p.y() < centerY) q2++;
            if (p.x() < centerX && p.y() >= centerY) q3++;
            if (p.x() >= centerX && p.y() >= centerY) q4++;
            if (p.y() < centerY) topHalf++;
            if (p.y() >= centerY) bottomHalf++;
            if (p.x() < centerX) leftHalf++;
            if (p.x() >= centerX) rightHalf++;
        }

        // Calculate edge points
        int edgePoints = 0;
        for (const QPoint& p : points) {
            if (abs(p.x() - xMin) < 20 || abs(p.x() - xMax) < 20 ||
                abs(p.y() - yMin) < 20 || abs(p.y() - yMax) < 20) {
                edgePoints++;
            }
        }

        // More accurate recognition algorithm based on point distribution
        
        // First, handle very distinct cases
        
        // 1. Recognize digit 1: thin vertical line
        if (aspectRatio < 0.3 && height > 100) {
            return '1';
        }
        
        // 2. Recognize digit 7: top-heavy with mostly right side
        if (topHalf > bottomHalf * 1.5 && rightHalf > leftHalf * 1.2) {
            return '7';
        }
        
        // 3. Recognize digit 4: wide with distinct top and bottom
        if (width > height && topHalf < bottomHalf * 1.2) {
            if (rightHalf > leftHalf * 1.1) {
                return '4';
            }
        }
        
        // 4. Recognize digit 0: circular shape with points around edges
        if (aspectRatio > 0.8 && aspectRatio < 1.2 && height > 70) {
            if (edgePoints > numPoints * 0.4 && 
                q1 > numPoints * 0.15 && q2 > numPoints * 0.15 &&
                q3 > numPoints * 0.15 && q4 > numPoints * 0.15) {
                return '0';
            }
        }
        
        // 5. Recognize digit 8: round with many points everywhere
        if (numPoints > 250 && aspectRatio > 0.7 && aspectRatio < 1.3) {
            if (q1 > numPoints * 0.1 && q2 > numPoints * 0.1 &&
                q3 > numPoints * 0.1 && q4 > numPoints * 0.1) {
                return '8';
            }
        }
        
        // 6. Recognize digit 2: bottom-heavy, right side
        if (bottomHalf > topHalf * 1.3 && rightHalf > leftHalf * 1.1) {
            return '2';
        }
        
        // 7. Recognize digit 3: top-heavy with balanced sides
        if (topHalf > bottomHalf * 1.2 && abs(leftHalf - rightHalf) < leftHalf * 0.3) {
            return '3';
        }
        
        // 8. Recognize digit 5: bottom-heavy, left side
        if (bottomHalf > topHalf * 1.3 && leftHalf > rightHalf * 1.1) {
            return '5';
        }
        
        // 9. Recognize digit 6: left side with curve at bottom
        if (leftHalf > rightHalf * 1.3 && q3 > q1 * 1.2) {
            return '6';
        }
        
        // 10. Recognize digit 9: right side with curve at bottom
        if (rightHalf > leftHalf * 1.3 && q4 > q2 * 1.2) {
            return '9';
        }
        
        // Fallback based on point count
        if (numPoints < 100) return '7';
        if (numPoints < 150) return '1';
        if (numPoints < 200) return '4';
        if (numPoints < 250) return '2';
        if (numPoints < 300) return '3';
        
        return '8'; // Default for many points
    }

    DigitRecognizerWidget *digitWidget;
    QPushButton *clearButton;
    QPushButton *recognizeButton;
    QLabel *resultLabel;
};

#include "digit_recognizer.moc"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    DigitRecognizer window;
    window.show();
    return app.exec();
}