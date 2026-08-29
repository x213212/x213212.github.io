---
title: "gcp loadblance setting & gcp armor"
date: "2021-09-18T14:43:00.006+08:00"
updated: "2023-11-04T12:12:05.860+08:00"
permalink: "/2021/09/gcp-loadblance-setting.html"
original_url: "https://x8795278.blogspot.com/2021/09/gcp-loadblance-setting.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3678132042105672112"
tags: ["GCP", "Load Balancing"]
layout: post
---

![](https://hackmd.io/_uploads/HJZcNrQma.png)

# gcp loadblance setting & gcp armor
前幾天開了一台linux 本來要做後台作品集的，結果第一天晚上因為想說應該沒人那麼無聊結果就有一個大陸人用tomcat弱密碼就被入侵了，它們透過tomcat 的 manager，上傳自己的war 包，去執行真他們的java 程式，被它們拿來挖礦，記得排查apache2 的log
![](https://i.imgur.com/DEvmxZx.png)
ip就不碼了
![](https://i.imgur.com/PVr464Q.png)
直接被放這隻
![](https://i.imgur.com/STbNE7H.png)
莫名被上傳一隻jsp_app
https://github.com/magicming200/tomcat-weak-password-scanner
後面因為我是專案檔案
![](https://i.imgur.com/KRqpQha.png)
也抓到了他也埋在我的vue專案，幸好剛部屬是沒有什麼機密資料可以偷

後來流量來源當然是從大陸來的，自己是有初估排查，但是其中還是被以嘗試挖礦嫌疑停止專案，另外專案內幾百g的流量官方要另外給我一個答覆，
![](https://i.imgur.com/0lYkKGp.png)
我只開了2g ram 2 vcpu 兩天流量到幾百g bytes
第一時間發現被埋後台是因為我本來就有設定預算
![](https://i.imgur.com/0DEKGQJ.png)
想說流量怎麼這麼大半夜被call 起來聯絡客服
當下要停止流量，要馬上關閉付款帳戶這個蠻重要的
![](https://i.imgur.com/2Hx0ViV.png)
還有另一個部分假設你的專案權限還可以登入進去的話
![](https://i.imgur.com/3K3M03G.png)
去api服務把所有api全部關閉，這樣再去關閉專案，
因為當下你的服務停止流量不會馬上停止計費，要小心阿，我以為關閉專案就沒事了，跟客服來信他們說當下停止帳戶大概預計48小時內妳的流量還是會繼續，可能要一段時間才會你的最終帳戶才會停止計算。
![](https://i.imgur.com/R0UwCQP.png)
後續溝通還會持續，主要那幾天都睡不著，因為你關閉專案還是會持續扣款，睡醒可能莫名其妙多兩千這還是有優惠的情況下，他沒打折的話可能就要破萬了。
![](https://i.imgur.com/EGBW4Vr.png)
審核也不太算快大概兩三天，它們大概會先封鎖付款帳戶，切記不要再去做開啟動作或刪除，
![](https://i.imgur.com/QXPCRmt.png)
另外一封信就蠻奇怪的了，可能我這幾天剛好遇到一個bug
![](https://i.imgur.com/4Ovzzt6.png)
![](https://i.imgur.com/ysm6p2g.png)

跟這一次的流量有問題。

下面我來示範一下，假設要過濾大陸流量
![](https://i.imgur.com/xE2dz3X.png)
設定端點群組，記得對應到你的防火牆輸出的端口
![](https://i.imgur.com/HWwiisI.png)
設定負載平衡
![](https://i.imgur.com/exjfOHK.png)
![](https://i.imgur.com/NeilZDc.png)
因為我的專案可以瀏覽http可以把它導向https，其他可能要依照個人使用環境來做調整
![](https://i.imgur.com/fLeePt9.png)
這邊安全性我來補這塊

![](https://i.imgur.com/3Fry4IN.png)
![](https://i.imgur.com/xBLP5d1.png)
選剛剛的網路端點群組
![](https://i.imgur.com/jslj3ti.png)
![](https://i.imgur.com/3iJebwo.png)

# google armor
https://blog.cloud-ace.tw/security/gcp-tutorial-how-to-set-google-cloud-armor-to-block-traffic-from-countries/

![](https://i.imgur.com/IKiF2Q4.png)

照那篇文章填入
```
 origin.region_code == 'TW'
```
就可以過濾到只剩台灣的流量
從捷克瀏覽我的網站
![](https://i.imgur.com/v9Jo6aj.png)

