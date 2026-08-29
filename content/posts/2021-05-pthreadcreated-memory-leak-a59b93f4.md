---
title: "pthread_created 追蹤 與防止 memory leak"
date: "2021-05-10T17:36:00.001+08:00"
updated: "2021-05-10T17:36:31.948+08:00"
permalink: "/2021/05/pthreadcreated-memory-leak.html"
original_url: "https://x8795278.blogspot.com/2021/05/pthreadcreated-memory-leak.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-1561202750184151932"
tags: ["pthread"]
layout: post
---

![](https://i.imgur.com/Qu4HrMV.png)

# pthread_created
![](https://i.imgur.com/RAZHFBS.png)

pthread_created 會發生 memory leak 的情況來探討
追程式碼
https://blog.csdn.net/hnwyllmm/article/details/45749063
這邊大部分解說的情況確實是正確的
我這邊再把他稍微精簡一下
https://blog.csdn.net/David_xtd/article/details/16840371
這篇文章有大概抽出片段但是我覺得還是少了某些部分
https://code.woboq.org/userspace/glibc/nptl/pthread_create.c.html

# struct pthread
這邊要注意的是 joinid 假設本身等於自己的 tid 則就是
detach 也就是 thread 與 process 分離
```c
struct pthread
{
    union
    {
#if !TLS_DTV_AT_TP
        tcbhead_t header;       /* TLS 使用的TCB，不包含线程 */
        struct
        {
            /* 
            当进程产生了至少一个线程或一个单线程的进程取消本身时
            启用multiple_threads。这样就允许在做一些compare_and_exchange
            操作之前添加一些额外的代码来引入锁,也可以开启取消点(cancellation point)。
            多个线程的概念和取消点的概念是分开的,因为没有必要为取消
            点设计成多线程,就跟单线程进程取消本身一样。
            因为开启多线程就允许在取消点和compare_and_exchange操作中
            添加一些额外的代码，这样的话对于一个单线程、自取消(self-canceling)
            的进程可能会有不必要的性能影响。但是这样也没问题，因为
            仅当它要取消自己并且要结束的时候，一个单线程的进程会开启
            异步取消
            */
            int multiple_threads;
            int gscope_flag;
# ifndef __ASSUME_PRIVATE_FUTEX
            int private_futex;
# endif
        } header;
#endif
        void *__padding[24];
    };

    list_t list;    // `stack_used' 或 `__stack_user' 链表节点
    pid_t tid;      // 线程ID，也是线程描述符
    pid_t pid;      // 进程ID，线程组ID

    // 进程当前持有的robust mutex
#ifdef __PTHREAD_MUTEX_HAVE_PREV
    void *robust_prev;
    struct robust_list_head robust_head;

    /* The list above is strange.   It is basically a double linked list
         but the pointer to the next/previous element of the list points
         in the middle of the object, the __next element.   Whenever
         casting to __pthread_list_t we need to adjust the pointer
         first. */

#else
    union
    {
        __pthread_slist_t robust_list;
        struct robust_list_head robust_head;
    };

#endif

    struct _pthread_cleanup_buffer *cleanup;    // cleanup缓存链表
    struct pthread_unwind_buf *cleanup_jmp_buf; // unwind信息
    int cancelhandling;                         // 判断处理取消的标识
    int flags;                                  // 标识. 包含从线程属性中复制的信息

    // 这里分配一个块. 对大多数应用程序应该能够尽量避免动态分配内存
    struct pthread_key_data
    {
        uintptr_t seq;                          // 序列号
        void *data;                             // 数据指针
    } specific_1stblock[PTHREAD_KEY_2NDLEVEL_SIZE];

    // 存放线程特有数据的二维数组
    // 第1个元素就是specific_1stblock
    struct pthread_key_data *specific[PTHREAD_KEY_1STLEVEL_SIZE];
    bool specific_used;                         // 标识符：是否使用特定(specific)数据(TLS)
    bool report_events;                         // 是否要汇报事件
    bool user_stack;                            // 是否用户提供栈
    bool stopped_start;                         // 启动的时候线程是否应该是停止状态

    // pthread_create执行的时候，parent的取消处理器。当需要取消的时候才用到
    int parent_cancelhandling;
    int lock;                                   // 同步访问的锁
    int setxid_futex;                           // setxid调用的同步锁

#if HP_TIMING_AVAIL
    /* Offset of the CPU clock at start thread start time.  */
    hp_timing_t cpuclock_offset;
#endif

    // 如果线程等待关联另一个线程ID, 就将那个线程的ID放在这里
    // 如果一个线程状态是detached，这里就存放它自己. 
    struct pthread *joinid;                     // 如果joinid是线程本身，就说明这个线程是detached状态
    void *result;                               // 线程函数执行的结果

    // 新线程的调度参数
    struct sched_param schedparam;              // 只有一个成员： int __sched_priority
    int schedpolicy;

    // 执行函数的地址和参数
    void *(*start_routine) (void *);
    void *arg;

    td_eventbuf_t eventbuf;                     // 调试状态
    struct pthread *nextevent;                  // 下一个有pending事件的描述符，应该是用来调试的

#ifdef HAVE_FORCED_UNWIND
    struct _Unwind_Exception exc;               // 与平台相关的unwind信息
#endif

    // 如果是非0，指栈上分配的区域和大小
    void *stackblock;
    size_t stackblock_size;

    size_t guardsize;                           // 保护区域的大小
    size_t reported_guardsize;                  // 用户指定的并且展示的保护区大小(就是通过接口获取保护区大小时，返回这个数字)
    struct priority_protection_data *tpp;       // 线程有限保护数据

    /* Resolver state.  */
    struct __res_state res;

    char end_padding[];

} __attribute ((aligned (TCB_ALIGNMENT)));

```
# glibc/nptl/pthread_create.c

```c
__pthread_create_2_1 (pthread_t *newthread, const pthread_attr_t *attr,
                      void *(*start_routine) (void *), void *arg)
        //這邊可以看到其實就是我們在撰寫程式碼的地方
        //會把 Process 的 fucntion 和要傳遞的變數強轉傳過來這邊
        //這邊再透過 struct pd 重新封裝 
struct pthread *pd = NULL;
  int err = ALLOCATE_STACK (iattr, &pd);
  int retval = 0;
  if (__glibc_unlikely (err != 0))
    /* Something went wrong.  Maybe a parameter of the attributes is
       invalid or we could not allocate memory.  Note we have to
       translate error codes.  */
    {
      retval = err == ENOMEM ? EAGAIN : err;
      goto out;
    }
  /* Initialize the TCB.  All initializations with zero should be
     performed in 'get_cached_stack'.  This way we avoid doing this if
     the stack freshly allocated with 'mmap'.  */
#if TLS_TCB_AT_TP

  /* Reference to the TCB itself.  */
  pd->header.self = pd;
  /* Self-reference for TLS.  */
  pd->header.tcb = pd;
#endif
  /* Store the address of the start routine and the parameter.  Since
     we do not start the function directly the stillborn thread will
     get the information from its thread descriptor.  */
     //這邊再透過 struct pd 傳入 start_rountine 和 arg
  pd->start_routine = start_routine;
  pd->arg = arg;
  pd->c11 = c11;
  
```
從這邊開始追是比較快的
# glibc/sysdeps/unix/sysv/linux/createthread.c
![](https://i.imgur.com/yyrou2j.png)
https://code.woboq.org/userspace/glibc/sysdeps/unix/sysv/linux/createthread.c.html#create_thread
他底層還是寫system call 去呼叫 clone
https://www.itread01.com/content/1549702822.html

https://blog.xuite.net/ian11832/blogg/23967641

| function  | characteristic | supplement |
| -------- | -------- | -------- |
| fork(無參數)     | 完全複製父行程的資源，子行程獨立於父行程， 但是二者之間的通訊需要通過專門的通訊機制如：pipe，popen&pclose、協同進程、fifo，System V IPC（消息隊列、信號量和共享內存）機制等。     |Linux中採取了copy-on-write技術減少無用複製。fork的父子行程運行順序是不定的，它取決於排程演算法。    |
| vfork(無參數) | 父子行程共享位址空間，也就是說子行程完全運行在父行程的位址空間上，子行程對虛擬位址空間任何數據的修改同樣為父行程所見。但是用 vfork創建子行程後，父行程會被block住直到子行程調用exec或exit。 | vfork主要是用在創建出來的子行程馬上又呼叫execve的情況下 vfork保證子行程先運行，在它調用exec或exit後父行程才可能排程運行。當子行程exec另一新程式時，即會給予新空間而不再佔用父行程空間 |
| clone(有參數) | 	按指定條件創建子行程，可決定哪些父子資源要共享，哪些要額外複製一份。 |  由POSIX支援的C函式pthread_create()函式呼叫？？ |

![](https://i.imgur.com/4xKlDHB.png)

```c

  if (__glibc_unlikely (ARCH_CLONE (&start_thread, STACK_VARIABLES_ARGS,
                                    clone_flags, pd, &pd->tid, tp, &pd->tid)
                        == -1))
```

![](https://i.imgur.com/wVc2LLl.png)
這邊會去呼叫 start_thread
```c
#define START_THREAD_DEFN \
  static int __attribute__ ((noreturn)) start_thread (void *arg)
#define START_THREAD_SELF arg
這邊又去定義start_thread
```
# start_thread
https://code.woboq.org/userspace/glibc/nptl/pthread_create.c.html#378
可以發現一直到結束 除非你一開始有設定 ATTR 去設定 THREAD 的屬性為DETACHED ,否則的話一般就會直接走到 RETURN，一般THREAD 預設 JOINABLE，這也就是為什麼 PTHREAD CREATED 會卡資源因為沒有釋放的緣故
```c
這邊查閱THREAD_SETMEM  大概是類斯
      /* Run the code the user provided.  */
      void *ret;
      if (pd->c11)
        {
          /* The function pointer of the c11 thread start is cast to an incorrect
             type on __pthread_create_2_1 call, however it is casted back to correct
             one so the call behavior is well-defined (it is assumed that pointers
             to void are able to represent all values of int.  */
          int (*start)(void*) = (int (*) (void*)) pd->start_routine;
          ret = (void*) (uintptr_t) start (pd->arg);
        }
      else
        ret = pd->start_routine (pd->arg);
      THREAD_SETMEM (pd, result, ret);
    }
    ///等待一個 THREAD 結束
    ........
    .
    .
    .
    
    stack_range (pd->stackblock, pd->stackblock_size, (uintptr_t) pd,
                      pd->guardsize);
