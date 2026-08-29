---
title: "Android google map 路徑規劃與估計到達時間(二完)"
date: "2018-03-07T17:45:00.000+08:00"
updated: "2018-09-05T07:46:03.448+08:00"
permalink: "/2018/03/android-google-map.html"
original_url: "https://x8795278.blogspot.com/2018/03/android-google-map.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2620049020918653440"
tags: ["Android", "Tutorial"]
layout: post
---

## 7:48AM

---

早上起來，昨天的MAP搜尋不動了，在一陣的搜尋下發現Android 的google map api key 的問題不開放給andorid ,因為程式碼是透過json所以算是一種web的應用程式呼叫，不過不用怕  
  
[![](https://i.imgur.com/OKuiGM3.png)](https://i.imgur.com/OKuiGM3.png)  
可以發現我試了很多種方法，包括自己的dns，ip等等，試到後面去申請了一個free php網站，然後接下來我透過ping把服務器的ip的網站給掛入，然後再更改。  
[![](https://i.imgur.com/ipHo3hj.png)](https://i.imgur.com/ipHo3hj.png)  
這樣的話，以前的code就都能動了。
## Google搜尋範圍內的指定目標

---

<https://developers.google.com/places/web-service/search?hl=zh-tw>  
[![](https://i.imgur.com/EpfIAs3.png)](https://i.imgur.com/EpfIAs3.png)  
慢慢是下來的結果是第三個  
[![](https://i.imgur.com/YcibK6U.png)](https://i.imgur.com/YcibK6U.png)  
  
標住起來的經緯度我填的是台灣然後範圍是500，關鍵字是胖老x,我們可以得到一串的json，後續我們只需要對json做解析就可以了。  
  
  
https://maps.googleapis.com/maps/api/place/textsearch/json?query=%E8%83%96%E8%80%81%E7%88%B9+main+street  
&location=23.5827883,118.7723606&radius=10000&key=AIzaSyB9TW…diQvE  
## 預約系統創建與架構

---

有了前面幾個的功能，我們已經可以把客人導入到最近的店裡了，然後我們接下來要做預約系統。

- free 伺服器 [byethost15.com](http://byethost15.com/) 裡面有php和mysql。
- 透過post資料對伺服器的mysql去下達指令。
- post到伺服器後回傳json，到我們的程式讀取。
- 這邊的實作方面先等簽約後再看看。

## 登入系統

---

- 透過post資料對伺服器的mysql去下達指令。
- 新增一筆資料到資料庫

## 註冊系統

---

- google+一鍵登入

預計使用google+來進行初步得帳號登入省去一些麻煩登入帳號後，沒用過或許會有一組key?  
那我們就可以用key去結合銀行卡號去做整合，這樣作為一組帳號做登入。  
有了前面幾個的功能，我們已經可以把客人導入到最近的店裡了，然後我們接下來要做預約系統。  
## 銀行api串接

---

- 銀行api

在這方面公司說會提供所以呢，假設選完所有療程後，將會有一筆總價  
這總價呢，假設預約成功或扣款成功的話呢，或許還會有一個消費紀錄，  
或許還會有紅利紀錄，等等系統的產生。  
## 結論

---

以上這大概就是一組，預約系統的app大概，ㄎㄎ或許吧  
主要是想去看業界 詳細的流程，聽說我跟到的是開發經驗有10年的怪物老師  
我已經有一堆問題要來問業界牛牛了。
