import time
import threading

import json
import datetime
from collections import deque
import os

import UpbitWrapper


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
    def __init__(self, market_name, market_cap, price, timestamp, acc_tp):
        self.market_name = market_name
        self.market_cap = market_cap
        self.price = price
        self.timestamp = timestamp
        self.acc_tp = acc_tp
        
class MarketMonitor:
    def __init__(self, change, market, interval, cooldown):
        self.market_code = market
        self.change = change
        self.interval = interval
        self.cooldown = cooldown
        self.container = deque()
        self.is_active = True
        self.time_disabled = 0

        self.max_item = None
        self.min_item = None
        
    def state_report(self):
        print('---------------')
        print(f"is_active: {self.is_active}")
        print(f"num_item: {len(self.container)}")
        for i in range(len(self.container)):
        	print(f"price: {self.container[i].price} time: {self.container[i].timestamp}")
        if self.min_item != None:
            print(f"min: {self.min_item.price} time: {self.min_item.timestamp}")
        print('---------------')
    
    def check_cooldown(self):
        # restore alarm if disabled
        if self.is_active == False:
            alarm_checked = False
            timestamp_now = datetime.datetime.now().timestamp()
            if self.time_disabled + self.cooldown < timestamp_now:
                self.is_active = True
    
    def update_ticker(self, new_item):

        self.check_cooldown()

        if len(self.container) == 0:
            self.container.append(new_item)
            return None
        
        first = self.container.popleft()
        self.container.appendleft(first)

        ins_idx = 0
        max_idx = 0
        outdated_idx = 0
        inserted = False
        outdated = False
        self.max_item = new_item
        self.min_item = new_item
        for i, item in enumerate(self.container):
            if item.timestamp == new_item.timestamp:
                return None
            if not outdated and \
                    item.timestamp + self.interval < first.timestamp or \
                    item.timestamp + self.interval < new_item.timestamp:
                outdated = True
                outdated_idx = i
            if not inserted and item.timestamp <= new_item.timestamp:
                ins_idx = i
                inserted = True
            if not outdated and self.max_item.price < item.price:
                self.max_item = item
            if not outdated and self.min_item.price > item.price:
                self.min_item = item
        
        if inserted:
            self.container.insert(ins_idx, new_item)
        else:
            self.container.append(new_item)

        outdated_item = None
        if outdated:
            outdated_item == self.container[outdated_idx]
            while len(self.container) >= outdated_idx and len(self.container) > 0:
                self.container.pop()
        
        if len(self.container) == 0:
            return None
        
        first = self.container.popleft()
        self.container.appendleft(first)
        
        cmp_item = None
        if self.change < 0:
            if outdated_item != None and outdated_item.price > self.max_item.price:
                cmp_item = outdated_item
            else:
                cmp_item = self.max_item
            highest_change = (new_item.price - cmp_item.price) / first.price
            time_taken = (new_item.timestamp - cmp_item.timestamp)
            if highest_change < self.change and time_taken > 0 and self.is_active:
                self.time_disabled = datetime.datetime.now().timestamp()
                self.is_active = False
                return Alarm(first.timestamp, self.market_code, first.market_name, 0, highest_change, time_taken, first.acc_tp)

        else:
            if outdated_item != None and outdated_item.price < self.min_item.price:
                cmp_item = outdated_item
            else:
                cmp_item = self.min_item
            
            highest_change = (new_item.price - cmp_item.price) / first.price
            time_taken = (new_item.timestamp - cmp_item.timestamp)
            if highest_change > self.change and time_taken > 0 and self.is_active:
                # self.state_report()
                # print(f"new p {new_item.price} new t {new_item.timestamp} cmp_item p {cmp_item.price} cmp_item t {cmp_item.timestamp}")
                self.time_disabled = datetime.datetime.now().timestamp()
                self.is_active = False
                return Alarm(first.timestamp, self.market_code, first.market_name, 0, highest_change, time_taken, first.acc_tp)
        
        return None

