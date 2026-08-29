---
title: "Load Binary to Shared Memory Using GDB"
date: "2024-08-21T02:20:00.001+08:00"
updated: "2024-08-21T02:20:07.805+08:00"
permalink: "/2024/08/load-binary-to-shared-memory-using-gdb.html"
original_url: "https://x8795278.blogspot.com/2024/08/load-binary-to-shared-memory-using-gdb.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5664026013586431044"
tags: ["gdb"]
layout: post
---

![](https://hackmd.io/_uploads/SkIynLGjR.png)

# Load Binary to Shared Memory Using GDB
最近在研究 gdbserver 順便驗證一些東西
應該說在 bare metal 情況下，gdb load 應該會把binary load 到記憶體位置，在riscv 看蠻多的但是在x86是否可以這樣模擬透過gdb的load 將 程式碼load 到指定位置

# create memory area
```c
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdio.h>

#define SHARED_MEM_SIZE 0x1000000  
#define SHARED_MEM_ADDR 0x60000000 

int main() {
    int shm_fd;
    void *ptr;

    shm_fd = shm_open("/my_shared_mem", O_CREAT | O_RDWR, 0666);
    if (shm_fd == -1) {
        perror("shm_open");
        return 1;
    }

    ftruncate(shm_fd, SHARED_MEM_SIZE);

    ptr = mmap((void*)SHARED_MEM_ADDR, SHARED_MEM_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_FIXED, shm_fd, 0);
    if (ptr == MAP_FAILED) {
        perror("mmap");
        return 1;
    }

    printf("Shared memory mapped at address %p\n", ptr);

    while (1) {
      
        sleep(1); 
    }

    close(shm_fd);
    return 0;
}
```

```bash
gcc -o allocate_memory allocate_memory.c -lrt
```

![image](https://hackmd.io/_uploads/BJjKi8fjA.png)

# simple_code.c
```c
void _start() {

    const char *msg = "Hello from GDB loaded memory!\n";
    while (*msg) {
        __asm__ volatile (
            "movq $1, %%rax;"      // system call (sys_write)
            "movq $1, %%rdi;"      // (stdout)
            "movq %0, %%rsi;"      // 
            "movq $1, %%rdx;"      // len (1 byte)
            "syscall;"             // call system call
            : : "r"(msg)
            : "rax", "rdi", "rsi", "rdx"
        );
        msg++;
    }

    while (1) {}
}
```

# simple_code.ld
```
MEMORY
{
    SHARED_MEM (rx) : ORIGIN = 0x60000000, LENGTH = 0x1000000
}

SECTIONS
{
    .text : {
        *(.text)
    } > SHARED_MEM

    .data : {
        *(.data)
    } > SHARED_MEM

    .bss : {
        *(.bss)
    } > SHARED_MEM
}
```
# compileile
```bash
gcc -g -nostartfiles  -T simple_code.ld -o simple_code.elf simple_code.c
```
# gdb server
```bash
gdbserver :1234 ./simple_code.elf
```
![image](https://hackmd.io/_uploads/B1evsUfjA.png)

# gdb
```bash
gdb simple_code.elf
target remote :1234
load
```
![image](https://hackmd.io/_uploads/ByBws8MiC.png)
![image](https://hackmd.io/_uploads/S112iIGs0.png)
這邊可以看到 elf 已經被 load 到指定位置
![image](https://hackmd.io/_uploads/HJYTjIMoA.png)
![image](https://hackmd.io/_uploads/B17RiLziC.png)
![image](https://hackmd.io/_uploads/rJMy2Izj0.png)
可以看到我們的 elf 已經被 load 到 shard memory 空間上並且成功執行，在嵌入式就是把程式放到某一個地方 再透過 pc直接指過去
![image](https://hackmd.io/_uploads/SkIynLGjR.png)

![image](https://hackmd.io/_uploads/ryFvpIGj0.png)

這邊要驗證到底是否有寫到記憶體裡面照理說假設我們的記憶體沒有釋放代表就可以不用load 直接指定
```bash
set $rip = 0x60000000
```
![image](https://hackmd.io/_uploads/rJvkC8GsR.png)
這邊看到就算不用load 就可以直接執行
![image](https://hackmd.io/_uploads/SyqeC8zo0.png)

