---
title: "golang websocket"
date: "2022-02-07T02:52:00.001+08:00"
updated: "2022-02-07T02:52:06.394+08:00"
permalink: "/2022/02/golang-websocket.html"
original_url: "https://x8795278.blogspot.com/2022/02/golang-websocket.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-7289277045539111925"
tags: ["Go"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Go_Logo_Blue.svg/1200px-Go_Logo_Blue.svg.png)

# golang websocket
![](https://i.imgur.com/cyAmKAC.png)

# server
```go
package main

import (
	"log"
	"net/http"

	"github.com/gorilla/websocket"
)

func main() {
	upgrader := &websocket.Upgrader{
		//如果有 cross domain 的需求，可加入這個，不檢查 cross domain
		CheckOrigin: func(r *http.Request) bool { return true },
	}
	http.HandleFunc("/echo", func(w http.ResponseWriter, r *http.Request) {
		c, err := upgrader.Upgrade(w, r, nil)
		if err != nil {
			log.Println("upgrade:", err)
			return
		}
		defer func() {
			log.Println("disconnect !!")
			c.Close()
		}()
		for {
			mtype, msg, err := c.ReadMessage()
			if err != nil {
				log.Println("read:", err)
				break
			}
			log.Printf("receive: %s\n", msg)
			err = c.WriteMessage(mtype, msg)
			if err != nil {
				log.Println("write:", err)
				break
			}
		}
	})
	log.Println("server start at :8899")
	log.Fatal(http.ListenAndServe(":8899", nil))
}

```
# client
```go
package main

import (
	"log"

	"github.com/gorilla/websocket"
)

func main() {

	c, _, err := websocket.DefaultDialer.Dial("ws://127.0.0.1:8899/echo", nil)
	if err != nil {
		log.Fatal("dial:", err)
	}
	defer c.Close()
	for {
		err = c.WriteMessage(websocket.TextMessage, []byte("hello x213212y"))
		if err != nil {
			log.Println(err)
			return
		}
		_, msg, err := c.ReadMessage()
		if err != nil {
			log.Println("read:", err)
			return
		}
		log.Printf("receive: %s\n", msg)
	}

}

```

