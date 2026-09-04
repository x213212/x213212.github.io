---
title: "Mini-BitTorrent"
date: "2022-08-19T15:08:00.003+08:00"
updated: "2022-08-30T14:06:00.531+08:00"
permalink: "/2022/08/mini-bittorrent.html"
original_url: "https://x8795278.blogspot.com/2022/08/mini-bittorrent.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8920318555377626487"
tags: ["Mini BitTorrent"]
layout: post
---

![](https://i.imgur.com/yYl4O6m.png)

# mini-BitTorrent
https://github.com/darshank15/Mini-BitTorrent
fork一個有趣的專案
https://github.com/x213212/Mini-BitTorrent
新增了檔案切割和重組，遇到來源中斷也可以切換source,新增進度條，基本上如果tracker做成搜尋的樣子(不難，實現一個foxy 也是蠻好玩
![](https://i.imgur.com/45v8LpY.png)

![](https://i.imgur.com/LSskvcS.png)
整體流程就是跟一般bt差不多，client 上傳檔案分享，tracker 的seederlist 會記錄各個client傳送過來的種子檔(紀錄client要分享的檔案位置和port),當有另外一個client想下載檔案，client就會詢問tracker 然後 tracker再把seederlist可用的cleint在傳給使用者。
目前改動傳輸的檔案不再是單一檔案，類似可以中斷下載，這樣後續如果各個分割檔案都分享出去，那麼就不再侷限只能分享一個檔案，可以分享一個檔案的chunk ,這樣檔案來源應該不容易死。
![](https://i.imgur.com/7Ci53cM.png)
所以download我寫成分割檔
也寫了一個merge
![](https://i.imgur.com/OzSqvWO.png)
原本download沒有進度顯示我也加了進度條和merge binary 總byte 的部分，和下載速率.
![](https://i.imgur.com/JPRhPKj.png)

實測確實binary合併後可以正確執行.
新增了檔案校驗的md5檢查，本來想選crc32的，後來發現作者本來就有引用openssl的lib

![](https://i.imgur.com/6rlqiO0.png)

切換來源如何準確找出我想要的resource.
有新增了md5我們就可以從tracker的來源中挑出md5有符合的source
新增了自動換source
![](https://i.imgur.com/NPFDA6l.png)

