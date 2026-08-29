---
title: "Docker 安裝 和搭建Redis編寫環境"
date: "2019-04-05T00:50:00.001+08:00"
updated: "2019-06-22T20:02:33.660+08:00"
permalink: "/2019/04/docker-redis.html"
original_url: "https://x8795278.blogspot.com/2019/04/docker-redis.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-196419281598010813"
tags: ["C", "Docker", "Redis", "Tutorial"]
layout: post
---

[![](https://cdn-images-1.medium.com/max/1200/1*MgdgqhwAZOKoOTCyqswaJA.png)](https://cdn-images-1.medium.com/max/1200/1*MgdgqhwAZOKoOTCyqswaJA.png)
<https://koukia.ca/installing-redis-on-windows-using-docker-containers-7737d2ebc25e>  

Docker 安裝 和搭建Redis編寫環境
## ---

大哥要走了，能不能繼承他的遺志呢，先來著手搭建環境，解決資料重複查詢問題，大哥說醫院架構組的是JPA機制，由於呢java 處理 xml的東西(? 是有問題的?，就在這一層假設能做到cache那麼，可以大大減少對伺服器重複的負擔。  

再裝 Redis 之前，我們要先裝起docker，  

先決條件是不能裝vm，  

然後電腦版本需求 不能是windows 預覽版，  

再來就是系統必須支援hyper-v，  

那麼 我的電腦又開始有一堆問題了  

，首先我裝的是 windows 10 home 所以呢，我需要強制開啟hyper-v  

上script  

再來就是 裝完重新開機我設成這樣  

[![](https://i.imgur.com/iKju2Eb.png)](https://i.imgur.com/iKju2Eb.png)，恩 其中裝環境就可以耗掉很多時間了  

<https://docs.docker.com/toolbox/toolbox_install_windows/>  

<https://oomusou.io/docker/toolbox/>  

，我已經把最難的script 找出來了接下來應該算滿簡單  

  

接下來比較詭異的地方來了我們要編譯Redis，當然我們是需要編寫程式去控制的所以呢我們要在這邊搭建編寫的環境  

然後我們使用的visual studio 環境  

這邊呢順便，這個專案是微軟專門維護的應該是(?  

<https://github.com/MicrosoftArchive/redis>  

然後我們下載進來，進去msvs  

[![](https://i.imgur.com/TlSG82I.png)](https://i.imgur.com/TlSG82I.png)
開啟我們的專案  

[![](https://i.imgur.com/qMoG2Le.png)](https://i.imgur.com/qMoG2Le.png)
這邊的話，因為我們已經決定要把伺服器架在，docker所以呢，我們這邊負責把 相關的lib 給編出來給我們 最上面那隻ConsoleApplication1 (這是我們新建的)給引用，下面會詳細介紹lib放置位置，在上圖中我們把hiredis，Win32_Interop給重新建置就可以了記得，我們假設使用的是 2017，我們在上一章環境把它設為較低一點，相容性會比較好?
[![](https://i.imgur.com/vEREJx6.png)](https://i.imgur.com/vEREJx6.png)
  

沒意外我們要來開始搬檔案了，首先我們先新增一個專案
<https://blog.csdn.net/sinat_33508334/article/details/85077966>
[![](https://i.imgur.com/VqRB1Bb.png)](https://i.imgur.com/VqRB1Bb.png)
其實我不常用visual studio 寫code，所以有點不知道 lib 檔案放置位置所以呢，我參照，一些神人的放置，加上我以前那樣放置code，就編譯成功了，
這位國人話說的有點籠統我們來詳細解析一下
  

首先我們把剛剛hiredis，Win32_Interop，給編譯完，取得下面這兩個

- \redis-3.0\deps\hiredis
- \redis-3.0\src\Win32_Interop

複製到我們ConsoleApplication1 目錄底下，然後我們的專案直接參考
[![](https://i.imgur.com/Km2qS9p.png)](https://i.imgur.com/Km2qS9p.png)
就對專案直接右鍵，有個參考，打勾這裡相當於 應該是
#pragma comment(lib,"XXX.lib")
然後我們按下確定，跑去標頭檔那邊
[![](https://i.imgur.com/k0MXi9e.png)](https://i.imgur.com/k0MXi9e.png)
這邊我們直接指定了
  

```html
<script src="https://gist.github.com/x213212/319354a301f14835a9f55d1d232a2872.js"></script>
```

  

再來回到我們主程式
  

[![](https://i.imgur.com/8lz8KTA.png)](https://i.imgur.com/8lz8KTA.png)
run!，但是目前你們是看不到畫面的
[![](https://i.imgur.com/HjlJEH7.png)](https://i.imgur.com/HjlJEH7.png)
