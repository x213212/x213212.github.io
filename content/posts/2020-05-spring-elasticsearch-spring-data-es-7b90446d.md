---
title: "Spring 基於 Elasticsearch 搜尋商品 (二) spring data es 踩坑 到使用 Java High Level REST Client 連接 es"
date: "2020-05-18T11:42:00.002+08:00"
updated: "2020-07-07T07:35:31.580+08:00"
permalink: "/2020/05/spring-elasticsearch-spring-data-es.html"
original_url: "https://x8795278.blogspot.com/2020/05/spring-elasticsearch-spring-data-es.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-7918312750638080350"
tags: ["elasticsearch", "HighLevelRESTClient", "spring boot", "Tutorial"]
layout: post
---

![](https://i.imgur.com/wffZ6bK.png)

# 基於 Elasticsearch 搜尋商品
踩坑中ing , 修改為 Java high-level REST client 連接 Elasticsearch

# 更換版本
![](https://i.imgur.com/QEcCKsp.png)
>2020-05-17 21:30:23.271  INFO 18644 --- [           main] o.s.d.elasticsearch.support.VersionInfo  : Version Elasticsearch Client in build: 7.6.2
2020-05-17 21:30:23.271  INFO 18644 --- [           main] o.s.d.elasticsearch.support.VersionInfo  : Version Elasticsearch Client used: 7.6.2
2020-05-17 21:30:23.271  INFO 18644 --- [           main] o.s.d.elasticsearch.support.VersionInfo  : Version Elasticsearch cluster: 6.2.2
2020-05-17 21:30:23.271  WARN 18644 --- [           main] o.s.d.elasticsearch.support.VersionInfo  : Version mismatch in between Elasticsearch Client and Cluster: 7.6.2 - 6.2.2
>

在前一個章節演示是直接下載我們的 es版本 6.2， 帶是我們的 spring boot maven 預設 pom.xml 會是
```xml
	<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-data-elasticsearch</artifactId>
	</dependency>
```
前一章節可能要對 pom.xml 去選擇匹配版本
![](https://i.imgur.com/8Ip3IlA.png)
位於官方教學文檔這邊要選擇相對應匹配的版本 當我降到 6.2 得版本時候 發現 配置檔 也就是 appliaction.yml
找不到我們的
spring.data.elasticsearch.repositories.cluster-name= elasticsearch
spring.data.elasticsearch.repositories.cluster-nodes=  127.0.0.1:9300

https://docs.spring.io/spring-data/elasticsearch/docs/4.0.0.RELEASE/reference/html/#preface.metadata
```xml
<dependency>
  <groupId>org.springframework.data</groupId>
  <artifactId>spring-data-elasticsearch</artifactId>
  <version>${version}.RELEASE</version>
</dependency>
```
![](https://i.imgur.com/fouFgMq.png)

所以我決定還是維持我們的 spring boot 最新版 也就是spring-boot-starter-data-elasticsearch 客戶端  4.0 版本
# install elasticsearch 7.6.2 docker 單點部屬

> docker pull docker.elastic.co/elasticsearch/elasticsearch:7.6.2
> docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.6.2
>
https://www.elastic.co/downloads/past-releases#elasticsearch
![](https://i.imgur.com/Bt37fEh.png)

# install elasticsearch 7.6.2 ik
![](https://i.imgur.com/NFjAQs4.png)

>//進入容器
docker exec -it es /bin/bash
// 使用bin目录下的elasticsearch-plugin install安装ik插件
bin/elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v7.6.2/elasticsearch-analysis-ik-7.6.2.zip
// 再重启下容器
docker restart es
>
![](https://i.imgur.com/I7DeEJG.png)

>
>https://www.elastic.co/guide/en/elasticsearch/plugins/current/plugin-management-custom-url.html

![](https://i.imgur.com/TTzOvjz.png)
# 測試連接
![](https://i.imgur.com/n7SXIvl.png)
延伸閱讀
https://www.jianshu.com/p/d8b0c736070f

# 選擇連接客戶端
https://juejin.im/post/5d63cae7f265da03bf0f500b
图中标红的箭头写明了，不推荐TransportClient。wtf，spring-boot-starter-data-elasticsearch就是使用的这种方式链接，居然不推荐。马上去官网找相关资料。如下图：
https://zhuanlan.zhihu.com/p/42763550

Java REST Client
Java REST Client 有两种版本:

Java Low Level REST Client
Java High Level REST Client
Java高级别REST客户端（The Java High Level REST Client）以后简称高级客户端，内部仍然是基于低级客户端。它提供了更多的API，接受请求对象作为参数并返回响应对象，由客户端自己处理编码和解码。

每个API都可以同步或异步调用。 同步方法返回一个响应对象，而异步方法的名称以async后缀结尾，需要一个监听器参数，一旦收到响应或错误，就会被通知（由低级客户端管理的线程池）。

Java high-level REST client
**Java high-level REST client 是目前官方推荐使用的客户端**
High Level REST Client 与 Elasticsearch 具有相同的发布周期。

故我们能够使用最新版的 Elasticsearch。

兼容性
使用 High Level REST Client 与 Elasticsearch 进行通信，主版本号需要一致，次版本号不必相同，因为它是向前兼容的。次版本号小于等于Elasticsearch的都可以。这意味着它支持与更高版本的Elasticsearch进行通信。

# Elasticsearch index read-only
![](https://i.imgur.com/irpmEnp.png)
```
原因

关于 ES 中的磁盘分配决策策略：

cluster.routing.allocation.disk.threshold_enabled 默认为 true，设置为 false 禁用磁盘分配决定器。

cluster.routing.allocation.disk.watermark.low 控制磁盘使用率的低水位线。它的默认值为 85%，这意味着 Elasticsearch 不会将分片分配给使用了超过 85％ 磁盘的节点。

cluster.routing.allocation.disk.watermark.high 控制高水位线。默认为 90%，表示 Elasticsearch 将尝试将分片从磁盘使用率超过 90％ 的节点移到其他节点。

cluster.routing.allocation.disk.watermark.flood_stage 默认为 95%，这意味着在每个节点上分配了一个或多个分片的每个索引上强制执行一个只读索引块（），一旦有足够的磁盘空间可用于继续进行索引操作，则必须手动解除限制。

cluster.info.update.interval 默认为 30s，Elasticsearch 应该多久检查一次集群中每个节点的磁盘使用情况。

 blocked by: [FORBIDDEN/12/index read-only / allow delete (api)];"}]
```

![](https://i.imgur.com/8FNNCjN.png)
![](https://i.imgur.com/Ky9VQBu.png)
https://zhuanlan.zhihu.com/p/34097299
https://blog.csdn.net/dyr_1203/article/details/85619238
根目錄 檔案不足
![](https://i.imgur.com/Lx7hEPS.png)
![](https://i.imgur.com/KfhKpvA.png)
```json
http://192.168.99.100:9200/_cluster/settings
 {
 "transient": {
    "cluster.routing.allocation.disk.threshold_enabled": "false"

  }
 }
```
```json
http://192.168.99.100:9200/persondata/_settings
{
    "index":{
        "blocks":{
            "read_only_allow_delete":"false"
        }
    }
}
```
其中原因就是因為我們從 docker 載 下來的映像檔檔 磁碟區分片策略問題
透過上圖已經知道超過預設 95% 我們這邊只是實驗用途，假設部屬到其他台機器則自行定義磁碟區分片策略限制

關閉後 我們就可以對我們的資料進行 實作我們的crud的功能囉

