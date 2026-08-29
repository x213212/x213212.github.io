---
title: "simple gcc plugin analysis"
date: "2020-11-28T15:28:00.002+08:00"
updated: "2020-11-28T15:28:14.454+08:00"
permalink: "/2020/11/simple-gcc-plugin-analysis.html"
original_url: "https://x8795278.blogspot.com/2020/11/simple-gcc-plugin-analysis.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-4522758708780005209"
tags: ["Compiler", "GCC"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/GNU_Compiler_Collection_logo.svg/640px-GNU_Compiler_Collection_logo.svg.png?1606591693910)

# gcc plugin 簡述
在網路上這部分的資訊非常的稀少，剛好有
https://zhuanlan.zhihu.com/p/49490338
假設要做分析的話我們首先要了解這個 plugin 是實作在哪一個階段，也就是
![](https://i.imgur.com/wdfK5zH.png)
我們是實作在gcc compiler 的這個階段
就是我們中間層 ir的部分 加入我們額外新增的一些gcc 原生的 api 進行分析
https://code.woboq.org/gcc/gcc/
https://gcc.gnu.org/onlinedocs/gccint/Passes.html
這類型的網站幫助我們去了解我們整個編譯器的架構，也差不多可以做個到目前這個學期的總結，
我們可以透過左上方的搜尋去查找我們需要的函數
![](https://i.imgur.com/sT7aEvY.png)
或者
[深入分析GCC](https://www.books.com.tw/products/CN11417092)
因為到目前為止我們的 gcc compiler 好像已經突破1600萬行，不過plugin和前中後端模組化，可以協助我們把問題縮小到專注在某些要研究區間的而不會失焦，如果對於研究compiler新手在不熟悉gcc compiler 的情況下要更動source code 實在是太難了，所以我們可以用 plugin 的方式 非侵入方式來更動我們的soruce code 分析，接下來會介紹一些background的東西，
什麼是call graph ,什麼是 basic block , 什麼是 gimple，怎麼透過 gimple 去得到我們最終的 varibale 再透過這些樹狀結構來分析
到此我們整個 gcc compiler 都圍繞在這些 backgroud 去做分析
# call graph
我們知道程式都是由不同function 來進行呼叫所以有call graph node 彼此之間連結起來，那麼可以知道假設我在main function 呼叫 f function 在 f function 呼叫 g function 就可以知道它們之間的關係是
```
main -> callee  f    -> caller 
f    -> callee  g    -> caller main
g    -> callee      -> caller  f 
```

關鍵字 FOR_EACH_DEFINED_FUNCTION 我們可以去 plugin 去遍歷我們的程式裡面所有 node，接下來我們可以透過 取的node 節點裡面的東西 get_fun()
https://stackoverflow.com/questions/29416434/get-the-number-of-functions-of-the-c-file-compiled-using-gcc-plugin
該提問有簡單提到怎麼去遍歷我的 function node
# basic block
當然一個fucntion 裡面有很多 basic block 因為程式碼在 compiler 編譯的階段可能會做一些優化的分析省略程式碼，舉例來說在走 if or else 的時候，我們可能走向其中一任意條件內容，假設if 條件恆真的情況下意味著 else 永遠無法到達，這個時候 compiler 可能會直接優化掉。以程式碼來看就是
```c
int main(){ 	
    int *a = malloc(1); 	
    if(a) 		
        a[0] = 1; 	
    else 		
        a = malloc(1); 	
    free(a); 	
    return 0 ; 
} 
```
![](https://i.imgur.com/R9OnDU4.png)
反正就是類似這樣的東西透過
https://code.woboq.org/gcc/gcc/cgraph.h.html
搜尋可以得到更多資訊獲取，
![](https://i.imgur.com/wgbYFGV.png)
得到我們的 function
https://code.woboq.org/gcc/gcc/function.h.html#function
繼續追蹤，我們的 gcc 裡面都是由 tree 彼此之間連結起來
https://thinkingeek.com/2015/08/16/simple-plugin-gcc-part-2/
裡面可以看到FOR_EACH_BB_FN (basic_block, function)
![](https://i.imgur.com/ngRqoJA.png)
裡面有提到如何去展開我們 function 的
![](https://i.imgur.com/h6SMX7p.png)
當然裡面也有提出我們的 gimple
# gimple
剛剛我們拿到我們所有 function，擇一function 遍歷所有 basic block
擇一 basic block 現在要來得到其中一個 basic block 裡面的 stmt 也就是其中一行程式碼，可以看剛剛那篇文章simple-plugin-gcc-part-2
gcc 已經都幫我們把程式之間的 basic block index 給定id 了，在我們分析時候 程式之間的 順序很重要，當然我們去循環 stmt 也可以透過
https://gcc.gnu.org/onlinedocs/gcc-4.9.1/gccint/Sequence-iterators.html
![](https://i.imgur.com/XbiOK1L.png)
看到我們的basic 所以現在我們又可以得到 basic 裡面所有的 stmt
```c
 gimple_stmt_iterator gsi;            
 for (gsi = gsi_start (seq); !gsi_end_p (gsi); gsi_next (&gsi))        {
 gimple g = gsi_stmt (gsi);          /* Do something with gimple statement G.  */       
 }
```
# gimple type
我們拿到gimple 又怎樣呢當然我們至少要展開到 variable tree 才能做分析
https://gcc.gnu.org/onlinedocs/gccint/Tuple-specific-accessors.html#Tuple-specific-accessors
不童的type 又可以對應到不同的 gimple api，我們可以下參數去分析
以
a=b; 是一個GIMPLE_ASSIGN，我們可以使用gimple_assign_rhs取得等號右邊的b的tree結構資料。
到這邊我們可以知道我們整個分析流程就清楚了，展開到我們的 variable

![](https://i.imgur.com/Iyva5zz.png)
當然gcc api 裡面有更多 api 提供我們做使用，可能後續研究會用到，比較多用到的是gcc 裡面有提供tree之間內的相交function 可供使用，到這邊我們只要對去額外紀錄一些pointer，或者一些table 方式我們就可以去制定一些規則，讓我們的 plugin 去做一些額外的分析等等。

