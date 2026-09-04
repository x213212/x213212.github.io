---
title: "http mixed content 解決"
date: "2019-02-26T21:10:00.000+08:00"
updated: "2019-06-22T20:02:34.154+08:00"
permalink: "/2019/02/http-mixed-content.html"
original_url: "https://x8795278.blogspot.com/2019/02/http-mixed-content.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-886511568397916856"
tags: ["adobe media server", "html5", "livego", "Tutorial"]
layout: post
---

[![](https://i.imgur.com/skhMmxQ.png)](https://i.imgur.com/skhMmxQ.png)
http mixed content 混和內容警告!!!!
## ---

公司明年春晚在北海道 ∼  太神了 冷靜回歸正題  

在上一篇在架設完，從adobe media server apache 的flv.js播放器 要改架設為 https 的問題，變成了以下問題在已經，https 可以正常進行推流後，在相同網域進行推播可以看到
[![](https://i.imgur.com/Lsrxywz.png)](https://i.imgur.com/Lsrxywz.png)[![](https://i.imgur.com/WMlL4KB.png)](https://i.imgur.com/WMlL4KB.png)

| 奇怪這邊好好的，在切換成flv  [![](https://i.imgur.com/apVyH14.png)](https://i.imgur.com/apVyH14.png) |
| --- |
| 新增說明文字 |

  

原因就是混和內容，在 [混合內容](https://developer.mozilla.org/zh-TW/docs/Web/Security/Mixed_content)，自己去查~，反正解決方案就是
一 基於 livego 伺服器轉發問題，我們可以得知 在https 的rtmp推播的情況下又在下一層的目錄，裡面的 flv.js 並不能播放 http 網址的東東，所以呢我找了很多，隧道? proxy 正向代理，反向代理?
[![](https://i.imgur.com/cVg5E3w.png)](https://i.imgur.com/cVg5E3w.png)
最後選擇的是 proxy，再找一個吧 [node-http-proxy](https://github.com/nodejitsu/node-http-proxy) 話說為什麼要寫那麼複雜
我們來精簡版，94這麼簡單  

[![](https://i.imgur.com/h6oqNan.png)](https://i.imgur.com/h6oqNan.png)
  

```javascript
var https = require('https'),
    httpProxy = require('http-proxy');
var fs = require('fs');
//
// Create a proxy server with latency
//
var proxy = httpProxy.createProxyServer();

//
// Create your server that makes an operation that waits a while
// and then proxies the request
//
httpProxy.createServer( {
 ssl: {
 key: fs.readFileSync('abels-key.pem'),
  cert: fs.readFileSync('abels-cert.pem')
  },
  target: 'http://localhost:7001',
  secure: false
  
}).listen(444);
```
