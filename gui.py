import os
import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from UI.MainWindow import MainWindow


def main():
    dir = os.getcwd()
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    QApplication.processEvents()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")
        sys.exit(0)

if __name__ == "__main__":
    main()