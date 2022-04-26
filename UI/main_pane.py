import os
import uuid

from PIL import ImageGrab
from PySide6 import QtCore, QtWidgets

import util

from Models.callout import Callout
from UI.controls_widget import ControlsWidget
from UI.timeline_table_model import TimelineTableModel
from UI.preview_pane import PreviewPane
from UI.timer_widget import TimerWidget
from UI.select_region_widget import SelectRegionWidget


REGION_CAPTURE = 1
REGION_CAST_BAR = 2

SCREENSHOTS_FOLDER = os.path.join(util.BASE_PATH, "screenshots")


class MainPane(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self)

        self.parent = parent
        self.callout_count = 0
        self.threads = []
        self.workers = []

        self.timer_widget: TimerWidget = None
        self.table_model: TimelineTableModel = None
        self.settings_widget: ControlsWidget = None
        self.capture_region = None
        self.cast_bar_region = None
        self.current_row = None

        main_layout = QtWidgets.QHBoxLayout()

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        left_panel = QtWidgets.QFrame(self)
        layout = QtWidgets.QVBoxLayout(self)

        layout.addWidget(self.setup_timers())
        layout.addWidget(self.setup_table())
        layout.addWidget(self.setup_settings())
        left_panel.setLayout(layout)

        self.preview_pane = PreviewPane(self, r"C:\Users\clara\Downloads\finallycontent.gif")

        self.splitter.addWidget(left_panel)
        self.splitter.addWidget(self.preview_pane)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        main_layout.addWidget(self.splitter)
        self.setLayout(main_layout)

        if not os.path.exists(SCREENSHOTS_FOLDER):
            os.mkdir(SCREENSHOTS_FOLDER)

        self.select_region_widget = SelectRegionWidget(app=QtWidgets.QApplication.instance())
        self.select_region_widget.on_region_selected = self.on_region_selected

    def setup_timers(self):
        self.timer_widget = TimerWidget(self)
        return self.timer_widget

    def setup_table(self):
        self.table_model = TimelineTableModel(self)
        self.table_view = QtWidgets.QTableView()
        self.table_view.setModel(self.table_model)

        resize = QtWidgets.QHeaderView.ResizeToContents
        self.table_view.horizontalHeader().setSectionResizeMode(resize)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.verticalHeader().setSectionResizeMode(resize)

        self.table_view.verticalHeader().sectionDoubleClicked.connect(self.on_row_double_clicked)

        self.table_view.selectionModel().currentRowChanged.connect(self.table_row_changed)

        return self.table_view

    def setup_settings(self):
        self.settings_widget = ControlsWidget(self)
        return self.settings_widget

    def select_row(self, row):
        if row >= self.table_model.rowCount():
            return

        old_index = self.table_view.selectionModel().currentIndex()
        new_index = self.table_model.index(row, 0)
        self.table_view.selectionModel().select(
            new_index,
            QtCore.QItemSelectionModel.Rows | QtCore.QItemSelectionModel.ClearAndSelect)
        self.table_view.selectionModel().currentRowChanged.emit(new_index, old_index)

    def update_on_finish(self, callout):
        self.table_model.add_callout(callout)
        self.select_row(self.table_model.rowCount() - 1)

    def lap_button_clicked(self, elapsed_ms):
        class Worker(QtCore.QObject):
            finished = QtCore.Signal()

            def __init__(self, data):
                QtCore.QObject.__init__(self)
                self.data = data

            def run(self):
                (worker_callout, capture_region, cast_bar_region) = self.data

                ImageGrab.grab(bbox=capture_region).save(worker_callout.screen_image_path)
                ImageGrab.grab(bbox=cast_bar_region).save(worker_callout.cast_image_path)
                self.finished.emit()

        file_id = str(uuid.uuid4())
        callout = Callout(
            timestamp=elapsed_ms,
            description="Some Mechanic",
            active=True,
            notes="",
            screen_image_path=os.path.join(SCREENSHOTS_FOLDER, f"{file_id}_capture.png"),
            cast_image_path=os.path.join(SCREENSHOTS_FOLDER, f"{file_id}_cast_bar.png"))

        self.callout_count += 1

        thread = QtCore.QThread()
        worker = Worker((callout, self.capture_region, self.cast_bar_region))

        self.threads.append(thread)
        self.workers.append(worker)

        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: self.update_on_finish(callout))
        thread.start()

    def on_row_double_clicked(self, row):
        self.timer_widget.set_elapsed_ms(self.table_model.callouts[row].timestamp)

    def on_region_selected(self, region, bbox):
        self.setWindowState(QtCore.Qt.WindowActive)

        if region == REGION_CAPTURE:
            self.capture_region = bbox
        elif region == REGION_CAST_BAR:
            self.cast_bar_region = bbox
        (x1, y1, x2, y2) = bbox
        print(str(f"region: {region}, x1: {x1}, x2: {x2}, y1: {y1}, y2: {y2}"))

    def select_region(self, region):
        self.setWindowState(QtCore.Qt.WindowMinimized)
        self.select_region_widget.start(region)

    def select_capture_region(self):
        self.select_region(REGION_CAPTURE)

    def select_cast_bar_region(self):
        self.select_region(REGION_CAST_BAR)

    def table_row_changed(self, current, previous):
        self.current_row = current.row()
        callout = self.table_model.callouts[current.row()]
        self.preview_pane.update_callout(callout)

    def playback_phase(self):
        return


if __name__ == '__main__':
    import os
    import sys
    app = QtWidgets.QApplication(sys.argv)

    box = QtWidgets.QGroupBox()
    vlayout = QtWidgets.QVBoxLayout()
    widget = MainPane(box)
    vlayout.addWidget(widget)
    box.setLayout(vlayout)
    box.resize(1280, 720)
    box.show()

    sys.exit(app.exec())
