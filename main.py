import sys
import interface
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic, QtCore

dwell_time = 1000
update_timer = QtCore.QTimer()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.update()

    def update(self):
        self.countA.setText(str(interface.get_count_A()))
        self.countB.setText(str(interface.get_count_B()))
        self.countAB.setText(str(interface.get_count_AB()))
        global dwell_time
        dwell_time = interface.get_dwell_time()
        update_timer.setInterval(dwell_time)

    def closeEvent(self, *args, **kwargs):
        super().closeEvent(*args, **kwargs)
        interface.close_connection()


if __name__ == "__main__":
    interface.open_connection()
    app = QApplication(sys.argv)

    mainWindow = MainWindow()

    update_timer.timeout.connect(mainWindow.update)
    update_timer.start(dwell_time)

    mainWindow.show()

    sys.exit(app.exec())
