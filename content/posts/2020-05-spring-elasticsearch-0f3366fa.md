---
title: "Spring 基於 Elasticsearch 搜尋商品 (一) 快速入門語法"
date: "2020-05-17T18:39:00.010+08:00"
updated: "2020-07-07T07:35:16.140+08:00"
permalink: "/2020/05/spring-elasticsearch.html"
original_url: "https://x8795278.blogspot.com/2020/05/spring-elasticsearch.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-4919013758948299652"
tags: ["elasticsearch", "spring boot", "Spring Cloud", "Tutorial"]
layout: post
---

![](https://i.imgur.com/wffZ6bK.png)

# 基於 Elasticsearch 搜尋商品

# 摘要
我們之前用 Elasticsearch 來去匯集 我們微服務之間的LOG 現在的話我們直接用搜尋再資料庫的某項商品資料
意味者賦予你的數據、搜索、分析等功能

# Elasticsearch 6.2.2
Elasticsearch 是一個分佈式、可擴展、實時的搜索與數據分析引擎。它能從項目一開始就賦予你的數據以搜索、分析和探索的能力，可用於實現全文搜索和實時數據統計。
https://www.elastic.co/cn/downloads/past-releases/elasticsearch-6-2-2

# 安裝 中文分詞 elasticsearch-plugin 6.2.2
延伸閱讀
https://blog.toright.com/posts/5319/fulltext-search-elasticsearch-kibana-bigdata.html

![](https://i.imgur.com/5xIsatO.png)
>elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v6.2.2/elasticsearch-analysis-ik-6.2.2.zip
>

![](https://i.imgur.com/pBt9YZD.png)

https://github.com/medcl/elasticsearch-analysis-ik

https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v6.2.2/elasticsearch-analysis-ik-6.2.2.zip

# 啟動 elasticsearch
> elasticsearch.bat
>

![](https://i.imgur.com/VvmZIyQ.png)
![](https://i.imgur.com/wvZPSuM.png)

# Kibana 6.2.2

> kibana.bat
>
![](https://i.imgur.com/2xMrUdT.png)
![](https://i.imgur.com/19mzJzH.png)
可以輸入 dsl 語句 操作 elasticsearch
![](https://i.imgur.com/RH7txc0.png)

# Elasticsearch 快速入門

> https://www.elastic.co/guide/cn/elasticsearch/guide/current/index-doc.html
>
就根據官方文檔案看下來，索引就相對於是資料庫，類型就相對於 資料庫裡面的表 文檔就就相對於資料庫裏面每一條紀錄，屬性就相對於欄位。

# 什麼是文檔？
在大多數應用中，多數實體或對象可以被序列化為包含鍵值對的JSON對象。 一個對象，一些計數值，或一些其他特殊類型表示日期的字符串，或代表一個定位的對象：
```json
{
    "name": "John Smith", 
    "age": 42, 
    "confirmed": true, 
    "join_date": "2014-06-01", 
    "home": {
        "lat": 51.5, 
        "lon": 0.1
    }, 
    "accounts": [
        {
            "type": "facebook", 
            "id": "johnsmith"
        }, 
        {
            "type": "twitter", 
            "id": "johnsmith"
        }
    ]
}
```

# 創建索引文檔
https://www.elastic.co/guide/cn/elasticsearch/guide/current/index-doc.html
```json
PUT http://localhost:9200/website/blog/123
{
  "title": "My first blog entry",
  "text":  "Just trying this out...",
  "date":  "2014/01/01"
}
```
![](https://i.imgur.com/1fIHuOp.png)

# 取回索引文檔
https://www.elastic.co/guide/cn/elasticsearch/guide/current/get-doc.html
```json
GET http://localhost:9200/website/blog/123?pretty
```
![](https://i.imgur.com/VZiUA3I.png)

# 檢查索引文檔是否存在
https://www.elastic.co/guide/cn/elasticsearch/guide/current/doc-exists.html
```json
HEAD http://localhost:9200/website/blog/123/
```
![](https://i.imgur.com/M6qGmkG.png)
存在他會直接response 200

# 更新索引文檔
https://www.elastic.co/guide/cn/elasticsearch/guide/current/update-doc.html
```json
PUT http://localhost:9200/website/blog/123
{
  "title": "My first blog entry",
  "text":  "Just trying this out...",
  "date":  "2014/01/01"
}
```
![](https://i.imgur.com/ztWOgPU.png)

# 創建新文檔
```json
PUT http://localhost:9200/website/blog/123?op_type=create
PUT /website/blog/123/_create
{
  "title": "My first blog entry",
  "text":  "Just trying WWthis out...",
  "date":  "2014/01/02"
}
```
![](https://i.imgur.com/9abKaKG.png)

# 刪除文檔
```json
DELETE http://localhost:9200/website/blog/123
```
![](https://i.imgur.com/msvy3Zg.png)

