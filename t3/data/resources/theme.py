import logging

from PySide6.QtCore import QFile, QTextStream
from PySide6.QtGui import QIcon


class Theme:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self):
        self.__file = ""
        self.__cache = {}

    def apply_stylesheet(self, qt_object):
        stylesheet = ""

        if "stylesheet" in self.__cache:
            stylesheet = self.__cache["stylesheet"]
        else:
            source = QFile(":/style.qss")
            if source.open(QFile.ReadOnly | QFile.Text):
                stream = QTextStream(source)
                stylesheet = stream.readAll()
                source.close()

                self.__cache["stylesheet"] = stylesheet

        qt_object.setStyleSheet(stylesheet)

    def icon(self, name):
        if not "icons" in self.__cache:
            self.__cache["icons"] = {}

        if "missing" in self.__cache["icons"]:
            return self.__cache["icon"]["missing"]
        else:
            icon = QIcon(":/icons/missing.png")
            self.__cache["icons"]["missing"] = icon
            return icon
