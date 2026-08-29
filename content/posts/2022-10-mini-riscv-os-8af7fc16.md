---
title: "mini-riscv-os 特權模式切換 m/s/u 達成system call"
date: "2022-10-16T06:04:00.002+08:00"
updated: "2022-10-16T18:13:36.391+08:00"
permalink: "/2022/10/mini-riscv-os.html"
original_url: "https://x8795278.blogspot.com/2022/10/mini-riscv-os.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5202058255533471932"
tags: []
layout: post
---

![](https://i.imgur.com/BJlJNTL.gif)

紀錄一下要切換特權模式要經過哪些步驟

https://ithelp.ithome.com.tw/articles/10301462
https://ithelp.ithome.com.tw/articles/10302200
http://rcore-os.cn/rCore-Tutorial-deploy/docs/lab-1/guide/part-2.html
https://blog.csdn.net/zoomdy/article/details/100176377
https://dingfen.github.io/risc-v/2020/08/05/riscv-privileged.html#mstatus-%E5%AF%84%E5%AD%98%E5%99%A8
https://learning-os.gitee.io/rcore-tutorial-book-v3/chapter2/4trap-handling.html#id3
http://wyfcyx.gitee.io/rcore-tutorial-book-v3/chapter2/1rv-privilege.html
這些網站都大部分都在講述實際os要怎麼設計比較好
那麼單純想從最初的Machine 模式跳到 User或者 Supervisor 要有實際code的呈現，卻在很少文章提到我們來看一下，那麼我們就來研究一下特權模式怎麼切換+程式碼，特權模式可以參考這份PDF
https://www2.eecs.berkeley.edu/Pubs/TechRpts/2016/EECS-2016-161.pdf
我們直接從mini-riscv-os來改，他已經完成時間中斷
https://github.com/cccriscv/mini-riscv-os

# riscv.h
參考https://github.com/mit-pdos/xv6-riscv/blob/7c958af7828973787f3c327854ba71dd3077ad2d/kernel/riscv.h

```c
#ifndef __RISCV_H__
#define __RISCV_H__

#include <stdint.h>

#define reg_t uint32_t // RISCV32: register is 32bits
// define reg_t as uint64_t // RISCV64: register is 64bits

// ref: https://www.activexperts.com/serial-port-component/tutorials/uart/
#define UART 0x10000000
#define UART_THR (uint8_t *)(UART + 0x00) // THR:transmitter holding register
#define UART_LSR (uint8_t *)(UART + 0x05) // LSR:line status register
#define UART_LSR_EMPTY_MASK 0x40          // LSR Bit 6: Transmitter empty; both the THR and LSR are empty

// Saved registers for kernel context switches.
struct context
{
  reg_t ra;
  reg_t sp;

  // callee-saved
  reg_t s0;
  reg_t s1;
  reg_t s2;
  reg_t s3;
  reg_t s4;
  reg_t s5;
  reg_t s6;
  reg_t s7;
  reg_t s8;
  reg_t s9;
  reg_t s10;
  reg_t s11;
};

// ref: https://github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/riscv.h
//
// local interrupt controller, which contains the timer.
// ================== Timer Interrput ====================

#define NCPU 8 // maximum number of CPUs
#define CLINT 0x2000000
#define CLINT_MTIMECMP(hartid) (CLINT + 0x4000 + 4 * (hartid))
#define CLINT_MTIME (CLINT + 0xBFF8) // cycles since boot.

// which hart (core) is this?
static inline reg_t r_mhartid()
{
  reg_t x;
  asm volatile("csrr %0, mhartid"
               : "=r"(x));
  return x;
}

// Machine Status Register, mstatus
#define MSTATUS_MPP_MASK (3 << 11) // previous mode.
#define MSTATUS_MPP_M (3 << 11)
#define MSTATUS_MPP_S (1 << 11)
#define MSTATUS_MIE (1 << 3) // machine-mode interrupt enable.
#define MSTATUS_MPP_U (0 << 11)

static inline reg_t r_mstatus()
{
  reg_t x;
  asm volatile("csrr %0, mstatus"
               : "=r"(x));
  return x;
}

static inline void w_mstatus(reg_t x)
{
  asm volatile("csrw mstatus, %0"
               :
               : "r"(x));
}

// machine exception program counter, holds the
// instruction address to which a return from
// exception will go.
static inline void w_mepc(reg_t x)
{
  asm volatile("csrw mepc, %0"
               :
               : "r"(x));
}

static inline reg_t r_mepc()
{
  reg_t x;
  asm volatile("csrr %0, mepc"
               : "=r"(x));
  return x;
}

// Machine Scratch register, for early trap handler
static inline void w_mscratch(reg_t x)
{
  asm volatile("csrw mscratch, %0"
               :
               : "r"(x));
}

// Machine-mode interrupt vector
static inline void w_mtvec(reg_t x)
{
  asm volatile("csrw mtvec, %0"
               :
               : "r"(x));
}

// Supervisor Interrupt Enable
#define SIE_SEIE (1 << 9)  // external
#define SIE_STIE (1 << 5)  // timer
#define SIE_SSIE (1 << 1)  // software
#define SIE_SEIE2 (1 << 8) // u external
#define SIE_STIE2 (1 << 4) // u timer
#define SIE_SSIE2 (1 << 0) // u software
// supervisor exception program counter, holds the
// instruction address to which a return from
// exception will go.
static inline void
w_sepc(uint32_t x)
{
  asm volatile("csrw sepc, %0"
               :
               : "r"(x));
}

static inline uint32_t
r_sepc()
{
  uint32_t x;
  asm volatile("csrr %0, sepc"
               : "=r"(x));
  return x;
}
// Supervisor Status Register, sstatus
#define SSTATUS_SPP (1 << 8)  // Previous mode, 1=Supervisor, 0=User
i#define SSTATUS_UPIE (1 << 4) // User Previous Interrupt Enable
#define SSTATUS_SIE (1 << 1)  // Supervisor Interrupt Enable
#define SSTATUS_SIE2 (0 << 1) // Supervisor Interrupt Enable
#define SSTATUS_UIE (1 << 0)  // User Interrupt Enable
#define SSTATUS_UIE2 (0 << 0) // User Interrupt Enable
static inline uint32_t
r_sstatus()
{
  uint32_t x;
  asm volatile("csrr %0, sstatus"
               : "=r"(x));
  return x;
}

static inline void
w_sstatus(uint32_t x)
{
  asm volatile("csrw sstatus, %0"
               :
               : "r"(x));
}

static inline void
w_mideleg(uint32_t x)
{
  asm volatile("csrw mideleg, %0"
               :
               : "r"(x));
}
static inline void w_medeleg(uint32_t x)
{
  asm volatile("csrw medeleg, %0"
               :
               : "r"(x));
}

static inline void
w_sie(uint32_t x)
{
  asm volatile("csrw sie, %0"
               :
               : "r"(x));
}
static inline uint32_t
r_sie()
{
  uint32_t x;
  asm volatile("csrr %0, sie"
               : "=r"(x));
  return x;
}

// Supervisor Trap-Vector Base Address
// low two bits are mode.
static inline void
w_stvec(uint32_t x)
{
  asm volatile("csrw stvec, %0"
               :
               : "r"(x));
}

static inline uint32_t
r_stvec()
{
  uint32_t x;
  asm volatile("csrr %0, stvec"
               : "=r"(x));
  return x;
}

// are device interrupts enabled?
static inline int
intr_get()
{
  uint32_t x = r_sstatus();
  return (x & SSTATUS_SIE) != 0;
}

// Supervisor Trap Cause
static inline uint32_t
r_scause()
{
  uint32_t x;
  asm volatile("csrr %0, scause"
               : "=r"(x));
  return x;
}

// Supervisor Trap Value
static inline uint32_t
r_stval()
{
  uint32_t x;
  asm volatile("csrr %0, stval"
               : "=r"(x));
  return x;
}

// Machine-mode Interrupt Enable
#define MIE_MEIE (1 << 11) // external
#define MIE_MTIE (1 << 7)  // timer
#define MIE_MTIE2 (0 << 7) // timer
#define MIE_MSIE (1 << 3)  // software
#define MIP_MSIP (1 << 3)  // software
#define MIP_MSIP2 (0 << 3) // software

static inline reg_t r_mie()
{
  reg_t x;
  asm volatile("csrr %0, mie"
               : "=r"(x));
  return x;
}

static inline void w_mie(reg_t x)
{
  asm volatile("csrw mie, %0"
               :
               : "r"(x));
}

static inline reg_t r_mip()
{
  reg_t x;
  asm volatile("csrr %0, mip"
               : "=r"(x));
  return x;
}

static inline void w_mip(reg_t x)
{
  asm volatile("csrw mip, %0"
               :
               : "r"(x));
}

// disable device interrupts
static inline void
intr_off()
{
  // w_mstatus(r_mstatus() & ~SSTATUS_UIE);
  // w_mstatus(r_mstatus() & ~SSTATUS_SIE);
  w_sstatus(r_sstatus() & ~SSTATUS_SIE);
  
}

#endif

```
# os.c
```c
#include "os.h"
extern void trap_init(void);
extern void trap_init(void);
extern void kernelvec();
extern void trap_vector();
extern int gethid();
int init_main(void);

void os_kernel()
{
	// int test = gethid();
	task_os();
}

// interrupts and exceptions from kernel code go here via kernelvec,
// on whatever the current kernel stack is.
reg_t kerneltrap(reg_t epc, reg_t cause)
{
	int which_dev = 0;
	uint32_t sepc = r_sepc();

	uint32_t sstatus = r_sstatus();
	uint32_t scause = r_scause();
	reg_t return_pc = sepc;
	reg_t cause_code = scause & 0xfff;

	if ((sstatus & SSTATUS_SPP) == 0)
		lib_puts("kerneltrap: not from supervisor mode\n");
	if (intr_get() != 0)
		lib_puts("kerneltrap: interrupts enabled\n");
	// lib_printf("%x\n", r_sepc());
	// lib_printf("%x\n", scause);
	// lib_printf("%x\n", cause_code);
	if (cause & 0x80000000)
	{
		lib_printf("spec %x\n", r_sepc());
		lib_printf("%x\n", scause);
		lib_printf("%x\n", cause_code);
		/* Asynchronous trap - interrupt */
		switch (cause_code)
		{
		case 1:
			lib_puts("Supervisor software interrupt!\n");
			// return_pc += 4;
			break;
		case 3:
			lib_puts("software interruption!\n");
			break;
		case 7:
			lib_puts("timer interruption!\n");
			// disable machine-mode timer interrupts.
			w_mie(~((~r_mie()) | (1 << 7)));
			timer_handler();
			return_pc = (reg_t)&os_kernel;
			// enable machine-mode timer interrupts.
			w_mie(r_mie() | MIE_MTIE);
			break;
		case 8:
			lib_puts("user extern interruption!\n");
			// sepc += 4;
			return_pc += 4;
			// w_sepc(sepc+4);
			// w_mepc(sepc+8);
			break;
		case 11:
			lib_puts("external interruption!\n");
			break;
		default:
			lib_puts("unknown async exception!\n");
			break;
		}
	}
	else
	{

		/* Synchronous trap - exception */
		lib_puts("Sync exceptions2!\n");
		lib_printf("%x\n", scause);
		lib_printf("%x\n", cause_code);
		switch (cause_code)
		{
		case 2:
			lib_puts("Illegal instruction!\n");
			return_pc += 4;
			break;
		case 8:
			lib_puts("Environment call from U-mode!\n");
			// do_syscall(ctx);
			return_pc += 4;
			break;
		case 9:
			lib_puts("Environment call from S-mode!\n");
			suinter();
			return_pc += 4;

			break;

		default:
			/* Synchronous trap - exception */
			lib_printf("Sync exceptions! cause code: %d\n", cause_code);
			break;
		}
	
	}
	 
    // set S Previous Privilege mode to User.
	unsigned long x = r_sstatus();
	// x2 &= ~SSTATUS_SIE;
	x &= ~SSTATUS_SPP; // clear SPP to 0 for user mode
	x |= SSTATUS_SPIE; // enable interrupts in user mode
	w_sstatus(x2);
    //下次sret就會回到user mod
	return return_pc;
}

void supmod()
{
    //設定mstatus 將在mret跳轉為user mode
	uint32_t x = r_mstatus();
	x &= ~MSTATUS_MPP_MASK;
	x |= MSTATUS_MPP_U;
	w_mstatus(x);

    //把machine 中斷/異常 委託給 Supervisor
	w_medeleg(0xffff);
	w_mideleg(0xffff);
	w_sie(r_sie() | SIE_SEIE | SIE_STIE | SIE_SSIE | SIE_SEIE2 | SIE_STIE2 | SIE_SSIE2);
	//  w_sie(r_sie() & SIE_SEIE2);
	lib_puts("sup mod\n");
    
	// set the sup-mode trap handler.
	w_stvec((reg_t)kernelvec);
}
void os_start()
{
	lib_puts("OS start\n");
	user_init();
	trap_init();
	timer_init(); // start timer interrupt ...
	supmod();
	w_mepc(init_main);
	asm volatile("mret");

}

int os_main(void)
{
	os_start();

	return 0;
}

int init_main(void)
{

	int current_task = 0;

	while (1)
	{

		lib_puts("OS: Activate next task\n");
		task_go(current_task);
		lib_puts("OS: Back to OS\n");
		current_task = (current_task + 1) % taskTop; // Round Robin Scheduling
		lib_puts("\n");

	}
	return 0;
}

```
# sys.h
```asm
# This Code derived from xv6-riscv (64bit)
# -- https://github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/swtch.S
.global gethid
gethid:
	ecall
	ret
# ============ MACRO ==================
.macro ctx_save base
        sw ra, 0(\base)
        sw sp, 4(\base)
        sw s0, 8(\base)
        sw s1, 12(\base)
        sw s2, 16(\base)
        sw s3, 20(\base)
        sw s4, 24(\base)
        sw s5, 28(\base)
        sw s6, 32(\base)
        sw s7, 36(\base)
        sw s8, 40(\base)
        sw s9, 44(\base)
        sw s10, 48(\base)
        sw s11, 52(\base)
.endm

.macro ctx_load base
        lw ra, 0(\base)
        lw sp, 4(\base)
        lw s0, 8(\base)
        lw s1, 12(\base)
        lw s2, 16(\base)
        lw s3, 20(\base)
        lw s4, 24(\base)
        lw s5, 28(\base)
        lw s6, 32(\base)
        lw s7, 36(\base)
        lw s8, 40(\base)
        lw s9, 44(\base)
        lw s10, 48(\base)
        lw s11, 52(\base)
.endm

.macro reg_save base
        # save the registers.
        sw ra, 0(\base)
        sw sp, 4(\base)
        sw gp, 8(\base)
        sw tp, 12(\base)
        sw t0, 16(\base)
        sw t1, 20(\base)
        sw t2, 24(\base)
        sw s0, 28(\base)
        sw s1, 32(\base)
        sw a0, 36(\base)
        sw a1, 40(\base)
        sw a2, 44(\base)
        sw a3, 48(\base)
        sw a4, 52(\base)
        sw a5, 56(\base)
        sw a6, 60(\base)
        sw a7, 64(\base)
        sw s2, 68(\base)
        sw s3, 72(\base)
        sw s4, 76(\base)
        sw s5, 80(\base)
        sw s6, 84(\base)
        sw s7, 88(\base)
        sw s8, 92(\base)
        sw s9, 96(\base)
        sw s10, 100(\base)
        sw s11, 104(\base)
        sw t3, 108(\base)
        sw t4, 112(\base)
        sw t5, 116(\base)
        sw t6, 120(\base)
.endm

.macro reg_load base
        # restore registers.
        lw ra, 0(\base)
        lw sp, 4(\base)
        lw gp, 8(\base)
        # not this, in case we moved CPUs: lw tp, 12(\base)
        lw t0, 16(\base)
        lw t1, 20(\base)
        lw t2, 24(\base)
        lw s0, 28(\base)
        lw s1, 32(\base)
        lw a0, 36(\base)
        lw a1, 40(\base)
        lw a2, 44(\base)
        lw a3, 48(\base)
        lw a4, 52(\base)
        lw a5, 56(\base)
        lw a6, 60(\base)
        lw a7, 64(\base)
        lw s2, 68(\base)
        lw s3, 72(\base)
        lw s4, 76(\base)
        lw s5, 80(\base)
        lw s6, 84(\base)
        lw s7, 88(\base)
        lw s8, 92(\base)
        lw s9, 96(\base)
        lw s10, 100(\base)
        lw s11, 104(\base)
        lw t3, 108(\base)
        lw t4, 112(\base)
        lw t5, 116(\base)
        lw t6, 120(\base)
.endm
# ============ Macro END   ==================
 
# Context switch
#
#   void sys_switch(struct context *old, struct context *new);
# 
# Save current registers in old. Load from new.

.globl sys_switch
.align 4
sys_switch:

        ctx_save a0  # a0 => struct context *old
        ctx_load a1  # a1 => struct context *new
        ret          # pc=ra; swtch to new task (new->ra)

.globl kerneltrap
.globl kernelvec
.align 4
kernelvec:
        csrrw	t5, sscratch, t5
        reg_save sp
	

        # call the C trap handler in trap.c
	csrr	a0, sepc
	csrr	a1, scause
	call	kerneltrap
        # trap_handler will return the return address via a0.
	csrw	sepc, a0
        csrr	t5, sscratch
        reg_load sp

        # return to whatever we were doing in the kernel.
        sret
.globl trap_vector
# the trap vector base address must always be aligned on a 4-byte boundary
.align 4
trap_vector:
	# save context(registers).
	csrrw	t6, mscratch, t6	# swap t6 and mscratch
        reg_save t6
	csrw	mscratch, t6
	# call the C trap handler in trap.c
	csrr	a0, mepc
	csrr	a1, mcause
	call	trap_handler

	# trap_handler will return the return address via a0.
	csrw	mepc, a0

	# load context(registers).
	csrr	t6, mscratch
         
	reg_load t6
        
        li a1, 1
        csrw sip, a1 <===記的supervisor設2 或3可能要在初始化設,有權限下放就要設我們下放到sup/user就設
	mret

```

既然Machine 已經委託給  Supervisor那麼
stev 則指向 kernelvec
kernelvec將會用組合語言做下列的事情儲存當前
sscratch
然後reg_save 把register 全部存到stack
```asm
    # call the C trap handler in trap.c
	csrr	a0, sepc
	csrr	a1, scause
	call	kerneltrap
```
塞參數到a0 , a1 呼叫fucntion kerneltrap
也就是到我們的trap,以user mode來說，觸發中斷將會由 Supervisor代理
那麼，我們就可以在kerneltrap地方使用sstatus,sscause,sepc暫存器,
可以看到sepc 和 cause都是由a0,a1傳參數進來，參考一些文章也可以看到其實呼叫ecall會卡在當前指令
所以通常從 sret回去還是回到ecall這樣會產生無窮回圈，這也是為什麼return address要+4的原因。
```c
// interrupts and exceptions from kernel code go here via kernelvec,
// on whatever the current kernel stack is.
reg_t kerneltrap(reg_t epc, reg_t cause)
{
	int which_dev = 0;
	uint32_t sepc = r_sepc();

	uint32_t sstatus = r_sstatus();
	uint32_t scause = r_scause();
	reg_t return_pc = sepc;
	reg_t cause_code = scause & 0xfff;

	if ((sstatus & SSTATUS_SPP) == 0)
		lib_puts("kerneltrap: not from supervisor mode\n");
	if (intr_get() != 0)
		lib_puts("kerneltrap: interrupts enabled\n");
	// lib_printf("%x\n", r_sepc());
	// lib_printf("%x\n", scause);
	// lib_printf("%x\n", cause_code);
	if (cause & 0x80000000)
	{
		lib_printf("spec %x\n", r_sepc());
		lib_printf("%x\n", scause);
		lib_printf("%x\n", cause_code);
		/* Asynchronous trap - interrupt */
		switch (cause_code)
		{
		case 1:
			lib_puts("Supervisor software interrupt!\n");
			// return_pc += 4;
			break;
		case 3:
			lib_puts("software interruption!\n");
			break;
		case 7:
			lib_puts("timer interruption!\n");
			// disable machine-mode timer interrupts.
			w_mie(~((~r_mie()) | (1 << 7)));
			timer_handler();
			return_pc = (reg_t)&os_kernel;
			// enable machine-mode timer interrupts.
			w_mie(r_mie() | MIE_MTIE);
			break;
		case 8:
			lib_puts("user extern interruption!\n");
			// sepc += 4;
			return_pc += 4;
			// w_sepc(sepc+4);
			// w_mepc(sepc+8);
			break;
		case 11:
			lib_puts("external interruption!\n");
			break;
		default:
			lib_puts("unknown async exception!\n");
			break;
		}
	}
	else
	{

		/* Synchronous trap - exception */
		lib_puts("Sync exceptions2!\n");
		lib_printf("%x\n", scause);
		lib_printf("%x\n", cause_code);
		switch (cause_code)
		{
		case 2:
			lib_puts("Illegal instruction!\n");
			return_pc += 4;
			break;
		case 8:
			lib_puts("Environment call from U-mode!\n");
			// do_syscall(ctx);
			return_pc += 4;
			break;
		case 9:
			lib_puts("Environment call from S-mode!\n");
			suinter();
			return_pc += 4;

			break;

		default:
			/* Synchronous trap - exception */
			lib_printf("Sync exceptions! cause code: %d\n", cause_code);
			break;
		}
	
	}
	 
    // set S Previous Privilege mode to User.
	unsigned long x = r_sstatus();
	// x2 &= ~SSTATUS_SIE;
	x &= ~SSTATUS_SPP; // clear SPP to 0 for user mode
	x |= SSTATUS_SPIE; // enable interrupts in user mode
	w_sstatus(x2);
    //下次sret就會回到user mod
	return return_pc;
}

```

在os 我們目前已經在user模式觸發一個中斷或者異常，
user.c user_task1 function 註解拿掉可以運行後看，看kerneltrap分別會觸發什麼中斷/異常

![](https://i.imgur.com/ywRYkSL.png)

# user.c
```c
#include "os.h"
extern int gethid();
void user_task0(void)
{
	lib_puts("Task0: Created!\n");
	while (1)
	{
		lib_puts("Task0: Running...\n");
		// asm volatile("ecall");
		lib_delay(1000);
	}
}

void user_task1(void)
{
	lib_puts("Task1: Created!\n");
	while (1)
	{
		lib_puts("Task1: Running...\n");
		// uint32_t x= r_mepc()+4;
		// uint32_t sstatus = r_sstatus();
	
		//lib_printf("%x\n",  0/0);
		asm volatile("ecall"); <==觸發中斷
	
		lib_delay(1000);

	}
}

void user_init()
{
	task_create(&user_task0);
	task_create(&user_task1);
}

```
這邊有看到rcore的設計或者是一般os的設計又有分kernel的stack 和 user stack
這邊大概的概念就是區開來，
假設我們構造一個system call
```c
.global gethid
gethid:
    li a7, 0
	ecall
	ret
```
如果單純的把值存入a7那麼在進行kerneltrap到走到
```c
		case 8:
			lib_puts("Environment call from U-mode!\n");
```
有把握a7的value都不會動嗎，所以他們基本上把這些stack 變為兩個stack,
也就是跳轉前我們要儲存process的 整個register狀態包含stack
如果不想這麼麻煩我們也可以先用一個global的變數替代一下
在os.c 新增變數
```c
extern int rko;
```
user.c
```c
    int rko=0;

    ....
        
		case 8:
			lib_puts("Environment call from U-mode!\n");
			// do_syscall(ctx);
			lib_printf("%d\n", rko);
			rko=0;
			return_pc += 4;
			break;
```
```c
void user_task1(void)
{
	lib_puts("Task1: Created!\n");
	while (1)
	{
		lib_puts("Task1: Running...\n");
        rko= 1;
		int a = gethid();
		
		lib_delay(1000);
	
	}
}

```

想像把global rko變數存起來，模擬儲存當前process整個register和 stack
# sys.s
```c
# This Code derived from xv6-riscv (64bit)
# -- https://github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/swtch.S

.global gethid
gethid:
      #  li a7, 0  <==如果自己能實現儲存整個stack就儲存到這個process的register和 stack
#這邊我們已經把參數假裝放到rko了
	ecall
	ret
```

也就是
https://github.com/cccriscv/mini-riscv-os/blob/3fcd134a2129fc5ecad9e1f904e7b910ab077e17/10-SystemCall/src/syscall.c
裡面常常看到的ctx,在之前的模擬器也可以常常看到這個context

所以呼叫一個system call則會到trap裡面根據rko對應system call編號，system call在自定義讀哪個argument(register),拿register的值做出什麼功能並回傳寫入(a0,a1...)

後續當然我只要machine 或者run 在supervisor模式下我們也可以單獨的設,
如果有權限下放，可以寫asm寫到固定會觸發的時間中斷trap_vector /懶得寫xd

# sys.s
```asm
# the trap vector base address must always be aligned on a 4-byte boundary
.align 4
trap_vector:
	....
        
        li a1, 1
        csrw sip, a1 <===記的supervisor設2 或3可能要在初始化設,有權限下放就要設我們下放到sup/user就設
	mret

```

# os.c
都要disable掉，不然sup會回去user mod 整個register會大亂,
supmod()
reg_t kerneltrap()裡面的都要註解掉
```c
	// set S Previous Privilege mode to User.
	// unsigned long x2 = r_sstatus();
	// // x2 |= SSTATUS_SIE;
	// x2 &= ~SSTATUS_SPP; // clear SPP to 0 for user mode
	// x2 |= SSTATUS_SPIE; // enable interrupts in user mode
	// w_sstatus(x2);
```
# machine /Supervisor / user mod
![](https://i.imgur.com/BJlJNTL.gif)
# Supervisor / machine
![](https://i.imgur.com/sdfBvgx.gif)

那麼在system call 的實驗，由於在切換 task的時候已經可以得知process的狀態
```task.c
#include "task.h"
#include "lib.h"

uint8_t task_stack[MAX_TASK][STACK_SIZE];
struct context ctx_os;
struct context ctx_tasks[MAX_TASK];
struct context *ctx_now;
int taskTop = 0; // total number of task
int current_task=0;
// create a new task
int task_create(void (*task)(void))
{
	int i = taskTop++;
	ctx_tasks[i].ra = (reg_t)task;
	ctx_tasks[i].sp = (reg_t)&task_stack[i][STACK_SIZE - 1];
	return i;
}

// switch to task[i]
void task_go(int i)
{

	ctx_now = &ctx_tasks[i];
	current_task=i;

	sys_switch(&ctx_os, &ctx_tasks[i]);
}

// switch back to os
void task_os()
{
	struct context *ctx = ctx_now;
	ctx_now = &ctx_os;
	sys_switch(ctx, &ctx_os);
}

```
我們把當前current_task和ctx_tasks傳出去給kerneltrap,當發生中斷時候我們就可以根據 current_task
查詢當前ctx_tasks
![](https://i.imgur.com/uPk2YEi.png)
照理說ecall 會把sysnum放在a7 返回值會在 a0 ,,這邊比較hack一點玩法在觸發中斷呼叫system call後強制把value寫在a0，在觸發中斷後gethid ecall 後呼叫J task_flush 把當前rigister更新，基本上不用理stack因為已經在kernelvec 恢復
```c
void __attribute__((always_inline)) task_flush()
{
	asm volatile("addi a0, %0, 0"
				 :
				 : "r"(ctx_tasks[current_task].a0));
	asm volatile("addi a7, %0, 0"
				 :
				 : "r"(ctx_tasks[current_task].a7));
	asm volatile("addi s1, %0, 0"
				 :
				 : "r"(ctx_tasks[current_task].s1));
	asm volatile("addi s2, %0, 0"
				 :
				 : "r"(ctx_tasks[current_task].s2));
	asm volatile("addi s3, %0, 0"
				 :
				 : "r"(ctx_tasks[current_task].s3));
	asm volatile("addi s4, %0, 0"
				 :
				 : "r"(ctx_tasks[current_task].s4));
	asm volatile("addi s5, %0, 0"
				 :
				 : "r"(ctx_tasks[current_task].s5));
	asm volatile("addi s6, %0, 0"
				 :
				 : "r"(ctx_tasks[current_task].s6));
	asm volatile("addi s7, %0, 0"
				 :
				 : "r"(ctx_tasks[current_task].s7));
	asm volatile("addi s8, %0, 0"
				 :
				 : "r"(ctx_tasks[current_task].s8));
	asm volatile("addi s9, %0, 0"
				 :
				 : "r"(ctx_tasks[current_task].s9));
	asm volatile("addi s10, %0, 0"
				 :
				 : "r"(ctx_tasks[current_task].s10));
	asm volatile("addi s11, %0, 0"
				 :
				 : "r"(ctx_tasks[current_task].s11));
}
```
```c
.global gethid
.align 4
gethid:
        li a7, 1
        addi s11, a0, 0
	ecall  
        J task_flush
	ret
```
```c
    extern int current_task;
    extern struct context ctx_tasks[MAX_TASK];
    //...
    case 8:
			lib_puts("Environment call from U-mode!\n");
		
			struct context *ctx_now;
			ctx_now =&ctx_tasks[current_task];
			sys_switch(&ctx_now[current_task], &ctx_now[current_task]);

			lib_printf("%d\n", current_task);
			lib_printf("%d\n", ctx_now[current_task].s11);
			do_syscall(ctx_now[current_task].a7,ctx_now[current_task].s11);

			lib_printf("%d\n", ctx_tasks[current_task].a0);
			//task_flush2();
			return_pc += 4;
			break;
```
```c
void do_syscall(int syscall_num,int syscall_value)
{
	switch (syscall_num)
	{
	case 1:
		lib_printf("hello%d\n",syscall_value);
		ctx_tasks[current_task].a0=syscall_value+2;
		break;
	case 2:
		break;
	}
}
```
這樣我們就完成一個system call,傳入100,將傳入的value+2返回值102的 function
![](https://i.imgur.com/1gkslXF.png)

# 在快速切換context switch 的情況下
```c
#include "timer.h"

// a scratch area per CPU for machine-mode timer interrupts.
reg_t timer_scratch[NCPU][5];

#define interval 50000000 // cycles; about 2 second in qemu.
static uint32_t mtime_lo(void)
{
  return *(volatile uint32_t *)(CLINT_MTIME);
}
static uint32_t mtime_hi(void)
{
  return *(volatile uint32_t *)(CLINT_MTIME + 4);
}
uint64_t get_timer_vale()
{
  while (1)
  {

    uint32_t hi = mtime_hi();
    uint32_t lo = mtime_lo();
    if(hi == mtime_hi())
    return (((uint64_t)hi << 32) | lo);
  }
}

static void mtimcmp_lo(uint32_t v)
{  int id = r_mhartid();

   *(volatile uint32_t *)(CLINT_MTIMECMP(id)) =v;
}
static void mtimcmp_hi(uint32_t v)
{
   int id = r_mhartid();
   *(volatile uint32_t *)(CLINT_MTIMECMP(id) + 4)=v;
}
uint64_t set_timer_vale(uint64_t v)
{
  uint32_t hi = (v >> 32) & 0xffffffff;
  uint32_t lo = (v ) & 0xffffffff;
  mtimcmp_lo(0xffffffff);
  mtimcmp_hi(hi);
  mtimcmp_lo(lo);
}
// extern int pending;
void timer_init()
{
  // each CPU has a separate source of timer interrupts.
  int id = r_mhartid();

  // ask the CLINT for a timer interrupt.
  // int interval = 1000000; // cycles; about 1/10th second in qemu.

  *(reg_t *)CLINT_MTIMECMP(id) = *(reg_t *)CLINT_MTIME + interval;

  // prepare information in scratch[] for timervec.
  // scratch[0..2] : space for timervec to save registers.
  // scratch[3] : address of CLINT MTIMECMP register.
  // scratch[4] : desired interval (in cycles) between timer interrupts.
  reg_t *scratch = &timer_scratch[id][0];
  scratch[3] = CLINT_MTIMECMP(id);
  scratch[4] = interval;
  w_mscratch((reg_t)scratch);

  // enable machine-mode timer interrupts.
  w_mie(r_mie() | MIE_MTIE);
  // w_mie(r_mie() & MIE_MTIE2);
  // lib_printf("%x\n", r_mepc());
}

static int timer_count = 0;
static inline reg_t r_sp()
{
  reg_t x;
  asm volatile("addi %0,sp, 0"
               : "=r"(x));
  return x;
}

void timer_handler()
{
  ++timer_count;
  lib_printf("timer_handler2: %d\n", timer_count++);
  lib_printf("%x\n", r_sepc());
  // 	w_sstatus(r_sstatus() | SSTATUS_SIE);
  int id = r_mhartid();

  lib_printf("timer_handler: %d\n", *(uint64_t *)CLINT_MTIME);
  // *(uint64_t *)CLINT_MTIMECMP(id) = *(uint64_t *)CLINT_MTIME + interval;
  set_timer_vale((get_timer_vale()+ interval));
}

```
這邊要注意CLINT_MTIMECMP 和CLINT_MTIME 格式，目前好像每個mini-os-riscv 都會有問題，
然後stack  
```c
  lib_printf("%x\n", r_sepc());
```
透過這個觀察context switch 的時候process之間的 stack 發現好像都會減少32
```c
 riscv64-unknown-elf-gcc -nostdlib -fno-builtin -mcmodel=medany -march=rv32ima -mabi=ilp32 -O0 -S os.c -o os.s

```
![](https://i.imgur.com/h6RbSX3.png)
16+32 把消失的stack補到48這樣context switch 每次的stack 才會正常。但是這樣就算有點作弊一點了,
可能在切換的時候中斷沒補回來等等。

```c
riscv64-unknown-elf-gcc -nostdlib -fno-builtin -mcmodel=medany -march=rv32ima -mabi=ilp32 -O0 -T os.ld -o os.elf start.s sys.s lib.c timer.c task.c os.s user.c trap.c
```

經過修改
#define interval 400000 // cycles; about 2 second in qemu.
的情況下，忘記統計時間，目前可以切換十萬多次不會crashe，有可能CLINT_MTIMECMP 和CLINT_MTIME  溢位情況下，時間中斷應該會異常，不過已經比以前好太多了。

https://blog.csdn.net/zoomdy/article/details/79361553

![](https://i.imgur.com/617OF8e.png)
![](https://i.imgur.com/3vFhufl.png)

## References

- [rCore-Tutorial-Book-v3](https://rcore-os.cn/rCore-Tutorial-Book-v3/) — RISC-V 特權模式與 Trap 處理的參考教材。
- [MIT PDOS / xv6-riscv](https://github.com/mit-pdos/xv6-riscv) — 文中引用的 `riscv.h` 教學作業系統原始碼。
- [RISC-V privileged architecture specification](https://riscv.org/technical/specifications/) — 特權模式與 CSR 的規格來源。

