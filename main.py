import sys
import interface
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6 import uic, QtCore

dwell_time = 1000
coin_window = 2
update_timer = QtCore.QTimer()
taking_data = False
dets = [None, None]      # [det1, det2]
chan_A = [0,0]          # [detector, channel] -- both indexed from 0
chan_B = [0,1]
chan_Bprime = [1,0]

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
        if dets[0]:
            dwell_time = dets[0].get_dwell_time()
            if dets[1]:
                dets[1].set_dwell_time(dwell_time)
        elif dets[1]:
            dwell_time = dets[1].get_dwell_time()
        self.spinBoxDwellTime.setValue(dwell_time)
        update_timer.setInterval(dwell_time)
        self.spinBoxDwellTime.valueChanged.connect(self.updateDwellTime)
        global coin_window
        if dets[0]:
            coin_window = dets[0].get_coin_window()
            if dets[1]:
                dets[1].set_coin_window(coin_window)
        elif dets[1]:
            coin_window = dets[1].get_coin_window()
        self.spinBoxCoinWindow.setValue(coin_window)
        self.spinBoxCoinWindow.valueChanged.connect(self.updateCoinWindow)
        self.update()

    def update(self):
        if dets[chan_A[0]]:
            self.countA.setText(str(dets[chan_A[0]].get_count(chan_A[1])))
        if dets[chan_B[0]]:
            self.countB.setText(str(dets[chan_B[0]].get_count(chan_B[1])))
        if dets[chan_Bprime[0]]:
            self.countBprime.setText(str(dets[chan_Bprime[0]].get_count(chan_Bprime[1])))
        self.countBprime.setText("0")
        self.countAB.setText("0")
        self.countBBprime.setText("0")
        self.countABBprime.setText("0")
        # self.countAB.setText(str(.get_count_coin()))
        # self.countBBprime.setText(str(.get_count_BBprime()))
        # self.countABBprime.setText(str(.get_count_ABBprime()))
        global taking_data
        if taking_data:
            self.data.append((int(self.countA.text()), int(self.countB.text()), int(self.countAB.text()), int(self.countBprime.text()), int(self.countBBprime.text()), int(self.countABBprime.text()), dwell_time, coin_window))
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
        for det in dets:
            if det:
                det.close_connection()

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
        for det in dets:
            if det:
                det.set_dwell_time(dwell_time)

    def updateCoinWindow(self):
        global coin_window
        coin_window = self.spinBoxCoinWindow.value()
        for det in dets:
            if det:
                det.set_coin_window(coin_window)
        print(coin_window)

    def write_data(self):
        data_file = sys.stdout
        data_file_name = self.filePath.text()
        if data_file_name != "":
            data_file = open(data_file_name, "w") # test to make sure doesn't fail

        print("N(A),N(B),N(AB),N(B'),N(BB'),N(ABB'),update_time,coincidence_window", file=data_file)
        for point in self.data:
            print(",".join(map(str, point)), file=data_file)

        if data_file != sys.stdout:
            data_file.close()


if __name__ == "__main__":
    dets[0] = interface.Connection("/dev/ttyACM0")
    # dets[1] = interface.Connection("/dev/ttyACM1")
    app = QApplication(sys.argv)

    mainWindow = MainWindow()

    update_timer.timeout.connect(mainWindow.update)
    update_timer.start(dwell_time)

    mainWindow.show()

    sys.exit(app.exec())
