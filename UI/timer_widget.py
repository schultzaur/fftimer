from PySide6 import QtCore, QtGui, QtWidgets

import util

STOPPED = 1
PAUSED = 2
RUNNING = 3

class TimerWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(TimerWidget, self).__init__()
        self.parent = parent

        self.elapsed_ms = 0
        self.state = STOPPED

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_timer)
        self.elapsed_timer = QtCore.QElapsedTimer()

        frame = QtWidgets.QFrame(self)
        grid_layout = QtWidgets.QGridLayout(self)

        self.timer_label = QtWidgets.QLabel("0.00s")
        font = self.timer_label.font()
        font.setPointSize(32)
        self.timer_label.setFont(font)
        self.timer_label.setAlignment(QtCore.Qt.AlignRight)

        self.add_second_button = QtWidgets.QPushButton("+1s")
        self.sub_second_button = QtWidgets.QPushButton("-1s")
        self.start_button = QtWidgets.QPushButton("Start")
        self.lap_button = QtWidgets.QPushButton("Add Call")
        self.reset_button = QtWidgets.QPushButton("Reset")

        self.add_second_button.clicked.connect(self.add_second_button_clicked)
        self.sub_second_button.clicked.connect(self.sub_second_button_clicked)
        self.start_button.clicked.connect(self.start_button_clicked)
        self.lap_button.clicked.connect(self.lap_button_clicked)
        self.reset_button.clicked.connect(self.reset_button_clicked)

        grid_layout.addWidget(self.timer_label, 0, 0, 2, 3)
        grid_layout.addWidget(self.sub_second_button, 2, 0, 1, 1)
        grid_layout.addWidget(self.add_second_button, 2, 2, 1, 1)

        grid_layout.addWidget(self.start_button, 0, 3, 1, 1)
        grid_layout.addWidget(self.lap_button, 1, 3, 1, 1)
        grid_layout.addWidget(self.reset_button, 2, 3, 1, 1)
        frame.setLayout(grid_layout)
        self.setLayout(grid_layout)

        self.playback_row = 0

    def add_second_button_clicked(self):
        self.set_elapsed_ms(self.elapsed_ms + 1000)

    def sub_second_button_clicked(self):
        self.set_elapsed_ms(self.elapsed_ms - 1000)

    def set_elapsed_ms(self, elapsed_ms):
        self.elapsed_ms = elapsed_ms
        self.update_timer_label()

        self.playback_row = 0

        while self.playback_row < self.parent.table_model.rowCount() and\
            self.elapsed_ms > self.parent.table_model.callouts[self.playback_row].timestamp:
            self.playback_row += 1

        self.parent.select_row(self.playback_row)

    def update_timer_label(self):
        self.timer_label.setText(util.format_ms(self.elapsed_ms)+"s")

    def update_timer(self):
        self.elapsed_ms += self.elapsed_timer.restart()
        self.update_timer_label()

        row_updated = False

        while self.playback_row < self.parent.table_model.rowCount() and\
            self.elapsed_ms > self.parent.table_model.callouts[self.playback_row].timestamp:
            self.playback_row += 1
            row_updated = True

        if row_updated:
            self.parent.select_row(self.playback_row)

    def start_button_clicked(self, event):
        if self.state == STOPPED:
            self.timer.start()
            self.elapsed_timer.start()
            self.start_button.setText("Pause")
            self.state = RUNNING

            self.parent.select_row(0)
        elif self.state == RUNNING:
            self.timer.stop()
            self.start_button.setText("Resume")
            self.state = PAUSED
        elif self.state == PAUSED:
            self.timer.start()
            self.elapsed_timer.restart()
            self.start_button.setText("Pause")
            self.state = RUNNING

    def lap_button_clicked(self, event):
        if self.state == RUNNING:
            self.parent.lap_button_clicked(self.elapsed_ms)

    def reset(self):
        self.timer.stop()
        self.timer_label.setText("0.00s")
        self.start_button.setText("Start")
        self.state = STOPPED
        self.elapsed_ms = 0
        self.playback_row = 0

    def reset_button_clicked(self, event):
        self.reset()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    box = QtWidgets.QGroupBox()
    layout = QtWidgets.QVBoxLayout()
    widget = TimerWidget(box)
    layout.addWidget(widget)
    box.setLayout(layout)
    box.resize(300, 200)
    box.show()

    sys.exit(app.exec())
