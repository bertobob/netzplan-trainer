from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen,QColor
from PyQt6.QtGui import QTransform
from PyQt6.QtCore import Qt

class InputCanvas(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lines = []  # Liste von Linien [(x1, y1, x2, y2, rgb)]

    def add_line(self, x1, y1, x2, y2, rgb):
        self.lines.append((x1, y1, x2, y2, rgb))  # Farbe pro Linie gespeichert
        self.update()

    def remove_lines(self):
        self.lines = []

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for line in self.lines:
            x1, y1, x2, y2, rgb = line
            pen = QPen(QColor(*rgb))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(x1, y1, x2, y2)
    