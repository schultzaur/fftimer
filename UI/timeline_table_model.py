# https://doc.qt.io/qtforpython/tutorials/datavisualize/index.html

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QEvent
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QItemDelegate

import util
from Models.callout import Callout

TIMESTAMP_COLUMN = 0
CALLOUT_COLUMN = 1
COLUMN_COUNT = 2


class TimelineTableModel(QAbstractTableModel):
    def __init__(self, parent, data=None):
        QAbstractTableModel.__init__(self)
        self.parent = parent
        self.callouts = data.copy() if data else []

    def rowCount(self, parent=QModelIndex()):
        return len(self.callouts)

    def columnCount(self, parent=QModelIndex()):
        return COLUMN_COUNT

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return ("Time (s)", "Callout (uncheck to suppress)")[section]
        else:
            return str(section)

    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        row = index.row()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if column == TIMESTAMP_COLUMN:
                return util.format_ms(self.callouts[row].timestamp)
            elif column == CALLOUT_COLUMN:
                return self.callouts[row].description
        elif role == Qt.CheckStateRole:
            if column == CALLOUT_COLUMN:
                return int(Qt.Checked) if self.callouts[row].active else int(Qt.Unchecked)
        elif role == Qt.BackgroundRole:
            return QColor(Qt.white)
        elif role == Qt.TextAlignmentRole:
            if column == TIMESTAMP_COLUMN:
                return int(Qt.AlignRight)
            elif column == CALLOUT_COLUMN:
                return int(Qt.AlignLeft)

        return None

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            if index.column() == TIMESTAMP_COLUMN:
                self.callouts[index.row()].timestamp = float(value) * 1000
            if index.column() == CALLOUT_COLUMN:
                self.callouts[index.row()].description = value
            return True
        elif role == Qt.CheckStateRole:
            self.callouts[index.row()].active = value == int(Qt.Checked)
            return True
        return False

    def flags(self, index):
        if index.column() == CALLOUT_COLUMN:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsEditable
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def add_callout(self, callout):
        self.beginInsertRows(QModelIndex(), len(self.callouts), len(self.callouts))
        self.callouts.append(callout)
        self.endInsertRows()
        return True

    def clear_rows(self):
        if len(self.callouts) > 0:
            self.beginRemoveRows(QModelIndex(), 0, len(self.callouts)-1)
            self.callouts.clear()
            self.endRemoveRows()

    def set_rows(self, callouts):
        self.beginInsertRows(QModelIndex(), len(self.callouts), len(self.callouts) + len(callouts) - 1)
        self.callouts.extend(callouts)
        self.endInsertRows()


if __name__ == "__main__":
    import sys
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QFrame, QHeaderView, QHBoxLayout, QTableView, QSizePolicy, QApplication

    # Qt Application
    app = QApplication()

    test_data = [Callout(i, "test"+str(i), i % 2 == 0, "a", "b", "C") for i in range(100)]
    model = TimelineTableModel(test_data)
    view = QTableView()
    view.setModel(model)

    # QTableView Headers
    resize = QHeaderView.ResizeToContents
    view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    view.horizontalHeader().setStretchLastSection(True)
    view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    # QWidget Layout
    main_layout = QHBoxLayout()
    size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    # Left layout
    size.setHorizontalStretch(1)
    view.setSizePolicy(size)

    main_layout.addWidget(view)

    frame = QFrame()
    frame.setLayout(main_layout)
    frame.resize(300,600)
    frame.show()

    sys.exit(app.exec())
