---
title: "run gb_emulator in webassembly"
date: "2022-09-22T06:57:00.001+08:00"
updated: "2022-09-22T06:58:55.421+08:00"
permalink: "/2022/09/run-gbemulator-in-webassembly.html"
original_url: "https://x8795278.blogspot.com/2022/09/run-gbemulator-in-webassembly.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-4052543212371459345"
tags: ["gb_emu", "WebAssembly"]
layout: post
---

![](https://i.imgur.com/WtOTTA5.gif)

# run gb_emu in webasm
https://web.dev/drawing-to-canvas-in-emscripten/
有了前面這個構想，現在的webasm不像2018那麼舊了，剛剛看了怎麼console 部分上面還有一塊區域，原來wasm 也整合了sdl2,剛好我們的gb_emu 也是用sdl2引擎那麼我們能不能直接移植上去呢我們來看一下。

```cpp
#include <SDL2/SDL.h>
#include <SDL2/SDL2_gfxPrimitives.h>
#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#endif

SDL_Window *window;
SDL_Renderer *renderer;

SDL_Point center = {.x = 100, .y = 100};
const int radius = 100;

void redraw() {
  SDL_SetRenderDrawColor(renderer, /* RGBA: black */ 0x00, 0x00, 0x00, 0xFF);
  SDL_RenderClear(renderer);
  filledCircleRGBA(renderer, center.x, center.y, radius,
                   /* RGBA: green */ 0x00, 0x80, 0x00, 0xFF);
  SDL_RenderPresent(renderer);
}

uint32_t ticksForNextKeyDown = 0;

bool handle_events() {
  SDL_Event event;
  SDL_PollEvent(&event);
  if (event.type == SDL_QUIT) {
    return false;
  }
  if (event.type == SDL_KEYDOWN) {
    uint32_t ticksNow = SDL_GetTicks();
    if (SDL_TICKS_PASSED(ticksNow, ticksForNextKeyDown)) {
      // Throttle keydown events for 10ms.
      ticksForNextKeyDown = ticksNow + 10;
      switch (event.key.keysym.sym) {
        case SDLK_UP:
          center.y -= 1;
          break;
        case SDLK_DOWN:
          center.y += 1;
          break;
        case SDLK_RIGHT:
          center.x += 1;
          break;
        case SDLK_LEFT:
          center.x -= 1;
          break;
      }
      redraw();
    }
  }
  return true;
}

void run_main_loop() {
#ifdef __EMSCRIPTEN__
  emscripten_set_main_loop([]() { handle_events(); }, 0, true);
#else
  while (handle_events())
    ;
#endif
}

int main() {
  SDL_Init(SDL_INIT_VIDEO);

  SDL_CreateWindowAndRenderer(300, 300, 0, &window, &renderer);

  redraw();
  run_main_loop();

  SDL_DestroyRenderer(renderer);
  SDL_DestroyWindow(window);

  SDL_Quit();
}
```
立刻有一個example 來達成用鍵盤來操控html上的圖形
```bash
emcc --bind foo.cpp -o foo.html -s USE_SDL=2 -s USE_SDL_GFX=2
```
![](https://i.imgur.com/kgByesW.png)

那麼來移植
```bash
 emcc --bind main.c ./lib/emu.c ./lib/cart.c -I ./include -o foo.html -s USE_SDL=2 -s USE_SDL_GFX=2 --preload-file LG.gb 
```
```bash
 emcc --bind main.c ./lib/cpu_fetch.c ./lib/interrupts.c ./lib/ppu_pipeline.c ./lib/timer.c ./lib/dma.c ./lib/bus.c ./lib/cart.c ./lib/cpu_proc.c ./lib/emu.c ./lib/io.c ./lib/ppu_sm.c ./lib/ui.c ./lib/cpu_util.c ./lib/gamepad.c ./lib/lcd.c ./lib/ram.c ./lib/cpu.c ./lib/dbg.c ./lib/instructions.c ./lib/ppu.c ./lib/stack.c -I ./include  -o foo.html -s USE_SDL=2 -s USE_SDL_GFX=2 --preload-file LG.gb 
```
![](https://i.imgur.com/7FwXmHt.png)

這邊可以看到可以load卡帶進前端了。

![](https://i.imgur.com/K6IV7yK.png)
讀取inst

稍微改動了大部分結構，有空再補，到這邊我們直接就gb_emu run 在 web上了，不過記憶體有點洩漏，可能要花更多一點時間排除
```c
emcc --bind main.c ./lib/cpu_fetch.c ./lib/interrupts.c ./lib/ppu_pipeline.c ./lib/timer.c ./lib/dma.c ./lib/bus.c ./lib/cart.c ./lib/cpu_proc.c ./lib/emu.c ./lib/io.c ./lib/ppu_sm.c ./lib/ui.c ./lib/cpu_util.c ./lib/gamepad.c ./lib/lcd.c ./lib/ram.c ./lib/cpu.c ./lib/dbg.c ./lib/instructions.c ./lib/ppu.c ./lib/stack.c -I ./include  -o foo.html -s USE_SDL=2 -s USE_SDL_GFX=2 --preload-file LG.gb   -sALLOW_MEMORY_GROWTH -s ASYNCIFY
```

```c
#include "../include/common.h"

// emcc --bind main.c ./lib/emu.c ./lib/cart.c ./lib/cart.c ./lib/cpu_proc.c ./lib/emu.c ./lib/io.c ./lib/ppu_sm.c ./lib/ui.c ./lib/cpu_util.c ./lib/gamepad.c ./lib/lcd.c ./lib/ram.c ./lib/cpu.c ./lib/dbg.c ./lib/instructions.c ./lib/ppu.c ./lib/stack.c -I ./include   -o foo.html -s USE_SDL=2 -s USE_SDL_GFX=2 --preload-file LG.gb 
//  emcc --bind main.c ./lib/emu.c ./lib/cart.c ./lib/cart.c ./lib/cpu_proc.c ./lib/emu.c ./lib/io.c ./lib/ppu_sm.c ./lib/ui.c ./lib/cpu_util.c ./lib/gamepad.c ./lib/lcd.c ./lib/ram.c ./lib/cpu.c ./lib/dbg.c ./lib/instructions.c ./lib/ppu.c ./lib/stack.c -I ./include   -o foo.html -s USE_SDL=2 -s USE_SDL_GFX=2 --preload-file LG.gb 
// TODO Add Windows Alternative...

/*
  Emu components:

  |Cart|
  |CPU|
  |Address Bus|
  |PPU|
  |Timer|

*/

static emu_context ctx;

emu_context *emu_get_context()
{
    return &ctx;
}

void *cpu_run(void *p)
{

    timer_init();
    cpu_init();
    ppu_init();

    ctx.running = true;
    ctx.paused = false;
    ctx.too = false;
    ctx.ticks = 0;
    //   cpu_set_flags(ctx,  ctx.regs.a, 1, (val & 0x0F) == 0x0F, -1);
    // fp = fopen("regist.txt", "w");
    while (ctx.running)
    {

        if (ctx.too)
            break;

        if (ctx.paused)
        {
            delay(10);
            continue;
        }
        if (!cpu_step())
        {

            printf("CPU Stopped\n");
            return 0;
        }
        // if (count2 >= 2000000 && count2 <= 4000000)
        //     continue;
    }

    return 0;
}

int emu_run()
{
    // if (argc < 2)
    // {
    //     printf("Usage: emu <rom_file>\n");
    //     return -1;
    // }
    if (!cart_load("LG.gb"))
    // if (!cart_load(argv[1]))
    {
        printf("Failed to load ROM file: %s\n", "LG.gb");
        return -2;
    }

    printf("Cart loaded..\n");

    ui_init();

    timer_init();
    cpu_init();
    ppu_init();

    ctx.running = true;
    ctx.paused = false;
    ctx.too = false;
    ctx.ticks = 0;
    u32 prev_frame = 0;
    int count2 = 0;
    //   cpu_set_flags(ctx,  ctx.regs.a, 1, (val & 0x0F) == 0x0F, -1);
    // fp = fopen("regist.txt", "w");
    
    while (ctx.running)
    {

        if (ctx.too)
            break;

        if (ctx.paused)
        {
            delay(10);
            continue;
        }
        if (!cpu_step())
        {

            printf("CPU Stopped\n");
            return 0;
        }
        count2++;
        if (count2 >=1000)
        {
        // usleep(100);
        ui_handle_events();
//  printf("CPU Stopped\n");
        if (prev_frame != ppu_get_context()->current_frame)
        {
            //   printf("CPU Stopped\n");
            ui_update();
        }

        prev_frame = ppu_get_context()->current_frame;
        count2 =0;}
            // continue;
    }
    // pthread_t t1;

    // if (pthread_create(&t1, NULL, cpu_run, NULL))
    // {
    //     fprintf(stderr, "FAILED TO START MAIN CPU THREAD!\n");
    //     return -1;
    // }

    // u32 prev_frame = 0;

    // while (!ctx.die)
    // {
    //     while (ctx.too)
    //         ;

    //     usleep(100);
    //     ui_handle_events();

    //     if (prev_frame != ppu_get_context()->current_frame)
    //     {
    //         ui_update();
    //     }

    //     prev_frame = ppu_get_context()->current_frame;
    //     // printf("%d\n",prev_frame);
    // }

    return 0;
}

void emu_cycles(int cpu_cycles)
{

    for (int i = 0; i < cpu_cycles; i++)
    {
        for (int n = 0; n < 4; n++)
        {
            ctx.ticks++;
            timer_tick();
            ppu_tick();
        }

        dma_tick();
    }
}

```

主要還是pthread_create 改成固定呼叫，javascrpit 是單執行續，似乎有出套件可以變多執行緒

![](https://i.imgur.com/Hyya7nl.png)
![](https://i.imgur.com/WtOTTA5.gif)

