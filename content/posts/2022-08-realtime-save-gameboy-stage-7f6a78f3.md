---
title: "realtime save gameboy state"
date: "2022-08-30T00:20:00.006+08:00"
updated: "2022-08-30T14:06:05.103+08:00"
permalink: "/2022/08/realtime-save-gameboy-stage.html"
original_url: "https://x8795278.blogspot.com/2022/08/realtime-save-gameboy-stage.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3169303014889603277"
tags: ["gameboy"]
layout: post
---

![](https://i.imgur.com/0WF1slS.gif)

# realtime save gameboy state

![](https://i.imgur.com/0WF1slS.gif)

前幾天修改一個專案，嘗試去改出gameboy 模擬器的即時存檔功能。
https://github.com/x213212/LLD_gbemu

https://www.coranac.com/tonc/text/hardware.htm?source=post_page
https://www.cs.rit.edu/~tjh8300/CowBite/CowBiteSpec.htm#Graphics%20Hardware%20Overview
下列大概gameboy模擬器做一個介紹
https://www.youtube.com/watch?v=e87qKixKFME

https://github.com/rockytriton/LLD_gbemu

既然是模擬器，那麼我們只要針對 模擬出來的register 和 memory 進行複製，dump 成檔案，在讀取時候再進行恢復記憶體，針對gameboy 記憶體這一部分，根據這一部分的vram,hram,wram,bank這些記憶體的區別在搜尋一些網站實在講得有點不太清楚，後來看到這一篇

https://macabeus.medium.com/reverse-engineering-a-gameboy-advance-game-understanding-the-game-physics-part-3-5b8dd3d91554

，才確定顯示在當前畫面的存在vram 或者 oam,儲存遊戲真正狀態而是在hram 和 wram,只要針對這些記憶體進行備份和還原即可。
一開始稍微紀錄一下cpu讀指令的過程到進入遊戲的過程
一開始就是先load 卡帶
# bool cart_load(char *cart)
![](https://i.imgur.com/fKaXaMi.png)

這邊會做到讀卡帶一些information
不同卡帶有不同memory大小
![](https://i.imgur.com/7HuiOBe.png)
https://gbdev.io/pandocs/Memory_Map.html
這邊有詳細介紹memory bank
一般使用遊戲存檔都會存在這些bank裡面。
#  int emu_run(int argc, char **argv)
這邊開始啟動會看到main 負責call sdl lib 進行刷新畫面
![](https://i.imgur.com/on0eD3q.png)

可以看到也開了一個thread 進行 cpu 讀取指令和解碼，也就是cpu_run

# void *cpu_run(void *p)
![](https://i.imgur.com/XlHCv6s.jpg)
呼叫這個cpu_step() 會開始進行解碼

![](https://i.imgur.com/jWQWIs0.png)
這邊指令可能複雜一點，作者實現了stack 和 based on modified 8080 and Z80 指令
https://www.pastraiser.com/cpu/gameboy/gameboy_opcodes.html
fetch_instruction();
fetch_data();
execute();
舉幾個例子

# static void fetch_instruction()
```c
static void fetch_instruction()
{
    ctx.cur_opcode = bus_read(ctx.regs.pc++);
    ctx.cur_inst = instruction_by_opcode(ctx.cur_opcode);
}
```
cpu 有一個pc 紀錄指令讀取到哪裡，裡面的bus_read或者bus_write
進來後addres再根據記憶體的範圍對相對應的memory 進行寫入
![](https://i.imgur.com/8W1Yifb.png)

詳細還是https://gbdev.io/pandocs/Memory_Map.html
介紹比較詳細

取得    ctx.cur_opcode 和 ctx.cur_inst後
fetch_data();
![](https://i.imgur.com/rl2dGjE.png)
進來之後根據抓取的ctx.cur_inst->mode
回返回一個instruction 的結構
![](https://i.imgur.com/7Wch46u.jpg)
我們在根據 ctx.cur_opcode，
![](https://i.imgur.com/UgxASAE.png)
就可以找尋相對應的ctx.cur_inst->mode

![](https://i.imgur.com/6MJEvXI.png)
```
   [0x00] = {IN_NOP, AM_IMP},         //NOP
   [0x01] = {IN_LD, AM_R_D16, RT_BC}, //LD BC,d16
```
   
像上面這個例子就是0x00 opcode 對應的就是
    reg_type reg_1;
    reg_type reg_2;
    
https://www.pastraiser.com/cpu/gameboy/gameboy_opcodes.html
![](https://i.imgur.com/uN7abTo.png)

https://github.com/rockytriton/LLD_gbemu/raw/main/docs/gbctr.pdf
這些register的type 可以對應到 指令表的reg1 和 reg2
![](https://i.imgur.com/cfSYG9X.png)
AM_R_D8、AM_R...
根據這些reg1的type
來更新當前的cpu_context 裡面的狀態
取得這些reg 當前資料後
   execute();
   就可以執行我們要的指令
   
作者也寫了unit 去更簡單的操作register
![](https://i.imgur.com/DHPM5j3.jpg)

# IN_PROC inst_get_processor(in_type type)

![](https://i.imgur.com/Q0d4sqr.png)

這些存放的是指令的
![](https://i.imgur.com/IyGOo5p.png)

ctx.cur_inst 對應的 function 執行
![](https://i.imgur.com/gQZcQas.png)
# vram & orm
繪圖的部分沒有看得很仔細，這部分就先不介紹，大概是根據當前指令去跟rom 要資料存到 ppu_context
![](https://i.imgur.com/eRdcCqZ.png)

sdl 再根據vram 就是當前畫面的資料，orm應該是各個貼圖的位置刷新到sdl lib
# hram & wram
hram 和 wram 儲存遊戲的狀態
![](https://i.imgur.com/ibi8bB9.png)
![](https://i.imgur.com/3GjB1sJ.png)

為了實現即時存檔/讀檔案
https://macabeus.medium.com/reverse-engineering-a-gameboy-advance-game-extracting-the-objects-from-the-level-part-6-9af59c047164
一開始對gameboy的記憶體概念還不清楚參考了這個網站才知道對要對哪個部份的進行備份

所以我依序新增了fucntion 返回各自ctx
emu_get_context()
ppu_get_context()
cart_get_context()
dma_get_context()
lcd_get_context()
ppu_get_context()
ram_get_context()
timer_get_context()
cpu_get_context()

![](https://i.imgur.com/ug6Q9eE.png)
針對這些資料我額外進行紀錄並寫入到檔案裡完成即時讀檔/備份
這邊要注意cpu 和 ui畫面是分開的
![](https://i.imgur.com/6wqFW3M.png)
所以按下存檔和讀檔速度我加了時間限制
![](https://i.imgur.com/rbWcEyF.png)

最後使用者可以用f1快速存檔用f2可以快速讀檔案.

