---
title: "打造一個多人串流系統 Android 推流 至 rtmp server part6"
date: "2019-02-06T18:36:00.004+08:00"
updated: "2019-06-22T20:02:33.999+08:00"
permalink: "/2019/02/android-rtmp-server-end.html"
original_url: "https://x8795278.blogspot.com/2019/02/android-rtmp-server-end.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6546372986931355296"
tags: ["adobe media server", "Android", "livego", "Tutorial"]
layout: post
---

遠距醫療串抖音cc，在跟病人通話的時候可以加點特效(誤，病人玩起來了，顧及到健康長照?)
公司功能越加越多了，在搭建完flex html5 android ...，編碼速度瓶頸可能要從軟體編碼變到硬體編碼，過一陣子再來研究ffmpeg硬體加速，感覺弄完都可以自己架一個直播串流平台了。
過完年...公司變港商了666，取之github還之github
<https://github.com/x213212/rtmp_player_publish>
[![](https://i.imgur.com/w1CjaRF.png)](https://i.imgur.com/w1CjaRF.png)
  

 [![](https://i.imgur.com/5dnvBjZ.png)](https://i.imgur.com/5dnvBjZ.png)
[![](https://i.imgur.com/WahFcc2.png)](https://i.imgur.com/WahFcc2.png)
解析度調整
[![](https://i.imgur.com/Y1nYq2A.png)](https://i.imgur.com/Y1nYq2A.png)
  

ffmpeg to any media format bug
## ---

在Android 使用的是硬體編碼，在版本過低的或是手持裝置cpu速度不同下將會發生硬體編碼速度跟不上camera fps所以會導致產生media 時間戳發生不對導致
無法產生flv或者其他格式所以，除了在andorid 會發生這狀況，在上一章http5 to rtmp推流圖片至伺服器過程，也有可能會發生這狀況，有聲音沒畫面等等  

可以透過ffmpeg 再把進行轉推流，也算把格式再進行一次補齊，至於速度問題可能要好好研究一下用nvdia 進行硬體加速。  

[![](https://i.imgur.com/fDubQxg.png)](https://i.imgur.com/fDubQxg.png)
  

address1 adobe_media_server
address2 livego
 ffmpeg -re -i rtmp:// address1 -r 60 -vcodec libx264 -s 640x480 -preset ultrafast -tune zerolatency -filter_complex aresample=44100 -bufsize 1000 -c:a aac -b🅰️0 128k -f flv rtmp:// address2
