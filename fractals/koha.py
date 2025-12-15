from PyQt5.QtGui import QImage, QPainter, QPen, QColor, QPixmap
import math

class KochGenerator:
    def __init__(self, width=900, height=600):
        self.width = width
        self.height = height

    def koch_curve(self, x1, y1, x2, y2, level, painter):
        if level == 0:
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            return

        dx = (x2 - x1) / 3
        dy = (y2 - y1) / 3

        xA = x1 + dx
        yA = y1 + dy

        xB = x1 + 2 * dx
        yB = y1 + 2 * dy

        angle = math.atan2(yB - yA, xB - xA) - math.pi / 3
        dist = math.sqrt(dx**2 + dy**2)
        xC = xA + math.cos(angle) * dist
        yC = yA + math.sin(angle) * dist

        self.koch_curve(x1, y1, xA, yA, level - 1, painter)
        self.koch_curve(xA, yA, xC, yC, level - 1, painter)
        self.koch_curve(xC, yC, xB, yB, level - 1, painter)
        self.koch_curve(xB, yB, x2, y2, level - 1, painter)

    def generate(self, level=4, thickness=1, type="snowflake"):
        img = QImage(self.width, self.height, QImage.Format_RGB32)
        img.fill(QColor(255, 255, 255))

        painter = QPainter(img)
        pen = QPen(QColor(0, 0, 0), thickness)
        painter.setPen(pen)

        margin = 50

        if type == "line":
            x1, y1 = margin, self.height // 2
            x2, y2 = self.width - margin, self.height // 2
            self.koch_curve(x1, y1, x2, y2, level, painter)
            yield QPixmap.fromImage(img)

        elif type == "snowflake":
            x1, y1 = margin, self.height - margin
            x2, y2 = self.width - margin, self.height - margin
            x3 = (x1 + x2) / 2
            y3 = self.height - margin - math.sqrt(3)/2 * (x2 - x1)

            sides = [(x1, y1, x2, y2), (x2, y2, x3, y3), (x3, y3, x1, y1)]
            for x_start, y_start, x_end, y_end in sides:
                self.koch_curve(x_start, y_start, x_end, y_end, level, painter)
                yield QPixmap.fromImage(img)

        painter.end()
        yield QPixmap.fromImage(img)