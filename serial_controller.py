from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from time import sleep
import os


class SerialController(QObject):
    tasks = []
    started = pyqtSignal()
    finished = pyqtSignal()
    task_loop = QTimer()

    def __init__(self, tasks):
        super().__init__()
        self.tasks = tasks
        self.started.connect(self.start_timer)

    def start(self):
        self.started.emit()

    def start_timer(self):
        self.task_loop.timeout.connect(self.run)
        self.task_loop.start(1)

    def run(self):
        if self.tasks:
            task = self.tasks.pop(0)
            task()

    def add_task(self, task):
        self.tasks.append(task)

    def interrupt(self):
        self.task_loop.stop()
        self.task_loop.timeout.disconnect(self.run)
        self.finished.emit()
