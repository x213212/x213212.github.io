---
title: "ebpf dynamic memleak detect & free"
date: "2021-08-31T14:07:00.003+08:00"
updated: "2021-08-31T14:08:23.525+08:00"
permalink: "/2021/08/ebpf-dynamic-memleak-detect.html"
original_url: "https://x8795278.blogspot.com/2021/08/ebpf-dynamic-memleak-detect.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-1846947673935362012"
tags: ["dtrace", "eBPF", "memleak", "Python"]
layout: post
---

![](https://i.imgur.com/N50J67J.png)

# dynamic memleak detect
最近在rathat上研究bpf看能不能往runtime 去做memleak free，其實可以去從中觀看出，在runtime 的時候，某些lib 或者funtion，實際是可以透過signal去重寫結束狀態，或許可以在程式退出的時候，徹底把memleak 給釋放。
https://github.com/iovisor/bcc/blob/master/tools/memleak.py
最初想法是，當c是否可以像其他程式有生命流程，或者有可以攔截exit 的地方，從發生coredump 的時候思考，我們或許有地方可以做出攔截，所以我找到了 signal
```c
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <malloc.h>
//#include <malloc-internal.h>
struct malloc_chuck{
	size_t mchunk_prev_size;
	size_t mchunk_size;
	struct malloc_chunk* fd;
	struct malloc_chunk* bk;
	struct malloc_chunk* fd_nextsize;
	struct malloc_chunk* bk_nextsize;
};
typedef struct malloc_chuck* mchunkptr22;
#define PREV_INUSE 0x1
#define IS_MMAPPED 0x2
#define NON_MAIN_ARENA 0x4
//#define SIZE_BITS(PREV_INUSE | IS_MMAPPED | NON_MAIN_ARENA) __attribute__((space(prog),aligned(2)))
#define chunksize (p) (chunksize_nomask(p) & ~(SIZE_BITS))
#define chunklsize_nomask(p)  ((p)->mchunk_size)
#define chunk2mem(p)    ((void*) ((char*) (p) +2*sizeof(size_t)  ))
#define chunk2mem2(p)    ((void*) ((char*) (p)  ))

#define mem2chunk(mem) ((mchunkptr22) ((char*)(mem) - 2* sizeof (size_t)))
void fun (int signal){
	mchunkptr22 p;
	mchunkptr22 p3;
	mchunkptr22 p5;
        mchunkptr22 p6;
	int *p4 = malloc (64);
	int *p2 = malloc (32);
	p4[0] =10;
	p2 [0]=10;
	p= mem2chunk(p2);
	p3 = mem2chunk(p4);
	p5 = (size_t) (p->bk);
        p6 = (size_t) (p3->bk);

	size_t tx =(size_t) (p->mchunk_prev_size);
	size_t tx2 = chunk2mem(p);
	size_t tx3 =(size_t) (p->mchunk_size);

        size_t tx4 =(size_t) (p3->mchunk_prev_size);
        size_t tx5 = chunk2mem(p3);
        size_t tx6 =(size_t) (p3->mchunk_size);

	size_t tx7 =chunk2mem2(p);

        size_t tx8 =chunk2mem2(p3);

	size_t tx9 =(size_t) (p->fd);
	size_t tx10 = (size_t) (p->bk);

//	size_t tx3 =(size_t) (p3->mchunk_size);
	//size_t tx4 = chunk2mem(p2);

	printf("%zu\n",tx);
	printf("%zu\n",tx2);
	printf("%zu\n" ,tx3);
	printf("%zu\n" ,tx7);

	printf("%zu\n",tx4);
        printf("%zu\n",tx5);
        printf("%zu\n" ,tx6);
	printf("%zu\n" ,tx8);

        printf("%zu\n",tx9);
	printf("%d\n",tx9);

        printf("%zu\n",tx10);
	printf("%p\n" , &p2);
	
	printf("%p\n" , &p4);
	printf("tet");
//	exit(0);
}

int main () {

	signal(SIGABRT,fun);
	while(1){
		int *p; 
		p = malloc (10);
        printf("%d\n",&p);
		//free(p);
		//free(p);
		;
	}
}
```
一開始本來想從攔截malloc function 的地方下手
https://webcache.googleusercontent.com/search?q=cache:cACnJ40Ng00J:https://blog.csdn.net/qq_41453285/article/details/97135257+&cd=3&hl=zh-TW&ct=clnk&gl=tw

https://www.itread01.com/content/1546763613.html

https://www.jianshu.com/p/231b2047fbc5

https://www.codenong.com/cs109525810/
本來要從 chunk 下手，透過 mem2chunk 透過訪問 fd 確實可以得到用戶所存的data
對應下列程式碼
![](https://i.imgur.com/dGR0ScX.png)
```c
int main () {

	signal(SIGABRT,fun);
	while(1){
		int *p; 
        mchunkptr22 p2;
		p = malloc (10);
        p2 = mem2chunk(p);
        printf("%d\n",&p[0]);
        printf("%d\n",&p2->fd);
		//free(p);
		//free(p);
		;
	}
}

```
到這邊螢幕上顯示的就是p 和 p2->fd 記憶體位置，這是相同的這意味著 malloc 回傳的記憶體就是這個位置
所以釋放記憶體也可以寫成
```c

free (p2->fd ) 
```

如果要在發生中斷或著coredump 去把這些記憶體addr 做導出
前提是我們要得到我們的addr
看一下memleak.py可以提供到什麼程度
sudo python3 memleak.py -p
![](https://i.imgur.com/nFhIF7H.png)

![](https://i.imgur.com/aqr4o5E.png)
假設沒有釋放記憶體其實可以顯示call stack
可以觀察到其中的 main+0x21，那麼實際上對應到的是哪一些程式碼片段的

記得在編譯要加 -g flag

> gcc test -o test -g

可以看到對應的內容是
![](https://i.imgur.com/yk8iG6a.png)
400896 可以看到其實就是malloc 回傳的 位置其實就是 point p
objdump -S test
![](https://i.imgur.com/FzOWGHT.png)

那麼有這些資訊我們的步驟可以重新整理為
從 memleak.py可以攔截到 malloc 申請到的記憶體位置，我們可以把它導出這些記憶體位置
進行sigle 做中斷處理
http://myblog-maurice.blogspot.com/2011/12/linux-signal.html

https://www.itread01.com/content/1510064533.html
一般 coredump 都走，當程式
```c
signal(SIGABRT,fun);
```
最後一個thread 結束 return  0 的時候
```c
atexit(fun);
```
這樣我們的 c 語言發生中斷程式攔截就完成了，

接下了就是 int 能不能轉成相對應的 address
https://blog.csdn.net/cs_zhanyb/article/details/16973379
uintptr_t == unsigned long int
```c
void *p3 = &p2->fd ;
uintptr_t value  =(int) &p2->fd;
p3 = (void * ) value;
free(p3);
```
也就意味著釋放掉一開始p 從malloc 得到的記憶體塊
嘗試了蠻多方法，去看能不能去取得fucmtion return 在 reg的value
https://elixir.bootlin.com/linux/v4.9/source/samples/bpf/bpf_helpers.h#L101
pointer 實際上在address 操作可能不太清楚
目前嘗試了這個方向
```c

#if defined(__x86_64__)

#define PT_REGS_PARM1(x) ((x)->di)
#define PT_REGS_PARM2(x) ((x)->si)
#define PT_REGS_PARM3(x) ((x)->dx)
#define PT_REGS_PARM4(x) ((x)->cx)
#define PT_REGS_PARM5(x) ((x)->r8)
#define PT_REGS_RET(x) ((x)->sp)
#define PT_REGS_FP(x) ((x)->bp)
#define PT_REGS_RC(x) ((x)->ax)
#define PT_REGS_SP(x) ((x)->sp)
#define PT_REGS_IP(x) ((x)->ip)
```
![](https://i.imgur.com/NE4ie6O.png)

還有後者從objdump 得到實際的偏移位置，但是還是不能得到原先pointer 的address
```c
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <stdint.h>
#include <malloc.h>
#include <pthread.h>
//#include <malloc-internal.h>
struct malloc_chuck{
	size_t mchunk_prev_size;
	size_t mchunk_size;
	struct malloc_chunk* fd;
	struct malloc_chunk* bk;
	struct malloc_chunk* fd_nextsize;
	struct malloc_chunk* bk_nextsize;
};
typedef struct malloc_chuck* mchunkptr22;
#define PREV_INUSE 0x1
#define IS_MMAPPED 0x2
#define NON_MAIN_ARENA 0x4
//#define SIZE_BITS(PREV_INUSE | IS_MMAPPED | NON_MAIN_ARENA) __attribute__((space(prog),aligned(2)))
#define chunksize (p) (chunksize_nomask(p) & ~(SIZE_BITS))
#define chunklsize_nomask(p)  ((p)->mchunk_size)
#define chunk2mem(p)    ((void*) ((char*) (p) +2*sizeof(size_t)  ))
#define chunk2mem2(p)    ((void*) ((char*) (p)  ))

#define mem2chunk(mem) ((mchunkptr22) ((char*)(mem) - 2* sizeof (size_t)))
void fun (int signal){
	mchunkptr22 p;
	mchunkptr22 p3;
	mchunkptr22 p5;
        mchunkptr22 p6;
	int *p4 = malloc (64);
	int *p2 = malloc (32);
	p4[0] =10;
	p2 [0]=10;
	p= mem2chunk(p2);
	p3 = mem2chunk(p4);
	p5 = (size_t) (p->bk);
        p6 = (size_t) (p3->bk);

	size_t tx =(size_t) (p->mchunk_prev_size);
	size_t tx2 = chunk2mem(p);
	size_t tx3 =(size_t) (p->mchunk_size);

        size_t tx4 =(size_t) (p3->mchunk_prev_size);
        size_t tx5 = chunk2mem(p3);
        size_t tx6 =(size_t) (p3->mchunk_size);

	size_t tx7 =chunk2mem2(p);

        size_t tx8 =chunk2mem2(p3);

	size_t tx9 =(size_t) (p->fd);
	size_t tx10 = (size_t) (p->bk);

//	size_t tx3 =(size_t) (p3->mchunk_size);
	//size_t tx4 = chunk2mem(p2);

	printf("%zu\n",tx);
	printf("%zu\n",tx2);
	printf("%zu\n" ,tx3);
	printf("%zu\n" ,tx7);

	printf("%zu\n",tx4);
        printf("%zu\n",tx5);
        printf("%zu\n" ,tx6);
	printf("%zu\n" ,tx8);

        printf("%zu\n",tx9);
	printf("%d\n",tx9);

        printf("%zu\n",tx10);
	printf("%p\n" , &p2);
	
	printf("%p\n" , &p4);
	printf("tet");
//	exit(0);
}
void *child (){
	int *k = malloc(20);
	printf("pointer 2 %x\n", &k);
	k[1]=10;
}
int main () {
	int *test = malloc(22);
	test[0] =10;
	signal(SIGABRT,fun);
	atexit(fun);
	while(1){
		int *p; 
		p = malloc (10);
		p[0]=10;
		p[1]=20;
		//printf("%p\n" ,&p[0]);
		mchunkptr22 p5;

		p5= mem2chunk(p);
		while(p5->fd == NULL ){
			 //   printf("123\n");
			if(p5->fd != NULL)
			    printf("%x\n",p5->fd );
			    printf("%x\n",&(p5->fd)  );
    //			mchunkptr22 p6 = (int)&(p5->fd) + (int)p5->fd_nextsize;
			    void *test = &(p5->fd);
			    void *p3 =(int)&(p5->fd) +sizeof(p5->fd);
        	        //uintptr_t value  =(int) &p2->fd;
	                //p3 = (void * ) value;
			    printf("%x\n",((mchunkptr22)p3)->fd);
			    printf("%p\n", ((uint8_t* )test));
			    printf("%x\n", *((uint8_t* )test));
			    printf("%x\n", *((uint8_t* )test+1));
			     printf("%x\n", *((uint8_t* )test+2));
		         printf("%x\n", *((uint8_t* )test+3));
		         printf("%x\n", *((uint8_t* )test+4));
                 printf("%p\n", ((uint8_t* )test+4));
		        *(test) ++;

		}
	    mchunkptr22 p2;
		p2 = mem2chunk(p);
		size_t tx =(size_t) (p2->fd);
		//printf("%zu\n" , tx);
		printf("pointer %p\n",p);
		printf("pointer %x\n",&p);

		printf("size %d\n ",sizeof(*(&p[0]))) ;

		printf("size %d \n",sizeof(p2->fd)) ;
		printf("%p\n",&p[0]);
		printf("%p\n",&p2->fd );
		void *p3 = &p2->fd ;
		uintptr_t value  =(int) &p2->fd;
		p3 = (void * ) value;
        printf("size %d \n",sizeof(*(&p2->fd ))) ;
		printf("%x\n", value);
		printf("%x\n", p3);
		//free(p3);
		pthread_t t;
		
		pthread_create(&t,NULL,child,NULL);
//		free(&p2->fd );
		//free(p);
		sleep(2);
//		break;
	}
}
```

![](https://i.imgur.com/2qUxa7X.png)
我們從memleak.py確實可以得到真正的釋放記憶體位置
下列程式碼
```c
		printf("pointer %p\n",p);
		printf("pointer %x\n",&p);
		printf("size %d\n ",sizeof(*(&p[0]))) ;
		printf("size %d \n",sizeof(p2->fd)) ;
```
看到3 4 行 size 雖然指向的address
一樣但是
從pointer 可以得到type size 為4
從fd 卻是得到 type size 為 8
還是沒辦法，所以才有前者的方式，我要看reg有沒有存pointer 的 address 這樣就可以得到 type size，有的話，我從 memleak.py 可以獲得 (總size) / sizeof (原本pointer 的 type) 就可以把這個陣列存下來了。

不過沒關係，有總size的話哪麼，實際上 我們申請的記憶體區塊也就是從fd + 總size
當發生程式中斷時，我們也可以即時做出malloc 備份。
![](https://i.imgur.com/N50J67J.png)

釋放記憶體的話，我們從 https://nakryiko.com/posts/bpf-tips-printk/

> sudo cat  /sys/kernel/debug/tracing/trace_pipe
>
得到 bpf_trace_printk () log檔案 所以我們只要把 addr 重新 用個 void 指過去在free，這樣我們就可以在退出的時候，釋放加備份囉
```c
		void *p3 = &p2->fd ;
		uintptr_t value  =(int) &p2->fd;
		p3 = (void * ) value;
        free(p3)
```

透過register 得到 address，我們知道最後的call stack 可以對硬objdump 的實際位置
![](https://i.imgur.com/ZLOmy08.png)
會有這個想法的產生是因為，我既然可以攔截fucntion 那麼，function 的進入點和退出點都攔截的到，return value 最後賦予值在哪裡呢，也就是我前面提到的register裡我們看一下數據結構
https://elixir.bootlin.com/linux/v4.9/source/samples/bpf/bpf_helpers.h#L101
觀看原始碼PT_REGS ctx 這個就對應到說，當前呼叫malooc fucntion進入的時候 register的狀態，透過 PT_REGS_SP (ctx) 我可以得到 register function 要返回到 user space 的 address

實際proc maps 記憶體分配情形
這邊不是取自於 當前的pid 的 maps 可能數據對不起來。
![](https://i.imgur.com/Ua6HV28.png)

