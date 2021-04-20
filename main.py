# This Python file uses the following encoding: utf-8
import sys
import os

import time

import json
import datetime
from collections import deque

from os.path import abspath, dirname, join

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

import UpbitWrapper
import Monitor


# from style_py import *
# import style_py

class MonitorBridge(QObject):
    @Slot()
    def __init__(self):
        super().__init__()
        self.monitor = Monitor.Monitor()
        self.monitor.start()
        return

    @Slot(result=str)
    def get_messages_str(self):
        return self.monitor.get_messages()

    @Slot(float, float, float, result=int)
    def add_criteria(self, d_ratio, d_time, cooldown):
        return self.monitor.add_criteria(d_ratio, d_time, cooldown)

    @Slot(int, result=bool)
    def remove_criteria(self, cid):
        return self.monitor.remove_criteria(cid)

if __name__ != "__main__":
    sys.exit(1)

# os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
sys.argv += ['--style', 'Material', "--platform", "windows:dpiawareness=0"]

app = QGuiApplication(sys.argv)
engine = QQmlApplicationEngine()

bridge = MonitorBridge()

context = engine.rootContext()
context.setContextProperty("monitor", bridge)


engine.load(os.path.join(os.path.dirname(__file__), "main.qml"))

if not engine.rootObjects():
    sys.exit(-1)
sys.exit(app.exec_())
