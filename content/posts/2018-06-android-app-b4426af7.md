---
title: "Android 工具人app"
date: "2018-04-09T15:31:00.000+08:00"
updated: "2019-09-13T08:56:03.923+08:00"
permalink: "/2018/06/android-app.html"
original_url: "https://x8795278.blogspot.com/2018/06/android-app.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5222335496588391565"
tags: ["Android", "Tutorial", "Projects"]
layout: post
---

## 功能介紹

---

以前的課專，忘記上傳解說一波。
[![](https://i.imgur.com/V22mAMS.png)](https://i.imgur.com/V22mAMS.png)[![](https://i.imgur.com/OuFyxsd.png)](https://i.imgur.com/OuFyxsd.png)  

  

  

  

  

一個類似UBER的APP可以延伸運用  

但是不向UBER只侷限開車也很像神奇寶貝GO的抓寶地圖  

[![](https://i.imgur.com/K8Gqtcj.png)](https://i.imgur.com/K8Gqtcj.png)  

  

  

這APP打算用資料庫和GPS Or WIFI定位和GOOGLE MAP地圖  

功能的基本:就是可以任意在地圖上留下訊息，在下面欄位那邊可以搜尋之前的人所留留下的訊息點擊該marker可以觀看在該點下更多訊息，搜尋提供直觀的你的位置到對方位置在你搜尋時可以動態的觀看到線該線可以很清楚的看到你與留下訊息的人的距離  

## 功能

---

在地圖上點及任何一點，可以對該點設置你想說的話，將會插入一筆資料  

此筆資料可以有你的姓名和你想留下的資料，系統會產生時間戳記到這筆  

資料下方也有搜索欄位我們可以透過搜索欄位對所有留下資料的做搜尋，  

而點擊下方搜索欄位將會產生一條線和移動至該點，在搜尋欄位中做搜尋  

的話可以將繪畫多條線到目前你的位置，可以很直觀的看到位於你最近的  

人或服務在哪。  
## 如何呼叫mysql

---

Android 呼叫 網頁php 透過post將指令送出 到mysql，mysql 回傳資料json  

則我們將對這串資料做處理。  
## 重要功能

---

負責呼叫mysql 指令  

製作動態搜尋，並畫線  

為搜尋欄位新增監聽事件  

Init()  

searchitem(String textToSerch)  

點擊地圖上marker則會顯示該點會下所有的訊息(可以該點多筆資料  

點擊該點則會顯示該點座標位置。  

  
## query.php

---

```html
<script src="https://gist.github.com/x213212/ad15e1a2e10ee98228a449228e0d1b2c.js"></script>
```

  

  
## MapsActivity.java layout

---

[![](https://i.imgur.com/DwKGtmI.png)](https://i.imgur.com/DwKGtmI.png)  
## MainActivity.java layout

---

[![](https://i.imgur.com/kLLbvSt.png)](https://i.imgur.com/kLLbvSt.png)  
## 負責呼叫mysql 指令

---

```html
<script src="https://gist.github.com/x213212/642916bd1ce949ac0625daed43e015d5.js"></script>
```

  

  
## 製作動態搜尋，並畫線

---

如果點擊所有訊息則將會將會去跟mysql取的資料，然後將取得的資料丟到list <string> list裡面  

製作list搜尋欄位呢，我們要一個搜尋框，和所有資料，  

我們將會回傳資料存到list然後必須在搜尋框那邊新增一個監聽事件。  
## 回傳資料存到list

---

```html
<script src="https://gist.github.com/x213212/bc0411351da06cff73a2afd2361b8839.js"></script>
```

  

  
## 為搜尋欄位新增監聽事件

---

```html
<script src="https://gist.github.com/x213212/070287f7d17bb32676a1a4567546cfc3.js"></script>
```

  

  
## Init()

---

```html
<script src="https://gist.github.com/x213212/63d3b755155cbd7365cfb425e5dd07ed.js"></script>
```

  

  
## searchitem(String textToSerch)

---

```html
<script src="https://gist.github.com/x213212/ea9c553d7b837c18bb45f2082702470b.js"></script>
```

  

  
## 點擊地圖上marker則會顯示該點會下所有的訊息(可以該點多筆資料

---

```html
<script src="https://gist.github.com/x213212/d48cd23f3f07c2ffbb8cc1b48d2982f9.js"></script>
```

  

  
## 點擊該點則會顯示該點座標位置

---

```html
<script src="https://gist.github.com/x213212/56efba01cfb77b93c9e6cfd9c36bbcd9.js"></script>
```

  

  
##
