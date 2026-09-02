---
title: "掌機上的原生 YouTube"
date: "2026-09-01T23:10:00+08:00"
updated: "2026-09-01T23:10:00+08:00"
permalink: "/2026/09/rg40xxv-youtube.html"
tags: ["Linux Kernel", "Allwinner", "Embedded", "SDL", "Reverse Engineering"]
layout: post
---

[上一篇](/2026/08/rg40xxv-mainline.html)講的是把 RG40XX V 的面板點亮。畫面出來之後，問題就換了一批：這台機器**能拿來做什麼**。

![啟動器的應用程式分頁，YouTube 磚塊在選取狀態；上排是最近遊玩、遊戲庫、RPG、串流、網路等分頁](/assets/uploads/rg40xxv-apps-tab.jpg)

這一輪做完的是一個**原生 YouTube 客戶端**，外加一串各自獨立的修正。分開講。

![YouTube HOME：搜尋列、兩則影片與縮圖、左下角「2 cached videos ready」、底部按鍵提示 D-PAD MOVE / A SELECT / B BACK / X CHANNELS](/assets/uploads/rg40xxv-youtube-home.jpg)

## 為什麼是原生，不是塞一個瀏覽器

第一版走的是 Web：stock Cog/WPE 跑手機版 YouTube。它能開，但在 H700 上瀏覽本身就是 FAIL，而且整條路徑要拖進一個完整的瀏覽器引擎、DRM 模組與 SQLite profile。

第二版整個換掉，變成三個各自獨立的行程：

| 角色 | 東西 | 邊界 |
|---|---|---|
| UI | C++ / SDL texture scene | 只畫面、只收搖桿 |
| 媒體 | AArch64 libmpv + FFmpeg | 軟解 H.264 + ALSA |
| 解析 | `yt-dlp` 常駐服務 | **不是 UI、也不是解碼器** |

最後那條是刻意的。`yt-dlp` 關在一個 owner-private 的 resolver 服務裡，簽章過的設定檔在**每一條退出路徑**上都會被刪掉，播放器只拿得到 loopback endpoint。UI 和解碼器都不知道網址長什麼樣。

操作是搖桿優先，不是把滑鼠介面硬塞進 D-pad：X 開頻道選單、A 套用到下方影片格、B 在退出 HOME 之前先還原記憶體裡的總覽。播放中 A/START 暫停，方向鍵左右 10 秒、L1/R1 30 秒。

![頻道檢視：左上 CHANNEL 標題，三則影片各有標題、頻道名、日期，底部「8 ready · loading images」](/assets/uploads/rg40xxv-youtube-channel.jpg)

## 它真的在播

Host 測試過不算數 —— 這是整個專案最硬的一條規矩。實機收據長這樣：

```text
[23759.196336] YOUTUBE_TEXTURE_BROKER endpoint=READY
[23759.365163] YOUTUBE_TEXTURE_MEDIA loaded=1
[23759.366005] YOUTUBE_PLAYER_TIMELINE position=0 advancing=1
[23760.227800] YOUTUBE_TEXTURE_MEDIA first-frame=READY
```

測試起點是 monotonic `23756.36`，所以**行程啟動到第一張畫面約 3.87 秒**。

播放中隔一秒取兩次 ALSA：

```text
state=RUNNING hw_ptr=16256
state=RUNNING hw_ptr=65312
```

hw_ptr 在前進，這是「音訊真的在跑」的機器證據，不是「服務還活著」的推論 —— 這兩件事差很多。

再用 SIGUSR1 把 render memory 倒出來，1.2 MB 的 BMP 取樣到 **33 種顏色**，證明畫面不是一片純色。一個 HOME 行程連續跑完 **14 次以上**播放循環，每次都 `first-frame=READY`，沒有行程重啟、沒有第三次播放劣化。

![播放前的狀態：畫面中央 Loading video…，底部進度列顯示 PLAYING 00:00 / 32:41 與 A PAUSE、LEFT/RIGHT 10s、B BACK](/assets/uploads/rg40xxv-youtube-loading.jpg)

## 但它還不算驗收通過

這點得寫清楚。上面全部都是 `evidence_scope=COMPONENT_GATE`：

- 那顆 binary 的 SHA 對得起來、播放、音訊、timeline、畫面非純色 —— **都有收據**
- 但觀察用的是**非目標 p8**，沒有重建完整的 hot-bundle closure
- 所以 playback、audio、timeline、video、memory 全部維持 `PENDING_DEVICE`，使用者視覺／色彩驗收維持 `PENDING_DEVICE_USER`

Tile 可以按、按了會動，介面上標的是 `VERIFY` 不是 READY。**Host/QEMU 的輸出永遠不能當成實機的視覺或聽覺驗收。**

## 修正的部分

![啟動器的 RPG 分頁：封面直向排列，中央選取項下方標示「RPG 製作大師 2000/2003」](/assets/uploads/rg40xxv-rpg-library.jpg)

### Shovel Knight 起不來

這個查起來很有意思，因為它有三層，而且前兩層互相遮蔽。

TF1 的 p1 存遊戲內容，必須唯讀，而且掛載時帶 `noexec`。舊套件裡的 Box86 是 **2021 年的 v0.2.3**，從 p1 經 ARMhf loader 啟動時，動態載入器因為 `noexec` **根本映射不了它的 ELF segment** —— 回報 status 127。

