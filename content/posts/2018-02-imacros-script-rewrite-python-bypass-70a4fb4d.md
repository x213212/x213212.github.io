---
title: "Imacros Script rewrite Python bypass recaptcha v2比特幣水龍頭? 待續.."
date: "2018-02-07T18:25:00.000+08:00"
updated: "2018-12-07T01:06:49.631+08:00"
permalink: "/2018/02/imacros-script-rewrite-python-bypass.html"
original_url: "https://x8795278.blogspot.com/2018/02/imacros-script-rewrite-python-bypass.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5736676447425306633"
tags: ["bcoin", "Tutorial"]
layout: post
---

## 幹嘛改python呢?

---

[![](https://i.imgur.com/owziM20.png)](https://i.imgur.com/owziM20.png)
  

我看到了[https://freebitco.in](https://freebitco.in/) 發現了..這個每一小時簽到就有0.00000019btc 這是一隻帳號這樣的話那一天就有  

(0.00000019btc*24) = 0.00000456btc 三十天呢就有 0.0001368 趨近於42塊台幣  

  

[![](https://i.imgur.com/Mj6jIiN.png)](https://i.imgur.com/Mj6jIiN.png)  

  

  

  

大家可以看到 要出場需要付出0.00000187btc 而要滿足0.0003btc才可以出去則 假如這帳號滿三個月則可得 0.0001368 *3 =0.0004104 = 127塊 台幣 則我用機器人連續創一千隻的話 則一次獲利127000 那如果一萬隻? 將會達到1270000那我三個月可以賺120萬  

  
##

## Imacros

---

這是一個掛在網頁上的外掛程式可以以腳本方式去完成網頁相關動作  

然而為什麼有imacros腳本版要改pyhton呢  
## Google recaptcha v2

---

[![](https://i.imgur.com/n1CDYvS.png)](https://i.imgur.com/n1CDYvS.png)  

當然有夢最美應該早點看到這網站的，最近網站增加了google recaptcha v2  

而這什麼當然就是一種驗證機制，經過了一個下午的搜尋呢發現  

其實是有辦法可以bypass，具體方法呢就是用Imacros，但是最後發現呢  

網路上流通的都是只有腳本版，當然現在就是改造時間拉  

  

  

  
## 9KW?

---

[![](https://i.imgur.com/7LhXJmC.png)](https://i.imgur.com/7LhXJmC.png)  

  

這網站是幹嘛的呢，簡單來說就是以人工方式進行驗證碼輸入(xd  

  

  

這網站開出一個api可以讓使用者使用不用輸入驗證碼，  

當然也可以自己輸入驗證碼逆向賺取積分的方式.  

  

<http://2captcha.com/>  

也是一種網站，可以輸入驗證碼賺取比特幣  

  

  
## 分析base_macro_Av2.iim

---

[![](https://i.imgur.com/3durToa.png)](https://i.imgur.com/3durToa.png)
  

在網路看到了這腳本(下面有載點)，然後拆開來看發現腳本內導向了  

  

[![](https://i.imgur.com/GAkA7aH.png)](https://i.imgur.com/GAkA7aH.png)  

  

<http://www.9kw.eu/grafik/form_base64.html>  

上面這表單最下面ok左邊那列需填寫site-key則是  

  

  

[![](https://i.imgur.com/TvvU4T6.png)](https://i.imgur.com/TvvU4T6.png)  

  

6Lc6zQQTAAAAAD8TgxgC59CXtm1G56QLu8G7Q53K <----  

  

  

照腳本將所需的api_key和site_key填上，Interactive 記得勾上  

按下ok發送則會得到一串數字，額這邊就暫且理解成訂單編號吧  

  

  

[![](https://i.imgur.com/Nu80Axo.png)](https://i.imgur.com/Nu80Axo.png)  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

https://www.9kw.eu/index.cgi?source=imacros&action=usercaptchacorrectback&apikey={{GKQYSKY3BIO4PPZT7Y}}&correct={{2}}&id={{100970736}}  

這邊可以查詢當前訂單狀態  

而可以看到程式目前就是到這邊，而接下來要到看不到的畫面了  

## Python深入解析

---

[![](https://i.imgur.com/0INAtzs.png)](https://i.imgur.com/0INAtzs.png)
[大家可以找到post代表表單把資料傳到下個頁面，不錯莫名其妙要來做機器人了](https://i.imgur.com/0INAtzs.png)
  

[![](https://i.imgur.com/0UzVE7U.png)](https://i.imgur.com/0UzVE7U.png)
  

  

  

  

  

  

  

  

  

  

  

看到畫面了今天就先到這...一堆套件裝不起來  

![](https://i.imgur.com/UxKiQTT.png)

  

## 未完待續...

---

先來貼一下獲利圖  

[![](https://i.imgur.com/CfgtMi7.png)](https://i.imgur.com/CfgtMi7.png)  

  

  

  

  

95顆比特幣~洗到兩千多萬台幣當然是騙你的  

怎麼可能看這些驗證碼的工人  

40000/(高級解碼30普通解碼10)可以點1333次 5歐元=180元台幣  

那麼代表我點一次0.13台幣  

假設我有一萬帳號我要點一天24小時代表我要花掉31200  

那我一個月要花掉九百多萬ㄏㄏ，辦帳號扣除2次google驗證碼在噴0.75次 5歐元  

，三個月後還有賺九十萬诶(白癡後來算錯倒賠810萬，看到這篇文章我們可以討論一下真正的比特幣水龍頭  

這只是概念啦1/18中韓夾殺，如果遇到這種freebitcoin突然關了怎麼辦!!，嘿嘿想試看看也可以  

[![](https://i.imgur.com/kNrQBYw.png)](https://i.imgur.com/kNrQBYw.png)  

當然也是有積分那些連續賺得拉什麼推薦鍊什麼的，9kw網站也有提供解普通驗證碼  

假如喔，再搭配機器學習!!!接下來不多說下面流程圖運作起來會發生怎麼樣的事呢??  

[![](https://i.imgur.com/k7Wds7g.png)](https://i.imgur.com/k7Wds7g.png)  

整個系統搭起來的話應該很龐大  

開放合作模式，徵求野心強大的程式人(最近想搞東西
