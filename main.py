# This Python file uses the following encoding: utf-8
import sys
import os

from os.path import abspath, dirname, join

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

# from style_py import *
# import style_py

class Bridge(QObject):
    @Slot()
    def __init__(self):
        super().__init__()
        self.val = 0
        return

    @Slot()
    def update(self):
        self.val += 1
        return

    @Slot(result=str)
    def get(self):
        return str(self.val)

if __name__ != "__main__":
    sys.exit(1)

# os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
sys.argv += ['--style', 'Material']

app = QGuiApplication(sys.argv)
engine = QQmlApplicationEngine()

bridge = Bridge()

context = engine.rootContext()
context.setContextProperty("monitor", bridge)


engine.load(os.path.join(os.path.dirname(__file__), "main.qml"))

if not engine.rootObjects():
    sys.exit(-1)
sys.exit(app.exec_())
