---
title: "打造一個多人串流系統 html5 publish to adobe media server ? part4"
date: "2019-01-13T20:27:00.001+08:00"
updated: "2019-01-16T13:32:30.093+08:00"
permalink: "/2019/01/html5-publish-to-adobe-media-server.html"
original_url: "https://x8795278.blogspot.com/2019/01/html5-publish-to-adobe-media-server.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-1919809933605114071"
tags: ["adobe media server", "ffmpeg", "html5", "Node.js", "rtmp", "Tutorial"]
layout: post
---

[![](https://i.imgur.com/74gKZyZ.png)](https://i.imgur.com/74gKZyZ.png)

推送到了html5  瀏覽器又怎樣呢，我們的客戶端，假設也必須要，傳輸自己的畫面自server 怎麼辦呢?  找了一下子發現又有 solution 可以用了 <https://github.com/chenxiaoqino/getusermedia-to-rtmp>

## Install ffmpeg

##

[![](https://i.imgur.com/HzUbO0Z.png)](https://i.imgur.com/HzUbO0Z.png)

[![](https://i.imgur.com/7qJW6Uv.png)](https://i.imgur.com/7qJW6Uv.png)

加入系統變數 c:\ffmpeg\bin

[![](https://i.imgur.com/zKYksQX.png)](https://i.imgur.com/zKYksQX.png)

Cmd  >>>ffmpeg –version

[![](https://i.imgur.com/cjBpfIv.png)](https://i.imgur.com/cjBpfIv.png)

Install successful!

## Node.js install

##

##

[![](https://i.imgur.com/VOACF3m.png)](https://i.imgur.com/VOACF3m.png)

[![](https://i.imgur.com/XhIy4Np.png)](https://i.imgur.com/XhIy4Np.png)

一直下一步~ Cmd  >>> node -v

[![](https://i.imgur.com/vGC66Ji.png)](https://i.imgur.com/vGC66Ji.png)

## Clone github download getusermedia-to-rtmp

##

##

我們的主角 <https://github.com/chenxiaoqino/getusermedia-to-rtmp>

[![](https://i.imgur.com/vq6QSfM.png)](https://i.imgur.com/vq6QSfM.png)

必須切去該路徑 然後 cmd 輸入 npm install

[![](https://i.imgur.com/pq44I9i.png)](https://i.imgur.com/pq44I9i.png)

[![](https://i.imgur.com/IQQbqKt.png)](https://i.imgur.com/IQQbqKt.png)

## ffmpeg param setting

##

##

## --- Path: C:\Users\x2132\Desktop\nodejs\getusermedia-to-rtmp-master\server.js [![](https://i.imgur.com/qISFsCH.png)](https://i.imgur.com/qISFsCH.png)

```javascript

ffmpeg 參數設定
		var ops=[
			'-i','-',
			'-c:v', 'libx264', '-preset', 'veryfast', '-tune', 'zerolatency',
			'-an', //TODO: give up audio for now...
			//'-async', '1', 
			'-filter_complex', 'aresample=44100', //necessary for trunked streaming?
			//'-strict', 'experimental', '-c:a', 'aac', '-b:a', '128k',
			'-bufsize', '1000',
			'-f', 'flv', socket._rtmpDestination
		];
```

run nodejs server!

##

##

node server.js

[![](https://i.imgur.com/a2EZGzT.png)](https://i.imgur.com/a2EZGzT.png)

[![](https://i.imgur.com/ehsFfiX.png)](https://i.imgur.com/ehsFfiX.png)

## Html5 Rtmp server location

##

##

rtmp://127.0.0.1:1935/live/test 注意後面跟 flex 版本一樣必須要指定

[![](https://i.imgur.com/tQAi0uq.png)](https://i.imgur.com/tQAi0uq.png)

確實收到數據了!

[![](https://i.imgur.com/eX2963e.png)](https://i.imgur.com/eX2963e.png)

檢查 flex 端是否可以撥放

## [![](https://i.imgur.com/U52WEuD.png)](https://i.imgur.com/U52WEuD.png) 成功!，終於可以交貨了
