---
title: "Python Run一下神經網路(Lstm)"
date: "2018-07-16T16:55:00.001+08:00"
updated: "2019-09-13T08:53:13.328+08:00"
permalink: "/2018/07/python-runlstm.html"
original_url: "https://x8795278.blogspot.com/2018/07/python-runlstm.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3457063518963581927"
tags: ["Python", "Stock", "Tutorial"]
layout: post
---

## 之前說的神經網路可行性??

## ---

run300輪
[![](https://i.imgur.com/p5zzeom.png)](https://i.imgur.com/p5zzeom.png)
  

來run一下別人大神級的code，裡面大神已經都出不介紹lstm大概是什麼了，小白只能runrun別人寫好的code  

好code不run嗎?，這樣看下來好像只是根據原始的資料，後幾天才放馬後炮，我們當然要預測當天的阿，真的能預測當然就是神明了，之前有看過大神run出來的57%準度也是蠻狂的
[深度学习做股票预测靠谱吗？](https://www.zhihu.com/question/54542998)
之前也說過，我們不要來做它們那種，我們做部分的行為預測，那些要比數據量，專業度一般的人也拿不到那麼多的資料，我們來做小範圍的行為預知就好(做不出來)  

```html
<script src="https://gist.github.com/x213212/4ad5f76a55728ad34085f4754963b3d5.js"></script>
```

  

後來再來看一下，是不是訓練次數不夠?我們來加到1000輪
[![](https://i.imgur.com/SHgyKWn.png)](https://i.imgur.com/SHgyKWn.png)
[![](https://i.imgur.com/MUbXcZX.png)](https://i.imgur.com/MUbXcZX.png)
## 構思

## ---

會不會要針對某個特別情況進行訓練呢，在我們進行上一次的初步構想的篩選股票的咚咚
[![](https://i.imgur.com/tl9R9KD.png)](https://i.imgur.com/tl9R9KD.png)
[![](https://i.imgur.com/nX3aoug.png)](https://i.imgur.com/nX3aoug.png)
設定參數尋找BBand寬度特別寬的海選，接下來我們只要針對特殊買賣點做lstm做訓練，來修正買賣點以來提升初入金額?
[![](https://i.imgur.com/LY2wqTV.png)](https://i.imgur.com/LY2wqTV.png)
忘記加scorllbar
這些大概就是篩選下來的股票我們來印證一下
寬度確實在20以上
[![](https://i.imgur.com/rrKLLxm.png)](https://i.imgur.com/rrKLLxm.png)
[![](https://i.imgur.com/2GXeIto.png)](https://i.imgur.com/2GXeIto.png)
要規避情況
[![](https://i.imgur.com/moGD0sX.png)](https://i.imgur.com/moGD0sX.png)
初步我想進行，一檔股票裡所有波動度寬度>=20%在excel
應該是尋找特徵點，我像做的也就是最後面再加入規避正確後的一欄??
話說規避正確後幹嘛再用lstm??增加準度嗎還是??脫褲子放屁?，外行人只能試看看，找code run修修改改，與黃金交叉有什麼關聯，或者是kd??，正規好像不是這樣搞，異常弔詭
不斷的修正買賣點用來提升獲利最大化??亂講別噴

1. 海撈BBand寬度大於20
2. 再用excel在計算新的參考數值
3. 制定tensorflow模型(異常困難)
4. 訓練

精準的修正買賣點好了，每天海選20檔固定買賣，重要的是有本啦，以量制勝不過沒關西  

xq可以有模擬帳戶，這如果成功我們再來tick資料來串  

[![](https://i.imgur.com/9Ol2ku3.png)](https://i.imgur.com/9Ol2ku3.png)
ㄎㄎ沒辦法，一整個很動態xd，沒辦法透過記憶體方式取得tick否則，可以用這個軟體，幫我們分擔基礎的網路負擔，還是透過封包?當然會加密阿xd，證券台灣的開通要  

[![](https://i.imgur.com/Tj0fRbb.png)](https://i.imgur.com/Tj0fRbb.png)
貴送送，最後想到來爬蟲一下發現某c股市交易模擬交易網站可以拿得每秒tick，不是每分鐘喔喔喔喔到時再來做小爬蟲和即時技術分析吧!新名詞蝶式套利波動度交易??好像是很多人吃飯工具?
## 參考

## ---

## [基于keras 的lstm 股票收盘价预测](https://blog.csdn.net/luoganttcc/article/details/79046870)
