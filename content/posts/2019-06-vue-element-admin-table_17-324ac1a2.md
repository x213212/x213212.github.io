---
title: "Vue element admin Table 客製化表格(四)"
date: "2019-06-17T22:09:00.001+08:00"
updated: "2019-06-22T20:02:34.043+08:00"
permalink: "/2019/06/vue-element-admin-table_17.html"
original_url: "https://x8795278.blogspot.com/2019/06/vue-element-admin-table_17.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-7184494244842776504"
tags: ["spring boot", "Tutorial", "Vue.js"]
layout: post
---

# Element ui table

新增了一堆功能，在element 原生官方的table 並沒有寫好在操縱大量dom的時候會非常的lag，後期再來進行維護，不過發現了另一個寫好的table
<https://github.com/xuliangzhan/vxe-table>
[![](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhTCEbB9aB5C2onWR2-jIdThxr6XS5tsoEq51Wuaird3Iu6ANa0wzMUDKddraMdQd28-IB9LosciBvpFHIQbA8MNZLMasf1bCUdGsOdixUutGBRvZvK4-sp2N2e2h_fSXxGNB8KKsFf3xk/s1600/table.png)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhTCEbB9aB5C2onWR2-jIdThxr6XS5tsoEq51Wuaird3Iu6ANa0wzMUDKddraMdQd28-IB9LosciBvpFHIQbA8MNZLMasf1bCUdGsOdixUutGBRvZvK4-sp2N2e2h_fSXxGNB8KKsFf3xk/s1600/table.png)
  

  

這個issue 好像蠻久的 大概兩年
<https://github.com/ElemeFE/element/issues/6089>
  

可以考慮?
  

  

**虛擬滾動 or 滾動加載**
<https://zhuanlan.zhihu.com/p/53455289>
[![](https://pic4.zhimg.com/v2-687d84dca67e9e398bd44705c34d661b_r.jpg)](https://pic4.zhimg.com/v2-687d84dca67e9e398bd44705c34d661b_r.jpg)
  

我寫的code是寫類似於 滾動加載，本來想進行優化的...底子不夠深再看一陣子
  

  

```html
<script src="https://gist.github.com/x213212/21e175e50c10abb6b9e3bd92fe5656d3.js"></script>
```
