---
title: "AddressSanitizer 大致原理分析"
date: "2022-04-29T00:41:00.004+08:00"
updated: "2022-08-30T14:06:24.697+08:00"
permalink: "/2022/04/addresssanitizer.html"
original_url: "https://x8795278.blogspot.com/2022/04/addresssanitizer.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-4764741113330251572"
tags: ["AddressSanitizer"]
layout: post
---

![](https://i.imgur.com/4yzLGv5.png)

# AddressSanitizer
論文最近要加入AddressSanitizer大概研究一下實現的流程
參考了一些hook的流程找了一個大概不用去改glibc 的方式hook 方式，
https://blog.csdn.net/fengbingchun/article/details/82947673
https://blog.csdn.net/faxiang1230/article/details/107146912?spm=1001.2101.3001.6650.2&utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7ECTRLIST%7Edefault-2.pc_relevant_default&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7ECTRLIST%7Edefault-2.pc_relevant_default&utm_relevant_index=5
https://github.com/google/sanitizers/wiki/AddressSanitizerAlgorithm
https://toutiao.io/posts/usz2mt/preview
https://www.bynav.com/cn/resource/bywork/healthy-work/70.html
https://llvm.org/doxygen/AddressSanitizer_8cpp_source.html
這是官方的版本解釋
# Short version
運行時庫取代了malloc和free函數。被malloc的區域（紅色區域）周圍的內存被毒化。釋放的內存被放置在隔離區，也被毒化。程序中的每一個內存訪問都會被編譯器以如下方式進行轉換。

之前。

*address = ...; // or: ... = *address;
之後。

如果（IsPoisoned(address)）{
  ReportError(address, kAccessSize, kIsWrite)。
}
*address = ...; // 或者: ... = *address。
棘手的部分是如何非常快速地實現IsPoisoned和非常緊湊地實現ReportError。另外，對一些訪問的儀器化可能被證明是多餘的。

# main.c
```c

#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include "wrap_symbol.h"
 
int main()
{
	fprintf(stdout, "===== test start =====\n");
 
	char* p1 = (char*)malloc(4);
	free(p1);
 
	foo();
 
	int* p2 = new int;
	delete p2;
 
	fprintf(stdout, "===== test finish =====\n");
	return 0;
}

```
# wrap_symbol.cpp
```c++

#include "wrap_symbol.h"
#include <stdio.h>
#include <stdlib.h>
 
void* __wrap_malloc(size_t size)
{
	fprintf(stdout, "call __wrap_malloc function, size: %d\n", size);
	return __real_malloc(size);
}
 
void __wrap_free(void* ptr)
{
	fprintf(stdout, "call __wrap_free function\n");
	__real_free(ptr);
}
 
int foo()
{
	fprintf(stdout, "call foo function\n");
	return 0;
}
 
int __wrap_foo()
{
	fprintf(stdout, "call __wrap_foo function\n");
	return 0;
};
 
void* __wrap__Znwm(unsigned long size)
{
	fprintf(stdout, "call __wrap__Znwm funtcion, size: %d\n", size);
	return __real__Znwm(size);
}
 
void __wrap__ZdlPv(void* ptr)
{
	fprintf(stdout, "call __wrap__ZdlPv function\n");
	__real__ZdlPv(ptr);
}

```
# wrap_symbol.h
```c++

#ifndef FBC_LINUX_CODE_TEST_WRAP_SYMBOL_HPP_
#define FBC_LINUX_CODE_TEST_WRAP_SYMBOL_HPP_
 
#include <stdlib.h>
 
extern "C" {
 
void* __wrap_malloc(size_t size);
void __wrap_free(void* ptr);
 
void* __real_malloc(size_t size);
void __real_free(void* ptr);
 
int foo();
int __wrap_foo();
 
// c++filt: _Znwm ==> operator new(unsigned long)
void* __wrap__Znwm(unsigned long size);
// c++filt _ZdlPv ==> operator delete(void*)
void __wrap__ZdlPv(void* ptr);
 
void* __real__Znwm(unsigned long size);
void __real__ZdlPv(void* ptr);
 
} // extern "C"
 
#endif // FBC_LINUX_CODE_TEST_WRAP_SYMBOL_HPP_

```

# build
```
g++ -c *.cpp
g++ -o test_wrap_symbol *.o -O2 -Wall -Wl,--wrap=malloc -Wl,--wrap=free -Wl,--wrap=foo -Wl,--wrap=_Znwm -Wl,--wrap=_ZdlPv
```
初步可以看到這些fucntion被hook了，如果知道程式碼的call stack 和 source code，和程式流程就可以在任意地方進行override
![](https://i.imgur.com/oxQwD3Z.png)

這邊提到在程式碼編譯的過程中也會在申請記憶體的上下產生所謂的 redzone
每個redzone會有所謂的 shdow memory
這意味著假設要檢查 overflow 的話，就檢查緩衝區意味時，是否可能越界存取到 shdow memory,即寫入一般的memory 且覆蓋到shdow memory的 value即發生overflow

```
----------------------------------------------------------------   
|    redzone（前）    |    memory      |    redzone(後)    |   
----------------------------------------------------------------
```

# in stack 防止 overflow 簡略說明
```c

#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include "wrap_symbol.h"
using namespace std;
int main()
{
    fprintf(stdout, "===== test start =====\n");
    char redzone1[32];//instrumentation
    char p1[8];
    char redzone2[24];//instrumentation
    char redzone3[32];//instrumentation

    char *shadow_base = p1;
    char test = 'a';
    char test2 = 'b';
    printf("%p\n", &test);
    printf("%p\n", &test2);

    cout << &shadow_base << endl;
    cout << &shadow_base + 1 << endl;
    cout << &shadow_base + 2 << endl;
    // cout << &shadow_base + 10 << endl;
    cout << "-----------------" << endl;
    cout << &redzone1 << endl;
    cout << &p1 << endl;
    cout << &redzone2 << endl;
    // cout << &redzone3 << endl;

    shadow_base[0] = 0xffffffff; // 标记redzone1的32个字节都不可读写
    p1[0] = 'a';
    shadow_base[1] = 0xffffff00; // 标记数组a的8个字节为可读写的，而redzone2的24个字节均不可读写
    shadow_base[2] = 0xffffffff;

    cout << shadow_base[0] << endl;
    cout << shadow_base[1] << endl;
    cout << shadow_base[2] << endl;

    //發生越界存取的話則在透過comiler 在編譯過程中在所有
    //load/store 加入檢查
    if ((p1 + 0) > &shadow_base[8]) //instrumentation
        cout << "crash" << endl; //instrumentation
    p1[0] = '0';

    printf("%p\n", &shadow_base[0]);
    printf("%p\n", &shadow_base[8]);

    if ((p1 + 8) >= &shadow_base[8]) //instrumentation
        cout << "crash" << endl;//instrumentation
    p1[8] = '0';
   
    free(p1);

    fprintf(stdout, "===== test finish =====\n");
    return 0;
}

```

# in hepa 防止 overflow
簡略說明，這邊跟官方流程有點不太一樣
看著有趣，我自己做了些修改
透過hook malloc 與free達成
那麼重寫一下剛剛的Malloc
```c
void* __wrap_malloc(size_t size)
{
	fprintf(stdout, "call __wrap_malloc function, size: %d\n", size);
	return __real_malloc(size);
}
 
```
# __wrap_malloc
這邊只是模擬因為我沒有shadow，這邊想模擬的是透過重新封裝過後的malloc
可以看到在申請的記憶體位置加上了redzone，可以看到我在maptruesizet key 為原有的位置，value為原有的size
```c
static map<long, int> maptruesizet;
#define RED_ZONE_SIZE 8
void *__wrap_malloc(size_t size)
{
    // asan hook後的malloc

    size_t actual_size = RED_ZONE_SIZE /*前redzone*/ + (size) + RED_ZONE_SIZE /*後redzone*/;

    char *p = (char *)__real_malloc(actual_size);
    //  cout << (&p)<<endl;
    fprintf(stdout, "%x\n", p);
    fprintf(stdout, "%p\n", p);

    maptruesizet[(long)(p)] = size;

    fprintf(stdout, "call __wrap_malloc function, size: %d\n", size);
    return p;
}
```
# isPoisoned
用來檢查是否越界存取
```c
int isPoisoned(long address, int size)
{
    long sizecheck = ((address + size) - (address));
    if (bool(sizecheck > maptruesizet[(long)(address)]))
        return 1;
    else
        return 0;
}
```
# main.c
如果再結合compiler 進行正確的instrumentation，其實在某些狀態就可以正確的捕獲實際上的位置，這邊算是集中管理memeory 的狀態吧，大概是這樣的概念。
```c
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include "wrap_symbol.h"
using namespace std;
// int isPoisoned(){

// }
int main()
{
    fprintf(stdout, "===== test start =====\n");

    char *p1 = (char *)malloc(4);
    fprintf(stdout, "%x\n", p1);
    fprintf(stdout, "%p\n", p1);

    
    if (isPoisoned((long)p1, 1))//instrumentation 1
        cout << "crash" << endl;//instrumentation
    p1[1] = 'a';

    if (isPoisoned((long)p1, 10))//instrumentation 10
        cout << "crash2" << endl;//instrumentation
    p1[10] = 'a';

    free(p1);

    foo();

    int *p2 = new int;
    delete p2;

    fprintf(stdout, "===== test finish =====\n");
    return 0;
}
```
![](https://i.imgur.com/wPcoaDV.png)

上面兩個層面實現，從stack 與 heap 管理其 memory 從而得知是否越界存取等等，hook 可以從 底層glibc 到編譯過程中都可以。

# 這邊防止 shadow 蓋到一般 應用程式的memory
這邊是其他文章的
程序申请的对象内存和它的shadow内存映射关系
因为asan对每8bytes程序内存会保留1byte的shadow内存，所以在进程初始化时，asan得预留(mmap)1/8的虚拟内存，
而对于64bit的Linux，实际最大可用虚拟地址是pow(2, 47), 另外要保证预留的地址不会被程序启动时就占用
掉，所以实际预留的地址要再加上一个适当的偏移, 这样就不会与app的申请内存区域重叠，于是有：
ShadowByteAddr = (AppMemAddr >> 3) + Offset

這邊我在猜想實際上就是 memory 與 Shadow 的綁定，因為instrumentation ,再任意load/store 將會提前的訪問isPoisoned，以此來檢查指令目前寫入的位置是否可能發生越界訪問的問題。

