---
title: "Golang Install On Ubutun"
date: "2018-09-26T20:43:00.000+08:00"
updated: "2018-09-30T04:47:33.212+08:00"
permalink: "/2018/09/golang-install-with-ubutun.html"
original_url: "https://x8795278.blogspot.com/2018/09/golang-install-with-ubutun.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-712838410230770647"
tags: ["Go", "Tutorial"]
layout: post
---

## 接觸原因

## ---

搭建一個框架，想說在一般電腦中，架設伺服器的有沒有可以兼顧速度和執行效率的語言，就是GO了，其實在以前有寫過一個小範例，覺得蠻難寫的，那時Golang剛推出，可能是因為那時候還沒接觸Pyhton，以後會陸陸續續改一些以前的小專案看看，接下來看一下安裝過程吧!  

[![](https://i.imgur.com/7yNcU9W.png)](https://i.imgur.com/7yNcU9W.png)
## 想試一下也可以來這邊看看

[A Tour of Go](https://tour.golang.org/welcome/1)
那麼我們開始吧
[![](https://i.imgur.com/MZOcpEx.png)](https://i.imgur.com/MZOcpEx.png)
  
##

## Install

## ---

[Install golang](https://golang.org/doc/install?download=go1.11.linux-amd64.tar.gz)  

我們把環境裝在linxu吧，以後還要紀錄一下Ducker安裝過程等等。  

[![](https://i.imgur.com/x3OAnnX.png)](https://i.imgur.com/x3OAnnX.png)
在Windows子系統下我們可以直接複製到/mnt/c掛載區直接把我們的壓縮檔解壓縮並安裝。  

  

[![](https://i.imgur.com/VgjXn5o.png)](https://i.imgur.com/VgjXn5o.png)
  

  
```
sudo tar -C /usr/local -xzf go1.x.x.linux-amd64.tar.gz
```
[![](https://i.imgur.com/ssNsoTA.png)](https://i.imgur.com/ssNsoTA.png)
  

  
```
export PATH=$PATH:/usr/local/go/bin
```
[![](https://i.imgur.com/SRFRhtl.png)](https://i.imgur.com/SRFRhtl.png)
```html
<script src="https://gist.github.com/x213212/fc6c3ed8221aee258c006c1bad527d4d.js"></script>
```
存成hello.go，之後執行看看吧!  

[![](https://i.imgur.com/VU9OX4T.png)](https://i.imgur.com/VU9OX4T.png)
  
```
go build hello.go
 ./hello
```
[![](https://i.imgur.com/hra90zs.png)](https://i.imgur.com/hra90zs.png)
  

  
## 環境參數

## ---

  
```
go env
```
[![](https://i.imgur.com/HHWIcpD.png)](https://i.imgur.com/HHWIcpD.png)
  

比較重要的是  

  

  
```
GOPATH="/home/x213212/go"
```
  

- src    - 放Go程式碼的地方
- pkg  - 放Go package的地方
- bin   - 編譯好的執行檔會放在這裡
## 學習資源

## ---

[Go by Example](https://gobyexample.com/)  

[golangpkg](https://golang.org/pkg/)
