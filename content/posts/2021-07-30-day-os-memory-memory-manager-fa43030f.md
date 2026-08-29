---
title: "30 DAY os Memory Manager"
date: "2021-07-11T11:28:00.004+08:00"
updated: "2021-07-11T11:39:51.411+08:00"
permalink: "/2021/07/30-day-os-memory-memory-manager.html"
original_url: "https://x8795278.blogspot.com/2021/07/30-day-os-memory-memory-manager.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-4813232289447982129"
tags: ["osdev"]
layout: post
---

![](https://i.imgur.com/QbgCynQ.png)

# 30 Day os day 3
這幾天有點忙我們來把記憶體管理的基礎打好，接下來下一個地方可能會去研究不同任務的切換，有大致上讀過，linux kernel 0.11也是跟這個地方在不同任務的調度做不同的演算法，透過gtd 去動態切換 tss這邊，這邊看能不能直接幫這個作業系統改一些linux kernel 0.11 實驗上去
https://mooc.study.163.com/course/1000002008?tid=2403044007
但是還是要詳細抽取相關聯的地方，到時候再來決定要在linux kernel 0.11 上實作gui還是 在這個os 上實現其他功能等等
# memory 統計
這邊前面有稍微提到 計算機結構 memory spatial localit、、的一些東西，就是假設在一個迴圈裡，裡面的變數其實那些varable 的位置 可以被存在緩存裡，[spatial  ](https://zh.wikipedia.org/wiki/%E8%AE%BF%E9%97%AE%E5%B1%80%E9%83%A8%E6%80%A7)
![](https://i.imgur.com/oe8tOwz.png)
這一章可能會教大家怎麼去讀出一共使用多少memory 空間

内存检查时，要往内存里随便写入一个值，然后马上读取，来检查读取的值与写入的值是否
相等。如果内存连接正常，则写入的值能够记在内存里。如果没连接上，则读出的值肯定是乱七
八糟的。方法很简单。但是，如果CPU里加上了缓存会怎么样呢？写入和读出的不是内存，而是
缓存。结果，所有的内存都“正常”，检查处理不能完成。

這個就是他使用的方式
直接上code來看
## 	bootpack.c
會覺得難懂，可能是不太知道
這邊要直接跑code 去看比較清楚
define 和 unsigned int 之間要怎麼轉
```c
#include <stdio.h>
#include <stdlib.h>
#define TEST 0x00040000
int main (){
        int test = 0;
        unsigned int i = 0xfffbffff;
        i = i| TEST;
        printf("%x\n",i);

        return 0;
}
```
> 簡單來說下面這段程式碼，就是 eflag 我們在以前的章節有提過這是假設有發生 進位 這邊的 eflag 就會 更改，而我們現在這些動作就是 先把 eflag 讀近來，再去做 or 他這邊的意思是，假設不管一開始有沒有怎樣都當嘗試把 ac-flag 進行寫入
> 他用這樣的方式去判斷 cpu 到底是386 還是 486 這邊可以看到程式碼又透過io_store_eflags(eflg); 再把修改完後的eflg 再存入 這邊的化可以看到假設是386的話他還是會跑為0，因為根本就沒這個ac-flag 當然你不能寫所以下一次階段還是會維持之前的數值，反之則你是 flag486
> 然後往下可以看到不管怎樣對這個 ac-flag 進行讀寫他這邊又用and 反向過後的 eflag 則 假設有值的話你還是會有值 最後復原原先的 eflag
> 接下來則去呼叫 memtest_sub 來檢查memory使用率
> 這就是他這段程式碼要做的事情
```c
#define EFLAGS_AC_BIT 0x00040000
#define CR0_CACHE_DISABLE 0x60000000
```

![](https://i.imgur.com/6mb9D5V.png)
簡單來說
unsigned int memtest(unsigned int start, unsigned int end){
		char flg486 = 0;
		unsigned int eflg, cr0, i;

		/* 确认CPU是386还是486以上的 */
		eflg = io_load_eflags();
		eflg |= EFLAGS_AC_BIT; /* AC-bit = 1 */
		io_store_eflags(eflg);
		eflg = io_load_eflags();
		if ((eflg & EFLAGS_AC_BIT) != 0)
		{ /* 如果是386，即使设定AC=1，AC的值还会自动回到0 */
			flg486 = 1;
		}
		eflg &= ~EFLAGS_AC_BIT; /* AC-bit = 0 */
		io_store_eflags(eflg);
		if (flg486 != 0)
		{
			cr0 = load_cr0();
			cr0 |= CR0_CACHE_DISABLE; /* 禁止缓存 */
			store_cr0(cr0);
		}
		i = memtest_sub(start, end);
		if (flg486 != 0)
		{
			cr0 = load_cr0();
			cr0 &= ~CR0_CACHE_DISABLE; /* 允许缓存 */
			store_cr0(cr0);
		}
		return i;
}
```

## memtest_sub
這裡算是第一代的計算memory 總共有多少容量的code

```
	memtest_sub unsigned int memtest_sub(unsigned int start, unsigned int end)
	{
		unsigned int i, *p, old, pat0 = 0xaa55aa55, pat1 = 0x55aa55aa;
		for (i = start; i <= end; i += 4)
		{
			p = (unsigned int *)i;
			old = *p;		  /* 先记住修改前的值 */
			*p = pat0;		  /* 试写 */
			*p ^= 0xffffffff; /* 反转 */
			if (*p != pat1)
			{ /* 检查反转结果 */
			not_memory:
				*p = old;
				break;
			}
			*p ^= 0xffffffff; /* 再次反转 */
			if (*p != pat0)
			{ /* 检查值是否恢复 */
				goto not_memory;
			}
			*p = old; /* 恢复为修改前的值 */
		}
		return i;
	}
```
## memtest_sub sec quick version
他原因就是假設如果只要單純計算容量的話，應該就不用再去嘗試去讀寫，預設所有memory 都可讀可寫
她就每4k開始算，總容量為 32mb
```

unsigned int memtest_sub(unsigned int start, unsigned int end)
{
 unsigned int i, *p, old, pat0 = 0xaa55aa55, pat1 = 0x55aa55aa;
 for (i = start; i <= end; i += 0x1000) {
     p = (unsigned int *) (i + 0xffc);
     old = *p; /* 先记住修改前的值 */
 	*p = pat0;		  /* 试写 */
			*p ^= 0xffffffff; /* 反转 */
			if (*p != pat1)
			{ /* 检查反转结果 */
			not_memory:
				*p = old;
				break;
			}
			*p ^= 0xffffffff; /* 再次反转 */
			if (*p != pat0)
			{ /* 检查值是否恢复 */
				goto not_memory;
			}
			*p = old; /* 恢复为修改前的值 */
		}
		return i;
	}
```
## bootpack.c
他這邊，因為compiler 幫他做最佳化導致他的程式碼
```
i = memtest(0x00400000, 0xbfffffff) / (1024 * 1024);
 sprintf(s, "memory %dMB", i);
 putfonts8_asc(binfo->vram, binfo->scrnx, 0, 32, COL8_FFFFFF, s);
```
暂时先使用以上程序对0x00400000～0xbfffffff范围的内存进行检查。这个程序最大可以识别
3GB范围的内存。0x00400000号以前的内存已经被使用了（参考8.5节的内存分布图），没有内存，
程序根本运行不到这里，所以我们没做内存检查。如果以byte或KB为单位来显示结果不容易看明
白，所以我们以MB为单位。
也不知道能不能正常运行。如果在QEMU上运行，根据模拟器的设定，内存应该为32MB。
运行“make run”。

變成這樣
## memtest_sub compiler optimization
```
unsigned int memtest_sub(unsigned int start, unsigned int end)
{
 unsigned int i;
 for (i = start; i <= end; i += 0x1000) { }
 return i;
}
```
所以作者又乾脆去寫一個asm 版本的統計 asm

## memtest_sub asm version
可能會懷疑的就是 push 會影響 esp 位置 ，再來就是這些register 被拿來當作變數使用難度應該還可以主要對照
memtest_sub sec quick version 程式碼搬過來
```
_memtest_sub: ; unsigned int memtest_sub(unsigned int start, unsigned int end)
 PUSH EDI ; （由于还要使用EBX, ESI, EDI） esp+4
 PUSH ESI  esp+4
 PUSH EBX  esp+4
 MOV ESI,0xaa55aa55 ; pat0 = 0xaa55aa55;
 MOV EDI,0x55aa55aa ; pat1 = 0x55aa55aa;
 MOV EAX,[ESP+12+4] ; i = start;  = 12 繼續只向第一個 start
mts_loop:
 MOV EBX,EAX
 ADD EBX,0xffc ; p = i + 0xffc;
 MOV EDX,[EBX] ; old = *p;
 MOV [EBX],ESI ; *p = pat0;
 XOR DWORD [EBX],0xffffffff ; *p ^= 0xffffffff;
 CMP EDI,[EBX] ; if (*p != pat1) goto fin;
 JNE mts_fin
 XOR DWORD [EBX],0xffffffff ; *p ^= 0xffffffff;
 CMP ESI,[EBX] ; if (*p != pat0) goto fin;
 JNE mts_fin
 MOV [EBX],EDX ; *p = old;
 ADD EAX,0x1000 ; i += 0x1000;
 CMP EAX,[ESP+12+8] ; if (i <= end) goto mts_loop;
 JBE mts_loop
 POP EBX
 POP ESI
 POP EDI
 RET
mts_fin:
 MOV [EBX],EDX ; *p = old;
 POP EBX
 POP ESI
 POP EDI
 RET
```

```

![](https://i.imgur.com/GRixWcB.png)
到這一節可以看到這邊書中的內容可以去統計 memory 的容量從
0x00400000, 0xbfffffff 每 4k 統計
# 管理 memory
這一節前面有大致提到過怎麼去統計這一節是要講怎麼分配，在一台電腦裡每個不同的 application 都有各自不同的記憶體，這邊是再說要怎麼去 free
## bootpack.c
### HariMain
```c
#define MEMMAN_ADDR 0x003c0000 
void HariMain(void) 
{ 
	（中略）
	unsigned int memtotal;
	struct MEMMAN *memman = (struct MEMMAN *)MEMMAN_ADDR;
	（中略）
	memtotal = memtest(0x00400000, 0xbfffffff);
	memman_init(memman);
	memman_free(memman, 0x00001000, 0x0009e000); /* 0x00001000 - 0x0009efff */
	memman_free(memman, 0x00400000, memtotal - 0x00400000);
	（中略）
	sprintf(s, "memory %dMB free : %dKB",
			memtotal / (1024 * 1024), memman_total(memman) / 1024);
	putfonts8_asc(binfo->vram, binfo->scrnx, 0, 32, COL8_FFFFFF, s);
```

### alloc
```c
    #define MEMMAN_FREES 4090 /* 大约是32KB*/
	struct FREEINFO
	{ /* 可用信息 */
		unsigned int addr, size;
	};
	struct MEMMAN
	{ /* 内存管理 */
		int frees, maxfrees, lostsize, losts;
		struct FREEINFO free[MEMMAN_FREES];
	};
	void memman_init(struct MEMMAN * man)
	{
		man->frees = 0;	   /* 可用信息数目 */
		man->maxfrees = 0; /* 用于观察可用状况：frees的最大值 */
		man->lostsize = 0; /* 释放失败的内存的大小总和 */
		man->losts = 0;	   /* 释放失败次数 */
		return;
	}
	unsigned int memman_total(struct MEMMAN * man)
	/* 报告空余内存大小的合计 */
	{
		unsigned int i, t = 0;
		for (i = 0; i < man->frees; i++)
		{
			t += man->free[i].size;
		}
		return t;
	}
	unsigned int memman_alloc(struct MEMMAN * man, unsigned int size)
	/* 分配 */
	{
		unsigned int i, a;
		for (i = 0; i < man->frees; i++)
		{
			if (man->free[i].size >= size)
			{
				/* 找到了足够大的内存 */
				a = man->free[i].addr;
				man->free[i].addr += size;
				man->free[i].size -= size;
				if (man->free[i].size == 0)
				{
					/* 如果free[i]变成了0，就减掉一条可用信息 */
					man->frees--;
					for (; i < man->frees; i++)
					{
						man->free[i] = man->free[i + 1]; /* 代入结构体 */
					}
				}
				return a;
			}
		}
		return 0; /* 没有可用空间 */
	}

```
### free
```c
	 int memman_free(struct MEMMAN * man, unsigned int addr, unsigned int size)
	/* 释放 */
	{
		int i, j;
		/* 为便于归纳内存，将free[]按照addr的顺序排列 */
		/* 所以，先决定应该放在哪里 */
		for (i = 0; i < man->frees; i++)
		{
			if (man->free[i].addr > addr)
			{
				break;
			}
		}
		/* free[i - 1].addr < addr < free[i].addr */
		if (i > 0)
		{
			/* 前面有可用内存 */
			if (man->free[i - 1].addr + man->free[i - 1].size == addr)
			{
				/* 可以与前面的可用内存归纳到一起 */
				man->free[i - 1].size += size;
				if (i < man->frees)
				{
					/* 后面也有 */
					if (addr + size == man->free[i].addr)
					{
						/* 也可以与后面的可用内存归纳到一起 */
						man->free[i - 1].size += man->free[i].size;
						/* man->free[i]删除 */
						/* free[i]变成0后归纳到前面去 */
						man->frees--;
						for (; i < man->frees; i++)
						{
							man->free[i] = man->free[i + 1]; /* 结构体赋值 */
						}
					}
				}
				return 0; /* 成功完成 */
			}
		}
		/* 不能与前面的可用空间归纳到一起 */
		if (i < man->frees)
		{
			/* 后面还有 */
			if (addr + size == man->free[i].addr)
			{
				/* 可以与后面的内容归纳到一起 */
				man->free[i].addr = addr;
				man->free[i].size += size;
				return 0; /* 成功完成 */
			}
		}
		/* 既不能与前面归纳到一起，也不能与后面归纳到一起 */
		if (man->frees < MEMMAN_FREES)
		{
			/* free[i]之后的，向后移动，腾出一点可用空间 */
			for (j = man->frees; j > i; j--)
			{
				man->free[j] = man->free[j - 1];
			}
			man->frees++;
			if (man->maxfrees < man->frees)
			{
				man->maxfrees = man->frees; /* 更新最大值 */
			}
			man->free[i].addr = addr;
			man->free[i].size = size;
			return 0; /* 成功完成 */
		}
		/* 不能往后移动 */
		man->losts++;
		man->lostsize += size;
		return -1; /* 失败 */
	}
```

0x00000000 - 0x000fffff : 虽然在启动中会多次使用，但之后就变空。（1MB）
0x00100000 - 0x00267fff : 用于保存软盘的内容。（1440KB）
0x00268000 - 0x0026f7ff : 空（30KB）
0x0026f800 - 0x0026ffff : IDT （2KB）
0x00270000 - 0x0027ffff : GDT （64KB）
0x00280000 - 0x002fffff : bootpack.hrb（512KB）
0x00300000 - 0x003fffff : 栈及其他（1MB）
0x00400000 - : 空
這個是8.5 章節 作者提到的這邊有看到作者的用於記憶體管理的分布圖，他說他只是隨便挑其中，並沒有什麼跟硬體知識做關聯

	memman_free(memman, 0x00001000, 0x0009e000); /* 0x00001000 - 0x0009efff */
    這塊記憶體是幹嘛用的，可能是測試用的，可能後面看完才能來解釋這一塊，不前不知道用途
    
	memtotal = memtest(0x00400000, 0xbfffffff);
	memman_init(memman);
	memman_free(memman, 0x00400000, memtotal - 0x00400000);
   
memtotal = memtest(0x00400000, 0xbfffffff);
假設上限到 0x00400000 - 0xbfffffff 32mb
幾乎上一段程式碼只會走下面這些流程，依照他說的，這邊可能只是去free某一塊 記憶體然後標註為 free
也就是取一段範圍並設置

    man->free[i].addr = addr;
	man->free[i].size = size;
    
```c

	/* 既不能与前面归纳到一起，也不能与后面归纳到一起 */
		if (man->frees < MEMMAN_FREES)
		{
			/* free[i]之后的，向后移动，腾出一点可用空间 */
			for (j = man->frees; j > i; j--)
			{
				man->free[j] = man->free[j - 1];
			}
			man->frees++;
			if (man->maxfrees < man->frees)
			{
				man->maxfrees = man->frees; /* 更新最大值 */
			}
			man->free[i].addr = addr;
			man->free[i].size = size;
			return 0; /* 成功完成 */
		}
```
## 搭配 alloc 和 free 流程
這邊實際應用可能要結合 alloc 比較看得懂
![](https://i.imgur.com/QbgCynQ.png)

也就是
同一個 memman 可能會管理很多free 陣列 可以透過上層的 free 來計算目前可用的free陣列有多少，一個 free[0]
裡面又有分 size 和 addr 則他的意思就是
我先宣告有一塊記憶體位置

>   也就是 free[0]
> 	memman_free(memman, 0x00001000, 0x0009e000); /* 0x00001000 - 0x0009efff */
>   現在我要去申請兩塊記憶體
>   address1 = memman_alloc(memman,0x00001000);
>   address2 = memman_alloc(memman,0x00001000);
>   則分別存到 unsigned int  的位置
>   分別可得到
>   0x1000
>   0x2000
>   也就是記憶體目前的位移
>   從 free[0].addr + size 0x00001000+0x00001000 得到下一個addr的偏移量
>   和減去  free[0].size 預先的 free[0].size 當 size =0 則 這塊free 就沒辦法再用了
>   這一段就是 alloc 的程式碼內容

那麼在看 free程式碼就會比較好懂了
    也就是他內容的就是在找 free陣列裡的addr + size 的偏移 能夠剛好符合你所要記憶體區段
    也就是很像 glibc 裡面 malloc 和 free
    https://wzt.ac.cn/2019/03/15/glibc_analyse2/
    glibc 裡面free
    那麼free這個程式主要就是要怎麼把這一塊記憶體回收，避免某些記憶體不能去做讀寫與釋放
    作者這段程式碼來解釋就是
    
>    第一段
>    先找前面addr 到+ size 能不能符合你所釋放的區段有的話則進行合併，假設真的找到了則直接return 0
>    否則就進入到
>    第二段
>    要注意 man->free[i].addr 比 addr 大 所以 i 會小於  man->frees
>    假設第一段程式碼判斷完還是不行則代表 全部已經找完一遍了所以就找符合
>     (addr + size == man->free[i].addr)
>    這段程式碼又代表 不一定是最後但是 後面addr +size  還有其他記憶體位置
>    則更新 free 位置範圍
>    man->free[i].addr = addr;
> 	 man->free[i].size += size;
> 	 則這一塊的 free [i] 位置從 free[i].addr ~  free[i].addr+size
> 	 reutnr 0
>    第三段
>    最後則在小於MEMMAN_FREES 區段最大值 && if (i < man->frees) 第二區段條件符合但是
>    但是還是沒辦法alloc
>    addr + size == man->free[i].addr
>    找不到符合的區段，所以要產生一塊記憶體位置空間了，則假設下面片段
>    假設記憶體區段 9 和 10
```
        i= 9
        j= 10
        10 9
```
>    可以看到 i =9 的話 假設 j = 10 將原本10記憶體範圍則會指向 9的記憶體範圍(後面位置都要重新規劃)
>，則下一次10位置 可能會被重新分配成新的記憶體範圍
>    而當前記憶體區段 9的位置將被更新成目前新的記憶體範圍
```c
    man->frees++;
	if (man->maxfrees < man->frees)
	{
		man->maxfrees = man->frees; /* 更新最大值 */
	}
	man->free[i].addr = addr;
	man->free[i].size = size;
```

```c

#define MEMMAN_ADDR 0x003c0000

void HariMain(void)
{
	struct BOOTINFO *binfo = (struct BOOTINFO *) ADR_BOOTINFO;
	char s[40], mcursor[256], keybuf[32], mousebuf[128];
	int mx, my, i;
	struct MOUSE_DEC mdec;

	unsigned int memtotal;
	unsigned int address1;
	unsigned int address2;
	struct MEMMAN *memman = (struct MEMMAN *) MEMMAN_ADDR;

	init_gdtidt();
	init_pic();
	io_sti(); /* IDT/PIC的初始化已经完成，于是开放CPU的中断 */

	fifo8_init(&keyfifo, 32, keybuf);
	fifo8_init(&mousefifo, 128, mousebuf);
	io_out8(PIC0_IMR, 0xf9); /* 开放PIC1和键盘中断(11111001) */
	io_out8(PIC1_IMR, 0xef); /* 开放鼠标中断(11101111) */

	init_keyboard();
	enable_mouse(&mdec);
	memtotal = memtest(0x00400000, 0xbfffffff);
	init_palette();
	init_screen8(binfo->vram, binfo->scrnx, binfo->scrny);
	memman_init(memman);
	memman_free(memman, 0x00001000, 0x0009e000); /* 0x00001000 - 0x0009efff */

	
	sprintf(s, "memman : %x time",memman->free[0].size );
	putfonts8_asc(binfo->vram, binfo->scrnx, 0, 112, COL8_FFFFFF, s);
	
	address1 = memman_alloc(memman,0x00001000);

	sprintf(s, "memman : %x time",memman->free[0].size );
	putfonts8_asc(binfo->vram, binfo->scrnx, 0, 128, COL8_FFFFFF, s);
	
	address2 = memman_alloc(memman,0x00001000);
	memman_free(memman, 0x00400000, memtotal - 0x00400000);

	mx = (binfo->scrnx - 16) / 2; /* 计算画面中心坐标 */
	my = (binfo->scrny - 28 - 16) / 2;
	init_mouse_cursor8(mcursor, COL8_008484);
	putblock8_8(binfo->vram, binfo->scrnx, 16, 16, mx, my, mcursor, 16);
	sprintf(s, "(%d, %d)", mx, my);
	putfonts8_asc(binfo->vram, binfo->scrnx, 0, 0, COL8_FFFFFF, s);

	sprintf(s, "memory %dKB free : %dKB", memtotal / (1024), memman_total(memman) / 1024,((memtotal / (1024))- (memman_total(memman) / 1024)));
	putfonts8_asc(binfo->vram, binfo->scrnx, 0, 32, COL8_FFFFFF, s);
	sprintf(s, "usage : %dKB", ((memtotal / (1024))- (memman_total(memman) / 1024)));
	putfonts8_asc(binfo->vram, binfo->scrnx, 0, 48, COL8_FFFFFF, s);
	
	sprintf(s, "memman : %x time",memman->frees );
	putfonts8_asc(binfo->vram, binfo->scrnx, 0, 64, COL8_FFFFFF, s);
	
	
	sprintf(s, "memman : %x time",address1 );
	putfonts8_asc(binfo->vram, binfo->scrnx, 0, 80, COL8_FFFFFF, s);

	sprintf(s, "memman : %x time",address2 );
	putfonts8_asc(binfo->vram, binfo->scrnx, 0, 96, COL8_FFFFFF, s);

```
# alloc & free 4k
我们要编写一些总是以0x1000字节为单位进行内存分配和释放的函数，它们会把指定
的内存大小按0x1000字节为单位向上舍入（ roundup），而之所以要以0x1000字节为单位，是因为
笔者觉得这个数比较规整。另外，0x1000字节的大小正好是4KB

## memory.c
```c
unsigned int memman_alloc_4k(struct MEMMAN *man, unsigned int size) 
{ 
 unsigned int a; 
 size = (size + 0xfff) & 0xfffff000; 
 a = memman_alloc(man, size); 
 return a; 
} 
```

```c
int memman_free_4k(struct MEMMAN *man, unsigned int addr, unsigned int size) 
{ 
 int i; 
 size = (size + 0xfff) & 0xfffff000; 
 i = memman_free(man, addr, size); 
 return i; 
} 
```

## References

- 川合秀實，《30日でできる！OS自作入門》，毎日コミュニケーションズ，2006，ISBN 978-4-8399-1984-9. [Book record](https://ndlsearch.ndl.go.jp/books/R100000002-I000008118788)
- [yourtion/30dayMakeOS](https://github.com/yourtion/30dayMakeOS) — 本文使用的中文學習用原始碼倉庫。

