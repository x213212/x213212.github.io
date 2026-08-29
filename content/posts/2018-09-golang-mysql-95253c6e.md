---
title: "Golang 數據處理與 Mysql 基礎語法"
date: "2018-09-29T05:29:00.002+08:00"
updated: "2018-09-30T04:47:33.272+08:00"
permalink: "/2018/09/golang-mysql.html"
original_url: "https://x8795278.blogspot.com/2018/09/golang-mysql.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-718578078047606833"
tags: ["Go", "Stock", "Tutorial"]
layout: post
---

打造股票回測/盯盤網頁  
## 目標

## ---

## 昨天有說到要打造一個用redis資料庫，後來想一想這是用在有快取場合的方面，那麼 我們能做到什麼呢，我打算用golang mongodb jquery來實現我們的框架初步回測的框架 那麼我們可能需要完成下列清單不過我們先用mysql搭起來熟悉一下環境吧~ 整個流程跑完苦 - 數據的導入 - 架設伺服器回傳json - 畫折線圖 - 新增回測按鈕與篩選條件 - 打造一個盯盤軟體

## 數據的處理

## ---

##

### 看著我你CSV你才能動->>>>[CSV檔案下載](https://gist.github.com/x213212/98d9a7d371caa114ac2a011393313e80)

就是說這一次的話沒想過要弄爬蟲，相信大家可以在很多地方找到股票的歷史資料，  

我們今天就對數據做一個處理吧首先我們先來直上代碼  

這邊代碼我們把檔案讀進去了接下來看要怎樣對上傳CSV檔案到SQL資料庫吧  

```html
<script src="https://gist.github.com/x213212/df30e37e13493728b6bdbc7e0ba3262b.js"></script>
```

  
## Mysql 的 常用函數

## ---

```html
<script src="https://gist.github.com/x213212/c2f74b41dab01fe75d5b4dfc6c159b14.js"></script>
```

  
##

我大致上把它整理一下  
## 讀csv檔與上傳到數據庫

## ---

##

每一檔股票都它其編號，所以呢我們可以create一個table名稱對應股票的代號這邊先做個簡易版  

先來讀一下檔  

[![](https://i.imgur.com/C2bxSJd.png)](https://i.imgur.com/C2bxSJd.png)
  

```html
<script src="https://gist.github.com/x213212/9769a08aa2adae06d7f24c9e1ecd4754.js"></script>
```

綜合下
  

[![](https://i.imgur.com/ONFPRF5.png)](https://i.imgur.com/ONFPRF5.png)
[![](https://i.imgur.com/lNnwyYL.png)](https://i.imgur.com/lNnwyYL.png)
在資料的insert速度超快跟python比差一大截
