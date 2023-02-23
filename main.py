import sys
import interface
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6 import uic, QtCore

dwell_time = 1000
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
        self.update()

    def update(self):
        self.countA.setText(str(interface.get_count_A()))
        self.countB.setText(str(interface.get_count_B()))
        self.countAB.setText(str(interface.get_count_AB()))
        global taking_data
        if taking_data:
            self.data.append(self.countA.text())
            self.data_points_taken += 1
            if self.data_points_taken >= self.spinBoxNumPoints.value(): # make this save original value so it can be updated while taking data and not interfere with current run
                data_file = sys.stdout
                data_file_name = self.filePath.text()
                if data_file_name != "":
                    data_file = open(data_file_name, "w") # test to make sure doesn't fail
                print(str(self.data), file=data_file)
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


if __name__ == "__main__":
    interface.open_connection()
    app = QApplication(sys.argv)

    mainWindow = MainWindow()

    update_timer.timeout.connect(mainWindow.update)
    update_timer.start(dwell_time)

    mainWindow.show()

    sys.exit(app.exec())
