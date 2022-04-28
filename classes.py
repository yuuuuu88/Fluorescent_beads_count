import numpy as np
import pandas as pd
import random
# ta-libの読み込み
try:
    import talib
    talibflag = True
except ModuleNotFoundError:
    print("talibがinstallされていないため一部指標の計算が遅くなります")
    talibflag = False

# 指標
class Indicators:
    def __init__(self,ohlc):
        """
        ohlc : np.array([[timestamp,o,h,l,c],...])
        """
        self.ohlc = ohlc # OHLC配列(5,*)
        self.closeprice = ohlc[:,4] # 終値配列(*)

    def ATR(self,n):
        """
        return : ATRのndarray(length=len(ohlc))
        """
        if talibflag:
            return talib.ATR(self.ohlc[:,2],self.ohlc[:,3],self.closeprice,timeperiod=n)
        else:
            tr = []
            atr = []
            for i in range(1,len(self.ohlc)):
                tr.append(max(self.ohlc[-i][2],self.ohlc[-i-1][4]) - min(self.ohlc[-i][3],self.ohlc[-i-1][4]))
            tr.reverse()
            atr = pd.Series(tr).ewm(span=n).mean().values
            return atr


    # EMA
    def EMA(self,n):
        """
        return : EMAのndarray(length=len(ohlc))
        """
        alpha = 2/(n+1)
        x0 = self.closeprice[:n].mean()
        ema = [x0]
        for i in range(len(self.closeprice)-n):
            ema.append(ema[-1]*(1-alpha)+self.closeprice[n+i]*alpha)

        nanlist = np.zeros(n-1)
        nanlist[:] = np.nan
        return np.concatenate([nanlist,np.array(ema)])

    # SMA
    def SMA(self,n):
        """
        return : SMAのndarray(length=len(ohlc))
        """
        return pd.Series(self.closeprice).rolling(n).mean().values

    # MACD(n1:shortEMA,n2:longEMA,n3:signal)
    def MACD(self,n1,n2,n3):
        """
        return : MACDのndarray,signalのndarray
        """
        macd = self.EMA(n1) - self.EMA(n2)
        macd[:n2] = np.nan
        signal = pd.Series(macd).rolling(n3).mean().values
        signal[:n2] = np.nan
        tipama = macd - signal

        # print(tipama)

        return macd,signal,tipama


    def RSI(self,n):
        """
        return : RSIのndarray
        """
        if talibflag:
            rsi = talib.RSI(self.closeprice,timeperiod=n)
            return rsi
        else:
            RSI_period = n
            diff = pd.Series(self.closeprice).diff(1)
            positive = diff.clip(lower=0).ewm(alpha=1.0/RSI_period).mean()
            negative = diff.clip(upper=0).ewm(alpha=1.0/RSI_period).mean()
            rsi = 100 - 100/(1-positive/negative)
            return rsi.values


    def RCI(self,n):
        """
        return: RCIのndarray
        """
        rci = []

        for j in range(len(self.closeprice) - (n-1)):
            table = np.zeros([2,n])
            # closeprice[-n:0]になるのを回避
            if j == len(self.closeprice)-n:
                table[0] = self.closeprice[-n:]
            else:
                table[0] = self.closeprice[-len(self.closeprice)+j:-len(self.closeprice)+n+j]
            table[1] = np.arange(n,0,-1)

            sortedtabel = table[:,np.argsort(table[0])]

            index = np.arange(n,0,-1)
            d = 0
            for i in range(n):
                d += (index[i]-sortedtabel[1][i])**2
            rci.append((1-6*d/(n*(n*n-1)))*100)
        nanlist = np.zeros(n-1)
        nanlist[:] = np.nan
        return np.concatenate([nanlist,np.array(rci)])

    def BB(self,n,sigma):
        base = pd.Series(self.closeprice).rolling(n).mean().values
        sig = pd.Series(self.closeprice).rolling(n).std(ddof=1).values

        upper_band = base + sigma*sig
        lower_band = base - sigma*sig

        return upper_band, lower_band, base

    def DMI(self, n):
        adx = talib.ADX(self.ohlc[:,2],self.ohlc[:,3],self.closeprice, timeperiod=n)
        dip = talib.PLUS_DI(self.ohlc[:,2],self.ohlc[:,3],self.closeprice, timeperiod=n)
        dim = talib.MINUS_DI(self.ohlc[:,2],self.ohlc[:,3],self.closeprice, timeperiod=n)

        return adx, dip, dim

    def STOC(self, n1, n2, n3):
        slowK, slowD = talib.STOCH(self.ohlc[:,2],self.ohlc[:,3],self.closeprice, fastk_period=n1, slowk_period=n2, slowd_period=n3)
        return slowK, slowD


