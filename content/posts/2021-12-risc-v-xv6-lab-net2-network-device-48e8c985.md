---
title: "RISC-V XV6 LAB-NET2 network device 大致概念"
date: "2021-12-06T21:34:00.002+08:00"
updated: "2022-05-14T09:48:59.227+08:00"
permalink: "/2021/12/risc-v-xv6-lab-net2-network-device.html"
original_url: "https://x8795278.blogspot.com/2021/12/risc-v-xv6-lab-net2-network-device.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2335944298336882821"
tags: ["lab-net", "xv6"]
layout: post
---

![](https://i.imgur.com/SSPrWdU.png)

# xv6 network-net 2
5hr
![](https://i.imgur.com/SSPrWdU.png)
![](https://i.imgur.com/Z1hC7v2.png)
![](https://i.imgur.com/MYalXlk.png)

這一次的trace 要結合前面的部分內容來推測，要完成一個
multi-process ping 改裝成 server bind listen 到底會經過那些步驟.

就已中斷來說我們網卡確實是可以接收封包 但是僅限於 udp 為了證明上一次的思考方向是對的我們嘗試構造一個tcp 連接，不知道會不寫到http server不過大致上可以講個概念

# makefile forwarding port
這邊踩坑，原因是為什麼可以收到UDP封包而收不到 TCP 封包 並且 PYTHON 連接並出現 connection refused，我查了好幾天，對照好幾個版本的code
一連翻到x86版本都沒看出異樣，最終想到在qemu 轉發port 那邊去做了些修改

![](https://i.imgur.com/e3METxG.png)
```makefile
user,id=net0,hostfwd=udp::$(FWDPORT)-:2000,hostfwd=tcp::12346-:7 
```
仔細看 tcp 那邊 我們如果要透過 pyhton client 連接 必須要下 port 為12346端口
# python  client
```python

import socket
import sys
import requests
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
addr = ('172.18.86.160',12346)
#byte_message = bytes("Hello, World!", "utf-8")
byte_message = bytes("this is the host!", "utf-8")
# server_address = ('www.python.org', 80)
print(int(sys.argv[1]))
print('listening on %s port %s' % addr, file=sys.stderr)
sock.connect(addr)
count  = 0
request_header = 'GET / HTTP/1.0\r\nHost: 172.18.86.160\r\n\r\n'
# sock.send(request_header.encode('utf-8'))
while count<100000:
    time.sleep(0.0001)

    sent =sock.send(request_header.encode('utf-8'))
    # sent = sock.sendto(byte_message, ('172.18.86.160', 25999))

    if sent:
        count = count +1 
        print("send okk")
        print(count)

    print(sent)
    

sock.close()  
```
可以看到可以成功work 接收到tcp 封包
![](https://i.imgur.com/aCLINIU.png)
![](https://i.imgur.com/lSyV3wP.png)
那些數字是我debug 在看的東西請自動忽略，現在我們來全部trace 一次，並試著猜實現一個http server 大概怎麼弄

# 概念圖
![](https://i.imgur.com/iJikLYR.png)

這邊我隨便找一張
整個大概的概念可以想成data 透過 ip_header 不斷的封裝，ip_header 可以 幫助 router 在互聯網找到彼此的電腦，在區域網路可能可以透過廣播與Mac 找到彼此的位置，但是 互聯網就不一樣了，可能要透過ip_address 加上一些算法才能找到屬於你的電腦。

回到我們的最初兩個fucntion

# e1000_transmit
```c
int e1000_transmit(struct mbuf *m)
{
  //
  // Your code here.
  //
  // the mbuf contains an ethernet frame; program it into
  // the TX descriptor ring so that the e1000 sends it. Stash
  // a pointer so that it can be freed after sending.
  //
  acquire(&e1000_lock);
  uint32 tail = regs[E1000_TDT];
  // overflow
  if (tx_ring[tail].status != E1000_TXD_STAT_DD)
  {
    release(&e1000_lock);
    return -1;
  }
  if (tx_mbufs[tail])
  {
    mbuffree(tx_mbufs[tail]);
  }
  tx_ring[tail].length = (uint16)m->len;
  tx_ring[tail].addr = (uint64)m->head;
  tx_ring[tail].cmd = 9;
  tx_mbufs[tail] = m;
  regs[E1000_TDT] = (tail + 1) % TX_RING_SIZE;
  release(&e1000_lock);
  return 0;
}
```

# e1000_recv
```c
static void
e1000_recv(void)
{
  //
  // Your code here.
  //
  // Check for packets that have arrived from the e1000
  // Create and deliver an mbuf for each packet (using net_rx()).
  //

  int tail = regs[E1000_RDT];
  int i = (tail + 1) % RX_RING_SIZE; // tail is owned by Hardware!

  while (rx_ring[i].status & E1000_RXD_STAT_DD)
  {

    rx_mbufs[i]->len = rx_ring[i].length;
    // send mbuf to upper level (the network stack in net.c).
    net_rx(rx_mbufs[i]);
    // get a new buffer for next recv.
    rx_mbufs[i] = mbufalloc(0);
    rx_ring[i].addr = (uint64)rx_mbufs[i]->head;
    // update status for next recv.
    rx_ring[i].status = 0;
    i = (i + 1) % RX_RING_SIZE;
    printf("teet %d \n", i);
  }
  regs[E1000_RDT] = i - 1; // - 1 for the while loop.
}
```
這兩個 function 怎麼呼叫的呢，我們往更上一層的中斷來看

# int devintr()
可以發現 在 硬體發生中斷這邊發現當我們的網卡正常啟動後，照理說我們透過設定reg 可以讓網卡收到封包的時候發生中斷。就是這段程式碼在檢測有沒有其他連線試圖連到我們的網路
```c
#ifdef LAB_NET
    else if(irq == E1000_IRQ){
      e1000_intr();
    }
```

#  e1000_intr
```c

void e1000_intr(void)
{

  // tell the e1000 we've seen this interrupt;
  // without this the e1000 won't raise any
  // further interrupts.
  regs[E1000_ICR] = 0xffffffff;

  e1000_recv();
}

```

# packet
當收到ip封包後我們要做的處理就是拆
拆到只剩 data 我們首先會先經過net_rx
![](https://i.imgur.com/8p8M8VT.png)

## void net_rx(struct mbuf *m)
可以發現這邊可以初步對ip header 進行類型判斷
```
// called by e1000 driver's interrupt handler to deliver a packet to the
// networking stack
static int count2 =0;
void net_rx(struct mbuf *m)
{
  struct eth *ethhdr;
  uint16 type;
count2++;
  ethhdr = mbufpullhdr(m, *ethhdr);
  if (!ethhdr) {
    mbuffree(m);
    return;
  }
 printf("rko test %d\n" , count2);
  type = ntohs(ethhdr->type);
   printf("test11 %d\n",type);
  if (type == ETHTYPE_IP)
    net_rx_ip(m);
  else if (type == ETHTYPE_ARP)
    net_rx_arp(m);
  else
    mbuffree(m);
}

```
# eth struct
可以發現
ethhdr = mbufpullhdr(m, *ethhdr);
應該是塞滿到 ethhder 結構上，我們先不管原理
```c
struct eth {
  uint8  dhost[ETHADDR_LEN];
  uint8  shost[ETHADDR_LEN];
  uint16 type;
} __attribute__((packed));

```
https://codertw.com/%E7%A8%8B%E5%BC%8F%E8%AA%9E%E8%A8%80/624590/
  type = ntohs(ethhdr->type);
先把他當成轉態的東西，反正可以得出type
https://zh.wikipedia.org/wiki/%E4%BB%A5%E5%A4%AA%E7%B1%BB%E5%9E%8B
![](https://i.imgur.com/tGdxQTg.png)

以太類型編號	代表協定
0x0800	Internet Protocol version 4 (IPv4)
0x0806	Address Resolution Protocol (ARP)

看來就是這個格式

![](https://i.imgur.com/RWmiW85.png)

在這一部分可能初步先判斷要對我們送過來的封包要進入那些環節的判斷

那我們走 ipv4 那個環節

# net_rx_ip(struct mbuf *m)
到這邊我加了幾段程式碼，原本只支援udp 我新增了tcp 新的結構，目前只做到 tcp 實作相對來講比較單純

##  a UDP packet header
```c
// a UDP packet header (comes after an IP header).
struct udp {
  uint16 sport; // source port
  uint16 dport; // destination port
  uint16 ulen;  // length, including udp header, not including IP header
  uint16 sum;   // checksum
};

```

##  a TCP packet header
```c
struct tcp {
    uint16 src;
    uint16 dst;
    uint16 seq;
    uint32 ack;
    uint8  off;
    uint8  flg;
    uint16 win;
    uint16 sum;
    uint16 urg;
};
```

## ADD TCP judgment
到這邊我們已經將 TCP 和 UDP 封包分開了
```c
// receives an IP packet
static void
net_rx_ip(struct mbuf *m)
{

  struct ip *iphdr;
  uint16 len;

  iphdr = mbufpullhdr(m, *iphdr);
  if (!iphdr)
	  goto fail;

  // check IP version and header len
  if (iphdr->ip_vhl != ((4 << 4) | (20 >> 2)))
    goto fail;
  // validate IP checksum
  if (in_cksum((unsigned char *)iphdr, sizeof(*iphdr)))
    goto fail;
  // can't support fragmented IP packets
  if (htons(iphdr->ip_off) != 0)
    goto fail;
  // is the packet addressed to us?
  if (htonl(iphdr->ip_dst) != local_ip)
    goto fail;
  if(iphdr->ip_p == IPPROTO_TCP)
   printf("walk tcp\n");
    if(iphdr->ip_p == IPPROTO_UDP)
   printf("walk tcp\n");
  // can only support UDP
  // if (iphdr->ip_p != IPPROTO_UDP)
  //   goto fail;
  len = ntohs(iphdr->ip_len) - sizeof(*iphdr);
  net_rx_udp(m, len, iphdr);
  return;

fail:
  mbuffree(m);
}

```

## 改裝一下 UDP 流程
```c
// receives a UDP packet
static void
net_rx_udp(struct mbuf *m, uint16 len, struct ip *iphdr)
{
  struct tcp *udphdr;
  uint16 src;
  uint16 dst, seq;

 printf("test16\n");
  udphdr = mbufpullhdr(m, *udphdr);
  if (!udphdr)
    goto fail;
 printf("pre recv\n");
  // // TODO: validate UDP checksum

  // // validate lengths reported in headers
  // if (ntohs(udphdr->ulen) != len)
  //   goto fail;
  // len -= sizeof(*udphdr);
  // if (len > m->len)
  //   goto fail;
  // // minimum packet size could be larger than the payload
  // mbuftrim(m, m->len - len);
  // printf("test14\n");
  // // parse the necessary fields
  src = ntohl(iphdr->ip_src);
  dst = ntohs(udphdr->dst);
  seq = ntohs(udphdr->seq);
printf("%d\n",src);
printf("%d\n",dst);
printf("%d\n",seq);

  // sockrecvudp(m, sip, dport, sport);
  return;

fail:
  mbuffree(m);
}

```
剛剛那些亂碼其實就是我在DEBUG

![](https://i.imgur.com/WCh64wY.png)
到這邊可以到 就是 src 和 dst 更詳細的 tcp/udp 對比 格式可能會長這樣

![](https://i.imgur.com/0CKB4sU.png)

這邊算是最近才有的進展tcp 要考慮的東西非常多
我後面只介紹 udp，看有空再能不能弄出 tcp

# sockrecvudp
這邊我有稍微改裝過，本來要用udp當例子，去模擬 tcp 的 bind listen  recv 等等，如果是我們自己架構的話，三方交握 看是要握幾次應該都可以xd，可以看到我們從最初
packet -> ip -> tcp/udp 到要往 user 層送資料其實可以很清楚的明白又回到了socket
無非我們在user 層 建立 socket
socket 再用 socket 去對檔案去做寫檔案
在下列程式碼，可以看到我直接忽略port 簡單解釋就是

dst port 可能由網卡給， source 可能是網卡本來就有開出去的port  (有可能理解錯誤沒去看
https://zh.wikipedia.org/wiki/TCP/UDP%E7%AB%AF%E5%8F%A3%E5%88%97%E8%A1%A8

在接受到封包後，在依照 dst port 去 mapping 到一個 socket 接收在資料後，會寫入一個檔案做buffer or 組合 成想要的資料格式 ( 串流..等等

那麼可以得知這個fucntion 就是在喚醒對列的socket
我們要開始往測資去理解我們的程式碼架構

```c
// called by protocol handler layer to deliver UDP packets
void sockrecvudp(struct mbuf *m, uint32 raddr, uint16 lport, uint16 rport)
{
  //
  // Find the socket that handles this mbuf and deliver it, waking
  // any sleeping reader. Free the mbuf if there are no sockets
  // registered to handle it.
  //

  struct sock *si;

  acquire(&lock);
  count++;
  if(count%500 == 0)
  printf("read count test----------------------------------------  %d\n", count);
  // printf("find remote address %d\n", raddr);
  // printf("find remote port %d\n", lport);
  // printf("find remote port2 %d\n", rport);

  si = sockets;
  // printf("find established address %d\n", si->raddr);
  // printf("find established port %d\n", si->lport);
  // printf("find established port2 %d\n", si->rport);
  while (si)
  {
    //&& si->lport == lport  &&
    if (si->raddr == raddr && si->lport == lport )
    {

      // printf("find established address %d\n", si->raddr);
      // printf("find established port %d\n", si->lport);
      // printf("find established port2 %d\n", si->rport);
 
      // printf("find \n");
      goto found;
    }
    si = si->next;
  }
  release(&lock);
  mbuffree(m);
  return;

found:
  acquire(&si->lock);
  mbufq_pushtail(&si->rxq, m);
  wakeup(&si->rxq);

  release(&si->lock);
  release(&lock);
}

```

# udp testing
這邊我們拿測資 multi-process，這又讓我想到 thread pool實作

```c
  printf("testing multi-process pings: ");
```

```c
  for (i = 0; i < 10; i++)
  {
    int pid = fork();
    if (pid == 0)
    {
      ping(2000 + i + 1, dport, 1);
      exit(0);
    }
  }
  for (i = 0; i < 10; i++)
  {
    wait(&ret);
    if (ret != 0)
      exit(1);
  }
```

# ping

```c
static void
ping(uint16 sport, uint16 dport, int attempts)
{
  int fd;
  char *obuf = "a message from xv6!";
  uint32 dst;

  // 10.0.2.2, which qemu remaps to the external host,
  // i.e. the machine you're running qemu on.
  dst = (10 << 24) | (0 << 16) | (2 << 8) | (2 << 0);

  // you can send a UDP packet to any Internet address
  // by using a different dst.
  
  if((fd = connect(dst, sport, dport)) < 0){
    fprintf(2, "ping: connect() failed\n");
    exit(1);
  }

  for(int i = 0; i < attempts; i++) {
    if(write(fd, obuf, strlen(obuf)) < 0){
      fprintf(2, "ping: send() failed\n");
      exit(1);
    }
  }

  char ibuf[128];
  int cc = read(fd, ibuf, sizeof(ibuf)-1);
  if(cc < 0){
    fprintf(2, "ping: recv() failed\n");
    exit(1);
  }

  close(fd);
  ibuf[cc] = '\0';
  if(strcmp(ibuf, "this is the host!") != 0){
    fprintf(2, "ping didn't receive correct payload\n");
    exit(1);
  }
}

```

![](https://i.imgur.com/qghV6S1.png)

回歸到 Makefile，可以看到最初的版本 udp 是綁定到 port  2000 但是外部 可以透過 5000 和 25999 進行呼叫
那我們可以看到 tcp
port 綁定到 7 內部端口對應到的是 12346
# min thread pool udp socket

```c

int main(int argc, char *argv[])
{
  // int i, ret;
  uint16 dport = NET_TESTS_PORT;

  printf("nettests running on port %d\n", dport);

  printf("testing ping: ");
  printf("OK %d \n", dport);
  ping(7, dport, 1);
  // printf("OK\n");
  exit(0);
```
# ping  ex2
可以看到改裝後的ping 變成可以recv 封包的fucntion

 if ((fd = connect(dst, sport, dport)) < 0)
 這行執行後 socket 會存在 buffer 我們來看實際的 sys_call

```c
static void
ping(uint16 sport, uint16 dport, int attempts)
{
  int fd;

  uint32 dst;

  // 10.0.2.2, which qemu remaps to the external host,
  // i.e. the machine you're running qemu on.
  dst = (10 << 24) | (0 << 16) | (2 << 8) | (2 << 0);

  if ((fd = connect(dst, sport, dport)) < 0)
  {
    fprintf(2, "ping: connect() failed\n");
    exit(1);
  }

  bind(dst, sport, dport);

  char ibuf[128];

  // int count = 0;
  int i, ret;
  while (1)
  {
    for (i = 0; i < 10; i++)
    {
      int pid = fork();
      if (pid == 0)
      {
        int cc = read(fd, ibuf, sizeof(ibuf) - 1);
        if (cc < 0)
        {
          fprintf(2, "ping: recv() failed\n");
          exit(1);
        }
        // printf("teet2\n");
        ibuf[cc] = '\0';
        if (strcmp(ibuf, "this is the host!") != 0)
        {
          fprintf(2, "ping didn't receive correct payload\n");
          exit(1);
        }
      
        close(fd);
        exit(0);
      }
    }
    for (i = 0; i < 10; i++)
    {
      wait(&ret);
      if (ret != 0)
        exit(1);
    }

  }

}
```
# sys_connect(void)
繼剛剛的部分，如果參考別份程式碼可以看到
大部分還是會構造 socket bind listen accept 但是我們直接省略，原本的程式碼
也可以看到

>   if(sockalloc(&f, raddr, lport, rport) < 0)
  
```c

sys_connect(void)
{
  struct file *f;
  int fd;
  uint32 raddr;
  uint32 rport;
  uint32 lport;

  if (argint(0, (int*)&raddr) < 0 ||
      argint(1, (int*)&lport) < 0 ||
      argint(2, (int*)&rport) < 0) {
    return -1;
  }

  if(sockalloc(&f, raddr, lport, rport) < 0)
    return -1;
  if((fd=fdalloc(f)) < 0){
    fileclose(f);
    return -1;
  }

  return fd;
}

```

# sockalloc
這邊可以看到socket 的實體
sockalloc，包括可以去設定
整體概念就是申請一個 socket 裡面有個member 指向一個 file，這樣在 後續 sys_read
sys_write 將會看到
  (*f)->type = FD_SOCK;
實際意義
這邊沒看分析錯的話應該是 環狀的 buffer

```c

int sockalloc(struct file **f, uint32 raddr, uint16 lport, uint16 rport)
{
  struct sock *si, *pos;

  si = 0;
  *f = 0;
  if ((*f = filealloc()) == 0)
    goto bad;
  if ((si = (struct sock *)kalloc()) == 0)
    goto bad;

  // initialize objects
  si->raddr = raddr;
  si->lport = lport;
  si->rport = rport;
  si->busy = 0;
  initlock(&si->lock, "sock");
  mbufq_init(&si->rxq);
  (*f)->type = FD_SOCK;
  (*f)->readable = 1;
  (*f)->writable = 1;
  (*f)->sock = si;

  // add to list of sockets
  acquire(&lock);
  pos = sockets;
  while (pos)
  {
    if (pos->raddr == raddr &&
        pos->lport == lport &&
        pos->rport == rport)
    {
      release(&lock);
      goto bad;
    }
    pos = pos->next;
  }
  si->next = sockets;
  sockets = si;
  release(&lock);
  return 0;

bad:
  if (si)
    kfree((char *)si);
  if (*f)
    fileclose(*f);
  return -1;
}
```

# sys_bind
繼續往 ping ex2 往下看
我這邊草寫了一個 bind

```c
bind(dst, sport, dport);
```
這邊我在猜想，當硬體層一路送到我們os 基本上還是要再buffer 找到一組socket 狀態是有在listen 並且端口是正確
```c
int sockbind(struct file **f, uint32 raddr, uint16 lport, uint16 rport)
{
  struct sock *pos;

  acquire(&lock);
  pos = sockets;
  int count = 0;
  while (pos)
  {
    if (pos->raddr == raddr &&
        pos->lport == lport &&
        pos->rport == rport)
    {
      count++;
      // printf("find hah %d \n", rport);
      // release(&lock);
      // goto bad;
    }
    pos = pos->next;
    // printf("test socket %d \n", count);
  }
  // si->next = sockets;
  // sockets = si;
  release(&lock);
  return 0;
}
```
# sockrecvudp
從頭來觀看這段程式碼
我把一些條件都忽略，只要有對上port 都可以回應這些 connect
注意   wakeup(&si->rxq);
spring lock 這段 要喚醒那些 程式呢
沒錯就是我們的 socket
```c
  if (si->raddr == raddr && si->lport == lport )
    {

      // printf("find established address %d\n", si->raddr);
      // printf("find established port %d\n", si->lport);
      // printf("find established port2 %d\n", si->rport);
 
      // printf("find \n");
      goto found;
    }
```
```c
// called by protocol handler layer to deliver UDP packets
void sockrecvudp(struct mbuf *m, uint32 raddr, uint16 lport, uint16 rport)
{
  //
  // Find the socket that handles this mbuf and deliver it, waking
  // any sleeping reader. Free the mbuf if there are no sockets
  // registered to handle it.
  //

  struct sock *si;

  acquire(&lock);
  count++;
  if(count%500 == 0)
  printf("read count test----------------------------------------  %d\n", count);
  // printf("find remote address %d\n", raddr);
  // printf("find remote port %d\n", lport);
  // printf("find remote port2 %d\n", rport);

  si = sockets;
  // printf("find established address %d\n", si->raddr);
  // printf("find established port %d\n", si->lport);
  // printf("find established port2 %d\n", si->rport);
  while (si)
  {
    //&& si->lport == lport  &&
    if (si->raddr == raddr && si->lport == lport )
    {

      // printf("find established address %d\n", si->raddr);
      // printf("find established port %d\n", si->lport);
      // printf("find established port2 %d\n", si->rport);
 
      // printf("find \n");
      goto found;
    }
    si = si->next;
  }
  release(&lock);
  mbuffree(m);
  return;

found:
  acquire(&si->lock);
  mbufq_pushtail(&si->rxq, m);
  wakeup(&si->rxq);

  release(&si->lock);
  release(&lock);
}
```

```c
    for (i = 0; i < 10; i++)
    {
      int pid = fork();
      if (pid == 0)
      {
        int cc = read(fd, ibuf, sizeof(ibuf) - 1);
        if (cc < 0)
        {
          fprintf(2, "ping: recv() failed\n");
          exit(1);
        }
        // printf("teet2\n");
        ibuf[cc] = '\0';
        if (strcmp(ibuf, "this is the host!") != 0)
        {
          fprintf(2, "ping didn't receive correct payload\n");
          exit(1);
        }
      
        close(fd);
        exit(0);
      }
    }
    for (i = 0; i < 10; i++)
    {
      wait(&ret);
      if (ret != 0)
        exit(1);
    }
```

# sys_read
可以看到 剛剛的 read 是在等 網路卡封包中斷後一路往上送
  int cc = read(fd, ibuf, sizeof(ibuf) - 1);
read  究竟做了什麼些事    
```c
uint64
sys_read(void)
{
  struct file *f;
  int n;
  uint64 p;

  if(argfd(0, 0, &f) < 0 || argint(2, &n) < 0 || argaddr(1, &p) < 0)
    return -1;
  return fileread(f, p, n);
}
```

# int fileread(struct file *f, uint64 addr, int n)
還記的前面的 sys_connect 返回也是一個
struct file *f 還記得  sockalloc
新創了一個 socket 並為他配置一個 fd 可以讓
這邊的 read 可以判斷檔案的 type (FD_SOCK)
對應到下面程式碼
 else if(f->type == FD_SOCK){
達成切換到 sockread
```c

// Read from file f.
// addr is a user virtual address.
int
fileread(struct file *f, uint64 addr, int n)
{
  int r = 0;

  if(f->readable == 0)
    return -1;

  if(f->type == FD_PIPE){
    r = piperead(f->pipe, addr, n);
  } else if(f->type == FD_DEVICE){
    if(f->major < 0 || f->major >= NDEV || !devsw[f->major].read)
      return -1;
    r = devsw[f->major].read(1, addr, n);
  } else if(f->type == FD_INODE){
    ilock(f->ip);
    if((r = readi(f->ip, 1, addr, f->off, n)) > 0)
      f->off += r;
    iunlock(f->ip);
  }
#ifdef LAB_NET
  else if(f->type == FD_SOCK){
    r = sockread(f->sock, addr, n);
  }
#endif
  else {
    panic("fileread");
  }

  return r;
}
```

#  int sockread(struct sock *si, uint64 addr, int n)
這一段可以看到 當我們run 10 child process
全部都都會在
  while (mbufq_empty(&si->rxq) && !pr->killed)
  {
    sleep(&si->rxq, &si->lock);
  }
  進行自旋
  
```c

int sockread(struct sock *si, uint64 addr, int n)
{
  struct proc *pr = myproc();
  struct mbuf *m;
  int len;

  acquire(&si->lock);
  si->busy = 1;
  // printf("socket read\n");
  while (mbufq_empty(&si->rxq) && !pr->killed)
  {
    sleep(&si->rxq, &si->lock);
  }
 
  // printf("socket read2\n");
  
  if (pr->killed)
  {
      si->busy = 0;
    release(&si->lock);
    return -1;
  }
  m = mbufq_pophead(&si->rxq);
  release(&si->lock);

  len = m->len;
  if (len > n)
    len = n;
  if (copyout(pr->pagetable, addr, m->head, len) == -1)
  {
     si->busy = 0;
    mbuffree(m);
    return -1;
  }
   si->busy = 0;
  mbuffree(m);
  return len;
}
```
而剛剛我們說的 sockrecvudp
對應到的就是 喚醒自旋中的 process
```c
  while (si)
  {
    //&& si->lport == lport  &&
    if (si->raddr == raddr && si->lport == lport )
    {

      // printf("find established address %d\n", si->raddr);
      // printf("find established port %d\n", si->lport);
      // printf("find established port2 %d\n", si->rport);
 
      // printf("find \n");
      goto found;
    }
    si = si->next;
  }
  release(&lock);
  mbuffree(m);
  return;

found:
  acquire(&si->lock);
  mbufq_pushtail(&si->rxq, m);
  wakeup(&si->rxq);
```
到這邊我們 就可以輕鬆去 udp response
每秒請求也達到了 500當然這邊只是想用 udp 去模擬 tcp 大致架構可能會漏掉蠻多東西的，目前tcp只做到收封包的前置，目前有注意到 interrupt 好像會變polling(??
要等看懂 lwip 整體架構才能再進一步紀錄一下

![](https://i.imgur.com/KaUb996.png)

## References

- Russ Cox, Frans Kaashoek, Robert Morris, [*xv6: a simple, Unix-like teaching operating system*](https://pdos.csail.mit.edu/6.828/2020/xv6.html), MIT PDOS.
- [MIT PDOS / xv6-riscv](https://github.com/mit-pdos/xv6-riscv) — 本文 trace 的 xv6 network lab 原始碼。

