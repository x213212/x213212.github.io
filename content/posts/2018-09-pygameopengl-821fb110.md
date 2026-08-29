---
title: "Pygame_openGL(第一人稱視角)"
date: "2018-09-07T02:09:00.001+08:00"
updated: "2019-09-13T08:53:13.629+08:00"
permalink: "/2018/09/pygameopengl.html"
original_url: "https://x8795278.blogspot.com/2018/09/pygameopengl.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5685245306657703089"
tags: ["Python", "Tutorial", "Projects"]
layout: post
---

## Pygame_openGL(第一人稱視角)

## ---

  

[![](https://i.imgur.com/IinMm86.gif)](https://i.imgur.com/IinMm86.gif)
  

修正後順便來鋪個地板，在移動方面可能還需要再更動
  

目前只有擺頭而已，移動的話可能還需要再研究，
找第一人稱視角真久，原理竟然是到線性代數最後幾章
[opengl-tutorial](http://www.opengl-tutorial.org/cn/beginners-tutorials/tutorial-6-keyboard-and-mouse/)參考公式
我們先來上扣以後再來理解原理
會覺得閃爍是版本問題沒有雙衝緩衝，pyopengl第一人稱資源少的可憐，恐怖fps?!
還是我沒找到?
#  if( buff==False):
#     buff= True
#     mypos_buff=direction
這邊我以為我腦袋有問題，看能不能避開閃爍，結果還是不行，y軸上下會增加卡頓，
  

  

```html
<script src="https://gist.github.com/x213212/dfada8c62300db5983bbf77b8f53a5f6.js"></script>
```

  

  

  
## 緩衝區問題?

## ---

glutSwapBuffers()
其實這一行就可以解決了，我比較衰挑到3.6版，none沒有這個函數?
  

移動問題
