import time
import threading

import json
import datetime
from collections import deque
import ctypes
import os

import UpbitWrapper
from playsound import playsound

ALARM_SWITCH = True
SOUND_SWITCH = True

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
		if abs(true_change) > self.change and true_change * self.change > 0 and self.is_active:
			self.time_disabled = datetime.datetime.now().timestamp()
			self.is_active = False
			return Alarm(first.timestamp, self.market_code, first.market_name, 0, true_change, true_interval)

class Alarm:
	def __init__(self, time, market_code, market_name, market_cap, d_ratio, d_time):
		# text = market_code_to_kor[self.market_code] + "(" + self.market + "): "
		self.time = time
		self.text = market_name + "(" + market_code + "): "
		self.text += "지난 " + tdstr(datetime.timedelta(seconds=d_time)) + " 동안"
		self.text += f"{d_ratio * 100:.3f}% 변화했습니다\n"
		# self.text += f"현재 시세는 {cur_price:.2f}, 현재 시간은 {datetime.datetime.fromtimestamp(time)} 입니다"
		self.text += f"현재 시간은 {datetime.datetime.fromtimestamp(time)} 입니다"
	def __str__(self):
		return self.text

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

class Monitor:
	def __init__(self):
		self.criteria_id = 1
		self.criteria = []
		self.criteria_lock = threading.Lock()
		self.message = deque()
		self.message_lock = threading.Lock()
		self.alarm_window_num = 0
		self.alarm_window_lock = threading.Lock()
	
	def update_messages(self, new_messages):
		self.message_lock.acquire(blocking=True)

		for msg in new_messages:
			idx = 0
			while idx < len(self.message) and msg.time >= self.message[idx].time:
				idx += 1
			if idx == len(self.message):
				self.message.append(msg)
			else:
				self.message.insert(idx, msg)
		
		if len(self.message) < 1:
			self.message_lock.release()
			return 
		
		first = self.message.popleft()
		self.message.appendleft(first)
		while len(self.message) > 0:
			last = self.message.pop()
			if last.time + 86400 > first.time:
				self.message.append(last)
				break
		
		self.message_lock.release()
		
	
	def alarm_thread_func(self, alarm):
		if SOUND_SWITCH:
			playsound('./alarm.wav')
		if not ALARM_SWITCH or self.alarm_window_num > 10:
			return
		self.alarm_window_lock.acquire(blocking=True)
		self.alarm_window_num += 1
		self.alarm_window_lock.release()
		ctypes.windll.user32.MessageBoxW(0, alarm.text, "알림", 0)
		self.alarm_window_lock.acquire(blocking=True)
		self.alarm_window_num -= 1
		self.alarm_window_lock.release()
	
	def send_alarm(self, alarm):
		threading.Thread(target=Monitor.alarm_thread_func, args=(self, alarm)).start()

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
			item = Ticker(markets[market['market']], 0, cur_price, timestamp)
			market_tickers[market['market']] = item

		self.criteria_lock.acquire(blocking=True)
		for criterion in self.criteria:
			new_messages.extend(criterion.update_monitors(market_tickers))
		self.criteria_lock.release()

		self.update_messages(new_messages)
	
		for msg in new_messages:
			self.send_alarm(msg)
		
		return

	def _monitor_wrapper(self):
		self._monitor()
		threading.Timer(0.05, Monitor._monitor_wrapper, args=(self,)).start()
	
	def start(self):
		threading.Thread(target=Monitor._monitor_wrapper, args=(self,)).start()

	def add_criteria(self, d_ratio, d_time, cooldown):
		new_criteria = Criteria(self.criteria_id, d_ratio, d_time, cooldown)
		self.criteria_id += 1
		self.criteria_lock.acquire(blocking=True)
		self.criteria.append(new_criteria)
		self.criteria_lock.release()
		return self.criteria_id - 1

	def list_criteria(self):
		text = ""
		self.criteria_lock.acquire(blocking=True)
		for c in self.criteria:
			text += f"알람 ID: {c.cid} 변화율: {c.d_ratio * 100}% 시간 간격: {datetime.timedelta(seconds=c.d_time)} 알람 주기: {datetime.timedelta(seconds=c.cooldown)}"
		self.criteria_lock.release()
		return text

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

	def list_messages(self):
		text = ""
		self.message_lock.acquire(blocking=True)
		for item in self.message:
			text += "-----------------------------------------------\n"
			text += str(datetime.datetime.fromtimestamp(item.time)) + "\n"
			text += item.text + "\n"
		self.message_lock.release()
		return text

