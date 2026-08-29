---
title: "PyOpengl Cube_control"
date: "2018-08-31T02:42:00.000+08:00"
updated: "2019-09-13T08:53:13.688+08:00"
permalink: "/2018/08/pyopengl-cubecontrol.html"
original_url: "https://x8795278.blogspot.com/2018/08/pyopengl-cubecontrol.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-9119680441061874015"
tags: ["GameMaker", "Python", "Tutorial"]
layout: post
---

## Pygame_openGL(初)

## ---

該怎麼去用Python去繪圖一個3D世界呢，終於來到這一天用CODE繪製3D畫面
[pythonprogramming.net](https://pythonprogramming.net/opengl-pyopengl-python-pygame-tutorial/)
先照哥的code跑一遍
[![](https://i.imgur.com/GgaIg7V.gif)](https://i.imgur.com/GgaIg7V.gif)
  

  

[![](https://pythonprogramming.net/static/images/pyopengl/openGL-cube-with-Python-and-PyOpenGL-tutorial.gif)](https://pythonprogramming.net/static/images/pyopengl/openGL-cube-with-Python-and-PyOpenGL-tutorial.gif)
得到哥的畫面呢，假設實現minecraft創世神有可能嗎之類的
就開始找到目前為止的資料吧
初步構想呢我想為這個遊戲新增什麼東西呢
今天共新增了
這些在網路上超少，或許我對opengl關鍵字不夠熟悉關係，
不過還是可以透過其他語言控制opengl的code從其中找出關聯性  

貼圖紋理和為這個世界加入音效，和顯示文字之類的東東
直接來上代碼吧
改裝後!用滾輪來調控速度
  
## 預計

## ---

徒手打造一個mmorpg，所以呢我們接下來我們可以來產生一個地面，讓腳色在cube行走，已經掌握貼圖後，我們可以再加入其他更多模型3dsmax骨架之類的，算了扯遠了，話說在座標還分很多種世界座標，視窗座標等等
[終於了解數學不好不能寫遊戲惹](https://blog.csdn.net/sac761/article/details/52179585)，又不是說要編寫一個引擎(或許可能?!)，光源阿之類的粒子特效，總而言之，有這個demo我們只要再加入碰撞效果，創建地圖的話我們就可以打造一個類似mmorpg，day1慢慢啃
```html
<script src="https://gist.github.com/x213212/b5c3576962cd98cde14977f31cb1e404.js"></script>
```

  

  

[![](https://i.imgur.com/j83qCbW.png)](https://i.imgur.com/j83qCbW.png)
個別物件進行翻轉的時候應該用投影矩陣類似的東西，有趣的是發現原來遊戲世界的周圍  

是可能用  

[![](https://i.imgur.com/ppCUPHw.png)](https://i.imgur.com/ppCUPHw.png)
[![](https://i.imgur.com/P75fCg9.png)](https://i.imgur.com/P75fCg9.png)
持續修練，爆肝QQ
  
## 參考

## ---

[http://blawat2015.no-ip.com/~mieki256/diary/201305.html](https://www.blogger.com/goog_2073707958)
[https://www.cs.pu.edu.tw/~tsay/course/cg/tutorial/install.html](https://www.blogger.com/goog_2073707958)  

[http://user.xmission.com/~nate/glut.html](https://www.blogger.com/goog_2073707958)  

[https://github.com/stef/swram-opengl/blob/master/swram-opengl.py](https://www.blogger.com/goog_2073707958)  

[https://stackoverflow.com/questions/46796459/how-to-install-glut-on-anaconda-on-windows](https://www.blogger.com/goog_2073707958)  

<https://github.com/elisehuard/game-in-haskell/issues/1>  

<https://blog.csdn.net/wangdingqiaoit/article/details/52506893>
