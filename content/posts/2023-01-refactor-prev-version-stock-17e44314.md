---
title: "refactor prev version stock"
date: "2023-01-31T06:06:00.003+08:00"
updated: "2023-01-31T06:06:18.318+08:00"
permalink: "/2023/01/refactor-prev-version-stock.html"
original_url: "https://x8795278.blogspot.com/2023/01/refactor-prev-version-stock.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-9086300062147269388"
tags: ["Stock"]
layout: post
---

![](https://i.imgur.com/CKCY8Pi.png)

# 無聊重構以前的回測軟體
之前的預言家模型每次anaconda更換環境都會出問題，在策略格式每個都不太一樣這次順便全部依國外網站的格式讓所有策略都兼容
https://github.com/WillKoehrsen/Data-Analysis/blob/master/stocker/Stocker%20Prediction%20Usage.ipynb
這邊不用以前的fbprob
[fbprob](https://facebook.github.io/prophet/docs/saturating_forecasts.html#forecasting-growth)
更換一下lib
```python
python -m pip install prophet
```
![](https://i.imgur.com/U6PE1Pq.png)
替換掉就ok了
![](https://i.imgur.com/1PJtYb7.png)
work!
![](https://i.imgur.com/MMzVShp.png)
![](https://i.imgur.com/HKpY3Tb.png)

把以前的策略統一到模組裡面
![](https://i.imgur.com/TNnwSaJ.png)
測試預測功能
![](https://i.imgur.com/CKCY8Pi.png)
慢慢增加一些常用指標，模組化
![](https://i.imgur.com/6Jg5Krq.png)
測試交易細節
![](https://i.imgur.com/QzZsaC2.png)

修復爬蟲
來爬國外的stock 網站資料,
![](https://i.imgur.com/Ga04XPd.png)
測試尋找五年內 波段 用talib 一些指標篩選
![](https://i.imgur.com/sZQ9xwJ.png)
![](https://i.imgur.com/mAL7aUI.png)
![](https://i.imgur.com/s2R7gTj.png)

