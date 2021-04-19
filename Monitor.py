import time

import json
import datetime
from collections import deque
import ctypes
import os

from PySide6.QtCore import QObject


def tdstr(td):
    days = ""
    hours = ""
    minutes = ""
    seconds = "0"
    ms = ""
    if td.days != 0:
        days = f"{td.days}일 "
    if td.seconds // 3600 != 0:
        hours = f"{td.seconds // 3600}시간 "
    if  (td.seconds % 3600) // 60 != 0:
        minutes = f"{(td.seconds % 3600) // 60:0>2d}분 "
    if td.seconds % 60 != 0:
        seconds = f"{td.seconds % 60}"
    if td.microseconds != 0:
        ms = f".{td.microseconds:1.0f}"
    return days + hours + minutes + seconds + ms + "초"

class Ticker:
    def __init__(self, market_name, market_cap, price, timestamp):
        self.market_name = market_name
        self.market_cap = market_cap
        self.price = price
        self.timestamp = timestamp
        
class MarketMonitor:
    def __init__(self, change, market, interval, cooldown):
        self.market_code = market
        self.change = change
        self.interval = interval
        self.cooldown = cooldown
        self.container = deque()
        self.is_active = True
        self.time_disabled = 0
        
    def state_report(self):
        print('---------------')
        print(f"is_active: {self.is_active}")
        print(f"ALARM_SWITCH: {ALARM_SWITCH}")
        print(f"num_item: {len(self.container)}")
        #for i in range(len(self.container)):
        #	print(f"price: {self.container[i].price} time: {self.container[i].timestamp}")
        print('---------------')
    
    def update_ticker(self, item):
    
        # self.state_report()
        
        # print(f"newcomer: {item.timestamp}")
        # restore alarm if disabled
        if self.is_active == False:
            alarm_checked = False
            timestamp_now = datetime.datetime.now().timestamp()
            if self.time_disabled + self.cooldown < timestamp_now:
                self.is_active = True
        
        # add an item
        idx = 0
        if len(self.container) == 0:
            self.container.append(item)
            return None
        
        while idx < len(self.container) and \
            self.container[idx].timestamp >= item.timestamp:
            # print(f"<<comparing {self.container[idx].timestamp} and {item.timestamp}")
            if self.container[idx].timestamp == item.timestamp:
                return None
            idx += 1
        if idx == len(self.container):
            self.container.append(item)
        else:
            self.container.insert(idx, item)
        
        # determine the newest
        first = self.container.popleft()
        self.container.appendleft(first)
        
        # determine the last
        last = self.container.pop()
        if last.timestamp + self.interval > first.timestamp:
            self.container.append(last)
            return None
        
        # determine the last outranged
        outranged = last
        while last.timestamp + self.interval < item.timestamp and \
            last != item:
            outranged = last
            last = self.container.pop()
        
        self.container.append(last)
        
        true_interval = item.timestamp - outranged.timestamp
        true_change = (item.price - outranged.price) / item.price
        
        # if satisfies condition, send off an alarm
        if abs(true_change) > abs(self.change) and true_change * self.change > 0 and self.is_active:
            self.time_disabled = datetime.datetime.now().timestamp()
            self.is_active = False
            return Alarm(first.timestamp, self.market_code, first.market_name, 0, true_change, true_interval)
        return None

class Alarm:
    def __init__(self, time, market_code, market_name, market_cap, d_ratio, d_time):
        # text = market_code_to_kor[self.market_code] + "(" + self.market + "): "
        self.msg_timestamp = time
        self.msg_market = market_name + "(" + market_code + ")"
        self.msg_text = market_name + "(" + market_code + "): "
        self.msg_text += "지난 " + tdstr(datetime.timedelta(seconds=d_time)) + " 동안"
        self.msg_text += f"{d_ratio * 100:.3f}% 변화했습니다\n"
        # self.text += f"현재 시세는 {cur_price:.2f}, 현재 시간은 {datetime.datetime.fromtimestamp(time)} 입니다"
        self.msg_text += f"현재 시간은 {datetime.datetime.fromtimestamp(time)} 입니다"
    def __str__(self):
        return self.msg_text

class Criteria:
    def __init__(self, cid, d_ratio, d_time, cooldown):
        self.cid = cid
        self.d_ratio = d_ratio
        self.d_time = d_time
        self.cooldown = cooldown
        self.monitor_dict = {}

    def add_monitor(self, new_market):
        new_monitor = MarketMonitor(self.d_ratio, new_market, self.d_time, self.cooldown)
        self.monitor_dict[new_market] = new_monitor
            
    
    def update_monitors(self, new_items):
        alarms = []
        for market, item in new_items.items():
            if market not in self.monitor_dict.keys():
                self.add_monitor(market)
            ret = self.monitor_dict[market].update_ticker(item)
            if ret != None:
                alarms.append(ret)
        
        return alarms

# def monitor_init():
#     return

# def update_monitor():
#     monitor.monitor()

# def msg_left():
#     return monitor.message_left()

# def get_msg():
#     return monitor.get_message()

# def add_criteria(d_ratio, d_time, cooldown):
#     return monitor.add_criteria(d_ratio, d_time, cooldown)

# def remove_criteria(cid):
#     return monitor.remove_criteria(cid)