//關注我
  /* If the thread is detached free the TCB.  */
  if (IS_DETACHED (pd))
    /* Free the TCB.  */
    __free_tcb (pd);
```

# THREAD_SETMEM
這邊可以看到他嘗試去存取 pthread struct 結構某一個部分
https://code.woboq.org/userspace/glibc/sysdeps/x86_64/nptl/tls.h.html#261
```c
/* Set member of the thread descriptor directly.  */
# define THREAD_SETMEM(descr, member, value) \
  ({ if (sizeof (descr->member) == 1)                                              \
       asm volatile ("movb %b0,%%fs:%P1" :                                      \
                     : "iq" (value),                                              \
                       "i" (offsetof (struct pthread, member)));              \
     else if (sizeof (descr->member) == 4)                                      \
       asm volatile ("movl %0,%%fs:%P1" :                                      \
                     : IMM_MODE (value),                                      \
                       "i" (offsetof (struct pthread, member)));              \
     else                                                                      \
       {                                                                      \
         if (sizeof (descr->member) != 8)                                      \
           /* There should not be any value with a size other than 1,              \
              4 or 8.  */                                                      \
           abort ();                                                              \
                                                                              \
         asm volatile ("movq %q0,%%fs:%P1" :                                      \
                       : IMM_MODE ((uint64_t) cast_to_integer (value)),              \
                         "i" (offsetof (struct pthread, member)));              \
       }})

