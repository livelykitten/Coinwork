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
from Monitor import *


# from style_py import *
# import style_py

class Monitor(QObject):
    @Slot()
    def __init__(self):
        super().__init__()
        self.criteria_id = 1
        self.criteria = []
        self.message = deque()

    @Slot(result = bool)
    def message_left(self):
        if (len(self.message)) == 0:
            return False
        return True

    @Slot(result=str)
    def get_message(self):
        return self.message.pop()

    # @Slot()
    def update_messages(self, msg):
        for m in msg:
            self.message.append(json.dumps(m.__dict__))
        return

    @Slot()
    def monitor(self):
        new_messages = []
        markets = UpbitWrapper.get_all_markets()
        if markets == None:
            return

        r_dict = UpbitWrapper.get_tickers(markets)
        if r_dict == None:
            return

        market_tickers = {} # dict, key: market code
        for market in r_dict:
            cur_price = market['trade_price']
            timestamp = market['timestamp']  / 1e3
            item = Ticker(markets[market['market']], 0, cur_price, timestamp)
            market_tickers[market['market']] = item

        for criterion in self.criteria:
            new_messages.extend(criterion.update_monitors(market_tickers))

        self.update_messages(new_messages)

        return

    @Slot(float, float, float, result = int)
    def add_criteria(self, d_ratio, d_time, cooldown):
        new_criteria = Criteria(self.criteria_id, d_ratio, d_time, cooldown)
        self.criteria_id += 1
        self.criteria.append(new_criteria)
        return self.criteria_id - 1

    # def list_criteria(self):
    # 	text = ""
    # 	self.criteria_lock.acquire(blocking=True)
    # 	for c in self.criteria:
    # 		text += f"알람 ID: {c.cid} 변화율: {c.d_ratio * 100}% 시간 간격: {datetime.timedelta(seconds=c.d_time)} 알람 주기: {datetime.timedelta(seconds=c.cooldown)}"
    # 	self.criteria_lock.release()
    # 	return text

    @Slot(int, result = int)
    def remove_criteria(self, cid):
        i = 0
        for i in range(len(self.criteria)):
            if self.criteria[i].cid == cid:
                self.criteria.pop(i)
                return True
        return False

    # def list_messages(self):
    # 	text = ""
    # 	self.message_lock.acquire(blocking=True)
    # 	for item in self.message:
    # 		text += "-----------------------------------------------\n"
    # 		text += str(datetime.datetime.fromtimestamp(item.time)) + "\n"
    # 		text += item.text + "\n"
    # 	self.message_lock.release()
    # 	return text

if __name__ != "__main__":
    sys.exit(1)

# os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
sys.argv += ['--style', 'Material']

app = QGuiApplication(sys.argv)
engine = QQmlApplicationEngine()

bridge = Monitor()

context = engine.rootContext()
context.setContextProperty("monitor", bridge)


engine.load(os.path.join(os.path.dirname(__file__), "main.qml"))

if not engine.rootObjects():
    sys.exit(-1)
sys.exit(app.exec_())
