import dataclasses
import os
import json

from PySide6 import QtWidgets
from PySide6 import QtGui

import util
from Models.callout import Callout

class ControlsWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(ControlsWidget, self).__init__()
        self.parent = parent

        grid_layout = QtWidgets.QGridLayout(self)

        self.set_export_button = QtWidgets.QPushButton("Export (clipboard)")
        self.set_capture_region_button = QtWidgets.QPushButton("Set Capture Region")
        self.set_cast_bar_region_button = QtWidgets.QPushButton("Set Cast Bar Region")
        self.set_save_folder_button = QtWidgets.QPushButton("Set Save Folder")

        self.phase_name = QtWidgets.QLineEdit("untitled")
        self.new_phase_button = QtWidgets.QPushButton("New Phase")
        self.save_phase_button = QtWidgets.QPushButton("Save Phase")
        self.open_phase_button = QtWidgets.QPushButton("Open Phase")

        grid_layout.addWidget(self.set_export_button, 0, 0, 1, 1)
        grid_layout.addWidget(self.set_capture_region_button, 1, 0, 1, 1)
        grid_layout.addWidget(self.set_cast_bar_region_button, 2, 0, 1, 1)
        grid_layout.addWidget(self.set_save_folder_button, 3, 0, 1, 1)
        grid_layout.addWidget(self.phase_name, 0, 1, 1, 1)
        grid_layout.addWidget(self.new_phase_button, 1, 1, 1, 1)
        grid_layout.addWidget(self.save_phase_button, 2, 1, 1, 1)
        grid_layout.addWidget(self.open_phase_button, 3, 1, 1, 1)

        self.setLayout(grid_layout)

        self.set_export_button.clicked.connect(self.export)
        self.set_capture_region_button.clicked.connect(self.parent.select_capture_region)
        self.set_cast_bar_region_button.clicked.connect(self.parent.select_cast_bar_region)
        #self.play_phase_button.clicked.connect(self.parent.playback_phase)

        grid_layout.addWidget(self.new_phase_button, 1, 1, 1, 1)
        self.new_phase_button.clicked.connect(self.new_phase)
        self.save_phase_button.clicked.connect(self.save_phase)
        self.open_phase_button.clicked.connect(self.open_phase)

    def export(self, event):
        callouts_txt = ""

        for callout in self.parent.table_model.callouts:
            if callout.active:
                callouts_txt += f"{util.format_ms(callout.timestamp)}\t{callout.description}\n"

        QtGui.QGuiApplication.clipboard().setText(callouts_txt, mode=QtGui.QClipboard.Mode.Clipboard)

    def new_phase(self):
        self.phase_name.setText("new phase")
        self.parent.timer_widget.reset()
        self.parent.table_model.clear_rows()

    def save_phase(self):
        path = os.path.join(util.BASE_PATH, f"{self.phase_name.text()}.json")
        with open(path, 'w') as f:
            json.dump([dataclasses.asdict(callout) for callout in self.parent.table_model.callouts], f)

    def open_phase(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setDirectory(str(util.BASE_PATH))
        file_name = file_dialog.getOpenFileName(self, 'OpenFile')[0]

        if not file_name:
            return

        callout_dicts = []
        with open(file_name, 'r') as f:
            callout_dicts = json.load(f)

        callouts = [
            Callout(
                timestamp=c["timestamp"],
                description=c["description"],
                active=c["active"],
                notes=c["notes"],
                screen_image_path=c["screen_image_path"],
                cast_image_path=c["cast_image_path"])
            for c in callout_dicts]

        self.parent.timer_widget.reset()
        self.parent.table_model.clear_rows()
        self.parent.table_model.set_rows(callouts)

        self.phase_name.setText(os.path.splitext(os.path.basename(file_name))[0])

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    box = QtWidgets.QGroupBox()
    layout = QtWidgets.QVBoxLayout()
    widget = ControlsWidget(box)
    layout.addWidget(widget)
    box.setLayout(layout)
    box.resize(200, 200)
    box.show()

    sys.exit(app.exec())
