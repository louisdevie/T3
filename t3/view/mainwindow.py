from PySide6.QtWidgets import QWidget, QLabel, QGridLayout
from PySide6 import QtCore

from .header import Header
from .sidebar import SideBar


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, objectName="window")

        self.setWindowTitle("T3")
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.__header = Header()
        self.__header.add_to_grid(self.layout)

        self.layout.addWidget(QWidget(), 1, 0, 1, 2)

        self.__sidebar = SideBar()
        self.__sidebar.add_to_grid(self.layout)