換成現行 Box86 之後，Box86 自己能跑了，然後它**正確地拒絕**了 p1 上那個不可執行的 `ShovelKnight` —— status 255。第一層修掉才看得到第二層。

第三層在遊戲自己身上：它直接匯入 SDL2 的私有函式 `SDL_GetJoystickGUIDInfo`，而且用的是舊的參數數量。Box86 upstream 有一個 commit 專門為這款遊戲加了 `BOX86_SDL2_JGUID=1` 相容模式，v0.2.3 沒有。

還有一個假線索：`libShovelKnight.so` 會印 `Failed to acquire nag_ptr signature`。它**只是記錄訊息，不會退出** —— 舊 signature 對不上本機版本而已。看到紅字就當根因，會查錯方向。

修法是不動 p1：adapter 先逐位驗證 p1 原始遊戲、原子複製到 p7 state、驗 patch site、套用精確的 **11-byte patch**、再驗完整輸出 SHA。

```text
原始  89 2c 24 c7 44 24 08 30 00 00 00
替換  ff 85 18 01 00 00 e9 70 01 00 00
```

### 關螢幕不要關面板

`ui-hardwarectl screen-off` / `screen-on`，實機量到：

```text
BEFORE  brightness=1250 bl_power=0
OFF     brightness=0    bl_power=4
ON      brightness=1250 bl_power=0
```

關鍵在它**沒做的事**：沒有對 `fb0` powerdown、沒有關 TCON、沒有 reset 面板、沒有 DRM panel unprepare。只是存起來然後關掉背光與搖桿燈，讓 GPU runtime PM 回到 `auto`，點亮時還原。

理由跟上一篇是同一個 —— 這塊面板的 init sequence 是廠商機密，**能不重新初始化就不要碰它**。省下的每一次面板 re-init，都是一次不會黑掉的機會。

（這只證明一輪安全的背光開關，不是 suspend-to-RAM。）

### NDS 模擬器：兩個看起來會贏的優化，一個沒用

同一台機、同一個 ROM、同一份 RetroArch 設定、600 個 emulated frames，跑 A/B/C/A 四段：

| 候選 | wall | FPS | 主執行緒 CPU |
|---|---:|---:|---:|
| baseline A | 13.826 s | 43.398 | 95.77% |
| O3 + vectorize | 13.850 s | 43.320 | 93.25% |
| render skip=1 | 12.267 s | 48.913 | 77.70% |
| baseline B | 13.865 s | 43.274 | 95.04% |

baseline A/B 的 wall drift 只有 **0.286%**，所以這場的重複性足以判斷候選。結果：

- **O3 + vectorize 慢了 0.037%** —— 在雜訊裡，沒有可量測的收益
- **render skip=1 快 11.4%**，但它刻意少畫一半的 emulated frame。那是流暢度取捨，**不是免費的 CPU 優化**

四段都 `rc=0`、framebuffer CRC 相同、沒有新的 GL error。真正的瓶頸寫在最後一欄：**主執行緒接近單核飽和**。在那之前調編譯旗標是在錯的地方使力。

順帶一提，四段都存在一塊 16,773,120 byte 的匿名 `rwxp` mapping —— 這證明 AArch64 JIT 真的配置並執行了 runtime code cache，而不只是 config 裡有那個字串。

### 部署時裝置上沒有 jq

第一次安裝**安全地失敗了**，而且是在 current-release 指標被改掉**之前**。

原因很蠢：release verifier 用 `jq` 解析 RPG catalog，而裝置上沒裝 `jq`。但這個蠢問題暴露出設計是對的 —— 驗證失敗發生在切換指標之前，所以裝置上跑的還是舊 release，沒有半死不活的狀態。

後來 verifier 改成用 Python 解析。

## 現在裝在上面的東西

| Component | Host/QEMU | 實機 |
|---|---|---|
| emulator-runtime | PASS | PENDING |
| rpg-content | PASS | PENDING |
| bluetooth-runtime | PASS | PENDING |
| device-control | PASS | PENDING |
| youtube-h700 | PASS | PENDING |
| rmut-h700 | PASS | PENDING |

`rmut-h700` 是 RPG Maker MV/MZ 的中文化 runtime，只搬掌機真的需要的資料路徑，不搬桌面 GUI；預設關閉，開啟時建立 save-safe 的隔離工作樹。

**這張表有兩欄，不是一欄**，而且第二欄不會因為第一欄綠了就跟著綠。這是整套流程唯一在防的事情：把「測得動」講成「驗過了」。

![開機選單與 systemd 輸出：頂端 RG40XX V SAFE BOOT，選取 RG40XX OS (LINUX 7.2)，下方是各服務的 OK 與一行 FAILED](/assets/uploads/rg40xxv-boot-selector.jpg)

## 冷開機還是沒解決

跟上一篇同一堵牆，沒有進展。

現役那顆 p8 在更早一次首輪冷開失敗之後就被標成 `BANNED`。這一輪的 p7 部署是在明確授權下、**保持 p8 逐位不動**的前提做的 —— p8 前後 SHA 相同、`p8 write=NONE`。

所以現況誠實地說是：**接管路徑上的東西越做越完整，冷態帶起面板這件事還是沒解。** 這兩件事互不相欠。

---

原始碼：<https://github.com/x213212/rg40xxv-mainline>
