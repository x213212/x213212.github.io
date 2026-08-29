---
title: "linux hook record"
date: "2023-01-15T17:49:00.002+08:00"
updated: "2023-01-15T17:49:55.746+08:00"
permalink: "/2023/01/linux-hook-record.html"
original_url: "https://x8795278.blogspot.com/2023/01/linux-hook-record.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-4579036340097735513"
tags: ["linux hook"]
layout: post
---

![](https://i.imgur.com/eC6Msia.png)

# linux hook
之前有分享 linux hook的方式，包括ld_preload,目前有個情況需要額外override 原本的某個function在linux 環境，這邊記錄一下可行方案

# lief
https://github.com/lief-project/LIEF
```bash
pip install lief
```
如果採用直接修改elf 是否有可能直接hook 原來的function
直接看官方文檔
https://lief-project.github.io/doc/latest/tutorials/04_elf_hooking.html
https://lief-project.github.io/doc/latest/tutorials/05_elf_infect_plt_got.html
我們直接對比較重要的這兩個範例紀錄一下
https://github.com/lief-project/tutorials
作者的github project連結

# 04_elf_hooking
## do_math.c
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main(int argc, char **argv) {
  if (argc != 2) {
    printf("Usage: %s <a> \n", argv[0]);
    exit(-1);
  }

  int a = atoi(argv[1]);
  printf("cos(%d) = %f\n", a, cos(a));
  return 0;
}

```
## hook.c
```c
double hook(double x) {
  return x + 1;
  //return (double)((int)x + 3);
}
```
## insert_hook.py
```
#!/usr/bin/env python3

# Description
# -----------
# Hook the 'cos' function from the standard math library (libm)
import lief

libm = lief.parse("/usr/lib/libm.so.6")
hook = lief.parse("hook")

cos_symbol  = libm.get_symbol("cos")
hook_symbol = hook.get_symbol("hook")

code_segment = hook.segment_from_virtual_address(hook_symbol.value)
segment_added = libm.add(code_segment)

print("Hook inserted at VA: 0x{:06x}".format(segment_added.virtual_address))

# Offset of the function 'hook' within the CODE segment
hook_offset = hook_symbol.value - code_segment.virtual_address
new_addr    = segment_added.virtual_address + hook_offset
print(f"Change {cos_symbol.name}!{cos_symbol.value:x} -> {cos_symbol.name}!{new_addr:x}")
cos_symbol.value = new_addr
libm.write("libm.so.6")
```
到這邊do_math 所加載的 數學函式庫 cos 已經被替換成hook function

# 05_elf_infect_plt_got.html
這一個範例來說
## crackme.c
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Damn_YoU_Got_The_Flag
char password[] = "\x18\x3d\x31\x32\x03\x05\x33\x09\x03\x1b\x33\x28\x03\x08\x34\x39\x03\x1a\x30\x3d\x3b";

inline int check(char* input);

int check(char* input) {
  for (int i = 0; i < sizeof(password) - 1; ++i) {
    password[i] ^= 0x5c;
  }
  return memcmp(password, input, sizeof(password) - 1);
}

int main(int argc, char **argv) {
  if (argc != 2) {
    printf("Usage: %s <password>\n", argv[0]);
    return EXIT_FAILURE;
  }

  if (strlen(argv[1]) == (sizeof(password) - 1) && check(argv[1]) == 0) {
    puts("You got it !!");
    return EXIT_SUCCESS;
  }

  puts("Wrong");
  return EXIT_FAILURE;

}
```
## hook.c
```c
#include "arch/x86_64/syscall.c"
#define stdout 1

int my_memcmp(const void* lhs, const void* rhs, int n) {
  const char msg[] = "Hook add\n";
  _write(stdout, msg, sizeof(msg));
  _write(stdout, (const char*)lhs, n);
  _write(stdout, "\n", 2);
  _write(stdout, (const char*)rhs, n);
  _write(stdout, "\n", 2);
  return 0;
}
```

## hook_pltgot.py
```python
# ./crackme.hooked XXXXXXXXXXXXXXXXXXXXX
# Hook add
# Damn_YoU_Got_The_Flag
# XXXXXXXXXXXXXXXXXXXXX
# You got it !!
import lief

crackme = lief.parse("crackme.bin")
hook    = lief.parse("hook")

segment_added  = crackme.add(hook.segments[0])

my_memcmp      = hook.get_symbol("my_memcmp")
my_memcmp_addr = segment_added.virtual_address + my_memcmp.value

crackme.patch_pltgot('memcmp', my_memcmp_addr)

# Remove bind now if present
if lief.ELF.DYNAMIC_TAGS.FLAGS in crackme:
    flags = crackme[lief.ELF.DYNAMIC_TAGS.FLAGS]
    flags.remove(lief.ELF.DYNAMIC_FLAGS.BIND_NOW)

if lief.ELF.DYNAMIC_TAGS.FLAGS_1 in crackme:
    flags = crackme[lief.ELF.DYNAMIC_TAGS.FLAGS_1]
    flags.remove(lief.ELF.DYNAMIC_FLAGS_1.NOW)

# Remove RELRO
if lief.ELF.SEGMENT_TYPES.GNU_RELRO in crackme:
    crackme[lief.ELF.SEGMENT_TYPES.GNU_RELRO].type = lief.ELF.SEGMENT_TYPES.NULL

crackme.write("crackme.hooked")
```
直接把memcmp 轉為 my_memcmp 間接orverride掉function ,試了幾次好像沒辦法替換掉libc 的 function

# ld_preload
```
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <stdio.h>
#include <dlfcn.h>

static int (*orig_printf)(const char *format, ...) = NULL;

int printf(const char *format, ...)
{
 if (orig_printf == NULL)
 {
  orig_printf = (int (*)(const char *format, ...))dlsym(RTLD_NEXT, "printf");
 }
orig_printf("within my own printf\n");
 // TODO: print desired message from caller. 
 return orig_printf("within my own printf\n");
}
```
```bash
gcc -Wall -fPIC -shared -o PrintfHank.so PrintfHank.c -ldl 
export LD_PRELOAD=./PrintfHank.so
```
![](https://i.imgur.com/QhTo86o.png)
大概整理了這些方式，主要要針對沒辦法修改的程式碼進行額外處理
算是重新封裝printf ,讓輸出log可以濾掉
必須注意
https://stackoverflow.com/questions/1576689/problems-on-injecting-into-printf-using-ld-preload-method
有時候假設printf沒有帶參數可能會被優化成puts
printf
```
printf("rko%d\n",123);
```
puts
```
printf("rko\n",123);
```

# example

```c
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <stdio.h>
#include <dlfcn.h>
#include <stdlib.h>
#include <stdarg.h>
static int (*orig_printf)(const char *format, ...) = NULL;
static int (*orig_puts)(const char *str) = NULL;
int puts(const char *str)
{
    if (orig_puts == NULL)
    {
        orig_puts = (int (*)(const char *str))dlsym(RTLD_NEXT, "puts");
    }    
    return orig_puts("within my own puts");
}
int printf(const char *format, ...)
{

  
    if (orig_printf == NULL)
    {
        orig_printf = (int (*)(const char *format, ...))dlsym(RTLD_NEXT, "printf");
    }

    va_list arg;
   int done;

   va_start (arg, format);
   done = vfprintf (stdout, format, arg);
   char *ch;
   ch =arg;
   orig_printf("%s\n",ch);
   va_end (arg);

   return orig_printf("within my own printf\n");
}
```
# ptrace
當然使用 ptrace 也可以
## override printf
```c
#include <stdio.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <sys/user.h>
#include <sys/reg.h>
#include <sys/syscall.h>
void hook_printf() {
    printf("printf has been intercepted!\n");
}

int main() {
    pid_t child = fork();
    if (child == 0) {
        ptrace(PTRACE_TRACEME, 0, 0, 0);
        execl("./a.out", "24", 0);
    }
    else {
        wait(NULL);
        long orig_eax;
        while (1) {
        struct user_regs_struct regs;
            ptrace(PTRACE_SYSCALL, child, 0, 0);
            wait(NULL);
            ptrace(PTRACE_GETREGS, child, NULL, &regs);
            orig_eax = ptrace(PTRACE_PEEKUSER, child, 8 * ORIG_RAX, NULL);
            if (orig_eax == __NR_write) {
                // change the return address to hook_printf
                hook_printf();
                // read the string from memory
                char *str = (char*)regs.rdi;
                char buffer[1024];
                for (int i = 0; i < regs.rdx; i++) {
                buffer[i] = ptrace(PTRACE_PEEKDATA, child, regs.rsi + i, NULL);
                }
                buffer[regs.rdx] = '\0';
                printf("printf2: %s\n", buffer);
            }
        }
    }
    return 0;
}

```
## no execute printf
```c
#include <stdio.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <sys/user.h>
#include <sys/reg.h>
#include <sys/syscall.h>
void hook_printf() {
    printf("printf has been intercepted!\n");
}

int main() {
    pid_t child = fork();
    if (child == 0) {
        ptrace(PTRACE_TRACEME, 0, 0, 0);
        execl("./a.out", "24", 0);
    }
    else {
        wait(NULL);
        long orig_eax;
        while (1) {
        struct user_regs_struct regs;
            ptrace(PTRACE_SYSCALL, child, 0, 0);
            wait(NULL);
            ptrace(PTRACE_GETREGS, child, NULL, &regs);
            orig_eax = ptrace(PTRACE_PEEKUSER, child, 8 * ORIG_RAX, NULL);
            if (orig_eax == __NR_write) {
                // change the return address to hook_printf
                hook_printf();
                regs.rax = -1;
                ptrace(PTRACE_SETREGS, child, NULL, &regs);
                printf("printf disabled\n");
                // read the string from memory
                // char *str = (char*)regs.rdi;
                // char buffer[1024];
                // for (int i = 0; i < regs.rdx; i++) {
                // buffer[i] = ptrace(PTRACE_PEEKDATA, child, regs.rsi + i, NULL);
                // }
                // buffer[regs.rdx] = '\0';
                // printf("printf: %s\n", buffer);

            }
        }
    }
    return 0;
}
```

## run exit
```c
#include <stdio.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <sys/user.h>
#include <sys/reg.h>
#include <sys/syscall.h>
void hook_printf() {
    printf("printf has been intercepted!\n");
}

int main() {
    pid_t child = fork();
    if (child == 0) {
        ptrace(PTRACE_TRACEME, 0, 0, 0);
        execl("./a.out", "24", 0);
    }
    else {
          int status;
        wait(NULL);
        long orig_eax;
        while (1) {
        struct user_regs_struct regs;
            ptrace(PTRACE_SYSCALL, child, 0, 0);
            // wait(NULL);
            if(wait(&status) == -1)
                break;
            if (WIFEXITED(status)) {
                ptrace(PTRACE_DETACH, child, 0, 0);
                break;
            }
            ptrace(PTRACE_GETREGS, child, NULL, &regs);
            orig_eax = ptrace(PTRACE_PEEKUSER, child, 8 * ORIG_RAX, NULL);
            if (orig_eax == __NR_write) {
                // change the return address to hook_printf
                hook_printf();
                // regs.rax = -1;
                // ptrace(PTRACE_SETREGS, child, NULL, &regs);
                // printf("printf disabled\n");
                // read the string from memory
                char *str = (char*)regs.rdi;
                char buffer[1024];
                for (int i = 0; i < regs.rdx; i++) {
                buffer[i] = ptrace(PTRACE_PEEKDATA, child, regs.rsi + i, NULL);
                }
                buffer[regs.rdx] = '\0';
                printf("printf: %s\n", buffer);
             
            }
        }
    }
    return 0;
}

```
# read arg
```
        execl("./a.out", "a.out","XXXXXXXXXX", 0);
```

![](https://i.imgur.com/nrOKWIp.png)

這樣印出來的後綴都有加上想要的字串了，其實glibc 跟之前介紹一樣有malloc hook 和 free hook,ebpf 也可以達成hook不
過需要重編linux kernel 開啟ebpf的模組，使用ld_preload 還是蠻方便的不過權限可能需要實際情況才能確定，
![](https://i.imgur.com/eC6Msia.png)

# 參考
https://axcheron.github.io/playing-with-ld_preload/

