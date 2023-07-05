from PySide6.QtWidgets import QFrame, QPushButton, QHBoxLayout, QLabel
from PySide6 import QtCore

from data.resources.theme import Theme


class Header(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent, objectName="header")

        self.setFixedHeight(50)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 0, 0, 0)

        self.__menu_button = QPushButton(Theme().icon("menu"), "", flat=True)
        self.__menu_button.setFixedSize(34, 34)
        self.layout.addWidget(self.__menu_button)

        self.__title = QLabel("Test")
        self.layout.addWidget(self.__title)

    def add_to_grid(self, grid_layout):
        grid_layout.addWidget(self, 0, 0, 1, 2)
