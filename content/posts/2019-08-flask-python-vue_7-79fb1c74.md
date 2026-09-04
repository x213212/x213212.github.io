---
title: "flask python vue 股票回測 (二) 隨機森林演算法"
date: "2019-08-07T13:52:00.001+08:00"
updated: "2019-10-11T02:38:02.176+08:00"
permalink: "/2019/08/flask-python-vue_7.html"
original_url: "https://x8795278.blogspot.com/2019/08/flask-python-vue_7.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5266281503147953722"
tags: ["flask", "Python", "Stock", "Tutorial", "Vue.js"]
layout: post
---

# 隨機森林演算法

翻到以前的code來補齊一下，新增隨機森林演算法  

預測與權重誰比較重要  

在漲跌來看，在一股價移動平均線5天來看最可以影響漲跌，  

在股票不只股票，像是天氣下雨，濕度.....都可以使用隨機森林找到最有相關性的特徵!?  

![](https://i.imgur.com/E4rZMl2.png)

  

在判斷 當天和隔天的狀況下可以經由判斷前一天的close 收盤價  

新增一個 新的一個特徵點 label假設為漲跌則設為1 否則為0  

![](https://i.imgur.com/xbYc7Ak.png)

  

  

```python
    sma_5 = talib.SMA(np.array(close), 5)
    sma_10 = talib.SMA(np.array(close), 10)
    sma_20 = talib.SMA(np.array(close), 20)
    sma_60 = talib.SMA(np.array(close), 60)
    
    macd = get_MACD(np.array(close))
#    
    data_list4 = []

    for x in range (len (randomforest_list)-1 , 33 ,-1 ):
#         今天大於 昨天 等於 漲跌
        tmp =0
        if(x+1 <len (randomforest_list)):
            if((randomforest_list[x][4] > randomforest_list[x+1][4]) ):
                tmp=1
            else:
                tmp=0
#  datas2 = (t, ope[x], high[x], low[x],close[x],vol[x])
#
#        data_list4.append({'account': str(data_list2[x][0]),data_list2[x][1],data_list2[x][2],data_list2[x][3],data_list2[x][4],data_list2[x][5],sma_5[x]
#        ,sma_10[x],sma_20[x],sma_20[x], macd[x] ,tmp})

        data_list4.append({ 'date': str(randomforest_list[x][0]).split()[0],'open': str(randomforest_list[x][1]) ,
        'high': str(randomforest_list[x][2]),'low': str(randomforest_list[x][3]) ,'close': str(randomforest_list[x][4]),'vol': str(randomforest_list[x][5]) 
        ,'ma5': sma_5[x] ,'ma10':sma_10[x] ,'ma20': sma_20[x],'macd': macd[x],'label': tmp})
    
    df = pd.DataFrame(    data_list4)
    df = df[['date','open','high','low','close','vol','ma5','ma10','ma20','macd','label']]
#    
#    df.set_index("date" , inplace=True)
#    
#    df.to_csv("./sss.csv", index=True)
    df = df.dropna() #剔除缺失值

    df['ts'] =pd.to_datetime(df['date'])

    
    df = df.drop('date', axis=1)
#    df = df.set_index(['ts'])
    df.to_csv("./sss.csv", index=True)
#
    train_data = df[df['ts']<"2017-01-04"]
    
    test_data = df[df['ts']>="2017-01-04"]
    train_X = train_data.ix[:,'open':"ma20"].values
    train_y = train_data['label'].values
    test_X = test_data.ix[:,'open':"ma20"].values
    test_y = test_data['label'].values
    clf = RandomForestClassifier(max_depth=10,n_estimators=100  )
    clf.fit(train_X,train_y)
    print(accuracy_score(train_y,clf.predict(train_X)))
    print(accuracy_score(test_y,clf.predict(test_X)))
    importance = clf.feature_importances_
    indices = np.argsort(importance)[::-1]
    feat_labels = df.columns[1:]

#    features = train_X.columns
    test =[]
    for f in range(train_X.shape[1]):
        test.append([feat_labels[indices[f]],   importance[indices[f]]])
#    data_list4=str(accuracy_score(train_y,clf.predict(train_X)))+"next :"+str(accuracy_score(test_y,clf.predict(test_X)))
    data_list4=test
```
