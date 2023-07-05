import sys
import logging

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from logic import Logger
from data.resources import Resource, Theme
from view import MainWindow

from t3ff import Counter

if __name__ == "__main__":
    Logger.setup()

    app = QApplication(sys.argv)

    QFontDatabase.addApplicationFont(":/fonts/LibertySans.ttf")
    Theme().apply_stylesheet(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
