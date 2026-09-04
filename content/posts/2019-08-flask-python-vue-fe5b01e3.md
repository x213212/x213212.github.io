---
title: "flask python vue 股票回測 (一) Vue移植"
date: "2019-08-06T16:41:00.003+08:00"
updated: "2019-10-11T02:37:54.087+08:00"
permalink: "/2019/08/flask-python-vue.html"
original_url: "https://x8795278.blogspot.com/2019/08/flask-python-vue.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-1861666753259647903"
tags: ["flask", "Python", "Stock", "Tutorial", "Vue.js"]
layout: post
---

搬移模組目前大致完成進度50%  

會延遲不是 Lag xd 是我用 gif 錄影 fps 調太低不然檔案很大  

[![](https://i.imgur.com/cwvAR1l.gif)](https://i.imgur.com/cwvAR1l.gif)
  

![](https://i.imgur.com/ExpOv5Z.png)

![](https://i.imgur.com/3NCsani.png)

  

目前新增各模組  

- bband
- macd
- flask restful api

繪圖速度大概是 python matplotlib 好幾倍  

來跟大數據結合一下好了看看  

這邊將會把後端全部改為 hadoop?  

機器學習部分改為用spark訓練  

然後每天回傳固定股市，漲幅等等
  

  

以前用python 做的回測軟體，現在要全部搬移到 vue上面，  

在之前前幾次有做了幾個教學就是golang架設伺服器篇  

<https://x8795278.blogspot.com/2018/09/golang-json.html>
  

新的版面  

![](https://i.imgur.com/ONScCoW.png)

  

預計全部塞到裡面，做個良好的回測 準備開工!  

![](https://i.imgur.com/edNuNNL.png)

舊的  

![](https://i.imgur.com/bco32R8.png)

**`flask_api.py`**

```python
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 17:46:15 2017

@author: user
"""
import sys
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import logging
from logging.handlers import RotatingFileHandler

import urllib.request, json 
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import tkinter as tk
import datetime 
from tkinter import HORIZONTAL
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
import csv
import talib
import os
import time
import random
import tkinter.filedialog as filedialog
import threading
import warnings
warnings.filterwarnings('ignore')
import urllib.request; #用來建立請求
import urllib.parse;
from bs4 import *
import matplotlib.pyplot as plt 
from mpl_finance import candlestick_ohlc
from mpl_finance import volume_overlay3
import matplotlib.dates as dates
from datetime import datetime
import datetime as datetmp
from stocker import Stocker
import strategy.bband as bb
import strategy.rsi as rsi
import strategy.popular_model as popmoder 
from datetime import datetime

plt.rcParams['font.sans-serif'] = ['DFKai-sb'] 
plt.rcParams['font.family']='sans-serif'  
data_list = []
data_list2 = []
data_list3 = []
#購買資料
buy_list=[]
sell_list=[]

#root=tk.Tk()
#var = DoubleVar(root,0)
#var2 = DoubleVar(root,0)
#var3 = tk.IntVar(root,0)
#var4 = tk.IntVar(root,0)
#
#var5 = tk.StringVar(root,0)
#var6 = tk.StringVar(root,0)
#var9 = tk.StringVar(root,0)
#var10 = tk.StringVar(root,0)
#var11 = tk.StringVar(root,0)
#var12 = tk.StringVar(root,0)
#
#var7 = tk.IntVar(root,0)
#var8 = tk.IntVar(root,0)
##個別參數
global start
global end
global str_tmp
global date
global ope
global close
global high
global low 
global vol
global date 
global date_ex
global BBand_up
global BBand_sma
global BBand_down
global BBand_width
global BBand_mid

global catch_stock
global catch_stockgarbage
global fbpropht_data
global deposit

global draw_tmp
global thread_bolean 

##模組設定
global strategy_model
#1216統一 3144新揚科
num_48 = ["1216統一"]
df=pd.DataFrame()
df2=pd.DataFrame(num_48)

    #技術指標
def get_MACD(close):
    MACD = talib.MACD(close,
                            fastperiod=12, slowperiod=26, signalperiod=9)  
    return [float(x) for x in MACD [1]]
    
def get_DIF(close):
    DIF=[]
    EMA12=talib.EMA(close, timeperiod=12)  
    EMA26=talib.EMA(close, timeperiod=26)
    for tmp in range(0,len(EMA12)):
        DIF.append(float(EMA12[tmp]-EMA26[tmp]))
    return DIF
def get_BBand(close):
    #BBband
    BBand = talib.BBANDS(close,timeperiod=20,nbdevup=1.5,nbdevdn=1.5)
    return BBand 

def get_OSC(macd,dif):
    OSC=[]
    for tmp in range(0,len(macd),1):
        OSC.append(float(macd[tmp]-dif[tmp]))
    return OSC

def get_SMA(close):
    SMA= talib.MA(np.array(close), timeperiod=10, matype=0)
    return SMA

def get_fastktd(high,low,close):
    fastk, fastd = talib.STOCHF(high, low,close, fastk_period=60, fastd_period=7, fastd_matype=0)
    return (fastk,fastd)

#def call__band()


def backer(model_name):
    global start
    global end
    global str_tmp
    global ope
    global close
    global high
    global low 
    global vol
    global date 
    global date_ex
    global BBand_up
    global BBand_sma
    global BBand_width
    global BBand_down
    global deposit
    #交易策略參數
    str_tmp="回測模組:" + model_name +'\n'
    star=100000000  #初始金額無變動
    price=100000000 #變動初始金額
    star=price
    ex_handle=20   #一次股數上限
    #參數list
    data_param=[star,price,ex_handle,buy_list,sell_list,data_list ,data_list2 ,data_list3 ,start,end,str_tmp,ope,close,high,low,vol,date,date_ex]
    if (model_name == "BBand"):
        str_tmp += bb.bband(data_param)
    elif (model_name == "Rsi"):
        str_tmp += rsi.rsi(data_param)
    elif (model_name == "show_fbpropht"):
        show_fbpropht()
    
    
    
def read_file(file):
    global start
    global end
    global str_tmp
    global date
    global ope
    global close
    global high
    global low 
    global vol
    global date_ex
    global deposit
    global BBand
    global BBand_up
    global BBand_sma
    global BBand_down
    global BBand_mid
    global BBand_width
    # path_str=os.path.join("C:\\","Users","x2132","OneDrive","桌面","History_data",iii) 
    # path_str=path_str+'.csv'
    
    path_str=file
    print (path_str)
    #收盤
    c=[row[1] for row in file] #要導入的列
    
    #開盤
    o=[row[2] for row in file] #要導入的列 
    
    #最高
    h=[row[3] for row in file] #要導入的列 
    #最低
    l=[row[4] for row in file] #要導入的列     
    #成交量
    v=[row[5] for row in file] #要導入的列     
    #日期
    d=[row[0] for row in file] #要導入的列 
        
    date=[]
    low=[]
    high=[]
    close=[]
    ope=[]
    close=[]
    vol=[]
    date.clear()
    low.clear()
    high.clear()
    close.clear()
    ope.clear()
    vol.clear()
    ope = [float(x) for x in o]
    close = [float(x) for x in c]
    high = [float(x) for x in h]
    low = [float(x) for x in l]
    vol = [float(x) for x in v]
    date =d
    date_ex=[]
    date.reverse()
    low.reverse()
    high.reverse()
    close.reverse()
    ope.reverse()
    vol.reverse()
    
    #print (BBand_width)
    for x in range(0,len(ope),1):
                #datess =dates.date2num(d[x])
            #print (datetime.datetime(2017, 3, 13))
            #print (dates.date2num(datetime.datetime(2017, 3, 13, 12, 0)))
            #print (datetime.datetime(2017, 3, 13, 12, 0))
            
#        t = d[x].replace('/','-')
        t= datetime.fromtimestamp(d[x]/1000)
            #print ((dates.date2num(datetime.strptime(t, '%Y-%m-%d'))))
            # (type(datetime.datetime(2017, 3, 13, 12, 0)))
            #print (type(dates.date2num(datetime.datetime(2017, 3, 13, 12, 0))))
            #print(dates.date2num(datetime.datetime(2017, 3, 13, 12, 0)))
        datas = (t , ope[x], high[x], low[x],close[x])
        datas2 = (t, ope[x], high[x], low[x],close[x],vol[x])
        datas3 = (t,close[x])
            
        date_ex.append(t)
        data_list.append(datas)
        data_list2.append(datas2)
        data_list3.append(datas3)
    start=0
    end=len(data_list)
#    w=tk.Scale(frame2, from_=start, to=end-1, orient=HORIZONTAL, variable = var,length=200 ).grid(row=2,column=0)
#    w2=tk.Scale(frame2, from_=start, to=end-1, orient=HORIZONTAL, variable = var2,length=200).grid(row=2,column=1)
#    var2.set(int(end-1))
    df = pd.DataFrame(data_list3, columns=list(['date','deposit'])) 
    #print (df)
  
#    df=pd.DataFrame(datas, index=False)
 #   df.insert(0,'股票代號',df2)
    print(df)
    df.to_csv("price.csv", index=False)
    drawPic()

    
# tmp2=10
# print (str(tmp2))
# tmp =type(tmp2)
# fig, ax = plt.subplots()
# print (fig)
# print (ax)
# fig.subplots_adjust(bottom=0.2)

# # 设置X轴刻度为日期时间
# #data_list.reverse()
# ax.xaxis_date()

# plt.xticks(rotation=45)

# plt.yticks()

# plt.title("k線圖")

# plt.xlabel("時間")

# plt.ylabel("股價")
# #print (len(data_list))

# candlestick_ohlc(ax, data_list[1000:2000], width=0.5, colorup='r', colordown='g')

# for x in range(0,len(buy_list),1):    
#     ax.annotate('', xy=(buy_list[x][0],buy_list[x][1]), xytext=(-15, -27),
#               textcoords='offset points', ha="center",
#                  arrowprops=dict(facecolor='black', color='red',width=1),
#             )
# for x in range(0,len(sell_list),1):    
#     ax.annotate('', xy=(sell_list[x][0],sell_list[x][1]),  xytext=(-17, 20),
#               textcoords='offset points', ha="center",
#                  arrowprops=dict(facecolor='black', color='green',width=1),
#             )

# #print('hello')
# pro_fit='獲利金額:'+str((int(fin_price-star)))
# buy_count='交易次數 買/賣:'+str(len(buy_data))+'/'+str(len(self_data)) 
# plt.figtext(0.1,0.92,pro_fit+'\n'+buy_count,color='black')

# #plt.grid()
# plt.savefig("filename.png")
# #plt.show()

# print (buy_list[x][1])
# # print (buy_list)
# # print (MACD[500])
# # print (start)
# # print (end)
    
    
    
    
def data_deal():
    #Return the day of the week as an integer, where Monday is 0 and Sunday is 6.
    now = datetime.now()
    df_statements=[]
    tmp=[]
    
    print (now)
    #(datetime.datetime.now()+datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
    for y in range (0,10000,1):
        now_stock_number=""
        tmp=[]
        for x in range (int(now.weekday()),2000,1):
            d2 =now+datetmp.timedelta(days=-x)
            file_path = "./history_data/"+d2.strftime("%Y%m%d")+"statements.csv"
            if  (os.path.isfile(file_path)):
                print("File exists!")
                
                if (int(d2.weekday()) >=0 and int(d2.weekday()) <=5 and int(d2.weekday())!= int(now.weekday())):
                    print (str(d2.strftime("%Y%m%d")))
                    test = pd.read_csv(file_path) 
                    
                    try:
                        #print (test.loc[y,['證券代號','證券名稱']])
                        now_stock_number=str(test.loc[y,['證券代號']][0])
                        #print (test.loc[0,['證券代號']][0])
                        test.loc[y,'日期']=str(d2.strftime("%Y/%m/%d"))
                        tmp.append((test.loc[y,['日期','成交股數','成交筆數','成交金額','開盤價','最高價','最低價','收盤價','漲跌(+/-)','本益比']]))
                        print (tmp)
                    except:
                        print("An exception occurred")
                        continue
                continue
        df = pd.DataFrame(tmp, columns=list(['日期','成交股數','成交筆數','成交金額','開盤價','最高價','最低價','收盤價','漲跌(+/-)','本益比'])) 
        df.to_csv("./stock/"+now_stock_number+".csv", index=False)   
          #  df_statements=popmoder.get_today_tw(str(d2.strftime("%Y%m%d")))
           # x=random.randint(17, 20)
           # print (x)
           # time.sleep(x)
            #break
    #print (df_statements.loc[0,['證券代號','證券名稱','成交股數','成交筆數','成交金額','開盤價','最高價','最低價','收盤價','漲跌(+/-)','本益比']])
    
#畫圖區~~~~~~~~~
def get_statements():
    #Return the day of the week as an integer, where Monday is 0 and Sunday is 6.
    now = datetime.now()+datetmp.timedelta(days=-1420)
    df_statements=[]
    
    #(datetime.datetime.now()+datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
    for x in range (int(now.weekday()),1060,1):
        d2 =now+datetmp.timedelta(days=-x)
        file_path = "./history_data/"+d2.strftime("%Y%m%d")+"statements.csv"
        if  (os.path.isfile(file_path)):
            print("File exists!")
            continue
        if (int(d2.weekday()) >=0 and int(d2.weekday()) <=5 and int(d2.weekday())!= int(now.weekday())):
            print (str(d2.strftime("%Y%m%d")))
            df_statements=popmoder.get_today_tw(str(d2.strftime("%Y%m%d")))
            x=random.randint(17, 20)
            print (x)
            time.sleep(x)
            #break
    #print (df_statements.loc[0,['證券代號','證券名稱','成交股數','成交筆數','成交金額','開盤價','最高價','最低價','收盤價','漲跌(+/-)','本益比']])
    create_gride_statements(df_statements)
def create_gride_statements(df_statements):
    ## 篩選本益比
    #table grid
    height = 20
    width = 10
    namR = []
    parman=['證券代號','證券名稱','成交股數','成交筆數','成交金額','開盤價','最高價','最低價','收盤價','漲跌(+/-)','本益比']
    x=0
    z=0
    #df2 = df_statements[pd.to_numeric(df_statements['本益比'], errors='coerce') < 15]
    #df2.to_csv("./sss.csv", index=False)
    df_statements = pd.read_csv("20181224statements.csv")
    for i in range(height): #Rows
        z=0
        for j in range(width): #Columns
            namR.append(tk.Entry(frame6))
            namR[x].grid(row=i, column=j)
            namR[x].insert(0,str(df_statements.loc[x,parman[z]]))
            x+=1
            z+=1
    #for x in range (0,len(namR),1):
       # namR[x].insert(x,str(x))
    
    

def show_fbpropht():
    global fbpropht_data
    
    df = pd.read_csv('price.csv', index_col='date', parse_dates=['date'])
    price = df.squeeze()
    price.head()
    tsmc = Stocker(price)
    model, model_data ,ax, fig= tsmc.create_prophet_model(days=90)
    tsmc.changepoint_prior_analysis(changepoint_priors=[0.001, 0.05, 0.1, 0.2])
    fbpropht_data = model_data
    drawPic.f2.clf()
    drawPic.f2 = fig
    drawPic.canvas2 = FigureCanvasTkAgg(drawPic.f2, master=frame2)
    drawPic.a =ax 
    drawPic.a.set_title('price')
    drawPic.f2.subplots_adjust(hspace=0)
    drawPic.canvas2.show()
    drawPic.canvas2.get_tk_widget().grid(row=0,column=5,columnspan=1 , rowspan=6)   
    fbpropht_data0 = pd.read_csv('fbprophet0.csv')
    fbpropht_data1 = pd.read_csv('fbprophet1.csv')
    fbpropht_data2 = pd.read_csv('fbprophet2.csv')
    fbpropht_data3 = pd.read_csv('fbprophet3.csv')
    gain ( "fbpropht_data0",close [ len (close) -1 ],fbpropht_data0[fbpropht_data0['ds']>(  date[len(date)-1]) ])
    gain ( "fbpropht_data1",close [ len (close) -1 ],fbpropht_data1[fbpropht_data1['ds']>(  date[len(date)-1]) ])
    gain ( "fbpropht_data2",close [ len (close) -1 ],fbpropht_data2[fbpropht_data2['ds']>(  date[len(date)-1]) ])
    gain ( "fbpropht_data3",close [ len (close) -1 ],fbpropht_data3[fbpropht_data3['ds']>(  date[len(date)-1]) ])
    #print ( fbpropht_data0[fbpropht_data0['ds']>(  date[len(date)-1]) ])
    #print ()
    
    tk.messagebox.showinfo("show_fbpropht","預言家模組開啟")
    
def gain (name,inital,data):
    data.columns = range(len(data.columns)) 
    data.index = range(len(data.index)) 
    print (name)
    #print (data)
    print ( "前"+str((int(len(data)/4)) *1)+"筆漲幅" + str(float( ((data.loc [ int(len(data)/4) *1,1]-inital ) /inital  )*100)))
    print ( "前"+str((int(len(data)/4)) *2)+"筆漲幅" + str(float( ((data.loc [ int(len(data)/4) *2,1]-inital ) /inital  )*100)))
    print ( "前"+str((int(len(data)/4)) *3)+"筆漲幅" + str(float( ((data.loc [ int(len(data)/4) *3,1]-inital ) /inital  )*100)))
    print ( "前"+str((int(len(data)/4)) *4)+"筆漲幅" + str(float( ((data.loc [ int(len(data)/4) *4,1]-inital ) /inital  )*100)))
    #print ("60天漲幅" + str(float( ((data.loc [ int( 738+ 60) ,["trend"]]-inital)  /inital  )*100)))
    #print ("90天漲幅" + str(float( ((data.loc [ int(738+ 90) ,["trend"]]-inital)  /inital  )*100)))
    #print ("120天漲幅" + str(float( ((data.loc [ int(738+ 120) ,["trend"]]-inital)  /inital  )*100)))
   
def show_lstm():
    print ("暫時")
def show_info():
    global deposit
    global str_tmp

    
    #print (deposit)
    #tk.messagebox.showinfo("績效",str_tmp)
def clock():
    global start
    global end
    t=time.strftime('%I:%M:%S',time.localtime())
    if t!='':
        #var5.set(date[int(var.get())])
        start=var.get()
        #var6.set(date[int(var2.get())])
        end=var2.get()
        
    root.after(500,clock)

def drawPic():
    global deposit
    global str_tmp
    global date_ex
    global BBand_up
    global BBand_sma
    global BBand_down
    global BBand_width
    global BBand_mid
    global strategy_model
    global draw_tmp
    global deposit
    global str_tmp
    global thread_bolean 
    global buy_list
    global sell_list 
    
    buy_list=[]
    sell_list=[]
#    root.title("執行繪圖中..")
#    strategy_model =numberChosen.get()
    
    ## 取得模組名稱
    backer("BBand")
    print("testend")
#    drawPic.f.clf()
#    draw_tmp.f.clf()
    #ax.set_xticks([])
    #frame.axes.get_yaxis().set_visible(False)

# 
#    drawPic.a =drawPic.f.add_axes([0.1,0.4,0.8,0.5])
#    drawPic.a2 = drawPic.f.add_axes([0.1,0.190,0.8,0.2])
#    
#    drawPic.f.subplots_adjust(hspace=0)
#    drawPic.f.tight_layout()
#    drawPic.a.xaxis_date()
#    drawPic.a2.xaxis_date()
#    for label in drawPic.a.xaxis.get_ticklabels():   
#       label.set_rotation(45)
#    for label in drawPic.a2.xaxis.get_ticklabels():   
#       label.set_rotation(45)
 #   drawPic.a.set_title("K線圖", fontsize=20)
  #  drawPic.a2.set_xlabel("時間", fontsize=10)
   # drawPic.a.set_ylabel("股價", fontsize=10)
    #drawPic.a2.set_ylabel("成交量", fontsize=10)
#    drawPic.a.set_title("K", fontsize=20)
#    drawPic.a2.set_xlabel("time", fontsize=10)
#    drawPic.a.set_ylabel("price", fontsize=10)
#    drawPic.a2.set_ylabel("volume", fontsize=10)

    # 设置X轴刻度为日期时间
    #data_list.reverse()
    sma_5 = talib.SMA(np.array(close), 5)
    sma_10 = talib.SMA(np.array(close), 10)
    sma_20 = talib.SMA(np.array(close), 20)
    sma_60 = talib.SMA(np.array(close), 60)
#print (len(data_list))
#    start =int(var.get())
#    end=int(var2.get())
#    if(var4.get()==1):
#        drawPic.a.plot( date_ex[start:end:5],sma_5[start:end:5], label='SMA5')
#        drawPic.a.plot( date_ex[start:end:10],sma_10[start:end:10], label='SMA10')
#        drawPic.a.plot( date_ex[start:end:20],sma_20[start:end:20], label='SMA20')
#        drawPic.a.plot( date_ex[start:end:60],sma_60[start:end:60], label='SMA60')
#        drawPic.a.legend(loc='upper left')
#  
        
#    var5.set(date[start])
#    var6.set(date[end])
#    candlestick_ohlc(drawPic.a, data_list[start:end+1], width=0.5, colorup='r', colordown='g')
    #tupleto_listtmp=[]
    pos_d =[]
    pos_v =[]
    neg_d =[]
    neg_v =[]
    #開盤-收盤

    for x in data_list2[start:end+1]:
        if((x[1]-x[4])<=0):
            pos_d.append(x[0])
            pos_v.append(x[5])
        elif ((x[1]-x[4])>0):
            neg_d.append(x[0])
            neg_v.append(x[5])
#
#    drawPic.a2.bar(pos_d,pos_v,color='red',width=0.5,align='center')
#    drawPic.a2.bar(neg_d,neg_v,color='green',width=0.5,align='center')
            
    #drawPic.a2.bar(pos[0][0],pos[0][1],color='green',width=1,align='center')
    #print (tupleto_listtmp)
    # for x in pos:
    #     drawPic.a2.bar(x[0],x[1],color='green',width=1,align='center')
    #for x in neg:
    #    drawPic.a2.bar(x[0],x[1],color='red',width=1,align='center')
    #drawPic.a2.bar(pos[:][0],pos[:][1],color='green',width=1,align='center')
    #drawPic.a2.bar(neg[:][0],neg[:][1],color='red',width=1,align='center')
    #volume_overlay3(drawPic.a2,data_list2[start:end], colorup='r', colordown='g', width=0.5, alpha=0.8)
    
#    if(var7.get()==1):
    BBand=popmoder.get_BBand(np.asarray(close))
    BBand_up=[]
    BBand_sma=[]
    BBand_down=[]
    BBand_up=[float(x) for x in BBand  [0]]
    BBand_sma=[float(x) for x in BBand  [1]]
    BBand_down=[float(x) for x in BBand  [2]]
        
        
#        drawPic.a.plot( date_ex[start:end:1],BBand_sma[start:end:1], label='BBnad')
#        drawPic.a.plot( date_ex[start:end:1],BBand_up[start:end:1], label='BBnad_up')
#        drawPic.a.plot( date_ex[start:end:1],BBand_down[start:end:1], label='BBnad_down')
#        drawPic.a.legend(loc='upper left')
#    if(var8.get()==1):
    BBand_up=[float(x) for x in BBand  [0]]
    BBand_sma=[float(x) for x in BBand  [1]]
    BBand_down=[float(x) for x in BBand  [2]]
       
    BBand_mid=[]
    BBand_width=[]
    for x in range(0,len(BBand_sma),1):
        BBand_mid.append((BBand_up[x]+BBand_down[x])/2)
        #print ((BBand_mid))
    
    for x in range(0,len(BBand_mid),1):
        BBand_width.append(100*((BBand_up[x]-BBand_down[x])/BBand_mid[x]))
            
#        drawPic.a.plot( date_ex[start:end:1],BBand_width[start:end:1], label='BBnad_width')
#        drawPic.a.legend(loc='upper left')
    # for x in range(start,end,1):    
    #     drawPic.a.plot( date_ex[start:end:1],BBand_sma[start:end:1], label='bb')
    #     drawPic.a.plot(date_ex[x],BBand_sma[x], label='bb')
#    if(var3.get()==1):
#        for x in range(0,len(buy_list),1):    
#            drawPic.a.annotate('', xy=(buy_list[x][0],buy_list[x][1]), xytext=(-15, -27),
#              textcoords='offset points', ha="center",
#                 arrowprops=dict(facecolor='black', color='red',width=0.5),
#            )
#            
#        for x in range(0,len(sell_list),1):    
#            drawPic.a.annotate('', xy=(sell_list[x][0],sell_list[x][1]),  xytext=(-17, 20),
#              textcoords='offset points', ha="center",
#                 arrowprops=dict(facecolor='black', color='green',width=0.5),
#            )

 
#
#    drawPic.a.grid()
#    drawPic.a2.grid()
#    drawPic.canvas.show()
  
    df = pd.read_csv('price2.csv', index_col='date', parse_dates=['date'])
    price = df.squeeze()
    price.head()
#    drawPic.f2 = Figure(figsize=(10,4)) 
#    drawPic.canvas2 = FigureCanvasTkAgg(drawPic.f2, master=frame2)
#    drawPic.f2.clf()
#    drawPic.a =drawPic.f2.add_axes([0.1,0.1,0.8,0.8])
#    drawPic.a.set_title('price')
#    drawPic.f2.subplots_adjust(hspace=0) 
#    drawPic.a.plot(price)
#    drawPic.a.text(0.13, 0.3, str_tmp,transform=drawPic.f2.transFigure, fontsize=15, color='red',)
#    
#    drawPic.canvas2.show()
#    #drawPic.f2.set_size_inches(7, 3, forward=True) 
#    drawPic.canvas2.get_tk_widget().grid(row=0,column=5,columnspan=1 , rowspan=6)   
    show_info()
#    root.title("回測工具")

    
def insert_point():
    var = e.get(root)
    tk.messagebox.showinfo("績效",e.get())
def get_historical_data(name, number_of_days):
    global catch_stockgarbage
    max_bb=0
    data = []
    url = "https://finance.yahoo.com/quote/" + name + "/history/"

    try:
        rows = BeautifulSoup(urllib.request.urlopen(url).read()).findAll('table')[0].tbody.findAll('tr')
            
        for each_row in rows:
            divs = each_row.findAll('td')
            if divs[1].span.text  != 'Dividend': #Ignore this row in the table
                #I'm only interested in 'Open' price; For other values, play with divs[1 - 5]
                date_process=divs[0].span.text.replace(",", "")
                date_process=datetime.strptime(date_process, '%b %d %Y').date().strftime('%Y/%m/%d')
                t = date_process.replace('/','-')
                date_process = (dates.date2num(datetime.strptime(t, '%Y-%m-%d')))
                    #date_process=datetime.datetime.strptime(date_process, '%b %d %Y').date().strftime('%m %d %Y')
                    #data.append({'Date': str(date_process), 'Open': float(divs[1].span.text.replace(',',''))\
                                                        # , 'High': float(divs[2].span.text.replace(',',''))\
                                                        # , 'Low': float(divs[3].span.text.replace(',',''))\
                                                        # , 'Close': float(divs[4].span.text.replace(',',''))\
                                                        # , 'Volume': float(divs[6].span.text.replace(',',''))})
                #datas2 = (dates.date2num(datetime.strptime(t, '%Y-%m-%d')) , ope[x], high[x], low[x],close[x],vol[x])#
                data.append([ str(date_process), float(divs[1].span.text.replace(',',''))\
                                                        ,  float(divs[2].span.text.replace(',',''))\
                                                        ,  float(divs[3].span.text.replace(',',''))\
                                                        ,  float(divs[4].span.text.replace(',',''))\
                                                        ,  float(divs[6].span.text.replace(',',''))])
                    #篩選指標
        date.clear()
        low.clear()
        high.clear()
        close.clear()
        ope.clear()
        vol.clear()
        for x in data:
            date.append(x[0])
            ope.append(x[1])
            high.append(x[2])
            low.append(x[3])
            close.append(x[4])
            vol.append(x[5])
        date.reverse()
        low.reverse()
        high.reverse()
        close.reverse()
        ope.reverse()
        vol.reverse()

                
        BBand=get_BBand()
        BBand_up=[float(x) for x in BBand  [0]]
        BBand_sma=[float(x) for x in BBand  [1]]
        BBand_down=[float(x) for x in BBand  [2]]
       
        BBand_mid=[]
        BBand_width=[]
        for x in range(0,len(BBand_sma),1):
            BBand_mid.append((BBand_up[x]+BBand_down[x])/2)


        for x in range(0,len(BBand_mid),1):
            BBand_width.append(100*((BBand_up[x]-BBand_down[x])/BBand_mid[x]))
            #print (BBand_width)
            #print (max(BBand_width[20:]))

        print ('----------')
        max_vol=max(vol[-10:])
                #if(max(BBand_width[20:]))
                #return data[:number_of_days]

        if(max_vol>15*1000): #成交量大於1500
            max_bb=max(BBand_width[20:])
            #print (max(BBand_width[20:]))
        print (max_bb)
        print (max_vol)
    except  Exception as e:
        global catch_stockgarbage
            #print ('找不到所選資料,或發生異常錯誤.')
        max_bb=0
        #catch_stockgarbage.append(name)
    
    return  max_bb
def read_file2():
    fname = filedialog.askopenfilename(title=u"選擇回測檔案",
                                     initialdir=(os.path.expanduser(default_dir)))
    read_file(fname)
def call_download():
    global catch_stock
    global catch_stockgarbage
    catch_stock=[]
    #table grid
    height = len(catch_stock)
    width = 1
    count=0
    tree = ttk.Treeview(frame6, show="headings")
    tree["columns"]=('col1','col2')
    tree.column('col1', width=50)
    tree.column('col2', width=200)


    tree.heading('col1', text='num')
    tree.heading('col2', text='股票代號')
    tree.grid(row=0,column=0)
    #近三個月 bb寬度篩選

    # 建立 5 個子執行緒
    threads = []
    catch_stockgarbage=[]
    for x in range (1200,10000,2):
        for i in range(2):
            threads.append(threading.Thread(target = job, args = (x+i,)))
            threads[i].start()
            print (x+i)
            root.update()
            frame6.update()
        # 等待所有子執行緒結束
        for i in range(2):
            threads[i].join()

        threads.clear()


    # for x in range(1234,9999,1):
    #     if(get_historical_data(str(x)+'.TW', 90)>20):
    #         catch_stock.append(str(x)+'.TW')
    #         tree.insert('',i,text=str(i),values=('',str(x)+'.TW'))
    #         count=count+1

    print("Done.")
    
    print ('----------')
    print ('捕捉BBAND寬度>10股票')      
    for i in tree.get_children():
        tree.delete(i)
    for x in range(0,len(catch_stock),1):
        tree.insert('',count,text=str(i),values=(str(count),catch_stock[count]))
        count=count+1
    print (catch_stockgarbage)
    print (catch_stock)

    # for i in range (0,len(catch_stock),1):
    #     tree.insert('',i,text=str(i),values=(str(i),catch_stock[i]))
    
    # for x in catch_stock:
    #     b = Entry(frame6, text="11")
    #     b.grid(row=count, column=0)
    #     b.insert(0,x[count])
    #     count=count+1


    # for i in range(height): #Rows
    #     for j in range(width): #Columns
    #         b = tk.Entry(frame6, text="11")
    #         b.grid(row=i, column=j)
    #         b.insert(0,'50')

        # for i in get_historical_data(str(x)+'.TW', 90):
        #     print (i)
    
def print_selection():
    print( var.get())
#default_dir = r"C:\Users\lenovo\Desktop"  # 设置默认打开目录
#fname = filedialog.askopenfilename(title=u"選擇回測檔案",
#                                     initialdir=(os.path.expanduser(default_dir)))




#w, h = root.winfo_screenwidth(), root.winfo_screenheight()
#root.geometry("%dx%d+0+0" % (1360, 800))
#
#root.title("回測工具")
#notebook = ttk.Notebook(root)
#notebook2 = ttk.Notebook(root)
#
#frame1 = ttk.Frame(notebook)
#frame4 = ttk.Frame(notebook)
#frame5 = ttk.Frame(notebook)
#frame6 = ttk.Frame(notebook)
##
#frame2 = ttk.Frame(notebook2)
#frame3 = ttk.Frame(notebook2)
#frame7 = ttk.Frame(notebook2)
#frame8 = ttk.Frame(notebook2)
#
#notebook.add(frame1, text='回測技術分析')
#notebook.add(frame5, text='即時技術分析')
#notebook.add(frame4, text='即時監控')
#notebook.add(frame6, text='股票快篩')
#notebook2.add(frame2, text='工具箱')
#notebook2.add(frame3, text='策略微調')
#notebook2.add(frame7, text='快篩微調')
#notebook2.add(frame8, text='機器學習微調')

#工具箱

#clock()
#notebook.grid(row=0,column=0,sticky="nsew")
#notebook2.grid(sticky="nsew",row=1,column=0, columnspan=3, padx=10, pady=10,fill = None)
#drawPic.f = Figure(figsize=(18.3,6)) 
#drawPic.canvas = FigureCanvasTkAgg(drawPic.f, master=frame1)
#drawPic.f.clf()
#drawPic.canvas.show()
#drawPic.canvas.get_tk_widget().grid(row=0)    
#
#tk.Button(frame2,text='回測',command=drawPic).grid(row=0,column=0,columnspan=1)
#tk.Button(frame2,text='績效',command=show_info).grid(row=0,column=1,columnspan=1)
#tk.Button(frame2,text='特殊模組開啟',command=show_fbpropht).grid(row=0,column=3,columnspan=1)
#tk.Button(frame2,text='數據處理',command=data_deal).grid(row=0,column=4,columnspan=1)
#
#
#number = tk.StringVar()
#numberChosen = ttk.Combobox(frame2, width=12, textvariable=number)
#numberChosen['values'] = ("BBand","Rsi", "Arron","ATR","KD","T3",
#            "一紅吃一黑","紅三兵","辰星","跳空買進","arr","fbpropht",
#            "keras", "google_trend")     # 设置下拉列表的值
#numberChosen.grid(row=0,column=2,columnspan=1)      # 设置其在界面中出现的位置  column代表列   row 代表行
#numberChosen.current(0)    # 设置下拉列表默认显示的值，0为 numberChosen['values'] 的下标值
#
#drawPic.f2 = Figure(figsize=(10,4)) 
#drawPic.canvas2 = FigureCanvasTkAgg(drawPic.f2, master=frame2)
#drawPic.f2.clf()
#
#drawPic.canvas2.show()
#drawPic.canvas2.get_tk_widget().grid(row=0,column=5,columnspan=1 , rowspan=6)   
#
#draw_tmp = drawPic


#c1 = tk.Checkbutton(frame2, text='買賣點', variable=var3, onvalue=1, offvalue=0,
#                    ).grid(row=2,column=2)
#c2 = tk.Checkbutton(frame2, text='SMA', variable=var4, onvalue=1, offvalue=0,
#                    ).grid(row=3,column=2)
#c3 = tk.Checkbutton(frame2, text='BBnad', variable=var7, onvalue=1, offvalue=0,
#                    ).grid(row=4,column=2)
#c4 = tk.Checkbutton(frame2, text='BBnad_width', variable=var8, onvalue=1, offvalue=0,
#                    ).grid(row=5,column=2)
##tk.Label(frame2,text='请输入样本数量：').grid(row=1,column=0)
##inputEntry=tk.Entry(frame2)
##inputEntry.grid(row=1,column=1)
##inputEntry.insert(0,'50')
#
#data_label = tk.Label(frame2, text='-----', textvariable=var5).grid(row=3,column=0)
#data_label2 = tk.Label(frame2, text='-----', textvariable=var6).grid(row=3,column=1)
#e = tk.Entry(frame2,show='*').grid(row=4,column=0)
##快篩微調
#e2 = tk.Entry(frame7, textvariable=var9).grid(row=0,column=1)
#e3 = tk.Entry(frame7, textvariable=var10).grid(row=0,column=3)
#e3 = tk.Entry(frame7, textvariable=var11).grid(row=1,column=1)
#e4 = tk.Entry(frame7, textvariable=var12).grid(row=1,column=3)
#var9.set('1000')
#var10.set('9999')
#var11.set('<')
#var12.set('15')
#b1 = tk.Button(frame2,text="read_file",width=15,height=2,command=read_file2).grid(row=4,column=1)
#b2 = tk.Button(frame7,text="篩選",command=call_download).grid(row=0,column=4)
#tk.Button(frame7,text='取得財務報表',command=get_statements).grid(row=1,column=4,columnspan=2)
#L1 = tk.Label(frame7, text="運算子").grid(row=1,column=0)
#L2 = tk.Label(frame7, text="Value").grid(row=1,column=2)
#L1 = tk.Label(frame7, text="起始範圍").grid(row=0,column=0)
#L2 = tk.Label(frame7, text="結束範圍").grid(row=0,column=2)
#機器學習微調
#tk.Button(frame8,text='呼叫lstm',command=show_lstm).grid(row=1,column=4,columnspan=2)
#drawPic()
# 子執行緒的工作函數
def job(num):
    global catch_stock

    tmp=''
    if(get_historical_data(str(num)+'.TW',60)>20):
        catch_stock.append(str(num)+'.TW')
        tmp=str(num)+'.TW'


    print (tmp)

# 子執行緒的工作函數

  

app = Flask(__name__)
api = Api(app)

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    'todo3': {'task': 'profit!'},
}


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('task')


# Todo
# shows a single todo item and lets you delete a todo item
class Todo(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
#        json.load(urllib.request.urlopen("http://localhost:9000/321"))
        test2222 ="";
        url = "http://localhost:9000/321"
        
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode('utf-8'))
        print(data[0])
#        return TODOS[todo_id]
#        read_file(fname)
#        default_dir = r"C:\Users\lenovo\Desktop"  # 设置默认打开目录
#        fname = filedialog.askopenfilename(title=u"選擇回測檔案",
#                                             initialdir=(os.path.expanduser(default_dir)))
#        read_file()
        test_data = []
        for x in data :
            test_data.append([x[0],x[1],x[2],x[3],x[4],x[5]])
        read_file(test_data)
        
        drawPic()
#        app.logger.info('Info' +str_tmp)
#        app.logger.warning('A warning occurred (%d apples)', 42)
#        app.logger.error('An error occurred')
#        app.logger.info('Info')
#        b = bytes(str_tmp, 'utf-8')
#        str_tmp = str_tmp.encode('big5').decode('utf8')
#        return str_tmp.encode('utf8').decode('utf8','ignore')
#       // tmp = str_tmp.encode('big5').decode('unicode-escape')
#        u = unicode(str_tmp, "utf-8")
        stock_data ={};
        
        stock_data.clear()
        stock_data['bbandup']= list()
        
        stock_data['bbanddown']= list()
        
        stock_data['bbandwidth']= list()
        
        stock_data['buy_list']= list()
        
        stock_data['sell_list']= list()
        
        BBand_width
        
        for x in range (len(BBand_up)-1 , 0 , -1):
            if(  ~np.isnan(BBand_up[x])):
#        time.mktime(datetime.datetime.strptime(str(buy_list[x][0]), '%Y-%m-%d %H:%M:%S').timetuple())
#        time.mktime(datetime.datetime.strptime(str(buy_list[x][0]), "%d/%m/%Y").timetuple())
              
                stock_data['bbandup'].append([date[x],BBand_up[x]])
                stock_data['bbanddown'].append([date[x],BBand_down[x]])
                stock_data['bbandwidth'].append([date[x],BBand_width[x]])
        for x in range (0, len(buy_list), 1):
                stock_data['buy_list'].append([ str(buy_list[x][0]).split()[0],buy_list[x][1]])
        for x in range (0, len(sell_list), 1):
                stock_data['sell_list'].append([ str(sell_list[x][0]).split()[0],sell_list[x][1]])
                
#        for x in range (len(sell_list)-1,0 , -1):
#                stock_data['sell_list'].append([sell_list[x]])
                
#                tmp.append(  [date[x],BBand_up[x]])
#                tmp.
        
        return stock_data

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        return TODOS

    def post(self):
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TODOS[todo_id] = {'task': args['task']}
       
        return TODOS[todo_id], 201

##
## Actually setup the Api resource routing here
##
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')
# 跨域支持
def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = 'http://172.16.7.21:8080'
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp

app.after_request(after_request)


if __name__ == '__main__':
    
    handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(debug=True)
    _job = None
    
```

**`main.go`**

```go
package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
    //"github.com/go-sql-driver/mysql"
	"github.com/gorilla/mux"
	"reflect"
	"time"
	"strings"
	//"strconv"
)
import _ "github.com/go-sql-driver/mysql"
var people []Person

type Person struct {
	ID      string   `json:"id,omitempty"`
	Name    string   `json:"name,omitempty"`
	Address *Address `json:"address,omitempty"`
}
type Stock struct {
    Date      string    `json:"date"`
    Open string `json:"open"`
	High   string `json:"high"`
	Low     string    `json:"low"`
    Close string `json:"close"`
    Volume   string `json:"volume"`
}
type Address struct {
	Country string `json:"country,omitempty"`
	City    string `json:"city,omitempty"`
}

func DefaultHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprint(w, "Home")
	fmt.Fprint(w, "Home")
	fmt.Fprint(w, "Home")

}
// 定义一个结构体, 需要大写开头哦, 字段名也需要大写开头哦, 否则json模块会识别不了
// 结构体成员仅大写开头外界才能访问
type User struct {
    User      string    `json:"user"`
    Password string `json:"password"`
    Host   string `json:"host"`
}
func PeopleHandler(w http.ResponseWriter, r *http.Request) {

	w.Header().Set("Access-Control-Allow-Origin", "*")
	json.NewEncoder(w).Encode(people)

}

func PersonHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	params := mux.Vars(r)
	for _, item := range people {
		if item.ID == params["id"] {
			json.NewEncoder(w).Encode(item)
		}
	}

}
func HttpFileHandler(response http.ResponseWriter, request *http.Request) {
	//fmt.Fprintf(w, "Hi from e %s!", r.URL.Path[1:])
	http.ServeFile(response, request, "index.html")
}
func HttpFileHandler2(response http.ResponseWriter, request *http.Request) {
	//fmt.Fprintf(w, "Hi from e %s!", r.URL.Path[1:])
	http.ServeFile(response, request, "details.html")
}
func HttpFileHandler3(response http.ResponseWriter, request *http.Request) {
	//fmt.Fprintf(w, "Hi from e %s!", r.URL.Path[1:])
	http.ServeFile(response, request, "123.html")
}
func getFieldString(e *Stock, field string) string {
	r := reflect.ValueOf(e)
	f := reflect.Indirect(r).FieldByName(field)
	return f.String()
}

func checkCount(rows *sql.Rows) (count int) {
	for rows.Next() {
	   err:= rows.Scan(&count)
	   checkErr(err)
   }   
   return count
}

func checkErr(err error) {
   if err != nil {
	   panic(err)
   }
}
func HttpFileHandler4(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "http://172.16.7.21:8080")
	w.Header().Set("Access-Control-Allow-Credentials", "true")
	
	db, e := sql.Open("mysql", "root:1234@tcp(localhost:3306)/mysql?charset=utf8")
    if e != nil { //如果连接出错,e将不是nil的
        print("ERROR?")
        return
	}

    // 提醒一句, 运行到这里, 并不代表数据库连接是完全OK的, 因为发送第一条SQL才会校验密码 汗~!
    _, e2 := db.Query("select 1")
    if e2 == nil {
		println("DB OK")
		ttt,err := db.Exec("USE stock")
		if err != nil {
			print("ERROR?")
			return
		}
		fmt.Print(ttt)
        rows, e := db.Query("SELECT date,open,high,low,close,volume FROM `1216tw`;")
        if e != nil {
			fmt.Print("query error!!%v\n", e)
			
            return
		}
		fmt.Print(rows)
        if rows == nil {
            print("Rows is nil")   
            return
		}
	
		var first int
		first=0
		fmt.Fprintln(w,"[")
		for rows.Next() { //跟java的ResultSet一样,需要先next读取
			if first!=0{
				if rows.Next()!=false{
					fmt.Fprintln(w,",")
				}
			}
			if first==0{
				first=1
			}
		
			
            stock := new(Stock)
			// rows貌似只支持Scan方法 继续汗~! 当然,可以通过GetColumns()来得到字段顺序

            row_err := rows.Scan(&stock.Date,&stock.Open,&stock.High,&stock.Low,&stock.Close,&stock.Volume)
            if row_err != nil {
				//print("Row error!!")
				fmt.Fprintln(w,"]")
                return
			}
			fmt.Fprint(w,"[")
			tm2, _ := time.Parse("2006-01-02 15:04:05", strings.Replace(getFieldString(stock, "Date"), "/", "-", 2)+" 00:00:00")
	
			//fmt.Println(fmt.Sprint((int64(tm2.Unix()))))
			
			//fmt.Print(int32(tm2.Unix()))
			//fmt.Println(strings.Replace(getFieldString(stock, "Date"), "/", "-", 2)+" 00:00:00")
			//fmt.Print(int32(tm2.Unix()))
			fmt.Fprint(w,fmt.Sprint((int64(tm2.Unix()*1000)))+",")
			fmt.Fprint(w,getFieldString(stock, "Open")+",")
			fmt.Fprint(w,getFieldString(stock, "High")+",")
			fmt.Fprint(w,getFieldString(stock, "Low")+",")
			fmt.Fprint(w,getFieldString(stock, "Close")+",")
			fmt.Fprint(w,getFieldString(stock, "Volume"))
			fmt.Fprintln(w,"]")
			
			// fmt.Fprintln(w,checkCount(&rows))
            // b, _ := json.Marshal(stock)
			// fmt.Println(string(b)) // 这里没有判断错误, 呵呵, 一般都不会有错吧
			//fmt.Fprint(w,string(b))
        }
		fmt.Fprintln(w,"]")
	
    }

}

func getFromdatabase() {

	db, e := sql.Open("mysql", "root:1234@tcp(localhost:3306)/mysql?charset=utf8")
    if e != nil { 
        print("ERROR?")
        return
    }
   
    _, e2 := db.Query("select 1")
    if e2 == nil {
        println("DB OK")
        rows, e := db.Query("select user,password,host from mysql.user")
        if e != nil {
            fmt.Print("query error!!%v\n", e)
            return
        }
        if rows == nil {
            print("Rows is nil")   
            return
        }
        for rows.Next() { 
            user := new(User)
         
            row_err := rows.Scan(&user.User,&user.Password, &user.Host)
            if row_err != nil {
                print("Row error!!")
                return
            }
            b, _ := json.Marshal(user)
            fmt.Println(string(b)) 
        }

    }

}
func getFromdatabase2() {

	db, e := sql.Open("mysql", "root:1234@tcp(localhost:3306)/mysql?charset=utf8")
    if e != nil { //如果连接出错,e将不是nil的
        print("ERROR?")
        return
	}

    // 提醒一句, 运行到这里, 并不代表数据库连接是完全OK的, 因为发送第一条SQL才会校验密码 汗~!
    _, e2 := db.Query("select 1")
    if e2 == nil {
		println("DB OK")
		ttt,err := db.Exec("USE stock")
		if err != nil {
			print("ERROR?")
			return
		}
		fmt.Print(ttt)
        rows, e := db.Query("SELECT date,open,high,low,close,volume FROM `1216tw`;")
        if e != nil {
			fmt.Print("query error!!%v\n", e)
			
            return
		}
		fmt.Print(rows)
        if rows == nil {
            print("Rows is nil")   
            return
		}

		for rows.Next() { //跟java的ResultSet一样,需要先next读取

            stock := new(Stock)
			// rows貌似只支持Scan方法 继续汗~! 当然,可以通过GetColumns()来得到字段顺序

            row_err := rows.Scan(&stock.Date,&stock.Open,&stock.High,&stock.Low,&stock.Close,&stock.Volume)
            if row_err != nil {
                print("Row error!!")
                return
            }
            b, _ := json.Marshal(stock)
            fmt.Println(string(b)) // 这里没有判断错误, 呵呵, 一般都不会有错吧
        }

    }

}
//插入demo
func insert() {
    db, err := sql.Open("mysql", "root:1234@tcp(localhost:3306)/mysql?charset=utf8")

    stmt, err := db.Prepare(`INSERT user (Host,user,password) values (?,?,?)`)
	if err != nil {
		panic(err)
	}
    res, err := stmt.Exec("tony", 20, 1)
	if err != nil {
		panic(err)
	}
    id, err := res.LastInsertId()
	if err != nil {
		panic(err)
	}
    fmt.Println(id)
}
func create(name string) {

	db, err := sql.Open("mysql", "root:1234@tcp(localhost:3306)/mysql?charset=utf8")
	if err != nil {
		panic(err)
	}
	defer db.Close()
 

 
	_,err = db.Exec("USE stock")
	if err != nil {
		panic(err)
	}
	var  query string
	
	query="CREATE TABLE "+name+"  (data varchar(32) ,open float, high float, low float ,close float , volume float)"

	fmt.Println(query)

	_,err = db.Exec(query)
	if err != nil {
		panic(err)
	}
 }
 func update() {
    db, err := sql.Open("mysql", "root:1234@tcp(localhost:3306)/mysql?charset=utf8")
	if err != nil {
		panic(err)
	}
    stmt, err := db.Prepare(`UPDATE user SET user_age=?,user_sex=? WHERE user_id=?`)
	if err != nil {
		panic(err)
	}
    res, err := stmt.Exec(21, 2, 1)
	if err != nil {
		panic(err)
	}
    num, err := res.RowsAffected()
	if err != nil {
		panic(err)
	}
    fmt.Println(num)
}
 
//删除数据
func remove() {
    db, err := sql.Open("mysql", "root:1234@tcp(localhost:3306)/mysql?charset=utf8")
	if err != nil {
		panic(err)
	}
    stmt, err := db.Prepare(`DELETE FROM user WHERE user_id=?`)
	if err != nil {
		panic(err)
	}
    res, err := stmt.Exec(1)
	if err != nil {
		panic(err)
	}
    num, err := res.RowsAffected()
	if err != nil {
		panic(err)
	}
    fmt.Println(num)
}
func main() {
	route := mux.NewRouter()
	people = append(people, Person{ID: "1", Name: "sojib", Address: &Address{Country: "bangladesh", City: "Dhaka"}})
	people = append(people, Person{ID: "2", Name: "hasan", Address: &Address{Country: "china", City: "C"}})
	people = append(people, Person{ID: "3", Name: "kamal", Address: &Address{Country: "japan", City: "J"}})
	route.HandleFunc("/", DefaultHandler).Methods("Get")
	route.HandleFunc("/people", PeopleHandler).Methods("Get")
	route.HandleFunc("/people/{id}", PersonHandler).Methods("Get")
	route.HandleFunc("/index", HttpFileHandler)
	route.HandleFunc("/details", HttpFileHandler2)
	route.HandleFunc("/123", HttpFileHandler3)
	route.HandleFunc("/321", HttpFileHandler4)
	//route.Handle("/details", http.FileServer(http.Dir("/mnt/c/golangtmp")))
	//getFromdatabase2()
	//create("2015tw")
	//create("qwdwqd")
	log.Fatal(http.ListenAndServe(":9000", route))
}
```

**`main2.go`**

```go
package main

import (
    "encoding/csv"
    "fmt"
    "io"
	"os"	
	"database/sql"
)
import _ "github.com/go-sql-driver/mysql"
func typeof(v interface{}) string {
    return fmt.Sprintf("%T", v)
}
func create(name string) {

	db, err := sql.Open("mysql", "root:1234@tcp(localhost:3306)/mysql?charset=utf8")
	if err != nil {
		panic(err)
	}
	defer db.Close()
 

 
	_,err = db.Exec("USE stock")
	if err != nil {
		panic(err)
	}
	var  query string
	
	query="CREATE TABLE "+name+"  (date date ,open float, high float, low float ,close float , volume float)"

	fmt.Println(query)

	_,err = db.Exec(query)
	if err != nil {
		//panic(err)
		print (err)
	}
 }
 

//插入demo
func insert(name string,date string,open string,high string,low string,close string,volume string) {
    db, err := sql.Open("mysql", "root:1234@tcp(localhost:3306)/mysql?charset=utf8")
	if err != nil {
		panic(err)
	}
	_,err = db.Exec("USE stock")
	if err != nil {
		panic(err)
	}
    stmt, err := db.Prepare("INSERT "+name+" (date,open,high,low,close,volume) values (?,?,?,?,?,?)")
	if err != nil {
		panic(err)
	}
    res, err := stmt.Exec(date,open,high,low,close,volume)
	if err != nil {
		panic(err)
	}
	
    id, err := res.LastInsertId()
	if err != nil {
		fmt.Println(id)
	}
	
	db.Close()
}
func main() {
    file, err := os.Open("1216統一.csv")
    if err != nil {
        fmt.Println("Error:", err)
        return
	}
	create("1216tw")
	
    defer file.Close()
    reader := csv.NewReader(file)
    for {
        record, err := reader.Read()
        if err == io.EOF {
            break
        } else if err != nil {
			fmt.Println("Error:", err)
			
            return
        }
		insert("1216tw",record[0],record[1],record[2],record[3],record[4],record[5])
		//fmt.Println(record) // record has the type []string
		//fmt.Println("get:", record[0])
		//fmt.Println(strings.Replace(string(record), " ", ",", 2))
	}
	//insert("1216tw","1","1","1","1","1","1")
	fmt.Println("ok")
	
}
```

**`stock.vue`**

```vue
<template>
  <div class="act-form">
    <!--    <iframe :src="src" ref="iframe" width="100%" height="700" frameborder="0"></iframe>-->
    <button @click="test()">darw pic</button>
    <button @click="test2()">darw bband</button>
    <div id="container" style="height:600px; min-width: 310px"></div>
  </div>
</template>


<script>
export default {
  data() {
    return {
      stock_data: [],
      bband_up: [],
      bband_down: [],
      bband_width: [],
      buy_data: [],
      sell_data: []
    };
  },
  mounted() {
    // 这里就拿到了iframe的对象
    console.log(this.$refs.iframe);
  },
  methods: {
    test2() {
      this.getRequest("http://localhost:5000/todos/todo3").then(resp => {
        this.stock_data = this.bband_up = this.bband_down = this.buy_data = [];
        this.bband_up = resp.data["bbandup"];
        this.bband_down = resp.data["bbanddown"];
        this.buy_data = resp.data["buy_list"];
        this.sell_data = resp.data["sell_list"];
        this.bband_width = resp.data["bbandwidth"];

        console.log("test");
        this.test();
      });
    },
    test() {
      this.getRequest("/321").then(resp => {
        //const items = resp.data.data.items;
        this.stock_data = resp.data;
        let tmp_data = [];

        console.log(tmp_data);
        let series_tmp = [
          {
            type: "candlestick",
            name: "AAPL Stock Price",
            id: "aapl",
            zIndex: 1,
            data: this.stock_data,
            dataGrouping: {
              units: [
                [
                  "week", // unit name
                  [1] // allowed multiples
                ],
                ["month", [1, 2, 3, 4, 6]]
              ]
            }
          },

          {
            type: "macd",
            yAxis: 1,
            linkedTo: "aapl"
          },
          {
            name: "bband_up",
            data: this.bband_up,
            type: "spline",
            tooltip: {
              valueDecimals: 2
            },
            color: "green"
          },

          {
            name: "bband_down",
            data: this.bband_down,
            type: "spline",
            tooltip: {
              valueDecimals: 2
            },
            color: "green"
          },

          {
            name: "bband_width",
            data: this.bband_width,
            type: "spline",
            tooltip: {
              valueDecimals: 2
            },
            color: "blue"
          }
        ];
        console.log(series_tmp);
        let tmp = [];
        this.buy_data.forEach(function(element) {
          let array = {
            type: "flags",
            data: [
              {
                x: new Date(element[0]).getTime(),
                y: element[1],

                title: "買入" + element[1],
                text: 'Shape: "squarepin"'
              }
            ],
            onSeries: "dataseries",
            shape: "squarepin",
            width: 16,
            style: {
              // text style
              color: "red"
            }
          };
          series_tmp.push(array);
        });

        tmp = [];
        this.sell_data.forEach(function(element) {
          let array = {
            type: "flags",
            data: [
              {
                x: new Date(element[0]).getTime(),
                y: element[1],

                title: "賣出" + element[1],
                text: 'Shape: "squarepin"'
              }
            ],
            onSeries: "dataseries",
            shape: "squarepin",
            width: 16,
            style: {
              // text style
              color: "green"
            }
          };
          series_tmp.push(array);
        });

        console.log(this.buy_data);
        console.log(series_tmp);
        Highcharts.stockChart("container", {
          title: {
            text: "AAPL Stock Price"
          },

          yAxis: [
            {
              height: "75%",
              resize: {
                enabled: true
              },
              labels: {
                align: "right",
                x: -3
              },
              title: {
                text: "AAPL"
              }
            },
            {
              top: "75%",
              height: "25%",
              labels: {
                align: "right",
                x: -3
              },
              offset: 0,
              title: {
                text: "MACD"
              }
            }
          ],
          series: series_tmp
        });
      });
    }
  }
};
</script>
```
