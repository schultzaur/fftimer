from PySide6 import QtCore, QtGui, QtWidgets


class PreviewPane(QtWidgets.QWidget):
    def __init__(self, parent, file_path):
        QtWidgets.QWidget.__init__(self)
        self.current_callout = None

        self.parent = parent
        self.image = QtGui.QImage(file_path)

        self.layout = QtWidgets.QVBoxLayout(self)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.splitter.splitterMoved.connect(self.resize_image)

        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.image_label.setMinimumSize(1, 1)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.notes = QtWidgets.QTextEdit(self)
        self.notes.setBaseSize(50, 50)
        self.notes.textChanged.connect(self.notes_changed)

        self.splitter.addWidget(self.image_label)
        self.splitter.addWidget(self.notes)
        height = self.splitter.height()
        self.splitter.setSizes([height-50, 50])

        self.layout.addWidget(self.splitter)
        self.setMinimumSize(1, 1)

        self.setLayout(self.layout)

        self.resize_image()

    def resize_image(self, event=None):
        image = self.image.scaled(
            self.image_label.size(),
            aspectMode=QtCore.Qt.KeepAspectRatio,
            mode=QtCore.Qt.SmoothTransformation)
        self.image_label.setPixmap(QtGui.QPixmap.fromImage(image))

    def paintEvent(self, event):
        self.resize_image(event)

    def update_callout(self, callout):
        self.current_callout = callout
        self.image = QtGui.QImage(callout.screen_image_path)
        self.notes.setText(callout.notes)

    def notes_changed(self):
        self.current_callout.notes = self.notes.toPlainText()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    box = QtWidgets.QGroupBox()
    layout = QtWidgets.QVBoxLayout()
    widget = PreviewPane(
        box, r"C:\Users\clara\PycharmProjects\pythonProject\exampleScreenshots\ffxiv_dx11_SHHh24UZwO.jpg")
    layout.addWidget(widget)
    box.setLayout(layout)
    box.resize(800, 600)
    box.show()

    sys.exit(app.exec())
