---
title: "打造一個多人串流系統 adobe_media_server part2"
date: "2019-01-06T13:25:00.003+08:00"
updated: "2019-01-13T20:33:37.147+08:00"
permalink: "/2019/01/adobemediaserver-part2.html"
original_url: "https://x8795278.blogspot.com/2019/01/adobemediaserver-part2.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5573490937441947003"
tags: ["adobe media server", "live", "Tutorial"]
layout: post
---

## [![](https://www.arup.com/-/media/arup/images/expertise/industries/highways-header-m6_toll_birmingham_northern_relief_road_bnrr_david_griffiths_photography-2000x1125.jpg?h=1125&la=en&w=2000&hash=B2EA70C39B467E5BD987337BE4A14C83DC7241DF)](https://www.arup.com/-/media/arup/images/expertise/industries/highways-header-m6_toll_birmingham_northern_relief_road_bnrr_david_griffiths_photography-2000x1125.jpg?h=1125&la=en&w=2000&hash=B2EA70C39B467E5BD987337BE4A14C83DC7241DF) [![](https://img.scoop.it/ieCvyfSfE7uPlEujeypLuTl72eJkfbmt4t8yenImKBVvK0kTmF0xjctABnaLJIm9)](https://img.scoop.it/ieCvyfSfE7uPlEujeypLuTl72eJkfbmt4t8yenImKBVvK0kTmF0xjctABnaLJIm9)

## RTMFP VS RTMP

## ---

## **什么是RTMFP？** RTMFP 是 Real‐Time Media Flow Protocol的缩写，是Adobe准备推出的一种新的通信协议，这种通信协议可以让 Flash 客户端直接和另外一个Flash 客户端之间进行数据通信，也就是常说的p2p的方式进行通信。 **什么时候能用上RTMFP？需要什么技术支持？** 只有下一个版本的播放器：Flash Player10 才支持RTMFP 协议，同时服务器端还需要下一个版本的 Flash Media Server，估计就是FMS4了，（我博客之前的一篇文章：http://www.cuplayer.com/index.php?play=reply&id=115没猜错）。 目前虽然Flash Player10的预览版本已经出来了，但是FMS4发布日期还没有定下来。所以目前RTMFP还体验不了。 **RTMFP有哪些新的功能？** 使用RTMFP，一些使用即时通讯技术的Flash应用，例如在线聊天，在线多人游戏等应用的通信效率将会大大提高，因为RTMFP支持客户端之间直接通信，包括麦克风、摄像头的共享等。（目前Flash客户端之间的通信都是要先经过服务器中转的，所以效率不高，服务器压力比较大，RTMFP技术出现后这些问题将会迎刃而解）。 不过RTMFP不支持文件的传输和共享。 **RTMFP给我们带来什么好处？** RTMFP将会大大地减少音视频直播、点播、多人在线游戏等应用的网络带宽的消耗，减轻服务器的负担。因为很多数据都是客户端之间直接传输了，无须再经过服务器中转了。 RTMFP由于使用了UDP网络协议，所以相对之前的TCP协议在数据传输效率上也会大大提高，这种优势在音视频数据传输方面是非常明显的。 关于TCP和UDP网络通信协议之间的区别以及各自的优缺点大家可以去网上搜索相关的介绍，这里就不再做过多的介绍了。 **RTMFP和RTMP有哪些区别？** 从本质上的区别就是网络通信的协议不一样，RTMFP是使用User Datagram Protocol (UDP)协议，而RTMP是使用Transmission Control Protocol (TCP)协议。 UDP协议对比TCP协议最大的优点就是传输流媒体数据的时候效率非常高，网络延迟少，增强音视频的传输质量，以及网络连接的可靠性增强。 RTMP的客户端之间要进行数据通信，必须先将数据发送到FMS等服务器端，然后服务器端再转发到另外一个用户，而RTMFP则支持客户端直接发送数据到另外一个客户端，无需经过服务器的中转。此时你也许会问，居然客户端之间的数据可以之间通信，还要FMS服务器做什么？其实此时的FMS服务器只起到桥梁作用，因为客户端之间要创建通信会话就必须要知道对方客户端的相关信息，就相当于你找对象要先经过媒婆介绍一样的道理，哈哈。 下面的示意图表现了RTMFP和RTMP的不同之处： **RTMFP适合用于哪些类型的应用？** RTMFP比较适合用于网络通信数据量比较大，通信即时性要求比较强的应用，例如VoIP，音视频即时沟通工具（IM），多人网络游戏等等。 **Adobe以后还会丰富RTMFP相关技术吗？** 会的，Adobe以后还会一如既往地对RTMFP进行进一步增强、优化以适合市场发展的需求，不过目前还没有进一步的相关声明。

## [![](https://i.imgur.com/ifSRbK3.png)](https://i.imgur.com/ifSRbK3.png)

## [![](https://i.imgur.com/ltMqnNy.png)](https://i.imgur.com/ltMqnNy.png)

推送去有支援rtmp的mediaserver，不過延遲的問題可能要考慮到buffertime  

  
## 打造一個多人視訊系統

## ---

請注意參數設定的
ams.ini Application.xml terminal
這關係到應用程式是否能正常運行，上述檔案有關檔案是否有權限。
  
## ```html <script src="https://gist.github.com/x213212/d855a2de34970d3d5c71bae99a75f13a.js"></script> ``` 防火牆設定

## ---

  

最重要!，連到伺服器外面端口，一定要把輸出輸入原則納編新增連接端口1935設為允許，  

不同電腦之間連接，防火牆一定要設置，否則debug到爽。  

[![](https://i.imgur.com/LMOalD7.png)](https://i.imgur.com/LMOalD7.png)
## shareObject

## ---

  

痾最後我不打算用shareObject，由於在性能上，適用共享去廣播參數，這會導致客戶端有無想接收訊息都會接受到廣播，第二個原因就是我弄到今天，在flash非同步的狀況下，fso檔案到底有沒有被寫入，原因可能就是上述，功力不夠?，綜合以上所已改用其他來開發  

  

<https://blog.csdn.net/wkyb608/article/details/5930823>  

  

  
##

## 結

## ---

## 上述算是未完成的程式碼懶得寫了，主要可以獲得該執行程式可以透過廣播的方式去傳遞，只要自行定義傳遞參數，把自己直播推流，和id傳遞過來基本再加一點邏輯判斷，一對多多對多，基本上都可以，視訊，監視器，直播阿應該都可以透過adobe media server實現，rtmp，至於詬病<https://blog.csdn.net/haima1998/article/details/78007123>，速度方面可能改天再做一個p2p之間的傳輸，目前adobe media server 會自動轉為 rtmfp所以之前的癥結點沒囉，目前等公司提案再來考慮要不要搭建其他平台囉。
