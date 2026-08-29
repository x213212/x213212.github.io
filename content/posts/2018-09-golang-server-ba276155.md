---
title: "Golang 搭建一個簡單Http Server"
date: "2018-09-26T22:49:00.002+08:00"
updated: "2018-09-30T04:47:33.391+08:00"
permalink: "/2018/09/golang-server.html"
original_url: "https://x8795278.blogspot.com/2018/09/golang-server.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-7469045311439688862"
tags: ["Go", "Tutorial"]
layout: post
---

上一次我們講到安裝Golang那麼今天我們來看如何架設一個跟網頁溝通的伺服器  
## Setting

## ---

## ``` go get -u github.com/gorilla/mux ```

## 安裝套件的過程它不會講話xd，套一句老師說的沒消息就是好消息  [![](https://i.imgur.com/lQ0H32U.png)](https://i.imgur.com/lQ0H32U.png)

## 放置檔案路徑，沒什麼難度，放到資料夾而已。

## [![](https://i.imgur.com/NRdoHCu.png)](https://i.imgur.com/NRdoHCu.png) 上述相關文件安裝完後，沒想到的是，只要設定好route，仔細看整組搬過來就可以了這是比較正規的作法，當然網路上也有其他更暴力的方法(牛逼稍微進行一下小改裝 [Go语言实现简单的一个静态WEB服务器](https://studygolang.com/articles/5116) [![](https://i.imgur.com/KfgAa6v.png)](https://i.imgur.com/KfgAa6v.png)

[![](https://i.imgur.com/C6MyOk8.png)](https://i.imgur.com/C6MyOk8.png)
##

##

##

##

##

```html
<script src="https://gist.github.com/x213212/d974750fc6f8c614c888f6954d57d4bd.js"></script>
```

  
## 後續

## ---

## 整組搬來用是不錯啦，這樣的話我們做處理的時候可以在golange做處理了 之前在python寫的交易系統，在前段時間呢看到了一個 影片 [遺傳演算法最佳化高頻交易策略](https://youtu.be/r-FBtE5pOtQ) 沒錯很喜歡模擬的我們呢已經搭建好這框架了 至於資料庫呢，既然都是用新技術在做事了，學習一下用[redis](https://redis.io/)當作資料庫 讓我們速度起飛!

##
