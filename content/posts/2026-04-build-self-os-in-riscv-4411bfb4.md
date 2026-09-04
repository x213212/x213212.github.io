---
title: "build self os in riscv"
date: "2026-04-18T21:11:00.003+08:00"
updated: "2026-04-18T21:11:32.105+08:00"
permalink: "/2026/04/build-self-os-in-riscv.html"
original_url: "https://x8795278.blogspot.com/2026/04/build-self-os-in-riscv.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-7544584792967569554"
tags: ["os", "RISC-V"]
layout: post
---

# build self os in riscv
很久沒更新，最近看到TempleOS，
今天早上無聊來將之前的專案進行合併，新增了lwip wget 下載檔案，預計想要再將這個os再多一個vga的瀏覽器，感覺用NetSurf 渲染都Ok，應該可以在目前的os進行上網，新增了檔案系統，和鍵盤滑鼠硬碟vga驅動
修掉了context switch bug , 使用vga去繪製os的圖形介面和移植一些
30dayMakeOS.
可以自由地放大縮小視窗，改了一個doom 風格迷宮的進去os，多context switch，可以透過qemu 下載http server上的 bmp 檔案，應該在堆一下tls 應該就可以上，等我加完https再來push
![image](https://hackmd.io/_uploads/rJbh3g-pbe.png)
![image](https://hackmd.io/_uploads/HkOA3xWa-l.png)
![image](https://hackmd.io/_uploads/BJsA2lb6Zg.png)
![image](https://hackmd.io/_uploads/rkPy6eZ6bl.png)
![image](https://hackmd.io/_uploads/BJpJalWpbe.png)
![image](https://hackmd.io/_uploads/SyVlaeZTWx.png)
![image](https://hackmd.io/_uploads/S1_-6x-6Ze.png)
![image](https://hackmd.io/_uploads/BJPrpg-abl.png)
![image](https://hackmd.io/_uploads/r1nSaxWT-e.png)
![image](https://hackmd.io/_uploads/H1-LaeW6Zg.png)
![Recording 2026-04-18 at 20.51.46](https://hackmd.io/_uploads/rJQsZbWaZl.gif)
![Recording 2026-04-18 at 20.50.05](https://hackmd.io/_uploads/B1Qi-ZWTZx.gif)
![Recording 2026-04-18 at 21.05.06](https://hackmd.io/_uploads/r1Qi-bZ6Wg.gif)

## References

- [yourtion/30dayMakeOS](https://github.com/yourtion/30dayMakeOS) — 本文提到的移植／參考原始碼基底。
- 川合秀實，《30日でできる！OS自作入門》，毎日コミュニケーションズ，2006，ISBN 978-4-8399-1984-9. [Book record](https://ndlsearch.ndl.go.jp/books/R100000002-I000008118788)

