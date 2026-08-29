---
title: "linux namespace 實現小型container"
date: "2022-01-16T13:42:00.002+08:00"
updated: "2022-01-16T13:42:39.166+08:00"
permalink: "/2022/01/linux-namespace-container.html"
original_url: "https://x8795278.blogspot.com/2022/01/linux-namespace-container.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-1377606161205215406"
tags: []
layout: post
---

![](https://modugo.com/wp-content/uploads/2021/05/Container-10-foot_side-Measure.png)

# mini-docker
最近看到docker 又看到了podman
突然想了解一下容器底層到底如何實現，整體步驟參考
[https://coolshell.cn/articles/17010.html](https://coolshell.cn/articles/17010.html)
還蠻清晰的，透過linux namespace最後可以看到用簡單的c語言就可以實現一個container 概念
```c
#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/wait.h>
#include <stdio.h>
#include <sched.h>
#include <signal.h>
#include <unistd.h>

/* 定义一个给 clone 用的栈，栈大小1M */
#define STACK_SIZE (1024 * 1024)
static char container_stack[STACK_SIZE];
char *const container_args[] = {
    "/bin/bash",
    NULL};
char *const container_args2[] = {
    "/usr/sbin/chroot",
    NULL};
int pipefd[2];
void set_map(char *file, int inside_id, int outside_id, int len)
{
    FILE *mapfd = fopen(file, "w");
    if (NULL == mapfd)
    {
        perror("open file error");
        return;
    }
    fprintf(mapfd, "%d %d %d", inside_id, outside_id, len);
    fclose(mapfd);
}
void set_uid_map(pid_t pid, int inside_id, int outside_id, int len)
{
    char file[256];
    sprintf(file, "/proc/%d/uid_map", pid);
    set_map(file, inside_id, outside_id, len);
}
void set_gid_map(pid_t pid, int inside_id, int outside_id, int len)
{
    char file[256];
    sprintf(file, "/proc/%d/gid_map", pid);
    set_map(file, inside_id, outside_id, len);
}

int container_main(void *arg)
{
    printf("Container [%5d] - inside the container!\n", getpid());
    printf("Container: eUID = %ld;  eGID = %ld, UID=%ld, GID=%ld\n",
           (long)geteuid(), (long)getegid(), (long)getuid(), (long)getgid());
    /* 等待父进程通知后再往下执行（进程间的同步） */
    char ch;

    close(pipefd[1]);

    read(pipefd[0], &ch, 1);

    printf("Container [%5d] - setup hostname!\n", getpid());
    sethostname("container", 10);
    if (chdir("./rootfs") != 0 || chroot("./") != 0)
    {
        perror("chdir/chroot");
    }
 

    mount("proc", "/proc", "proc", 0, NULL);

    execv(container_args[0], container_args);

    printf("Something's wrong!\n");
    return 1;
}
int main()
{
    const int gid = getgid(), uid = getuid();
    printf("Parent: eUID = %ld;  eGID = %ld, UID=%ld, GID=%ld\n",
           (long)geteuid(), (long)getegid(), (long)getuid(), (long)getgid());
    pipe(pipefd);

    printf("Parent [%5d] - start a container!\n", getpid());

    /* 启用Mount Namespace - 增加CLONE_NEWNS参数 */
    int container_pid = clone(container_main, container_stack + STACK_SIZE,
                            CLONE_NEWIPC|  CLONE_NEWUTS | CLONE_NEWPID | CLONE_NEWNS | CLONE_NEWUSER | SIGCHLD, NULL);

    printf("Parent [%5d] - Container [%5d]!\n", getpid(), container_pid);
    set_uid_map(container_pid, 0, uid, 1);
    set_gid_map(container_pid, 0, gid, 1);
    printf("Parent [%5d] - user/group mapping done!\n", getpid());
    /* 通知子进程 */
    close(pipefd[1]);

    waitpid(container_pid, NULL, 0);
    printf("Parent - container stopped!\n");
    return 0;
}
```
# rootfs
將要放入container 的 執行檔案與所需的 lib 放入 想對應的資料夾內，以這個例子為
```bash
mkdir bin 
cp /bin/bash
ldd ./bash
```
![](https://i.imgur.com/HFoLp3i.png)

將這些lib 複製到 rootfs 資料夾下
```bash
        linux-vdso.so.1 (0x00007ffcaa9cd000)
        libtinfo.so.6 => /lib/x86_64-linux-gnu/libtinfo.so.6 (0x00007f44a2e5c000)
        libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007f44a2e55000)
        libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f44a2c69000)
        /lib64/ld-linux-x86-64.so.2 (0x00007f44a3002000)
```
![](https://i.imgur.com/VjnAHzl.png)

當上述程式執行後會以rootfs這個資料夾為根目錄，並限制於這個資料夾。

# cgroup
我們來加點東西，限制容器資源大小
https://www.cnblogs.com/sparkdev/p/8296063.html
http://guildwar23.blogspot.com/2013/01/linux-control-group.html
https://www.cntofu.com/book/114/Cgroups/cgroups1.md
於/sys/fs/cgroup/cpu 創建兩個資料夾

```bash
mkdir  hight
mkdir  low
```
![](https://i.imgur.com/GPvHC3J.png)

查看現有核心數量
```bash
 cat /sys/fs/cgroup/cpuset/cpuset.cpus
```
![](https://i.imgur.com/6BsPbXl.png)
wsl 資料夾全部設為最高權限，用了文章中的mkdir 在寫入檔案時會發生權限問題
改用 cgcreate 來創造cgroup
```bash
chowm 777 -R low
chowm 777 -R hight
chowm 777 -R singlecore
 cgcreate -g cpu:low
 cgcreate -g cpu:hight
cgcreate -g cpuset:singlecore
```

```bash
 chown root:root -R /sys/fs/cgroup/cpu/low
 echo 512 > /sys/fs/cgroup/cpu/low/cpu.shares
 chown root:root -R /sys/fs/cgroup/cpu/hight
 echo 2048 > /sys/fs/cgroup/cpu/hight/cpu.shares
 echo "0-1" > /sys/fs/cgroup/cpuset/low/cpuset.cpus
 

chown root:root -R /sys/fs/cgroup/cpuset/singlecore

echo 0 > /sys/fs/cgroup/cpuset/singlecore/cpuset.mems
echo 0 > /sys/fs/cgroup/cpuset/singlecore/cpuset.cpus
```

# 設為共用同一個核心
# test file
```c
#include <stdio.h>
int main(){
	int i , end;
	end = 1024*1024*1024;
	for(i =  0 ; i < end;)
	{
	//++;
	}
}

```
根據前面的權重 512:2048
1:4 在同一顆cpu 裡面 20232 佔80 ,20231 佔 20

```
echo 20231 >/sys/fs/cgroup/cpuset/singlecore/tasks
echo 20232 >/sys/fs/cgroup/cpuset/singlecore/tasks

cgdelete   cpu:/low
cgdelete   cpu:/hight
```
![](https://i.imgur.com/QpPrwgS.png)

![](https://i.imgur.com/zY426gQ.png)
# 調整memory
# test2 file
```c
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include <unistd.h>

#define CHUNK_SIZE 1024 * 1024 * 1

void main()
{
    char *p;
    int i;

    for(i = 0; i < 100; i ++)
    {
        p = malloc(sizeof(char) * CHUNK_SIZE);
        if(p == NULL)
        {
            printf("fail to malloc!");
            return ;
        }
		sleep(1); // 1s
        // memset() 函数用来将指定内存的前 n 个字节设置为特定的值
        memset(p, 0, CHUNK_SIZE);
        printf("malloc memory %d MB\n", (i + 1) * 1);
    }
}
```
 調整記憶體上限為10M Bytes
```
mkdir /sys/fs/cgroup/memory/mymemory
chown -R root:root /sys/fs/cgroup/memory/mymemory  
記憶體限制 10mb
echo 10000000 > /sys/fs/cgroup/memory/mymemory/memory.limit_in_bytes
關閉swap
echo 0 > /sys/fs/cgroup/memory/mymemory/memory.swappiness
echo 20807 > /sys/fs/cgroup/memory/mymemory/tasks
```
![](https://i.imgur.com/0sbgs23.png)
再往上一層，可以看到 bash 只要是child process 這樣就可以大致算一個cgroup
![](https://i.imgur.com/V6z8gnW.png)

關閉 swap 可以看到 process 直接被 kill
到這邊就可以透過 cgroup 分別控管容器。
![](https://i.imgur.com/CWUqOo7.png)

# 其他參考
## 透過 systemd 控制 cgroup
https://www.cnblogs.com/sparkdev/p/9523194.html
```bash
ps --ppid 20203
apt install cgroup-tools
```
創建臨時cgroup
```bash
sudo systemd-run --unit=toptest --slice=test top -b
```
```bash
ls \-l /proc/?/ns

```
可以看到它會自動產生一些配置

https://www.waynerv.com/posts/container-fundamentals-resource-limitation-using-cgroups/

https://www.cntofu.com/book/46/linux_system/pipehe_fifo.md

https://coolshell.cn/articles/17010.html

