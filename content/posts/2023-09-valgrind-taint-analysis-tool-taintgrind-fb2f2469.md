---
title: "Valgrind taint analysis tool :taintgrind"
date: "2023-09-21T22:18:00.006+08:00"
updated: "2023-09-21T22:18:43.458+08:00"
permalink: "/2023/09/valgrind-taint-analysis-tool-taintgrind.html"
original_url: "https://x8795278.blogspot.com/2023/09/valgrind-taint-analysis-tool-taintgrind.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3789193488739361313"
tags: ["taintgrind", "Valgrind"]
layout: post
---

![](https://hackmd.io/_uploads/S1Y7kAY16.png)

# Taint analysis
Valgrind taint analysis tool :taintgrind
前幾天有說想要關聯所有variable 最簡單的方式可以用taintgrind ,這邊找尋一下variable之間的關聯

Git clone https://github.com/eembc/coremark.git
/home/gcc-plugin/coremark/barebones/core_portme.mak
/home/gcc-plugin/coremark/posix/core_portme.mak
```makefile
# Flag: OUTFLAG
#   Use this flag to define how to to get an executable (e.g -o)
OUTFLAG= -o
# Flag: CC
#   Use this flag to define compiler to use
CC?= cc
# Flag: CFLAGS
#   Use this flag to define compiler options. Note, you can add compiler options from the command line using XCFLAGS="other flags"
PORT_CFLAGS = -O0 -g
```
/home/gcc-plugin/Makefile
```makefile

PLUGIN_CFLAGS = -I/home/rex603/valgrind-3.18.1/taintgrind/ -I/home/rex603/valgrind-3.18.1/include 
HEADERS = coremark.h 
CHECK_FILES = $(ORIG_SRCS) $(HEADERS)

….
compile: $(OPATH) $(SRCS) $(HEADERS) 
    $(CC) $(PLUGIN_CFLAGS) $(CFLAGS) $(XCFLAGS) $(SRCS) $(OUTCMD) 2> ./check.log

```
這邊要注意的是 -O0 這邊境可能的保留程式碼沒被優化的訊息 ,記得-g 保留source code 位置
# Build Valgrind & taintgrind
這裡要確保 Valgrind 版本為 3.18.1,也就是 taintgrind 最後更新的對應的 Valgrind 版本
然後稍微換一下來源capstone-3.0.4
```bash

wget https://sourceware.org/pub/valgrind/valgrind-3.18.1.tar.bz2
tar jxvf valgrind-3.18.1.tar.bz2
cd valgrind-3.18.1.tar.bz2 
git clone http://github.com/wmkhoo/taintgrind.git
cd taintgrind 
Need change capstone-3.0.4.tar.gz https://opentuna.cn/pypi/web/packages/e7/29/e9ad2a12c38f19e9ca8aff05122e5b9e271da6ecbfb6c4e20aee381b49ff/capstone-3.0.4.tar.gz#sha256=945d3b8c3646a1c3914824c416439e2cf2df8969dd722c8979cdcc23b40ad225
sudo sh build_taintgrind.sh
```

# Run
```bash
/home/rex603/valgrind-3.18.1/build/bin/valgrind --tool=taintgrind
```

# build test case
第一個 -I../ 該目錄是位於 taintgrind 的"taintgrind.h"
第二個 -I../../ 是對應 Valgrind 下的include

```bash
gcc -I../ -I../../include -O0 -g ./test.c -o test 
```
假設要找出a的所有汙染路徑
```c
#include "taintgrind.h"
#include <stdio.h>

int test(int x ){
	// printf("test%d",x);
    // TNT_TAINT(&x,sizeof(x));
	return x%99;
}
int get_sign(int x) {
    if (x == 0) return test(x);
    if (x < 0)  return test(x);
    return test(x);
}
int main(int argc, char **argv)
{
    // Turns on printing
    //TNT_START_PRINT();
    int a = 1000;
    // Defines int a as tainted
    TNT_TAINT(&a,sizeof(a));
    int s = get_sign(a);
    // Turns off printing
    //TNT_STOP_PRINT();
    return 0;
}

```
# run test case
```bash
/home/rex603/valgrind-3.18.1/build/bin/valgrind --tool=taintgrind ./tests/test
```
![](https://hackmd.io/_uploads/S1Y7kAY16.png)

# coremark test
add trace point
## core_main.c
```c
#error "Cannot use a static data area with multiple contexts!"
#endif
#elif (MEM_METHOD == MEM_MALLOC)
    for (i = 0; i < MULTITHREAD; i++)
    {
        ee_s32 malloc_override = get_seed(7);
        if (malloc_override != 0)
            results[i].size = malloc_override;
        else
            results[i].size = TOTAL_DATA_SIZE;
        results[i].memblock[0] = portable_malloc(results[i].size);
       
        results[i].seed1       = results[0].seed1;
        results[i].seed2       = results[0].seed2;
        results[i].seed3       = results[0].seed3;
        results[i].err         = 0;
        results[i].execs       = results[0].execs;
    }
    TNT_TAINT(& results[0].memblock, sizeof( results[0].memblock));
```

# run coremark
這邊可以看到log 數量蠻多的
```bash
 /home/valgrind-3.18.1/build/bin/valgrind --tool=taintgrind ./coremark.exe  0x0 0x0 0x66 1 7 1 2000 2> logfile

```
![](https://hackmd.io/_uploads/rkZR1RYy6.png)
# parse logfile
```python
file_path = "logfile"

results = {}
with open(file_path, "r") as file:
    for line in file:
        parts = line.strip().split("|")
        if len(parts) >= 2:

            source_code, asm,variable_memory = parts[0], parts[1] ,parts[-1].strip()
        
            if(variable_memory.find("<-")>=0):
                operation, variable = variable_memory.split("<-")

                source_code = source_code.strip()
                operation = operation.strip()
                variable = variable.strip()
                # Use the source code as the dictionary key and add the operation and variable to a set
                
                if variable.find(":")>=0:
                    result_save = (f"{source_code} | {asm} | {variable}")
                elif operation.find(":")>=0:
                    result_save = (f"{source_code} | {asm} | {operation}")
                if source_code in results:
                    
                    results[result_save].add(result_save)
                else:
                    results[result_save] = {result_save}
                
# Print the simplified results
for source_code, data_set in results.items():
    for data in data_set:
        print(f"{data}")
```
# output log
這邊可以看到最終過濾出來的variable 剩下 600多個也就是 memblock 關聯了600多個variable
![](https://hackmd.io/_uploads/Sk0Ge0F1T.png)
![](https://hackmd.io/_uploads/BJ5Xx0Kya.png)

