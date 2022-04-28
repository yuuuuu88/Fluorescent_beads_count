import csv,json
import numpy as np
import pandas as pd
import datetime
from pprint import pprint
import matplotlib.pyplot as plt
import time
import requests
import glob, os
import random

# ログ設定
import logging
from logging import getLogger,FileHandler,Formatter
logger = getLogger("backtest")
logger.setLevel(logging.INFO)
fh = FileHandler('backtest.log')
fh.setLevel(logging.INFO)
format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(format)
logger.addHandler(fh)

import classes

# ドローダウン計算
def drawdown(result):
    top = 0
    down = 0
    for i in range(len(result)):
        if top < result[i]:
            top = result[i]
        else:
            if down < top - result[i]:
                down = top - result[i]

    return down/top*100




if __name__ == "__main__":
    ana_frag = True
    ana_count = 1
    kaisu = 1
    kaisu = kaisu + 1
    rieki = []
    best_v = []
    MAX_RETRY = 10
    dict = {}
    delta_list = [0] * 5901
    BB2u = []
    BB2l = []
    ana_signal = []
    RSI = []
    MACD = []

    for m in range(MAX_RETRY):
        try:
            while ana_frag:



                print("【バックテストを行います】")


                # ロジックの読み込み
                # ------------------------------
                logic = classes.Logic_test()
                period = 3600
                size = 0.001
                # ------------------------------


                # bot
                flag = {'check':True, 'sell_position':False, 'buy_position':False}
                result = [0]

                # OHLCデータをはじめにまとめて取得しておく
                # response = requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc",params = {"periods": period})
                json_open = open('test.json', 'r')
                json_load = json.load(json_open)
                rawohlc = np.array(json_load['result'][str(period)])
                # rawohlc = np.array(response.json()['result'][str(period)])
                # print(len(rawohlc))
                index = 0
                y_ohlc = []
                x_ohlc = 0

                result_list = [0]

                # ロジック内の変数の設定
                v1 = random.randint(2, 15)
                v2 = random.randrange(10000, 50000, 1000)
                v3 = random.randrange(1000, 20000, 1000)
                v_list = [v1, v2, v3]



                try:
                    while True:
                        # 建玉未保有時
                        while flag['check']:
                            # ohlcの設定
                            ohlc = rawohlc[index:index+100]
                            # IndexErrorの発生
                            err = rawohlc[index+100]
                            # print(len(ohlc))
                            y_ohlc.append(ohlc[-1][4])
                            result_list.append(result_list[-1])
                            BB2u.append((logic.test_ind(ohlc)[0]))
                            BB2l.append((logic.test_ind(ohlc)[1]))
                            ana_signal.append((logic.test_ind(ohlc)[2]))
                            if ana_signal[-1] == 1 and len(ana_signal) >= 31 :
                                ana_signal[-31] = 1
                                ana_signal[-1] = 0
                            RSI.append((logic.test_ind(ohlc)[3]))
                            MACD.append((logic.test_ind(ohlc)[4]))
                            counter = 0

                            # entryの判断
                            entry,_,aaa = logic.try_entry(ohlc,v_list)



                            if entry['buy']:
                                # logger.info("買い注文をします　現在価格："+str(ohlc[-1][4]))
                                # print("買い注文をします　現在価格："+str(ohlc[-1][4]))


                                # flagの更新
                                flag['check'] = False
                                flag['buy_position'] = True

                                index += 1

                                break

                            if entry['sell']:
                                # logger.info("売り注文をします　現在価格："+str(ohlc[-1][4]))
                                # print("売り注文をします　現在価格："+str(ohlc[-1][4]))

                                # flagの更新
                                flag['check'] = False
                                flag['sell_position'] = True

                                index += 1

                                break

                            index += 1


                        # 買いポジション保有時
                        while flag['buy_position']:
                            # ohlcの設定
                            ohlc = rawohlc[index:index+100]
                            result_list.append(result_list[-1])
                            y_ohlc.append(ohlc[-1][4])
                            BB2u.append((logic.test_ind(ohlc)[0]))
                            BB2l.append((logic.test_ind(ohlc)[1]))
                            ana_signal.append((logic.test_ind(ohlc)[2]))
                            if ana_signal[-1] == 1 and len(ana_signal) >= 31 :
                                ana_signal[-31] = 1
                                ana_signal[-1] = 0
                            RSI.append((logic.test_ind(ohlc)[3]))
                            MACD.append((logic.test_ind(ohlc)[4]))

                            # IndexErrorの発生
                            err = rawohlc[index+100]


                            counter += 1
                            # exitの判断
                            if counter > 1:
                                exit = logic.buy_exit(ohlc)

                            else:
                                exit = {'settle':False, 'result':None}


                            if exit['settle']:
                                # logger.info("売り決済をします　損益："+str(exit['result']))
                                # print("売り決済をします　損益："+str(exit['result']))
                                result.append(exit['result'])
                                result_list[-1] = exit['result']

                                # flagの更新
                                flag['check'] = True
                                flag['buy_position'] = False

                                delta_list[index] = 1
                                delta_list[index-1] = 0.5
                                delta_list[index+1] = 0.5

                                index += 1

                                break

                            index += 1


                        # 売りポジション保有時
                        while flag['sell_position']:
                            # ohlcの設定
                            ohlc = rawohlc[index:index+100]
                            result_list.append(result_list[-1])
                            y_ohlc.append(ohlc[-1][4])
                            BB2u.append((logic.test_ind(ohlc)[0]))
                            BB2l.append((logic.test_ind(ohlc)[1]))
                            ana_signal.append((logic.test_ind(ohlc)[2]))
                            if ana_signal[-1] == 1 and len(ana_signal) >= 31 :
                                ana_signal[-31] = 1
                                ana_signal[-1] = 0
                            RSI.append((logic.test_ind(ohlc)[3]))
                            MACD.append((logic.test_ind(ohlc)[4]))

                            # IndexErrorの発生
                            err = rawohlc[index+100]

                            counter += 1
                            # exitの判断
                            if counter > 1:
                                exit = logic.sell_exit(ohlc)

                            else:
                                exit = {'settle':False, 'result':None}

                            if exit['settle']:
                                # logger.info("買い決済をします　損益："+str(exit['result']))
                                # print("買い決済をします　損益："+str(exit['result']))
                                result.append(exit['result'])
                                result_list[-1] = exit['result']


                                # flagの更新
                                flag['check'] = True
                                flag['sell_position'] = False

                                delta_list[index] = 1
                                delta_list[index-1] = 0.5
                                delta_list[index+1] = 0.5

                                index += 1

                                break

                            index += 1




                # index+100がohlcの長さを超えたところがバックテストの終了条件
                except IndexError:

                    print("【バックテストを終了します】\n")

                    # 分析

                    result = np.array(result)

                    profit = sum(result)
                    winrate = len(result[result > 0])/len(result) # 勝率
                    pandlratio = -(sum(result[result > 0])/len(result[result > 0]))/(sum(result[result < 0])/len(result[result < 0])) # 損益率
                    pf = -sum(result[result > 0])/sum(result[result < 0]) # profit factor
                    dd = drawdown(result) # ドローダウン
                    profit = profit * size
                    day_trade = len(result) / 250


                    print(f"---バックテスト結果---\nトレード回数：{len(result)}__{day_trade:.0f}回/日\n総利益：{profit:.0f}\n勝率：{winrate:.2f} \
                        \n損益率：{pandlratio:.2f}\nprofit factor：{pf:.2f}\n最大ドローダウン：{dd:.2f} %")


                    kekka = f"---バックテスト結果---\nトレード回数：{len(result)}__{day_trade:.0f}回/日\n総利益：{profit:.0f}\n勝率：{winrate:.2f} \
                        \n損益率：{pandlratio:.2f}\nprofit factor：{pf:.2f}\n最大ドローダウン：{dd:.2f} %"

                    dict[profit] = v_list
                    rieki.append(profit)
                    if max(rieki) == profit and pf < 4:
                        bestkekka = kekka


                    if kaisu == 2:
                        to0 = y_ohlc[0]
                        y_ohlc = list(map(lambda x: x - to0, y_ohlc))
                        x_ohlc = list(range(len(y_ohlc)))
                        result_list = list(map(lambda x: x * 0.008, result_list))
                        result_list = np.array(result_list[1:])
                        # print(len(delta_list))
                        # print(len(x_ohlc))
                        if len(x_ohlc) == 5900:
                            delta_list = delta_list[:5900]
                        delta_list = list(map(lambda x: x * 1000000, delta_list))

                        BB2u = list(map(lambda x: x - to0, BB2u))
                        BB2l = list(map(lambda x: x - to0, BB2l))

                        count = 0
                        frag = 0
                        for i in ana_signal:
                            if i == 1 and frag == 0:
                                frag = 1
                                count += 1
                                continue
                            if i == 0:
                                frag = 0

                            if frag == 1:
                                ana_signal[count] = 0

                            count += 1
                        ana_signal = list(map(lambda x: x * 1000000, ana_signal))
                        RSI = list(map(lambda x: x * 10000, RSI))
                        MACD = list(map(lambda x: x * 10, MACD))


                        # 描画
                        plt.plot(x_ohlc,y_ohlc)
                        plt.plot(x_ohlc,result_list.cumsum())
                        # plt.plot(x_ohlc,delta_list)
                        # plt.plot(x_ohlc,BB2u)
                        # plt.plot(x_ohlc,BB2l)
                        plt.plot(x_ohlc,ana_signal)
                        # plt.plot(x_ohlc,RSI)
                        # plt.plot(x_ohlc,MACD)

                        file = glob.glob(r"c:\python\virtualenv\coin_env\coin_fig\*.png")
                        file_count = len(file)
                        save_dir = "c:/python/virtualenv/coin_env/coin_fig/"
                        plt.savefig(os.path.join(save_dir, "result{0:04d}.png".format(file_count)))
                        plt.show()

                        # plt.plot(range(len(result)),result.cumsum())
                        # plt.title("Result")
                        # plt.xlabel("Number of entries made")
                        # plt.ylabel(f"Profit (×{size} JPY)")
                        # plt.show()
                        break

                    print(ana_count)
                    ana_count += 1
                    if ana_count == kaisu and kaisu > 2:
                        print("\n\n\n\n最終結果は以下です")

                        logger.info("\n\n【バックテストを行います】")
                        logger.info("【バックテストを終了します】")
                        sort_dict = sorted(dict.items(), key=lambda x:x[0])
                        print(sort_dict[-3:])
                        logger.info(bestkekka)



                        x = list(range(kaisu-1))
                        y = rieki
                        print(bestkekka)
                        plt.plot(x, y)
                        plt.show()
                        break

        except Exception as e:
            print("Error")
            print('=== エラー内容 ===')
            print('type:' + str(type(e)))
            print('args:' + str(e.args))
            # print('message:' + e.message)
            print('e自身:' + str(e))
            if m == MAX_RETRY - 1:
                break

        else:
            break