```
仔細觀察  ret = pd->start_routine (pd->arg);
可以發現他是透過 我們在 created_thread 那邊又把 pd 結構裡面預存的 從 process function 和 參數 又重新呼叫一遍
所以 就是 clone process 一部分的 resource 去呼叫

到目前為止
要完全釋放佔有的資源就是預設 ATTR 為 DETACH
有沒有其他方式呢，還有一種方式是在 CREATED出來的 THREAD
開頭加入
  pthread_detach(pthread_self());
我們來研究一下他的原理
# pthread_detach(npth/pthread_detach.c)
https://code.woboq.org/userspace/glibc/nptl/pthread_detach.c.html

```c
int
__pthread_detach (pthread_t th)
{
  struct pthread *pd = (struct pthread *) th;
  /* Make sure the descriptor is valid.  */
  if (INVALID_NOT_TERMINATED_TD_P (pd))
    /* Not a valid thread handle.  */
    return ESRCH;
  int result = 0;
  /* Mark the thread as detached.  */
  if (atomic_compare_and_exchange_bool_acq (&pd->joinid, pd, NULL))
    {
      /* There are two possibilities here.  First, the thread might
         already be detached.  In this case we return EINVAL.
         Otherwise there might already be a waiter.  The standard does
         not mention what happens in this case.  */
      if (IS_DETACHED (pd))
        result = EINVAL;
    }
  else
    /* Check whether the thread terminated meanwhile.  In this case we
       will just free the TCB.  */
    if ((pd->cancelhandling & EXITING_BITMASK) != 0)
      /* Note that the code in __free_tcb makes sure each thread
         control block is freed only once.  */
      __free_tcb (pd);
  return result;
}
weak_alias (__pthread_detach, pthread_detach)
```
可以看到他註解寫的 mark thread 為 detach
繼續追蹤atomic_compare_and_exchange_bool_acq
# atomic_compare_and_exchange_bool_acq
https://code.woboq.org/userspace/glibc/sysdeps/x86/atomic-machine.h.html#79
又是一個define 可以查閱
> __sync_bool_compare_and_swap

https://zhuanlan.zhihu.com/p/32303037
```c
#define atomic_compare_and_exchange_bool_acq(mem, newval, oldval) \
  (! __sync_bool_compare_and_swap (mem, oldval, newval))
