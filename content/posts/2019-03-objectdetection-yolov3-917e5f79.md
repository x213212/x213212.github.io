---
title: "自定義 Object_detection yolov3 待續..."
date: "2019-03-31T23:05:00.002+08:00"
updated: "2019-06-22T20:02:34.066+08:00"
permalink: "/2019/03/objectdetection-yolov3.html"
original_url: "https://x8795278.blogspot.com/2019/03/objectdetection-yolov3.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-7835823511898592380"
tags: ["C", "Tutorial"]
layout: post
---

[![](https://i.imgur.com/c7DuWIU.png)](https://i.imgur.com/c7DuWIU.png)
自定義 Object_detection yolov3
## ---

這大概是我裝過算有點難裝的一套 [darknet github](https://github.com/AlexeyAB/darknet) 版本的 [yolo v3](https://mropengate.blogspot.com/2018/06/yolo-yolov3.html)  
## **(You only look once)**

演算法更快 更穩，當然安裝更難裝  

首先呢，  

先安裝 vs2017  

再來就是下載 cuda 9.1 嗯嗯別問我為什麼 我在 cuda 9.0 包 這邊 走跟 github 不同的方式  

因為會有衝突，visual studio 2017 請裝 community 因為可以新增套件，等等  

所以詳細步驟則是  

  

  

- install vs2017
- install opencv3.1
- install cuda 9.1
- Cuda v9.1 setting
- visual studio 2017 setting
- build
- runing object data

  

系統配置
## ---

windwos10  

cuda V9.1  

opencv 3.1  

darknet gpu 版

Install Visual studio 2017
## ---

  

[![](https://i.imgur.com/GEvp2IA.png)](https://i.imgur.com/GEvp2IA.png)  

這邊安裝完後的時候請勾選
[![](https://i.imgur.com/fJmzaMZ.png)](https://i.imgur.com/fJmzaMZ.png)
vc++ 2015v140 工具組
[![](https://i.imgur.com/RRqQXPN.png)](https://i.imgur.com/RRqQXPN.png)
然後 darknet 專案檔案為
C:\Users\x2132\Desktop\darknet-master\build\darknet
[![](https://i.imgur.com/DA7D8Lo.png)](https://i.imgur.com/DA7D8Lo.png)
  

  

Install opencv3.1
## ---

在nuget 裡面搜尋 opencv3.1
[![](https://i.imgur.com/U2rhGTA.png)](https://i.imgur.com/U2rhGTA.png)

Install cuda9.1
## ---

  

[![](https://i.imgur.com/PcH5upJ.png)](https://i.imgur.com/PcH5upJ.png)
這邊官網會說 請把 2017 移除再重裝cuda 這邊的話會花費太多時間，而且還不一定會對
在darknet 編譯的過程中會需要裡面資料夾的一些設定檔
D:\download\cuda_9.1.85_win10\CUDAVisualStudioIntegration\extras\visual_studio_integration\MSBuildExtensions
[![](https://i.imgur.com/j6kRkOF.png)](https://i.imgur.com/j6kRkOF.png)
  

複製到  

C:\Program Files (x86)\MSBuild\Microsoft.Cpp\v4.0\v140\BuildCustomizations  

[![](https://i.imgur.com/GutxXJS.png)](https://i.imgur.com/GutxXJS.png)
  

Cuda v9.1 setting

  
## ---

在這邊的話 為了讓visual studio 2017 可以抓到，恩..大致原因就是 cuda 跟不太上 vs 速度 哈哈  

C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v9.1\include\crt  

[![](https://i.imgur.com/f1SlV7B.png)](https://i.imgur.com/f1SlV7B.png)
更改為 1920 或更高版號  

  

  

visual studio 2017 setting

  
## ---

這邊呢，假設是要用自定義的 cuda 這邊選用為 cuda 9.1設定檔則  

[![](https://i.imgur.com/PRO7Oqs.png)](https://i.imgur.com/PRO7Oqs.png)
和  

[![](https://i.imgur.com/Hsiz7Xk.png)](https://i.imgur.com/Hsiz7Xk.png)
更改為 cuda 9.1 設定檔  

  

然後喔這邊的組態設定為 所有組態為x64，平台工具組設為 v140  

[![](https://i.imgur.com/2e6nfwr.png)](https://i.imgur.com/2e6nfwr.png)
請設置為你目前電腦版本的cuda! 這邊設定為v9.1
[![](https://i.imgur.com/aCV1ExZ.png)](https://i.imgur.com/aCV1ExZ.png)
這邊聽官方說的只留這個compute_30,sm_30;
[![](https://i.imgur.com/tbGXd7f.png)](https://i.imgur.com/tbGXd7f.png)
  

build!

  
## ---

當然不可能給你這麼好過  

  

[![](https://i.imgur.com/x8EyW0O.png)](https://i.imgur.com/x8EyW0O.png)
加個括號
[![](https://i.imgur.com/TRYAZyI.png)](https://i.imgur.com/TRYAZyI.png)
終於編譯成功， 半天時間也消失了@@
  

  

runing object data

  
## ---

可能明天才會做 數據標籤的教學，然後則  

<https://pjreddie.com/media/files/yolov3.weights>  

這個是 國外大大訓練好的數據，可以下來再來測試  

下載完則放置於  

[![](https://i.imgur.com/JuHsGQR.png)](https://i.imgur.com/JuHsGQR.png)
開始下指令囉，
<https://pjreddie.com/darknet/yolo/>
[![](https://i.imgur.com/lHkzNVk.png)](https://i.imgur.com/lHkzNVk.png)
```
./darknet detector demo cfg/coco.data cfg/yolov3.cfg yolov3.weights
```
[![](https://i.imgur.com/sCjNj1d.png)](https://i.imgur.com/sCjNj1d.png)
這邊 chrome 分頁開太多qq
關掉一些
  

[![](https://i.imgur.com/c7DuWIU.png)](https://i.imgur.com/c7DuWIU.png)
