---
title: "以websotmp 連接 rabbitmq 紀錄"
date: "2020-06-24T20:51:00.002+08:00"
updated: "2020-07-07T07:38:12.245+08:00"
permalink: "/2020/06/websotmp-rabbitmq.html"
original_url: "https://x8795278.blogspot.com/2020/06/websotmp-rabbitmq.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3230685055650687717"
tags: ["reactjs", "Tutorial"]
layout: post
---

![](https://miro.medium.com/max/3600/1*h8d-4wYLN9wwiEsLAA_5yg.jpeg)

# 以 Websocket STOMP 與 rabbitmq 溝通

# 啟用 Web STOMP
> rabbitmq-plugins enable rabbitmq_web_stomp
>

![](https://i.imgur.com/X25TUDS.png)

# 引入 js WebSocket
> 把 [stomp-websocket](https://github.com/jmesnil/stomp-websocket/tree/master/lib) \lib\stomp.js
Add support for receiving fragmented STOMP frames. These can orginate…
>
```javascript
<!-- include the client library -->
<script src="stomp.js"></script>
```
![](https://i.imgur.com/p87VGvx.png)

# docker 記得把 端口 暴露
> port 15672

![](https://i.imgur.com/6nloqhM.png)

# Sample Code

```javascript
var ws = new WebSocket('ws://127.0.0.1:15674/ws');
var client = Stomp.over(ws);

var on_connect = function() {
    console.log('connected');
};
var on_error =  function() {
    console.log('error');
};

```

發送消息:
```javascript
client.send('/exchange/交換機名字/路由鍵', {}, "Hello");
```

訂閱交換機
```javascript
client.subscribe('/exchange/交換機名字/路由鍵', function(frame){}, {});
```
可以對 交換機內容做封裝
這邊是針對 我自己額外寫的一個 sha 根據登陸名稱來 產生 sha256
因為 假設都是同一組 queue 這樣的話，這樣 當兩個 client 同時訂閱同一個 queue 的話 會變成 queue 裡面有兩個 client 好像是 ha模式?
意味者 執行 上方 發送訊息 則 假設 queue 有兩個 client,也就是 a和 b 那麼 第一次呼叫後 則會 a收到訊息 再來就是 b 這樣循環下去
[延伸閱讀 三种Exchange模式 ](https://blog.csdn.net/u013045437/article/details/71710067)
```javascript
      var sha =sha256(loginName);
      client.subscribe('/exchange/amq.fanout/test', this.AmqpReturn, {
        'x-queue-name':sha,
        'durable': true
      });
```
擴展:
```javascript
  AmqpReturn(frame) {
    
    var obj = JSON.parse(frame.body);
  
    console.log(obj.data);
  }
```

其他參數:
除了這裡用到的參數外，還支持下面的隊列參數：

durable (aliased as persistent)：持久化
auto-delete：自动删除
exclusive：独占
還額外支持 x- 參數控制死信、隊列和消息等：

x-dead-letter-exchange
x-dead-letter-routing-key
x-expires
x-message-ttl
x-max-length
x-max-length-bytes
x-overflow
x-max-priority

