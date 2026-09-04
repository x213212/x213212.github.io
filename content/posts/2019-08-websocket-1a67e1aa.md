---
title: "websocket 達到百萬連接?"
date: "2019-08-12T17:58:00.002+08:00"
updated: "2020-07-07T06:33:48.786+08:00"
permalink: "/2019/08/websocket.html"
original_url: "https://x8795278.blogspot.com/2019/08/websocket.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5586515833201085463"
tags: ["Go", "server", "Tutorial", "websocket"]
layout: post
---

在跟技術經理討論過一次，我們的推送 server，將會面臨到有沒有可能斷線  

或者資料遺失的可能性，  

假設一最多只能有 65536 個port 扣掉 連接埠後，剩下  

可用連接埠可能兩三萬，那麼有沒有可能單台 server 就突破 65536 個 port呢 ?  

emmmm…  

在經過一番查詢是有的，那麼就是差實做囉， 我們來架設一波  

首先呢我們要對 linux 進行 一些額外的設定  

至於伺服器方面呢，我們把移到golang 的 websocket 伺服器
client 和 server 是run 在 同一台 虛擬機
# client 端

## docker搭建

<https://joshhu.gitbooks.io/dockercommands/content/Containers/DockerRun.html>  

![](https://i.imgur.com/rhgzXlF.png)

產生 n個 docker 映像檔並執行 client.go 編譯出來的 client  使用 docker 映射到 docker 容器裡 再讓容器 發起 m個連接到 指定 ip 上
```
#!/bin/bash
## This script helps regenerating multiple client instances in different network namespaces using Docker
## This helps to overcome the ephemeral source port limitation
## Usage: ./connect <connections> <number of clients> <server ip>
## Server IP is usually the Docker gateway IP address, which is 172.17.0.1 by default
## Number of clients helps to speed up connections establishment at large scale, in order to make the demo faster

CONNECTIONS=$1
REPLICAS=$2
IP=$3
#go build --tags "static netgo" -o client client.go
for (( c=0; c<${REPLICAS}; c++ ))
do
    docker run -v $(pwd)/client:/client --name 1mclient_$c -d  alpine /client -conn=${CONNECTIONS} -ip=${IP}
done
```
client 發起 10萬連接
```
sudo bash setup.sh 20000 5 192.168.109.129
```
刪除 迴圈產生出來的 docker 映像檔
```
sudo docker rm -f 1mclient_4
sudo docker rm -f 1mclient_3
sudo docker rm -f 1mclient_2
sudo docker rm -f 1mclient_1
sudo docker rm -f 1mclient_0
```
# server 端

## linux 調效篇

這篇講得不錯很容易懂  

<http://blog.udn.com/q928856957/25855941>
<https://blog.csdn.net/xiexingshishu/article/details/43373297>
<https://serverfault.com/questions/769978/sysctl-cannot-stat-proc-sys-net-ipv4-netfilter-ip-conntrack-max-no-such-file>
```
sudo sysctl -w fs.file-max=2000500
sudo sysctl -w fs.nr_open=2000500
sudo sysctl -w net.nf_conntrack_max=2000500
sudo ulimit -n 2000500
sudo sysctl -w net.ipv4.tcp_mem='131072  262144  524288'
sudo sysctl -w net.ipv4.tcp_rmem='8760  256960  4088000'
sudo sysctl -w net.ipv4.tcp_wmem='8760  256960  4088000'
sudo sysctl -w net.core.rmem_max=16384
sudo sysctl -w net.core.wmem_max=16384
sudo sysctl -w net.core.somaxconn=2048
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=2048
sudo sysctl -w /proc/sys/net/core/netdev_max_backlog=2048
sudo sysctl -w net.ipv4.tcp_tw_recycle=1
sudo sysctl -w net.ipv4.tcp_tw_reuse=1
sudo echo 2000500 > /proc/sys/fs/nr_open
```
[https://www.google.com/search?q=centos+開啟+端口&rlz=1C1WPZA_enTW818TW818&oq=centos+開啟+端口&aqs=chrome..69i57.6505j0j7&sourceid=chrome&ie=UTF-8](https://www.google.com/search?q=centos+%E9%96%8B%E5%95%9F+%E7%AB%AF%E5%8F%A3&rlz=1C1WPZA_enTW818TW818&oq=centos+%E9%96%8B%E5%95%9F+%E7%AB%AF%E5%8F%A3&aqs=chrome..69i57.6505j0j7&sourceid=chrome&ie=UTF-8)
## Run server!

組態檔，我們把onlyTestConnect 設為 false
```
{
        "port": 8888,
        "delay": "1m",
        "interval": "1m",
        "totalSize": 1,
        "onlyTestConnect": false
}
```
server.go
```
package main

import (
 "container/list"
 "fmt"
 "golang.org/x/net/websocket"
 "net/http"
 "strconv"
 "time"
 "encoding/json"
 "os"
 "sync"
 "goserver"
 "math/rand"
 //"unsafe"
)

var Config goserver.Configuration
const n = 10
var wsList = [n]*list.List {list.New(),list.New(),list.New(),list.New(),list.New(),list.New(),list.New(),list.New(),list.New(),list.New()}
var locks = [n]sync.RWMutex {}

func wsHandler(ws *websocket.Conn) {
 //p := unsafe.Pointer(&ws)
 //index := ((int)(uintptr(p))) % n
 index := rand.Intn(n)
 lock := locks[index]
 lock.Lock()
 wsList[index].PushBack(ws)  
 lock.Unlock()
 
 for {
  var reply string
  if err := websocket.Message.Receive(ws, &reply); err != nil {
   fmt.Println("Can't receive because of " + err.Error())
   break
  }
 }
 
 lock.Lock()
 for e := wsList[index].Front(); e != nil; e = e.Next() {
  if e.Value.(*websocket.Conn) == ws {
   wsList[index].Remove(e)
   break
  }
 }
 lock.Unlock()
}

func load(configfile string) goserver.Configuration {
 config := goserver.Configuration{}
 file, _ := os.Open(configfile)
 decoder := json.NewDecoder(file)
 err := decoder.Decode(&config)
 if err != nil {
  panic(err.Error())
 }

 return config
}

func main() {
 seed := time.Now().UTC().UnixNano()
 rand.Seed(seed)

 Config = load("config.json")
 
 //http.Handle("/", websocket.Handler(wsHandler))
 http.HandleFunc("/", func(w http.ResponseWriter, req *http.Request) {
  s := websocket.Server{Handler: websocket.Handler(wsHandler)}
  s.ServeHTTP(w, req)
 })
 
 delay, _ := time.ParseDuration(Config.Delay)
 interval, _ := time.ParseDuration(Config.Interval)
 timer := time.NewTimer(delay)
 if !Config.OnlyTestConnect {
  go func() {
   for {
    <-timer.C
    timer.Reset(interval)
    totalLen := 0
    for i :=0; i < n; i++ {
     totalLen += wsList[i].Len()
    }
    if totalLen >= Config.TotalSize {
     fmt.Println("send timestamp to all")
     for i :=0; i < n; i++ {
      i := i
      go func() {
       for e := wsList[i].Front(); e != nil; e = e.Next() {
        var ws = e.Value.(*websocket.Conn)
        now := time.Now().UnixNano() / int64(time.Millisecond)
        err := websocket.Message.Send(ws, strconv.FormatInt(now, 10))
        if err != nil {
         panic("Error: " + err.Error())
        }
       }
      }()

     }     
    } else {
     fmt.Println("current websockets: " + strconv.Itoa(totalLen))
    }
    
   }
  }()
 }

 err := http.ListenAndServe(":"+strconv.Itoa(Config.Port), nil)
 if err != nil {
  panic("Error: " + err.Error())
 }
}
```

![](https://i.imgur.com/0NZ5OXN.png)

  

emm… emmemm. 看起來差不多調校好了??
記憶體吃滿了先開 10w client 玩玩看，不過單台 確實突破 65536 的迷思 (?  

![](https://i.imgur.com/tRdKBON.png)

中間能不能再夾一層 nginx 呢進行更多變化呢或優化呢… 看來要在 買一些洋垃圾組一台 server
# 連接埠重複使用? 假象?

<https://colobu.com/2019/02/23/1m-go-tcp-connection/>  
在看了下數據後 最下面貼文 發現了是不是只是 本地端 的假象?
來實驗一下  
在使用docker 虛擬連接發現docker 創建的連線數是正常的嗎  
開了兩台 client 模擬客戶端 每台上限65536，可以看到 server 確實達到  
接近12萬連線數 所以 這個就取決的server的硬件是否強大囉  

![](https://i.imgur.com/UFUHSP6.png)

  
後面 其中一docker 可能掛了還是怎樣，連線數掉到剩一台client  
數據 大概 滿仔數據 記憶體大概是 快接近 6g cpu除了每個一分鐘回傳滿載  
幾乎 接近10%左右，頻寬 回傳 1.4m
接近 剛才的 部落格實測數據

參考
<https://colobu.com/2019/02/23/1m-go-tcp-connection/>  

<https://github.com/eranyanay/1m-go-websockets>  

<https://github.com/smallnest/C1000K-Servers>
