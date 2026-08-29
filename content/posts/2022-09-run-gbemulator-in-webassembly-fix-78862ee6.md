---
title: "run gb_emulator in webassembly & fix memleak & back to pthread"
date: "2022-09-22T12:29:00.003+08:00"
updated: "2022-09-22T12:29:49.908+08:00"
permalink: "/2022/09/run-gbemulator-in-webassembly-fix.html"
original_url: "https://x8795278.blogspot.com/2022/09/run-gbemulator-in-webassembly-fix.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-525352168957772280"
tags: []
layout: post
---

![](https://imgur.com/LApSnni.gif)

https://github.com/x213212/LLD_gbemu_wasm/

# enable SharedArrayBuffer
![](https://i.imgur.com/qALQRCJ.png)

# enable pthread
```c
#include "../include/common.h"
#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#endif

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
u32 prev_frame = 0;
int count2 = 0;

// EMSCRIPTEN_KEEPALIVE
void handle_events()
{
 
    usleep(100);
    ui_handle_events();
    ui_update();
 
}

void run_main_loop()
{
#ifdef __EMSCRIPTEN__
    printf("Cart loaded..\n");
    emscripten_set_main_loop(handle_events, 60, true);
#else
    printf("Cart loaded2..\n");
    while (ctx.running)
    {
        handle_events();
    }
#endif
}

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
    // u32 prev_frame = 0;
    // int count2 = 0;
    //   cpu_set_flags(ctx,  ctx.regs.a, 1, (val & 0x0F) == 0x0F, -1);
    // fp = fopen("regist.txt", "w");

    pthread_t t1;

    if (pthread_create(&t1, NULL, cpu_run, NULL))
    {
        fprintf(stderr, "FAILED TO START MAIN CPU THREAD!\n");
        return -1;
    }

    u32 prev_frame = 0;
    run_main_loop();
  

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
注意要加這個
 -s USE_PTHREADS=1  -s PTHREAD_POOL_SIZE=4

```bash
 emcc --bind main.c ./lib/cpu_fetch.c ./lib/interrupts.c ./lib/ppu_pipeline.c ./lib/timer.c ./lib/dma.c ./lib/bus.c ./lib/cart.c ./lib/cpu_proc.c ./lib/emu.c ./lib/io.c ./lib/ppu_sm.c ./lib/ui.c ./lib/cpu_util.c ./lib/gamepad.c ./lib/lcd.c ./lib/ram.c ./lib/cpu.c ./lib/dbg.c ./lib/instructions.c ./lib/ppu.c ./lib/stack.c -I ./include  -o foo.html -s USE_SDL=2 -s USE_SDL_GFX=2 --preload-file LG.gb   -sALLOW_MEMORY_GROWTH  -s USE_PTHREADS=1  -s PTHREAD_POOL_SIZE=4
```
現在我們的fps也可以到達快60幀，我們的按鍵全部都可以work!
![](https://i.imgur.com/EFwQoz4.png)

來處理記憶體洩漏
![](https://i.imgur.com/qkG3Qcp.png)
於pixel_fifo_pop()
```c
u32 pixel_fifo_pop() {
    if (ppu_get_context()->pfc.pixel_fifo.size <= 0) {
        fprintf(stderr, "ERR IN PIXEL FIFO!\n");
        exit(-8);
    }

    fifo_entry *popped = ppu_get_context()->pfc.pixel_fifo.head;
    ppu_get_context()->pfc.pixel_fifo.head = popped->next;
    ppu_get_context()->pfc.pixel_fifo.size--;

    u32 val = popped->value;

    free(popped); <==作者忘記補
    

    return val;
}
```

現在wasm 就可以全速運行我們的gb_emu，也不會有記憶體洩漏的問題，加上個存檔讀檔就可以像上次提到的專案進行cloud大家一起玩，畫面顯示也不會一幀一幀的跳

![](https://imgur.com/LApSnni.gif)

