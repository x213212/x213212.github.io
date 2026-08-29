---
title: "把 RG40XX V 搬上 mainline kernel：一塊點不亮的螢幕"
date: "2026-08-30T04:30:00+08:00"
updated: "2026-08-30T04:30:00+08:00"
permalink: "/2026/08/rg40xxv-mainline.html"
tags: ["Linux Kernel", "Allwinner", "DRM", "Embedded", "Reverse Engineering"]
layout: post
---

Anbernic RG40XX V 是一台 Allwinner H700 的掌機，出廠跑廠商的 BSP kernel。我想讓它跑 **mainline Linux 7.2**。

起因很單純：想要串流玩得順、想跑 RPG Maker 的遊戲。結果擋在路上的是**顯示**。

![啟動器在裝置上執行：由 mainline 顯示堆疊算圖的遊戲清單畫面](/assets/uploads/rg40xxv-shell.jpg)

## 問題不是「還沒支援」，是「亮不起來」

Linux 7.2 本來就能在 H700 上開機，device tree 也涵蓋好幾台 Anbernic 掌機。缺的不是支援，是**這塊面板點不亮、點亮了也撐不住**。

大部分工作都在顯示，其中三個值得寫下來。

## 一、兩種 RDMA 架構混用造成的黑畫面

症狀是背光亮著、畫面全黑。

一開始往「userland 繞過驅動直接寫面板暫存器」的方向查，結果不是。問題在 kernel 裡面：DE33 mixer 已經改成**兩階段 RDMA enable** 流程，但初始化時**沒有把 blender 和 formatter 註冊為 deferred enable**。第一次 atomic commit 因此帶起一條少了兩級的管線，面板就黑了。

只有兩種組合是自洽的：

| Core | Deferred registration | 結果 |
|---|---|---|
| single-phase RDMA | 無 | 正常 |
| two-phase RDMA | **有** | 正常 |
| two-phase RDMA | 無 | **黑畫面** |

修正就是補上兩個 `sun8i_rdma_defer_enable()`，讓第三列不可能發生。

但這個 diff 不是重點。重點是**顯示 bug 可以長得跟應用程式亂搞一模一樣**，而分辨的方法是先確立：邊界的哪一側曾經碰過 DE33、TCON 或面板 timing 暫存器？追下去發現 release 分割區只發過 `FBIOBLANK`、`FBIO_WAITFORVSYNC` 和 VT ioctl —— 於是 kernel 成了唯一嫌疑犯。

## 二、接管面板，而不是重新初始化它

這類面板開機時**已經在掃描**了：原廠 boot chain 在 Linux 起來之前就把它點亮，而那段 init sequence 沒有任何文件。

猜一段 init sequence 去重放，得到的就是黑屏或閃爍。

所以面板驅動改成**偵測面板是否已經亮著並在掃描，然後接管那個狀態** —— 引用它必須持有的時脈、讀回 timing，**不重新設定 mode、不重放 reset**。kernel log 會明講：

```
RG40XXV: panel adopted from firmware scanout (lit-at-probe=1 scanning-now=1):
         no reset/init replay, PI_DATA=...
TCON0 timing adopted from firmware (stock sw_enable): mode not re-programmed
```

這是一個可以泛用的手法：**面板 init 是廠商機密的硬體，繼承那個能動的狀態，不要跟它競爭。**

## 三、關機也要有順序

顯示能撐過重開機的另一半是關閉流程。`sun4i_drv` 和 mixer 現在會依定義好的順序把管線靜置下來，而不是把當下碰巧的狀態留給下一階段繼承。

## 其他

- **Panfrost GPU fault** — 針對這顆 SoC 修了 device、GPU、MMU、job handling。用的是開源 Mali 驅動，不是廠商 blob
- **搖桿驅動依賴一個被移除的 API** — ROCKNIX 的單 ADC 搖桿驅動依賴 `input-polldev`，而 mainline 已經刪掉它。這裡把它**還原了 362 行**，而不是重寫一個本來就能動的驅動
- **背光控制器根本沒有驅動** — `pwm-sun8i.c`，新增 **1,542 行**
- 電量回報、視訊解碼、USB gadget、音訊、watchdog、藍牙、suspend，以及整個 Anbernic H700 家族的 device tree

## 目前的狀態：冷開機還沒解決

這點我寫在 README 最上面，因為它決定這份東西能不能當日常韌體用 —— **不能**。

- **能動的**：匯入原廠面板資料、乾淨重刷之後，可以開到 **boot menu**。這條路徑能動，是因為**已經有東西把面板點亮了**，驅動接管的是運行中的狀態
- **沒解決的**：完整斷電之後，沒有任何東西點亮過面板，必須從**冷態**帶起來。而那正是「沒有東西可以接管」的情況

這兩件事是同一堵牆的兩面：接管路徑之所以有效，正是因為它避開了重放一段 Anbernic 從未公開的 init sequence。

## 刷機前先備份

`docs/flash.md` 的第 1 步是備份原廠分割區，那是**前提條件不是建議**。原廠映像不在這個 repo 裡，以後也不會有 —— 你自己的備份是唯一的還原來源，而且 `docs/firmware.md` 用到的面板資料也只能從那裡來。

刷機腳本只寫 64 MiB 的 p8 boot 分割區、其餘不動。但那是護欄，不是保證。

---

原始碼：<https://github.com/x213212/rg40xxv-mainline>
