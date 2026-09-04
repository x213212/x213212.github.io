---
title: "Spring Cloud 微服務入門 (十) Zipkin 追蹤鏈 rabbitmq 模式"
date: "2019-12-31T14:01:00.000+08:00"
updated: "2020-01-16T10:59:24.704+08:00"
permalink: "/2019/12/spring-cloud-zipkin-rabbitmq.html"
original_url: "https://x8795278.blogspot.com/2019/12/spring-cloud-zipkin-rabbitmq.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6382533988666138511"
tags: ["rabbitmq", "Spring Cloud", "Tutorial", "zipkin"]
layout: post
---

當服務擴增到一定的程度時，併發時候，因為 zipkin 預設 是靠 http 去做傳輸，所以怕 耗到這部份的效能，也不能保證我們的 zipkin server 會不會 掛掉所以我們要一個中間層也就是rabbitmq，所以可以先把 log 發送到 rabbitmq 佇列裡等待被派送到 由他來判斷我們的 zipkin server 狀態是否可以接收我們的 log  

因為 rabbitmq 有重送機制或直到任務成功為止這功能，在任務未完成的時候可以送到依 server 能力 慢慢讓我們的 server 去消化這一大堆的 log，好吧開始。
# 引入rabbitmq依賴

```
<dependency>
 <groupId>org.springframework.boot</groupId>
 <artifactId>spring-boot-starter-amqp</artifactId>
 </dependency>
<dependency>
 <groupId>org.springframework.amqp</groupId>
    <artifactId>spring-rabbit-test</artifactId>
 <scope>test</scope>
</dependency>
```

![](https://i.imgur.com/SIwSJxN.png)

# 設定檔

provider,consumer,zuul 這些地方有想用 zipkin 的地方都要加上
```
eureka:
  client:
    serviceUrl:
      defaultZone: http://localhost:8761/eureka/

spring:
  application:
    name: feign-consumer
  zipkin:
    base-url:  http://192.168.0.146:9411
    sender:
      type: rabbit
    rabbitmq:
      addresses: 192.168.0.146:5672
      password: test
      username: test
      queue: zipkin
feign:
  hystrix:
    enabled: true
    
server:
  port: 9001
```
# rabbitmq

<https://x8795278.blogspot.com/2019/08/websocket-rabbitmq.html>  

上次玩到一半，這邊是安裝還要加上
```
sudo vim  /etc/rabbitmq/rabbitmq.config
```
允許遠端訪問
```
[
{rabbit, [{tcp_listeners, [5672]}, {loopback_users, ["test"]}]}
].
```
```
sudo systemctl start rabbitmq-server
```
# zipkin 啟動

```
java -jar zipkin.jar --zipkin.collector.rabbitmq.addresses=localhost
```
在執行可以先去消耗  

也就是去觸發 我們的 provider  

訊息會被 cache 在 我們的 rabbitmq  

![](https://i.imgur.com/kJ5nj4u.png)

  

服務啟動後  

然後springtool 好Lag我把它移到 vscode了  

![](https://i.imgur.com/gy11be7.png)

  

![](https://i.imgur.com/FaMLR5T.png)

  

![](https://i.imgur.com/32Ef52v.png)

還沒加其他數據每秒大概可以處理500次 反應時間136ms(吧?
```
http://localhost:9000/feign-consumer/hello/1/12?token=Bearer%20eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1Nzc3NzE5OTcsInVzZXJuYW1lIjoiamFjayJ9.-2DWFi3MbbuilGvl0B6jVnmb6TzIWQ_FbH0X2hF1XOU
```

![](https://i.imgur.com/hZueEjB.png)
