---
title: "Face detection_抓小偷"
date: "2018-06-24T06:19:00.004+08:00"
updated: "2019-09-13T08:56:04.410+08:00"
permalink: "/2018/06/face-detection.html"
original_url: "https://x8795278.blogspot.com/2018/06/face-detection.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6491266282729651009"
tags: ["Android", "Java", "Tutorial", "Projects"]
layout: post
---

## 介紹

## --- 如果java client 端如果有偵測到人臉的話會儲存一張圖片到c:\\peoples.png 然後偵測到的人臉大於1的話則會將嫌疑人的照片儲存下來並發送一張圖片到 指定ip並告知可能有人在你家 Server 端如果有將會一直開著持續監聽 [![](https://i.imgur.com/FwW1OjL.png)](https://i.imgur.com/FwW1OjL.png)[![](https://i.imgur.com/C2Aeb2t.png)](https://i.imgur.com/C2Aeb2t.png)

## 環境設定

---

Javacv 1.2: <https://github.com/bytedeco/javacv>
Eclipse
Android studio
Opencv 2.49 or 48

<https://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.4.9/>
  

  
## Javacv 1.2建置

---

下載好javacv後建立一個eclipse 專案 選jse就可以了這邊要來做監控的client,記得把這些函示庫引入
[![](https://i.imgur.com/6Dlq3W9.png)](https://i.imgur.com/6Dlq3W9.png)
[![](https://i.imgur.com/YRHNAGM.png)](https://i.imgur.com/YRHNAGM.png)
## Opencv 建置

---

[![](https://i.imgur.com/aXzii5I.png)](https://i.imgur.com/aXzii5I.png)
[![](https://i.imgur.com/XhfkAde.png)](https://i.imgur.com/XhfkAde.png)
64位元就選x64,32位元就選x86
## Face detection.code

---

  

```html
<script src="https://gist.github.com/x213212/0ccd9003cb1c02323e849b9e9f43eb04.js"></script>
```
