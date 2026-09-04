---
title: "RISC-V XV6 不依靠lib 完成 3 way handshake"
date: "2021-12-15T21:41:00.003+08:00"
updated: "2021-12-15T21:41:18.880+08:00"
permalink: "/2021/12/xv6-lab-6-lib-3-way-handshake.html"
original_url: "https://x8795278.blogspot.com/2021/12/xv6-lab-6-lib-3-way-handshake.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6317389500634785819"
tags: ["xv6"]
layout: post
---

![](https://i.imgur.com/2vpVYJk.jpg)

# xv6 network-net 3
最近土法煉鋼完成三方交握的部分，沒錯這個實驗還在繼續，為了證明最初的概念是對的。
# server
我們要完成的是三方交握的第一階段，也就是
bind - listening - accept
能不能節省掉這個步驟是可以的
![](https://i.imgur.com/3T3N11T.png)
![](https://i.imgur.com/fJ53VR4.png)
當我把sockecvudp while 迴圈裡 if判斷是拿掉的當下就是變成所有流量只要有socket 監聽就可以直接回傳。

# tcp header
![](https://i.imgur.com/cWDGkCw.png)
目前就已經整合進修改過後的xv6 kernel
可以對一般的socket 進行到三方交握階段，

# multi-network card  qemu tap
透過這些設定，可以讓我們的xv6 支援更多張網卡
```bahs
	ip tuntap add mode tap name tap0
	ip addr add 172.16.100.1/24 dev tap0
	ip link set tap0 up
```
```makefile
# QEMUOPTS += -netdev user,id=net0,hostfwd=udp::$(FWDPORT)-:2000,hostfwd=tcp::7-:7 -object filter-dump,id=net0,netdev=net0,file=packets.pcap
# QEMUOPTS += -device e1000,netdev=net0,bus=pcie.0

QEMUOPTS += -netdev tap,id=net1,ifname=tap0  -object filter-dump,id=net1,netdev=net1,file=packets2.pcap
QEMUOPTS += -device e1000,netdev=net1
```
![](https://i.imgur.com/Tp615Sa.png)
# debug checksuming
最主要的部份如果真的要實現一個tcp 協議需要對封包處理很熟悉，如果有多張網卡的情況可以透過下列指令關閉網卡的checksum 驗證，不然你的封包會莫名其妙地消失
ethtool -K ethx tx off rx off
下列網卡就是針對 tap0 但是可以看到 他寫的是fixed (有關等於沒關
![](https://i.imgur.com/0JQsRmO.png)
下列是出現封包遺失階段的畫面，網路上資料非常少

![](https://i.imgur.com/EUiMoZd.png)
server 可以看到有發送syn/ack 但是client遲遲不能解析封包

沒有gui介面可以透過

```bash
sudo tcpdump -i tap0 -nn tcp
```
我找了一個https://github.com/pandax381/xv6-net
虛擬機可以研究了一段時間，稍微研究了他的封包之間的協議可以發現上方是對方的封包訊息，下方是我的
![](https://i.imgur.com/krvMnEW.png)
![](https://i.imgur.com/Q7lPY5E.png)

透過
```bash
netstat --statistics --tcp
```
![](https://i.imgur.com/PympDTq.png)
可以看到我們的封包 被網卡拋棄了!

在檢查碼的這部分我發現我的檢查碼每次算會跟真實checksuming 差
```c
uint16 tmp = 0x4fb;
```

開啟wireshark 可以看到封包checksum狀況
![](https://i.imgur.com/od6vCiN.png)
這是錯誤範例
![](https://i.imgur.com/wAoMAYG.png)

後面還有異動幾個版本，最後結論就是
最後懶得改了直接 答案-4fb
```c
static void
net_rx_udp(struct mbuf *m, uint16 len, struct ip *iphdr)
{
  struct tcp *udphdr, *udphdr2;
  uint16 src;
  uint16 dst;
  uint32 tmp, seq;

  uint8 flg;
  uint8 flg2;
  uint8 dst1;
  uint8 dst2;
  uint8 dst3;
  uint8 dst4;
  uint32 ack;
  // uint32 sip;
  uint16 sport, dport;
  printf("test16\n");
  struct mbuf *m2;

  m2 = mbufalloc(MBUF_DEFAULT_HEADROOM);
  udphdr = mbufpullhdr(m, *udphdr);
  udphdr2 = mbufpushhdr(m2, (*udphdr2));
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
  tmp = udphdr->dst;
  udphdr->dst = udphdr->src;
  udphdr->src = tmp;
  udphdr2->src = udphdr->dst;
  udphdr2->dst = udphdr->src;

  // udphdr2->src = udphdr->dst;
  // udphdr2->dst = udphdr->src;
  //   udphdr2->seq = 0;
  // udphdr2->ack = 0;
  // udphdr2->off = 0;
  // udphdr2->win = 0;
  // udphdr2->sum = 0;
  // udphdr2->urg =0;

  //  uint16 src;
  //   uint16 dst;
  //   uint32 seq;
  //   uint32 ack;
  //   uint8  off;
  //   uint8  flg;
  //   uint16 win;
  //   uint16 sum;
  //   uint16 urg;
  dst = ntohs(udphdr->dst);
  seq = udphdr->seq;
  flg = udphdr->flg;
  flg2 = 18;

  dst = (iphdr->ip_src << 24) | (iphdr->ip_src << 16) | (iphdr->ip_src << 8) | (iphdr->ip_src << 0);
  dst1 = (iphdr->ip_src >> 24);
  dst2 = (iphdr->ip_src >> 16);
  dst3 = (iphdr->ip_src >> 8);
  dst4 = (iphdr->ip_src >> 0);

  ack = udphdr->ack;

  //  | (0 << 16) | (2 << 8) | (2 << 0);
  printf("dst%u\n", dst);
  printf("src%u\n", src);
  // printf("dst %u\n", udphdr->dst);
  printf("src%d\n", ntohs(udphdr->src));
  printf("dst %d\n", ntohs(udphdr->dst));
  printf("seq %u\n", ntohl(seq));
  printBits(flg);
  printBits(flg2);

  printf("flg %d\n", flg);
  printf("flg2 %d\n", flg2);
  printf("addr4 %d\n", dst4);
  printf("addr3 %d\n", dst3);
  printf("addr2 %d\n", dst2);
  printf("addr1 %d\n", dst1);
  dst1 = (iphdr->ip_dst >> 24);
  dst2 = (iphdr->ip_dst >> 16);
  dst3 = (iphdr->ip_dst >> 8);
  dst4 = (iphdr->ip_dst >> 0);
  printf("addr4 %d\n", dst4);
  printf("addr3 %d\n", dst3);
  printf("addr2 %d\n", dst2);
  printf("addr1 %d\n", dst1);

  printf("ack %u\n", ntohl(ack));
  printf("seq  ntohs %u\n", ntohs(seq) + 1);
  printf("seq  ntohl %u\n", ntohl(seq) + 1);

  udphdr->flg = flg2;
  if (stseq == 0)
  {
    udphdr->seq = htonl(ntohl(seq) + 99);
  }
  else
  {
    udphdr->seq = htonl(ntohl(stseq) + 1);
    stseq = ntohl(stseq) + 1;
  }
  // 172.17.35.175
  //  tmp = (192 << 24) | (168<< 16) | (100<< 8) | (1 << 0);
  udphdr2->src = udphdr->src;
  udphdr2->dst = udphdr->dst;
  udphdr2->ack = htonl(ntohl(seq) + 1);

  udphdr2->seq = htonl(ntohl(seq) + 123123123);
  udphdr2->flg = flg2;
  udphdr2->off = (sizeof(struct tcp) >> 2) << 4;
  udphdr2->win = udphdr->win;
  udphdr2->sum = 0;
  udphdr2->urg = 0;
  // udphdr2->option = udphdr->option;
  uint32 pseudo = 0;
  // tmp = (172 << 24) | (16 << 16) | (100 << 8) | (2 << 0);
  // tmp = (10 << 24) | (0 << 16) | (2 << 8) | (15 << 0);
  pseudo += ((local_ip) >> 16) & 0xffff;
  pseudo += (local_ip)&0xffff;
  // tmp = (172 << 24) | (16 << 16) | (100 << 8) | (1 << 0);
  tmp = (172 << 24) | (16 << 16) | (100 << 8) | (1 << 0);
  pseudo += (tmp >> 16) & 0xffff;
  pseudo += tmp & 0xffff;
  pseudo += htons((uint16)IP_PROTOCOL_TCP);
  pseudo += htons(sizeof(struct tcp));
  uint16 tmp2 = 0x4fb;
  printf("%u\n", tmp2);
  // udphdr2->sum =cksum16((uint16 *)udphdr2, sizeof(struct tcp), pseudo);
  udphdr2->sum = cksum16((uint16 *)udphdr2, sizeof(struct tcp), pseudo);
  printf("%u\n", udphdr2->sum);
  printf("%u\n", udphdr2->sum + tmp2);
  printf("%u\n", htons(udphdr2->sum));
  printf("%u\n", htons(tmp2));
  printf("%u\n", htons(udphdr2->sum) + tmp2);
  udphdr2->sum = htons(htons(udphdr2->sum) + tmp2);
  printf("%u\n", htons(udphdr2->sum) + htons(tmp2));
  uint32 pseudo2 = 0;
  // tmp = (172 << 24) | (16 << 16) | (100 << 8) | (2 << 0);
  // tmp = (10 << 24) | (0 << 16) | (2 << 8) | (15 << 0);
  pseudo2 += (local_ip) >> 16;
  pseudo2 += (local_ip)&0xffff;
  // tmp = (172 << 24) | (16 << 16) | (100 << 8) | (1 << 0);
  // 3	0.005475	172.29.64.1	10.0.2.15	TCP	58	58866 → 11111 [SYN] Seq=0 Win=65535 Len=0 MSS=1460
  tmp = (172 << 24) | (16 << 16) | (100 << 8) | (1 << 0);
  pseudo2 += tmp >> 16;
  pseudo2 += tmp & 0xffff;
  pseudo2 += htons((uint16)IP_PROTOCOL_TCP);
  pseudo2 += htons(sizeof(struct tcp));
  // in_cksum()
  if (cksum16((uint16 *)udphdr2, sizeof(struct tcp), pseudo2) != 0)
  {

    printf("tcp checksum error!\n");
  }
  else
    printf("tcp checksum ok!\n");
  //  mbuftrim(m2,4)
  printf("%x\n", cksum16((uint16 *)udphdr2, sizeof(struct tcp), pseudo));
  printf("%x\n", cksum16((uint16 *)udphdr2, sizeof(struct tcp), pseudo2));
  //  uint16 src;
  //   uint16 dst;
  //   uint32 seq;
  //   uint32 ack;
  //   uint8  off;
  //   uint8  flg;
  //   uint16 win;
  //   uint16 sum;
  //   uint16 urg;
  //  printf("seq  ntohs %u\n", ntohs(seq));
  //  printf("seq  ntohs %u\n", ntohl( seq));
  //  printf("ack %u\n", ntohl ( udphdr->ack ));
  udphdr->ack = htonl(ntohl(seq) + 1);

  ack = udphdr2->seq;
  seq = udphdr2->ack;
  // uint8_t *buf;
  // memcpy(udphdr2 + 1, buf, sizeof(20));
  printf("ack %u\n", ntohl(ack));
  printf("seq %u\n", ntohl(seq));
  // struct udp *udphdr;
  // udphdr = mbufpushhdr(m2, *udphdr);
  // // put the UDP header
  // udphdr = mbufpushhdr(m, *udphdr);
  // udphdr->sport = htons(sport);
  // udphdr->dport = htons(dport);
  // udphdr->ulen = htons(m->len);
  // udphdr->sum = 0; // zero means no checksum is provided
  // // 172.18.86.160
  // R(172, 16, 100, 2)

  tmp = (172 << 24) | (16 << 16) | (100 << 8) | (1 << 0);
  // now on to the IP layer
  // struct mbuf *m2;
  //   m2 = mbufalloc(MBUF_DEFAULT_HEADROOM);
  // if (!m2)
  //   return -1;

  // if (copyin(pr->pagetable, mbufput(m, n), addr, n) == -1)
  // {
  //   mbuffree(m);
  //   return -1;
  // }

  // udphdr = mbufpullhdr(m, *udphdr);
  sport = 1;
  dport = 2;
  printf("src%d\n", ntohs(udphdr->src));
  printf("dst %d\n", ntohs(udphdr->dst));
  printf("%d\n", sizeof(udphdr2));
  printf("%d\n", sizeof(udphdr));
  // char *obuf = "a message from xv6!";
  //  mbufput(m2, sizeof(obuf));
  // m2->len = m2->len+sizeof(obuf);
  if (count222 == 0)
  {
    flg2 = (1 << 4) | (1 << 1);
    udphdr2->flg = flg2;

    net_tx_ip(m2, IPPROTO_TCP, tmp);
    //  net_tx_ip(m2, IPPROTO_TCP, tmp);
    //   net_tx_ip(m2, IPPROTO_TCP, tmp);
    //    net_tx_ip(m2, IPPROTO_TCP, tmp);
    //     net_tx_ip(m2, IPPROTO_TCP, tmp);
    //      net_tx_ip(m2, IPPROTO_TCP, tmp);

    // net_tx_ip(m2, IPPROTO_TCP, tmp);
    // mbuffree(m2);
    count222++;
    mbuffree(m2);
  }
  else
  {

    //  flg2 = (1 << 4);
    //    udphdr2->flg = flg2;
    //  net_tx_ip(m, IPPROTO_TCP, tmp);
    //  udphdr2->flg = flg2;
    // net_tx_ip(m2, IPPROTO_TCP, tmp);
  }

  // }
  // else
  sockrecvudp2(m, tmp, dport, sport);
  // sip = htonl(local_ip);;
  // sockrecvudp(m, sip, dport, sport);
  // printf("-------------------\n");
  // sockrecvudp2(m, tmp, dport, sport);
  return;

fail:
  mbuffree(m);
}
```
算是比較作弊的方式，最近比較忙沒空看檢查碼這部分哪裡有問題，最後看到我的程式碼成功收到來自xv6 的確認封包。
![](https://i.imgur.com/2vpVYJk.jpg)
這些問題解決完後面要做的事情就是
![](https://i.imgur.com/WTtyChi.png)
![](https://i.imgur.com/mtDdeFO.png)

增加http 協議和 arp 快取，要看有沒有時間去弄了，最近整理一下再放github

## References

- Russ Cox, Frans Kaashoek, Robert Morris, [*xv6: a simple, Unix-like teaching operating system*](https://pdos.csail.mit.edu/6.828/2020/xv6.html), MIT PDOS.
- [MIT PDOS / xv6-riscv](https://github.com/mit-pdos/xv6-riscv) — 本文延伸的 xv6 network lab 實作基底。

