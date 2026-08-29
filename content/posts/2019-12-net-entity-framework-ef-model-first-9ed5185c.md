---
title: ".net entity framework 初步探討 (二) EF model first"
date: "2019-12-05T08:31:00.001+08:00"
updated: "2019-12-05T11:04:02.854+08:00"
permalink: "/2019/12/net-entity-framework-ef-model-first.html"
original_url: "https://x8795278.blogspot.com/2019/12/net-entity-framework-ef-model-first.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-220207985056333649"
tags: [".NET", "C#", "Tutorial"]
layout: post
---

# 建立一個 [ADO.NET](http://ado.net/) 資料庫模型

![](https://i.imgur.com/lueORAn.png)

  

選用 ADO.NET實體資料庫模型  

![](https://i.imgur.com/MOe7l25.png)

# EF model first from db

從"現有"的資料庫產生 EF model，可以直接對現有 table 欄位進行修改 而不動到其 資料表結構  

![](https://i.imgur.com/xeVRNcu.png)

  

![](https://i.imgur.com/0LL0tbs.png)

  

選用新增連接  

![](https://i.imgur.com/GxFIeSk.png)

  

當前現有資料庫  

![](https://i.imgur.com/Cp0bBO0.png)

  

![](https://i.imgur.com/SfhDYwI.png)

  

選完後準備產生模型  

![](https://i.imgur.com/ANZVOuY.png)

  

![](https://i.imgur.com/VZ8D5za.png)

  

這邊可以看到我們的EF model 已經產生出來了  

![](https://i.imgur.com/HNSYYsZ.png)

# Empty EF model generate db

從空的 EF model 產生 資料庫  

![](https://i.imgur.com/lgh1i8n.png)

  

那麼這邊就可以進行直接的資料庫建構，從工具箱直接拉取需要的物件  

![](https://i.imgur.com/fta0QwQ.png)

  

包括一些關聯等等  

![](https://i.imgur.com/8PD6vvP.png)

  

![](https://i.imgur.com/k6NtPds.png)

  

一個部落格可以有很多文章  

當資料庫設計好了之後我們可以直接產生相對應的 t-sql 語法  

![](https://i.imgur.com/TH0Lwmh.png)

  

![](https://i.imgur.com/4K2jGTK.png)

這邊在上面的範例已經填入相對應資料  

![](https://i.imgur.com/izFuyg5.png)

這邊可以看到 會產生下列錯誤，這邊國外網友是說重開就好 xd(有更好解決方案以後再說，或請網友留言  

![](https://i.imgur.com/lGeGPYH.png)

  

重開後可以看到  

![](https://i.imgur.com/QZjqXtO.png)

  

已經可以產生相對應 SQL 檔案，我們再重新運行 SQL 腳本  

![](https://i.imgur.com/dUIq9YB.png)

  

![](https://i.imgur.com/Hb2tySA.png)

  

好了直接連接  

![](https://i.imgur.com/djZfzSp.png)

  

這邊可以看到到腳本已經運行完畢!，我們去開MSMS看一下，或者 visual stdion 旁邊的sql 瀏覽窗口也行  

![](https://i.imgur.com/ZU9nVYf.png)

  

![](https://i.imgur.com/EyImbvy.png)

  

可以觀察一下結果是否跟你的資料庫設計是否吻合
