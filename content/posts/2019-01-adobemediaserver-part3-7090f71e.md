---
title: "打造一個多人串流系統 adobe media server f4m to HTTP Live Streaming(hls) part3"
date: "2019-01-09T22:37:00.002+08:00"
updated: "2019-01-13T20:33:37.180+08:00"
permalink: "/2019/01/adobemediaserver-part3.html"
original_url: "https://x8795278.blogspot.com/2019/01/adobemediaserver-part3.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-840215920307252208"
tags: ["adobe media server", "hls", "Tutorial"]
layout: post
---

[![](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSoIDac7djq02zwwtRWyS4MA_jL_2DmddSk4cP2i9SSvas8-lLq)](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSoIDac7djq02zwwtRWyS4MA_jL_2DmddSk4cP2i9SSvas8-lLq)
  
# Adobe宣布Flash不再更新2020年全面停用,HTML5淘汰Flash成為多媒體網頁主流

![Adobe宣布Flash不再更新2020年全面停用,HTML5淘汰Flash成為多媒體網頁主流 (比較，取代,2D動畫，多媒體,ActionScript,Safari,Firefox,Flash Player)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiJcdW0Vv8S8NB1hhAAhTjS_umYe1KTNt6ZF7EhzxjJ0ii4E4TfxkCFKFVBd7mMZTS2jzOAXYTLLb65HsccTuDViPIkHGjU8vxpApuxkLbipKaOLP6nOtOJV-ZY-ebr-4bH82shosVP3u4/s1600/1463406966-1583329830.jpg "Adobe宣布Flash不再更新2020年全面停用,HTML5淘汰Flash成為多媒體網頁主流 (比較，取代,2D動畫，多媒體,ActionScript,Safari,Firefox,Flash Player)")

  

HTML5 出現之後，和 Flash 的比較、取代到淘汰的話題始終熱門。Flash 歷經 Macromedia 時代到 Adobe 時代，可以說是平面2D多媒體設計的主流軟體；然而，時至今日Flash 已經是走入末途，越來越多的開發公司表示不採用 Flash Player 與其相關技術，主流瀏覽器也陸續停止支援這個漏洞永遠補不完且很吃系統資源的舊技術。  

  

自2016年 Google 表示最快該年底就會將 Chrome 瀏覽器預設停止支援與使用Flash後，2017年的現在，Adobe 都已經確定宣告 Flash 將走入歷史。  

  

Adobe宣布Flash不再更新2020年全面停用,HTML5淘汰Flash成為多媒體網頁主流 (比較，取代,2D動畫，多媒體,ActionScript,Safari,Firefox,Flash Player)
<https://liangyowen.blogspot.com/2017/09/html5-replace-adobe-flash.html>

  

綜合於上述原因我們來思考一下解決方案吧!
## HTTP Live Streaming(hls)

## ---

