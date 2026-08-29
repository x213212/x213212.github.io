---
title: "qemu virtio net lwip"
date: "2025-08-04T00:57:00.004+08:00"
updated: "2025-08-04T00:57:45.641+08:00"
permalink: "/2025/08/qemu-virtio-net-lwip.html"
original_url: "https://x8795278.blogspot.com/2025/08/qemu-virtio-net-lwip.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-141267698839965863"
tags: ["net", "qemu", "virtio"]
layout: post
---

![](https://hackmd.io/_uploads/ryRc6W6Dge.png)

# qemu virtio net lwip
整個改動在這個commit 實現
https://github.com/x213212/mini-riscv-os/commit/64d82fd26d69ecdd1985264ac2261d8a8919f46a
研究一下怎麼在 qemu 裡面新增一張 virtio 網卡並註冊到 lwip，使用一些常見的協議
![image](https://hackmd.io/_uploads/B1uCabpvxx.png)
這邊要讓 qemu 網卡收到封包，要透過橋接的方式送qemu虛擬網卡封包
```bash
# 建立 bridge
sudo ip addr add 192.168.100.1/24 dev br0
sudo ip link set br0 up
sudo ip link add name br0 type bridge

# 把實體網卡加入橋接（先下線）
sudo ip link set ens33 down
sudo ip link set ens33 master br0
sudo ip link set ens33 up

# 建立 tap 裝置（若沒有）
sudo ip tuntap add dev tap0 mode tap user $(whoami)

# 把 tap0 加入橋接並開啟
sudo ip link set tap0 master br0
sudo ip link set tap0 up

# 開啟橋接介面
sudo ip link set br0 up

```
檢查狀態
```bash
ip link show br0
ip link show ens33
ip link show tap0
```
反正到時候看到staus 裡面都要up就對了。
注意tap0是在你qemu run 起來 tap 再透過ip link show tap0 查看status才看的到 status up
```
4: br0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000
    link/ether 4e:5d:19:e5:6c:cd brd ff:ff:ff:ff:ff:ff
2: ens33: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000
    link/ether 00:0c:29:d4:9c:38 brd ff:ff:ff:ff:ff:ff
    altname enp2s1
```
```
x213212@x213212-VMware-Virtual-Platform:~/qemu2/qemu/build$ ip link show tap0 
3: tap0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc pfifo_fast master br0 state DOWN mode DEFAULT group default qlen 1000
    link/ether e6:69:14:e9:1e:b3 brd ff:ff:ff:ff:ff:ff
x213212@x213212-VMware-Virtual-Platform:~/qemu2/qemu/build$ ip link show tap0 
3: tap0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast master br0 state UP mode DEFAULT group default qlen 1000
    link/ether e6:69:14:e9:1e:b3 brd ff:ff:ff:ff:ff:ff
```

qemu 網卡設定，這邊為了掩飾方便，我找了之前研究的 git repo
https://github.com/x213212/mini-riscv-os/tree/master/08-BlockDeviceDriver
這邊makefile要做幾種新增
```makefile
CC = /home/x213212/riscv/bin/riscv32-unknown-elf-gcc
CFLAGS = -nostdlib -fno-builtin -mcmodel=medany -march=rv32imac_zicsr -mabi=ilp32  -DLWIP_NO_CTYPE_H -g -Wall -w -I./ -I./lwip/src/include -I./lwip/src/core -I./lwip/src/netif  
GDB = /home/x213212/riscv/bin/riscv64-unknown-elf-gdb
```
現在要引入lwip這樣就可以在 bare metal 使用簡單的tcp.udp 協議
這邊還要額外下載lwip
https://github.com/lwip-tcpip/lwip
放到你的根目錄
add .c
```makefile
OBJ = \
start.s \
sys.s \
lib.c \
timer.c \
task.c \
os.c \
user.c \
trap.c \
lock.c \
plic.c \
virtio.c \
string.c \
lwip/src/core/def.c\
lwip/src/core/init.c\
lwip/src/core/mem.c\
lwip/src/core/memp.c\
lwip/src/core/netif.c\
lwip/src/core/pbuf.c\
lwip/src/core/raw.c\
lwip/src/core/sys.c\
lwip/src/core/tcp.c\
lwip/src/core/tcp_in.c\
lwip/src/core/tcp_out.c\
lwip/src/core/udp.c\
lwip/src/core/ip.c\
lwip/src/netif/ethernet.c\
lwip/src/netif/lowpan6.c\
lwip/src/core/timeouts.c\
lwip/src/core/inet_chksum.c\
lwip/src/core/ipv4/ip4.c\
lwip/src/core/ipv4/acd.c\
lwip/src/core/ipv4/autoip.c\
lwip/src/core/ipv4/igmp.c\
lwip/src/core/ipv4/ip4_addr.c\
lwip/src/core/ipv4/icmp.c\
lwip/src/core/ipv4/dhcp.c\
lwip/src/core/ipv4/etharp.c\
lwip/src/core/ipv4/ip4_frag.c\
lwip/src/core/sys.c
```

接下就要新增大概三個檔案
lwipopts.h 這個放在當前目錄
```h
#define SYS_LIGHTWEIGHT_PROT 0
#define NO_SYS 1                   // 不使用RTOS，裸機模式
#define LWIP_ARP 1                // 啟用ARP
#define LWIP_ICMP 1                // 啟用ICMP
#define LWIP_TCP 1                // 啟用TCP
#define LWIP_UDP 1                 // 啟用UDP
#define LWIP_DHCP 1                // DHCP可選
#define LWIP_NETCONN 0
#define LWIP_SOCKET 0
#define MEM_SIZE 16000             // lwIP核心記憶體大小
#define MEMP_NUM_PBUF 16
#define MEMP_NUM_TCP_PCB 5
#define MEMP_NUM_TCP_PBUF 16
#define PBUF_POOL_SIZE 16
#define TCP_MSS 1460
#define TCP_WND (4 * TCP_MSS)
#define LWIP_DEBUG 0
#define LWIP_PLATFORM_DIAG(x) do { } while(0)
#define LWIP_DEBUG 0
#define LWIP_NO_STDOUT 1
#define LWIP_STATS 0
// #define LWIP_SOCKET     1
// #define LWIP_IPV4       1
```
你還要再
/home/x213212/mini-riscv-os/08-BlockDeviceDriver/lwip/src/include/lwip/arch
裡面新增兩個檔案
cc.h
```h
#ifndef LWIP_ARCH_CC_H
#define LWIP_ARCH_CC_H

#include <stdint.h>
#include "riscv.h"
// Fixed-width integer types
typedef uint8_t  u8_t;
typedef int8_t   s8_t;
typedef uint16_t u16_t;
typedef int16_t  s16_t;
typedef uint32_t u32_t;
typedef int32_t  s32_t;
#define MSTATUS_MIE (1 << 3)

// Type used for interrupt protection
typedef unsigned int sys_prot_t;

// Implement interrupt protection using your own enable/disable interrupt functions
static inline sys_prot_t sys_arch_protect(void) {
    // Disable machine mode interrupts (e.g., clear MIE)
    unsigned int mstatus = r_mstatus();
    w_mstatus(mstatus & ~MSTATUS_MIE);
    return mstatus; // Return old status for restoration
}

static inline void sys_arch_unprotect(sys_prot_t state) {
    // Restore previous interrupt status
    w_mstatus(state);
}

// Define empty macros for lwIP protection functions (customize for finer granularity if needed)
#define SYS_ARCH_DECL_PROTECT(level)  sys_prot_t level
#define SYS_ARCH_PROTECT(level)       (level = sys_arch_protect())
#define SYS_ARCH_UNPROTECT(level)     sys_arch_unprotect(level)

// Byte order
#define LWIP_PLATFORM_BYTESWAP 0

#endif /* LWIP_ARCH_CC_H */

```
sys_arch.h
```h
#ifndef LWIP_HDR_ARCH_SYS_ARCH_H
#define LWIP_HDR_ARCH_SYS_ARCH_H

/* For NO_SYS=1, define empty types and macros for compatibility with lwIP. */

typedef uint32_t sys_prot_t;

#define SYS_MBOX_NULL  NULL   // Mailbox null placeholder
#define SYS_SEM_NULL   NULL   // Semaphore null placeholder

typedef int sys_sem_t;        // Semaphore type (dummy for NO_SYS=1)
typedef int sys_mbox_t;       // Mailbox type (dummy for NO_SYS=1)
typedef int sys_thread_t;     // Thread type (dummy for NO_SYS=1)

/* No actual interrupt protection in NO_SYS=1, just stubs */
static inline sys_prot_t sys_arch_protect(void) { return 0; }
static inline void sys_arch_unprotect(sys_prot_t p) { (void)p; }

#endif /* LWIP_HDR_ARCH_SYS_ARCH_H */

```
然後qemu這邊可以配置你的網卡，這邊本來順便初始化鍵盤與滑鼠驅動但是可能我run在windows 虛擬機裡面，收不到滑鼠與鍵盤的irq訊號，這部份過幾天再研究。
```makefile
QEMU = /home/x213212/qemu2/qemu/build/qemu-system-riscv32  \
   -smp 1 -machine virt -bios none \
  -drive if=none,format=raw,file=hdd.dsk,id=x0 \
  -device virtio-blk-device,drive=x0,bus=virtio-mmio-bus.0 \
  -device virtio-net-device,netdev=net0,mac=52:54:00:12:34:56 \
  -netdev tap,id=net0,ifname=tap0,script=no,downscript=no \
  -d guest_errors -icount shift=0,align=off,sleep=off \
  -device virtio-keyboard-device \
  -device virtio-mouse-device \
  -monitor telnet:localhost:4321,server,nowait
```

這邊要注意我在編譯過程中有遇到某些c code 是有使用ctype 類型的function
-DLWIP_NO_CTYPE_H
所以我在編譯有額外再加入這個
/home/x213212//mini-riscv-os/08-BlockDeviceDriver/lwip/src/include/lwip/arch.h
```h
#ifndef LWIP_NO_CTYPE_H
#define LWIP_NO_CTYPE_H 0
#endif

#if LWIP_NO_CTYPE_H
#define lwip_in_range(c, lo, up)  ((u8_t)(c) >= (lo) && (u8_t)(c) <= (up))
#define lwip_isdigit(c)           lwip_in_range((c), '0', '9')
#define lwip_isxdigit(c)          (lwip_isdigit(c) || lwip_in_range((c), 'a', 'f') || lwip_in_range((c), 'A', 'F'))
#define lwip_islower(c)           lwip_in_range((c), 'a', 'z')
#define lwip_isspace(c)           ((c) == ' ' || (c) == '\f' || (c) == '\n' || (c) == '\r' || (c) == '\t' || (c) == '\v')
#define lwip_isupper(c)           lwip_in_range((c), 'A', 'Z')
#define lwip_tolower(c)           (lwip_isupper(c) ? (c) - 'A' + 'a' : c)
#define lwip_toupper(c)           (lwip_islower(c) ? (c) - 'a' + 'A' : c)
#else
#include <ctype.h>
#define lwip_isdigit(c)           isdigit((unsigned char)(c))
#define lwip_isxdigit(c)          isxdigit((unsigned char)(c))
#define lwip_islower(c)           islower((unsigned char)(c))
#define lwip_isspace(c)           isspace((unsigned char)(c))
#define lwip_isupper(c)           isupper((unsigned char)(c))
#define lwip_tolower(c)           tolower((unsigned char)(c))
#define lwip_toupper(c)           toupper((unsigned char)(c))
#endif
```

然後在
lib.c新增幾個glibc 簡單的 function 實作
```c

// abort implementation: infinite loop or system reset trigger
void abort(void)
{
    while (1)
    {
        // You can place watchdog reset or blink LED code here
    }
}
int fflush(void* stream) {
    // No flush needed on baremetal, just return success
    (void)stream;  // Avoid unused parameter warning
    return 0;
}
int atoi(const char *s) {
    int n = 0;
    while (*s >= '0' && *s <= '9') {
        n = n * 10 + (*s - '0');
        s++;
    }
    return n;
}

int memcmp(const void *s1, const void *s2, size_t n) {
    const unsigned char *p1 = s1, *p2 = s2;
    for (size_t i = 0; i < n; i++) {
        if (p1[i] != p2[i])
            return (int)(p1[i] - p2[i]);
    }
    return 0;
}

// Minimal bare-metal strstr, not NULL-safe
char* strstr(const char* haystack, const char* needle)
{
    if (!*needle) return (char*)haystack;
    for (; *haystack; haystack++) {
        const char *h = haystack, *n = needle;
        while (*h && *n && *h == *n) { h++; n++; }
        if (!*n) return (char*)haystack;
    }
    return 0;
}
void panic(char *s)
{
	lib_puts(s);
	for (;;)
	{
	}
}

// strlen implementation
size_t strlen(const char *s)
{
    size_t len = 0;
    while (s[len] != '\0')
        len++;
    return len;
}

// strncmp implementation
int strncmp(const char *s1, const char *s2, size_t n)
{
    for (size_t i = 0; i < n; i++)
    {
        if (s1[i] != s2[i])
            return (unsigned char)s1[i] - (unsigned char)s2[i];
        if (s1[i] == '\0')
            return 0;
    }
    return 0;
}

```

注意在bare metal 還要加入一些64bit的 soft function 實作，這邊靠chatgpt幫忙gen
```c

// 64-bit unsigned modulo, return remainder
uint64_t __umoddi3(uint64_t n, uint64_t d) {
    uint64_t r = 0;
    for (int i = 63; i >= 0; i--) {
        r = (r << 1) | ((n >> i) & 1);
        if (r >= d) {
            r -= d;
        }
    }
    return r;
}

// 64-bit unsigned division software implementation for __udivdi3
uint64_t __udivdi3(uint64_t numerator, uint64_t denominator) {
    uint64_t quotient = 0, remainder = 0;
    int i;

    if (denominator == 0) {
        // Handle divide by zero if needed
        return 0xFFFFFFFFFFFFFFFFULL;
    }

    for (i = 63; i >= 0; i--) {
        remainder = (remainder << 1) | ((numerator >> i) & 1);
        if (remainder >= denominator) {
            remainder -= denominator;
            quotient |= (1ULL << i);
        }
    }
    return quotient;
}

// Signed division
int64_t __divdi3(int64_t n, int64_t d) {
    int sign = 1;
    if (n < 0) { n = -n; sign = -sign; }
    if (d < 0) { d = -d; sign = -sign; }
    uint64_t q = __udivdi3((uint64_t)n, (uint64_t)d);
    return sign * (int64_t)q;
}

// Signed modulo
int64_t __moddi3(int64_t n, int64_t d) {
    int sign = 1;
    if (n < 0) { n = -n; sign = -sign; }
    if (d < 0) { d = -d; }
    uint64_t r = __umoddi3((uint64_t)n, (uint64_t)d);
    return sign * (int64_t)r;
}
```
這邊初始化9個irq，可能實際有8個這邊不確定。
plic.c
```c
// plic.c
#include "os.h"
#include <stdint.h>

// ---------- PLIC definitions ----------
#define PLIC_BASE             0x0c000000UL
#define PLIC_PRIORITY(id)     (PLIC_BASE + ((id) * 4))
#define PLIC_PENDING(id)      (PLIC_BASE + 0x1000 + (((id) / 32) * 4))
#define PLIC_MENABLE(hart)    (PLIC_BASE + 0x2000 + (hart) * 0x80)
#define PLIC_MTHRESHOLD(hart) (PLIC_BASE + 0x200000 + (hart) * 0x1000)
#define PLIC_MCLAIM(hart)     (PLIC_BASE + 0x200004 + (hart) * 0x1000)
#define PLIC_MCOMPLETE(hart)  PLIC_MCLAIM(hart) // Write back to the same register to complete

// helpers
static inline void write32(uintptr_t addr, uint32_t val) {
    *(volatile uint32_t *)addr = val;
    asm volatile("" ::: "memory");
}
static inline uint32_t read32(uintptr_t addr) {
    return *(volatile uint32_t *)addr;
}

// ---------- mscratch setup (xv6-style) ----------
#define MAX_HARTS 4
#define SCRATCH_PER_HART 256  // 256 bytes per hart, enough for reg_save/reg_load

__attribute__((aligned(16))) static uint8_t scratch_space[MAX_HARTS * SCRATCH_PER_HART];

void setup_mscratch_for_hart(void) {
    int hart = r_mhartid();
    uintptr_t base = (uintptr_t)(scratch_space + hart * SCRATCH_PER_HART);
    // optional: zero it out to avoid stale data
    for (int i = 0; i < SCRATCH_PER_HART; i += 8) {
        *(uint64_t *)(base + i) = 0;
    }
    w_mscratch(base);
}

// PLIC priority limits: read from your platform (hardcoded here based on qemu virt)
#define PLIC_MAX_PRIORITY 7

static void plic_enable_irq(int hart, uint32_t irq, uint32_t priority) {
    if (irq == 0) return;

    // clamp priority
    if (priority == 0) priority = 1;
    if (priority > PLIC_MAX_PRIORITY) priority = PLIC_MAX_PRIORITY;
    write32(PLIC_PRIORITY(irq), priority);

    // enable in the appropriate word
    uintptr_t enable_word = PLIC_MENABLE(hart) + (irq / 32) * 4;
    uint32_t v = read32(enable_word);
    v |= (1u << (irq % 32));
    write32(enable_word, v);
}

void plic_init(void)
{
    int hart = r_mhartid();

    // Make sure mscratch is set if your trap vector uses it
    // setup_mscratch_for_hart();

    // Set threshold = 0 to accept priority >=1
    write32(PLIC_MTHRESHOLD(hart), 0);

    // Enable relevant sources with priorities (example list)
    struct { uint32_t irq; uint32_t prio; } sources[] = {
        { UART0_IRQ, 1 },
        { VIRTIO_IRQ, 2 },
        { VIRTIO_IRQ2, 3 },
        { VIRTIO_IRQ3, 4 },
        { VIRTIO_IRQ4, 5 },
        { VIRTIO_IRQ5, 7 },
        { VIRTIO_IRQ6, 7 },
        { VIRTIO_IRQ7, 7 },
        { VIRTIO_IRQ8, 7 },
        { VIRTIO_IRQ9, 7 },
    };
    int n = sizeof(sources) / sizeof(sources[0]);
    for (int i = 0; i < n; i++) {
        plic_enable_irq(hart, sources[i].irq, sources[i].prio);
    }

    // Enable external interrupts in mie & global
    w_mie(r_mie() | MIE_MEIE);
    w_mstatus(r_mstatus() | MSTATUS_MIE);
}

int plic_claim()
{
    int hart = r_mhartid();
    return (int)read32(PLIC_MCLAIM(hart));
}

void plic_complete(int irq)
{
    if (irq == 0) return;
    int hart = r_mhartid();
    write32(PLIC_MCOMPLETE(hart), (uint32_t)irq);
}

```

riscv.h
```h
#ifndef __RISCV_H__
#define __RISCV_H__

#include <stdint.h>

#ifdef __riscv_xlen64
  typedef uint64_t reg_t;
#else
  typedef uint32_t reg_t;
#endif
#define PGSIZE 4096 // bytes per page

// ref: https://www.activexperts.com/serial-port-component/tutorials/uart/
#define UART 0x10000000L
#define UART_THR (volatile uint8_t *)(UART + 0x00) // THR: transmitter holding register
#define UART_RHR (volatile uint8_t *)(UART + 0x00) // RHR: receive holding register
#define UART_DLL (volatile uint8_t *)(UART + 0x00) // LSB of divisor latch (write mode)
#define UART_DLM (volatile uint8_t *)(UART + 0x01) // MSB of divisor latch (write mode)
#define UART_IER (volatile uint8_t *)(UART + 0x01) // Interrupt Enable Register
#define UART_LCR (volatile uint8_t *)(UART + 0x03) // Line Control Register
#define UART_LSR (volatile uint8_t *)(UART + 0x05) // LSR: line status register
#define UART_LSR_EMPTY_MASK 0x40                   // LSR Bit 6: transmitter empty; both THR and LSR are empty

#define UART_REGR(reg) (*(reg))
#define UART_REGW(reg, v) ((*reg) = (v))

// ref: https://github.com/qemu/qemu/blob/master/include/hw/riscv/virt.h
// enum {
//     UART0_IRQ = 10,
//     RTC_IRQ = 11,
//     VIRTIO_IRQ = 1, /* 1 to 8 */
//     VIRTIO_COUNT = 8,
//     PCIE_IRQ = 0x20, /* 32 to 35 */
//     VIRTIO_NDEV = 0x35 /* Arbitrary maximum number of interrupts */
// };
#define UART0_IRQ 10
#define VIRTIO_IRQ 1
#define VIRTIO_IRQ2 2
#define VIRTIO_IRQ3 3
#define VIRTIO_IRQ4 4
#define VIRTIO_IRQ5 5
#define VIRTIO_IRQ6 6
#define VIRTIO_IRQ7 7
#define VIRTIO_IRQ8 8
#define VIRTIO_IRQ9 9

// Saved registers for kernel context switches
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
// Local interrupt controller, contains the timer
// ================== Timer Interrupt ====================

#define NCPU 8 // maximum number of CPUs
#define CLINT 0x2000000
#define CLINT_MTIMECMP(hartid) (CLINT + 0x4000 + 4 * (hartid))
#define CLINT_MTIME (CLINT + 0xBFF8) // cycles since boot

static inline reg_t r_tp()
{
  reg_t x;
  asm volatile("mv %0, tp"
               : "=r"(x));
  return x;
}

// Return which hart (core) this is

static inline reg_t r_mhartid()
{
  reg_t x;
  asm volatile("csrr %0, mhartid"
               : "=r"(x));
  return x;
}

// Machine Status Register, mstatus
#define MSTATUS_MPP_MASK (3L << 11) // previous mode
#define MSTATUS_MPP_M (3L << 11)
#define MSTATUS_MPP_S (1L << 11)
#define MSTATUS_MPP_U (0L << 11)
#define MSTATUS_MIE (1L << 3) // machine-mode interrupt enable

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

// Machine exception program counter, holds the
// instruction address to return to from exception
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

// Machine-mode Interrupt Enable
#define MIE_MEIE (1L << 11) // external
#define MIE_MTIE (1L << 7)  // timer
#define MIE_MSIE (1L << 3)  // software

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

#endif
```

timer.c
```c
#ifndef __RISCV_H__
#define __RISCV_H__

#include <stdint.h>

// Register width type (64-bit or 32-bit depending on architecture)
#ifdef __riscv_xlen64
  typedef uint64_t reg_t;
#else
  typedef uint32_t reg_t;
#endif

#define PGSIZE 4096 // bytes per page

// UART base address and register definitions (see: https://www.activexperts.com/serial-port-component/tutorials/uart/)
#define UART 0x10000000L
#define UART_THR (volatile uint8_t *)(UART + 0x00) // THR: transmitter holding register
#define UART_RHR (volatile uint8_t *)(UART + 0x00) // RHR: receiver holding register
#define UART_DLL (volatile uint8_t *)(UART + 0x00) // LSB of divisor latch (write mode)
#define UART_DLM (volatile uint8_t *)(UART + 0x01) // MSB of divisor latch (write mode)
#define UART_IER (volatile uint8_t *)(UART + 0x01) // Interrupt Enable Register
#define UART_LCR (volatile uint8_t *)(UART + 0x03) // Line Control Register
#define UART_LSR (volatile uint8_t *)(UART + 0x05) // LSR: line status register
#define UART_LSR_EMPTY_MASK 0x40                   // LSR Bit 6: transmitter empty; both THR and LSR are empty

#define UART_REGR(reg) (*(reg))
#define UART_REGW(reg, v) ((*reg) = (v))

// IRQ definitions (see: https://github.com/qemu/qemu/blob/master/include/hw/riscv/virt.h)
// UART0 IRQ = 10, VirtIO IRQs = 1-9
#define UART0_IRQ 10
#define VIRTIO_IRQ 1
#define VIRTIO_IRQ2 2
#define VIRTIO_IRQ3 3
#define VIRTIO_IRQ4 4
#define VIRTIO_IRQ5 5
#define VIRTIO_IRQ6 6
#define VIRTIO_IRQ7 7
#define VIRTIO_IRQ8 8
#define VIRTIO_IRQ9 9

// Saved registers for kernel context switches
struct context
{
  reg_t ra;   // Return address
  reg_t sp;   // Stack pointer

  // Callee-saved registers
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

// Local interrupt controller, contains the timer (see: https://github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/riscv.h)
// ================== Timer Interrupt ====================

#define NCPU 8 // Maximum number of CPUs
#define CLINT 0x2000000
#define CLINT_MTIMECMP(hartid) (CLINT + 0x4000 + 4 * (hartid)) // Timer compare register per hart
#define CLINT_MTIME (CLINT + 0xBFF8) // Cycles since boot

// Read thread pointer register
static inline reg_t r_tp()
{
  reg_t x;
  asm volatile("mv %0, tp"
               : "=r"(x));
  return x;
}

// Read hardware thread (hart) ID
static inline reg_t r_mhartid()
{
  reg_t x;
  asm volatile("csrr %0, mhartid"
               : "=r"(x));
  return x;
}

// Machine Status Register, mstatus
#define MSTATUS_MPP_MASK (3L << 11) // Previous mode mask
#define MSTATUS_MPP_M (3L << 11)    // Machine mode
#define MSTATUS_MPP_S (1L << 11)    // Supervisor mode
#define MSTATUS_MPP_U (0L << 11)    // User mode
#define MSTATUS_MIE (1L << 3)       // Machine-mode interrupt enable

// Read mstatus CSR
static inline reg_t r_mstatus()
{
  reg_t x;
  asm volatile("csrr %0, mstatus"
               : "=r"(x));
  return x;
}

// Write mstatus CSR
static inline void w_mstatus(reg_t x)
{
  asm volatile("csrw mstatus, %0"
               :
               : "r"(x));
}

// Machine exception program counter (holds the instruction address to return to from exception)
static inline void w_mepc(reg_t x)
{
  asm volatile("csrw mepc, %0"
               :
               : "r"(x));
}

// Read mepc CSR
static inline reg_t r_mepc()
{
  reg_t x;
  asm volatile("csrr %0, mepc"
               : "=r"(x));
  return x;
}

// Machine Scratch register (used by early trap handler)
static inline void w_mscratch(reg_t x)
{
  asm volatile("csrw mscratch, %0"
               :
               : "r"(x));
}

// Machine-mode interrupt vector base address
static inline void w_mtvec(reg_t x)
{
  asm volatile("csrw mtvec, %0"
               :
               : "r"(x));
}

// Machine-mode Interrupt Enable bits
#define MIE_MEIE (1L << 11) // External interrupt enable
#define MIE_MTIE (1L << 7)  // Timer interrupt enable
#define MIE_MSIE (1L << 3)  // Software interrupt enable

// Read mie CSR
static inline reg_t r_mie()
{
  reg_t x;
  asm volatile("csrr %0, mie"
               : "=r"(x));
  return x;
}

// Write mie CSR
static inline void w_mie(reg_t x)
{
  asm volatile("csrw mie, %0"
               :
               : "r"(x));
}

#endif

```

trap.c
這邊從process原本的搶佔式，變成協同模式，並新增一個irq 網卡收到封包後會觸發一個irq，
這邊我弄蠻久，每次切換task sp都會少0x20,多跑幾分鐘整個就會qemu crash，這邊先這樣
```c
    else if (irq == VIRTIO_IRQ8)
    {
        lib_puts("Virtio net IRQ\n");
        virtio_net_interrupt_handler();
    }

    case 7:
        lib_puts("timer interruption!\n");
        w_mie(r_mie() & ~(1 << 7));
        timer_handler();       // Update timer
        need_resched = 1;     // Only set flag, do not directly switch context
        w_mie(r_mie() | MIE_MTIE); // Ensure timer interrupt is enabled
        reg_t sp;
        asm volatile("mv %0, sp" : "=r"(sp));
        lib_printf("Current sp in trap_handler: 0x%llx\n", (unsigned long long)sp);
        break;
```
這邊就交給 user.c 自動將cpu主控權交給os了
user.c
```c
#include "os.h"

int shared_var = 500;
extern volatile int need_resched;

lock_t lock;

void user_task0(void)
{
	lib_puts("Task0: Created!\n");
	while (1)
	{
		lib_puts("Task0: Running...\n");
		lib_delay(1000);

 if (need_resched) {
            lib_puts("Task1: Yield to OS...\n");  // debug 用
            need_resched = 0;
            task_os();
        }
    }
	}

void user_task1(void)
{
	lib_puts("Task1: Created!\n");
	while (1)
	{
		lib_puts("Task1: Running...\n");
		lib_delay(1000);

 if (need_resched) {
            lib_puts("Task1: Yield to OS...\n");  // debug 用
            need_resched = 0;
            task_os();
        }
    }
	}

void user_task2(void)
{
	lib_puts("Task2: Created!\n");
	while (1)
	{
		for (int i = 0; i < 50; i++)
		{
			lock_acquire(&lock);
			shared_var++;
			lock_free(&lock);
			lib_delay(100);
		}
		lib_printf("The value of shared_var is: %d \n", shared_var);
	}
}

void user_task3(void)
{
	lib_puts("Task3: Created!\n");
	while (1)
	{
		lib_puts("Trying to get the lock... \n");
		lock_acquire(&lock);
		lib_puts("Get the lock!\n");
		lock_free(&lock);
		lib_delay(1000);
		
	}
}

void user_init()
{
	// lock_init(&lock);
	task_create(&user_task0);
	task_create(&user_task1);
	// task_create(&user_task2);
	// task_create(&user_task3);
}

```

現在進入到初始化網卡的部分，
這邊要注意的是分兩個步驟，第一是對virtio net網卡進行初始化，第二步驟再把網卡註冊進 lwip,
這邊是否一定要lwip才能接受網頁協定?，不一定，你完全可以透過控制rx tx，攔截你想要的封包，檢測到什麼發送你要的封包出去,
你可以註冊完網卡就開一個小型 httpserver 擬就可以透過curl 或者網頁連到。，理所當然也可以自己ping
![image](https://hackmd.io/_uploads/ryRc6W6Dge.png)
![image](https://hackmd.io/_uploads/B1uCabpvxx.png)
還是說要開啟一個http server這邊都是沒問題的`,看你要直接polling 還是等isr 都ok
```c
    simple_http_server_raw();
    net_init = 1 ;
    // It is recommended to run RX loop or call sys_check_timeouts() regularly here
    while (1) {
          virtio_net_rx_loop2();    // RX event loop, do not omit!
        sys_check_timeouts();     // TCP timeout/retransmit
    }
```
```c

#define VIRTIO_NET_BASE   0x10008000UL
#define NET_QUEUE_SIZE    64
#define ETH_FRAME_SIZE    1600
#define PGSIZE           4096
#define RAM_BASE         0x80000000UL

#define R_NET(addr) ((volatile uint32_t *)(VIRTIO_NET_BASE + (addr)))

// Virtio MMIO Registers (non-legacy)
#define VIRTIO_MMIO_MAGIC_VALUE       0x000
#define VIRTIO_MMIO_VERSION           0x004
#define VIRTIO_MMIO_DEVICE_ID         0x008
#define VIRTIO_MMIO_VENDOR_ID         0x00c
#define VIRTIO_MMIO_DEVICE_FEATURES   0x010
#define VIRTIO_MMIO_DRIVER_FEATURES   0x020
#define VIRTIO_MMIO_FEATURES_SEL      0x014
#define VIRTIO_MMIO_QUEUE_SEL         0x030
#define VIRTIO_MMIO_QUEUE_NUM_MAX     0x034
#define VIRTIO_MMIO_QUEUE_NUM         0x038
#define VIRTIO_MMIO_QUEUE_READY       0x044
#define VIRTIO_MMIO_QUEUE_NOTIFY      0x050
#define VIRTIO_MMIO_INTERRUPT_STATUS  0x060
#define VIRTIO_MMIO_INTERRUPT_ACK     0x064
#define VIRTIO_MMIO_STATUS            0x070
#define VIRTIO_MMIO_GUEST_PAGE_SIZE   0x028

#define VRING_DESC_F_NEXT  1
#define VRING_DESC_F_WRITE 2

#define VIRTIO_CONFIG_S_ACKNOWLEDGE 0x01
#define VIRTIO_CONFIG_S_DRIVER      0x02
#define VIRTIO_CONFIG_S_DRIVER_OK   0x04
#define VIRTIO_CONFIG_S_FEATURES_OK 0x08
#define VIRTIO_CONFIG_S_FAILED      0x80

typedef struct {
    char pages[2 * PGSIZE] __attribute__((aligned(PGSIZE)));
    virtq_desc_t *desc;         // RX descriptors
    virtq_avail_t *avail;       // RX avail ring
    virtq_used_t *used;         // RX used ring
    uint16_t used_idx;

    // TX queue
    char tx_pages[2 * PGSIZE] __attribute__((aligned(PGSIZE)));
    virtq_desc_t *tx_desc;      // TX descriptors
    virtq_avail_t *tx_avail;    // TX avail ring
    virtq_used_t *tx_used;      // TX used ring
    uint16_t tx_free_idx;
    uint16_t tx_used_idx;

    uint8_t rx_buffers[NET_QUEUE_SIZE][ETH_FRAME_SIZE] __attribute__((aligned(16)));
    uint8_t tx_buffers[NET_QUEUE_SIZE][ETH_FRAME_SIZE] __attribute__((aligned(16)));
} virtio_net_t;

static virtio_net_t vnet;
#define VIRTIO_NET_F_MAC    5  // bit 5
#define VIRTIO_NET_CONFIG_MAC_OFFSET  0x0   // The first field of the config region is MAC
#define VIRTIO_MMIO_CONFIG  0x100  // Config space offset

// Define these constants according to your platform
#define NET_QUEUE_SIZE  8
#define ETH_FRAME_SIZE  1514
#define PGSIZE  4096

// QEMU RISC-V virtio-mmio base register, according to your linker settings
#define VIRTIO_MMIO_BASE   0x10008000UL
#define R_NET(offset)  ((volatile uint32_t *)(VIRTIO_MMIO_BASE + (offset)))

// legacy mmio register offset
#define VIRTIO_MMIO_MAGIC_VALUE      0x000
#define VIRTIO_MMIO_VERSION         0x004
#define VIRTIO_MMIO_DEVICE_ID       0x008
#define VIRTIO_MMIO_VENDOR_ID       0x00c
#define VIRTIO_MMIO_DEVICE_FEATURES 0x010
#define VIRTIO_MMIO_DRIVER_FEATURES 0x020
#define VIRTIO_MMIO_GUEST_PAGE_SIZE 0x028
#define VIRTIO_MMIO_QUEUE_SEL       0x030
#define VIRTIO_MMIO_QUEUE_NUM_MAX   0x034
#define VIRTIO_MMIO_QUEUE_NUM       0x038
#define VIRTIO_MMIO_QUEUE_ALIGN     0x03c
#define VIRTIO_MMIO_QUEUE_PFN       0x040
#define VIRTIO_MMIO_QUEUE_NOTIFY    0x050
#define VIRTIO_MMIO_STATUS          0x070

// Status bits
#define VIRTIO_CONFIG_S_ACKNOWLEDGE (1 << 0)
#define VIRTIO_CONFIG_S_DRIVER      (1 << 1)
#define VIRTIO_CONFIG_S_DRIVER_OK   (1 << 2)
#define VIRTIO_CONFIG_S_FEATURES_OK (1 << 3)
#define VIRTIO_CONFIG_S_FAILED      (1 << 7)

// --- Your queue, desc, avail, used structures and global buffer ----
// According to your previous definitions

static inline uintptr_t virt_to_phys(const void *addr) {
    return (uintptr_t)addr;
}
struct netif vnet_netif;

static int net_init = 0;
// netif initialization callback
err_t virtio_netif_init(struct netif *netif)
{
    uint8_t mac[6];
    volatile uint8_t *cfg_base = (volatile uint8_t *)(VIRTIO_MMIO_BASE + VIRTIO_MMIO_CONFIG);
    for (int i = 0; i < 6; ++i)
        mac[i] = cfg_base[i];

    netif->linkoutput = virtio_netif_linkoutput;
    netif->output = etharp_output;
    netif->hwaddr_len = 6;
    memcpy(netif->hwaddr, mac, 6);
    netif->mtu = 1500;
    netif->flags = NETIF_FLAG_BROADCAST | NETIF_FLAG_ETHARP | NETIF_FLAG_LINK_UP;
    return ERR_OK;
}

void virtio_net_input(uint8_t *eth_frame, uint32_t len)
{
    struct pbuf *p = pbuf_alloc(PBUF_RAW, len, PBUF_POOL);
    if (!p) return;
    pbuf_take(p, eth_frame, len);

    if (vnet_netif.input(p, &vnet_netif) != ERR_OK)
        pbuf_free(p);
}

void virtio_net_rx_loop2(void)
{
    if(net_init== 1){
        // while (1) {
        virtio_net_tx_recycle();

        uint16_t cur_used_idx = vnet.used->idx;
        while (vnet.used_idx != cur_used_idx) {
            uint16_t ring_idx = vnet.used_idx % NET_QUEUE_SIZE;
            uint16_t desc_idx = vnet.used->ring[ring_idx].id;
            uint32_t len = vnet.used->ring[ring_idx].len;
            uint8_t *buf = vnet.rx_buffers[desc_idx];
            uint8_t *eth_frame = buf + 10;  // virtio header

            // Pass the whole packet to lwIP
            virtio_net_input(eth_frame, len - 10);

            // Refill RX buffer
            vnet.avail->ring[vnet.avail->idx % NET_QUEUE_SIZE] = desc_idx;
            asm volatile("fence w, w" ::: "memory");
            vnet.avail->idx++;
            vnet.used_idx++;
        }
        // If you use polling, you can add a small delay or sys_check_timeouts();
        sys_check_timeouts(); // lwIP timeout mechanism (necessary)
    }
}

static err_t http_recv(void *arg, struct tcp_pcb *pcb, struct pbuf *p, err_t err)
{
    if (p == NULL) {
        tcp_close(pcb);
        return ERR_OK;
    }

    // Simple parsing of the first line GET path
    char *req = (char *)p->payload;
    if (strstr(req, "GET /hello ") == req) {
        // Return HTTP/1.1 + JSON
        const char *html = "<html><body><h1>Hello World!</h1></body></html>";
        const int html_len = 46; // Please check this manually or use strlen(html)
        const char *resp_head =
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            "Content-Length: 46\r\n"
            "Connection: close\r\n"
            "\r\n";

        char resp[256];
        int pos = 0;

        // Copy HTTP header
        for (int i = 0; resp_head[i]; ++i)
            resp[pos++] = resp_head[i];
        // Copy HTML content
        for (int i = 0; html[i]; ++i)
            resp[pos++] = html[i];
        resp[pos] = '\0'; // Not necessary for HTTP, but useful for debug print

        tcp_write(pcb, resp, strlen(resp), TCP_WRITE_FLAG_COPY);
        tcp_output(pcb);
    } else {
        // Other paths return 404
        const char *resp =
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 9\r\n"
            "Connection: close\r\n"
            "\r\n"
            "Not found";
        tcp_write(pcb, resp, strlen(resp), TCP_WRITE_FLAG_COPY);
        tcp_output(pcb);
    }

    tcp_recved(pcb, p->tot_len);
    pbuf_free(p);
    tcp_close(pcb); // Close after processing (short connection)
    return ERR_OK;
}

static err_t http_accept(void *arg, struct tcp_pcb *newpcb, err_t err)
{
    tcp_recv(newpcb, http_recv);
    return ERR_OK;
}

void simple_http_server_raw(void)
{
    struct tcp_pcb *pcb = tcp_new();
    if (!pcb) return;
    tcp_bind(pcb, IP_ADDR_ANY, 80);
    pcb = tcp_listen(pcb);
    tcp_accept(pcb, http_accept);
}

void virtio_net_init() {
    uint32_t status = 0;
    uint32_t magic = *(R_NET(VIRTIO_MMIO_MAGIC_VALUE));
    uint32_t version = *(R_NET(VIRTIO_MMIO_VERSION));
    uint32_t device_id = *(R_NET(VIRTIO_MMIO_DEVICE_ID));
    uint32_t vendor_id = *(R_NET(VIRTIO_MMIO_VENDOR_ID));

    lib_printf("[NET] Magic: 0x%x\n", magic);
    lib_printf("[NET] Version: %d\n", version);
    lib_printf("[NET] Device ID: %d\n", device_id);
    lib_printf("[NET] Vendor ID: 0x%x\n", vendor_id);

    if (magic != 0x74726976 || version != 1 || device_id != 1 || vendor_id != 0x554d4551) {
        panic("[NET] virtio-net legacy device not found or incompatible");
    }

    // 1. Reset
    *(R_NET(VIRTIO_MMIO_STATUS)) = 0;
    status = 0;

    // 2. Acknowledge
    status |= VIRTIO_CONFIG_S_ACKNOWLEDGE;
    *(R_NET(VIRTIO_MMIO_STATUS)) = status;

    // 3. Driver
    status |= VIRTIO_CONFIG_S_DRIVER;
    *(R_NET(VIRTIO_MMIO_STATUS)) = status;

    // 4. Feature negotiation (only use low 32 bits)
    uint32_t features = *(R_NET(VIRTIO_MMIO_DEVICE_FEATURES));
    uint32_t supported_features = 0; // No extra features supported
    features &= supported_features;
    *(R_NET(VIRTIO_MMIO_DRIVER_FEATURES)) = features;

    // 5. Set guest page size
    *(R_NET(VIRTIO_MMIO_GUEST_PAGE_SIZE)) = PGSIZE;

    // 6. Initialize RX queue (queue 0)
    *(R_NET(VIRTIO_MMIO_QUEUE_SEL)) = 0;
    uint32_t maxq = *(R_NET(VIRTIO_MMIO_QUEUE_NUM_MAX));
    if (maxq == 0 || maxq < NET_QUEUE_SIZE) {
        panic("[NET] queue too small");
    }
    *(R_NET(VIRTIO_MMIO_QUEUE_NUM)) = NET_QUEUE_SIZE;

    memset(vnet.pages, 0, sizeof(vnet.pages));
    vnet.desc = (virtq_desc_t *)vnet.pages;
    vnet.avail = (virtq_avail_t *)(vnet.pages + NET_QUEUE_SIZE * sizeof(virtq_desc_t));
    vnet.used = (virtq_used_t *)(vnet.pages + PGSIZE);
    vnet.used_idx = 0;

    for (int i = 0; i < NET_QUEUE_SIZE; i++) {
        vnet.desc[i].addr = virt_to_phys(&vnet.rx_buffers[i]);
        vnet.desc[i].len = ETH_FRAME_SIZE;
        vnet.desc[i].flags = VRING_DESC_F_WRITE;
        vnet.avail->ring[i] = i;
    }
    vnet.avail->idx = NET_QUEUE_SIZE;

    uintptr_t pfn_rx = virt_to_phys(vnet.pages) / PGSIZE;
    *(R_NET(VIRTIO_MMIO_QUEUE_PFN)) = pfn_rx;
    *(R_NET(VIRTIO_MMIO_QUEUE_READY)) = 1;

    lib_printf("desc @ VA:%p PA:0x%lx\n", vnet.desc, virt_to_phys(vnet.desc));
    lib_printf("avail @ VA:%p PA:0x%lx\n", vnet.avail, virt_to_phys(vnet.avail));
    lib_printf("used @ VA:%p PA:0x%lx\n", vnet.used, virt_to_phys(vnet.used));
    for (int i=0; i<NET_QUEUE_SIZE; i++) {
        lib_printf("desc[%d] buf VA:%p PA:0x%lx\n", i, &vnet.rx_buffers[i], virt_to_phys(&vnet.rx_buffers[i]));
    }

    // 7. Initialize TX queue (queue 1)
    static char tx_pages[2 * PGSIZE] __attribute__((aligned(PGSIZE)));
    memset(tx_pages, 0, sizeof(tx_pages));
    vnet.tx_desc = (virtq_desc_t *)tx_pages;
    vnet.tx_avail = (virtq_avail_t *)(tx_pages + NET_QUEUE_SIZE * sizeof(virtq_desc_t));
    vnet.tx_used = (virtq_used_t *)(tx_pages + PGSIZE);
    vnet.tx_free_idx = 0;

    for (int i = 0; i < NET_QUEUE_SIZE; i++) {
        vnet.tx_desc[i].addr = virt_to_phys(&vnet.tx_buffers[i]);
        vnet.tx_desc[i].len = 0;
        vnet.tx_desc[i].flags = 0;
    }
    vnet.tx_avail->idx = 0;

    *(R_NET(VIRTIO_MMIO_QUEUE_SEL)) = 1;
    *(R_NET(VIRTIO_MMIO_QUEUE_NUM)) = NET_QUEUE_SIZE;

    uintptr_t pfn_tx = virt_to_phys(tx_pages) / PGSIZE;
    *(R_NET(VIRTIO_MMIO_QUEUE_PFN)) = pfn_tx;
    *(R_NET(VIRTIO_MMIO_QUEUE_READY)) = 1;

    // 8. Driver OK
    status |= VIRTIO_CONFIG_S_DRIVER_OK;
    *(R_NET(VIRTIO_MMIO_STATUS)) = status;

    uint8_t mac[6];
    volatile uint8_t *cfg_base = (volatile uint8_t *)(VIRTIO_MMIO_BASE + VIRTIO_MMIO_CONFIG);
    for (int i = 0; i < 6; ++i)
        mac[i] = cfg_base[i];
    lib_printf("[NET] Device MAC: %x:%x:%x:%x:%x:%x\n",
        mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);

    lib_printf("pages VA: %p, PA: 0x%lx\n", vnet.pages, virt_to_phys(vnet.pages));
    for (int i=0; i<NET_QUEUE_SIZE; ++i)
        lib_printf("desc[%d] buf VA: %p, PA: 0x%lx\n", i, &vnet.rx_buffers[i], virt_to_phys(&vnet.rx_buffers[i]));

    // virtio_net_rx_loop();
    lwip_init();
    // 3. Register lwIP netif
    ip4_addr_t ipaddr, netmask, gw;
    IP4_ADDR(&ipaddr, 192,168,123,1);
    IP4_ADDR(&netmask, 255,255,255,0);
    IP4_ADDR(&gw, 192,168,123,1);

    netif_add(&vnet_netif, &ipaddr, &netmask, &gw, NULL, virtio_netif_init, ethernet_input);
    netif_set_default(&vnet_netif);
    netif_set_up(&vnet_netif);
    virtio_net_tx_init_free_list();
    // virtio_net_rx_loop2();
    simple_http_server_raw();
    net_init = 1 ;
    // It is recommended to run RX loop or call sys_check_timeouts() regularly here
    // while (1) {
    //       virtio_net_rx_loop2();    // RX event loop, do not omit!
    //     sys_check_timeouts();     // TCP timeout/retransmit
    // }
    // virtio_net_rx_loop();
}

void print_packet(uint8_t *buf, uint32_t len) {
    lib_printf("[NET] Packet len=%d\n", len);
    for (uint32_t i=0; i<len && i<64; i++) {
        lib_printf("%x ", buf[i]);
        if ((i+1)%16==0) lib_printf("\n");
    }
    lib_printf("\n");
}
void print_arp_reply_packet(uint8_t *tx_eth_frame) {
    lib_printf("ARP Reply Packet Content:\n");

    lib_printf("Dst MAC: ");
    for (int i = 0; i < 6; i++) {
        lib_printf("%x ", tx_eth_frame[i]);
    }
    lib_printf("\n");

    lib_printf("Src MAC: ");
    for (int i = 6; i < 12; i++) {
        lib_printf("%x ", tx_eth_frame[i]);
    }
    lib_printf("\n");

    lib_printf("EtherType: %x %x\n", tx_eth_frame[12], tx_eth_frame[13]);

    lib_printf("Hardware Type: %x %x\n", tx_eth_frame[14], tx_eth_frame[15]);
    lib_printf("Protocol Type: %x %x\n", tx_eth_frame[16], tx_eth_frame[17]);
    lib_printf("Hardware Size: %x\n", tx_eth_frame[18]);
    lib_printf("Protocol Size: %x\n", tx_eth_frame[19]);

    lib_printf("Opcode: %x %x\n", tx_eth_frame[20], tx_eth_frame[21]);

    lib_printf("Sender MAC: ");
    for (int i = 22; i < 28; i++) {
        lib_printf("%x ", tx_eth_frame[i]);
    }
    lib_printf("\n");

    lib_printf("Sender IP: ");
    for (int i = 28; i < 32; i++) {
        lib_printf("%d.", tx_eth_frame[i]);
    }
    lib_printf("\b \n");

    lib_printf("Target MAC: ");
    for (int i = 32; i < 38; i++) {
        lib_printf("%x ", tx_eth_frame[i]);
    }
    lib_printf("\n");

    lib_printf("Target IP: ");
    for (int i = 38; i < 42; i++) {
        lib_printf("%d.", tx_eth_frame[i]);
    }
    lib_printf("\b \n");
}

// Example ICMP checksum calculation function
uint16_t icmp_checksum(uint8_t *data, int len) {
    uint32_t sum = 0;
    for (int i = 0; i < len; i += 2) {
        uint16_t word = data[i] << 8;
        if (i + 1 < len)
            word |= data[i + 1];
        else
            word |= 0;
        sum += word;
    }
    // Carry wrap-around
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }
    return (uint16_t)(~sum);
}

static uint16_t tx_free_list[NET_QUEUE_SIZE];
static uint16_t tx_free_head = 0, tx_free_tail = 0;
void virtio_net_tx_init_free_list(void) {
    for (int i = 0; i < NET_QUEUE_SIZE; i++) {
        tx_free_list[i] = i;
    }
    tx_free_head = 0;
    tx_free_tail = NET_QUEUE_SIZE;
}

void virtio_net_tx_recycle(void) {
    while (vnet.tx_used_idx != vnet.tx_used->idx) {
        uint16_t used_ring_idx = vnet.tx_used_idx % NET_QUEUE_SIZE;
        uint16_t desc_idx = vnet.tx_used->ring[used_ring_idx].id;

        // Return to free_list
        tx_free_list[tx_free_tail % NET_QUEUE_SIZE] = desc_idx;
        tx_free_tail = (tx_free_tail + 1) % (2 * NET_QUEUE_SIZE); // Prevent overflow

        lib_printf("[NET] Recycle TX descriptor %d (head=%d tail=%d)\n", desc_idx, tx_free_head, tx_free_tail);
        vnet.tx_used_idx++;
    }
}

err_t virtio_netif_linkoutput(struct netif *netif, struct pbuf *p)
{
    if (tx_free_head == tx_free_tail) {
        // No available TX desc
        return ERR_MEM;
    }

    uint16_t tx_idx = tx_free_list[tx_free_head % NET_QUEUE_SIZE];
    tx_free_head = (tx_free_head + 1) % (2 * NET_QUEUE_SIZE); // Prevent overflow

    uint8_t *tx_buf = vnet.tx_buffers[tx_idx];
    memset(tx_buf, 0, 10);
    pbuf_copy_partial(p, tx_buf + 10, p->tot_len, 0);

    vnet.tx_desc[tx_idx].addr = virt_to_phys(tx_buf);
    vnet.tx_desc[tx_idx].len = p->tot_len + 10;
    vnet.tx_desc[tx_idx].flags = 0;

    vnet.tx_avail->ring[vnet.tx_avail->idx % NET_QUEUE_SIZE] = tx_idx;
    asm volatile("fence w, w" ::: "memory");
    vnet.tx_avail->idx++;

    *(R_NET(VIRTIO_MMIO_QUEUE_NOTIFY)) = 1;

    return ERR_OK;
}

// Interrupt handler for virtio-net
void virtio_net_interrupt_handler(void) {
    // Read ISR to clear interrupt (legacy virtio-mmio)
    // uint32_t isr = *(R_NET(VIRTIO_MMIO_ISR));
    // (void)isr; // You can check bits to determine RX/TX
    // Process new packets in the used ring
    // virtio_net_rx_loop();
    virtio_net_rx_loop2(); // Handler used for polling
    // Replenish descriptor, update avail, notify device if needed
}
```

當然這邊virtio_net_rx_loop2 這邊有看到兩個版本，virtio_net_rx_loop這部分是還沒引入 lwip，你要自己實做arp 和 icmp 協議假設你要全部自己來的話
![image](https://hackmd.io/_uploads/HyOXJGTvxx.png)
也是沒問題的，這部分要叫chatgpt debug 最好的方式就是把封包全印，這樣chatgpt 才能取得更好的context 去推理
```c
// Interrupt handler for virtio-net
void virtio_net_interrupt_handler(void) {
    // Read ISR to clear interrupt (legacy virtio-mmio)
    // uint32_t isr = *(R_NET(VIRTIO_MMIO_ISR));
    // (void)isr; // You can check bits to determine RX/TX
    // Process new packets in the used ring
    // virtio_net_rx_loop();
    virtio_net_rx_loop(); // Handler used for polling
    // Replenish descriptor, update avail, notify device if needed
}
```
```c
// Interrupt handler for virtio-net
static uint16_t tx_used_idx = 0;  
static uint16_t tx_free_idx = 0; 

// The main RX event loop for polling mode
void virtio_net_rx_loop() {
    uint8_t my_mac[6] = {0x52,0x54,0x00,0x12,0x34,0x56};
    uint8_t my_ip[4] = {192,168,123,1};

    while (1) {
        virtio_net_tx_recycle();  // Recycle completed TX descriptors

        uint16_t cur_used_idx = vnet.used->idx;
        while (vnet.used_idx != cur_used_idx) {
            uint16_t ring_idx = vnet.used_idx % NET_QUEUE_SIZE;
            uint16_t desc_idx = vnet.used->ring[ring_idx].id;
            uint32_t len = vnet.used->ring[ring_idx].len;
            uint8_t *buf = vnet.rx_buffers[desc_idx];
            uint8_t *eth_frame = buf + 10;  // Skip virtio-net header

            // Print the packet content (for debugging)
            print_packet(eth_frame, len - 10);

            // ----- ARP Request check and reply -----
            if (len >= 42 &&
                eth_frame[12] == 0x08 && eth_frame[13] == 0x06 &&      // EtherType ARP
                eth_frame[20] == 0x00 && eth_frame[21] == 0x01 &&      // Opcode request
                eth_frame[38] == my_ip[0] && eth_frame[39] == my_ip[1] &&
                eth_frame[40] == my_ip[2] && eth_frame[41] == my_ip[3]) { // Target IP matches

                uint16_t next_free = (tx_free_idx + 1) % NET_QUEUE_SIZE;
                if (next_free == tx_used_idx) {
                    // No available descriptor, refill RX buffer and drop packet
                    vnet.avail->ring[vnet.avail->idx % NET_QUEUE_SIZE] = desc_idx;
                    asm volatile("fence w, w" ::: "memory");
                    vnet.avail->idx++;
                    vnet.used_idx++;
                    continue;
                }

                uint16_t tx_idx = tx_free_idx;
                uint8_t *tx_buf = vnet.tx_buffers[tx_idx];
                uint8_t *tx_eth_frame = tx_buf + 10;

                // Copy packet and modify as ARP Reply
                memcpy(tx_eth_frame, eth_frame, len - 10);

                // Modify ARP Reply fields
                for (int i = 0; i < 6; i++) tx_eth_frame[i] = eth_frame[6 + i];    // dst MAC = original src MAC
                for (int i = 0; i < 6; i++) tx_eth_frame[6 + i] = my_mac[i];      // src MAC = our MAC
                tx_eth_frame[20] = 0x00; tx_eth_frame[21] = 0x02;                 // opcode = reply
                for (int i = 0; i < 6; i++) tx_eth_frame[22 + i] = my_mac[i];     // sender MAC = us
                for (int i = 0; i < 4; i++) tx_eth_frame[28 + i] = my_ip[i];      // sender IP = us
                for (int i = 0; i < 6; i++) tx_eth_frame[32 + i] = eth_frame[6 + i];  // target MAC = original sender MAC
                for (int i = 0; i < 4; i++) tx_eth_frame[38 + i] = eth_frame[28 + i]; // target IP = original sender IP

                print_arp_reply_packet(tx_eth_frame);

                // Set TX descriptor
                vnet.tx_desc[tx_idx].addr = virt_to_phys(tx_buf);
                vnet.tx_desc[tx_idx].len = 52;
                vnet.tx_desc[tx_idx].flags = 0;

                // Place into TX avail ring and notify device
                vnet.tx_avail->ring[vnet.tx_avail->idx % NET_QUEUE_SIZE] = tx_idx;
                asm volatile("fence w, w" ::: "memory");
                vnet.tx_avail->idx++;

                *(R_NET(VIRTIO_MMIO_QUEUE_NOTIFY)) = 1;

                tx_free_idx = next_free;

                // Refill RX buffer
                vnet.avail->ring[vnet.avail->idx % NET_QUEUE_SIZE] = desc_idx;
                asm volatile("fence w, w" ::: "memory");
                vnet.avail->idx++;

                lib_puts("[NET] Sent ARP Reply via TX queue!\n");
                vnet.used_idx++;
                continue;
            }

            // ----- ICMP Echo Request (Ping) check and reply -----
            uint8_t ip_header_len = (eth_frame[14] & 0x0f) * 4;
            uint8_t icmp_type = eth_frame[14 + ip_header_len];

            lib_printf("Check EtherType: %x  %x \n", eth_frame[12], eth_frame[13]);
            lib_printf("Check Protocol: %x \n", eth_frame[23]);
            lib_printf("Check ICMP Type: %x \n", icmp_type);
            lib_printf("Check Target IP: %d.%d.%d.%d\n", eth_frame[14 + 16], eth_frame[14 + 17], eth_frame[14 + 18], eth_frame[14 + 19]);

            if (len >= 42 &&
                eth_frame[12] == 0x08 && eth_frame[13] == 0x00 &&              // EtherType IPv4
                eth_frame[23] == 0x01 &&                                       // Protocol ICMP
                icmp_type == 0x08 &&                                           // ICMP Echo Request
                eth_frame[14 + 16] == my_ip[0] && eth_frame[14 + 17] == my_ip[1] &&
                eth_frame[14 + 18] == my_ip[2] && eth_frame[14 + 19] == my_ip[3]) { // Target IP matches

                uint16_t next_free = (tx_free_idx + 1) % NET_QUEUE_SIZE;
                if (next_free == tx_used_idx) {
                    // No available descriptor, drop packet
                    vnet.avail->ring[vnet.avail->idx % NET_QUEUE_SIZE] = desc_idx;
                    asm volatile("fence w, w" ::: "memory");
                    vnet.avail->idx++;
                    vnet.used_idx++;
                    continue;
                }

                uint16_t tx_idx = tx_free_idx;
                uint8_t *tx_buf = vnet.tx_buffers[tx_idx];
                uint8_t *tx_eth_frame = tx_buf + 10;

                memcpy(tx_eth_frame, eth_frame, len - 10);

                // Modify Ethernet header (src/dst MAC)
                for (int i = 0; i < 6; i++) tx_eth_frame[i] = eth_frame[6 + i];      // dst MAC = original src MAC
                for (int i = 0; i < 6; i++) tx_eth_frame[6 + i] = my_mac[i];        // src MAC = our MAC

                // IP header offset 14, swap src/dst IP
                for (int i = 0; i < 4; i++) {
                    tx_eth_frame[14 + 16 + i] = eth_frame[14 + 12 + i];       // dst IP = original src IP
                    tx_eth_frame[14 + 12 + i] = my_ip[i];                     // src IP = our IP
                }

                // ICMP header: offset 14+20
                tx_eth_frame[14 + 20] = 0x00;   // ICMP type = Echo Reply
                tx_eth_frame[14 + 22] = 0;
                tx_eth_frame[14 + 23] = 0;
                uint16_t icmp_len = len - 10 - 14 - 20;
                uint16_t checksum = icmp_checksum(tx_eth_frame + 14 + 20, icmp_len);
                tx_eth_frame[14 + 22] = (checksum >> 8) & 0xFF;
                tx_eth_frame[14 + 23] = checksum & 0xFF;

                vnet.tx_desc[tx_idx].addr = virt_to_phys(tx_buf);
                vnet.tx_desc[tx_idx].len = len ;
                vnet.tx_desc[tx_idx].flags = 0;

                vnet.tx_avail->ring[vnet.tx_avail->idx % NET_QUEUE_SIZE] = tx_idx;
                asm volatile("fence w, w" ::: "memory");
                vnet.tx_avail->idx++;

                *(R_NET(VIRTIO_MMIO_QUEUE_NOTIFY)) = 1;

                tx_free_idx = next_free;

                vnet.avail->ring[vnet.avail->idx % NET_QUEUE_SIZE] = desc_idx;
                asm volatile("fence w, w" ::: "memory");
                vnet.avail->idx++;

                lib_puts("[NET] Sent ICMP Echo Reply via TX queue!\n");
                vnet.used_idx++;
                continue;
            }

            // Not ARP or ICMP Echo Request, just recycle RX buffer
            vnet.avail->ring[vnet.avail->idx % NET_QUEUE_SIZE] = desc_idx;
            asm volatile("fence w, w" ::: "memory");
            vnet.avail->idx++;
            vnet.used_idx++;
        }
    }
}

```

