import sys
import interface
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)

        self.countA.setText(str(interface.get_count_A()))
        self.countB.setText(str(interface.get_count_B()))
        self.countAB.setText(str(interface.get_count_AB()))


if __name__ == "__main__":
    interface.open_connection()
    app = QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.show()

    interface.close_connection()
    sys.exit(app.exec())
