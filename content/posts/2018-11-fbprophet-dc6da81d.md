---
title: "fbprophet 預測家模型 股票?"
date: "2018-11-18T00:47:00.002+08:00"
updated: "2018-12-01T00:10:31.060+08:00"
permalink: "/2018/11/fbprophet.html"
original_url: "https://x8795278.blogspot.com/2018/11/fbprophet.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8533149140038268394"
tags: ["Python", "Stock", "Tutorial"]
layout: post
---

[![](https://i.imgur.com/mUUDMeD.png)](https://i.imgur.com/mUUDMeD.png)
#### [超簡單用Python預測股價](https://www.finlab.tw/%E8%B6%85%E7%B0%A1%E5%96%AE-Machine-Learning-%E9%A0%90%E6%B8%AC%E8%82%A1%E5%83%B9/)

如圖，我也不知道我在寫什麼東西，就吸收整合，大不分的內容還是由比較正規的文章所引用，也有附上連結，有錯別來找我诶，我想入門的小白在搭建環境上會很雷，所以我通常會附上搭建環境的過程，以便大家可以快速run起來~
## 預測股票?

## ---

##

之前有寫過用lstm預測股票的東西，當然股票這種東西，不是長就是跌，大牛最多也是逼近50%50%不是漲就是碟嗎。不過放到中長期就不一樣了，如果再加入google tend關鍵字分析再來預測股票是否有其關聯性呢???，恩以後再來說先來做這實作先~  

  

剛好聽同學說它們有參加一個比賽，然後呢，它們的主要工作是需要預測下一個禮拜股市的精準度，就我這旁門走道來看，lstm或者用這預言家模型，應該都可以達到不錯的效果，  

假設我們要預測一個麗拜的資料需要大概那些能用的工具呢，第一步我們要把我們的資料禿通通時間序列化，再來就是套國外solution(公司大牛)說的，哈哈在接下來我們來看看之前兩個月沒動的程式碼吧。  

首先呢我們打開我們的老程式碼跑一下範例。  
## 速度迷思

## ---

##

##

我覺得痾應該速度再跑回測的時候有差拉，不過在觀察其規律性，要求速度的話在急速下單邏輯判斷一定要超快，像我之前寫的一個比特幣交易軟體，取得買賣單量瞬間下單，最後還是被官網鎖了，只能說莊家最大，然後喔一定會找到適合你的組合最重要，程式跑回測，不一定是找到聖杯，除非你的策略寫的超棒，無破綻，去跑當沖，每秒幾十萬上下，[2018二月全球股災～黑天鵝是機器人？](https://www.youtube.com/watch?v=FlY7Ms53wyI) 遇到一次就gg囉，不過有人贏就有人輸，我是年輕人還是先在旁邊觀察一陣子好了。  

![ãé£éç ´å£ãçåçæå°çµæ](https://storage.cosmoxmusic.com/product/5cafeeee-1f37-4963-8aaa-6337d5aec39a)

  
## 搭建環境與安裝

##

## ---

```
# bash $ pip install fbprophet
```

慘慘慘 轉用anaconda裝[![](https://i.imgur.com/1SuA6x2.png)](https://i.imgur.com/1SuA6x2.png)
```
conda update -c conda-forge conda conda update -n base conda conda config --add pinned_packages defaults::conda conda install  -c conda-forge fbprophet -y conda install -c masdeseiscaracteres ta-lib
```

[![](https://i.imgur.com/VXn9REc.png)](https://i.imgur.com/VXn9REc.png)
  
## 複製stocker

## ---

##

##

不想下一堆指令的話，可以偷懶學我把關聯py丟到目錄下  

[![](https://i.imgur.com/zEIfVeZ.png)](https://i.imgur.com/zEIfVeZ.png)
  

  

[![](https://i.imgur.com/tEpWLp2.png)](https://i.imgur.com/tEpWLp2.png)
  

nice解決環境好利器，搜尋了快一小時還以為當機，惱人的環境設定，中途還跑去裝docker，結果windows hyper 要專業版才有QQ 我畚箕安裝的python 資源包，一堆元件衝突總而言之，安裝好後呢(anaconda裝了很多次結果降版本Anaconda3-5.2.0-Windows-x86_64.exe 這就大概裝完囉。  
## 程式碼

## ---

##

##

小改  

```python
import pandas as pd

# 去除煩人的 warrning
import warnings
from stocker import Stocker

warnings.filterwarnings('ignore')

# 讀入series
df = pd.read_csv('price.csv', index_col='date', parse_dates=['date'])
price = df.squeeze()
price.head()
tsmc = Stocker(price)
tsmc.evaluate_prediction()
tsmc.changepoint_prior_analysis(changepoint_priors=[0.001, 0.05, 0.1, 0.2])
tsmc.predict_future(days=100)
```

  
## 運行畫面

##

[![](https://i.imgur.com/6QL9YCJ.png)](https://i.imgur.com/6QL9YCJ.png)
其實，用來預測一些事情也蠻好玩的。
  

  

[國外Stocker文章](https://towardsdatascience.com/stock-prediction-in-python-b66555171a2)
[國外github](https://github.com/WillKoehrsen/Data-Analysis/tree/master/stocker)  

[預言家github](https://github.com/facebook/prophet)  

  

  

## 幻想

## ---

##

目前大概再搭建玩平台後，現在目前都是寫小策略，那麼嘗試投資組合使用基因演算法(?)，  

簡單成效好、不簡單成效好、簡單成效不好、不簡單成效不好。(取自[量化實驗室](https://www.finlab.tw/)片段)  

就上述這幾種情況，大家應該都會偏向於第一種方法因為就算是失敗的話，也很好找出原因並且除錯，大概再跑兩個範例，google tend對金融性產品 是否也有其關聯，在來就是一些小策略的紀錄。  

沒意外後其大概都是  

  

1. 提出組合
2. 回測
3. 修正

  

回測 - > 修正 - > 回測 - > 修正 - > 回測 - > 修正 - > 回測 - > 修正 .......  

  

public int debug()
{
if(debug == 1)
debug(1);
return debug(1);
}目前活在這種地獄，重構，非同步，deubg無限循環，體驗新手村的感覺，什麼時候可以用嘴巴寫程式。。。。。。。
##
