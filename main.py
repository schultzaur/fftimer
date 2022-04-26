if __name__ == '__main__':
    import sys
    from PySide6 import QtWidgets
    from UI import main_pane
    app = QtWidgets.QApplication(sys.argv)

    box = QtWidgets.QGroupBox()
    v_layout = QtWidgets.QVBoxLayout()
    widget = main_pane.MainPane(box)
    v_layout.addWidget(widget)
    box.setLayout(v_layout)
    box.resize(1280, 720)
    box.show()
    sys.exit(app.exec())
