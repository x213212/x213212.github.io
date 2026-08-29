---
title: "Logstash 同步 MySQL 到 Elasticsearch"
date: "2020-05-22T20:30:00.005+08:00"
updated: "2020-07-07T07:35:54.768+08:00"
permalink: "/2020/05/logstash-mysql-elasticsearch.html"
original_url: "https://x8795278.blogspot.com/2020/05/logstash-mysql-elasticsearch.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2258965416713608324"
tags: ["elasticsearch", "Logstash", "mysql", "Tutorial"]
layout: post
---

![安装Logstash | 博客Bujarra.com](https://i.imgur.com/oFVDIhI.png)

# Logstash 同步 MySQL 到 Elasticsearch
下載
logstash-7.6.2
mysql-connector-java-8.0.20

> /bin/logstash -f logstash-es-mysql.conf
>

```
input{
     stdin {
     }
     jdbc {
         # 驅動方式
         jdbc_driver_library => "D:\Programming\mysql-connector-java-8.0.20\mysql-connector-java-8.0.20.jar"
         # 驅動類名
         jdbc_driver_class => "com.mysql.jdbc.Driver"
         # mysql 數據庫鏈接,blog為數據庫名 &useSSL=false 這個是為了防止不支持ssl連接的問題
         jdbc_connection_string => "jdbc:mysql://localhost:3306/stock?serverTimezone=UTC&characterEncoding=utf8&useSSL=false"
         # 連接數據庫用戶名
         jdbc_user => "root"
         # 連接數據庫密碼
         jdbc_password => "root"
         # 是否啟用分頁
         jdbc_paging_enabled => "true"
         jdbc_page_size => "50000"
         # 設置監聽間隔 各字段含義（由左至右）分、時、天、月、年，全部為*默認含>義為每分鐘都更新
         schedule => "* * * * * "
         type => "jdbc"
         # 執行sql文路徑及名稱
         # statement_filepath => "/home/logstash/blog.sql"
         # 直接寫sql語句用這個
         #statement => "select `article_detail`.article_id,article_title as title,article_detail_content as content from `article` LEFT JOIN `article_detail` ON `article`.`article_id` = `article_detail`.article_id"
statement => "SELECT * FROM `1216tw`"
         # use_column_value => true
         # tracking_column => "updatetime"
         # 保存上一次運行>的信息(tracking_column)
         # last_run_metadata_path => "./logstash_jdbc_last_run"
       }
}

filter{
    json{
        source => "message"
        remove_field => ["message"]
    }
}
#output插件配置
output{
      elasticsearch {
         #這裡可以是數組，可以是多個節點的地址，會自動啟用負載均衡
         hosts => ["192.168.99.100:9200"]
         #index名稱
         index => "kafei"
         #document_type => "haoyebao" #文檔類型
         document_type =>"_doc"
         #文檔id，必須設置，且表達式的變量存在，否則只>能插入一條記錄
         document_id => "%{id}"
template_overwrite => true
      }
      #控制台打印json
      stdout {
         codec => json_lines
     }
 }
```
![](https://i.imgur.com/s22zkFB.png)
使用之前做資料回測的東西 測試
![](https://i.imgur.com/p7SLFLz.png)

![](https://i.imgur.com/hHYJqvq.jpg)

![](https://i.imgur.com/V2EXqWW.png)

