---
title: "Python Run一下神經網路(Lstm)"
date: "2018-07-16T16:55:00.001+08:00"
updated: "2019-09-13T08:53:13.328+08:00"
permalink: "/2018/07/python-runlstm.html"
original_url: "https://x8795278.blogspot.com/2018/07/python-runlstm.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3457063518963581927"
tags: ["Python", "Stock", "Tutorial"]
layout: post
---

## 之前說的神經網路可行性??

## ---

run300輪
[![](https://i.imgur.com/p5zzeom.png)](https://i.imgur.com/p5zzeom.png)
  

來run一下別人大神級的code，裡面大神已經都出不介紹lstm大概是什麼了，小白只能runrun別人寫好的code  

好code不run嗎?，這樣看下來好像只是根據原始的資料，後幾天才放馬後炮，我們當然要預測當天的阿，真的能預測當然就是神明了，之前有看過大神run出來的57%準度也是蠻狂的
[深度学习做股票预测靠谱吗？](https://www.zhihu.com/question/54542998)
之前也說過，我們不要來做它們那種，我們做部分的行為預測，那些要比數據量，專業度一般的人也拿不到那麼多的資料，我們來做小範圍的行為預知就好(做不出來)  

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Activation


from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY,YEARLY
from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc
#import matplotlib
import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pylab import date2num
import datetime
import numpy as np
from pandas import DataFrame
from numpy import row_stack,column_stack
import pandas

df=ts.get_hist_data('601857',start='2016-06-15',end='2018-01-12')
dd=df[['open','high','low','close']]

#print(dd.values.shape[0])

dd1=dd .sort_index()

dd2=dd1.values.flatten()

dd3=pandas.DataFrame(dd1['close'])

def load_data(df, sequence_length=10, split=0.8):

    #df = pd.read_csv(file_name, sep=',', usecols=[1])
    #data_all = np.array(df).astype(float)

    data_all = np.array(df).astype(float)
    scaler = MinMaxScaler()
    data_all = scaler.fit_transform(data_all)
    data = []
    for i in range(len(data_all) - sequence_length - 1):
        data.append(data_all[i: i + sequence_length + 1])
    reshaped_data = np.array(data).astype('float64')
    #np.random.shuffle(reshaped_data)
    # 对x进行统一归一化，而y则不归一化
    x = reshaped_data[:, :-1]
    y = reshaped_data[:, -1]
    split_boundary = int(reshaped_data.shape[0] * split)
    train_x = x[: split_boundary]
    test_x = x[split_boundary:]

    train_y = y[: split_boundary]
    test_y = y[split_boundary:]

    return train_x, train_y, test_x, test_y, scaler


def build_model():
    # input_dim是输入的train_x的最后一个维度，train_x的维度为(n_samples, time_steps, input_dim)
    model = Sequential()
    model.add(LSTM(input_dim=1, output_dim=6, return_sequences=True))
    #model.add(LSTM(6, input_dim=1, return_sequences=True))
    #model.add(LSTM(6, input_shape=(None, 1),return_sequences=True))

    """
    #model.add(LSTM(input_dim=1, output_dim=6,input_length=10, return_sequences=True))
    #model.add(LSTM(6, input_dim=1, input_length=10, return_sequences=True))
    model.add(LSTM(6, input_shape=(10, 1),return_sequences=True))
    """
    print(model.layers)
    #model.add(LSTM(100, return_sequences=True))
    #model.add(LSTM(100, return_sequences=True))
    model.add(LSTM(100, return_sequences=False))
    model.add(Dense(output_dim=1))
    model.add(Activation('linear'))

    model.compile(loss='mse', optimizer='rmsprop')
    return model


def train_model(train_x, train_y, test_x, test_y):
    model = build_model()

    try:
        model.fit(train_x, train_y, batch_size=512, nb_epoch=300, validation_split=0.1)
        predict = model.predict(test_x)
        predict = np.reshape(predict, (predict.size, ))
    except KeyboardInterrupt:
        print(predict)
        print(test_y)
    print(predict)
    print(test_y)
    try:
        fig = plt.figure(1)
        plt.plot(predict, 'r:')
        plt.plot(test_y, 'g-')
        plt.legend(['predict', 'true'])
    except Exception as e:
        print(e)
    return predict, test_y


if __name__ == '__main__':
    #train_x, train_y, test_x, test_y, scaler = load_data('international-airline-passengers.csv')
    train_x, train_y, test_x, test_y, scaler =load_data(dd3, sequence_length=10, split=0.8)
    train_x = np.reshape(train_x, (train_x.shape[0], train_x.shape[1], 1))
    test_x = np.reshape(test_x, (test_x.shape[0], test_x.shape[1], 1))
    predict_y, test_y = train_model(train_x, train_y, test_x, test_y)
    predict_y = scaler.inverse_transform([[i] for i in predict_y])
    test_y = scaler.inverse_transform(test_y)
    fig2 = plt.figure(2)
    plt.plot(predict_y, 'g:')
    plt.plot(test_y, 'r-')
    plt.show()
```

  

後來再來看一下，是不是訓練次數不夠?我們來加到1000輪
[![](https://i.imgur.com/SHgyKWn.png)](https://i.imgur.com/SHgyKWn.png)
[![](https://i.imgur.com/MUbXcZX.png)](https://i.imgur.com/MUbXcZX.png)
## 構思

## ---

會不會要針對某個特別情況進行訓練呢，在我們進行上一次的初步構想的篩選股票的咚咚
[![](https://i.imgur.com/tl9R9KD.png)](https://i.imgur.com/tl9R9KD.png)
[![](https://i.imgur.com/nX3aoug.png)](https://i.imgur.com/nX3aoug.png)
設定參數尋找BBand寬度特別寬的海選，接下來我們只要針對特殊買賣點做lstm做訓練，來修正買賣點以來提升初入金額?
[![](https://i.imgur.com/LY2wqTV.png)](https://i.imgur.com/LY2wqTV.png)
忘記加scorllbar
這些大概就是篩選下來的股票我們來印證一下
寬度確實在20以上
[![](https://i.imgur.com/rrKLLxm.png)](https://i.imgur.com/rrKLLxm.png)
[![](https://i.imgur.com/2GXeIto.png)](https://i.imgur.com/2GXeIto.png)
要規避情況
[![](https://i.imgur.com/moGD0sX.png)](https://i.imgur.com/moGD0sX.png)
初步我想進行，一檔股票裡所有波動度寬度>=20%在excel
應該是尋找特徵點，我像做的也就是最後面再加入規避正確後的一欄??
話說規避正確後幹嘛再用lstm??增加準度嗎還是??脫褲子放屁?，外行人只能試看看，找code run修修改改，與黃金交叉有什麼關聯，或者是kd??，正規好像不是這樣搞，異常弔詭
不斷的修正買賣點用來提升獲利最大化??亂講別噴

1. 海撈BBand寬度大於20
2. 再用excel在計算新的參考數值
3. 制定tensorflow模型(異常困難)
4. 訓練

精準的修正買賣點好了，每天海選20檔固定買賣，重要的是有本啦，以量制勝不過沒關西  

xq可以有模擬帳戶，這如果成功我們再來tick資料來串  

[![](https://i.imgur.com/9Ol2ku3.png)](https://i.imgur.com/9Ol2ku3.png)
ㄎㄎ沒辦法，一整個很動態xd，沒辦法透過記憶體方式取得tick否則，可以用這個軟體，幫我們分擔基礎的網路負擔，還是透過封包?當然會加密阿xd，證券台灣的開通要  

[![](https://i.imgur.com/Tj0fRbb.png)](https://i.imgur.com/Tj0fRbb.png)
貴送送，最後想到來爬蟲一下發現某c股市交易模擬交易網站可以拿得每秒tick，不是每分鐘喔喔喔喔到時再來做小爬蟲和即時技術分析吧!新名詞蝶式套利波動度交易??好像是很多人吃飯工具?
## 參考

## ---

## [基于keras 的lstm 股票收盘价预测](https://blog.csdn.net/luoganttcc/article/details/79046870)
