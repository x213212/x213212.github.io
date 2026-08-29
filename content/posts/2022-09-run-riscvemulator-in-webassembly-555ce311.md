---
title: "run riscv_emulator in webassembly"
date: "2022-09-21T12:51:00.002+08:00"
updated: "2022-09-22T06:57:12.918+08:00"
permalink: "/2022/09/run-riscvemulator-in-webassembly.html"
original_url: "https://x8795278.blogspot.com/2022/09/run-riscvemulator-in-webassembly.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5345522828811080541"
tags: ["RISC-V", "WebAssembly"]
layout: post
---

![](https://i.imgur.com/RfdJgKi.png)

# run riscv_emulator in webassembly
之前看到gameboy 模擬器run在 瀏覽器上蠻新奇的，之前有寫過重新編譯ffmpeg 到 網頁這次也來編譯一下
https://developer.mozilla.org/en-US/docs/WebAssembly/C_to_wasm
這邊有簡單起始
# install emcc
```bash
git clone https://github.com/juj/emsdk.git
cd emsdk
./emsdk install --build=Release sdk-incoming-64bit binaryen-master-64bit
./emsdk activate --global --build=Release sdk-incoming-64bit binaryen-master-64bit
./emsdk install latest
./emsdk activate latest
# on Linux or Mac macOS
source ./emsdk_env.sh
```

```c
#include <stdio.h>

int main() {
    printf("Hello World\n");
    return 0;
}
```

compile
```bash
emcc hello.c -o hello.html
```

上一篇有一個risc v 模擬器我們看有哪些檔案要編譯下
```bash
make -n
```
![](https://i.imgur.com/O9JJu9j.png)

我們模擬器還要讀binary 所以還要用到webasm的虛擬檔案系統
https://cntofu.com/book/150/zh/ch3-runtime/ch3-03-fs.md
改一下指令
```bash
 emcc main.c ./src/csr.c ./src/cpu.c ./src/bus.c ./src/dram.c -o main -I ./include  -s WASM=1 -o hello.html  --preload-file addi.bin
```
![](https://i.imgur.com/ITr6aJu.png)
編譯成功,copy 到nginx,在windows run
![](https://i.imgur.com/6dzb1IF.png)
![](https://i.imgur.com/vZlhoGV.png)

到這裡我們成功把模擬器run 在前端
![](https://i.imgur.com/RfdJgKi.png)
之前有一個gb模擬器可以運行在當前畫面瀏覽器畫面
https://github.com/HFO4/gameboy.live
既然遊戲實體記憶體都存於wram,hram那我們每走一步我們都做存檔和寫入，再返回畫面data給js進行繪圖
這樣應該就可以實現這個功能。

會到gb_emu開發環境
https://blog.csdn.net/ggggyj/article/details/124164136%20
https://blog.csdn.net/qq_38851184/article/details/125697442
升級到GLIBCXX_3.4.26

![](https://i.imgur.com/cGtRTPA.png)

