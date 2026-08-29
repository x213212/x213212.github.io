---
title: "google tends 反指標可行性? FIX_DATA (二)"
date: "2018-11-29T22:16:00.002+08:00"
updated: "2018-12-01T00:10:11.195+08:00"
permalink: "/2018/11/google-tends-fixdata.html"
original_url: "https://x8795278.blogspot.com/2018/11/google-tends-fixdata.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-589305655362364495"
tags: ["Python", "Stock", "Tutorial"]
layout: post
---

## 資料量可能會呈現全部趨向於100%的狀況

## ---

##

所以我打算先取得該年度區間所有的百分比再去*上每日百分比，這樣數據的呈現應該才是最準確的數字。  

先取得2004至今的趨勢  

## 程式碼

## ---

##

```html
<script src="https://gist.github.com/x213212/7eca5c5d0afc28da584baa449fbdf496.js"></script>
```

運行結果  

[![](https://i.imgur.com/0ETbBc8.png)](https://i.imgur.com/0ETbBc8.png)  

  

  
## 資料量問題

## ---

##

一開始我還以為要對資料做正規化，思考一下應該不是這問題，這邊會面臨到一直要數據被伺服器阻擋的問題(我先備份了數據)  

  

[![](https://i.imgur.com/alJwQAL.png)](https://i.imgur.com/alJwQAL.png)
這是取得每月得數據
  

[![](https://i.imgur.com/nP9A8Uj.png)](https://i.imgur.com/nP9A8Uj.png)
這是我們之前取得每日的數據
  

然後我們要對數據加工一下
[![](https://i.imgur.com/aGA0Z12.png)](https://i.imgur.com/aGA0Z12.png)
這才是正確的等比例數據
來看一下程式碼
  
## 程式碼

[下載我我是資料~data.csv](https://gist.github.com/x213212/bcbc087578f32725d6fd0334b15c8850)  

## ---

##

```html
<script src="https://gist.github.com/x213212/fb300453bd6e184803a5d2a99c1e192b.js"></script>
```