class Alarm:
    def __init__(self, time, market_code, market_name, market_cap, d_ratio, d_time, acc_tp):
        # text = market_code_to_kor[self.market_code] + "(" + self.market + "): "
        self.msg_timestamp = time
        self.msg_market = market_name + "(" + market_code + ")"
        self.msg_text = market_name + "(" + market_code + "): "
        # self.msg_text += "지난 " + tdstr(datetime.timedelta(seconds=d_time)) + " 동안"
        # self.msg_text += f"{d_ratio * 100:.3f}% 변화했습니다\n"
        self.msg_text += f"거래대금: {int(acc_tp / 1000000)}백만\n"
        self.user_checked = False
        # self.text += f"현재 시세는 {cur_price:.2f}, 현재 시간은 {datetime.datetime.fromtimestamp(time)} 입니다"
        # self.msg_text += f"현재 시간은 {datetime.datetime.fromtimestamp(time)} 입니다"
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
        # alarms = []
        for market, item in new_items.items():
            if market not in self.monitor_dict.keys():
                self.add_monitor(market)
            ret = self.monitor_dict[market].update_ticker(item)
            if ret != None:
                yield ret
        
        # return alarms


class Monitor():
    def __init__(self):
        super().__init__()
        self.criteria_id = 1
        self.criteria = []
        self.criteria_lock = threading.Lock()
        self.message = ""
        self.message_lock = threading.Lock()

    def message_left(self):
        if (len(self.message)) == 0:
            return False
        return True

    def get_messages(self):
        self.message_lock.acquire(blocking=True)
        ret = self.message
        self.message = ""
        self.message_lock.release()
        return ret
    
    

    def update_messages(self, msg):
        self.message_lock.acquire(blocking=True)
        
        for m in msg:
            if self.message == "":
                self.message = json.dumps(m.__dict__)
            else:
                self.message += "$" + json.dumps(m.__dict__)

        self.message_lock.release()
        return
    
    def _monitor_wrapper(self):
        prev = datetime.datetime.now()
        self._monitor()
        time_taken = (datetime.datetime.now() - prev).total_seconds()
        if time_taken < 0.1:
            threading.Timer(0.1 - time_taken, Monitor._monitor_wrapper, args=(self,)).start()
        else:
            threading.Thread(target=Monitor._monitor_wrapper, args=(self,)).start()
    
    def start(self):
        threading.Thread(target=Monitor._monitor_wrapper, args=(self,)).start()

    def _monitor(self):
        new_messages = []
        markets = UpbitWrapper.get_all_markets()
        if markets == None:
            return

        r_dict = UpbitWrapper.get_tickers(markets)
        if r_dict == None:
            return

        market_tickers = {} # dict, key: market code
        for market in r_dict:
            if "KRW" not in market['market']:
                continue
            cur_price = market['trade_price']
            timestamp = market['timestamp']  / 1e3
            item = Ticker(markets[market['market']], 0, cur_price, timestamp, market['acc_trade_price_24h'])
            market_tickers[market['market']] = item

        self.criteria_lock.acquire(blocking=True)
        for criterion in self.criteria:
            new_messages.extend(criterion.update_monitors(market_tickers))
        self.criteria_lock.release()

        self.update_messages(new_messages)

        return

    # @Slot(float, float, float, result = int)
    def add_criteria(self, d_ratio, d_time, cooldown):
        new_criteria = Criteria(self.criteria_id, d_ratio, d_time, cooldown)
        self.criteria_lock.acquire(blocking=True)
        cid = self.criteria_id
        self.criteria_id += 1
        self.criteria.append(new_criteria)
        self.criteria_lock.release()
        return cid

    # def list_criteria(self):
    # 	text = ""
    # 	self.criteria_lock.acquire(blocking=True)
    # 	for c in self.criteria:
    # 		text += f"알람 ID: {c.cid} 변화율: {c.d_ratio * 100}% 시간 간격: {datetime.timedelta(seconds=c.d_time)} 알람 주기: {datetime.timedelta(seconds=c.cooldown)}"
    # 	self.criteria_lock.release()
    # 	return text

    # @Slot(int, result = int)
    def remove_criteria(self, cid):
        i = 0
        self.criteria_lock.acquire(blocking=True)
        for i in range(len(self.criteria)):
            if self.criteria[i].cid == cid:
                self.criteria.pop(i)
                self.criteria_lock.release()
                return True
        self.criteria_lock.release()
        return False
    
    def end(self):
        os._exit(0)

    # def list_messages(self):
    # 	text = ""
    # 	self.message_lock.acquire(blocking=True)
    # 	for item in self.message:
    # 		text += "-----------------------------------------------\n"
    # 		text += str(datetime.datetime.fromtimestamp(item.time)) + "\n"
    # 		text += item.text + "\n"
    # 	self.message_lock.release()
    # 	return text