```
這邊要注意 newval 和 oldval 他的順序調換過來了
__sync_bool_compare_and_swap 也就是cas 樂觀鎖的概念
他預設就是在異動value 的時候 沒有 thread 會存取這個 value
(就是類似資料庫某些 data version 假設版本號不相同是不能異動這裡面目前的資料，能確保併發安全性，但是確保併發資料的順序性
這邊就是假設mem 裡面的 data 等於 null 則把自己的 newval 複製到 mem
然後回傳 false
反之
假設 不等於則return true 回到pthread_detach
也就是

```c
     /* There are two possibilities here.  First, the thread might
         already be detached.  In this case we return EINVAL.
         Otherwise there might already be a waiter.  The standard does
         not mention what happens in this case.  */
      if (IS_DETACHED (pd))
        result = EINVAL;
```

結合上面的 joinid來看 假設 joinid 等於 自己則就是DETACHED
也就是 process 與 thread 分離 thread 結束後馬上會釋放資源

# IS_DETACHED
https://code.woboq.org/userspace/glibc/nptl/descr.h.html#357
```c
  struct pthread *joinid;
  /* Check whether a thread is detached.  */
#define IS_DETACHED(pd) ((pd)->joinid == (pd))
```
到這邊就大概可以知道假設
thread 額外去呼叫  pthread_detach(pthread_self());
我們考慮到start_thread 那邊就是自己再去call 自己
```c
      ret = pd->start_routine (pd->arg);
      THREAD_SETMEM (pd, result, ret);
```
因為thread 預設是 joinable
```c
在上面 struct pthread 介紹有說到
    // 如果线程等待关联另一个线程ID, 就将那个线程的ID放在这里
    // 如果一个线程状态是detached，这里就存放它自己. 
    struct pthread *joinid;                     // 如果joinid是线程本身，就说明这个线程是detached状态
```
就是說 假設是 joinable 預設的 join 就是 null
```c
    // 如果是detached状态，joined就设置为自己本身
    pd->joinid = iattr->flags & ATTR_FLAG_DETACHSTATE ? pd : NULL;
