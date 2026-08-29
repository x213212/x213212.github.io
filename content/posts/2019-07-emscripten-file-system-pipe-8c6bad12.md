---
title: "WebAssembly 編譯ffmpeg 新增入口點和 web workweb work簡單設定 (二)"
date: "2019-07-14T22:46:00.000+08:00"
updated: "2019-08-06T22:02:42.430+08:00"
permalink: "/2019/07/emscripten-file-system-pipe.html"
original_url: "https://x8795278.blogspot.com/2019/07/emscripten-file-system-pipe.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-16157756253380543"
tags: ["Tutorial", "WebAssembly"]
layout: post
---

實現串流這部分看來是不行了，雖然後面有編譯成功， [emscripten file system](https://emscripten.org/docs/api_reference/Filesystem-API.html)  

  

嘗試用pipe 流，去做處理也是失敗，最後只完成了 轉檔，部分指令可能失效?，  

  

可能有關於配置的關係，SharedArrayBuffer，透過mediarecorder 去抓blob 再轉成  

  

ArrayBuffer 去讓ffmpeg.js 讀也是失敗，嘖嘖，可能功力不太夠，可能要在研究一番 又要停止更新這主題了xd  

  

<https://github.com/x213212/build_ffmpeg.js>  

  

[![](https://camo.githubusercontent.com/8633ea6ea2c743c30f7d5b2a664413a745078245/68747470733a2f2f692e696d6775722e636f6d2f795546527641452e706e67)](https://camo.githubusercontent.com/8633ea6ea2c743c30f7d5b2a664413a745078245/68747470733a2f2f692e696d6775722e636f6d2f795546527641452e706e67)[![](https://camo.githubusercontent.com/cbd2d3148aa766989aa711ccd58c9fbc97b8c5c1/68747470733a2f2f692e696d6775722e636f6d2f376f6553434c7a2e706e67)](https://camo.githubusercontent.com/cbd2d3148aa766989aa711ccd58c9fbc97b8c5c1/68747470733a2f2f692e696d6775722e636f6d2f376f6553434c7a2e706e67)
# version

- emcc v1.38.38
- ffmpeg lest version

[ffmpeg](https://github.com/FFmpeg/FFmpeg.git)
# script

```
此版本編譯為
CPPFLAGS="-D_POSIX_C_SOURCE=200112 -D_XOPEN_SOURCE=600" \
emconfigure ./configure --cc="emcc" \
--prefix=$(pwd)/../dist --enable-cross-compile --target-os=none --arch=x86_64 \
--cpu=generic --disable-ffplay --disable-ffprobe  \
--disable-asm --disable-doc --disable-devices --disable-pthreads \
--disable-w32threads  --disable-hwaccels \
--disable-parsers --disable-bsfs --disable-debug --disable-protocols \
--disable-indevs --disable-outdevs --enable-protocol=file --enable-protocol=rtmp --enable-protocol=pipe \
--enable-network --enable-protocol=tcp --enable-demuxer=rtsp --enable-decoder=h264 --enable-encoder=libx264 \
--enable-demuxer=flv 

emcc -s ASSERTIONS=1 -s VERBOSE=1 -s TOTAL_MEMORY=33554432 \
-s ALLOW_MEMORY_GROWTH=1 -s WASM=1 -O2 -v ffmpeg.bc \
-o ../ffmpeg.js --pre-js ./pre.js --post-js ./post.js
```
```

```
````
add some html index.html
```
<html>
<p>ffmpeg.js</p>
<input id="file-input" type="file" />
</html>
<script>

var worker = new Worker('worker.js');
var inputElement = document.getElementById("file-input");
inputElement.addEventListener("change", handleFiles, false);
function handleFiles() {
var fileList = this.files; 
console.log(fileList)
worker.postMessage(fileList);
}
</script>
```
worker.js
```
self.importScripts('ffmpeg.js');

onmessage = function(e) {
  console.log('ffmpeg_run', ffmpeg_run);
  var files = e.data;
  console.log(files);
  ffmpeg_run({
   // arguments: ['-i', 'https://gw.alicdn.com/bao/uploaded/LB1l2iXISzqK1RjSZFjXXblCFXa.mp4?file=LB1l2iXISzqK1RjSZFjXXblCFXa.mp4', '-b:v', '64k', '-bufsize', '64k', '-vf', 'showinfo', '-strict', '-2', 'out.mp4'],
  // arguments: ['-i', '/input/' + files[0].name  'out.mp4'],
   arguments: ['-version'],
    //files: files,
  }, function(results) {
    console.log('result',results);
   // self.postMessage(results[0].data, [results[0].data]);
  });

}
```
enjoy~
````
