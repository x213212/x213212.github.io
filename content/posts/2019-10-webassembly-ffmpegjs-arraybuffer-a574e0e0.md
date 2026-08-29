---
title: "WebAssembly 修改 ffmpeg.js 在運行時輸出 檔案 ArrayBuffer (三)"
date: "2019-10-16T17:19:00.000+08:00"
updated: "2019-10-17T00:50:39.122+08:00"
permalink: "/2019/10/webassembly-ffmpegjs-arraybuffer.html"
original_url: "https://x8795278.blogspot.com/2019/10/webassembly-ffmpegjs-arraybuffer.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5027153694518944272"
tags: ["Tutorial", "WebAssembly"]
layout: post
---

今天要解決的問題是，之前我們遇到的，除非 wasm 權限越開越大，  

不然就是 ffmpeg output 可以輸出至 其他 通訊 tcp/rtmp
那上次研究的結果還會卡到 既然是在 web worker 裡面那我們可能還會面臨 chrome 的
https/http 協議不能混用
  

這邊的話想了一下有沒有能在程式執行中 進行 output呢?  

所以我覺得能不能在這兩個函數內找到一些結果，果然有發現  

開始初始化前
Module[“preRun”]
結束後輸出
Module[“postRun”]

![](https://i.imgur.com/z4dBLjg.png)

  

```html
<script src="https://gist.github.com/x213212/48fd9c141192910ede2e085acd0b1343.js"></script>
```

也就是大大們卡很久的檔案映射問題?  

之前想為什麼輸出能掛載在虛擬機上，既然是虛擬機，我跑ffmpeg 的時候應該就可以讀到  

掛載的檔案那麼是不是可以在ffmpeg run 的時候就可以取的檔案 buffer?  

![](https://i.imgur.com/1EtywTi.png)

  

實驗結果是可以的就是在檔案輸出 stdout 的時候去呼叫原本我們在 postRun的那邊結束後呼叫的時候才會產生blob檔案只要修改這邊就可以了  

  

再參考論壇等等有發現已經有可以從stdin 前端"解碼"的範例了，也可以讀 串流  

<https://cloud.tencent.com/developer/article/1453425>  

<https://github.com/sonysuqin/WasmVideoPlayer>  

至於讀出呢，可以透過這些方式去 回傳 給 js 去做處理

接下來呢，後續可能會有什麼玩法?
目前的話可以，因為不同的電腦cpu呼叫 ffmpeg 編碼的話速率不同，一次解碼的量也會不同所以我們buffer的偏移量我覺得應該也會不同，至於一次要偏移有空下次研究，假設這個問題可以解決，返回函數到，js後我們可以或許我們可以做 ArrayBuffer 合併 串流 那我們就可以完成前端 "編碼"的問題，那我們之前要實作的，就只差通訊協定了 可以透過 websocket 進行傳輸，  

  

我們目前就已經解決我之前做的範例透過 chrome mediarecoder 在傳輸給 socket.io 先進行 畫面上的錄製再傳送給後端 nodejs， nodejs 在 fork 很多個 ffmpeg 在進行推畫面上的重組送給其他串流伺服器。  

  

現在我們是 先 透過  chrome mediarecoder 進行畫面上的 傳輸，再透過走 TCP 或 udp (謎樣方式串流)
輸入至位於webwork 裡面的 ffmpeg wasm 在這邊 執行 用戶端編碼再透過我的方式去把檔案的 ArrayBuffer，看是要在前端進行js 編碼上的處理還是  還是透過 websocket傳輸至後端處理再推送給其他串流伺服器。  

  

這邊可以看到我們已經大大的減少 伺服器端幫我們做的事情，這樣我們是不是更貼近 無插件進行 串流了呢(?  

  

  

在2020 chrome 要徹底廢除掉 flash 的話，那我們就可以實現，在前端不加掛任何插件的方式下
透過chrome mediarecord 進行 攝像頭的讀入，再根據我們剛剛的方式，再配合偏移量的演算法寫作，應該就可以達到 無插件 進行 前端 推流，wasm 在繼續進步下去或許效能會越來越強，adobe flash 可能就要掰了哈哈
