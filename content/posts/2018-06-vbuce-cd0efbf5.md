---
title: "VB_寫個UCE記憶體修改程式"
date: "2012-06-24T13:29:00.000+08:00"
updated: "2019-09-13T08:56:02.851+08:00"
permalink: "/2018/06/vbuce.html"
original_url: "https://x8795278.blogspot.com/2018/06/vbuce.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-1850142428424661554"
tags: ["cheat", "Tutorial", "VB6", "Projects"]
layout: post
---

## 實現?

普通遊戲防護後來都有掛載一個防護像是NP新一點還有HS等等為什麼那些都會達到阻擋呢在VB有一種方式就是用writememony這個去寫一個一個位元當然後面還是被擋掉了，要用其他地方恢復的話要用hook或是遊戲剛開起時候快速覆蓋掉有係防護的掛勾達到bypass的作用 這邊我沒用，我用的是引用ce的寫入crc方式在載入一個dll inject去達到bypass的方式去使用外掛

[![](https://i.imgur.com/6sUGERW.png)](https://i.imgur.com/6sUGERW.png)

[![](https://i.imgur.com/ODTI58F.png)](https://i.imgur.com/ODTI58F.png)

[![](https://i.imgur.com/ZapZAYE.png)](https://i.imgur.com/ZapZAYE.png)
