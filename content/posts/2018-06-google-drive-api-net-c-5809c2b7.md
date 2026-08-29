---
title: "Google Drive API .NET 一條龍系列 C#"
date: "2018-06-11T17:38:00.001+08:00"
updated: "2018-09-05T07:51:44.606+08:00"
permalink: "/2018/06/google-drive-api-net-c.html"
original_url: "https://x8795278.blogspot.com/2018/06/google-drive-api-net-c.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-7781194577694379892"
tags: ["C#", "Tutorial"]
layout: post
---

## 前置作業

---

[google_console](https://console.developers.google.com/)  

我們近來到這裡我們找尋左邊的
[![](https://i.imgur.com/FwK3eep.png)](https://i.imgur.com/FwK3eep.png)
接下來呢
[![](https://i.imgur.com/QcrPt9w.png)](https://i.imgur.com/QcrPt9w.png)
應用程式類型一定要選擇其他
然後呢
創建完後得到
[![](https://i.imgur.com/docjCXm.png)](https://i.imgur.com/docjCXm.png)
下載後得到一個json
  
## Visual Studio

---

  

透過NUGET 搜尋並下載 Google APIs Client Library點選右方安裝!
[![](https://i.imgur.com/kIi1ryo.png)](https://i.imgur.com/kIi1ryo.png)
[![](https://i.imgur.com/hy8GpL7.png)](https://i.imgur.com/hy8GpL7.png)
取名叫做client_id，一定要記得勾選一率複製重要!然後複製到目前的專案底下我們這邊放在參考這邊  

[![](https://i.imgur.com/ewmCgFf.png)](https://i.imgur.com/ewmCgFf.png)
  
## 可疑情況

---

## 0x1 redirect_uri_mismatch

ㄎㄎvisual studio 有一個位置重導向，這在開發asp.net也就是網路應用程式的話，每次你的visual studio 會動態的產生一組port，在asp.net的話呢可以把動態port設為false。  

## 0x2 secret key 遺失

就是可能你授權出錯或是下載到錯誤的json檔解析錯誤這樣，我一開始選擇的是網路應用程式，debug好久呢~  

  

## Github

<https://gist.github.com/x213212/340a324c25aee5b8df9513806ced0187>

---

```html
<script src="https://gist.github.com/x213212/340a324c25aee5b8df9513806ced0187.js"></script>
```

  
## 最後來小小抱怨一下

---

我的部落格阿，考杯剩下6X個文章嗚嗚
