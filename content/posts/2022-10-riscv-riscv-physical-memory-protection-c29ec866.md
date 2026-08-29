---
title: "riscv physical memory protection"
date: "2022-10-29T20:48:00.001+08:00"
updated: "2023-01-05T22:48:15.919+08:00"
permalink: "/2022/10/riscv-riscv-physical-memory-protection.html"
original_url: "https://x8795278.blogspot.com/2022/10/riscv-riscv-physical-memory-protection.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-29774664228472525"
tags: ["RISC-V"]
layout: post
---

![](https://i.imgur.com/Ts4O50E.png)

# riscv-probe

```
extern char _rodata_end;
extern char _data_start;
extern char _bss_end;
#define KB (0x1 << 10)
static uintptr_t uart_keys[] = {
        SIFIVE_UART0_CTRL_ADDR,
        NS16550A_UART0_CTRL_ADDR,
        RISCV_HTIF_BASE_ADDR,
        0
};

#ifdef __riscv
#include "arch/riscv/encoding.h"
#include "arch/riscv/machine.h"
#include "arch/riscv/csr.h"
#endif
unsigned char RO_Array[1 * KB] __attribute__((aligned(2 * KB)));
int main()
{
        uintptr_t uart = 0;
        uintptr_t *uart_k = uart_keys;
        const uintptr_t uartlen = 32;

        /* locate UART address using known configuration keys */
        while (*uart_k && !(uart = getauxval(*uart_k++)));

        /* locate ROM/Flash (text+rodata) and RAM (data+bss) */
        uintptr_t rx_s = (uintptr_t)&_text_start;
        uintptr_t rx_l = roundpow2((uintptr_t)(&_rodata_end - &_text_start));
        uintptr_t rw_s = (uintptr_t)&_data_start;
        uintptr_t rw_l = roundpow2((uintptr_t)(&_bss_end - &_data_start));

        uintptr_t rd_s = (uintptr_t)&RO_Array[0];
        uintptr_t rd_l = roundpow2((uintptr_t)((&RO_Array[0] + sizeof(RO_Array))));

        /* print our findings */
        printf("text: 0x%x - 0x%x\n", rx_s, rx_s + rx_l - 1);
        printf("data: 0x%x - 0x%x\n", rw_s, rw_s + rw_l - 1);
        if (uart) {
                printf("uart: 0x%x - 0x%x\n", uart, uart + uartlen - 1);
        }

    #ifdef __riscv

        pmp_info_t info = pmp_probe();
        if (info.count == 0) {
                puts("pmp-not-supported");
                return 0;
        } else {
                printf("pmp.count: %d\n", info.count);
                printf("pmp.width: %d\n", info.width);
                printf("pmp.granularity: %d\n", info.granularity);
        }
        /* set up physical memory protection */
        pmp_entry_set(0, PMP_R | PMP_X, rx_s, rx_l);
        pmp_entry_set(1, PMP_R | PMP_W, rw_s, rw_l);
        if (uart) {
                pmp_entry_set(2, PMP_R | PMP_W, uart, uartlen);
        }
        pmp_entry_set(3, PMP_R , rd_s,rd_l);
        RO_Array[0]=1;
        printf("p.count: %d\n",  RO_Array[0]);

        /* switch to user mode enclave */
        mode_set_and_continue(PRV_U);
        puts("riscv-enclave");
        RO_Array[0]=2;

        printf("p.count: %d\n",  RO_Array[0]);
#else
        RO_Array[0]=2;
        printf("p.count: %d\n",  RO_Array[0]);
        puts("architecture-not-supported");
#endif
}

```
```bash
$ spike --isa=RV32IMAFDC build/bin/rv32imac/spike/probe
$ spike --isa=RV64IMAFDC build/bin/rv64imac/spike/probe
$ qemu-system-riscv32 -nographic -machine spike -kernel build/bin/rv32imac/spike/probe -bios none
$ qemu-system-riscv64 -nographic -machine spike -kernel build/bin/rv64imac/spike/probe -bios none
$ qemu-system-riscv32 -nographic -machine virt -kernel build/bin/rv32imac/virt/probe -bios none
$ qemu-system-riscv64 -nographic -machine virt -kernel build/bin/rv64imac/virt/probe -bios none
$ qemu-system-riscv32 -nographic -machine sifive_e -kernel build/bin/rv32imac/qemu-sifive_e/probe -bios none
$ qemu-system-riscv64 -nographic -machine sifive_e -kernel build/bin/rv64imac/qemu-sifive_e/probe -bios none
$ qemu-system-riscv32 -nographic -machine sifive_u -kernel build/bin/rv32imac/qemu-sifive_u/probe -bios none
$ qemu-system-riscv64 -nographic -machine sifive_u -kernel build/bin/rv64imac/qemu-sifive_u/probe -bios none
```
![](https://i.imgur.com/Ts4O50E.png)
https://github.com/michaeljclark/riscv-probe
這邊改了一些小地方，增加對RO_Array的保護，補充一下，mini-riscv-os 為什麼qemu 5.x用的好好的到了qemu 6,7 都會出現卡死的情況

![](https://i.imgur.com/KmJhAN0.png)
因為qemu 6,7預設都要對pmpcfg0進行初始化才行
```asm

    li      t0, 0x0                     #pmp config
    csrw    pmpaddr0, t0
    li      t0, 0xf
    csrw    pmpcfg0, t0
    csrw satp, zero
   
```
再來的話，還在排除有可能因為qemu的版本導致我沒辦法設置pmp的value達成記憶體保護，
參考riscv-probe其實可以發現qemu 可以指定 machine  type 或許換成相同machine 就可以pmp了

```c
#include "os.h"
extern void trap_init(void);
extern void trap_init(void);
extern void kernelvec();
extern void trap_vector();
extern int gethid();
extern int rko;
extern int taskTop;
extern int current_task;
extern struct context ctx_tasks[MAX_TASK];
extern void task_flush(int i, struct context *ctx_old, struct context *ctx_new);
extern void task_flush2();
void start();
extern int prev_task;
int init_main(void);
uint32_t sepc2 = 0;
struct context ctx_tmp;
void os_kernel()
{
	task_os();
}
#define EILM_SIZE 0x40000
/* Check platform support which PMP scheme!
 * CLIC platform only support NAPOT scheme! */
#define USE_NAPOT 1
#define USE_TOR !(USE_NAPOT)
#define SCHEME_NAPOT 3
#define SCHEME_NA4 2
#define SCHEME_TOR 1
#define SCHEME_OFF 0
#define NAPOT(base, size) (unsigned long)(((size) > 0) ? ((((unsigned long)(base) & (~((unsigned long)(size)-1))) >> 2) | (((unsigned long)(size)-1) >> 3)) : 0)
#define PMP_L_OFF 0
#define PMP_L_ON 1
#define PMP_A_OFF 0
#define PMP_A_TOR SCHEME_TOR
#define PMP_A_NA4 SCHEME_NA4
#define PMP_A_NAPOT SCHEME_NAPOT
#define PMP_X_OFF 0
#define PMP_X_ON 1
#define PMP_W_OFF 0
#define PMP_W_ON 1
#define PMP_R_OFF 0
#define PMP_R_ON 1
#define KB (0x1 << 10)
#define read_csr(reg) ({ unsigned int __tmp; \
  asm volatile ("csrr %0, " #reg : "=r"(__tmp)); __tmp; })
volatile unsigned int g_testmodify = 0;
unsigned char RO_Array[1 * KB] __attribute__((aligned(2 * KB)));
#define write_csr(reg, val) ({ asm volatile("csrw " #reg ", %0" ::"rK"(val)); })
void tmp()
{
}
#define TOR(top) (uint32_t)((uint32_t)(top) >> 2)
void pmp_napot_config(char entry, void *va, unsigned long size, char pmpcfg)
{
#pragma optimize("", off);
	unsigned long size2 = (unsigned long)((((unsigned long)(va) & (~((unsigned long)(size)-1))) >> 2) | (((unsigned long)(size)-1) >> 3));
#pragma optimize("", on);
	// printf("%ld\n",va);
	// printf("%ld\n",size);
	// printf("%ld\n",size2);
	switch (entry)
	{
	case 0:
		//		unsigned long tmp = (unsigned long)((((unsigned long)(va) & (~((unsigned long)(size) - 1))) >> 2) | (((unsigned long)(size) - 1) >> 3) );
		write_csr(pmpaddr0, size2);
		break;
	case 1:
		write_csr(pmpaddr1, size2);
		break;
	case 2:
		write_csr(pmpaddr2, size2);
		break;
	case 3:
		write_csr(pmpaddr3, size2);
		break;
	case 4:
		write_csr(pmpaddr4, size2);
		break;
	case 5:
		write_csr(pmpaddr5, size2);
		break;
	case 6:
		write_csr(pmpaddr6, size2);
		break;
	case 7:
		write_csr(pmpaddr7, size2);
		break;
	case 8:
		write_csr(pmpaddr8, size2);
		break;
	case 9:
		write_csr(pmpaddr9, size2);
		break;
	case 10:
		write_csr(pmpaddr10, size2);
		break;
	case 11:
		write_csr(pmpaddr11, size2);
		break;
	case 12:
		write_csr(pmpaddr12, size2);
		break;
	case 13:
		write_csr(pmpaddr13, size2);
		break;
	case 14:
		write_csr(pmpaddr14, size2);
		break;
	case 15:
		write_csr(pmpaddr15, size2);
		break;
	}

#if __riscv_xlen == 64
	switch (entry >> 3)
	{
	case 0:
		write_csr(pmpcfg0, ((read_csr(pmpcfg0) & (~(0xFFLL << ((long)(entry % 8) << 3)))) | (((long)pmpcfg) << ((long)(entry % 8) << 3))));
		break;
	case 1:
		write_csr(pmpcfg2, ((read_csr(pmpcfg2) & (~(0xFFLL << ((long)(entry % 8) << 3)))) | (((long)pmpcfg) << ((long)(entry % 8) << 3))));
		break;
	}
#else
	switch (entry >> 2)
	{
	case 0:
		write_csr(pmpcfg0, ((read_csr(pmpcfg0) & (~((0xFF) << ((entry % 4) << 3)))) | (((long)pmpcfg) << ((entry % 4) << 3))));
		break;
	case 1:
		write_csr(pmpcfg1, ((read_csr(pmpcfg1) & (~((0xFF) << ((entry % 4) << 3)))) | (((long)pmpcfg) << ((entry % 4) << 3))));
		break;
	case 2:
		write_csr(pmpcfg2, ((read_csr(pmpcfg2) & (~((0xFF) << ((entry % 4) << 3)))) | (((long)pmpcfg) << ((entry % 4) << 3))));
		break;
	case 3:
		write_csr(pmpcfg3, ((read_csr(pmpcfg3) & (~((0xFF) << ((entry % 4) << 3)))) | (((long)pmpcfg) << ((entry % 4) << 3))));
		break;
	}
#endif
}

void do_syscall(int syscall_num, int syscall_value)
{
	switch (syscall_num)
	{
	case 1:
		lib_printf("hello%d\n", syscall_value);
		ctx_tasks[current_task].a0 = syscall_value + 2;
		break;
	case 2:
		break;
	}
}
// interrupts and exceptions from kernel code go here via kernelvec,
// on whatever the current kernel stack is.
reg_t kerneltrap(reg_t epc, reg_t cause)
{
	intr_off();
	int which_dev = 0;
	uint32_t sepc = r_sepc();

	uint32_t sstatus = r_sstatus();
	uint32_t scause = r_scause();
	reg_t return_pc = sepc;
	reg_t cause_code = scause & 0xfff;
	// if(sepc2==0)
	// sepc2=r_sepc();
	// else
	// 	w_sepc(0x80008038);
	// sepc2=
	// w_sie(r_sie() & ~SIE_SSIE);
	if ((sstatus & SSTATUS_SPP) == 0)
		lib_puts("kerneltrap: not from supervisor mode\n");
	if (intr_get() != 0)
		lib_puts("kerneltrap: interrupts enabled\n");
	// lib_printf("%x\n", r_sepc());
	// lib_printf("%x\n", scause);
	lib_printf("%x\n", cause_code);
	if (cause & 0x80000000)
	{
		// lib_printf("spec %x\n", r_sepc());
		// lib_printf("%x\n", scause);
		// lib_printf("%x\n", cause_code);
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
		// lib_puts("Sync exceptions2!\n");
		// lib_printf("%x\n", scause);
		// lib_printf("%x\n", cause_code);
		switch (cause_code)
		{
		case 2:
			lib_puts("Illegal instruction!\n");
			return_pc += 4;
			break;
		case 8:
			lib_puts("Environment call from U-mode!\n");
			// intr_off();
			// do_syscall(ctx);
			// task_syscall(current_task);
			// task_os();
			struct context *ctx_now;
			ctx_now = &ctx_tasks[current_task];

			sys_switch(&ctx_now[current_task], &ctx_now[current_task]);

			lib_printf("%d\n", current_task);
			lib_printf("%d\n", ctx_now[current_task].s11);
			do_syscall(ctx_now[current_task].a7, ctx_now[current_task].s11);

			lib_printf("%d\n", ctx_tasks[current_task].a0);
			// task_flush2();
			return_pc += 4;
			// intr_on();
			break;
		case 9:
			lib_puts("Environment call from S-mode!\n");
			// suinter();
			return_pc += 4;

			break;

		default:
			/* Synchronous trap - exception */
			lib_printf("Sync exceptions! cause code: %d\n", cause_code);
			break;
		}
		// w_sepc(suinter);
		// w_mtvec((reg_t)trap_vector);
		//   w_mepc((uint64)main);
		// enable sup-mode interrupts.
		// w_sepc(init_main);
		// asm volatile("sret");
		// return_pc += 4;

		// while (1)
		// {
		// 	// break;
		// 	/* code */
		// }
	}

	unsigned long x2 = r_sstatus();
	// x2 &= ~SSTATUS_SIE;
	x2 &= ~SSTATUS_SPP; // clear SPP to 0 for user mode
	x2 |= SSTATUS_SPIE; // enable interrupts in user mode
	w_sstatus(x2);
	intr_on();
	return return_pc;
}
/* attribute is used for PA */
#define PMPCFG_ALXWR(a, l, x, w, r) (((a) << 3) | ((l) << 7) | ((x) << 2) | ((w) << 1) | ((r) << 0))
#define MSTATUS_MPRV_MASK (1 << 17) // previous mode.
void supmod()
{
	lib_puts("sup mod\n");
	// w_mip(r_mip() | MIP_MSIP);
	// w_mip(r_mip() | MIP_MSIP2);
	// w_mie(r_mie() | MIE_MSIE);
	uint32_t x = r_mstatus();
	x &= ~MSTATUS_MPP_MASK;
	// x | MSTATUS_MPRV_MASK;
	x |= MSTATUS_MPP_U;
	w_mstatus(x);

	w_medeleg(0xffff);
	w_mideleg(0xffff);
	w_sie(r_sie() | SIE_SEIE | SIE_STIE | SIE_SSIE | SIE_SEIE2 | SIE_STIE2 | SIE_SSIE2);
	//  w_sie(r_sie() & SIE_SEIE2);
	// set the sup-mode trap handler.
	w_stvec((reg_t)kernelvec);

	//   w_mepc((uint64)main);
	// enable sup-mode interrupts.
	// w_sepc(init_main);

	// set S Previous Privilege mode to User.
	// set S Previous Privilege mode to User.
	// unsigned long x2 = r_sstatus();
	// // x2 |= SSTATUS_SIE;
	// x2 &= ~SSTATUS_SPP; // clear SPP to 0 for user mode
	// x2 |= SSTATUS_SPIE; // enable interrupts in user mode
	// w_sstatus(x2);
	// asm volatile("ecall");

	// asm volatile("sret");
	// asm volatile("ecall");
	// suinter();
}
#define U32 *(volatile uint32_t *)
// static inline void w_pmpcfg(reg_t x)
// {
//   asm volatile("csrw pmpcfg1, 0xf");

// }

void pmpconfig()
{
	extern char _start;
	extern char __data_start;
	extern char stacks;
	// write_csr(pmpcfg0, 0x);
	// w_pmpcfg(0xf);
	// if (!read_csr(pmpcfg0)) {
	// 	lib_printf("PMP entries is 0, CPU does NOT support PMP.\n");
	// 	while(1);
	// }else
	// 	lib_printf("support PMP.\n");
	// lib_printf("support PMP. %x\n" ,&RO_Array[0]);
	// lib_printf("support PMP. %x\n" ,(&RO_Array[0] + sizeof(RO_Array)));

	
	/* PMP addresses are 4-byte aligned, drop the bottom two bits */
	size_t protected_addr = ((size_t) &RO_Array[0]) ;
	
	/* Clear the bit corresponding with alignment */
	// protected_addr &= ~(NAPOT_SIZE >> 3);

	/* Set the bits up to the alignment bit */
	// protected_addr |= ((NAPOT_SIZE >> 3) - 1);

	write_csr(pmpaddr0, TOR( (void*)&RO_Array[0]));
	write_csr(pmpaddr1, TOR((void *)&RO_Array[0])+1);
	write_csr(pmpaddr2, TOR((void *)(&RO_Array[0] + sizeof(RO_Array))));
	lib_printf("support PMP. %x\n", read_csr(pmpaddr1));
	lib_printf("support PMP. %x\n", read_csr(pmpaddr2));
	write_csr(pmpcfg0, 0x00880F0F);
		// write_csr(pmpcfg0, 0x0008ffff&read_csr(pmpcfg0));

	lib_printf("support PMP. %x\n", read_csr(pmpcfg0));
	// write_csr(pmpcfg1, PMPCFG_ALXWR(PMP_A_TOR, PMP_L_OFF, PMP_X_OFF, PMP_W_ON, PMP_R_ON));
	// write_csr(pmpcfg2, PMPCFG_ALXWR(PMP_A_TOR, PMP_L_ON, PMP_X_OFF, PMP_W_OFF, PMP_R_ON));

	lib_puts("OS start\n");
}
// #define KERNBASE 0x80101000
void os_start()
{
	lib_puts("OS start\n");
	user_init();
	trap_init();
	timer_init(); // start timer interrupt ...
	supmod();
	// pmpconfig();
	
	// lib_printf("kernel stap. %x\n",  (KERNBASE >> 12));
	(*((unsigned long *)((long)&RO_Array[0]))) = 0x5555AAAA;
	g_testmodify = 0x5555AAAA;
	if (0x5555AAAA == (*((unsigned long *)((long)&RO_Array[0]))))
	{
		lib_printf("[Store Pass]\n");
		// printf("[Store Pass]\n");
	}
	else
	{
		lib_printf("[Store Fail]\n");
	}
	asm volatile("li   a1,1");
	asm volatile("csrw sip, a1");

	w_mepc((reg_t)start);
	asm volatile("mret");
	//  li   a1,1
	// csrw sip, a1
}

int os_main(void)
{
	os_start();

	return 0;
}
void start()
{

	(*((unsigned long *)((long)&RO_Array[0]))) = 0x5555AAA2;
	g_testmodify = 0x5555AAAA;
	if (0x5555AAA2 == (*((unsigned long *)((long)&RO_Array[0]))))
	{
		lib_printf("[Store Pass]\n");
		// printf("[Store Pass]\n");
	}
	else
	{
		lib_printf("[Store Fail]\n");
	}
	// (*((unsigned long*)((long)&RO_Array[0]))) = 0x5555AAAA;
	// while(1){}
	int current_task = 0;
	while (1)
	{
		lib_puts("OS: Activate next task\n");
		task_go(current_task);
		lib_puts("OS: Back to OS\n");
		current_task = (current_task + 1) % taskTop; // Round Robin Scheduling
		lib_puts("\n");
	}
}
```
這邊查看蠻多次確定沒什麼問題，可能一些小細節沒注意到
或許是qemu -machine virt
換成spike 就ok ,這可能要找時間再試了近期不會再更新.

