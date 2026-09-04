---
title: "Spring Cloud 微服務入門 (三) Eureka + Consumer (Rest+Ribbon) 調用 Service"
date: "2019-12-25T20:36:00.005+08:00"
updated: "2019-12-26T03:32:56.955+08:00"
permalink: "/2019/12/spring-cloud-eureka-consumer-restribbon.html"
original_url: "https://x8795278.blogspot.com/2019/12/spring-cloud-eureka-consumer-restribbon.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-7256529811838663087"
tags: ["ribbon", "Spring Cloud", "Tutorial"]
layout: post
---

# Eureka + Consumer (Rest+Ribbon)

![](https://i.imgur.com/SVK61Uq.png) 今天要做的就是這一個部分，微服務的核心就是一個由互向獨立 微服務組成，不同的服務之間可以透過一些輕量級通訊協定來進行溝通 比如說 RPC, HTTP 等，不同服務可以用個別不同的的語言進行開發。

# 目錄結構

# Provider ![](https://i.imgur.com/OXUUgTj.png) Consumer ![](https://i.imgur.com/8yfebc7.png)

# Ribbon 核心

比較常見的有 - ServerList 用於獲取地址列表。它既可以是靜態的(提供一組固定的地址)，也可以是動態的(從註冊中心中定期查詢地址列表)。 - ServerListFilter 僅當使用動態ServerList時使用，用於在原始的服務列表中使用一定策略過慮掉一部分地址。 - IRule 選擇一個最終的服務地址作為LB結果。選擇策略有輪詢、根據響應時間加權、斷路器(當Hystrix可用時)等。 Ribbon在工作時首選會通過ServerList來獲取所有可用的服務列表，然後通過ServerListFilter過慮掉一部分地址，最後在剩下的地址中通過IRule選擇出一台服務器作為最終結果。

# Ribbon 負載均衡策略介紹

- 簡單輪詢負載均衡（RoundRobin） 以輪詢的方式依次將請求調度不同的伺服器，即每次調度執行i = (i + 1) mod n，並選出第i台伺服器。
- 隨機負載均衡 （Random） 隨機選擇狀態為UP的Server
- 加權回應時間負載均衡 （WeightedResponseTime） 根據相應時間分配一個weight，相應時間越長，weight越小，被選中的可能性越低。
- 區域感知輪詢負載均衡（ZoneAvoidanceRule） 複合判斷server所在區域的性能和server的可用性選擇server

# 改造 Service Provider

這邊我們要產生兩個 Service 兩個 Service 配置檔只有 port 不同如下 application.yml;

```
eureka: client: serviceUrl: defaultZone: http://localhost:8761/eureka/ spring: application: name: eureka-provider server: port: 8081 // 另一個 設為8082
```

# Provider main

EurekaServiceProviderApplication.java

```
@SpringBootApplication @EnableEurekaClient @RestController public class EurekaServiceProviderApplication { @Value("${server.port}") String port; @RequestMapping("/") public String home() { return "Hello world" + port; } public static void main(String[] args) { SpringApplication.run(EurekaServiceProviderApplication.class, args); } }
```

# Ribbon Consumer 依賴配置

pom.xml

```
<--eureka 客戶端--> <dependency> <groupId> org.springframework.cloud </groupId> <artifactId> spring-cloud-starter-netflix-eureka-server </artifactId> </dependency> <--Ribbon 客戶端--> <dependency> <groupId> org.springframework.cloud </groupId> <artifactId> spring-cloud-starter-netflix-ribbon </artifactId> </dependency>
```

# Consumer Main

EurekaServiceRibbonConsumer.java

```
@SpringBootApplication @EnableDiscoveryClient public class EurekaServiceRibbonConsumer { @LoadBalanced @Bean RestTemplate restTemplate() { return new RestTemplate(); } public static void main(String[] args) { SpringApplication.run(EurekaServiceRibbonConsumer.class, args); } }
```

# RibbonConsumerCotroller

這邊 Ribbon 會去跟 Eureka 取得目前註冊列表目前可用的清單

```
@RestController public class ConsumerController { @Autowired private RestTemplate restTemplate; @GetMapping(value = "/hello") public String hello() { return restTemplate.getForEntity("http://eureka-provider/", String.class).getBody(); } }
```

# 啟動順序

# Eureka Server - > Service Provider *2 - > Ribbon Consumer

# 運行畫面

![](https://i.imgur.com/DEZqpl7.png) 依序啟動後 Ribbon 預設策略為輪巡 ![](https://i.imgur.com/cOIk9j2.png) ![](https://i.imgur.com/VROYXAT.png) 大家可以試試看兩個 Provider 全關 是不是會出現轉圈圈，這個地方可以用Hystrix 斷路器下面幾章再做詳細講解，下一張先講Fegin 如何更好的呼叫我們的service。
