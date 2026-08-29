---
title: "how to enable/disable debug information"
date: "2021-01-14T15:48:00.001+08:00"
updated: "2021-01-14T15:48:27.342+08:00"
permalink: "/2021/01/how-to-enabledisable-debug-information.html"
original_url: "https://x8795278.blogspot.com/2021/01/how-to-enabledisable-debug-information.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2748104381497828452"
tags: ["ida", "server"]
layout: post
---

![](https://i.imgur.com/GpceAsd.jpg")

# debug 資訊嘗試了一下
順便開啟我們反編譯工具，以後打算來debug ggc 比較好用，來拿昨天的 ghost client 端來開刀，主要目標是
自己開issues 自己解xd
https://github.com/york8817612/Ghost/issues/23
![](https://i.imgur.com/VVN1V6K.png)
把debug 關掉
效果
![](https://i.imgur.com/GpceAsd.jpg)
來回憶一下

shift+ f12
後
![](https://i.imgur.com/926cgGP.png)
setup打勾 unicode 後可以對遊戲裡面的 text 做搜尋

![](https://i.imgur.com/S3HjJe8.png)
點擊兩下可以跳到程式碼
ida view 再來可以透過undefine 展開字串
![](https://i.imgur.com/kOEEoek.png)
hex view 畫面
![](https://i.imgur.com/jLEbOFO.png)
如何修改某行的 code 可以透過 Patched 去看已經更改後的code 位置
![](https://i.imgur.com/0OktPsl.png)
也可以對已經修改過的 code 輸出新的exe
![](https://i.imgur.com/8drIK4u.png)
那麼熟悉後來進入正題
剛剛有去抓到word字串片段後就比較好辦了

![](https://i.imgur.com/XP8OV0w.png)
按照剛剛的技巧可以透過 data xref 跳到程式碼位置
到這邊後
![](https://i.imgur.com/viFHBkI.png)
透過展開流程
![](https://i.imgur.com/Y8dSNPR.png)
![](https://i.imgur.com/sNNKRiY.png)
![](https://i.imgur.com/FAI86qU.png)
原本這裡會跳到 debug 的地方
![](https://i.imgur.com/T1OM4Ad.png)
我們把他jmp跳過 debug 的地方
這樣我們就 關掉了xd
除了可以手動下註解，我覺得可以透過Patched 去檢查以前改過的地方非常的方便!
![](https://i.imgur.com/xYTovgY.jpg)
前面關掉的地方可能，跟遊戲一開始加載衣服的地方東西有點bug((?))
![](https://i.imgur.com/qlVnhb8.jpg)
實際上運行結果~該分析 gcc 了 該用 source debug 來看一些重要的東西!

