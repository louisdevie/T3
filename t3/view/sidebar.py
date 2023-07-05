from PySide6.QtWidgets import QFrame, QPushButton, QHBoxLayout, QLabel
from PySide6 import QtCore

from data.resources.theme import Theme


class SideBar:
    class Shadow(QFrame):
        def __init__(self, parent=None):
            super().__init__(parent, objectName="sidebar-shadow")

    def __init__(self, parent=None):
        self.__shadow = self.Shadow(parent)

    def add_to_grid(self, grid_layout):
        grid_layout.addWidget(self.__shadow, 0, 1, 2, 1)
