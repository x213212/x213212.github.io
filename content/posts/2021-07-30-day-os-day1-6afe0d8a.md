---
title: "30 DAY os helloword os"
date: "2021-07-08T05:04:00.008+08:00"
updated: "2021-07-08T12:53:58.525+08:00"
permalink: "/2021/07/30-day-os-day1.html"
original_url: "https://x8795278.blogspot.com/2021/07/30-day-os-day1.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6190132927717450455"
tags: ["osdev"]
layout: post
---

![](https://i.imgur.com/H3oaWz8.png)

# 30 Day os day 1
這本書對於操作系統可以有基本的認識，想在暑假看能不能完成一下kernel，論文大致上已經在後半段兩年內業應該沒問題，暑假可以來玩一下別的東西但是對於因為本來想要學習一下linux kernel 0.11 目前有看一些原始碼，但是完成了一些Process 調度，和中斷的實驗 這邊參考
https://jasonblog.github.io/note/qemu/72.html ,影片這邊講解蠻清楚的 https://study.163.com/series/1202806603.htm 這邊課程是線上的針對 linux kernel 0.11大致架構進行解說，
我選 30天os 這本書的話，總體前面大致上可以上結合一些 組合語言和 c語言可以對操作系統有一些認識，後面將會對 中斷和 滑鼠和 鍵盤到 畫面的繪圖會比較有感，linux kernel 0.11 則比較偏向於優化等等，可能會先完成 30天os 加深一下作業系統在去詳細閱讀linux kernel 0.11，目前已經完成一些實驗，在想看能不能把一些gui的畫面移植到linux kernel 0.11 ,
[riscv ](https://github.com/cccriscv/riscv_to_os_book/tree/master/04-xv6os/doc/cccnote),感覺也不錯。

# source code
> https://github.com/yourtion/30dayMakeOS
> 這邊有提供這本書的原始碼，這個程式碼竟然可以直接運行在windows10，有托於 qemu 模擬器
> 搭配古老的bat 後續衍伸到 makefile。
>
> 我這邊只會抽出比較重要的，主要還是要看整個大致架構我們在挑地方改。
> code 下載完後可以把資料夾內的tolset資料夾往上一層搬移，在挑選各個目錄day1 到 day30
> 這樣我們就可以編實驗邊看書上內容來對，目前只是跟著書上帶過，可能會有些忘記或者錯誤回頭再來修一下。
>
# run
day 1
![](https://i.imgur.com/UkLKgWM.png)
![](https://i.imgur.com/OQV0ZPy.png)
day 5
![](https://i.imgur.com/psnjgLc.png)
day 10
![](https://i.imgur.com/1oHBi3r.png)
> 短短10 天內容可以有這些畫面包括控制滑鼠等，不會像一些書比較枯燥看的到畫面我們在挑重點去改慢慢熟悉一下，30 天 OS 這本書，前面說一般不懂程式設計或者對OS有一些概念想加深的可以看這本書，他會一路舉C或 組合語言，和一些作業系統的概念慢慢深入，我覺得是蠻不錯的，對於專業的人可能會顯得很冗長，可以把它當作複習就可以了，我主要擷取我認為比較重要然後在一些模糊地段做出補充，大部分我還是保留原本書籍的解釋、盡量簡化、主要還是看我有特別有用引用的部分作者的部分可以當作輔助來看、這樣閱讀比較快一點。

# Day1  編譯與啟動
nask.exe這是作者自己做的compiler，看書主要是說以前的compiler 出來的程式碼並不是最佳化的，可能會加一些其他的asm進來，所以作者自己用自己的comiler 開發

## asm.bat
```bat
..\z_tools\nask.exe helloos.nas helloos.img
```

複製image 讓qumu模擬器去執行。
## run.bat
```bat
copy helloos.img ..\z_tools\qemu\fdimage0.bin
..\z_tools\make.exe	-C ../z_tools/qemu
```
## hello-os
前面並不會直接說程式碼內容，大概給一些框架
主要是這本書還是從有磁碟片那時代開始，作者程式碼大概80k要塞進去，一張1.44MB裡面可以知道這個作業系統多小他書中的對比是跟windows 一個 calc 計算機都比他的作業系統大。

仔細看程式碼的書中是從磁片的概念，比如說一張磁片可能分分成18扇區，扇區又有正面和反面，主要是要加載這些程式碼片段，讓你的系統能讀到你寫的程式，(http://godleon.blogspot.com/2008/01/machine-language-cpu-machine-language.html) 可以開始建立一些組合語言的概念，我也是新手可以順便邊查邊看。

# 概念補充
```
启动区..........（boot sector）软盘第一个的扇区称为启动区。那么什么是扇区呢？计算机读写软
盘的时候，并不是一个字节一个字节地读写的，而是以512字节为一个单位进行读
写。因此,软盘的512字节就称为一个扇区。一张软盘的空间共有1440KB，也就是
1474560字节，除以512得2880，这也就是说一张软盘共有2880个扇区。那为什么
第一个扇区称为启动区呢？那是因为计算机首先从最初一个扇区开始读软盘，然
后去检查这个扇区最后2个字节的内容。4 加工润色 

如果这最后2个字节不是0x55 AA，计算机会认为这张盘上没有所需的启动程序，就
会报一个不能启动的错误。（也许有人会问为什么一定是0x55 AA呢？那是当初的
设计者随便定的，笔者也没法解释）。如果计算机确认了第一个扇区的最后两个字
节正好是0x55 AA，那它就认为这个扇区的开头是启动程序，并开始执行这个程序。

IPL.........…....initial program loader的缩写。启动程序加载器。启动区只有区区512字节，实际的
操作系统不像hello-os这么小，根本装不进去。所以几乎所有的操作系统，都是把
加载操作系统本身的程序放在启动区里的。有鉴于此，有时也将启动区称为IPL。
但hello-os没有加载程序的功能，所以HELLOIPL这个名字不太顺理成章。如果有
人正义感特别强，觉得“这是撒谎造假，万万不能容忍！”，那也可以改成其他的
名字。但是必须起一个8字节的名字，如果名字长度不到8字节的话，需要在最后
补上空格。

启动..........….（boot）boot这个词本是长靴（boots）的单数形式。它与计算机的启动有什么关系
呢？一般应该将启动称为start的。实际上，boot这个词是bootstrap的缩写，原指靴
子上附带的便于拿取的靴带。但自从有了《吹牛大王历险记》（德国）这个故事
以后，bootstrap这个词就有了“自力更生完成任务”这种意思（大家如果对详情感
兴趣，可以在Google上查找，也可以在帮助和支持网页http://hrb.osask.jp上提问）。
而且，磁盘上明明装有操作系统，还要说读入操作系统的程序（即IPL）也放在磁
盘里，这就像打开宝物箱的钥匙就在宝物箱里一样，是一种矛盾的说法。这种矛
盾的操作系统自动启动机制，被称为bootstrap方式。boot这个说法就来源于此。如
果是笔者来命名的话，肯定不会用bootstrap 这么奇怪的名字，笔者大概会叫它“多
级火箭式”吧。
```
```
L1  db      0       ; 標記為 L1，大小為 1 byte，初始值：0
L2  dw      1000    ; 標記為 L2，大小為 1 word(2 bytes)，初始值：1000
L3  db      110101b ; 標記為 L3，大小為 1 byte，初始值：110101(2進位，10進位為 53)
L4  db      12h     ; 標記為 L4，大小為 1 byte，初始值：12(16進位，10進位為 18)
L5  db      17o     ; 標記為 L5，大小為 1 byte，初始值：17(8進位，10進位為 15)
L6  dd      1A92h   ; 標記為 L6，大小為 1 double word(4 bytes)，初始值：1A92(16進位)
L7  resb    1       ; 標記為 L7，大小為 1 byte，未初始化
L8  db      "A"     ; 標記為 L8，大小為 1 byte，初始值：A(10進位為 65)
```
那麼下面這段程式碼簡單來說，有可能就是預設磁碟盤讀取每 512 byte來讀，下面的這些程式碼都是 系統啟動需要必備的
目前這個實驗只能大致猜成這樣，後續程式碼會越來越有可讀性。
```asm
; hello-os
; TAB=4

; 标准FAT12格式软盘专用的代码 Stand FAT12 format floppy code

		DB		0xeb, 0x4e, 0x90
		DB		"HELLOIPL"		; 启动扇区名称（8字节）
		DW		512				; 每个扇区（sector）大小（必须512字节）
		DB		1				; 簇（cluster）大小（必须为1个扇区）
		DW		1				; FAT起始位置（一般为第一个扇区）
		DB		2				; FAT个数（必须为2）
		DW		224				; 根目录大小（一般为224项）
		DW		2880			; 该磁盘大小（必须为2880扇区1440*1024/512）
		DB		0xf0			; 磁盘类型（必须为0xf0）
		DW		9				; FAT的长度（必须是9扇区）
		DW		18				; 一个磁道（track）有几个扇区（必须为1l;8）
		DW		2				; 磁头数（必须是2）
		DD		0				; 不使用分区，必须是0
		DD		2880			; 重写一次磁盘大小
		DB		0,0,0x29		; 意义不明（固定）
		DD		0xffffffff		; （可能是）卷标号码
		DB		"HELLO-OS   "	; 磁盘的名称（必须为11字节，不足填空格）
		DB		"FAT12   "		; 磁盘格式名称（必须是8字节，不足填空格）
		RESB	18				; 先空出18字节

; 程序主体

		DB		0xb8, 0x00, 0x00, 0x8e, 0xd0, 0xbc, 0x00, 0x7c
		DB		0x8e, 0xd8, 0x8e, 0xc0, 0xbe, 0x74, 0x7c, 0x8a
		DB		0x04, 0x83, 0xc6, 0x01, 0x3c, 0x00, 0x74, 0x09
		DB		0xb4, 0x0e, 0xbb, 0x0f, 0x00, 0xcd, 0x10, 0xeb
		DB		0xee, 0xf4, 0xeb, 0xfd

; 信息显示部分

		DB		0x0a, 0x0a		; 换行两次
		DB		"hello, world2222"
		DB		0x0a			; 换行
		DB		0

		RESB	0x1fe-$			; 填写0x00直到0x001fe

		DB		0x55, 0xaa

; 启动扇区以外部分输出

		DB		0xf0, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00
		RESB	4600
		DB		0xf0, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00
		RESB	1469432

```
![](https://i.imgur.com/XNJbIAx.png)

# 計算開機偏移量與register 初探

程式碼將從 0x7c00載入
https://gist.github.com/letoh/2790559
考慮到 OS 需要的最少記憶體，希望能在 32KB 中盡量空出空間
從位址 0 開始，一直到 3FFH 為止規劃為中斷向量，因此無法使用
所以，只能載入到 32KB 的後半段了
MBR 中的開機碼需要空間以便存放資料或作為堆疊使用，要多保留 512 bytes
根據上述，32KB - 512B (MBR) - 512B (資料與堆疊) 就得到了 7C00H
看這樣子多留 1k? 多-次 512(?
![](https://i.imgur.com/q5iPXO8.png)
![](https://i.imgur.com/EwbUQo8.png)
![](https://i.imgur.com/sr01BTk.png)

16 bit register
```
AX——accumulator，累加寄存器
CX——counter，计数寄存器
DX——data，数据寄存器
BX——base，基址寄存器
SP——stack pointer，栈指针寄存器
BP——base pointer，基址指针寄存器
SI——source index，源变址寄存器
DI——destination index，目的变址寄存器
```
https://finalfrank.pixnet.net/blog/post/22992166
這邊對regitster 來看意思就是AX register 裡面還有分 AL 和 AH
https://blog.csdn.net/maoliran/article/details/88814537
EAX与AX不是独立的，EAX是32位的寄存器，而AX是EAX的低16位。

举例来说
mov eax, 12345678h
那么AX将会是eax的低16位，也就是5678h。
而如果此时
mov ax，3344h
那么eax的值将变为12343344h，所以对ax的赋值是会影响eax的。

同样，AH是ax的高8位，而AL是ax的低8位，这就是说ah为33h，al为44h。

```
AL——累加寄存器低位（accumulator low）
CL——计数寄存器低位（counter low）
DL——数据寄存器低位（data low）
BL——基址寄存器低位（base low）
AH——累加寄存器高位（accumulator high）
CH——计数寄存器高位（counter high）
DH——数据寄存器高位（data high）
BH——基址寄存器高位（base high）
```

32 bit register
Extend
```
EAX
ECX
EDX
EBX
ESP
EBP
ESI
EDI 
```
32位中的低16位就是AX，而
高16位既没有名字，也没有寄存器编号。也就是说，虽然我们可以把EAX作为2个16位寄存器来
用，但只有低16位用起来方便；如果我们要用高16位的话，就需要使用移位命令，把高16位移到
低16位后才能用。

segment register，
所以在这里一并给大家介绍一下吧。这些段寄存器都是16位寄存器。
```
ES——附加段寄存器（extra segment）
CS——代码段寄存器（code segment）
SS——栈段寄存器（stack segment）
DS——数据段寄存器（data segment）
FS——没有名称（segment part 2）
GS——没有名称（segment part 3）
```

簡單ASM概念補完之後，後續章節會慢慢補足register內容

```
; hello-os
; TAB=4

		ORG		0x7c00			; 指明程序装载地址

; 标准FAT12格式软盘专用的代码 Stand FAT12 format floppy code

		JMP		entry
		DB		0x90
		DB		"HELLOIPL"		; 启动扇区名称（8字节）
		DW		512				; 每个扇区（sector）大小（必须512字节）
		DB		1				; 簇（cluster）大小（必须为1个扇区）
		DW		1				; FAT起始位置（一般为第一个扇区）
		DB		2				; FAT个数（必须为2）
		DW		224				; 根目录大小（一般为224项）
		DW		2880			; 该磁盘大小（必须为2880扇区1440*1024/512）
		DB		0xf0			; 磁盘类型（必须为0xf0）
		DW		9				; FAT的长度（必??9扇区）
		DW		18				; 一个磁道（track）有几个扇区（必须为18）
		DW		2				; 磁头数（必??2）
		DD		0				; 不使用分区，必须是0
		DD		2880			; 重写一次磁盘大小
		DB		0,0,0x29		; 意义不明（固定）
		DD		0xffffffff		; （可能是）卷标号码
		DB		"HELLO-OS   "	; 磁盘的名称（必须为11字?，不足填空格）
		DB		"FAT12   "		; 磁盘格式名称（必??8字?，不足填空格）
		RESB	18				; 先空出18字节

```
> 組合語言可以大至推斷，
> 一路到	MOV		SI,msg 之前ax ss  ds es register 清除為0，sp (栈指针寄存器) 指向 0x7c00E(SP. 紀錄stack的top(最後被push進來)) 然後把msg 的 address 讀到 SI register
> 像是做邊 entry、putloop、fin、msg 那些都是lable，jmp 可以直接在Lable 和 address 進行跳轉，
> 假設沒有其他操作遇到label 也是繼續往下讀
>
例:
```
MOV		SI,msg
MOV		AL,[SI]
```
這邊就是把 si
是MOV指令有一个规则①，那就是源数据和目的数据必须位数相同。也就是说，能向AL
里代入的就只有BYTE，这样一来就可以省略BYTE，即可以写成：
MOV AL, [SI]
哦，这样就与程序中的写法一样了。现在总算把这个指令解释清楚了，所以这个指令的意思
就是“把SI地址的1个字节的内容读入AL中”
```
ADD		SI,1
SI +1
CMP		AL,0
```
比	    AL,0是否為0假設是 下面的 JE 則跳到 fin
```
JE		fin
HLT	 則是 cpu切為省電模式的 asm
```
否則就往下繼續讀下面的

(虽然制造厂家给我们准备好了BIOS，但其用法鲜为人知。不过这些很容易查到，笔者就做
了一个关于BIOS的网页，下面给大家介绍一下。
http://community.osdev.info/? (AT)BIOS
比如我们现在想要显示文字，先假设一次只显示一个字，那么具体怎么做才能知道这个功能
的使用方法呢？
首先，既然是要显示文字，就应该看跟显卡有关的函数。这么看来，INT 0x10好像有点关系，
于是在上面网页上搜索，然后就能找到以下内容（网页的原文为日语）。
显示一个字符
```
AH=0x0e; 
AL=character code; 
BH=0; 
BL=color code; 
返回值：无
注：beep、退格（back space）、CR、LF都会被当做控制字符处理)
```

```
MOV		AH,0x0e			; 显示一个文字
MOV		BX,15			; 指定字符颜色
INT		0x10			; 调用显卡BIOS
JMP		putloop
```

> 這段程式碼先不理解的話，就是只要填入相對應的值，並透過int 0x10發生中斷，讓cpu執行你發生中斷要發生的事情(鍵盤、>滑鼠、螢幕繪圖、等等)
>
>
> 書中的虛擬碼
> 剛剛的意思就是　先對register 進行初始化
> 把 msg搬移到 SI
> 每次LOOP都會 導致MSG 往下讀一個 BYTE 一直讀到MSG沒有資料則跳到(HLT)省電模式
> 否則 每次LOOP MSG [SI ]裡面 讀一個 BYTE SI+1 填入相對應的數值到 register 並呼叫中斷，顯示資料
> 這個就是把 day1 的顯示文字改為 day2 改為比較可讀。
```
entry: 
 AX = 0; 
 SS = AX; 
 SP = 0x7c00; 
 DS = AX; 
 ES = AX; 
 SI = msg; 
putloop: 
 AL = BYTE [SI]; 
 SI = SI + 1; 
 if (AL == 0) { goto fin; } 
 AH = 0x0e; 
 BX = 15; 
 INT 0x10; 
 goto putloop; 
fin: 
 HLT; 
 goto fin;
```
```
; 程序主体
entry:
		MOV		AX,0			; 初始化寄存器
		MOV		SS,AX
		MOV		SP,0x7c00
		MOV		DS,AX
		MOV		ES,AX

		MOV		SI,msg
putloop:
		MOV		AL,[SI]
		ADD		SI,1			; 给SI加1
		CMP		AL,0
		JE		fin
		MOV		AH,0x0e			; 显示一个文字
		MOV		BX,15			; 指定字符颜色
		INT		0x10			; 调用显卡BIOS
		JMP		putloop
fin:
		HLT						; 让CPU停止，等待指令
		JMP		fin				; 无限循环

msg:
		DB		0x0a, 0x0a		; 换行两次
		DB		"hello, worlds"
		DB		0x0a			; 换行
		DB		0

		RESB	0x7dfe-$		; 填写0x00直到0x001fe

		DB		0x55, 0xaa

```
# Initial Program Loader

## 讀取磁區
補充概念
![](https://i.imgur.com/28MvD6E.png)
> 综上所述，1张软盘有80个柱面，2个磁头，18个扇区，且一个扇区有512字节。所以，一张
> 软盘的容量是：
> 80×2×18×512 = 1 474 560 Byte = 1 440KB
> 含有IPL的启动区，位于C0-H0-S1（柱面0，磁头0，扇区1的缩写），下一个扇区是C0-H0-S2。
> 这次我们想要装载的就是这个扇区
> 其他几个寄存器我们也来依次看一下吧。CH、CL、DH、DL分别是柱面号、扇区号、磁头
> 号、驱动器号，一定不要搞错。在上面的程序中，柱面号是0，磁头号是0，扇区号是2，磁盘号
> 是0
>
> 0x13 中斷
>  磁盘读、写，扇区校验（verify），以及寻道（seek）
> AH=0x02;（读盘）
> AH=0x03;（写盘）
> AH=0x04;（校验）
> AH=0x0c;（寻道）
> AL=处理对象的扇区数;（只能同时处理连续的扇区）
> CH=柱面号 &0xff;
> CL=扇区号（0-5位）|（柱面号&0x300）>>2;
> DH=磁头号;
> DL=驱动器号；
> ES:BX=缓冲地址；(校验及寻道时不使用)
> 返回值：
> FLACS.CF=0: 沒有錯誤 AH =0
> FLAGS.CF==1：有错误，错误号码存入AH内（与重置（reset）功能一样）
> 我们这次用的是AH=0x02，哦，原来是“读盘”的意思。
>
> 剩下的大家还不明白的就是缓冲区地址了吧。这是个内存地址，表明我们要把从软盘上读出
> 的数据装载到内存的哪个位置。一般说来，如果能用一个寄存器来表示内存地址的话，当然会很
> 方便，但一个BX只能表示0～0xffff的值，也就是只有0～65535，最大才64K。大家的电脑起码也
> 都有64M内存，或者更多，只用一个寄存器来表示内存地址的话，就只能用64K的内存，这太可
> 惜了。
> 于是为了解决这个问题，就增加了一个叫EBX的寄存器，这样就能处理4G内存了。这是CPU
> 能处理的最大内存量，没有任何问题。但EBX的导入是很久以后的事情，在设计BIOS的时代，
> CPU甚至还没有32位寄存器，所以当时只好设计了一个起辅助作用的段寄存器（segment register）。
> 在指定内存地址的时候，可以使用这个段寄存器。
> 我们使用段寄存器时，以ES:BX这种方式来表示地址，写成“MOV AL,[ES:BX]”，它代表
> ES×16+BX的内存地址。我们可以把它理解成先用ES寄存器指定一个大致的地址，然后再用BX
> 来指定其中一个具体地址。

這邊就是
65535 *16 + 65535
![](https://i.imgur.com/ZQeTRfV.png)
![](https://i.imgur.com/9j2FfOU.png)
![](https://i.imgur.com/RPjqWYl.png)

这样如果在ES里代入0xffff，在BX里也代入0xffff，就是1 114 095字节，也就是说可以指定1M
以内的内存地址了。虽然这也还是远远不到64M，但当时英特尔公司的大叔们，好像觉得这就足
够了。在最初设计BIOS的时代，这种配置已经很能满足当时的需要了，所以我们现在也还是要
遵从这一规则。因此，大家就先忍耐一下这1MB内存的限制吧。
这次，我们指定了ES=0x0820，BX=0，所以软盘的数据将被装载到内存中0x8200到0x83ff的
地方。可能有人会想，怎么也不弄个整点的数，比如0x8000什么的，那多好。但0x8000～0x81ff
这512字节是留给启动区的，要将启动区的内容读到那里，所以就这样吧。
那为什么使用0x8000以后的内存呢？这倒也没什么特别的理由，只是因为从内存分布图上
看，这一块领域没人使用，于是笔者就决定将我们的“纸娃娃操作系统”装载到这一区域。
0x7c00～0x7dff用于启动区，0x7e00以后直到0x9fbff为止的区域都没有特别的用途，操作系统
可以随便使用。

到目前为止我们开发的程序完全没有考虑段寄存器，但事实上，不管我们要指定内存的什么地址，都必须同时指定段寄存器，这是规定。一般如果省略的话就会把“DS:”作为默认的段寄存器。
以前我们用的“MOV CX,[1234]”，其实是“MOV CX,[DS:1234]”的意思。“MOV AL,[SI]”，
也就是“MOV AL,[DS:SI]”的意思。在汇编语言中，如果每回都这样写就太麻烦了，所以可以
省略默认的段寄存器DS。
因为有这样的规则，所以DS 必须预先指定为0，否则地址的值就要加上这个数的16倍，就会
读写到其他的地方，引起混乱。

现在启动区程序已经写得差不多了。如果算上系统加载时自动装载的启动扇区，那现在我们
已经能够把软盘最初的10 × 2 × 18 × 512 = 184 320 byte=180KB内容完整无误地装载到内存里了。
如果运行“make install”，把程序安装到磁盘上，然后用它来启动电脑的话，我们会发现装载过
程还是挺花时间的。这证明我们的程序运行正常。画面显示依然没什么变化，但这个程序已经用
从软盘读取的数据填满了内存0x08200～ 0x34fff的地方。
>
> 這邊就是後續大概的程式碼，主要內容就是因為 以前磁碟片 可能會發生讀不到的情況所以作者加入了 嘗試重讀 磁區
> 再來就是 多增加了讀取多讀扇區18個 和 10個柱面 *2 有兩面 每一個 512  的到 180k

ipl10.nas
```
; 程序主体

entry:
		MOV		AX,0			; 初始化寄存器
		MOV		SS,AX
		MOV		SP,0x7c00
		MOV		DS,AX

; 读取磁盘

		MOV		AX,0x0820
		MOV		ES,AX
		MOV		CH,0			; 柱面0
		MOV		DH,0			; 磁头0
		MOV		CL,2			; 扇区2

readloop:
		MOV		SI,0			; 记录失败次数寄存器

retry:
		MOV		AH,0x02			; AH=0x02 : 读入磁盘
		MOV		AL,1			; 1个扇区
		MOV		BX,0
		MOV		DL,0x00			; A驱动器
		INT		0x13			; 调用磁盘BIOS
		JNC		next			; 没出错则跳转到next
		ADD		SI,1			; 往SI加1
		CMP		SI,5			; 比较SI与5
		JAE		error			; SI >= 5 跳转到error
		MOV		AH,0x00
		MOV		DL,0x00			; A驱动器
		INT		0x13			; 重置驱动器
		JMP		retry
next:
		MOV		AX,ES			; 把内存地址后移0x200（512/16十六进制转换）
		ADD		AX,0x0020
		MOV		ES,AX			; ADD ES,0x020因为没有ADD ES，只能通过AX进行
		ADD		CL,1			; 往CL里面加1
		CMP		CL,18			; 比较CL与18
		JBE		readloop		; CL <= 18 跳转到readloop
		MOV		CL,1
		ADD		DH,1
		CMP		DH,2
		JB		readloop		; DH < 2 跳转到readloop
		MOV		DH,0
		ADD		CH,1
		CMP		CH,CYLS
		JB		readloop		; CH < CYLS 跳转到readloop

; 读取完毕，跳转到haribote.sys执行！
		MOV		[0x0ff0],CH		; IPLがどこまで読んだのかをメモ
		JMP		0xc200

error:
		MOV		SI,msg

putloop:
		MOV		AL,[SI]
		ADD		SI,1			; 给SI加1
		CMP		AL,0
		JE		fin
		MOV		AH,0x0e			; 显示一个文字
		MOV		BX,15			; 指定字符颜色
		INT		0x10			; 调用显卡BIOS
		JMP		putloop

fin:
		HLT						; 让CPU停止，等待指令
		JMP		fin				; 无限循环

msg:
		DB		0x0a, 0x0a		; 换行两次
		DB		"load error"
		DB		0x0a			; 换行
		DB		0

		RESB	0x7dfe-$		; 填写0x00直到0x001fe

		DB		0x55, 0xaa

```

# 開始進入並打造作業系統
作者推測

1) 文件名会写在0x002600以后的地方；
(2) 文件的内容会写在0x004200以后的地方。
这就是我们一直想知道的东西。
了解了这一点，下面要做的事就简单了。我们将操作系统本身的内容写到名为haribote.sys文
件中，再把它保存到磁盘映像里，然后我们从启动区执行这个haribote.sys就行了。接下来我们就
来做这件事。
6 从启动区执行操作系统
那么，要怎样才能执行磁盘映像上位于0x004200号地址的程序呢？现在的程序是从启动区开
始，把磁盘上的内容装载到内存0x8000号地址，所以磁盘0x4200处的内容就应该位于内存
0x8000+0x4200=0xc200号地址。

这样的话，我们就往haribote.nas里加上ORG 0xc200，然后在ipl.nas处理的最后加上JMP
0xc200这个指令。这样修改后，得到的就是“projects/03_day”下的harib00f。
赶紧运行“make run”，目前什么都没发生。那么程序到底有没有执行haribote.sys呢？大家可
能会有点担心。所以，下面我们让haribote.sys跳出来表现一下

haribote.nas
```
; haribote-os 
; TAB=4 
 ORG 0xc200 ; 这个程序将要被装载到内存的什么地方呢？
 MOV AL,0x13 ; VGA显卡，320x200x8位彩色
 MOV AH,0x00 
 INT 0x10 
fin: 
 HLT 
 JMP fin 
```

设置显卡模式（video mode）
 AH=0x00;
 AL=模式：（省略了一些不重要的画面模式）
 0x03：16色字符模式，80 × 25
 0x12：VGA 图形模式，640 × 480 × 4位彩色模式，独特的4面存储模式
 0x13：VGA 图形模式，320 × 200 × 8位彩色模式，调色板模式
 0x6a：扩展VGA 图形模式，800 × 600 × 4位彩色模式，独特的4面存储模式
（有的显卡不支持这个模式）
 返回值：无
参照以上说明，我们暂且选择0x13画面模式，因为8位彩色模式可以使用256种颜色，这一点
看来不错。
如果画面模式切换正常，画面应该会变为一片漆黑。也就是说，因为可以看到画面的变化，
所以能判断程序是否运行正常。由于变成了图形模式，因此光标会消失。

![](https://i.imgur.com/bznoHlR.png)

> 經過一連串的加載
> 我們從 boot設備 加載 磁碟片到 memory 到 執行我們的程式經過偏移得出我們在 0xc200 系統會自動執行我們的程式
> 我們的程式再透過中斷 切成顯示模式，這樣我們就大致完成畫面的切換了後續將會在上面實現 asm 與 c語言的 互相呼叫
>

# 邁向 32位元
今天还有些时间，再往下讲一点吧。
现在，汇编语言的开发告一段落，我们要开始以C语言为主进行开发了，这是我们当前的目标。
笔者准备的C编译器，只能生成32位模式的机器语言。如果一定要生成16位模式机器语言，
虽然也不是做不到，但是很费事，还没什么好处，所以就用32位模式吧。
所谓32位模式，指的是CPU的模式。CPU有16位和32位两种模式。如果以16位模式启动的话，
用AX和CX等16位寄存器会非常方便，但反过来，像EAX和ECX等32位的寄存器，使用起来就很
麻烦。另外，16位模式和32位模式中，机器语言的命令代码不一样。同样的机器语言，解释的方
法也不一样，所以16位模式的机器语言在32位模式下不能运行，反之亦然。
32位模式下可以使用的内存容量远远大于1MB。另外，CPU的自我保护功能（识别出可疑的
机器语言并进行屏蔽，以免破坏系统）在16位下不能用，但32位下能用。既然有这么多优点，当
然要使用32位模式了。

可是，如果用32位模式就不能调用BIOS功能了。这是因为BIOS是用16位机器语言写的。如
果我们有什么事情想用BIOS来做，那就全部都放在开头先做，因为一旦进入32位模式就不能调
用BIOS函数了。（当然，也有从32位返回到16位的方法，但是非常费工夫，所以本书不予赘述。）
再回头说说要使用BIOS做的事情。画面模式的设定已经做完了，接下来还想从BIOS得到键
盘状态。所谓键盘状态，是指NumLock是ON还是OFF等这些状态。
所以，我们这次只修改了haribote.nas。修改后的程序就是projects/03_day下的harib00h

haribote.nas
```
; haribote-os 
; TAB=4 
; 有关BOOT_INFO 
CYLS EQU 0x0ff0 ; 设定启动区
LEDS EQU 0x0ff1 
VMODE EQU 0x0ff2 ; 关于颜色数目的信息。颜色的位数。
SCRNX EQU 0x0ff4 ; 分辨率的X（screen x）
SCRNY EQU 0x0ff6 ; 分辨率的Y（screen y）
VRAM EQU 0x0ff8 ; 图像缓冲区的开始地址
 ORG 0xc200 ; 这个程序将要被装载到内存的什么地方呢？
 MOV AL,0x13 ; VGA 显卡，320x200x8位彩色
 MOV AH,0x00 
 INT 0x10 
 MOV BYTE [VMODE],8 ; 记录画面模式
 MOV WORD [SCRNX],320 
 MOV WORD [SCRNY],200 
 MOV DWORD [VRAM],0x000a0000 
;用BIOS取得键盘上各种LED指示灯的状态
 MOV AH,0x02 
 INT 0x16 ; keyboard BIOS 
 MOV [LEDS],AL 
fin: 
 HLT 
 JMP fin
```
> 這邊忘記說再做存值的時候
> BYTE []
> WORD []  
> 要去指向 位置的 型態
> 很像C 語言 你沒有定義型態去存的話，他不知道對應到 Address  是佔 幾個 BYTE
> MOV BYTE [VMODE],8 ; 记录画面模式
> MOV WORD [SCRNX],320
> MOV WORD [SCRNY],200
> MOV DWORD [VRAM],0x000a0000

看一下程序就能明白，设置画面模式之后，还把画面模式的信息保存在了内存里。这是因为，
以后我们可能要支持各种不同的画面模式，这就需要把现在的设置信息保存起来以备后用。我们
暂且将启动时的信息称为BOOT_INFO。INFO是英文information（信息）的缩写。

[VRAM]里保存的是0xa0000。在电脑的世界里，VRAM指的是显卡内存（video RAM），也
就是用来显示画面的内存。这一块内存当然可以像一般的内存一样存储数据，但VRAM的功能不
仅限于此，它的各个地址都对应着画面上的像素，可以利用这一机制在画面上绘制出五彩缤纷的
图案。
其实VRAM分布在内存分布图上好几个不同的地方。这是因为，不同画面模式的像素数也不
一样。当画面模式为〇×时使用这个VRAM；而画面模式为◇△时可能使用那个VRAM，像这样，
不同画面模式可以使用的内存也不一样。所以我们就预先把要使用的VRAM地址保存在
BOOT_INFO里以备后用。
这次VRAM的值是0xa0000。这个值又是从哪儿得来的呢？还是来看看我们每次都参考的
（AT）BIOS支持网页。在INT 0x10的说明的最后写着，这种画面模式下“VRAM是0xa0000～0xaffff
的64KB”。
另外，我们还把画面的像素数、颜色数，以及从BIOS取得的键盘信息都保存了起来。保存
位置是在内存0x0ff0附近。从内存分布图上看，这一块并没被使用，所以应该没问题。

雖然看不到那個網頁的bios 不過現在我先猜測 0xa0000～0xaffff 對應到的記憶體後面我們將要對裡面的內容進行填值
再來就是 在把 keyboard 裡面的 值讀取到 沒有人用到的0x0ff0，主要原因就是，我們後面可能可以透過直接訪問這些記憶體的位置來得到，bios 的一些載入訊息。

# 導入c 語言
程序里添加和修改了很多内容。首先是haribote.sys，它的前半部分是用汇编语言编写的，而
后半部分则是用C语言编写的。所以以前的文件名haribote.nas也随之改成了asmhead.nas。并且，
为了调用C语言写的程序，添加了100行左右的汇编代码。
> 這邊因為程式碼涉及中斷和一些 usermode 和 kernel 保護模式，後續會慢慢補充

這個地方作者想要透過某些方式可以去呼叫組合語言
## bootpack.c
```
void HariMain(void) 
{ 
fin: 
 /*这里想写上HLT，但C语言中不能用HLT!*/ 
 goto fin; 
}
```

那么，这个bootpack.c是怎样变成机器语言的呢？如果不能变成机器语言，就是说得再多也
没有意义。这个步骤很长，让我们看一看。

1. 首先，使用cc1.exe从bootpack.c生成bootpack.gas。
2. 第二步，使用gas2nask.exe从bootpack.gas生成bootpack.nas。
3. 第三步，使用nask.exe从bootpack.nas生成bootpack.obj。
4. 第四步，使用obi2bim.exe从bootpack.obj生成bootpack.bim。
5. 最后，使用bim2hrb.exe从bootpack.bim生成bootpack.hrb。
6. 这样就做成了机器语言，再使用copy指令将asmhead.bin与bootpack.hrb单纯结合到起来，
就成了haribote.sys。

## naskfunc.nas
```
; naskfunc 
; TAB=4 
[FORMAT "WCOFF"] ; 制作目标文件的模式
[BITS 32] ; 制作32位模式用的机械语言
;制作目标文件的信息
[FILE "naskfunc.nas"] ; 源文件名信息
 GLOBAL①
 _io_hlt ; 程序中包含的函数名
;以下是实际的函数
[SECTION .text] ; 目标文件中写了这些之后再写程序
_io_hlt: ; void io_hlt(void); 
 HLT 
 RET
```

## bootpack.c
```c
/*告诉C编译器，有一个函数在别的文件里*/ 
void io_hlt(void); 
/*是函数声明却不用{ }，而用;，这表示的意思是：函数是在别的文件中，你自己找一下吧！*/ 
void HariMain(void) 
{ 
fin: 
 io_hlt(); /*执行naskfunc.nas里的_io_hlt*/ 
 goto fin; 
}
```

個人覺得這一小節，主要是在解決 asm call c or c call asm 等等，後續章節應該會補足這塊。 (還沒看到最後

# 使用 c 語言 寫入記憶體
在上一個小節，我們成功讓螢幕變成vga模式，有提到一塊記憶體空間叫做 vram 這一塊記憶體空間有一段記憶體位置
 0xa0000～0xaffff ,現在我們要為這一塊記憶體位置進行修改

## naskfunc.nas
```asm
_write_mem8: ; void write_mem8(int addr, int data); 
 MOV ECX,[ESP+4] ; [ESP + 4]中存放的是地址，将其读入ECX 
 MOV AL,[ESP+8] ; [ESP + 8]中存放的是数据，将其读入AL 
 MOV [ECX],AL 
 RET
```
第一个数字的存放地址：[ESP + 4]
第二个数字的存放地址：[ESP + 8]
第三个数字的存放地址：[ESP + 12]
第四个数字的存放地址：[ESP + 16]
个函数类似于C语言中的“write_mem8（0x1234,0x56）;”语句，动作上相当于“MOV
BYTE[0x1234],0x56”。顺便说一下，addr是address的缩写，在这里用它来表示地址。

> 對應到他講的應該是 esp +4 = addr esp +8 = data以此類推

## bootpack.c
```c
void io_hlt(void); 
void write_mem8(int addr, int data); 
void HariMain(void) 
{ 
 int i; /*变量声明：i是一个32位整数*/ 
 for (i = 0xa0000; i <= 0xaffff; i++) { 
 write_mem8(i, 15); /* MOV BYTE [i],15 */ 
 } 
 for (;;) { 
 io_hlt(); 
 } 
} 
```

![](https://i.imgur.com/8uUgQRg.png)

# 繪畫條文
上一小節全部填為15 對應到 顏色就是 白色
## bootpack.c
```c
for (i = 0xa0000; i <= 0xaffff; i++) { 
 write_mem8(i, i & 0x0f); 
 } 
```
![](https://i.imgur.com/WakXEH8.png)

# 替換 write_mem8
> 上述兩個小節等效程式碼，主要用c語言的 Pointer 裡面有針對 asm 和 pointer 的方式介紹這邊就不多做敘述，
> 主要的意思就是 當你宣告
> char p
> p= i 帶入的就是記憶體位置
> MOV [ 0x1234], 0x56
> 這邊在記憶體位置是錯誤的
> char *p
> p= i 帶入的就是記憶體位置
> MOV [BYTE][ 0x1234], 0x56
> 當有人放入記憶體位置空間的話進行取值將會轉為相對應的 type 並存入
> 下面程式碼就可以看到
> p=i
> *p 在進行取值，而在第一小節我們用的是 asm 的 function 再透過操縱ESP 來取值

下面的程式碼 不用 write_mem8也可以進行讀寫記憶。

```c
void HariMain(void) 
{ 
 int i; /*变量声明。变量i是32位整数*/ 
 char *p; /*变量p，用于BYTE型地址*/ 
 for (i = 0xa0000; i <= 0xaffff; i++) { 
 p = i; /*代入地址*/ 
 *p = i & 0x0f; 
 /*这可以替代write_mem8(i, i & 0x0f);*/ 
 } 
 for (;;) { 
 io_hlt(); 
 } 
} 
```
# 設定顏色
好了，到现在为止我们的话题都是以C语言为中心的，但我们的目的不是为了掌握C语言，
而是为了制作操作系统，操作系统中是不需要条纹图案之类的。我们继续来做操作系统吧。
可能大家马上就想描绘一个操作系统模样的画面，但在此之前要先做一件事，那就是处理颜
色问题。这次使用的是320× 200的8位颜色模式，色号使用8位（二进制）数，也就是只能使用0～
255的数。我想熟悉电脑颜色的人都会知道，这是非常少的。一般说起指定颜色，都是用#ffffff
一类的数。这就是RGB（红绿蓝）方式，用6位十六进制数，也就是24位（二进制）来指定颜色。
8位数完全不够。那么，该怎么指定#ffffff方式的颜色呢？
这个8位彩色模式，是由程序员随意指定0～255的数字所对应的颜色的。比如说25号颜色对
应#ffffff，26号颜色对应#123456等。这种方式就叫做调色板（palette）。
如果像现在这样，程序员不做任何设定，0号颜色就是#000000，15号颜色就是#ffffff。其他
>
> 我們在第一節提到的就是15，對應到顏色就是白色 15号颜色就是#ffffff 2(bin)

#000000:黑 #00ffff:浅亮蓝 #000084:暗蓝
#ff0000:亮红 #ffffff:白 #840084:暗紫
#00ff00:亮绿 #c6c6c6:亮灰 #008484:浅暗蓝
#ffff00:亮黄 #840000:暗红 #848484:暗灰
#0000ff:亮蓝 #008400:暗绿
#ff00ff:亮紫 #848400:暗黄

# 增加調色盤
## bootpack.c
```c
void io_hlt(void); 
void io_cli(void); 
void io_out8(int port, int data); 
int io_load_eflags(void); 
void io_store_eflags(int eflags); 
/*就算写在同一个源文件里，如果想在定义前使用，还是必须事先声明一下。*/ 
void init_palette(void); 
void set_palette(int start, int end, unsigned char *rgb); 
void HariMain(void) 
{ 
 int i; /* 声明变量。变量i是32位整数型 */ 
 char *p; /* 变量p是BYTE [...]用的地址 */ 
 init_palette(); /* 设定调色板 */ 
 p = (char *) 0xa0000; /* 指定地址 */ 
 for (i = 0; i <= 0xffff; i++) { 
 p[i] = i & 0x0f; 
 } 
 for (;;) { 
 io_hlt(); 
 } 
} 
void init_palette(void) 
{ 
 static unsigned char table_rgb[16 * 3] = { 
 0x00, 0x00, 0x00, /* 0:黑 */ 6 色号设定（harib01f） 
 0xff, 0x00, 0x00, /* 1:亮红 */ 
 0x00, 0xff, 0x00, /* 2:亮绿 */ 
 0xff, 0xff, 0x00, /* 3:亮黄 */ 
 0x00, 0x00, 0xff, /* 4:亮蓝 */ 
 0xff, 0x00, 0xff, /* 5:亮紫 */ 
 0x00, 0xff, 0xff, /* 6:浅亮蓝 */ 
 0xff, 0xff, 0xff, /* 7:白 */ 
 0xc6, 0xc6, 0xc6, /* 8:亮灰 */ 
 0x84, 0x00, 0x00, /* 9:暗红 */ 
 0x00, 0x84, 0x00, /* 10:暗绿 */ 
 0x84, 0x84, 0x00, /* 11:暗黄 */ 
 0x00, 0x00, 0x84, /* 12:暗青 */ 
 0x84, 0x00, 0x84, /* 13:暗紫 */ 
 0x00, 0x84, 0x84, /* 14:浅暗蓝 */ 
 0x84, 0x84, 0x84 /* 15:暗灰 */ 
 }; 
 set_palette(0, 15, table_rgb); 
 return; 
 /* C语言中的static char语句只能用于数据，相当于汇编中的DB指令 */ 
} 
void set_palette(int start, int end, unsigned char *rgb) 
{ 
 int i, eflags; 
 eflags = io_load_eflags(); /* 记录中断许可标志的值*/ 
 io_cli(); /* 将中断许可标志置为0，禁止中断 */ 
 io_out8(0x03c8, start); 
 for (i = start; i <= end; i++) { 
 io_out8(0x03c9, rgb[0] / 4); 
 io_out8(0x03c9, rgb[1] / 4); 
 io_out8(0x03c9, rgb[2] / 4); 
 rgb += 3; 
 } 
 io_store_eflags(eflags); /* 复原中断许可标志 */ 
 return; 
}
```
## init_palette
```c
void init_palette(void) 
{ 
 static unsigned char table_rgb[16 * 3] = { 
 0x00, 0x00, 0x00, /* 0:黑 */ 6 色号设定（harib01f） 
 0xff, 0x00, 0x00, /* 1:亮红 */ 
 0x00, 0xff, 0x00, /* 2:亮绿 */ 
 0xff, 0xff, 0x00, /* 3:亮黄 */ 
 0x00, 0x00, 0xff, /* 4:亮蓝 */ 
 0xff, 0x00, 0xff, /* 5:亮紫 */ 
 0x00, 0xff, 0xff, /* 6:浅亮蓝 */ 
 0xff, 0xff, 0xff, /* 7:白 */ 
 0xc6, 0xc6, 0xc6, /* 8:亮灰 */ 
 0x84, 0x00, 0x00, /* 9:暗红 */ 
 0x00, 0x84, 0x00, /* 10:暗绿 */ 
 0x84, 0x84, 0x00, /* 11:暗黄 */ 
 0x00, 0x00, 0x84, /* 12:暗青 */ 
 0x84, 0x00, 0x84, /* 13:暗紫 */ 
 0x00, 0x84, 0x84, /* 14:浅暗蓝 */ 
 0x84, 0x84, 0x84 /* 15:暗灰 */ 
 }; 
 set_palette(0, 15, table_rgb); 
 return; 
 /* C语言中的static char语句只能用于数据，相当于汇编中的DB指令 */ 
} 
```
> 裡面覺得還蠻有趣的是
> char a[3];意味著
> a:
>  RESB 3
> RESB 為保留位置提出這個概念後。
>
> 在 C語言意味者下面這兩個一樣
> char a[3]= { 1,2,3 };
>
> char a[3];
> a[0] = 1;
> a[1] = 2;
> a[2] = 3;
> 這時候作者就覺得
>
> 那么这次，应该代入的值共有16× 3=48个。笔者不希望大家做如此多的赋值语句。每次赋值
> 都至少要消耗3个字节，这样算下来光这些赋值语句就要花费将近150字节，这太不值了。
> 其实写成下面这样一般的DB形式，不就挺好吗。
> table_rgb:
>  DB 0x00, 0x00, 0x00, 0xff, 0x00, 0x00, 0x00, 0xff, 0x00,

所以衍伸出
這些寫法，反正就是第一用 unsigned 怕 compiler 把 0xff 轉成 -1 之類的東西
再來這些就是意味著三個一組代表著RGB等等，不同的組合對應不同顏色等等
```
 static unsigned char table_rgb[16 * 3] = { 
 0x00, 0x00, 0x00,
```
下面是作者的解釋

>  char型的变量有3种模式，分别是signed型、unsigned型和未指定型。signed型用于处理128～
> 127的整数。它虽然也能处理负数，扩大了处理范围，很方便，但能够处理的最大值却减小了一
> 半。unsigned型能够处理0～255的整数。未指定型是指没有特别指定时，可由编译器决定是
> unsigned还是signed。6 色号设定（harib01f） …… 79
>
> 在这个程序里，多次出现了0xff这个数值，也就是255，我们想用它来表示最大亮度，如果它
> 被误解成负数（0xff会被误解成1）就麻烦了。虽然我们不清楚亮度比0还弱会是什么概念，但
> 无论如何不能产生这种误解。所以我们决定将这个数设定为unsigned。顺便提一句，int和short也
> 分signed和unsigned。……好了，关于init_palette的说明就到此为止。

##  set_palette
> 這邊作者為io_out8 這些都是在對 io 設備送出訊號
> 這邊提出 Port 的概念，也就是我們在對這些設備號 0x3c8、0x3c9 送出訊號

video DA converter”，其中有以下记述。

* 调色板的访问步骤。
* 首先在一连串的访问中屏蔽中断（比如CLI）。
* 将想要设定的调色板号码写入0x03c8，紧接着，按R，G，B的顺序写入0x03c9。如果还
* 想继续设定下一个调色板，则省略调色板号码，再按照RGB的顺序写入0x03c9就行了。
* 如果想要读出当前调色板的状态，首先要将调色板的号码写入0x03c7，再从0x03c9读取3
* 次。读出的顺序就是R，G，B。如果要继续读出下一个调色板，同样也是省略调色板号
* 码的设定，按RGB的顺序读出。
* 如果最初执行了CLI，那么最后要执行STI

首先是CLI和STI。所谓CLI，是将中断标志（interrupt flag）置为0的指令（clear interrupt flag）。
STI是要将这个中断标志置为1的指令（set interrupt flag）。而标志，是指像以前曾出现过的进位标
志一样的各种标志，也就是说在CPU中有多种多样的标志。更改中断标志有什么好处呢？正如其
名所示，它与CPU的中断处理有关系。当CPU遇到中断请求时，是立即处理中断请求（中断标志6 色号设定（harib01f）
为1），还是忽略中断请求（中断标志为0），就由这个中断标志位来设定。

這邊後續章節、在控制滑鼠和鍵盤的時候會講到 中斷在後面再詳細串起來

## EFLAGS 特殊 register
> 在前面的時候，當我執行 JC 或者 JMP 那些額外判斷的FLAG 會有疑問，到底這些指令的結果存到哪裡、比較的結果、有沒有進位等等、在依照相對應的值進行跳轉或處理，其實那些指令就是觀察這些FLAG。

![](https://i.imgur.com/jgcmhbk.png)

下面再来介绍一下EFLAGS这一特别的寄存器。这是由名为FLAGS的16位寄存器扩展而来的
32位寄存器。FLAGS是存储进位标志和中断标志等标志的寄存器。进位标志可以通过JC或JNC等
跳转指令来简单地判断到底是0还是1。但对于中断标志，没有类似的JI或JNI命令，所以只能读入
EFLAGS，再检查第9位是0还是1。顺便说一下，进位标志是EFLAGS的第0位。

set_palette中想要做的事情是在设定调色板之前首先执行CLI，但处理结束以后一定要恢复中
断标志，因此需要记住最开始的中断标志是什么。所以我们制作了一个函数io_load_eflags，读取
最初的eflags值。处理结束以后，可以先看看eflags的内容，再决定是否执行STI，但仔细想一想，
也没必要搞得那么复杂，干脆将eflags的值代入EFLAGS，中断标志位就恢复为原来的值了。函数
io_store_eflags就是完成这个处理的。
估计不说大家也知道了，CLI也好，STI也好，EFLAGS的读取也好，EFLAGS的写入也好，
都不能用C语言来完成。所以我们就努力一下，用汇编语言来写吧。

> 也就是說按照他的 BIOS 要控制調色板就要按照那些流程，對下面這段程式碼來講
> 他透過
> PUSHFD和POPFD
> 來進行存入 EFlage和取出

也就是说，“PUSHFD POP EAX”，是指首先将EFLAGS压入栈，再将弹出的值代入EAX。
所以说它代替了“MOV EAX,EFLAGS”。另一方面，PUSH EAX POPFD正与此相反，它相当于
“MOV EFLAGS,EAX”。
![](https://i.imgur.com/TJ7Y4VJ.png)

```c
void set_palette(int start, int end, unsigned char *rgb) 
{ 
 int i, eflags; 
 eflags = io_load_eflags(); /* 记录中断许可标志的值*/ 
 io_cli(); /* 将中断许可标志置为0，禁止中断 */ 
 io_out8(0x03c8, start); 
 for (i = start; i <= end; i++) { 
 io_out8(0x03c9, rgb[0] / 4); 
 io_out8(0x03c9, rgb[1] / 4); 
 io_out8(0x03c9, rgb[2] / 4); 
 rgb += 3; 
 } 
 io_store_eflags(eflags); /* 复原中断许可标志 */ 
 return; 
}
```

作者在這一小節，又放了一些東西、我們主要看
## io_load_eflags
```ASM
io_load_eflags: ; int io_load_eflags(void); 
 PUSHFD ; 指 PUSH EFLAGS 
 POP EAX 
 RET 
```
## io_store_eflags
```ASM
_io_store_eflags: ; void io_store_eflags(int eflags); 
 MOV EAX,[ESP+4] 6 色号设定（harib01f）

 PUSH EAX 
 POPFD ; 指 POP EFLAGS 
 RET
```
## naskfunc.nas
```ASM
; naskfunc 
; TAB=4 
[FORMAT "WCOFF"] ; 制作目标文件的模式 
[INSTRSET "i486p"] ; 使用到486为止的指令
[BITS 32] ; 制作32位模式用的机器语言
[FILE "naskfunc.nas"] ; 源程序文件名
 GLOBAL _io_hlt, _io_cli, _io_sti, io_stihlt 
 GLOBAL _io_in8, _io_in16, _io_in32 
 GLOBAL _io_out8, _io_out16, _io_out32 
 GLOBAL _io_load_eflags, _io_store_eflags 
[SECTION .text] 
_io_hlt: ; void io_hlt(void); 
 HLT 
 RET 
_io_cli: ; void io_cli(void); 
 CLI 
 RET 
_io_sti: ; void io_sti(void); 
 STI 
 RET 
_io_stihlt: ; void io_stihlt(void); 
 STI 
 HLT 
 RET 
_io_in8: ; int io_in8(int port); 
 MOV EDX,[ESP+4] ; port 
 MOV EAX,0 
 IN AL,DX 
 RET 
_io_in16: ; int io_in16(int port); 
 MOV EDX,[ESP+4] ; port 
 MOV EAX,0 
 IN AX,DX 
 RET 
_io_in32: ; int io_in32(int port); 
 MOV EDX,[ESP+4] ; port 
 IN EAX,DX 
 RET 
_io_out8: ; void io_out8(int port, int data); 
 MOV EDX,[ESP+4] ; port 
 MOV AL,[ESP+8] ; data 
 OUT DX,AL 
 RET 
_io_out16: ; void io_out16(int port, int data); 
 MOV EDX,[ESP+4] ; port 
 MOV EAX,[ESP+8] ; data 
 OUT DX,AX 
 RET 
_io_out32: ; void io_out32(int port, int data); 
 MOV EDX,[ESP+4] ; port 
 MOV EAX,[ESP+8] ; data 
 OUT DX,EAX 
 RET 
_io_load_eflags: ; int io_load_eflags(void); 
 PUSHFD ; 指 PUSH EFLAGS 
 POP EAX 
 RET 
_io_store_eflags: ; void io_store_eflags(int eflags); 
 MOV EAX,[ESP+4] 6 色号设定（harib01f）

 PUSH EAX 
 POPFD ; 指 POP EFLAGS 
 RET
```

作者這邊是黑白的、實際運行我就沒再去運行了。

![](https://i.imgur.com/xzhm2qX.png)

# 繪製矩形

> 颜色备齐了，下面我们来画“画”吧。首先从VRAM与画面上的“点”的关系开始说起。在
> 当前画面模式中，画面上有320×200（=64 000）个像素。假设左上点的坐标是（0,0），右下点的
> 坐标是（319,199），那么像素坐标（x,y）对应的VRAM地址应按下式计算。
> 0xa0000 + x + y * 320

> 其他画面模式也基本相同，只是0xa0000这个起始地址和y的系数320有些不同。
> 根据上式计算像素的地址，往该地址的内存里存放某种颜色的号码，那么画面上该像素的位
> 置就出现相应的颜色。这样就画出了一个点。继续增加x的值，循环以上操作，就能画一条长长
> 的水平直线。再向下循环这条直线，就能够画很多的直线，组成一个有填充色的长方形。
> 根据这种思路，我们制作了函数boxfill8。源程序就是bootpack.c。并且在程序HariMain中，
> 我们不再画条纹图案，而是使用这个函数3次，画3个矩形。也不知能不能正常运行，
> 我们来“make run”看看。哦，好像成功了。

以這個例子來講
 boxfill8(p, 320, COL8_FF0000, 20, 20, 120, 120);
 x0 20
 x1 120
 y0 20
 y1 120
 0xa0000可能就是位於 位於p的 內容可以看到他0xa0000+x+y*320 這可能對應到某一個點的位置

## bootpack.c
```c
#define COL8_000000 0 
#define COL8_FF0000 1 
#define COL8_00FF00 2 
#define COL8_FFFF00 3 
#define COL8_0000FF 4 
#define COL8_FF00FF 5 
#define COL8_00FFFF 6 
#define COL8_FFFFFF 7 
#define COL8_C6C6C6 8 
#define COL8_840000 9 
#define COL8_008400 10 
#define COL8_848400 11 
#define COL8_000084 12 
#define COL8_840084 13 
#define COL8_008484 14 
#define COL8_848484 15 
void HariMain(void) 
{ 
 char *p; /* p变量的地址 */ 
 init_palette(); /* 设置调色板 */ 
 p = (char *) 0xa0000; /* 将地址赋值进去 */ 
 boxfill8(p, 320, COL8_FF0000, 20, 20, 120, 120); 
 boxfill8(p, 320, COL8_00FF00, 70, 50, 170, 150); 
 boxfill8(p, 320, COL8_0000FF, 120, 80, 220, 180); 
 for (;;) { 
 io_hlt(); 
 } 
} 
void boxfill8(unsigned char *vram, int xsize, unsigned char c, int x0, int y0, int x1, int y1) 
{ 
 int x, y; 
 for (y = y0; y <= y1; y++) { 
 for (x = x0; x <= x1; x++) 
 vram[y * xsize + x] = c; 
 } 
 return; 
} 
```

![](https://i.imgur.com/iBqm25H.png)

# 完成工作列
## HariMain
```c
void HariMain(void) 
{ 
 char *vram; 
 int xsize, ysize; 
 init_palette(); 
 vram = (char *) 0xa0000; 
 xsize = 320; 
 ysize = 200; 
 boxfill8(vram, xsize, COL8_008484, 0, 0, xsize - 1, ysize - 29); 
 boxfill8(vram, xsize, COL8_C6C6C6, 0, ysize - 28, xsize - 1, ysize - 28); 
 boxfill8(vram, xsize, COL8_FFFFFF, 0, ysize - 27, xsize - 1, ysize - 27); 
 boxfill8(vram, xsize, COL8_C6C6C6, 0, ysize - 26, xsize - 1, ysize - 1); 
 boxfill8(vram, xsize, COL8_FFFFFF, 3, ysize - 24, 59, ysize - 24); 
 boxfill8(vram, xsize, COL8_FFFFFF, 2, ysize - 24, 2, ysize - 4); 
 boxfill8(vram, xsize, COL8_848484, 3, ysize - 4, 59, ysize - 4); 
 boxfill8(vram, xsize, COL8_848484, 59, ysize - 23, 59, ysize - 5); 
 boxfill8(vram, xsize, COL8_000000, 2, ysize - 3, 59, ysize - 3); 
 boxfill8(vram, xsize, COL8_000000, 60, ysize - 24, 60, ysize - 3); 
 boxfill8(vram, xsize, COL8_848484, xsize - 47, ysize - 24, xsize - 4, ysize - 24); 
 boxfill8(vram, xsize, COL8_848484, xsize - 47, ysize - 23, xsize - 47, ysize - 4); 
 boxfill8(vram, xsize, COL8_FFFFFF, xsize - 47, ysize - 3, xsize - 4, ysize - 3); 
 boxfill8(vram, xsize, COL8_FFFFFF, xsize - 3, ysize - 24, xsize - 3, ysize - 3); 
 for (;;) { 
 io_hlt(); 
 } 
}
```
![](https://i.imgur.com/H3oaWz8.png)
最後就來到我們最想講的地方了，這邊會開始介紹中斷等等

## References

- 川合秀實，《30日でできる！OS自作入門》，毎日コミュニケーションズ，2006，ISBN 978-4-8399-1984-9. [Book record](https://ndlsearch.ndl.go.jp/books/R100000002-I000008118788)
- [yourtion/30dayMakeOS](https://github.com/yourtion/30dayMakeOS) — 本文使用的中文學習用原始碼倉庫。