```
得以知道 假設都沒設置任何 thread 屬性則可以再透過這個方式重新定義thread 為 detach 這樣在 start_thread 那邊呼叫完他就會銜接判斷這個pd 結構是否屬性為thread 為 detach 進而釋放

# pthread_join(glibc/nptl/pthread_join_common.c)
https://code.woboq.org/userspace/glibc/nptl/pthread_join_common.c.html#__pthread_timedjoin_ex
再來看 pthread_join
```c
int __pthread_timedjoin_ex (pthread_t threadid, void **thread_return,
                        const struct timespec *abstime, bool block)
{
  struct pthread *pd = (struct pthread *) threadid;
  /* Make sure the descriptor is valid.  */
  if (INVALID_NOT_TERMINATED_TD_P (pd))
    /* Not a valid thread handle.  */
    return ESRCH;
  /* Is the thread joinable?.  */
  if (IS_DETACHED (pd))
    /* We cannot wait for the thread.  */
    return EINVAL;
  struct pthread *self = THREAD_SELF;
  int result = 0;
  LIBC_PROBE (pthread_join, 1, threadid);
  if ((pd == self
       || (self->joinid == pd
           && (pd->cancelhandling
               & (CANCELING_BITMASK | CANCELED_BITMASK | EXITING_BITMASK
                  | TERMINATED_BITMASK)) == 0))
      && !CANCEL_ENABLED_AND_CANCELED (self->cancelhandling))
    /* This is a deadlock situation.  The threads are waiting for each
       other to finish.  Note that this is a "may" error.  To be 100%
       sure we catch this error we would have to lock the data
       structures but it is not necessary.  In the unlikely case that
       two threads are really caught in this situation they will
       deadlock.  It is the programmer's problem to figure this
       out.  */
    return EDEADLK;
  /* Wait for the thread to finish.  If it is already locked something
     is wrong.  There can only be one waiter.  */
  else if (__glibc_unlikely (atomic_compare_exchange_weak_acquire (&pd->joinid,
                                                                   &self,
                                                                   NULL)))
    /* There is already somebody waiting for the thread.  */
    return EINVAL;
  /* BLOCK waits either indefinitely or based on an absolute time.  POSIX also
     states a cancellation point shall occur for pthread_join, and we use the
     same rationale for posix_timedjoin_np.  Both timedwait_tid and the futex
     call use the cancellable variant.  */
  if (block)
    {
      /* During the wait we change to asynchronous cancellation.  If we
         are cancelled the thread we are waiting for must be marked as
         un-wait-ed for again.  */
      pthread_cleanup_push (cleanup, &pd->joinid);
      if (abstime != NULL)
        result = timedwait_tid (&pd->tid, abstime);
      else
        {
          pid_t tid;
          /* We need acquire MO here so that we synchronize with the
             kernel's store to 0 when the clone terminates. (see above)  */
          while ((tid = atomic_load_acquire (&pd->tid)) != 0)
            lll_futex_wait_cancel (&pd->tid, tid, LLL_SHARED);
        }
      pthread_cleanup_pop (0);
    }
  void *pd_result = pd->result;
  if (__glibc_likely (result == 0))
    {
      /* We mark the thread as terminated and as joined.  */
      pd->tid = -1;
      /* Store the return value if the caller is interested.  */
      if (thread_return != NULL)
        *thread_return = pd_result;
      /* Free the TCB.  */
      __free_tcb (pd);
    }
  else
    pd->joinid = NULL;
  LIBC_PROBE (pthread_join_ret, 3, threadid, result, pd_result);
  return result;
}
```
關注這邊可以看到
__glibc_likely 和 __builtin_expect (result == 0, 1)
是一樣的
__glibc_unlikely 和 __builtin_expect (result == 0, 0)
這段意思就是說假設他判斷某些 value 是符合某些狀況，這邊就可以提前預測他下一個部分有很大的機率走向哪一個分支，進而讓程式更加有效率

這邊假設又是 joinable 則
可以看到__pthread_exit 其實也可以設置其他回傳值
https://code.woboq.org/userspace/glibc/nptl/pthread_exit.c.html
```c

void
__pthread_exit (void *value)
{
  THREAD_SETMEM (THREAD_SELF, result, value);
  __do_cancel ();
}
weak_alias (__pthread_exit, pthread_exit)

```

```c
//... 這邊又看到預設 result = 0
  struct pthread *self = THREAD_SELF;
  int result = 0;
  
   LIBC_PROBE (pthread_join, 1, threadid);
  if ((pd == self
       || (self->joinid == pd
           && (pd->cancelhandling
               & (CANCELING_BITMASK | CANCELED_BITMASK | EXITING_BITMASK
                  | TERMINATED_BITMASK)) == 0))
      && !CANCEL_ENABLED_AND_CANCELED (self->cancelhandling))
    /* This is a deadlock situation.  The threads are waiting for each
       other to finish.  Note that this is a "may" error.  To be 100%
       sure we catch this error we would have to lock the data
       structures but it is not necessary.  In the unlikely case that
       two threads are really caught in this situation they will
       deadlock.  It is the programmer's problem to figure this
       out.  */
    return EDEADLK;
  /* Wait for the thread to finish.  If it is already locked something
     is wrong.  There can only be one waiter.  */
  else if (__glibc_unlikely (atomic_compare_exchange_weak_acquire (&pd->joinid,
                                                                   &self,
                                                                   NULL)))
    /* There is already somebody waiting for the thread.  */
    return EINVAL;
    
    可以看到遇到奇奇怪怪的狀態就會回復這些狀態值
    EDEADLK EINVAL .. 有關 linux kernel 錯誤狀態碼
