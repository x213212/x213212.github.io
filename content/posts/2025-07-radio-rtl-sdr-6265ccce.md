---
title: "radio rtl sdr"
date: "2025-07-13T17:04:00.003+08:00"
updated: "2025-08-04T00:57:00.874+08:00"
permalink: "/2025/07/radio-rtl-sdr.html"
original_url: "https://x8795278.blogspot.com/2025/07/radio-rtl-sdr.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-4443515574493330862"
tags: ["radio rtl sdr"]
layout: post
---

![](https://hackmd.io/_uploads/ByprMl-8xg.png)

# radio rtl sdr
基本上有一段時間沒碰程式碼，玩一下無線電
# 攔截noaa衛星 氣象圖
noaa衛星追蹤軟體，這邊可以用
orbitron估算衛星經過的時間可以在這時候發送訊號，再透過錄製聲音訊號再轉NOAA APT、Weather Satellite APT、APT decoding應該可以看到圖
![image](https://hackmd.io/_uploads/SycBWeZIlx.png)
![image](https://hackmd.io/_uploads/Bkx8Wgb8ge.png)
預測後有兩種方法可以接受訊號那就是
rtl sdr 這邊我買的是亞馬遜的
![image](https://hackmd.io/_uploads/HyjOZx-Ixg.png)

順便買了幾組無線電，這是kv6 也是開源的之後無聊可以刷機一下
燒頻道
chirb ,
![image](https://hackmd.io/_uploads/H10-Mg-8xe.png)

![image](https://hackmd.io/_uploads/ByprMl-8xg.png)

# 攔截飛機訊號
這邊要下載
dump1090-master.zip 注意這個要用最高權限才攔截的到rtl sdr，搞好久
用virtual radar server也可以攔截到訊號
![image](https://hackmd.io/_uploads/BkS9MgWIle.png)

# 攔截無線電訊號
rtl sdr
![image](https://hackmd.io/_uploads/B15YNxZ8xl.png)

![image](https://hackmd.io/_uploads/Byjq4xZIlx.png)

