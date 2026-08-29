---
title: "氣浮球 實作"
date: "2018-08-25T14:14:00.000+08:00"
updated: "2019-10-06T22:46:39.081+08:00"
permalink: "/2018/08/x-ylcd2d-main.html"
original_url: "https://x8795278.blogspot.com/2018/08/x-ylcd2d-main.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-1597631945059229784"
tags: ["Embedded", "GameMaker", "Tutorial", "Projects"]
layout: post
---

# 氣浮球 嵌入式構思

這次我們要結合的觸控螢幕x y軸和lcd繪圖的控制做出2D氣浮球對打  

![](https://i.imgur.com/yNVtR3A.png)

遊戲方法想辦法進入對手的得分區  

![](https://i.imgur.com/HClMJDz.png)

預期功能要實作的功能是
牆壁反射和得分區和腳色移動的球反射
[![](https://i.imgur.com/Nal1r33.jpg)](https://i.imgur.com/Nal1r33.jpg)
  

時間允許的會可能會增加得分還是記分板
[![](https://i.imgur.com/IdHmP8g.jpg)](https://i.imgur.com/IdHmP8g.jpg)
  

```html
<script src="https://gist.github.com/x213212/2f12e7d744f7b79f2a6b5843a6f6b3b7.js"></script>
```
