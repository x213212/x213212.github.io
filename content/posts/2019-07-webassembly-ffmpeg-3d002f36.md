---
title: "WebAssembly 編譯ffmpeg 進行串流(構想與實現?"
date: "2019-07-13T20:06:00.001+08:00"
updated: "2019-11-04T16:27:18.754+08:00"
permalink: "/2019/07/webassembly-ffmpeg.html"
original_url: "https://x8795278.blogspot.com/2019/07/webassembly-ffmpeg.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5109012571830160067"
tags: ["Tutorial", "WebAssembly"]
layout: post
---

[![](https://miro.medium.com/max/3200/1*f__SEWRvsNwt4B-u8-85Bw.png)](https://miro.medium.com/max/3200/1*f__SEWRvsNwt4B-u8-85Bw.png)
上一個系列要來暫停了，來進入回憶…
在進公司打算一開始做串流 sever 的時候，怕出糗本來想用wasm 的來做前端解碼，我則選擇了用 [socket.io](http://socket.io/) 傳送畫面至後端 再交給 ffmpeg 進行編碼，
真的不幸，高軟停電的時候把其中一台 串流 server 虛擬機毀損了…，
近期內又要再搭建一台， 最近比較有空閒，大致上網頁的規畫已經完成差不多了
又要切換成 研究模式 來小研究一下技術，在串流這邊這部分還沒有看過有人這樣玩的，或許可以在 github上面刷星星了xd，說要追逐到目前的技術的化大概跟現在的技術差兩年吧…。
近期內我們來完成 以前想要做的事情吧。
[使用WebAssembly+FFmpeg实现前端视频转码(上)](https://zhuanlan.zhihu.com/p/27874253)  

[使用WebAssembly+FFmpeg实现前端视频转码(下)](https://zhuanlan.zhihu.com/p/27910351)
其中的科普我就不多作介紹了  

最近一直在猶豫 是否只要把相關連結 貼出來，然後 我們來將實作 所遇到的 bug 再詳細解決，是否 整體版面會比較乾淨?
# WebAssembly 是什么

这里不阐述太多了，知乎上各种科普帖子都有，基本上理解成浏览器标准实现的一个web汇编格式，使得可以将llvm转成可以在web上运行的代码来加快运行速度，这里主要介绍从c/c++/rust等语言编译到wasm的一些工具
# Emscripten & asm.js

Emscripten: An LLVM-to-JavaScript Compiler
Asm.js an extraordinarily optimizable, low-level subset of JavaScript
这是wasm过程中2个比较重要的工具，官网链接在上：
# [Emscripte](https://emscripten.org/docs/getting_started/downloads.html):

wasm的编译器，根据上面的介绍，这是一个LLVM到js的编译器。咱对于编译原理这些底层的东西了解也不太多，简单理解的话LLVM就是一个编译的中间状态，使用llvm-gcc或者clang这些编译工具可以将c/c  

编译到LLVM bitcode这样一个中间代码的状态, 同样类似像rust的语言也可以编译到LLVM。有了LLVM bitcode，就可以使用Emscripten这个工具来将其编译成更底层的汇编js代码。  

那么更底层的汇编js代码是啥，早期在wasm还没有实现之前，汇编js的实现就是Asm.js（字如其名。。）。asm.js的核心功能就是模拟一个汇编语言的运行环境，通过一个大的UintArray数组来模拟机器内存，然后通过js实现各种汇编指令来对这个虚拟的内存(UintArray对象)进行操作。  

通过上面这2个步骤，我们先是把c/c通过编译器编译到LLVM，再利用emscripten将LLVM编译成asm.js，当我们在运行这段asm.js代码的时候，就会省去大量的解释器开销，相当于直接使用汇编代码一样来直接操作内存空间运行。
但是asm.js实现的汇编环境毕竟还是基于js的，在性能上还是不能完全满意，这个时候，WebAssebmly就应运而生了，由浏览器来实现汇编环境，规定好webassembly的汇编格式，使得性能进一步提示
# 編譯ffmpeg to wasm

```
git clone https://github.com/juj/emsdk && cd emsdk 
./emsdk install sdk-incoming-64bit binaryen-master-64bit 
./emsdk activate sdk-incoming-64bit binaryen-master-64bit
. ./emsdk_env.sh
```
需要一段時間...  

![](https://i.imgur.com/HbFCNX6.png)

  

![](https://i.imgur.com/widm9l1.png)

  

就這一段 我們的 centos 很詭異，  

我們遇到了這個 bug，這個原因找了很久，是不是官方相關套件沒裝呢還是編譯器問題，  

跑去官網看要怎樣編譯原生的ffmpeg  

<https://trac.ffmpeg.org/wiki/CompilationGuide/Centos>
```
# 首先，从github等地方获取ffmpeg的源代码
git clone https://github.com/FFmpeg/FFmpeg
cd FFmpeg

# 开始configure
# 这里的参数参考自videoconverter.js，其中注意需要额外带上下面第一行的CPPFLAGS
# 否则不能在最新的emcripten下编译通过
# 这里通过--cc="emcc"来指定编译器为emcc，emcc会调用clang来将target设置成LLVM
CPPFLAGS="-D_POSIX_C_SOURCE=200112 -D_XOPEN_SOURCE=600" \
emconfigure ./configure --cc="emcc" \
--prefix=$(pwd)/../dist --enable-cross-compile --target-os=none --arch=x86_64 \
--cpu=generic --disable-ffplay --disable-ffprobe --disable-ffserver \
--disable-asm --disable-doc --disable-devices --disable-pthreads \
--disable-w32threads --disable-network --disable-hwaccels \
--disable-parsers --disable-bsfs --disable-debug --disable-protocols \
--disable-indevs --disable-outdevs --enable-protocol=file
```
```
make # 記得開始編譯
```
  

![](https://i.imgur.com/W1gjBbx.png)

# centos 7 gcc 升級

[https://www.booolen.com/post/20190403_centos下glibcxx_3.4.20的问题/](https://www.booolen.com/post/20190403_centos%E4%B8%8Bglibcxx_3.4.20%E7%9A%84%E9%97%AE%E9%A2%98/)  

請按照他的版本完成升級到 7.2  

![](https://i.imgur.com/tqEsrsg.png)

我安裝gcc 要破半天?(冏，難怪預設不讓使用者去官方下載 xd  

可能虛擬機 cpu 核心分配太少 還是記憶體不太夠  

![](https://i.imgur.com/UcaTiCE.png)

# centos 7 版本切換 gcc

<https://www.cnblogs.com/dj0325/p/8481092.html>
```
scl --list
scl enable devtoolset-7 bash
```
<https://blog.csdn.net/xueyushenzhou/article/details/82856860>  

![](https://i.imgur.com/ktlrnBU.png)

這樣大致上就可以完成編譯囉，太久沒交叉編譯可能會deubg到死。
```
[root@localhost lib64]# mv libstdc++.so.6 libstdc++.so.6bck
[root@localhost lib64]# ln -s libstdc++.so.6.0.24 libstdc++.so.6
[root@localhost lib64]# strings /usr/lib64/libstdc++.so.6 | grep GLIBC
```

![](https://i.imgur.com/ImDzjy5.png)

  

重新指向  

nice  
# cmake install

![](https://i.imgur.com/u6tdgLE.png)

  

<https://blog.csdn.net/cloudeagle_bupt/article/details/82498255>  

![](https://i.imgur.com/cTcyy03.png)

  

請升級到 3.43 以上更高版本  

<http://jotmynotes.blogspot.com/2016/10/updating-cmake-from-2811-to-362-or.html>  

![](https://i.imgur.com/8IrNTVp.png)

  

安裝完成!
# ffmpeg.js

經過18小時第一個 編譯終於要開始了…

![](https://i.imgur.com/C5t0IRP.png)

![](https://i.imgur.com/iQGuhnT.png)

再撐一下 容量快報了…  

![](https://i.imgur.com/zoY5yB2.png)

今天先這樣 明天大概就看的到 ffmpeg.js 了  

後面大致架構應該是， 從 其他分支下手 service worker 加掛一個  

[socket.io](http://socket.io/) 再透過 io 進行 畫面傳輸，再配合 hmtl5 的函數  

MediaRecorder，恩恩(構思很好，希望可以編譯成功，交叉編譯真的會吐血。
隔天了，恩不錯  

![](https://i.imgur.com/7FLEgKr.png)

```
make
```
在下一個指令!!!  

![](https://i.imgur.com/4iGe0Mz.png)

  

誕生…  

![](https://i.imgur.com/w13jDtO.png)

  

![](https://i.imgur.com/Colvmec.png)

<https://github.com/disoul/videoconverter.js/blob/master/build/ffmpeg_pre.js>  

<https://github.com/disoul/videoconverter.js/blob/master/build/ffmpeg_post.js>  

这里放出我最终自己使用pre.js和post.js代码
<https://github.com/disoul/videoconverter.js/blob/master/build/ffmpeg_pre.js>  

<https://github.com/disoul/videoconverter.js/blob/master/build/ffmpeg_post.js>  

好啦好啦，扯了这么多，终于万事俱备可以愉快的开始最后一步编译啦
# Final Battle 編譯LLVM到WebAssmbly

这里使用的命令依旧是emcc，但是注意此时emcc的输入为LLVM bitcode，它将会调用emscriptem来将其编译到js (和第一步emcc的行为不同，因为输入格式不同，target也会不同)
```
# 这里的ffmpeg是上一步编译输出的LLVM bitcode
cp ffmpeg ffmpeg.bc

# 最终的输出是 -o 指定的，这些 -s 参数的意义可以从emcc的文档中找到
# 这里打开了ALLOW_MEMORY_GROWTH是因为在移动端测试下会遇到内存(wasm/asm.js的虚拟内存)
# 不够的情况，默认内存大小是TOTAL_MEMORY指定的
# 设置WASM=1就会编译到WebAssembly,默认编译到asm.js
emcc -s ASSERTIONS=1 -s VERBOSE=1 -s TOTAL_MEMORY=33554432 \
-s ALLOW_MEMORY_GROWTH=1 -s WASM=1 -O2 -v ffmpeg.bc \
-o ../ffmpeg.js --pre-js ../ffmpeg_pre.js --post-js ../ffmpeg_post.js
```
我真的…淦  

![](https://i.imgur.com/jTwT5vt.png)

  

沒空間我來想想要去哪裡生  

[https://webcache.googleusercontent.com/search?q=cache:0uf3Xfr5a1AJ:https://www.novicepq.com/2018/06/07/%E6%B8%85%E7%90%86centos6%E6%88%96centos7%E5%9E%83%E5%9C%BE%E6%96%87%E4%BB%B6%E7%9A%84%E5%91%BD%E4%BB%A4%E8%A1%8C/+&cd=2&hl=zh-TW&ct=clnk&gl=tw](https://webcache.googleusercontent.com/search?q=cache:0uf3Xfr5a1AJ:https://www.novicepq.com/2018/06/07/%25E6%25B8%2585%25E7%2590%2586centos6%25E6%2588%2596centos7%25E5%259E%2583%25E5%259C%25BE%25E6%2596%2587%25E4%25BB%25B6%25E7%259A%2584%25E5%2591%25BD%25E4%25BB%25A4%25E8%25A1%258C/+&cd=2&hl=zh-TW&ct=clnk&gl=tw)  

![](https://i.imgur.com/sxZo0SQ.png)

  

不錯不錯順便複習一下指令
```
emcc ffmpeg.bc -o ffmpeg.html -s TOTAL_MEMORY=33554432
```
隔天， 加大虛擬機 記憶體編譯就過了…

![](https://i.imgur.com/q33aM2N.png)

#開啟chrome 實驗wasm  

![](https://i.imgur.com/gKKTZ0g.png)

然後呢再加點html  

index.html
```
<html>
<p>test</p>
<button onclick="sayHI()">Say HI</button>
</html>
<script>

var worker = new Worker('worker.js');

worker.postMessage("message");
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
伺服器使用nginx 運行結果就是  

<https://developer.mozilla.org/zh-CN/docs/Web/API/Worker/onmessage>  

![](https://i.imgur.com/8ALhGoy.png)

下一篇來看看能不能串流...

# 參考

<https://blog.csdn.net/xueyushenzhou/article/details/82856860>  

<https://askubuntu.com/questions/575505/glibcxx-3-4-20-not-found-how-to-fix-this-error>  

<https://www.yinchengli.com/2018/07/28/wasm-ffmpeg-get-video-frame/>
