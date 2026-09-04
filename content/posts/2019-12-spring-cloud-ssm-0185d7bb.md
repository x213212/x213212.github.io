---
title: "Spring Cloud 微服務入門 (一) SSM架構 到 微服務架構 變化"
date: "2019-12-25T04:10:00.002+08:00"
updated: "2019-12-26T03:15:49.507+08:00"
permalink: "/2019/12/spring-cloud-ssm.html"
original_url: "https://x8795278.blogspot.com/2019/12/spring-cloud-ssm.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3863716623837348074"
tags: ["Java", "Spring Cloud", "Tutorial"]
layout: post
---

![](https://i.imgur.com/JIyAzyX.png)

前面幾章已經大致上了解 微服務，大概在幹嘛了吧，終於可以進到使用 Spring Cloud 了，假設前面幾個框架沒學錯的話(在家修練)，雖然前面只有說到 zookeeper，之前有找到 spring boot+ rpc +zookeeer 實作有點多有空再玩哈哈，反正先有下面這些概念，以後想自幹框架自己再慢慢玩也不遲 XD
下面就稍微總結一下我對微服務架構初步的認識  

在練習畫流程圖意外發現有這個咚咚  

<https://online.visual-paradigm.com/drive/#diagramlist:proj=0&new=AlibabaCloudArchitectureDiagram>
  

然後...........沒想到那個阿里巴巴獵頭居然是真的 xd  

![](https://i.imgur.com/kgLGDTT.png)

  

  

應該在面試 java 深一點就會被電爆吧xd，來認識一下阿里巴巴大牛也不錯哈哈  

有任何面試心得進度再來分享一下，廢話太多來進入正題
# Spring Cloud

裡面整合了，如何快速搭建一個微服務的架構，下面我就來稍微整理一下目前對微服務的理解。  

- 服務高可用問題 - Eureka
- 負載平衡與呼叫服務 - Ribbon
- 呼叫異常處理 - Hystrix
- 呼叫服務更加簡化 - fegin
- Api gateway - Zuul
# 微服務架構

一般在傳統系統中要拆成微服務大概長這樣，  

這是後面要達成的目標，下面會稍微介紹各個組件大概是什麼，以及要解決的問題  

![](https://i.imgur.com/9iTFNGf.png)

  

這張圖算是簡單版的微服務架構  

下面會對這些元件做一一介紹
# 服務高可用問題，擴展能力等等 - Eureka

![](https://i.imgur.com/iXlbIO9.png)

也就是圖中這些地方  

這裡也是之前說的要解決高可用的問題，  

這邊使用了 Eureka，跟 zookeeper 很像，  

主要就是把  

server1 2 3 的服務都註冊給 Eureka，然後  

我們的用戶端就會透過 Zuul Api gateway 去路由我們的 服務，後面會說 為什麼要再夾一層 Zuul
# 怎麼實現負載平衡 -ribbon

Server 端 負責 負載平衡  

![](https://i.imgur.com/u8kGMPf.png)

  

這邊的話是直接請求 Server，然後請 Server 去幫我們看哪一些可以用 哪一些不能用，返回可以用的服務給 使用者
Client 端 負責 負載平衡  

![](https://i.imgur.com/QH9W7pm.png)

  

呼叫者先去跟 Eureka 去取的 有哪幾台伺服器可以用  

然後返回可以用的 Service，然後使用者再去調用
# 怎麼調用服務 -ribbon

有了上面兩個概念  

![](https://i.imgur.com/1M0GZGU.png)

  

我的的微服務架構目前就可以變成上圖  

之前我常說呼叫服務可以用 Http 和 Rpc 框架這邊如果要自幹的話，就是你服務和服務之間要有共同的協議等等…一堆等著你去涉略 xd
不過官方也幫你整合了解決兩個問題的方案  

![](https://i.imgur.com/SVK61Uq.png)

  

也就是這一塊其實就是可以交給 ribbon
# 服務呼叫異常處理 - Hystrix

Hystrix 斷路器  

![](https://i.imgur.com/KFIA9JP.png)

  

這邊舉例假設有一個一連串的服務  

假設f 節點 出現問題  

![](https://i.imgur.com/igWkatJ.png)

c節點也會出現問題 因為在等 f  

![](https://i.imgur.com/IxwHnD6.png)

在等 c的過程呢 a也會再出現等待的問題  

![](https://i.imgur.com/7u5Jb9o.png)

  

所以很有可能會發生就是 雪崩式 錯誤，系統整就攤掉
那麼 Hystrix 斷路器 是幹嘛的呢?  

![](https://i.imgur.com/YMOl2GG.png)

  

抱歉老人梗，反正 Hystrix 這個東西就是可以讓你額外設定策略看是要立即返回 預設 的 錯誤 Response  

還是你要做額外的動作，設定 Timeout 等等 這邊在實作的時候再細談。
# 如何讓 服務呼叫更加簡化? - fegin

fegin 這個東西裡面有含 ribbon 的東西，和呼叫方式很像我們在 更早之前學 MMS 架構的方式很像，採用注入的方式，這邊可能實作的時候會更加明顯稍後探討，解決了 RestTemplte 傳多參數的問題 簡化了 呼叫方式  

等於又再一次的封裝 rabbon，下回仔細分析。
# Api gateway - Zuul

![](https://i.imgur.com/NQui7CJ.png)

主要是在訪問很多服務的時候，向我們一開始實作一個  

簡單的 Restful 的 service 的時候不是有作 如何更安全的呼叫，但是在從SSM 轉到 微服務的架構中，  

我們的服務變成更多，所以我們可以把驗證邏輯寫在 API gateway，或者做限流等等控管，  

而我們的 Api gateway 也會根據 Eureka 去取得可用的 伺服器清單，是不是覺得全部都邦我們做完了哈哈 看完都不想造輪子了。

- 權限控制
- 路由
- 監控
- 限流
- 日誌  
  請求次數很重要XD  
  (上次就是kucoin bug 寫了一個比特幣自動交易程式，根據買賣量來下單，不到一天 我的 ip 就被鎖了 xd  
  
  ![](https://i.imgur.com/KJE6XqX.png)

那麼最後就是  

![](https://i.imgur.com/9iTFNGf.png)

  

後面當然有很多沒講當然可以用 SpringCloud Bus 去即時更新我們每一個 service 的設定檔，後面有用到再說。  

明天吧xd 再仔細對這幾個目標去做實作，總而言之SpringCloud  就是一個 微服務的套餐(另一邊叫做全家桶)。
