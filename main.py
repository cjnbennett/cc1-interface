import sys
import interface
import serial.tools.list_ports
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6 import uic, QtCore
from PyQt6.QtCore import QThread
import serial_controller
from collections import Counter

dwell_time = 1000
coin_window = 2
update_timer = QtCore.QTimer()
taking_data = False
dets = [None, None]      # [det1, det2]
chan_A = [0,0]          # [detector, channel] -- both indexed from 0
chan_B = [0,1]
chan_Bprime = [1,0]
sc = None

class MainWindow(QMainWindow):
    data_points_taken = 0
    data = []

    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)

        global chan_A, chan_B, chan_Bprime
        chan_A = channelize(self.comboBoxChanA.currentIndex())
        chan_B = channelize(self.comboBoxChanB.currentIndex())
        chan_Bprime = channelize(self.comboBoxChanBprime.currentIndex())
        self.comboBoxChanA.currentIndexChanged.connect(self.updateChannels)
        self.comboBoxChanB.currentIndexChanged.connect(self.updateChannels)
        self.comboBoxChanBprime.currentIndexChanged.connect(self.updateChannels)

        self.buttonTakeData.setCheckable(True)
        self.buttonTakeData.clicked.connect(lambda:self.toggleButton(self.buttonTakeData))
        self.buttonBrowseFile.clicked.connect(self.onBrowseFileClicked)

        self.buttonReconnect.clicked.connect(self.reconnect)

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

        global sc
        sc = serial_controller.SerialController([])
        self.task_thread = QThread()
        sc.moveToThread(self.task_thread)
        self.task_thread.started.connect(sc.start)
        sc.finished.connect(self.task_thread.quit)
        sc.finished.connect(self.task_thread.deleteLater)
        self.task_thread.finished.connect(self.task_thread.deleteLater)
        self.task_thread.start()

        self.update()

    def update(self):
        ports = [comport.device for comport in serial.tools.list_ports.comports()]
        if Counter(ports) != Counter(self.comboBoxPortDet1.itemText(i) for i in range(self.comboBoxPortDet1.count()) if self.comboBoxPortDet1.itemText(i) != ""):
            old_port = self.comboBoxPortDet1.currentText()
            self.comboBoxPortDet1.clear()
            self.comboBoxPortDet1.addItem("")
            self.comboBoxPortDet1.addItems(ports)
            if old_port in [self.comboBoxPortDet1.itemText(i) for i in range(self.comboBoxPortDet1.count())]:
                self.comboBoxPortDet1.setCurrentText(old_port)
            else:
                if dets[0]:
                    dets[0].close_connection()

        if Counter(ports) != Counter(self.comboBoxPortDet2.itemText(i) for i in range(self.comboBoxPortDet2.count()) if self.comboBoxPortDet2.itemText(i) != ""):
            old_port = self.comboBoxPortDet2.currentText()
            self.comboBoxPortDet2.clear()
            self.comboBoxPortDet2.addItem("")
            self.comboBoxPortDet2.addItems(ports)
            if old_port in [self.comboBoxPortDet2.itemText(i) for i in range(self.comboBoxPortDet2.count())]:
                self.comboBoxPortDet2.setCurrentText(old_port)
            else:
                if dets[1]:
                    dets[1].close_connection()

        global taking_data
        if not taking_data:
            sc.add_task(self.get_counts)

        if taking_data:
            sc.add_task(self.take_data)
            if self.data_points_taken >= self.spinBoxNumPoints.value(): # make this save original value so it can be updated while taking data and not interfere with current run
                self.write_data()
                self.data = []
                self.buttonTakeData.setChecked(False)
                self.buttonTakeData.setText("Take Data")
                taking_data = False
                self.data_points_taken = 0

    def closeEvent(self, *args, **kwargs):
        super().closeEvent(*args, **kwargs)
        sc.interrupt()
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

    def updateChannels(self):
        global chan_A, chan_B, chan_Bprime
        chan_A = channelize(self.comboBoxChanA.currentIndex())
        chan_B = channelize(self.comboBoxChanB.currentIndex())
        chan_Bprime = channelize(self.comboBoxChanBprime.currentIndex())

    def reconnect(self):
        port = self.comboBoxPortDet1.currentText()
        if port != "":
            if dets[0]:
                dets[0].close_connection()
            dets[0] = interface.Connection(port)
            dets[0].set_trigger(interface.Trigger.CONTINUOUS)
        port = self.comboBoxPortDet2.currentText()
        if port != "":
            if dets[1]:
                dets[1].close_connection()
            dets[1] = interface.Connection(port)
            dets[1].set_trigger(interface.Trigger.CONTINUOUS)

    def get_counts(self):
        if chan_A and dets[chan_A[0]]:
            nA = dets[chan_A[0]].get_count(chan_A[1])
        else:
            nA = 0
        if chan_B and dets[chan_B[0]]:
            nB = dets[chan_B[0]].get_count(chan_B[1])
        else:
            nB = 0
        if chan_Bprime and dets[chan_Bprime[0]]:
            nBprime = dets[chan_Bprime[0]].get_count(chan_Bprime[1])
        else:
            nBprime = 0
        if chan_A and chan_B and dets[chan_A[0]] and dets[chan_B[0]]:
            if chan_A[0] == chan_B[0]:
                nAB = dets[chan_A[0]].get_count_coin()
            else:
                nAB = 0
        else:
            nAB = 0
        if chan_B and chan_Bprime and dets[chan_B[0]] and dets[chan_Bprime[0]]:
            if chan_B[0] == chan_Bprime[0]:
                nBBprime = dets[chan_B[0]].get_count_coin() # if
            else:
                nBBprime = 0
        else:
            nBBprime = 0
        nABBprime = 0
        self.countA.setText(str(nA))
        self.countB.setText(str(nB))
        self.countAB.setText(str(nAB))
        self.countBprime.setText(str(nBprime))
        self.countBBprime.setText(str(nBBprime))
        self.countABBprime.setText(str(nABBprime))
        return nA, nB, nBprime, nAB, nBBprime, nABBprime

    def take_data(self):
        self.data.append((*self.get_counts(), dwell_time, coin_window))
        self.data_points_taken += 1

    def write_data(self):
        data_file = sys.stdout
        data_file_name = self.filePath.text()
        if data_file_name != "":
            data_file = open(data_file_name, "w") # test to make sure doesn't fail

        print("N(A),N(B),N(B'),N(AB),N(BB'),N(ABB'),update_time,coincidence_window", file=data_file)
        for point in self.data:
            print(",".join(map(str, point)), file=data_file)

        if data_file != sys.stdout:
            data_file.close()


def channelize(i):
    if i == 1:
        return [0,0]
    elif i == 2:
        return [0,1]
    elif i == 3:
        return [1,0]
    elif i == 4:
        return [1,1]
    return None

if __name__ == "__main__":
    app = QApplication(sys.argv)

    mainWindow = MainWindow()

    update_timer.timeout.connect(mainWindow.update)
    update_timer.start(dwell_time)

    mainWindow.show()

    sys.exit(app.exec())
