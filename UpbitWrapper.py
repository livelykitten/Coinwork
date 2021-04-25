import requests
import json

# key: market_code
# value: a dict where
# {
#     market: ~
#     korean_name: ~
#     english_name: ~
# }
def get_all_markets():
	market_list_url = "https://api.upbit.com/v1/market/all"
	market_list_qs = {"isDetails":"false"}

	try:
		response = requests.request("GET", market_list_url, params=market_list_qs)
		markets_list_raw = json.loads(response.text)
	except:
		return None

	markets = {}
	for market_item in markets_list_raw:
		# if market_item['market'] != "KRW-BTC":
		# 	continue
		markets[market_item['market']] = market_item["korean_name"] + "/" + market_item["english_name"]
	
	return markets

def get_ticker_querystring(markets):
	text = ""
	for code in markets.keys():
		text += code + ","
	text = text[:-1]
	return {"markets":text}

# dict, key: market code value: Ticker object
def get_tickers(markets):
	ticker_url = "https://api.upbit.com/v1/ticker"
	ticker_qs = get_ticker_querystring(markets)
	
	try:
		response = requests.request("GET", ticker_url, params=ticker_qs)
	except:
		return None
	if not response.ok:
		return None
	
	r_dict = json.loads(response.text)
		# 시가 총액도 가능하면 넣자
	
	return r_dict