---
title: "WebAssembly ffmpeg.js 透過 stdio async 讀入檔案 (驗證?"
date: "2019-10-21T04:12:00.003+08:00"
updated: "2019-11-01T08:47:08.352+08:00"
permalink: "/2019/10/webassembly-ffmpegjs-stdio-async.html"
original_url: "https://x8795278.blogspot.com/2019/10/webassembly-ffmpegjs-stdio-async.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5973009825186414697"
tags: ["ffmpeg", "Tutorial", "WebAssembly"]
layout: post
---

![](https://i.imgur.com/IFuDdrU.png)

# 在與來自烏克蘭github大大來信後，他推薦我用WebRTC方式，最後進行串流討論後得出以下結論 ![](https://i.imgur.com/9s1c3Pi.png)

我覺得WebRTC預設編碼的x264,本身好像也是p2p??,雖然延遲性和安全性提高了但是在應付大規模場景下應該不適合，
别迷信 WebRtc，WebRtc只适合小范围（8人以内）音视频会议，不适合做直播：  

**1. 视频部分：vpx的编码器太弱，专利原因不能用264，做的好的都要自己改264/265代码才行。**  

**2. 音频部分：音频只适合人声编码，对音乐和其他非人声的效果很糟糕。**  

**3. 网络部分：对国内各种奇葩网络适应性太低，网络糟糕点或者人多点就卡。**  

**4. 信号处理：同时用过 GIPS和 WebRTC 进行对比，可以肯定目前开源的代码是GIPS阉割过的。**  

**5. 使用规模：10人以内使用，超过10人就挂了，WebEx方案支持的人数都比 RTC 强。**
作者：韦易笑  

链接：https://www.zhihu.com/question/25497090/answer/72397450  

来源：知乎  

著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
在我詢問他是否可以通過我在上回的方向去實作他說是可行的(基於商業客戶向他買解決方案)不能透漏，在分支
<https://github.com/Kukunin/ffmpeg.js/commit/acca0c151807d88bddd73e885a183750bd793246#diff-b67911656ef5d18c4ae36cb6741b7965R347>
提到這個部分大概就可以解決我所說的問題，再來就是猜猜看怎麼處理了
  

**在ffmpeg 轉成 ffmpeg.js 他在把 ffmpeg 裡面的 file 和 tcp 的函數裡面的意外中斷的片段程式碼**  

都給 remark掉 這樣在 運行 async stdio就不會意外中止 ( 或許就可以 向他說的 透過 getUserMedia 去 讀取資料這樣我們只要把 那些blob 轉成 file 跟原先一樣不用動，在結合上一個文章就可以 達到 用網路傳遞數據給後端 推送給 其他串流伺服器了前端編碼就完成囉!
再來就是 要再編譯的參數 EMTERPRETIFY_ASYNC=1 給打開
他fork出來額外新增的內容應該就是這些

提到他說可以從這方向找尋到我要的解答所以確定可以用getUesrMedia去實作還有以下要問題要解決  

第一個就是blob跟輸出檔案問題一樣超過70mb可能會出現 記憶體崩潰或者溢位導致瀏覽器crash  

可能要查閱 wasm fs 虛擬檔案映射那邊  

第二個則是檔案的讀入方式
他提問我為什麼要用自定義ffmpeg 去做 影音上的串流，目前不是有 WebRTC可以達成目標了嗎  

我當初想做是因為可以實現任意編碼的問題和可以隨意推送去任意 RTMP串流伺服器，再者就是 目前大部分主流是RTMP 又有豐富的 CDN 當然 WebRTC也可以實作CDN，國外網友好像不怎麼贊成 好像不太怎麼穩定)  

上述內容可能需要 重新compliter 整個 ffmpeg.js才能實證了，又是一個17小時?，有空再來玩 (話說 是不是該刷leetcode了