[![](https://blackie1019.github.io/2017/04/02/HLS-js-for-Chrome-Desktop/hls.png)](https://blackie1019.github.io/2017/04/02/HLS-js-for-Chrome-Desktop/hls.png)  

**HTTP Live Streaming**（縮寫是**HLS**）是一個由[蘋果公司](https://zh.wikipedia.org/wiki/%E8%8B%B9%E6%9E%9C%E5%85%AC%E5%8F%B8 "蘋果公司")提出的基於[HTTP](https://zh.wikipedia.org/wiki/HTTP "HTTP")的[流媒體](https://zh.wikipedia.org/wiki/%E6%B5%81%E5%AA%92%E4%BD%93 "流媒體")[網絡傳輸協議](https://zh.wikipedia.org/wiki/%E7%BD%91%E7%BB%9C%E4%BC%A0%E8%BE%93%E5%8D%8F%E8%AE%AE "網絡傳輸協議")。是蘋果公司[QuickTime X](https://zh.wikipedia.org/w/index.php?title=QuickTime_X&action=edit&redlink=1 "QuickTime X（頁面不存在）")和[iPhone](https://zh.wikipedia.org/wiki/IPhone "IPhone")軟體系統的一部分。它的工作原理是把整個流分成一個個小的基於HTTP的文件來下載，每次只下載一些。當媒體流正在播放時，客戶端可以選擇從許多不同的備用源中以不同的速率下載同樣的資源，允許流媒體會話適應不同的數據速率。在開始一個流媒體會話時，客戶端會下載一個包含元數據的[extended M3U (m3u8)](https://zh.wikipedia.org/w/index.php?title=Extended_M3U&action=edit&redlink=1 "Extended M3U（頁面不存在）") [playlist](https://zh.wikipedia.org/w/index.php?title=Playlist&action=edit&redlink=1 "Playlist（頁面不存在）")文件，用於尋找可用的媒體流。
HLS只請求基本的HTTP報文，與[實時傳輸協議（RTP）](https://zh.wikipedia.org/wiki/%E5%AE%9E%E6%97%B6%E4%BC%A0%E8%BE%93%E5%8D%8F%E8%AE%AE "實時傳輸協議")不同，HLS可以穿過任何允許HTTP數據通過的[防火牆](https://zh.wikipedia.org/wiki/%E9%98%B2%E7%81%AB%E5%A2%99 "防火牆")或者[代理伺服器](https://zh.wikipedia.org/wiki/%E4%BB%A3%E7%90%86%E6%9C%8D%E5%8A%A1%E5%99%A8 "代理伺服器")。它也很容易使用[內容分發網絡](https://zh.wikipedia.org/wiki/%E5%85%A7%E5%AE%B9%E5%88%86%E7%99%BC%E7%B6%B2%E7%B5%A1 "內容分發網絡")來傳輸媒體流。
蘋果公司把HLS協議作為一個[網際網路草案](https://zh.wikipedia.org/w/index.php?title=Internet-Draft&action=edit&redlink=1 "Internet-Draft（頁面不存在）")（逐步提交），在第一階段中已作為一個非正式的標準提交到[IETF](https://zh.wikipedia.org/wiki/IETF "IETF")。2017年8月，RFC 8216發布，描述了HLS協議第7版的定義。
  

## adobe media server to hls

## ---

[![](https://i.imgur.com/vJNJjEh.png)](https://i.imgur.com/vJNJjEh.png)
  

恩恩看來新版adobe media server 有支援 hls 之間的轉換，就來看怎樣實現過程吧!
  

## Flex to HTTP Live Streaming

## ---

  

使用html5進行撥放，並不支援原生撥放數據，所以必須再轉成hls
  

  

http://localhost/hds-live/livepkgr/_definst_/liveevent/livestream.m3u8
  

  

http://localhost/hds-live/livepkgr/_definst_/liveevent/livestream.f4m
  

  

使用html5進行撥放，並不支援原生撥放數據，所以必須再轉成hls
  

  

http://localhost/hds-live/livepkgr/_definst_/liveevent/livestream.m3u8
[![](https://i.imgur.com/UfZNQOc.png)](https://i.imgur.com/UfZNQOc.png)
  

輸入範例  

rtmp://localhost/livepkgr  

和  

 livestream?adbe-live-event=liveevent  

  

[name]? adbe-live-event=liveevent  

  

Stream里面输入：livestream?adbe-live-event=liveevent 如果左边的Preset设置了多路，Stream就要修改为：livestream%i?adbe-live-event=liveevent   

  

  

## 新建crossdomain.xml跨網域權限文件

## --- 目前設為最寬鬆 位置 C:\Program Files\Adobe\Adobe Media Server 5\webroot\crossdomain.xml ```html <script src="https://gist.github.com/x213212/874560d6412eed30e7089ad1e28e17d5.js"></script> ```

## 推送頻道範例

## ---

  

[![](https://i.imgur.com/y8AQ4dm.png)](https://i.imgur.com/y8AQ4dm.png)
推送去123頻道成功會在
C:\Program Files\Adobe\Adobe Media Server5\applications\livepkgr\streams\_definst_   

產生該頻道資料夾

![](https://i.imgur.com/LPZXanM.png)

  

  

  

注意端口，和url文件位置與檔案格式  

  

http://172.16.2.111:8134/hds-live/livepkgr/_definst_/liveevent/livestream.f4m  

  

  

http://172.16.2.111:8134/hls-live/livepkgr/_definst_/liveevent/livestream.m3u8
  

檢測是否成功推送可以鍵入此連結  

http://172.16.2.111:8134/hds-live/livepkgr/_definst_/liveevent/livestream.f4m  

  

  

[![](https://i.imgur.com/lNfaxhh.png)](https://i.imgur.com/lNfaxhh.png)
  
## 多路推送 品質修改 (尚未研究)

## --- (好像是自動適應，依網路速度自行切換吧? C:\Program Files\Adobe\Adobe Media Server 5\applications\livepkgr\events\_definst_\liveevent\ Manifest.xml [![](https://i.imgur.com/zy9kKqa.png)](https://i.imgur.com/zy9kKqa.png)

## Html5使用hls.js 撥放器，撥放m3u8串流

## --- [![](https://i.imgur.com/gOyN796.png)](https://i.imgur.com/gOyN796.png) [![](https://i.imgur.com/2wPcS9T.png)](https://i.imgur.com/2wPcS9T.png) adobe  media server  to hls ! ```html <script src="https://gist.github.com/x213212/1fb5af253396fab284026e74778e522c.js"></script> ```
