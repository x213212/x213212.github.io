---
title: "Python Facebook聊天機器人 Echo Ngork"
date: "2018-09-24T10:26:00.001+08:00"
updated: "2018-09-30T04:47:33.332+08:00"
permalink: "/2018/09/facebookbot-echo-ngork.html"
original_url: "https://x8795278.blogspot.com/2018/09/facebookbot-echo-ngork.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-7214808236683166096"
tags: ["chatbot", "ngrok", "Python", "Tutorial"]
layout: post
---

## 前置作業

## ---

聊天機器人  

想說[Linebot](https://x8795278.blogspot.com/2018/09/linebot-echo-ngork.html)弄完後順便連Facebookbot一併弄一下好了  

bot也算是兩年前的東西了，以前寫沒留下近期內用到再來寫一下作教學文  

不然每次的話都要再重找  

不過Facebookbot比較麻煩一點就是了  

那在我們上一回的[Linebot](https://x8795278.blogspot.com/2018/09/linebot-echo-ngork.html)都裝的差不多了，  

為什麼技術文章寫來寫去還是很像在寫心情雜記xd  

  
## 創立一個粉絲專頁

## ---

[![](https://i.imgur.com/ajXdKCf.jpg)](https://i.imgur.com/ajXdKCf.jpg)
  
##

##

## Facebook Developers Setting Messager

## ---

創完之後呢我們接下來要進去facebook developers 設定messager  

我們來到  

<https://developers.facebook.com/>  

[![](https://i.imgur.com/ujVhf7V.png)](https://i.imgur.com/ujVhf7V.png)
建立完成後呢  

[![](https://i.imgur.com/2mg0cuw.png)](https://i.imgur.com/2mg0cuw.png)
選擇我們自己設立的粉絲專頁  

[![](https://i.imgur.com/QW749rN.png)](https://i.imgur.com/QW749rN.png)
  

授權  

[![](https://i.imgur.com/0kAUAOr.png)](https://i.imgur.com/0kAUAOr.png)
  
## Facebook Developers  Application審查

## ---

## 隱私權政策網址 [Privacy Policy Generato](https://blog.ccjeng.com/2016/05/privacy-policy-generator.html)

填完資料後一定要按右上角開啟app
## [![](https://i.imgur.com/GqhJml1.png)](https://i.imgur.com/GqhJml1.png)

## [![](https://i.imgur.com/Mjor9f9.png)](https://i.imgur.com/Mjor9f9.png) [![](https://i.imgur.com/ZoiiMws.png)](https://i.imgur.com/ZoiiMws.png)

## Facebook Developers Setting Webhooks

## ---

[![](https://i.imgur.com/W09Fl4m.png)](https://i.imgur.com/W09Fl4m.png)
  

我們複製我們穿透厚的網址https!  

[![](https://i.imgur.com/4sVO3bG.png)](https://i.imgur.com/4sVO3bG.png)
驗證成功
[![](https://i.imgur.com/RsbqcDw.png)](https://i.imgur.com/RsbqcDw.png)
[![](https://i.imgur.com/IBHRjz7.png)](https://i.imgur.com/IBHRjz7.png)
記得把權杖再複製一次給webhooks
[![](https://i.imgur.com/FjI6U89.png)](https://i.imgur.com/FjI6U89.png)
  

  

  

  

安裝元件  

$ pip install pymessenger
[![](https://i.imgur.com/AHOInyK.png)](https://i.imgur.com/AHOInyK.png)
裝完後跑一下code
```html
<script src="https://gist.github.com/nikhilkumarsingh/8f6e109e4968820d37dd27d4afbf72b0.js"></script>
```

  

記得替換掉token  

端口與ngork端口需要一至  

[![](https://i.imgur.com/UEEwwss.png)](https://i.imgur.com/UEEwwss.png)
啟動伺服器
## 直接開密!

## ---

[![](https://i.imgur.com/0LB9ZLa.png)](https://i.imgur.com/0LB9ZLa.png)
  

[![](https://i.imgur.com/PPEEood.png)](https://i.imgur.com/PPEEood.png)
ngork伺服器響應時間有夠慢的，然後既然是免費的嗎算惹
  
## 如果在權杖有問題的話這邊可以把webhooks進行移除

## ---

[![](https://i.imgur.com/foPO9iF.png)](https://i.imgur.com/foPO9iF.png)
