---
title: "oscilloscope art"
date: "2025-07-13T17:02:00.008+08:00"
updated: "2025-07-13T17:02:57.965+08:00"
permalink: "/2025/07/oscilloscope-art.html"
original_url: "https://x8795278.blogspot.com/2025/07/oscilloscope-art.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-1734772857058066561"
tags: ["oscilloscope art"]
layout: post
---

![](https://hackmd.io/_uploads/S1wjylW8lx.png)

# Oscilloscope art
https://www.youtube.com/watch?v=lrtXt2Liaf8
以前看到就很想來實驗一下，最近蠻有空的，要說示波器的話，我想先買簡單版的順便三用電表也不見了，買了這台zt702s
https://www.youtube.com/shorts/EBNega43BBY
那主控端就是nodemcu 了，那這邊用了node mcu 的兩個adc 和螢幕和旋鈕
再來就是比較有趣的震鏡可以控制xy軸這時候再買一個雷射當光源好材料到齊了開組
```c
/*
  GALVO – Auto-cycle Waveforms (Square ▸ Triangle ▸ Circle)
  ---------------------------------------------------------
  • DAC25 → X  • DAC26 → Y
  • ADC34 旋鈕：1-60 fps
  • 每 2 秒自動切換圖樣：Square → Triangle → Circle → …
*/

#include <Arduino.h>

// ── 腳位 ─────────────────────────────────────
constexpr int DAC_X     = 25;          // 內建 DAC1
constexpr int DAC_Y     = 26;          // 內建 DAC2
constexpr int ADC_KNOB  = 34;          // 旋鈕

// ── 參數 ────────────────────────────────────
constexpr int MAX_POINTS = 512;        // 每幀點數
constexpr int FPS_MIN = 1, FPS_MAX = 60;
constexpr uint8_t AMP = 100;           // 圖形半徑 (0-255)

// ── 波形列舉 ────────────────────────────────
enum class Pattern { Square, Triangle, Circle };
Pattern current = Pattern::Square;

uint8_t xBuf[MAX_POINTS], yBuf[MAX_POINTS];
volatile int idx = 0;

hw_timer_t *timer = nullptr;

/* ──────────────────────────────────────────
   各圖形生成器
   ──────────────────────────────────────────*/
void buildSquare()
{
  int seg = MAX_POINTS / 4;            // 每邊點數
  for (int i = 0; i < MAX_POINTS; ++i) {
    int p = i % seg;
    if (i < seg) {                     // 右 → 上
      xBuf[i] = 127 + AMP;
      yBuf[i] = 127 + AMP - (2 * AMP * p) / seg;
    } else if (i < 2 * seg) {          // 上 → 左
      xBuf[i] = 127 + AMP - (2 * AMP * p) / seg;
      yBuf[i] = 127 - AMP;
    } else if (i < 3 * seg) {          // 左 → 下
      xBuf[i] = 127 - AMP;
      yBuf[i] = 127 - AMP + (2 * AMP * p) / seg;
    } else {                           // 下 → 右
      xBuf[i] = 127 - AMP + (2 * AMP * p) / seg;
      yBuf[i] = 127 + AMP;
    }
  }
}
/* ──────────────────────────────────────────
   正三角 (頂點在上方、底邊水平)
   ──────────────────────────────────────────*/
void buildTriangle()
{
  const uint8_t x1 = 127;        // 頂：正中
  const uint8_t y1 = 127 - AMP;

  const uint8_t x2 = 127 + AMP;  // 右下
  const uint8_t y2 = 127 + AMP;

  const uint8_t x3 = 127 - AMP;  // 左下
  const uint8_t y3 = 127 + AMP;

  int seg = MAX_POINTS / 3;      // 三條邊各 seg 點

  for (int i = 0; i < MAX_POINTS; ++i) {
    int k   = i / seg;           // 第幾條邊 0,1,2
    int idx = i % seg;           // 該邊內位置
    float t = float(idx) / (seg - 1);

    switch (k) {
      case 0:   // 頂 → 右下
        xBuf[i] = uint8_t( x1 + (x2 - x1) * t );
        yBuf[i] = uint8_t( y1 + (y2 - y1) * t );
        break;

      case 1:   // 右下 → 左下
        xBuf[i] = uint8_t( x2 + (x3 - x2) * t );
        yBuf[i] = y2;            // y 固定
        break;

      default:  // 左下 → 頂
        xBuf[i] = uint8_t( x3 + (x1 - x3) * t );
        yBuf[i] = uint8_t( y3 + (y1 - y3) * t );
        break;
    }
  }
}

void buildCircle()
{
  for (int i = 0; i < MAX_POINTS; ++i) {
    float a = 2.0f * PI * i / MAX_POINTS;
    xBuf[i] = 127 + AMP * sinf(a);
    yBuf[i] = 127 + AMP * cosf(a);
  }
}

/* 選圖形並重建表格 */
void rebuild()
{
  switch (current) {
    case Pattern::Square:   buildSquare();   break;
    case Pattern::Triangle: buildTriangle(); break;
    case Pattern::Circle:   buildCircle();   break;
  }
}

/* ── Timer 相關 ─────────────────────────── */
void IRAM_ATTR onTimer()
{
  dacWrite(DAC_X, xBuf[idx]);
  dacWrite(DAC_Y, yBuf[idx]);
  idx = (idx + 1) % MAX_POINTS;
}

void setFPS(int fps)
{
  uint64_t step = 1'000'000ULL / (fps * MAX_POINTS);
  if (step < 10) step = 10;            // ≈100 kHz 上限

  if (timer) { timerEnd(timer); timer = nullptr; }
  timer = timerBegin(1'000'000);       // 1 MHz → 1 µs
  timerAttachInterrupt(timer, &onTimer);
  timerAlarm(timer, step, true, 0);
}

/* ── 初始化 ─────────────────────────────── */
void setup()
{
  analogReadResolution(12);
  rebuild();          // 先建 Square
  setFPS(10);         // 預設 10 fps
}

/* ── 主迴圈 ─────────────────────────────── */
void loop()
{
  static uint32_t lastSw = 0;          // 圖形切換計時
  static uint32_t lastFPS = 0;         // FPS 更新計時

  uint32_t now = millis();

  /* 每 2 秒自動切換圖形 */
  if (now - lastSw >= 2000) {
    current = (current == Pattern::Square)   ? Pattern::Triangle :
              (current == Pattern::Triangle) ? Pattern::Circle   :
                                               Pattern::Square;
    rebuild();
    lastSw = now;
  }

  /* 每 0.2 秒讀旋鈕，更新 FPS */
  if (now - lastFPS >= 200) {
    int adc = analogRead(ADC_KNOB);
    int fps = map(adc, 0, 4095, FPS_MIN, FPS_MAX);
    fps = constrain(fps, FPS_MIN, FPS_MAX);
    setFPS(fps);
    lastFPS = now;
  }
}

```
![image](https://hackmd.io/_uploads/rJ-SC1bUxl.png)
注意線要插110v可能會有危險，不確定中國會不會爆炸

![image](https://hackmd.io/_uploads/S1wjylW8lx.png)
![image](https://hackmd.io/_uploads/r1Xpyg-8gx.png)
![image](https://hackmd.io/_uploads/SkZJxg-Lgl.png)
![image](https://hackmd.io/_uploads/HySellb8gg.png)
如果再針對 雷射模組做開關應該就可以畫出流暢的圖

