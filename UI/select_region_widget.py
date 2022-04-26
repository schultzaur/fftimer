import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class SelectRegionWidget(QWidget):
    # https://stackoverflow.com/questions/34567869/pyqt-take-screenshot-of-certain-screen-area
    # Refer to https://github.com/harupy/snipping-tool

    def __init__(self, parent=None, app=None):
        super(SelectRegionWidget, self).__init__()
        self.parent = parent
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.is_snipping = False
        self.screen = app.primaryScreen()
        self.setGeometry(0, 0, self.screen.size().width(), self.screen.size().height())
        self.begin = QPoint()
        self.end = QPoint()
        self.on_region_selected = None
        self.region = 0

    def start(self, region):
        self.region = region
        self.is_snipping = True
        self.setWindowOpacity(0.3)
        QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
        self.show()

    def reset(self):
        self.region = 0
        self.begin = QPoint()
        self.end = QPoint()

    def paintEvent(self, event):
        if self.is_snipping:
            brush_color = (128, 128, 255, 100)
            lw = 3
            opacity = 0.3
        else:
            self.reset()
            brush_color = (0, 0, 0, 0)
            lw = 0
            opacity = 0

        self.setWindowOpacity(opacity)
        qp = QPainter(self)
        qp.setPen(QPen(QColor('black'), lw))
        qp.setBrush(QColor(*brush_color))
        rect = QRectF(self.begin, self.end)
        qp.drawRect(rect)

    def mousePressEvent(self, event):
        self.begin = event.globalPosition()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.globalPosition()
        self.update()

    def mouseReleaseEvent(self, event):
        self.is_snipping = False
        QApplication.restoreOverrideCursor()
        x1 = min(self.begin.x(), self.end.x()) * self.devicePixelRatio()
        y1 = min(self.begin.y(), self.end.y()) * self.devicePixelRatio()
        x2 = max(self.begin.x(), self.end.x()) * self.devicePixelRatio()
        y2 = max(self.begin.y(), self.end.y()) * self.devicePixelRatio()

        if self.on_region_selected is not None:
            self.on_region_selected(self.region, (x1, y1, x2, y2))

        self.reset()
        self.close()

    def dragEnterEvent(self, event):
        event.acceptProposedAction()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    box = QFrame()
    layout = QVBoxLayout()
    button = QPushButton("Select Region")
    label = QLabel("")
    layout.addWidget(button)
    layout.addWidget(label)
    box.setLayout(layout)
    box.show()

    def onRegionSelected(x1, x2, y1, y2):
        box.setWindowState(Qt.WindowActive)
        label.setText(str(f"x1: {x1}, x2: {x2}, y1: {y1}, y2: {y2}"))

    widget = SelectRegionWidget(app=QApplication.instance())
    widget.onRegionSelected = onRegionSelected

    def selectRegion(self):
        box.setWindowState(Qt.WindowMinimized)
        widget.start()

    button.clicked.connect(selectRegion)

    sys.exit(app.exec())