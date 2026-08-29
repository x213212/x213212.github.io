---
title: "mtrace runtime output"
date: "2021-01-27T04:31:00.002+08:00"
updated: "2021-01-27T04:31:36.131+08:00"
permalink: "/2021/01/mtrace-runtime-output.html"
original_url: "https://x8795278.blogspot.com/2021/01/mtrace-runtime-output.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3240665701202961611"
tags: ["mtrace"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/GNU_Compiler_Collection_logo.svg/640px-GNU_Compiler_Collection_logo.svg.png?1606591693910")

# mtrace
如何在程式還沒跑完的時候用mtrace 攔截發生記憶體洩漏的問題呢
mtrace 就是去 hook malloc or free 的 function 的東西
嘗試了幾種方式，在編譯glibc 也就是 c語言 預設會去call function 的 library
主要就是在
![](https://i.imgur.com/n0tCc6y.png)
有加鎖，預設我是要從原本的入口點
![](https://i.imgur.com/5OgjVUR.png)
這邊修改的結果嘗試了很多方式，
主要是看能不能讓寫檔部分脫離main thread
再來自行寫thread 會遇到 編譯lib 需要加lpthread 的問題主要我還是找不到要加在哪
再來就是試圖在hook function 的地方也就是，我們 c語言經過我們的
   > mtrace();  
正常流程要到 return 才能得到我們的輸出
mtrace 的原理就是去 hook malloc free 預設function
```c
#include <stdio.h>  
#include <stdlib.h>  
#include <string.h>  
   
#include <mcheck.h>  

int main(){  
	    setenv("MALLOC_TRACE", "output", 1);  
	    mtrace();  

		char * text = ( char * ) malloc (sizeof(char) * 100);  
   
		memset(text,'/0',100);  
		memcpy(text,"hello,world!",12);  
		while(true){}  <=============程式還沒跑完要得到 output
		printf("%s/n","1");	       
		printf("%s/n",text);  
        free(text);
		return 0;  
} 
```
最後我們用奇怪的方式，脫離main thread
```c

char buffer[50];
  sprintf(buffer,"echo qqqqqqq+ %p %#lx >> test.txt", hdr, (unsigned long int) size);

  system(buffer);
```
這樣我們就可以在程式還沒結束之前得到我們的輸出了，我們會再進一步對這些記憶體做處理
![](https://i.imgur.com/fRNuQck.png)

# glibc
紀錄一下編譯 glibc link 到 我們編譯test 步驟
http://www.gnu.org/software/libc/

```bash

tar zxvf glibc-2.27.tar.gz
記得不是在解壓縮的目錄裡面創往目錄外面一層創
mkdir -p build/glibc-build
cd  build/glibc-build
../../glibc-2.27/configure CFLAGS="-fno-builtin-strlen  -lpthread -ggdb -O2" FEATURES="preserve-libs nostrip splitdebug" --prefix=/root/mtrace/build/glibc-build

make -j20
make install

g++ test.c -o test ... \
   -Wl,--rpath=/root/mtrace/build/glibc-build/lib \
   -Wl,--dynamic-linker=/root/mtrace/build/glibc-build/lib/ld-linux-x86-64.so.2
```

