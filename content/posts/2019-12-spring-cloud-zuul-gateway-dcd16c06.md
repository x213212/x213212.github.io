---
title: "Spring Cloud 微服務入門 (六) Zuul gateway入門"
date: "2019-12-26T20:43:00.002+08:00"
updated: "2020-01-16T10:59:24.530+08:00"
permalink: "/2019/12/spring-cloud-zuul-gateway.html"
original_url: "https://x8795278.blogspot.com/2019/12/spring-cloud-zuul-gateway.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2433003063069291078"
tags: ["Spring Cloud", "Tutorial", "Zuul"]
layout: post
---

![](https://i.imgur.com/y9IoF7D.png)

# Zuul gateway入門

部分參考 <https://www.ymq.io/2017/12/10/spring-cloud-zuul/> 前面如果比較重要的概念目前還太淺不能做總結，交給大神做整理觀念比較重要 服務網關是微服務架構中一個不可或缺的部分。通過服務網關統一向外系統提供REST API的過程中，除了具備服務路由、均衡負載功能之外，它還具備了權限控制等功能。 Spring Cloud Netflix中的Zuul就擔任了這樣的一個角色，為微服務架構提供了前門保護的作用，同時將權限控制這些較重的非業務邏輯內容遷移到服務路由層面，使得服務集群主體能夠具備更高的可複用性和可測試性。 路由在微服務體系結構的一個組成部分。例如，/可以映射到您的Web應用程序，/api/users映射到用戶服務，並將/api/shop映射到商店服務。 Zuul是Netflix的基於JVM的路由器和服務器端負載均衡器。 Netflix使用Zuul進行以下操作： - 認證 - 洞察 - 壓力測試 - 金絲雀測試 - 動態路由 - 服務遷移 - 負載脫落 - 安全 - 靜態響應處理 - 主動/主動流量管理 Zuul的規則引擎允許基本上寫任何JVM語言編寫規則和過濾器，內置Java和Groovy。 什麼是服務網關 服務網關 = 路由轉發 + 過濾器 1. 路由轉發：接收一切外界請求，轉發到後端的微服務上去； 2. 過濾器：在服務網關中可以完成一系列的橫切功能，例如權限校驗、限流以及監控等，這些都可以通過過濾器完成（其實路由轉發也是通過過濾器實現的）。 為什麼需要服務網關 上述所說的橫切功能（以權限校驗為例）可以寫在三個位置： 每個服務自己實現一遍 寫到一個公共的服務中，然後其他所有服務都依賴這個服務 寫到服務網關的前置過濾器中，所有請求過來進行權限校驗 第一種，缺點太明顯，基本不用；第二種，相較於第一點好很多，代碼開發不會冗餘，但是有兩個缺點： 由於每個服務引入了這個公共服務，那麼相當於在每個服務中都引入了相同的權限校驗的代碼，使得每個服務的jar包大小無故增加了一些，尤其是對於使用docker鏡像進行部署的場景，jar越小越好； 由於每個服務都引入了這個公共服務，那麼我們後續升級這個服務可能就比較困難，而且公共服務的功能越多，升級就越難，而且假設我們改變了公共服務中的權限校驗的方式，想讓所有的服務都去使用新的權限校驗方式，我們就需要將之前所有的服務都重新引包，編譯部署。 - 而服務網關恰好可以解決這樣的問題： 將權限校驗的邏輯寫在網關的過濾器中，後端服務不需要關注權限校驗的代碼，所以服務的jar包中也不會引入權限校驗的邏輯，不會增加jar包大小； 如果想修改權限校驗的邏輯，只需要修改網關中的權限校驗過濾器即可，而不需要升級所有已存在的微服務。 - 所以，需要服務網關！！！

# 服務網關技術選型

![](https://i.imgur.com/AHuy4r2.png) 引入服務網關後的微服務架構如上，總體包含三部分：服務網關、open-service和service。 1. 總體流程： 服務網關、open-service和service啟動時註冊到註冊中心上去； 用戶請求時直接請求網關，網關做智能路由轉發（包括服務發現，負載均衡）到open-service，這其中包含權限校驗、監控、限流等操作 open-service聚合內部service響應，返回給網關，網關再返回給用戶 2. 引入網關的注意點 增加了網關，多了一層轉發（原本用戶請求直接訪問open-service即可），性能會下降一些（但是下降不大，通常，網關機器性能會很好，而且網關與open-service的訪問通常是內網訪問，速度很快）； 網關的單點問題：在整個網絡調用過程中，一定會有一個單點，可能是網關、nginx、dns服務器等。防止網關單點，可以在網關層前邊再掛一台nginx，nginx的性能極高，基本不會掛，這樣之後，網關服務就可以不斷的添加機器。但是這樣一個請求就轉發了兩次，所以最好的方式是網關單點服務部署在一台牛逼的機器上（通過壓測來估算機器的配置），而且nginx與zuul的性能比較，根據國外的一個哥們儿做的實驗來看，其實相差不大，zuul是netflix開源的一個用來做網關的開源框架； 網關要盡量輕。 3. 服務網關基本功能 智能路由：接收外部一切請求，並轉發到後端的對外服務open-service上去； 注意：我們只轉發外部請求，服務之間的請求不走網關，這就表示全鏈路追踪、內部服務API監控、內部服務之間調用的容錯、智能路由不能在網關完成；當然，也可以將所有的服務調用都走網關，那麼幾乎所有的功能都可以集成到網關中，但是這樣的話，網關的壓力會很大，不堪重負。 權限校驗：只校驗用戶向open-service服務的請求，不校驗服務內部的請求。服務內部的請求有必要校驗嗎？ API監控：只監控經過網關的請求，以及網關本身的一些性能指標（例如，gc等）； 限流：與監控配合，進行限流操作； API日誌統一收集：類似於一個aspect切面，記錄接口的進入和出去時的相關日誌

# Zuul

```
@EnableZuulProxy @SpringBootApplication public class EurekaServiceZuulApplication { public static void main(String[] args) { SpringApplication.run(EurekaServiceZuulApplication.class, args); } }
```

# 設定檔

application.yml

```
spring: application: name: zuul-service server: port: 9000 #zuul: # routes: # blog: # path: /ymq/**# url: https://www.ymq.io/about eureka: client: serviceUrl: defaultZone: http://localhost:8761/eureka/ zuul: routes: api: path: /** serviceId: eureka-provider
```

# 服務啟動

![](https://i.imgur.com/YGBlva6.png) 可以看到我的參數是用? 因為 我們是直接調用Provider 用的是**@RequestParam** 有此概念我們下一章來結合更早之前的 Security ,硬幹看能不能接的上!
