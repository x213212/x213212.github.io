---
title: "打造一個多人串流系統 adobe_media_server part1"
date: "2019-01-04T23:30:00.000+08:00"
updated: "2019-01-13T20:33:37.114+08:00"
permalink: "/2019/01/adobe-media-server-part1.html"
original_url: "https://x8795278.blogspot.com/2019/01/adobe-media-server-part1.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-4977135129736190504"
tags: ["adobe media server", "Flex", "Tutorial"]
layout: post
---

## 打造一個多人串流系統

## ---

基本上伺服器用的是adobe media server 免費版開放連接數是10個為上限
然後程式碼的話，像在常見的環境，有的人可能不想裝flash，或者裝其他套件來播放，就以fb來說，假設可能要裝flash那時候可能就有可能一堆人都不要用了，當然有內建，現在是html5的時代，後續我會補上這功能。
就以稍微看一下目前的話
包括flash
adobe media server 後台
## ---

[![](https://i.imgur.com/YQpHoJ3.png)](https://i.imgur.com/YQpHoJ3.png)
也就是
[![](https://i.imgur.com/PAj2vgb.png)](https://i.imgur.com/PAj2vgb.png)
可以共同分享這個物件
打開document參考一下  

[![](https://i.imgur.com/XjtQsag.png)](https://i.imgur.com/XjtQsag.png)

##

  
## 程式碼

## ---

  

```html
<script src="https://gist.github.com/x213212/ec98760db09228442e0d51afebbe484e.js"></script>
```

程式碼大致上長這樣應該可以改了，
修改了大概考慮到控件的貼圖等等不考用慮用
addchild這個算比較舊的，所以改用
 var tmp:UIComponent = new UIComponent();
 tmp.addChild(vidPlayer);
 canvas.addElement(tmp);
  

nc.client ={ onBWDone: function():void{} };
回調
再來就是最重要的
NetStream的buffertime=0.1;
這關係到畫面上的抖動，在開刀的時候很重要呢，不過痾，缺點就是會延遲
到時候公司的伺服器可能又要升級了，
再者就是
目前使用flash去開發
因為考慮到跨平台
所以在打造一個多人的系統呢我打算用裡面的shareobject
  
## 編譯

## ---

目前使用的程式碼可以通用於執行檔和web網頁，因為底層都是flash所以只要能載入flash基本上可以達到跨平台的效果，然後flash真的是我用過最舊的東西，可能我是目光太淺，痾在build web application的時候  

請注意
[![](https://i.imgur.com/58MAgRm.png)](https://i.imgur.com/58MAgRm.png)
  

[Download the Flash Player content debugger for Opera and Chromium based applications – PPAPI](https://fpdownload.macromedia.com/pub/flashplayer/updaters/32/flashplayer_32_ppapi_debug.exe)
太舊了，這點下去會開啟ie，在windows10的時候把預設瀏覽器設為chrome，他直接沒反應，裝完的時候，這才是問題的第一步，我們請看下一步
## 執行

## ---

能編譯還不算還要伺服器，這邊呢因為考慮到測試，目前用xampp來架設伺服器  

[![](https://i.imgur.com/ipFcTy9.png)](https://i.imgur.com/ipFcTy9.png)
端口會跟flash media server 的後台互衝，所以我們的伺服器換個端口8080  

[![](https://i.imgur.com/22sIC6U.png)](https://i.imgur.com/22sIC6U.png)
有可能要離線設置或著flash player 權限問題
[![](https://i.imgur.com/TwtnBpa.png)](https://i.imgur.com/TwtnBpa.png)
  

[Global Security Settings panel](http://www.macromedia.com/support/documentation/en/flashplayer/help/settings_manager04.html)
  

有可能要來這裡新增一下把網站的swf都加入
## 執行part2

## ---

[![](https://i.imgur.com/xfgrdBF.png)](https://i.imgur.com/xfgrdBF.png)
[![](https://i.imgur.com/hqHrCKS.png)](https://i.imgur.com/hqHrCKS.png)
直接執行的話，還是會跳出錯誤訊息，然後跳出一個ie，然後就沒有然後了，這個時候會卡在50%，
可能是windows 預設瀏覽器裡面就有裝adobe不過那裏面沒有debug plugin之類的，所以flash buileder會卡在那邊等deubg工具回應，不過沒關係我們在編譯的那邊已經裝了，chrome的debug工具，所以現在我們貼上網址去chrome瀏覽器
  

[![](https://i.imgur.com/BdgbHKX.png)](https://i.imgur.com/BdgbHKX.png)
  

[![](https://i.imgur.com/YxNu3Y0.png)](https://i.imgur.com/YxNu3Y0.png)
成功可以debug囉
## 畫面

## ---

[![](https://i.imgur.com/UdFvxYX.png)](https://i.imgur.com/UdFvxYX.png)

## 初期架構

## ---

做個小筆記，初期架構額到時可能每個人都有一個獨立app也就是獨自的rtmp，那麼，架設多人視訊的話，會去讀房間的shareobject假設要撥放的話，假設其他客戶端連線的話也代表它們也有rtmp，初步設定他們的名稱就是，rtmp的網址  

那麼我只要在shareobject裡面master一定是第一個放主畫面，自己的url略過這樣的話就算  

初步實現多人會議了，痾就這麼簡單，要實作一個直播平台，youtube串流也可以不過協定應該不會使用rtmp，當然在伺服器分流也要做好處理，網速當然是重點，cpu解碼速度不知道有沒有用這可能就要深入探討，下回揭曉沒意外應該會寫sharobject應用到實際  

  

  

參考
<https://www.itread01.com/content/1541966720.html>
<https://wenku.baidu.com/view/b9e159bfc77da26925c5b023.html>
<https://blog.csdn.net/leixiaohua1020/article/details/43936141>
