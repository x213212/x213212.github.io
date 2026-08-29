---
title: "webassmbly gb simulator support audio"
date: "2025-01-04T02:18:00.002+08:00"
updated: "2025-01-04T02:18:23.378+08:00"
permalink: "/2025/01/webassmbly-gb-simulator-support-audio.html"
original_url: "https://x8795278.blogspot.com/2025/01/webassmbly-gb-simulator-support-audio.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6069164989829595660"
tags: ["gb_emu"]
layout: post
---

![](https://hackmd.io/_uploads/ryzYuiBUkx.png)

# webassmbly gb simulator support audio
之前的一個小專案移植到 webassbly 就沒繼續弄下去了，過了兩年chatgpt 出來真的感覺在讀文件還是完成需求或者一些bug好像幾乎用時間嚕都可以解決，
https://github.com/x213212/LLD_gbemu_wasm
https://github.com/x213212/LLD_gbemu_wasm/commit/5e64d6a4ffdd06f483d69c7f1128ba1495d7961d
補上makefile
```
make build 
make run 
```
就可以了.

![image](https://hackmd.io/_uploads/ryzYuiBUkx.png)
記得用 chrome 去跑才可以跑滿 60 fps，直接跑應該可以make run 聽到熟悉~~薩爾達傳說music~~
我覺得在 chanl4 再跑 usa版的 rom 好像還是會有雜音不確定是否處理的正常，不過大部分其他聲道都有出來選單音效背景，感覺做一些以前的即時存檔和給大家線上輪流玩的程式碼應該改個幾天就弄完，不過等到下次想到在弄哈哈

