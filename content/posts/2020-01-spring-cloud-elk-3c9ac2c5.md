---
title: "Spring Cloud 微服務入門 (十一) ELk 日誌中心搭建與執行 rabbitmq 模式 docker - compose 構建 (一)"
date: "2020-01-01T08:36:00.002+08:00"
updated: "2020-01-16T10:59:24.730+08:00"
permalink: "/2020/01/spring-cloud-elk.html"
original_url: "https://x8795278.blogspot.com/2020/01/spring-cloud-elk.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6544771780230646116"
tags: ["elasticsearch", "elk", "kibana", "Logstash", "rabbitmq", "Tutorial"]
layout: post
---

![](https://i.imgur.com/B6HfPUc.png)

本來想用kafka 看看的，睡醒在弄看看吧，我在想接下來是不是要通通移到docker 上了，乾脆上雲好了xd在看個aws  

![](https://i.imgur.com/U1tqb5j.png)

  

目前整個架構就這樣
# 初步介紹

查看日誌的傳統方法是：登錄操作系統，使用命令工具如cat、tail、sed、awk、grep等等進行過濾輸出後分析，處理少量日誌還好，日誌量大處理效率就沒那麼高了。而且很多情況下開發人員需要查看並分析日誌進行排錯，但他們對Linux命令又不是太熟悉，而且有時候又不能賦予他們服務器權限，更多時候是運維把日誌文件導出來發給開發人員，這無疑會給我們增加工作量。 ELK（Elasticsearch+Logstash+Kibana）架構就是專門為採集、分析、存儲日誌所設計的：
Elasticsearch：基於Lucenne的搜索服務器，提供一個分佈式多用戶的全文搜索引擎，能過做到實時搜索。
Logstash：可以對日誌進行採集、過濾、輸出。
Kibana：可以匯總、分析、搜索日誌數據並提供友好的web界面。
工作流程：logstash agent監控並過濾日誌，為了保證日誌的完整性先將日誌內容輸出到RabbitMQ進行存儲；logstash indexer再把RabbitMQ上的日誌隊列收集後發送給全文搜索服務器Elasticsearch，然後可以用Elasticsearch進行自定義搜索，再通過Kibana來結合自定義搜索進行頁面展示。
# 安裝 ELK

這邊我們使用 docker 主要就是 解決 維運和 開發工程師 環境的不同而弄出來的東西，在微服務時代中可以快速部屬(好像是這樣
然後我也懶得架在linux 開發版了，直接用 docker 比較快一點  

順便複習一下 **docker**，之前在安裝 redis 有用到，  

參考:<https://www.jianshu.com/p/18778a8ee6f0>
玩了快一天 :  

windows10 subsystem Linux不行  

ai開發版不行  

windows 10 home 家用版 不行  

終於可以 關hyper 開 docker 可以  

下次我要灌專業版了，目前灌的是預覽版 一堆正常 docker 都不能裝  

elk 我找了半天  

找了台灣人  

<https://github.com/twtrubiks/docker-elk-tutorial>  

只能她的 docker 可以用，其他版本的 elk 記憶體要求過大，還沒進容器裡就掛了，他裡面還有用 docker-compose 我來小魔改一下，最下面有蒐集的 資料大該就那些範圍
# docker

docker 的網路有三種模式，先挖坑，  

這邊的容器可以看到跟一般不同，學習一下這種方式，  

我用 docker tool 是不能把端口映射到我的電腦上，  

除非 nginx (創辦人好像被告了 或其他 gateway  

<https://github.com/x213212/elk>  

安裝只要
```
docker-compose up 
docker-compose down
```
他預設會抓docker-compose.yml  

也就是下面的東東
```
version: '2'

services:

  elasticsearch:
    build:
      context: elasticsearch/
    volumes:
      - ./elasticsearch/config/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml:ro
    ports:
      - "9200:9200"
      - "9300:9300"
    environment:
      ES_JAVA_OPTS: "-Xmx256m -Xms256m"
    networks:
      - elk

  logstash:
    build:
      context: logstash/
    volumes:
      - ./logstash/config/logstash.yml:/usr/share/logstash/config/logstash.yml:ro
      - ./logstash/pipeline:/usr/share/logstash/pipeline:ro
    ports:
      - "5000:5000"
    environment:
      LS_JAVA_OPTS: "-Xmx256m -Xms256m"
    networks:
      - elk
    depends_on:
      - elasticsearch

  kibana:
    build:
      context: kibana/
    volumes:
      - ./kibana/config/:/usr/share/kibana/config:ro
    ports:
      - "5601:5601"
    networks:
      - elk
    depends_on:
      - elasticsearch
      
  rabbitmq :
    build:
     context: rabbitmq /
    volumes:
      - ./rabbitmq/config/:/usr/share/rabbitmq/config:ro
    ports:
      - "5672:5672"
      - "15672:15672"
    networks:
      - elk
    depends_on:
      - elasticsearch
networks:

  elk:
    driver: bridge
```
這個解決完後大概他會去抓四個程式  

rabbitmq  

Elasticsearch  

Logstash  

Kibana  

![](https://i.imgur.com/J0fLq4i.png)

  

我都調好了，應該沒什麼意外
# Logstash.conf

這個真的雷 全形半形沒log 可以除錯只能用猜的
```
input {
 tcp {
  port => 5000
 }
 rabbitmq {
  type => "all"
  durable => true
  exchange => "ex_logstash"
  exchange_type => "direct"
  key => "lgstash"
  host => "192.168.99.100"
  user => guest
  password => guest
  queue => "faceJob-logstash"
  auto_delete => false
 }
}

## Add your filters / logstash plugins configuration here
output {
 elasticsearch {
  hosts => "elasticsearch:9200"
 }
}
```
# Kibana.yml

```
---
## Default Kibana configuration from kibana-docker.
## from https://github.com/elastic/kibana-docker/blob/master/build/kibana/config/kibana.yml
#
server.name: kibana
server.host: "0"
elasticsearch.url: http://elasticsearch:9200
```
# Elasticsearch

```
---
## Default Elasticsearch configuration from elasticsearch-docker.
## from https://github.com/elastic/elasticsearch-docker/blob/master/build/elasticsearch/elasticsearch.yml
#
cluster.name: "docker-cluster"
network.host: 0.0.0.0

# minimum_master_nodes need to be explicitly set when bound on a public IP
# set to 1 to allow single node clusters
# Details: https://github.com/elastic/elasticsearch/pull/17288
discovery.zen.minimum_master_nodes: 1

## Use single node discovery in order to disable production mode and avoid bootstrap checks
## see https://www.elastic.co/guide/en/elasticsearch/reference/current/bootstrap-checks.html
#
discovery.type: single-node
```
好了之後配置我們的 logback
# logback-spring.xml

有用log的地方都可以加，依樣放在 resources
```
<?xml version="1.0" encoding="UTF-8"?>

<configuration>

    <!--定义日志文件的存储地址 勿在 LogBack 的配置中使用相对路径-->  

    <property name="LOG_HOME" value="d:/" />   

    

    <!-- 控制台输出 -->     

    <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">  

        <encoder class="ch.qos.logback.classic.encoder.PatternLayoutEncoder">   

             <!--格式化输出,%d:日期;%thread:线程名;%-5level：级别,从左显示5个字符宽度;%msg:日志消息;%n:换行符-->   

            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n</pattern>     

        </encoder>  

    </appender>  

    

    <appender name="RABBITMQ"

  class="org.springframework.amqp.rabbit.logback.AmqpAppender">

  <layout>

   <pattern><![CDATA[ %d %p %t [%c] - <%m>%n ]]></pattern>

  </layout>

  <!--rabbitmq地址 -->

  <addresses>192.168.99.100:5672</addresses>

  <username>guest</username>

  <password>guest</password>

  <declareExchange>true</declareExchange>

  <exchangeType>direct</exchangeType>

  <exchangeName>ex_logstash</exchangeName>

  <routingKeyPattern>lgstash</routingKeyPattern>

  <generateId>true</generateId>

  <charset>UTF-8</charset>

  <durable>true</durable>

  <deliveryMode>NON_PERSISTENT</deliveryMode>

  <autoDelete>false</autoDelete>

 </appender>

 <logger name="com.light.rabbitmq" level="info" additivity="false">

        <appender-ref ref="STDOUT"/>

        <appender-ref ref="RABBITMQ"/>

    </logger>

    <!-- 日志输出级别，level 默认值 DEBUG，root 其实是 logger，它是 logger 的根 -->  

    <root level="INFO">  

        <appender-ref ref="STDOUT" />  

        <appender-ref ref="RABBITMQ" />  

    </root>   
</configuration>
```
這個原理日後再探討，又是另一個坑了下次再玩先把框架先大致弄完
# rabbitmq

記得加我們的 Excanges  

![](https://i.imgur.com/Jkh4KRg.png)

  

還有我們的 Quenues  

![](https://i.imgur.com/Y7RJNgC.png)

  

最重要的binding  

![](https://i.imgur.com/c7Czrzd.png)

  

這邊設定好就差不多了
# 啟動

elasticsearch  

![](https://i.imgur.com/MVjStnD.png)

  

rabbitmq  

![](https://i.imgur.com/AbabwXZ.png)

  

kibana  

![](https://i.imgur.com/f0hVJBV.png)

  

  

  

debug 區 (ps不用理我，我在最慘的情況下試了很多方式了  

![](https://i.imgur.com/raUDbIq.png)

  

gg  

![](https://i.imgur.com/1C3iQMi.png)

arm開發版目前不支援 目前版本 用 vm囉裡面再用 docker  

我們裝在 win10子系統  

<https://www.itread01.com/content/1543061166.html>  

<https://blog.walterlv.com/post/how-to-install-wsl2.html>  

切成 WSL2  

<https://www.pigo.idv.tw/archives/3359>  

之前的 WSL 不能跑 DOCKER 現在 切成 WSL2 就可以跑了  

<https://blog.yowko.com/cannot-connect-docker-daemon/>  

<https://medium.com/faun/docker-running-seamlessly-in-windows-subsystem-linux-6ef8412377aa>
````
![](https://i.imgur.com/zw2hL5H.png)

```code

docker pull sebp/elk

docker run -p 5601:5601 -p 9200:9200 -p 5044:5044 -e ES_MIN_MEM=128m  -e ES_MAX_MEM=1024m -it --name elk sebp/elk
````

![](https://i.imgur.com/TAYcnbB.png)

  

![](https://i.imgur.com/4orRMD2.png)

  

1、执行命令：docker pull sebp/elk 将镜像pull到本地来；
2、执行命令：docker run -p 5601:5601 -p 9200:9200 -p 5044:5044 -e ES_MIN_MEM=128m  -e ES_MAX_MEM=1024m -it --name elk sebp/elk 将镜像运行为容器，由于我本机内存不符合安装要求，为了保证ELK能够正常运行，加了-e参数限制使用最小内存及最大内存。
3、打开浏览器，输入：http://<your-host>:5601，看到图形化解面即安装成功
vm.max_map_count至少需要262144.否則啟動時會報錯。
設定方式：
sudo vi /etc/sysctl.conf  

增加 :
vm.max_map_count = 262144  

fs.file-max = 65536
docker exec -it elk /bin/bash  

![](https://i.imgur.com/8wV8KzI.png)
