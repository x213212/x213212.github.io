---
title: "mini-riscv-os vga"
date: "2022-09-29T12:27:00.004+08:00"
updated: "2022-09-29T13:09:26.936+08:00"
permalink: "/2022/09/mini-riscv-os-vga.html"
original_url: "https://x8795278.blogspot.com/2022/09/mini-riscv-os-vga.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-7265378745503280475"
tags: ["vga"]
layout: post
---

![](https://i.imgur.com/67MDyds.gif)

# mini-riscv-os vga
https://gist.github.com/iamgreaser/15a0a81cd117d4efd1c47ce598c13c91

https://github.com/cccriscv/mini-riscv-os/tree/master/03-MultiTasking
找到一個riscv 的vga 驅動

記得bios 改為 no bios
```bash
~/qemu-vga$ riscv32-unknown-elf-gcc  -Os -mcmodel=medany -nostdlib  -Wl,-T,qemu.ld -o vga-hello.elf boot.S main.c 
~/qemu-vga$ qemu-system-riscv32 -bios none -machine virt -device VGA -smp 1 -kernel vga-hello.elf

```
![](https://i.imgur.com/9ZOPfqn.png)

我們來移到 https://github.com/cccriscv/mini-riscv-os
在
mini-riscv-os 00 hello-os確實可以進行繪圖
![](https://i.imgur.com/wOF7xa7.png)
![](https://i.imgur.com/DzaUkgI.png)
嘗試移植到03切換多任務的部分，改一下stack
![](https://i.imgur.com/ZxvtSF2.png)
![](https://i.imgur.com/h5vn8tF.png)
到這裡就可以做切換任務，有多工，參考30 day os我們就可以對視窗畫圖，接收中斷，畫面會閃爍可能就是要統一對圖層新增優先權看誰可以覆蓋誰，或者雙重緩衝(?。
https://wiki.osdev.org/Drawing_In_Protected_Mode
https://github.com/cccriscv/mini-riscv-os/tree/master/03-MultiTasking
以兩個任務分別畫正方形與直線
https://github.com/x213212/mini-riscv-os-vga
![](https://i.imgur.com/67MDyds.gif)

## References

- [cccriscv/mini-riscv-os](https://github.com/cccriscv/mini-riscv-os) — 本文的 RISC-V OS 實作基底。
- 川合秀實，《30日でできる！OS自作入門》，毎日コミュニケーションズ，2006，ISBN 978-4-8399-1984-9. [Book record](https://ndlsearch.ndl.go.jp/books/R100000002-I000008118788) — 文中提及的設計靈感來源。