class Logic_test:
    """
    EMA25とEMA10のゴールデンクロスで買い、デッドクロスで売り
    """

    def __init__(self):
        self.state = {'buy':False, 'sell':False}
        self.exit = {'settle':False, 'result':None}
        self.width = {'base':-1, 'p_width':-1, 'l_width':-1}
        self.entry_frag = [0,0,0]

    def test_ind(self,ohlc):
        ind = Indicators(ohlc)


        a = 7
        b = 2
        c = 50000
        d = 0
        # BB1 = ind.BB(21, 1)
        BB2 = ind.BB(21, 2)
        RSI14 = ind.RSI(14)
        MACD = ind.MACD(12, 26, 9)

        # if BB2[1][-a-2] > BB2[1][-b] and BB2[1][-b] < BB2[1][-1] and BB2[1][-a] - BB2[1][-b] > c:
        #     goukei = -1
        # elif BB2[0][-a] < BB2[0][-b] and BB2[0][-b] > BB2[0][-1] and BB2[0][-b] - BB2[0][-a] > c:
        #     goukei = 1
        # else:
        #     goukei = 0
        if ohlc[-1][4] - ohlc[-26][4] > 300000:
            goukei = 1
        else:
            goukei = 0

        #MACD
        # if MACD[2][-1] < 0:
        #     if MACD[0][-1] < MACD[1][-1] and MACD[0][-1] > MACD[1][-1]:
        #         buy_fraglist[0] = 1
        # if MACD[2][-1] > 0:
        #     if MACD[0][-1] > MACD[1][-1] and MACD[0][-1] < MACD[1][-1]:
        #         sell_fraglist[0] = 1
        #
        # #RSI
        # if RSI14[0][-1] > 70:
        #     sell_fraglist[1] = 1
        # if RSI14[0][-1] < 30:
        #     buy_fraglist[1] = 1

        #



        # BB3 = ind.BB(21, 3)

        return BB2[0][-1], BB2[1][-1], goukei, RSI14[-1], MACD[2][-1]

    def try_entry(self,ohlc,v_list):
        """
        signalがTrueになる条件（売買のエントリー条件）と
        利確損切りのwidthを定義する。
        """
        ind = Indicators(ohlc)

        self.state['buy'] = self.state['sell'] = False
        self.width['p_width'] = self.width['l_width'] = -1
        self.entry_frag = [0,0,0,0]

        """
        ロジック部分
        """
        buy_frag = 0
        sell_frag = 0
        trend_frag = 0
        oscillator_frag = 0

        v1,v2,v3 = v_list[0],v_list[1],v_list[2]

        BB1 = ind.BB(21, 1)
        BB2 = ind.BB(21, 2)
        BB3 = ind.BB(21, 3)

        RSI14 = ind.RSI(14)
        MACD = ind.MACD(12, 26, 9)
        SMA5 = ind.SMA(5)
        EMA5 = ind.EMA(5)
        EMA20 = ind.EMA(20)
        STOC = ind.STOC(9,3,3)

        a = 7
        b = 2
        c = 50000
        if SMA5[-1] - SMA5[-v1] > v2:
            buy_frag += 1
            self.entry_frag[2] = 1
        if SMA5[-v1] - SMA5[-1] > v3:
            sell_frag += 1
            self.entry_frag[2] = 1

        # if BB2[1][-a] > BB2[1][-b] and BB2[1][-b] < BB2[1][-1] and BB2[1][-a] - BB2[1][-b] > c:
        #     buy_frag += 1
        #     self.entry_frag[2] = 1
        #
        # if BB2[0][-a] < BB2[0][-b] and BB2[0][-b] > BB2[0][-1] and BB2[0][-b] - BB2[0][-a] > c:
        #     sell_frag += 1
        #     self.entry_frag[2] = 1

        # if STOC[1][-1] > 80:
        #     if STOC[0][-2] > STOC[1][-2] and STOC[0][-1] < STOC[1][-1]:
        #         sell_frag += 1
        #         # buy_frag += 1
        #         self.entry_frag[2] = 1
        #
        # if STOC[1][-1] < 20:
        #     if STOC[0][-2] < STOC[1][-2] and STOC[0][-1] > STOC[1][-1]:
        #         buy_frag += 1
        #         # sell_frag += 1
        #         self.entry_frag[2] = 1

        # if RSI14[-1] > 60 and SMA5[-1] > SMA5[-2] and SMA5[-2] < SMA5[-3]:
        #     for i in range(3):
        #         if MACD[0][-i-1] < MACD[1][-i-1] and MACD[0][-i] > MACD[1][-i]:
        #             buy_frag += 1
        #             self.entry_frag[2] = 1
        #
        #
        # if MACD[0][-1] < MACD[1][-1] and MACD[0][-1] > MACD[1][-1]:
        #     buy_frag += 1
        #     self.entry_frag[3] = 1
        # if EMA5[-1] < EMA20[-1] and EMA5[-1] > EMA20[-1]:
        #     buy_frag += 1
        #     self.entry_frag[3] = 1


        # for i in range(6):
        #     i = i + 1
            # if ohlc[-i][4] < BB2[1][-i]:
            #     buy_frag += 1
            #     self.entry_frag[2] = 1
            #
            # if MACD[2][-i-1] < 0 and MACD[2][-i] >= 0:
            #     buy_frag += 1
            #     self.entry_frag[2] = 1
            #
            # if RSI14[-i-1] < 30 and RSI14[-i] > 30:
            #      buy_frag += 1
            #      self.entry_frag[2] = 1


            # if RSI14[-i-1] > 70 and RSI14[-i] < 30:
            #     sell_frag += 1
            #     self.entry_frag[2] = 1
            #
            # if ohlc[-i][4] > BB2[0][-i]:
            #     sell_frag += 1
            #     self.entry_frag[2] = 1
            #
            # if MACD[2][-i-1] > 0 and MACD[2][-i] <= 0:
            #     sell_frag += 1
            #     self.entry_frag[2] = 1

        # if BB3[0][-1] - BB3[1][-1] >= 75:
        #     # バンドが並行してるとき
        #     a = 12
        #     b = 3
        #     c = a - b
        #     bias1_1 = (BB1[0][-a] - BB1[0][-b])/c
        #     bias1_2 = (BB1[1][-a] - BB1[1][-b])/c
        #     bias1 = (bias1_1+bias1_2)/2
        #     bias2 = (BB2[0][-7] - BB2[1][-7] - (BB2[0][-3] - BB2[1][-3]))/7
        #     # bias3 = abs(BB1[0][-7] - BB1[1][-7] - (BB1[0][-1] - BB1[1][-1]))/7
        #
        #     #傾き
        #     bias = (BB1[2][-a] - BB1[2][-b])/c
        #     bias_v = 1000
        #     # if bias - bias_v < bias1 < bias + bias_v and bias - bias_v < bias2 < bias + bias_v:#並行かを確認
        #     if abs(bias - bias1) < 20000:
        #
        #         #買いエントリー
        #         if BB1[0][-7] < BB1[0][-5] and BB1[0][-5] < BB1[0][-2]:
        #             if RSI14[-1] < 40:
        #                 buy_frag += 1
        #
        #                 self.entry_frag[0] = 1
        #         #売りエントリー
        #         if BB1[0][-7] > BB1[0][-5] and BB1[0][-5] > BB1[0][-2]:
        #             if RSI14[-1] > 60:
        #                 sell_frag += 1
        #
        #                 self.entry_frag[0] = 1
        #
        #     # 水平の時
        #
        #     if -v1 < bias < v1:
        #
        #         #買い
        #         if RSI14[-1] < 30 and ohlc[-1][4] < BB2[1][-1]:
        #             buy_frag += 1
        #
        #             self.entry_frag[1] = 1
        #
        #         #売り
        #         if RSI14[-1] > 70 and ohlc[-1][4] > BB2[0][-1]:
        #             sell_frag += 1
        #
        #             self.entry_frag[1] = 1
        #
        #     #単純
        #     if BB2[0][-1] < ohlc[-1][4]:
        #         if RSI14[-5] < RSI14[-1] and RSI14[-1] > 70:
        #             # buy_frag += 1
        #             sell_frag += 1
        #             if self.entry_frag[2] == 0:
        #                 self.entry_frag[2] = 1
        #
        #     if BB2[1][-1] > ohlc[-1][4]:
        #         if RSI14[-5] > RSI14[-1] and RSI14[-1] < 30:
        #             # sell_frag += 1
        #             buy_frag += 1
        #             if self.entry_frag[2] == 0:
        #                 self.entry_frag[2] = 1





        if sell_frag >= 1:
            self.state['sell'] = True

        if buy_frag >= 1:
            self.state['buy'] = True
 # >= sell_frag and sell_frag
 #  >= buy_frag and buy_frag

        # 一定値の値幅で利確損切りをする場合以下を設定する
        self.width['p_width'] = ohlc[-1][4]  * 0.008
        self.width['l_width'] = ohlc[-1][4] * 0.001


        self.width['base'] = ohlc[-1][4]

        return self.state,self.width,self.entry_frag

    def sell_exit(self,ohlc):
        """
        ショートポジションの際のexit条件を記載する。
        条件を満たすならself.exitのsettleにTrueを、resultにその際の（予想される）損益を入れる。
        """
        ind = Indicators(ohlc)
        self.exit = {'settle':False, 'result':None}

        BB2 = ind.BB(21,2)
        BB3 = ind.BB(21,3)

        # 利確
        if self.entry_frag[0] == 1:#平行

            if ohlc[-1][4] < BB2[1][-1] or BB3[0][-1] - BB3[1][-1] < 30:
                self.exit['settle'] = True
                self.exit['result'] = abs(ohlc[-1][4] - self.width['base'])


        # 損切り
            if ohlc[-1][4] > BB2[0][-1]:
                self.exit['settle'] = True
                self.exit['result'] = abs(ohlc[-1][4] - self.width['base']) * -1
                # print("損しました")


        elif self.entry_frag[1] == 1:#水平
            #利格
            if BB2[2][-1] > ohlc[-1][4]:
                self.exit['settle'] = True
                self.exit['result'] = abs(ohlc[-1][4] - self.width['base'])

            #損切
            if ohlc[-1][4] - self.width['base'] > self.width['l_width']:
                self.exit['settle'] = True
                self.exit['result'] = -self.width['l_width']
                # print("損しました")

        elif self.entry_frag[2] == 1:

            if self.width['base'] - ohlc[-1][4] > self.width['p_width']:
                self.exit['settle'] = True
                self.exit['result'] = self.width['p_width']

            if ohlc[-1][4] - self.width['base'] > self.width['l_width']:
                self.exit['settle'] = True
                self.exit['result'] = -self.width['l_width']
                # print("損しました")
        """
        # ドテンの場合
        else:
            signal,_ = self.try_entry(ohlc)
            if signal['buy']:
                self.exit['settle'] = True
                self.exit['result'] = self.width['base'] - ohlc[-1][4]

        # その他のexitの場合
        if hogehoge:
            self.exit['settle'] = True
            self.exit['result'] = self.width['base'] - ohlc[-1][4]
        """

        return self.exit

    def buy_exit(self,ohlc):
        """
        ロングポジションの際のexit条件を記載する。
        条件を満たすならself.exitのsettleにTrueを、resultにその際の（予想される）損益を入れる。
        """
        ind = Indicators(ohlc)
        self.exit = {'settle':False, 'result':None}

        BB2 = ind.BB(21,2)
        BB3 = ind.BB(21,3)
        MACD = ind.MACD(12, 26, 9)
        EMA5 = ind.EMA(5)
        EMA20 = ind.EMA(20)


        if self.entry_frag[0] == 1:#平行
        #利格
            if ohlc[-1][4] > BB2[0][-1] or BB3[0][-1] - BB3[1][-1] < 30:
                self.exit['settle'] = True
                self.exit['result'] = abs(ohlc[-1][4] - self.width['base'])

        # 損切り
            if ohlc[-1][4] < BB2[1][-1]:
                self.exit['settle'] = True
                self.exit['result'] = abs(ohlc[-1][4] - self.width['base']) * -1
                # print("損しました")


        elif self.entry_frag[1] == 1:#水平
            #利格
            if BB2[2][-1] < ohlc[-1][4]:
                self.exit['settle'] = True
                self.exit['result'] = abs(ohlc[-1][4] - self.width['base'])

            #損切
            if self.width['base'] - ohlc[-1][4] > self.width['l_width']:
                self.exit['settle'] = True
                self.exit['result'] = -self.width['l_width']
                # print("損しました")

        elif self.entry_frag[2] == 1:
            # 利確
            if ohlc[-1][4] - self.width['base'] > self.width['p_width']:
                self.exit['settle'] = True
                self.exit['result'] = self.width['p_width']
            # 損切
            if self.width['base'] - ohlc[-1][4] > self.width['l_width']:
                self.exit['settle'] = True
                self.exit['result'] = -self.width['l_width']
                # print("損しました")

        elif self.entry_frag[3] == 1:
            # 利確
            if MACD[0][-1] > MACD[1][-1] and MACD[0][-1] < MACD[1][-1]:
                self.exit['settle'] = True
                self.exit['result'] = abs(ohlc[-1][4] - self.width['base'])
            elif EMA5[-1] > EMA20[-1] and EMA[-1] < EMA20[-1]:
                self.exit['settle'] = True
                self.exit['result'] = abs(ohlc[-1][4] - self.width['base']) * -1

            # 損切
            if self.width['base'] - ohlc[-1][4] > self.width['l_width']:
                self.exit['settle'] = True
                self.exit['result'] = -self.width['l_width']
                # print("損しました")


        """
        # ドテンの場合
        signal,_ = self.try_entry(ohlc)
        if signal['sell']:
            self.exit['settle'] = True
            self.exit['result'] = ohlc[-1][4] - self.width['base']

        # その他のexitの場合
        if hogehoge:
            self.exit['settle'] = True
            self.exit['result'] = ohlc[-1][4] - self.width['base']
        """

        return self.exit
