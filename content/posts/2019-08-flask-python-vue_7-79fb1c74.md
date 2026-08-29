---
title: "flask python vue 股票回測 (二) 隨機森林演算法"
date: "2019-08-07T13:52:00.001+08:00"
updated: "2019-10-11T02:38:02.176+08:00"
permalink: "/2019/08/flask-python-vue_7.html"
original_url: "https://x8795278.blogspot.com/2019/08/flask-python-vue_7.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5266281503147953722"
tags: ["flask", "Python", "Stock", "Tutorial", "Vue.js"]
layout: post
---

# 隨機森林演算法

翻到以前的code來補齊一下，新增隨機森林演算法  

預測與權重誰比較重要  

在漲跌來看，在一股價移動平均線5天來看最可以影響漲跌，  

在股票不只股票，像是天氣下雨，濕度.....都可以使用隨機森林找到最有相關性的特徵!?  

![](https://i.imgur.com/E4rZMl2.png)

  

在判斷 當天和隔天的狀況下可以經由判斷前一天的close 收盤價  

新增一個 新的一個特徵點 label假設為漲跌則設為1 否則為0  

![](https://i.imgur.com/xbYc7Ak.png)

  

  

```html
<script src="https://gist.github.com/x213212/576694efec20b1860005d8cd4e7f09a5.js"></script>
```