```
[ include/asm-generic/errno.h ]( https://code.woboq.org/gcc/include/asm-generic/errno.h.html)

# join會等待資源被銷毀在這裡也就是阻塞的原因
```c
       /* We need acquire MO here so that we synchronize with the
             kernel's store to 0 when the clone terminates. (see above)  */
          while ((tid = atomic_load_acquire (&pd->tid)) != 0)
            lll_futex_wait_cancel (&pd->tid, tid,
```
我覺得這邊再等 start_thread 裡面的訊號發出
```c

    // 不能调用'_exit'. '_exit'会终止进程.
    // 因为'clone'函数设置了参数CLONE_CHILD_CLEARTID标志位, 在进程真正的结束后,
    // 内核中实现的'exit'会发送信号.
    // TCB中的'tid'字段会设置成0

    // 退出代码是0，以防所有线程调用'pthread_exit'退出
    __exit_thread ();

    return 0;
}

```
持續等待內部中斷的 system call
```c
static inline void __attribute__ ((noreturn, always_inline, unused))
__exit_thread (void)
{
  /* Doing this in a loop is mostly just to satisfy the compiler that the
     function really qualifies as noreturn.  It also means that in some
     pathological situation where the system call does not get made or does
     not work, the thread will simply spin rather than running off the end
     of the caller and doing unexpectedly strange things.  */
  while (1)
    {
      INTERNAL_SYSCALL_DECL (err);
      INTERNAL_SYSCALL (exit, err, 1, 0);
    }
}
```
所以我們可以在process 去等到 kernel 去把 tid 設為0代表
clone 已經執行完並且沒問題。這時候 pthread_join 就可以往下走

可以發現判斷式
假設有很大的機率result == 0，也就是沒發生什麼異常的中斷就釋放記憶體

```c
  void *pd_result = pd->result;
  if (__glibc_likely (result == 0))
    {
      /* We mark the thread as terminated and as joined.  */
      pd->tid = -1;
      /* Store the return value if the caller is interested.  */
      if (thread_return != NULL)

      //丟還給  pthread_join(t1, 我目前這個地方);
      //可以發現
        *thread_return = pd_result;
      /* Free the TCB.  */
      __free_tcb (pd);
    }
      else
    pd->joinid = NULL;
  LIBC_PROBE (pthread_join_ret, 3, threadid, result, pd_result);
  return result;
```
# kernel 處理 thread exit
這邊去看kernel 收到 thread 離開會做什麼事情
https://docs.ioin.in/writeup/v-v.mom/_2016_06_25_kernel_ds_rw_/index.html

https://code.woboq.org/linux/linux/kernel/fork.c.html#mm_release
退出流程

当fork或clone一个进程的时候，会调用copy_process函数:

```c

task_struct *copy_process(...){
  ...
  p->clear_child_tid = (clone_flags & CLONE_CHILD_CLEARTID) ? child_tidptr: NULL;
}
```
如果设置了CLONE_CHILD_CLEARTID标志，就会将child_tidptr赋值给clear_child_tid,而child_tidptr来自用户空间，可以受用户控制，意味着我们可以指向内核地址.

下面这个是clone的函数原型,ctid就是child_tidptr指针

```c

int clone(int (*fn)(void *), void *child_stack,
                 int flags, void *arg, ...
                 /* pid_t *ptid, struct user_desc *tls, pid_t *ctid */ );
                 }
```
CLONE_CHILD_CLEARTID (since Linux 2.5.49)
在线程退出的时候清除子线程的ctid执行的地址，并唤醒该地址的futex.

当一个线程退出的时候,do_exit()会执行如下操作：
```c
NORET_TYPE void do_exit(long code){
  exit_mm(tsk);
}
static void exit_mm(struct task_struct * tsk){
  struct mm_struct *mm = tsk->mm;
  struct core_state *core_state;
  mm_release(tsk, mm);
}

