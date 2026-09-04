---
title: "Spring Cloud 微服務入門 (三) Eureka + Consumer (Feign) 調用 Service"
date: "2019-12-26T07:43:00.001+08:00"
updated: "2020-01-16T10:59:24.619+08:00"
permalink: "/2019/12/spring-cloud-eureka-consumer-feign.html"
original_url: "https://x8795278.blogspot.com/2019/12/spring-cloud-eureka-consumer-feign.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-4740179297433260740"
tags: ["feign", "Spring Cloud", "Tutorial"]
layout: post
---

![](https://i.imgur.com/PrtpDca.png) Feign簡介

Feign是一個聲明式的偽Http客戶端，它使得寫Http客戶端變得更簡單。
使用Feign，只需要創建一個介面並註解，它具有可插拔的註解特性，可使用Feign 註解和JAX-RS註解，Feign支持可插拔的編碼器和解碼器，Feign預設整合了Ribbon，並和Eureka結合，預設實現了負載均衡的效果。
Feign 具有如下特性：
可插拔的註解支持，包括Feign註解和JAX-RS註解  

支持可插拔的HTTP編碼器和解碼器  

支持Hystrix和它的Fallback  

支持Ribbon的負載均衡  

支持HTTP請求和回應的壓縮Feign是一個聲明式的Web Service客戶端，它的目的就是讓Web Service呼叫更加簡單。它整合了Ribbon和Hystrix，從而不再需要顯式地使用這兩個組件。 Feign還提供了HTTP請求的模板，通過編寫簡單的介面和註解，就可以定義好HTTP請求的參數、格式、地址等資訊。接下來，Feign會完全代理HTTP的請求，我們只需要像呼叫方法一樣呼叫它就可以完成服務請求。  

簡而言之：Feign能幹Ribbon和Hystrix的事情，但是要用Ribbon和Hystrix自帶的註解必須要引入相應的jar包才可以。
# 環境準備

如果已經有前面幾章跟著環境一起做大概就會有

- Eureka Service
- Eureka Provider *2
- Ribbon Consumer

等等我們會來用 Feign 完成一次服務呼叫範例
# 配置設定

application.yml
```
eureka:
  client:
    serviceUrl:
      defaultZone: http://localhost:8761/eureka/

spring:
  application:
    name: feign-consumer

server:
  port: 9000
```
# Feign Consumer

```
@SpringBootApplication
@EnableDiscoveryClient
@EnableFeignClients
public class EurekaServiceFeignConsumer {
 

 public static void main(String[] args) {
  SpringApplication.run(EurekaServiceFeignConsumer.class, args);
 }

}
```
# 定義介面

HomeClient.class  

這邊就是呼叫 eureka-provider 裡的 /,  

也就是從我們的Eureka 裡面已經註冊過的service  

Provider *2 裡面 home () 的方法
```
@FeignClient("eureka-provider")
public interface HomeClient {
 @GetMapping("/")
 String consumer();
}
```
# Controller

讓訪問 Fegin “/home” ,能導向我們剛剛寫的介面homeClient裡面的 consumer 方法
```
@RestController
public class ConsumerController {
  @Autowired
     private HomeClient homeClient;

     @GetMapping(value = "/hello")
     public String hello() {
         return homeClient.consumer();
     }
}
```
# 服務啟動

![](https://i.imgur.com/H70yjhA.png)

![](https://i.imgur.com/rzFutjP.png)

  

![](https://i.imgur.com/DdQJFIa.png)

下面一章就會寫  

如何呼叫service 傳參數，本來打算在這一章解決的，後來發現也算是一個坑，我把這一篇獨立出來。
