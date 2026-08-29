---
title: "golang rpc"
date: "2022-02-18T15:25:00.002+08:00"
updated: "2022-08-30T14:06:56.486+08:00"
permalink: "/2022/02/golang-rpc.html"
original_url: "https://x8795278.blogspot.com/2022/02/golang-rpc.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8995900153877717262"
tags: ["rpc"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Go_Logo_Blue.svg/1200px-Go_Logo_Blue.svg.png)

# goalng rpc
# server
```go
package main

import (
	"log"
	"net"
	"net/rpc"
)

// 作為rpc的server func，必須接受兩個參數 (duck typing) (request string, reply *string)
// 另外返回值為error，必須為公開的方法

type HelloService struct{}

func (h *HelloService) Hello(request string, reply *string) error {
	*reply = "hello: " + request
	return nil
}

func main() {
	// rpc.Register會將object中所有滿足rpc規則的方法註冊為rpc函數
	// 所有註冊的方法會被放在HelloService服務空間下。
	rpc.RegisterName("HelloService", new(HelloService))

	// 建立聆聽一個tcp連線，
	listner, err := net.Listen("tcp", ":8080")
	if err != nil {
		log.Fatal(err)
	}
	for {
		conn, err := listner.Accept()
		if err != nil {
			log.Fatal(err)
		}

		// rpc.ServeConn在該連線上提供client rpc函數
		go rpc.ServeConn(conn)
	}
}

```
# client
```go

package main

import (
	"fmt"
	"log"
	"net/rpc"
)

func main() {
	// rpc.Dial 連接該rpc服務
	conn, err := rpc.Dial("tcp", ":8080")
	if err != nil {
		log.Fatal(err)
	}

	var reply string
	// 透過conn.Call來使用rpc方法。
	// conn.Call(serviceMethod, args, reply)
	conn.Call("HelloService.Hello", "Jack", &reply)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(reply)
}
```

