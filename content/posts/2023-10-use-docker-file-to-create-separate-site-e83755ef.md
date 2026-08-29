---
title: "Use a docker file to create a separate site for the frontend and backend"
date: "2023-10-15T12:28:00.003+08:00"
updated: "2023-10-15T12:28:23.954+08:00"
permalink: "/2023/10/use-docker-file-to-create-separate-site.html"
original_url: "https://x8795278.blogspot.com/2023/10/use-docker-file-to-create-separate-site.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-1529315791773228266"
tags: ["Docker", "flask", "mongodb", "Redis", "Vue.js"]
layout: post
---

![](https://hackmd.io/_uploads/Hk7jt1Fbp.png)

# Use a docker file to create a separate site for the frontend and backend
https://github.com/x213212/test_report/tree/main
# test_report
Use a docker file to create a separate site for the frontend and backend
如果想快速做個小網站，最近把它弄成一個dockerfile的專案 裡面前後端分離用vue + flask + crud 中間加一層redis,資料庫用mogodb ,之後無聊玩東西可以用這個框架來玩
![](https://hackmd.io/_uploads/HJZEckY-p.png)

# command
```
docker cmpose build
docker cmpose up
docker cmpose down
```
![](https://hackmd.io/_uploads/Hk7jt1Fbp.png)

