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

import classes
logic = classes.Logic_test()
period = 3600
size = 0.001
index = 0

json_open = open('test.json', 'r')
json_load = json.load(json_open)
rawohlc = np.array(json_load['result'][str(period)])

aaa = []
bbb = []
ccc = []
dd = []
ee = []
ff = []
y_ohlc = []

try:
    while True:
        ohlc = rawohlc[index:index+100]
        aaa.append(logic.test_ind(ohlc)[0])
        # bbb.append(logic.test_ind(ohlc)[1])
        # ccc.append(logic.test_ind(ohlc)[2])
        dd.append(logic.test_ind(ohlc)[0])
        ee.append(logic.test_ind(ohlc)[1])
        # ff.append(logic.test_ind(ohlc)[5]*0.01)
        y_ohlc.append(ohlc[-1][4])
        # print(logic.test_ind(ohlc))
        index += 1

except IndexError:
    x = list(range(len(aaa)))
    plt.plot(x,dd)
    plt.plot(x,ee)
    # plt.plot(x,ff)
    # plt.plot(x,y_ohlc)
    plt.show()
