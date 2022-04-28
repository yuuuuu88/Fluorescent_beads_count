import requests
from datetime import datetime
import time
import json

chart_sec = 3600         # 保存したいローソク足の時間軸
file = "./test.json"   # 保存するファイル名

# Cryptowatchのデータを単に保存するだけの関数
def accumulate_data(min, path, before=0, after=0):

	# APIで価格データを取得
	params = {"periods" : min }
	if before != 0:
		params["before"] = before
	if after != 0:
		params["after"] = after
	response = requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc",params)
	data = response.json()

	#ファイルに書き込む
	file = open( path,"w",encoding="utf-8")
	json.dump(data,file)

	return data

# メイン処理
accumulate_data(chart_sec, file ,after=148322880)
