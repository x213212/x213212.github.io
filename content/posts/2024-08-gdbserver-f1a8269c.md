---
title: "大概分析 gdbserver 原理"
date: "2024-08-24T04:19:00.003+08:00"
updated: "2024-08-24T04:19:27.832+08:00"
permalink: "/2024/08/gdbserver.html"
original_url: "https://x8795278.blogspot.com/2024/08/gdbserver.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5229304703270662289"
tags: ["gdbserver"]
layout: post
---

![](https://hackmd.io/_uploads/SkIynLGjR.png)

# 大概分析 gdbserver 原理
這次來研究一下 gdbserver
https://github.com/bet4it/gdbserver.git
https://github.com/trixirt/deebe
簡單來說 gdbserver 工作原理就是透過ptrace 去控制 process 的動作
在main 可以看到
這邊會透過 get_request 來持續查看是否有封包傳入，也就是連接後等待gdb送指令過來

```c
void get_request()
{
  while (true)
  {
    read_packet();
    process_packet();
    write_flush();
  }
}
```
要解碼封包可以看這邊
https://sourceware.org/gdb/current/onlinedocs/gdb.html/Packets.html#Packets
也就是假設要在一個gdb 加上自己想要的功能的話，可能就要去異動這個部分，以這邊的例子是有os的情況下所以有ptrace可以用，在嵌入式可能要透過jtag 去讀寫register
```c
void process_packet()
{
  uint8_t *inbuf = inbuf_get();
  int inbuf_size = inbuf_end();
  uint8_t *packetend_ptr = (uint8_t *)memchr(inbuf, '#', inbuf_size);
  int packetend = packetend_ptr - inbuf;
  assert('$' == inbuf[0]);
  char request = inbuf[1];
  char *payload = (char *)&inbuf[2];
  inbuf[packetend] = '\0';

  uint8_t checksum = 0;
  uint8_t checksum_str[3];
  for (int i = 1; i < packetend; i++)
    checksum += inbuf[i];
  assert(checksum == (hex(inbuf[packetend + 1]) << 4 | hex(inbuf[packetend + 2])));

  switch (request)
  {
  case 'D':
    for (int i = 0, n = 0; i < THREAD_NUMBER && n < threads.len; i++)
      if (threads.t[i].tid)
        if (ptrace(PTRACE_DETACH, threads.t[i].tid, NULL, NULL) < 0)
          perror("ptrace()");
    exit(0);
  case 'g':
  {
    regs_struct regs;
    uint8_t regbuf[20];
    tmpbuf[0] = '\0';
    ptrace(PTRACE_GETREGS, threads.curr->tid, NULL, &regs);
    for (int i = 0; i < ARCH_REG_NUM; i++)
    {
      mem2hex((void *)(((size_t *)&regs) + regs_map[i].idx), regbuf, regs_map[i].size);
      regbuf[regs_map[i].size * 2] = '\0';
      strcat(tmpbuf, regbuf);
    }
    write_packet(tmpbuf);
    break;
  }
  case 'H':
    if ('g' == *payload++)
    {
      pid_t tid;
      char *dot = strchr(payload, '.');
      assert(dot);
      tid = strtol(dot, NULL, 16);
      if (tid > 0)
        set_curr_thread(tid);
    }
    write_packet("OK");
    break;
  case 'm':
  {
    size_t maddr, mlen, mdata;
    assert(sscanf(payload, "%zx,%zx", &maddr, &mlen) == 2);
    if (mlen * SZ * 2 > 0x20000)
    {
      puts("Buffer overflow!");
      exit(-1);
    }
    for (int i = 0; i < mlen; i += SZ)
    {
      errno = 0;
      mdata = ptrace(PTRACE_PEEKDATA, threads.curr->tid, maddr + i, NULL);
      if (errno)
      {
        sprintf(tmpbuf, "E%02x", errno);
        break;
      }
      mdata = restore_breakpoint(maddr, sizeof(size_t), mdata);
      mem2hex((void *)&mdata, tmpbuf + i * 2, (mlen - i >= SZ ? SZ : mlen - i));
    }
    tmpbuf[mlen * 2] = '\0';
    write_packet(tmpbuf);
    break;
  }
  case 'M':
  {
    size_t maddr, mlen, mdata;
    assert(sscanf(payload, "%zx,%zx", &maddr, &mlen) == 2);
    for (int i = 0; i < mlen; i += SZ)
    {
      if (mlen - i >= SZ)
        hex2mem(payload + i * 2, (void *)&mdata, SZ);
      else
      {
        mdata = ptrace(PTRACE_PEEKDATA, threads.curr->tid, maddr + i, NULL);
        hex2mem(payload + i * 2, (void *)&mdata, mlen - i);
      }
      ptrace(PTRACE_POKEDATA, threads.curr->tid, maddr + i, mdata);
    }
    write_packet("OK");
    break;
  }
  case 'p':
  {
    int i = strtol(payload, NULL, 16);
    if (i >= ARCH_REG_NUM && i != EXTRA_NUM)
    {
      write_packet("E01");
      break;
    }
    size_t regdata;
    if (i == EXTRA_NUM)
    {
      regdata = ptrace(PTRACE_PEEKUSER, threads.curr->tid, SZ * EXTRA_REG, NULL);
      mem2hex((void *)&regdata, tmpbuf, EXTRA_SIZE);
      tmpbuf[EXTRA_SIZE * 2] = '\0';
    }
    else
    {
      regdata = ptrace(PTRACE_PEEKUSER, threads.curr->tid, SZ * regs_map[i].idx, NULL);
      mem2hex((void *)&regdata, tmpbuf, regs_map[i].size);
      tmpbuf[regs_map[i].size * 2] = '\0';
    }
    write_packet(tmpbuf);
    break;
  }
  case 'P':
  {
    int i = strtol(payload, &payload, 16);
    assert('=' == *payload++);
    if (i >= ARCH_REG_NUM && i != EXTRA_NUM)
    {
      write_packet("E01");
      break;
    }
    size_t regdata = 0;
    hex2mem(payload, (void *)&regdata, SZ * 2);
    if (i == EXTRA_NUM)
      ptrace(PTRACE_POKEUSER, threads.curr->tid, SZ * EXTRA_REG, regdata);
    else
      ptrace(PTRACE_POKEUSER, threads.curr->tid, SZ * regs_map[i].idx, regdata);
    write_packet("OK");
    break;
  }
  case 'q':
    process_query(payload);
    break;
  case 'v':
    process_vpacket(payload);
    break;
  case 'X':
  {
    size_t maddr, mlen, mdata;
    int offset, new_len;
    assert(sscanf(payload, "%zx,%zx:%n", &maddr, &mlen, &offset) == 2);
    payload += offset;
    new_len = unescape(payload, (char *)packetend_ptr - payload);
    assert(new_len == mlen);
    for (int i = 0; i < mlen; i += SZ)
    {
      if (mlen - i >= SZ)
        memcpy((void *)&mdata, payload + i, SZ);
      else
      {
        mdata = ptrace(PTRACE_PEEKDATA, threads.curr->tid, maddr + i, NULL);
        memcpy((void *)&mdata, payload + i, mlen - i);
      }
      ptrace(PTRACE_POKEDATA, threads.curr->tid, maddr + i, mdata);
    }
    write_packet("OK");
    break;
  }
  case 'Z':
  {
    size_t type, addr, length;
    assert(sscanf(payload, "%zx,%zx,%zx", &type, &addr, &length) == 3);
    if (type == 0 && sizeof(break_instr))
    {
      bool ret = set_breakpoint(threads.curr->tid, addr, length);
      if (ret)
        write_packet("OK");
      else
        write_packet("E01");
    }
    else
      write_packet("");
    break;
  }
  case 'z':
  {
    size_t type, addr, length;
    assert(sscanf(payload, "%zx,%zx,%zx", &type, &addr, &length) == 3);
    if (type == 0)
    {
      bool ret = remove_breakpoint(threads.curr->tid, addr, length);
      if (ret)
        write_packet("OK");
      else
        write_packet("E01");
    }
    else
      write_packet("");
    break;
  }
  case '?':
    write_packet("S05");
    break;
  default:
    write_packet("");
  }

  inbuf_erase_head(packetend + 3);
}
```
```c
int main(int argc, char *argv[])
{
  pid_t pid;
  char **next_arg = &argv[1];
  char *arg_end, *target = NULL;
  int stat;

  if (*next_arg != NULL && strcmp(*next_arg, "--attach") == 0)
  {
    attach = true;
    next_arg++;
  }

  target = *next_arg;
  next_arg++;

  if (target == NULL || *next_arg == NULL)
  {
    printf("Usage : gdbserver 127.0.0.1:1234 a.out or gdbserver --attach 127.0.0.1:1234 2468\n");
    exit(-1);
  }

  if (attach)
  {
    pid = atoi(*next_arg);
    init_tids(pid);
    for (int i = 0, n = 0; i < THREAD_NUMBER && n < threads.len; i++)
      if (threads.t[i].tid)
      {
        if (ptrace(PTRACE_ATTACH, threads.t[i].tid, NULL, NULL) < 0)
        {
          perror("ptrace()");
          return -1;
        }
        if (waitpid(threads.t[i].tid, &threads.t[i].stat, __WALL) < 0)
        {
          perror("waitpid");
          return -1;
        }
        ptrace(PTRACE_SETOPTIONS, threads.t[i].tid, NULL, PTRACE_O_TRACECLONE);
        n++;
      }
  }
  else
  {
    pid = fork();
    if (pid == 0)
    {
      char **args = next_arg;
      setpgrp();
      ptrace(PTRACE_TRACEME, 0, NULL, NULL);
      execvp(args[0], args);
      perror(args[0]);
      _exit(1);
    }
    if (waitpid(pid, &stat, __WALL) < 0)
    {
      perror("waitpid");
      return -1;
    }
    threads.t[0].pid = threads.t[0].tid = pid;
    threads.t[0].stat = stat;
    threads.len = 1;
    int options = PTRACE_O_TRACECLONE;
#ifdef PTRACE_O_EXITKILL
    options |= PTRACE_O_EXITKILL;
#endif
    ptrace(PTRACE_SETOPTIONS, pid, NULL, options);
  }
  threads.curr = &threads.t[0];
  initialize_async_io(sigint_pid);
  remote_prepare(target);
  get_request();
  return 0;
}
```

在面對不同的指令集架構的情況下，可能從arch.h 描述register 的，不同版本的gdb 可能對應到的 headfile不太相同，版號大改之類的
```c
#ifndef ARCH_H
#define ARCH_H

#include <stdint.h>

struct reg_struct
{
    int idx;
    int size;
};

#define ARCH_REG_NUM (sizeof(regs_map) / sizeof(struct reg_struct))

#ifdef __i386__

#include <sys/reg.h>

#define SZ 4
#define FEATURE_STR "l<target version=\"1.0\"><architecture>i386</architecture></target>"
static uint8_t break_instr[] = {0xcc};

#define PC EIP
#define EXTRA_NUM 41
#define EXTRA_REG ORIG_EAX
#define EXTRA_SIZE 4

typedef struct user_regs_struct regs_struct;

// gdb/features/i386/32bit-core.c
struct reg_struct regs_map[] = {
    {EAX, 4},
    {ECX, 4},
    {EDX, 4},
    {EBX, 4},
    {UESP, 4},
    {EBP, 4},
    {ESI, 4},
    {EDI, 4},
    {EIP, 4},
    {EFL, 4},
    {CS, 4},
    {SS, 4},
    {DS, 4},
    {ES, 4},
    {FS, 4},
    {GS, 4},
};

#endif /* __i386__ */

#ifdef __x86_64__

#include <sys/reg.h>

#define SZ 8
#define FEATURE_STR "l<target version=\"1.0\"><architecture>i386:x86-64</architecture></target>"
static uint8_t break_instr[] = {0xcc};

#define PC RIP
#define EXTRA_NUM 57
#define EXTRA_REG ORIG_RAX
#define EXTRA_SIZE 8

typedef struct user_regs_struct regs_struct;

// gdb/features/i386/64bit-core.c
struct reg_struct regs_map[] = {
    {RAX, 8},
    {RBX, 8},
    {RCX, 8},
    {RDX, 8},
    {RSI, 8},
    {RDI, 8},
    {RBP, 8},
    {RSP, 8},
    {R8, 8},
    {R9, 8},
    {R10, 8},
    {R11, 8},
    {R12, 8},
    {R13, 8},
    {R14, 8},
    {R15, 8},
    {RIP, 8},
    {EFLAGS, 4},
    {CS, 4},
    {SS, 4},
    {DS, 4},
    {ES, 4},
    {FS, 4},
    {GS, 4},
};

#endif /* __x86_64__ */

#ifdef __arm__

#define SZ 4
#define FEATURE_STR "l<target version=\"1.0\"><architecture>arm</architecture></target>"

static uint8_t break_instr[] = {0xf0, 0x01, 0xf0, 0xe7};

#define PC 15
#define EXTRA_NUM 25
#define EXTRA_REG 16
#define EXTRA_SIZE 4

typedef struct user_regs regs_struct;

struct reg_struct regs_map[] = {
    {0, 4},
    {1, 4},
    {2, 4},
    {3, 4},
    {4, 4},
    {5, 4},
    {6, 4},
    {7, 4},
    {8, 4},
    {9, 4},
    {10, 4},
    {11, 4},
    {12, 4},
    {13, 4},
    {14, 4},
    {15, 4},
};

#endif /* __arm__ */

#ifdef __powerpc__

#define SZ 4
#define FEATURE_STR "l<target version=\"1.0\">\
  <architecture>powerpc:common</architecture>\
  <feature name=\"org.gnu.gdb.power.core\">\
    <reg name=\"r0\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r1\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r2\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r3\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r4\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r5\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r6\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r7\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r8\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r9\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r10\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r11\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r12\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r13\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r14\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r15\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r16\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r17\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r18\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r19\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r20\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r21\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r22\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r23\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r24\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r25\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r26\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r27\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r28\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r29\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r30\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"r31\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"pc\" bitsize=\"32\" type=\"code_ptr\"/>\
    <reg name=\"msr\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"orig_r3\" bitsize=\"32\" type=\"int\"/>\
    <reg name=\"ctr\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"lr\" bitsize=\"32\" type=\"code_ptr\"/>\
    <reg name=\"xer\" bitsize=\"32\" type=\"uint32\"/>\
    <reg name=\"cr\" bitsize=\"32\" type=\"uint32\"/>\
</feature>\
</target>"

static uint8_t break_instr[] = {};

#define PC 32
#define EXTRA_NUM -1
#define EXTRA_REG -1
#define EXTRA_SIZE -1

typedef struct pt_regs regs_struct;

struct reg_struct regs_map[] = {
    {0, 4},
    {1, 4},
    {2, 4},
    {3, 4},
    {4, 4},
    {5, 4},
    {6, 4},
    {7, 4},
    {8, 4},
    {9, 4},
    {10, 4},
    {11, 4},
    {12, 4},
    {13, 4},
    {14, 4},
    {15, 4},
    {16, 4},
    {17, 4},
    {18, 4},
    {19, 4},
    {20, 4},
    {21, 4},
    {22, 4},
    {23, 4},
    {24, 4},
    {25, 4},
    {26, 4},
    {27, 4},
    {28, 4},
    {29, 4},
    {30, 4},
    {31, 4},
    {32, 4},
    {33, 4},
    {34, 4},
    {35, 4},
    {36, 4},
    {37, 4},
    {38, 4},
};

#endif /* __powerpc__ */

#endif /* ARCH_H */
```

