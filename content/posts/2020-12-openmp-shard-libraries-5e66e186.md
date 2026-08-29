---
title: "OpenMp shard libraries link"
date: "2020-12-01T23:17:00.003+08:00"
updated: "2020-12-01T23:18:03.996+08:00"
permalink: "/2020/12/openmp-shard-libraries.html"
original_url: "https://x8795278.blogspot.com/2020/12/openmp-shard-libraries.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-4319006801148389647"
tags: ["GCC", "link", "OpenMP"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/e/eb/OpenMP_logo.png)

# shard library
https://medium.com/fcamels-notes/linux-%E7%B7%A8%E8%AD%AF-shared-library-%E7%9A%84%E6%96%B9%E6%B3%95%E5%92%8C%E6%B3%A8%E6%84%8F%E4%BA%8B%E9%A0%85-cb35844ef331
https://aben20807.blogspot.com/2018/08/1070825-c-static-shared.html
main.c
```c
#include "foo.h"
int main (void){
        foo();
        return 0;

}
```
foo.h
```c
#ifndef FOO_H
#define FOO_H
void foo();
#endif

```
foo.c
```c
#include "foo.h"
#include <stdio.h>
void foo(){
        printf("call foo\n");
}
```
```bash
gcc -g -fPIC -c foo.c

gcc -shared foo.o -o libfoo.so

gcc -g -o main main.c libfoo.so
or
gcc -g -o main main.c -lfoo -L.

sudo cp ./libfoo.so /usr/lib/
sudo rm /usr/lib/libfoo.so  

```
#    openmp
```c
#include "foo.h" 
#include <stdio.h> 
void foo(){  
    #pragma omp parallel   
    {   
    printf("start!\n"); 
    }         
    printf("call foo\n");
    int i ;         
    int n=10;         
    double s =0.0;         
    omp_set_num_threads(4);         
    #pragma omp parallel for reduction(+:s)         
    for(i = 0 ; i<n ; ++i)         {
        printf("threads %d\n", omp_get_thread_num());
        s+=i; 
    }         
    printf("%f\n",s); 
} 
```
```bash
gcc -g -fPIC -Wall -fopenmp   -c foo.c 
 gcc -shared -fopenmp foo.o -o libfoo.so 
 gcc -g -o main main.c -lfoo -L.  

```
![](https://i.imgur.com/IrppegQ.png)

