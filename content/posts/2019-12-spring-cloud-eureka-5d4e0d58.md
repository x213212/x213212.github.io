---
title: "Spring Cloud 微服務入門 (二) Eureka 服務註冊與發現"
date: "2019-12-25T15:03:00.003+08:00"
updated: "2019-12-26T03:15:49.447+08:00"
permalink: "/2019/12/spring-cloud-eureka.html"
original_url: "https://x8795278.blogspot.com/2019/12/spring-cloud-eureka.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2728698596623628181"
tags: ["Java", "Spring Cloud", "Tutorial"]
layout: post
---

![](https://i.imgur.com/piicpFA.png)

  

下面兩個分別是個別的 service 個別專案不是在同一個專案底下  

![](https://i.imgur.com/GseEi8P.png)

今天要完成的就是昨天說的這一塊
# 新增依賴

```
<dependency>
         <groupId>org.springframework.cloud</groupId>
         <artifactId>
          spring-cloud-starter-netflix-eureka-server
         </artifactId>
    </dependency>
```
# 配置文件properties 改成 yml 格式

example  

application.properties：
```
server.port=8081
 
spring.datasource.type=org.apache.tomcat.jdbc.pool.DataSource
spring.datasource.url=jdbc:mysql://aliyuncs.com:3306/database?useUnicode=true&zeroDateTimeBehavior=convertToNull&autoReconnect=true
spring.datasource.username=root
spring.datasource.password=******
spring.datasource.driver-class-name=com.mysql.jdbc.Driver
```
application.yml :
```
server:
  port: 8082
  
spring:
    datasource:
        name: test
        url: jdbc:mysql://127.0.0.1:3306/database
        username: root
        password: ******
        type: com.alibaba.druid.pool.DruidDataSource
        driver-class-name: com.mysql.jdbc.Driver
```
這邊我們預設的  

![](https://i.imgur.com/x9bzWLz.png)

# 設置 Eureka 配置文件

application.yml  

這一串就是防止自己註冊自己  
```
registerWithEureka: false 
  fetchRegistry: false
```
```
spring:
  cache:
    type : jcache
    jcache:
      config:
        classpath:ehcache.xml
server:
  port: 8761

eureka:
  instance:
    hostname: localhost
  client:
    registerWithEureka: false
    fetchRegistry: false
    serviceUrl:
      defaultZone: http://${eureka.instance.hostname}:${server.port}/eureka/
```
# Eureka Server Main

```
package org.inlighting.security;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cloud.netflix.eureka.server.EnableEurekaServer;

@SpringBootApplication
@EnableCaching
@EnableEurekaServer
public class WebApplication {

    public static void main(String[] args) {
        SpringApplication.run(WebApplication.class, args);
    }
}
```
# Eureka Server 啟用

![](https://i.imgur.com/XmXJOhb.png)

# Service Provider

負責把我們的 Service 註冊到 Eureka 讓他能被消費端找到
# 設置 Eureka 配置文件

```
eureka:
  client:
    serviceUrl:
      defaultZone: http://localhost:8761/eureka/

spring:
  application:
    name: eureka-provider

server:
  port: 8081
```
# Service Provider Main

```
package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.netflix.eureka.EnableEurekaClient;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@EnableEurekaClient
@RestController
public class EurekaServiceProviderApplication {

 @RequestMapping("/")
 public String home() {
       return "Hello world";
 }
 public static void main(String[] args) {
  SpringApplication.run(EurekaServiceProviderApplication.class, args);
 }

}
```
<http://localhost:8761/>  

![](https://i.imgur.com/73BpL0g.png)

  

<http://localhost:8081/>  

![](https://i.imgur.com/BSTJxkb.png)
