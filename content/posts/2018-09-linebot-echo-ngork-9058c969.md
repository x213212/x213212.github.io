---
title: "Python Line聊天機器人 Echo Ngork"
date: "2018-09-23T11:19:00.002+08:00"
updated: "2018-09-30T04:47:33.093+08:00"
permalink: "/2018/09/linebot-echo-ngork.html"
original_url: "https://x8795278.blogspot.com/2018/09/linebot-echo-ngork.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5894179508089709293"
tags: ["chatbot", "ngrok", "Python", "Tutorial"]
layout: post
---

## 前置作業

## ---

[https://admin-official.line.me](https://admin-official.line.me/)  

<https://developers.line.me/console/channel>
上面會用到的兩個網址
<https://yaoandy107.github.io/line-bot-tutorial/>
照這位大大把推廣的帳號和line console後台做綁定
好了之後呢我們來看一下正題
我們先來下載
<https://ngrok.com/>
下載後呢
[![](https://i.imgur.com/ZVrDmWz.png)](https://i.imgur.com/ZVrDmWz.png)
```html
<script src="https://gist.github.com/x213212/b7eb0dc409e3ed63cc1822dd1e016a31.js"></script>
```

解壓縮完我們執行他  
## 執行NGORK

## ---

[![](https://i.imgur.com/RItXtGu.png)](https://i.imgur.com/RItXtGu.png)
## LINE Webhook設定

## ---

這是將本機端口連到外網  

大家比較有問題的是webhooks  

記得把上面設成enable url則跟ngork產生的臨時網址+自己的伺服器回應網址做結合  

得到  

<https://05bfab1a.ngrok.io/callback>  

[![](https://i.imgur.com/V6ScdPG.png)](https://i.imgur.com/V6ScdPG.png)
  

那接下來執行  

```html
<script src="https://gist.github.com/x213212/62cd2daa5a58c1aa9bbeb3e5d822a86b.js"></script>
```

  

我們掃描我們的linebot帳號並輸入一連串文字
[![](https://i.imgur.com/8C7183P.png)](https://i.imgur.com/8C7183P.png)
  

成功的話我們可以看到伺服器會回傳json
[![](https://i.imgur.com/GUuu4gz.png)](https://i.imgur.com/GUuu4gz.png)
嫌這個看不太清楚的話呢輸入這串網址我們可以進到
[![](https://i.imgur.com/jj1r2VC.png)](https://i.imgur.com/jj1r2VC.png)
[![](https://i.imgur.com/MsAxVk9.png)](https://i.imgur.com/MsAxVk9.png)
  

看比較詳細的Requests詳細資料
以前的話呢是對json做處理現在有api可以call了
  

[![](https://i.imgur.com/tjdnExG.png)](https://i.imgur.com/tjdnExG.png)
  
## 關閉自動回復訊息範本

## ---

感謝您傳送訊息給我！(blush)  

  

很抱歉，這個帳號沒有辦法對用戶個別回覆。(hm)  

  

敬請期待下次的訊息內容！(shiny)  

這個咚咚呢，我們可以把他切掉  

  

  

[![](https://i.imgur.com/bcmAKIR.png)](https://i.imgur.com/bcmAKIR.png)
[![](https://i.imgur.com/ISGRzMS.png)](https://i.imgur.com/ISGRzMS.png)
這邊可以看到我們的linebot已經完成了!
