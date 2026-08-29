---
title: "Ida pro use python plugin remote debuging"
date: "2021-01-16T02:18:00.002+08:00"
updated: "2021-01-16T02:18:19.648+08:00"
permalink: "/2021/01/ida-pro-use-python-plugin-remote.html"
original_url: "https://x8795278.blogspot.com/2021/01/ida-pro-use-python-plugin-remote.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3143378039981731715"
tags: ["GCC", "ida"]
layout: post
---

![](https://i.imgur.com/8WH5RAc.png")

# ida pro use python plugin remote debuging
看了一下ida pro 原來是可以透過python plugin 的方式把組合語言轉成類似 c 語言的虛擬碼
步驟如下
環境是 windows 下 debug linux x64 elf 檔案
https://blog.csdn.net/weixin_26746861/article/details/108176312
主要參考
載入目標machine 檔案 (這邊選擇 linux x64 elf 檔案
主要步驟是要在windows 端 載入 cc1
```
chmod +x linux_server
chmod +x linux_server64
```
![](https://i.imgur.com/I2aFuwi.png)
![](https://i.imgur.com/DNRPEvk.png)
![](https://i.imgur.com/NbtqekE.png)
![](https://i.imgur.com/b0dO4Ce.png)
![](https://i.imgur.com/XfjTrZK.png)
![](https://i.imgur.com/ZXmTygU.png)
![](https://i.imgur.com/lcCU1kI.png)
![](https://i.imgur.com/ZS4Kw9O.png)
![](https://i.imgur.com/8vbK71G.png)
https://code.woboq.org/gcc/libcpp/line-map.c.html#_Z18get_range_from_locP9line_mapsj
隨便挑一個
![](https://i.imgur.com/Ybpc26h.png)
在修改gcc 無法變動的時候或者需要及時watch 流程分支的時候除了看官方文檔應該可以嘗試這些方式進行追蹤
當然也有提供一些分析 so 檔的方式 可能有空再來看一下這部分如何分析

