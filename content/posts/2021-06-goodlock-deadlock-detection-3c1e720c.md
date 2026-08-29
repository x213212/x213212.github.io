---
title: "Goodlock Deadlock detection"
date: "2021-06-08T16:27:00.003+08:00"
updated: "2021-06-08T16:27:49.211+08:00"
permalink: "/2021/06/goodlock-deadlock-detection.html"
original_url: "https://x8795278.blogspot.com/2021/06/goodlock-deadlock-detection.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3900413508159449503"
tags: ["deadlock"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Un_d%C3%AEner_de_philosophes.Jean_Huber.jpg/400px-Un_d%C3%AEner_de_philosophes.Jean_Huber.jpg)

# Goodlock Deadlock detection
如何檢測有效的死鎖之前，我們要找到死鎖的路徑
https://zoomkoding.github.io/os/2019/05/28/deadlock-3.html
那麼什麼路徑才是有效的呢??

當 Cycle 在一個 thread 中創建時

![](https://i.imgur.com/UdqA7tQ.png)

在上述情況下，cycle 是fake的，因為它在一個 thread 中創建。
想想看。thread能孤立自己嗎？
意思就是本身怎麼可能會發生死鎖一定會照順序執行

如果兩個 thread 的  Lock 相同
![](https://i.imgur.com/jEt2wjH.png)
也就是嵌套鎖 想像一個情形 兩個 thread 啟動 只會有一個 thread 得到 x 的鎖，假設其中一個thread 拿到鎖之後沒執行到最後，x 鎖是不會釋放的
那麼x 裡面的鎖絕對可以拿到並且釋放(操作)

![](https://i.imgur.com/XhlIwmW.png)

這邊要想像一下假設 f1 thread 啟動 在裡面 在呼叫 f2 thread2
那麼會不會造成死鎖，基本上 f1 在鎖最後在呼叫 f2基本上 x 跟 y的鎖基本上已經釋放了，所以這種情況也不用納入考慮因為可能隨著時間鎖就釋放掉了

https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwiaxfWBwYfxAhXnDaYKHaSAD4IQFjACegQIBhAE&url=http%3A%2F%2Fswtv.kaist.ac.kr%2Flab-orientation%2Fdeadlock.ppt&usg=AOvVaw1ayvbX0QU1RgnYsZw55Gh_
# 產生 lock tree
![](https://i.imgur.com/VfTSalB.png)

# 舉個三個例子
下面例子都考慮平行的時候
## 搶同一把鎖
![](https://i.imgur.com/ow97iKh.png)
這種情況就是 thread1 啟動 thread1 L3 加鎖
這樣會影響到 thread2 和 thread4 的 L3加鎖嗎
假設 thread1 先啟動基本上l4 做完的當下，l3已經解鎖
那麼 thread2 和 thread4 應該就可以順利拿到鎖
要注意這邊是按照他的路徑走法
規則就是不能訪問每個thread lock tree 相同的 lock (l3)
thread1 l3 啟動拿到鎖
thread2 l3 嘗試拿鎖，等thread1 釋放
thread4 l3 嘗試拿鎖，等thread1 釋放
thread1 l3 thread1 一定會做完，thread 2 和 thread 4 一定有機會拿到鎖。
考慮平行 則 只會有一個 thread 拿到 同一把鎖

所以路徑不合法

## 考慮平行，左右子樹問題
![](https://i.imgur.com/R1pW2Zb.png)
考慮平行
# cycle 1
同時 thread1 啟動 thread1 l1 加鎖成功
thread1 l1 l1 加鎖

同時 thread2 啟動 thread2 l2 加鎖成功
thread2 l2 l2 加鎖

同時 thread3 啟動 thread3 l4 加鎖成功
thread3 l4 l4 加鎖
thread3 l1 l1 等待加鎖
# cycle 2
同時 thread1 啟動 thread1 l1 加鎖成功
thread1 l1 l1 加鎖
thread1 l2 l2 嘗試加鎖l2

同時 thread2 啟動 thread2 l2 加鎖成功
thread2 l2 l2 加鎖
thread2 l2 l3 加鎖

同時 thread3 啟動 thread3 l4 加鎖成功
thread3 l4 l4 加鎖
thread3 l1 l1 等待加鎖
# cycle 3
同時 thread1 啟動 thread1 l1 加鎖成功
thread1 l1 l1 加鎖
thread1 l2 l2 加鎖 <== 加鎖成功

開始做右半邊

同時 thread2 啟動 thread2 l2 加鎖成功
thread2 l2 l2 加鎖
thread2 l2 l3 加鎖
thread2 l2 l3 釋放鎖 <== 釋放

同時 thread3 啟動 thread3 l4 加鎖成功
thread3 l4 l4 加鎖
thread3 l1 l1 等待加鎖
# cycle 3
同時 thread1 啟動 thread1 l1 加鎖成功
thread1 l1 l1 加鎖
thread1 l2 l2 加鎖
thread1 l1 l2 釋放鎖  <== 釋放
開始做右半邊
thread1 l3 l3 加鎖
thread1 l4 l4 嘗試加鎖

同時 thread2 啟動 thread2 l2 加鎖成功
thread2 l2 l2 加鎖
thread2 l2 l3 加鎖
thread2 l2 l3 釋放鎖  <== 釋放

同時 thread3 啟動 thread3 l4 加鎖成功
thread3 l4 l4 加鎖
thread3 l1 l1 加鎖 <== 加鎖成功

# cycle 4
同時 thread1 啟動 thread1 l1 加鎖成功
thread1 l1 l1 加鎖
thread1 l2 l2 加鎖
thread1 l1 l2 釋放鎖  <== 釋放
開始做右半邊
thread1 l3 l3 加鎖
thread1 l4 l4 加鎖

同時 thread2 啟動 thread2 l2 加鎖成功
thread2 l2 l2 加鎖
thread2 l2 l3 加鎖
thread2 l2 l3 釋放鎖  <== 釋放

同時 thread3 啟動 thread3 l4 加鎖成功
thread3 l4 l4 加鎖
thread3 l1 l1 加鎖
thread3 l4 l1 釋放鎖  <== 釋放

# cycle 5
同時 thread1 啟動 thread1 l1 加鎖成功
thread1 l1 l1 加鎖
thread1 l2 l2 加鎖
thread1 l1 l2 釋放鎖  <== 釋放
開始做右半邊
thread1 l3 l3 加鎖
thread1 l4 l4 加鎖
thread1 l3 l4 釋放鎖  <== 釋放

同時 thread2 啟動 thread2 l2 加鎖成功
thread2 l2 l2 加鎖
thread2 l2 l3 加鎖
thread2 l2 l3 釋放鎖  <== 釋放

同時 thread3 啟動 thread3 l4 加鎖成功
thread3 l4 l4 加鎖
thread3 l1 l1 加鎖
thread3 l4 l1 釋放鎖  <== 釋放

上述應該可以隨著時間釋放鎖
thread1  有左右子樹
路徑就不是有效的因為
thread1 執行 l3 l4 是接著 l1 l2繼續執行有可能就是
thread1 這個 thread1 執行完會把 l1 l2 l3 l4 通通解鎖
考慮到平行
thread2 l2 l3 假設 thread1 有可能加鎖解鎖 都沒問題
那麼 thread2 理所當然可以拿到 l2 l3
thread4 也理所當然可以 拿到 l4 l3
這邊 thread2 和 thread4 有沒有問題
thread 2 先做完l2 l3 也 釋放了
thread4 頂多稍微等一下
就可以拿到 l3

inter edges
			bidirectional edges between nodes that are labeled with 		the same locks and that are in different lock trees.
間邊
標有相同鎖且位於不同鎖樹中的節點之間的雙向邊。

For a lock graph G, a valid path is a path that does not contain consecutive inter edges and nodes from each lock tree appear as at most one consecutive subsequence in the path.
A valid cycle is a cycle that does not contain consecutive inter edges and nodes from each thread appear as at most one consecutive subsequence in the cycle.

對於鎖圖 G，有效路徑是不包含連續的間邊的路徑，並且來自每個鎖樹的節點在路徑中最多出現為一個連續的子序列。
有效循環是不包含連續的間邊和來自每個線程的節點的循環，該循環中最多出現一個連續的子序列。

結合我剛剛的想法，有連續間邊應該是 在等同一把鎖
假設在等同一把鎖一次就只有一個 thread 會進去
如果按照他的路徑走可能就會遇到間邊 其他 thread會 去等同一把鎖釋放這樣只有一個 thread 會操作完在繼續往下做，慢慢鎖就解開(?
https://www.jianshu.com/p/ae5a0c995f88
假設以 pthread_mutex 意味著喚醒
那麼考慮平行的時候，其中一個鎖釋放意味著其他 平行的 thread 鎖也會被通知解鎖，死鎖可能會一層一層被解開。
這個例子是連續兩個 間邊 有可能 在第一個間邊釋放某一把鎖也就是他說的
A deadlock may not be revealed depending on a schedule. The classical deadlock detection algorithm can not report unless a deadlock actually occurs.
可能會隨著時間，死鎖會一層一層的解開。
來自同一個thread 兩個或多個連續間邊

所以路徑不合法

## 合法路徑
![](https://i.imgur.com/CU0Tb5W.png)
第三個例子
沒有像第二個例子有在同一個 thread
鎖有可能有順序上的問題
也沒有共同拿同一把鎖的問題

最終情況就是
考慮平行的情況
thread1 l3 和 thread4 l4 同樣的時間啟動都取得鎖
那麼
thread1 l4 和 thread4 l3
thread1 l4 等待 thread4 l4
thread4 l3 等待 thread1 l3
鎖會呈現互相等待的情況(因為事情還沒做完)，但是跟上面那兩種情況來對比
我們的路徑是有效的，因為過濾掉會有自動解鎖的問題
為什麼這個可以呢又是有效的
對於鎖圖 G，有效路徑是不包含連續的間邊的路徑，並且來自每個鎖樹的節點在路徑中
最多出現為一個連續的子序列。<===
有效循環是不包含連續的間邊和來自每個線程的節點的循環，該循環中
最多出現一個連續的子序列。  <===

假設只有一個連續間邊
考慮平行情況
只要不斷的產生 thread 則可能會發生互等資源 (沒有其他例外

跟第二個例子對比
按照例子路徑可能會發生第一個連續間邊競爭某把鎖，當 thread 做完並釋放鎖假設另一個連續間便又來自同一個thread 那麼在後面執行的thread
可能會跟現有的並行，原有thread本身鎖本來就不會發生死鎖
而第二個連續間邊本來會發生死鎖但是第一個連續間邊釋放該鎖，鎖來自於自己，基本上沒有死鎖問題
thread2先搶到做完基本上thread2鎖就都釋放了
假設thread2沒搶到也沒關係l2已經加鎖等待l3
thread1已經搶到l3

連續間邊可能就是再找這些路徑中假設
多個thread都在操作同一個把鎖那麼就可能會出現
只有一個 thread 操作一把鎖其他thread呈現等待，這樣的話可能又回到第一個情形

所以路徑合法

下面來仔細思考為什麼要這麼做

# 同一個thread 加解鎖 導致 死鎖解除?

```c
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
pthread_mutex_t lock1, lock2,lock3,lock4;

void *resource1(){

    pthread_mutex_lock(&lock1);
    //printf("Job started in resource1..\n");
    //<< 這一行我註解因為會導致 thread 2 先搶占
    //假設先被搶佔這個就是死結了
    
    pthread_mutex_lock(&lock2);
    pthread_mutex_unlock(&lock2);
    pthread_mutex_unlock(&lock1);
    printf("Job started lock1 lock2 free..\n");
    pthread_mutex_lock(&lock3);
    pthread_mutex_lock(&lock4);
    pthread_mutex_unlock(&lock4);
    pthread_mutex_unlock(&lock3);

    printf("Job finished in resource1..\n");
    pthread_exit(NULL);

}

void *resource2(){

    pthread_mutex_lock(&lock2);
    printf("Job started in resource2..\n");
    pthread_mutex_lock(&lock1);

    pthread_mutex_unlock(&lock1);
    pthread_mutex_unlock(&lock2);

    printf("Job finished in resource2..\n");
    pthread_exit(NULL);
}
void *resource3(){

    pthread_mutex_lock(&lock4);
    printf("Job started in resource3..\n");
    pthread_mutex_lock(&lock1);
    pthread_mutex_unlock(&lock1);
    pthread_mutex_unlock(&lock4);

    printf("Job finished in resource3..\n");
    pthread_exit(NULL);
}

int main() {

    pthread_mutex_init(&lock1,NULL);
    pthread_mutex_init(&lock2,NULL);
    pthread_mutex_init(&lock3,NULL);
    pthread_mutex_init(&lock4,NULL);
    pthread_t t1,t2,t3;
 //   pthread_create(&t2,NULL,resource2,NULL);
    pthread_create(&t1,NULL,resource1,NULL);
    pthread_create(&t2,NULL,resource2,NULL);
    pthread_create(&t3,NULL,resource3,NULL);
    pthread_join(t1,NULL);
    pthread_join(t2,NULL);
    pthread_join(t3,NULL);

    return 0;

}

```

![](https://i.imgur.com/MLHKvuW.png)
考慮平行重畫
實際上 thread1 左子樹一定會先執行 thread1 右子樹暫時不考慮的話
這邊演算法要過濾的是不合法的路徑
這樣是不會發生死鎖的
![](https://i.imgur.com/Tbh13Sx.png)

![](https://i.imgur.com/14INmON.png)
等效
![](https://i.imgur.com/nY5Sbvk.png)

# 過濾連續間邊
有連續間邊 意味著平行執行 會有可能拿對方資源
考慮在平行執行的話
>只有一個連續間邊的話意味著
thread 裡面的 鎖 可能其他 thread 也會嘗試取得(可能你這條路徑
在嵌套鎖裡面，你裡面的鎖要釋放完畢，上一層的鎖才能釋放
所以到達最終過濾不能排除這個可能性

>多個連續間邊意味著
同一個時間會有多個 thread執行 只有一個 thread 會取得鎖，這邊演算法要過濾的是這種不合法的路徑

# 最終過濾
最後剩下來的合法路徑 在沒有其他因素干擾下，滿足上述的條件
這些路徑內又是一個環則判斷為死結
那麼判定 thread1 後半段 l3 和 l4
跟 thread4 l4 l3 有可能會發生死鎖
![](https://i.imgur.com/CU0Tb5W.png)

http://www.csie.ntnu.edu.tw/~swanky/os/chap5.htm

有可能 ppt 是想表達這些意思，日後靜態分析 pthread 死結會用到

