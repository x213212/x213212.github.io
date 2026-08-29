---
title: "使用 Spring Boot 輸出 jar 部署至 Linux"
date: "2019-12-15T17:17:00.004+08:00"
updated: "2019-12-26T03:15:49.387+08:00"
permalink: "/2019/12/spring-boot-jar-linux.html"
original_url: "https://x8795278.blogspot.com/2019/12/spring-boot-jar-linux.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2258216299358344719"
tags: ["Java", "spring boot", "Tutorial"]
layout: post
---

# 部署到 tomcat 伺服器?

這邊跟我們之前開發模式不一樣，我有寫過一個 用 Spring session 共享的文章，那時候自幹搭配 nginx 實現一套session，後面在考慮是否要來根據 spring boot 邏輯來重寫，今天是以前一天 restful api，我們寫完要部署到伺服，在之前的公司用的是 ant 算是比較早期(?，好像後面有用其他腳本。  

<https://www.itread01.com/content/1545095402.html>  

由於我們的 Spring boot 已經內建 tomcat ,  

當然你可以把它編成 war包 在給 其他的 tomcat 去做調用，我們今天只有以編成 jar 來示範 maven 來編譯一下
# maven 新增腳本

![](https://i.imgur.com/qSFfwHq.png)

  

在 goals 分別填入  

![](https://i.imgur.com/pMXBxow.png)

```
spring-boot:run
clean package
```
# maven 執行腳本

![](https://i.imgur.com/z1cMYXG.jpg)

  

![](https://i.imgur.com/jxX4XZn.png)

# jar

執行 clean package後  

可以看到  

![](https://i.imgur.com/B6wX2OL.png)

  

存在我們的 target  

![](https://i.imgur.com/Us1YSru.png)

# 常駐於 linux 使用 nohup

主要是解決Springboot 會自動關閉的問題  

解決方案就是用nohup
順便複習一下，在我們安裝 putty 裡面有 pscp 裡面可以 從 windows 傳輸到我們的 linux
```
pscp D:\Programming\java\Spring-Boot-Security-JWT-SPA-master\target\spring-boot-security-jwt-0.0.1-SNAPSHOT.jar x213212@192.168.0.146:/home/x213212
```

![](https://i.imgur.com/9knXH81.png)

  

得到了我們的 jar 囉，我們 來 run 起來  

![](https://i.imgur.com/03m4W60.png)

  

![](https://i.imgur.com/JgrNnTo.png)

![](https://i.imgur.com/qIApStY.png)

  

可以看到我們請求都被輸出到 microservice.log 文件囉
# nohup 是什麼?

用途：nohup是linux一个命令，不挂断地运行，或者理解为后台运行。
语法：nohup Command [ Arg … ] [　& ]
无论是否将 nohup 命令的输出重定向到终端，输出都将附加到当前目录的 nohup.out 文件中。
如果当前目录的 nohup.out 文件不可写，输出重定向到 $HOME/nohup.out 文件中。
如果没有文件能创建或打开以用于追加，那么 Command 参数指定的命令不可调用。
退出状态：该命令返回下列出口值： 　　  

　　126 可以查找但不能调用 Command 参数指定的命令。 　　  

　　127 nohup 命令发生错误或不能查找由 Command 参数指定的命令。 　　  

　　否则，nohup 命令的退出状态是 Command 参数指定命令的退出状态。
```
#docker
    nohup docker-compose up > /usr/local/logs/microservice-tcbj-yytsg/log.txt &

#springboot
    nohup java -jar microservice-web-0.0.1-SNAPSHOT.jar >microservice.log&
```
今天會以較輕鬆嘛，  

這邊有看到 部屬到 tomcat 伺服器，可以看應用場合部屬到 tomcat,在 spring 他就有內建  

tomcat 了，接下來部署到伺服器後，這是屬於單機情況，接下來要進行 集群的情況下如何。
參考  

[https://blog.xuite.net/hs19890622/job/388606028-執行Spring+Boot+專案的方式](https://blog.xuite.net/hs19890622/job/388606028-%E5%9F%B7%E8%A1%8CSpring+Boot+%E5%B0%88%E6%A1%88%E7%9A%84%E6%96%B9%E5%BC%8F)
<https://blog.csdn.net/moshowgame/article/details/82621913>
