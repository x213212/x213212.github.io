---
title: "OpenResty + nginx + redis + spring 如何達到高吞吐量伺服器的架構? (二) 壓力測試工具篇"
date: "2019-07-07T15:41:00.001+08:00"
updated: "2019-07-14T00:03:01.261+08:00"
permalink: "/2019/07/openresty-nginx-redis_7.html"
original_url: "https://x8795278.blogspot.com/2019/07/openresty-nginx-redis_7.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2897894180169396920"
tags: ["nginx", "openresty", "Redis", "spring boot", "Tutorial"]
layout: post
---

# 壓力測試工具 ab

安裝壓力測試工具，ab 源自 apache 的壓力測試工具我們來安裝吧  

在学习ab工具之前，我们需了解几个关于压力测试的概念  

1. **吞吐率（Requests per second）**  
   
  概念：服务器并发处理能力的量化描述，单位是reqs/s，指的是某个并发用户数下单位时间内处理的请求数。某个并发用户数下单位时间内能处理的最大请求数，称之为最大吞吐率。  
   
  计算公式：总请求数 / 处理完成这些请求数所花费的时间，即  
   
  Request per second = Complete requests / Time taken for tests

2. **并发连接数（The number of concurrent connections）**  
   
  概念：某个时刻服务器所接受的请求数目，简单的讲，就是一个会话。

3. **并发用户数（The number of concurrent users，Concurrency Level）**  
   
  概念：要注意区分这个概念和并发连接数之间的区别，一个用户可能同时会产生多个会话，也即连接数。

4. **用户平均请求等待时间（Time per request）**  
   
  计算公式：处理完成所有请求数所花费的时间/ （总请求数 / 并发用户数），即  
   
  Time per request = Time taken for tests /（ Complete requests / Concurrency Level）

5. **服务器平均请求等待时间（Time per request: across all concurrent requests）**  
   
  计算公式：处理完成所有请求数所花费的时间 / 总请求数，即  
   
  Time taken for / testsComplete requests  
   
  可以看到，它是吞吐率的倒数。  
   
  同时，它也=用户平均请求等待时间/并发用户数，即  
   
  Time per request / Concurrency Level

  

# install ab

### 安裝壓力測試

**安装压力测试工具ab**
```
yum -y install httpd-tools
```

**压力测试**

- -c:每次并发数为10个
- -n:共发送50000个请求

```
ab -c10 -n50000 http://localhost:6699/
```

  

[![](https://i.imgur.com/VLi8ZNd.png)](https://i.imgur.com/VLi8ZNd.png)
  

下一章節，就是 實作一下 附載平衡 可能會用 redis 叢集，或是單個 redis， 和結合 db 並 觀看 壓力測試工具來看看 有加 緩存的 系統和 一般 的 數據系統的差距。
