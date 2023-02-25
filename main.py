import sys
import interface
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6 import uic, QtCore

dwell_time = 1000
coin_window = 2
update_timer = QtCore.QTimer()
taking_data = False

class MainWindow(QMainWindow):
    data_points_taken = 0
    data = []

    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.buttonTakeData.setCheckable(True)
        self.buttonTakeData.clicked.connect(lambda:self.toggleButton(self.buttonTakeData))
        self.buttonBrowseFile.clicked.connect(self.onBrowseFileClicked)
        global dwell_time
        dwell_time = interface.get_dwell_time()
        self.spinBoxDwellTime.setValue(dwell_time)
        update_timer.setInterval(dwell_time)
        self.spinBoxDwellTime.valueChanged.connect(self.updateDwellTime)
        global coin_window
        coin_window = interface.get_coin_window()
        self.spinBoxCoinWindow.setValue(coin_window)
        self.spinBoxCoinWindow.valueChanged.connect(self.updateCoinWindow)
        self.update()

    def update(self):
        self.countA.setText(str(interface.get_count_A()))
        self.countB.setText(str(interface.get_count_B()))
        self.countAB.setText(str(interface.get_count_AB()))
        global taking_data
        if taking_data:
            self.data.append((int(self.countA.text()), int(self.countB.text()), int(self.countAB.text()), dwell_time, coin_window))
            self.data_points_taken += 1
            if self.data_points_taken >= self.spinBoxNumPoints.value(): # make this save original value so it can be updated while taking data and not interfere with current run
                self.write_data()
                self.data = []
                self.buttonTakeData.setChecked(False)
                self.buttonTakeData.setText("Take Data")
                taking_data = False
                self.data_points_taken = 0

    def closeEvent(self, *args, **kwargs):
        super().closeEvent(*args, **kwargs)
        interface.close_connection()

    def toggleButton(self, button):
        if button == self.buttonTakeData:
            global taking_data
            taking_data = button.isChecked()
            self.data_points_taken = 0
            self.data = []
            if button.isChecked():
                button.setText("Abort")
            else:
                button.setText("Take Data")

    def onBrowseFileClicked(self):
        filename, _ = QFileDialog.getSaveFileName(parent=self, caption="Select output file", directory=".", filter="csv (*.csv)")
        if filename:
            if ".csv" != filename[-4:]:
                filename += ".csv"
            self.filePath.setText(filename)

    def updateDwellTime(self):
        global dwell_time
        dwell_time = self.spinBoxDwellTime.value()
        update_timer.setInterval(dwell_time)
        interface.set_dwell_time(dwell_time)

    def updateCoinWindow(self):
        global coin_window
        coin_window = self.spinBoxCoinWindow.value()
        interface.set_coin_window(coin_window)
        print(coin_window)

    def write_data(self):
        data_file = sys.stdout
        data_file_name = self.filePath.text()
        if data_file_name != "":
            data_file = open(data_file_name, "w") # test to make sure doesn't fail, close file

        print("N(A),N(B),N(AB),update_time,coincidence_window", file=data_file)
        for point in self.data:
            print(",".join(map(str, point)), file=data_file)

        if data_file != sys.stdout:
            data_file.close()


if __name__ == "__main__":
    interface.open_connection()
    app = QApplication(sys.argv)

    mainWindow = MainWindow()

    update_timer.timeout.connect(mainWindow.update)
    update_timer.start(dwell_time)

    mainWindow.show()

    sys.exit(app.exec())