monitor = Monitor()
monitor.start()

print("===============================")
print("환영합니다! 도움말은 h를 입력하세요")
print("주의: 알람 메세지 박스는 최신이 아닐 수 있습니다")
print("주의: m을 입력해 메세지함을 사용하세요")
print("===============================")

while True:
	print(">> ", end=' ')
	user_input = input().lower()

	if user_input == 'h':
		help_text = "도움말은 h를 입력하세요\n \
			알람 추가는 a를 입력하세요\n \
			알람 목록 보기는 l을 입력하세요\n \
			알람 삭제를 위해선 r <알람 ID>를 입력하세요 (예시: r 3)\n \
			전체 알람 끄기/켜기는 d을 입력하세요\n \
			알람 소리 끄기/켜기는 s을 입력하세요\n \
			메세지함은 m을 입력하세요"
		print(help_text)
	
	if user_input == 'q':
		os._exit(0)

	if user_input[:1] == 'r':
		cid = 0
		while True:
			try:
				cid = int(user_input[1:])
			except:
				print("잘못 입력하셨습니다. 처음으로 돌아갑니다.")
				continue
			break
		
		if monitor.remove_criteria(cid) == False:
			print("알람을 성공적으로 삭제했습니다")
		else:
			print("대상 알람 ID를 찾을 수 없습니다")

	if user_input == 'l':
		text = monitor.list_criteria()
		print(text)
	if user_input == 'm':
		print(monitor.list_messages())
	if user_input == 'd':
		if ALARM_SWITCH:
			ALARM_SWITCH = False
			print("모든 알람이 꺼졌습니다")
		else:
			ALARM_SWITCH = True
			print("알람이 다시 작동합니다")
	if user_input == 's':
		if SOUND_SWITCH:
			SOUND_SWITCH = False
			print("곧 모든 소리가 꺼집니다")
		else:
			SOUND_SWITCH = True
			print("소리가 켜졌습니다")
	if user_input == 'a':
		print("알람을 추가합니다")

		while True:
			try:
				print("변화율을 입력하세요 (% 단위): ")
				change = float(input()) / 100
			except:
				continue
			break

		if change == 0:
			print("변화율은 0%가 될 수 없습니다. 처음으로 돌아갑니다")
			continue
		
		print("시간 간격을 입력하세요: 입력하신 시간 간격 동안 변화율 이상의 변화가 감지되면 알림을 내보냅니다")
		print("------------")
		min = sec = 0
		while True:
			try:
				print("분을 입력하세요 (알림의 간격이 3일 1시간 30분 12.52초라면 30을 입력): ", end='')
				min = int(input())
			except:
				continue
			break
		while True:
			try:
				print("초를 입력하세요 (알림의 간격이 3일 1시간 30분 12.52초라면 12.52를 입력): ", end='')
				sec = float(input())
			except:
				continue
			break
		
		interval = datetime.timedelta(minutes=min, seconds=sec).total_seconds()
		if interval == 0:
			print("시간 간격은 0이 될 수 없습니다. 처음으로 돌아갑니다")
			continue
		
		print("알람 주기를 입력하세요: 알람이 울린 후 다시 울리기까지 걸리는 시간입니다")
		print("------------")
		min = 0
		while True:
			try:
				print("분을 입력하세요 (알림의 간격이 3일 1시간 30분 12.52초라면 30을 입력): ", end='')
				min = int(input())
			except:
				continue
			break
		
		cooldown = datetime.timedelta(minutes=min).total_seconds()
		if cooldown == 0:
			print("알람 주기는 0이 될 수 없습니다. 처음으로 돌아갑니다")
			continue
			
		cid = monitor.add_criteria(change, interval, cooldown)
		if cid > 0:
			print(f"알람이 성공적으로 추가됐습니다. 알람 ID: <{cid}>")