void mm_release(struct task_struct *tsk, struct mm_struct *mm){
  if (tsk->clear_child_tid) {
    if (!(tsk->flags & PF_SIGNALED) &&atomic_read(&mm->mm_users) > 1) {
      put_user(0, tsk->clear_child_tid);  <<---這個就是把 tid 清空為0
      sys_futex(tsk->clear_child_tid, FUTEX_WAKE,1,NULL, NULL, 0);
    }
  tsk->clear_child_tid = NULL;
  }
}
```
上面是網站所寫的精簡版
# do_group_exit()
https://code.woboq.org/linux/linux/kernel/exit.c.html#do_group_exit
我們來看真的kernel 是否這樣寫
當發生 thread 銷毀時會call do_group_exit
```c
/*
 * Take down every thread in the group.  This is called by fatal signals
 * as well as by sys_exit_group (below).
 */
void
do_group_exit(int exit_code)
{
	struct signal_struct *sig = current->signal;
	BUG_ON(exit_code & 0x80); /* core dumps don't get here */
	if (signal_group_exit(sig))
		exit_code = sig->group_exit_code;
	else if (!thread_group_empty(current)) {
		struct sighand_struct *const sighand = current->sighand;
		spin_lock_irq(&sighand->siglock);
		if (signal_group_exit(sig))
			/* Another thread got here before we took the lock.  */
			exit_code = sig->group_exit_code;
		else {
			sig->group_exit_code = exit_code;
			sig->flags = SIGNAL_GROUP_EXIT;
			zap_other_threads(current);
		}
		spin_unlock_irq(&sighand->siglock);
	}
	do_exit(exit_code);
	/* NOTREACHED */
}
# void __noreturn do_exit(long code)
```
# do_exit()
https://code.woboq.org/linux/linux/kernel/exit.c.html#do_exit
```c
void __noreturn do_exit(long code)
{
	struct task_struct *tsk = current;
	int group_dead;
	profile_task_exit(tsk);
	kcov_task_exit(tsk);
	WARN_ON(blk_needs_flush_plug(tsk));
	if (unlikely(in_interrupt()))
		panic("Aiee, killing interrupt handler!");
	if (unlikely(!tsk->pid))
		panic("Attempted to kill the idle task!");
	/*
	 * If do_exit is called because this processes oopsed, it's possible
	 * that get_fs() was left as KERNEL_DS, so reset it to USER_DS before
	 * continuing. Amongst other possible reasons, this is to prevent
	 * mm_release()->clear_child_tid() from writing to a user-controlled
	 * kernel address.
	 */
	set_fs(USER_DS);
	ptrace_event(PTRACE_EVENT_EXIT, code);
	validate_creds_for_do_exit(tsk);
	/*
	 * We're taking recursive faults here in do_exit. Safest is to just
	 * leave this task alone and wait for reboot.
	 */
	if (unlikely(tsk->flags & PF_EXITING)) {
		pr_alert("Fixing recursive fault but reboot is needed!\n");
		/*
		 * We can do this unlocked here. The futex code uses
		 * this flag just to verify whether the pi state
		 * cleanup has been done or not. In the worst case it
		 * loops once more. We pretend that the cleanup was
		 * done as there is no way to return. Either the
		 * OWNER_DIED bit is set by now or we push the blocked
		 * task into the wait for ever nirwana as well.
		 */
		tsk->flags |= PF_EXITPIDONE;
		set_current_state(TASK_UNINTERRUPTIBLE);
		schedule();
	}
	exit_signals(tsk);  /* sets PF_EXITING */
	/*
	 * Ensure that all new tsk->pi_lock acquisitions must observe
	 * PF_EXITING. Serializes against futex.c:attach_to_pi_owner().
	 */
	smp_mb();
	/*
	 * Ensure that we must observe the pi_state in exit_mm() ->
	 * mm_release() -> exit_pi_state_list().
	 */
	raw_spin_lock_irq(&tsk->pi_lock);
	raw_spin_unlock_irq(&tsk->pi_lock);
	if (unlikely(in_atomic())) {
		pr_info("note: %s[%d] exited with preempt_count %d\n",
			current->comm, task_pid_nr(current),
			preempt_count());
		preempt_count_set(PREEMPT_ENABLED);
	}
	/* sync mm's RSS info before statistics gathering */
	if (tsk->mm)
		sync_mm_rss(tsk->mm);
	acct_update_integrals(tsk);
	group_dead = atomic_dec_and_test(&tsk->signal->live);
	if (group_dead) {
#ifdef CONFIG_POSIX_TIMERS
		hrtimer_cancel(&tsk->signal->real_timer);
		exit_itimers(tsk->signal);
#endif
		if (tsk->mm)
			setmax_mm_hiwater_rss(&tsk->signal->maxrss, tsk->mm);
	}
	acct_collect(code, group_dead);
	if (group_dead)
		tty_audit_exit();
	audit_free(tsk);
	tsk->exit_code = code;
	taskstats_exit(tsk, group_dead);
	exit_mm(); <=====就是我
    
```

# exit_mm
https://code.woboq.org/linux/linux/kernel/exit.c.html#exit_mm
```c
/*
 * Turn us into a lazy TLB process if we
 * aren't already..
 */
static void exit_mm(void)
{
	struct mm_struct *mm = current->mm;
	struct core_state *core_state;
	mm_release(current, mm);
```

# void mm_release(struct task_struct *tsk, struct mm_struct *mm)
https://code.woboq.org/linux/linux/kernel/fork.c.html#mm_release
```c
void mm_release(struct task_struct *tsk, struct mm_struct *mm)
{
	/* Get rid of any futexes when releasing the mm */
#ifdef CONFIG_FUTEX
	if (unlikely(tsk->robust_list)) {
		exit_robust_list(tsk);
		tsk->robust_list = NULL;
	}
#ifdef CONFIG_COMPAT
	if (unlikely(tsk->compat_robust_list)) {
		compat_exit_robust_list(tsk);
		tsk->compat_robust_list = NULL;
	}
#endif
	if (unlikely(!list_empty(&tsk->pi_state_list)))
		exit_pi_state_list(tsk);
#endif
	uprobe_free_utask(tsk);
	/* Get rid of any cached register state */
	deactivate_mm(tsk, mm);
	/*
	 * Signal userspace if we're not exiting with a core dump
	 * because we want to leave the value intact for debugging
	 * purposes.
	 */
	if (tsk->clear_child_tid) {
		if (!(tsk->signal->flags & SIGNAL_GROUP_COREDUMP) &&
		    atomic_read(&mm->mm_users) > 1) {
			/*
			 * We don't check the error code - if userspace has
			 * not set up a proper pointer then tough luck.
			 */
			put_user(0, tsk->clear_child_tid);
```

到此就知道thread 結束時 kernel 會怎樣處理我們的 tid
也就是put_user(0, tsk->clear_child_tid); 把tid清為0

回到我們剛剛說的 也就是pthread_join 的部分
等待資源被銷毀在這裡也就是阻塞的原因
然後假設沒有發生任何其他的錯誤狀態的話
result 會維持 0 所以pthread_join 就是會等到一個 thread，真正結束後 kernel 把 tid 設為0 這一塊地資源 才可以被回收，這一段時間也就是阻塞的時間。

# 所以要預防 pthred_create 避免發生memory leak 狀況有三種

## 創造 detachd 屬性的 thread
```c
void run() { 
    return;
} 
                                                                                                       
int main(){ 
    pthread_t thread; 
    pthread_attr_t attr; 
    pthread_attr_init( &attr ); 
    pthread_attr_setdetachstate(&attr,1); 
    pthread_create(&thread, &attr, run, 0); 
          
    //...... 
    return 0; 
}
```

## 在thread  start_routine 之前 把我們的 thread 標註為 detached
```c
void run() { 
    pthread_detach(pthread_self()); 
}                                            

int main(){ 
    pthread_t thread;  
    pthread_create(&thread, NULL, run, 0); 
              
    //...... 
    return 0; 
}
```
## process 採用 pthread_join 但是有阻塞的問題
不用就會發生資源無法回收，因為thread 預設是 joinable
```c
void run() { 
    return;
} 
                                                                                                       
int main(){ 
    pthread_t thread; 
    pthread_create(&thread, NULL, run, 0);  
                                       
    //...... 
    pthread_join(thread,NULL);
    return 0; 
}
```

