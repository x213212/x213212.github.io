---
title: "初探 DEVOPS 本地 CICD 部屬 Docker& DockerCompose 快速入門到發布 DockerHub (一)"
date: "2020-07-07T05:43:00.007+08:00"
updated: "2020-07-11T11:25:54.317+08:00"
permalink: "/2020/07/devops-cicd-docker.html"
original_url: "https://x8795278.blogspot.com/2020/07/devops-cicd-docker.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3971977184665386794"
tags: ["Docker", "Tutorial"]
layout: post
---

![](https://uploads-ssl.webflow.com/5d3a7aed4e11720246d46f49/5eccb1e0fe9844687499ed40_docker%20logo.jpg)

# 初探 DEVOPS 本地 CICD 部屬
怎麼麼說呢，在上一章 的 到 部屬到 GCP 的 CICD，這假設在一年的前端在大陸地區落地計畫肯定是行不通的，那麼我們可能就要採用 私有 本地的方式架設 CICD
可以學習到

* docker & docker-compose
* gitlab
* Drone
* Kubernetes

詳細相關概念參考與實作 https://ithelp.ithome.com.tw/users/20120491/ironman/2538?page=3

主要我們是要針對 我們的 vue 和 spring cloud 做一個 部屬的動作所以 中間使用 golang 的片段 可能會被改成 nodejs 部分

那麼我們開始簡化上述文章做一個整理。

# Docker
簡單執行一個 container
>docker run -d nginx

類似工作管理員 可以看目前執行的 container
>docker ps -a
>

讓你的 container 有名字
> docker run -d --name=nginx nginx
>

暴露連接埠到本地 因為我們適用 wsl 所以 這樣的意思就是直接讓畚箕 8081 指向容器內 80 連接埠
>docker run -d --name=nginx -p 8081:80 nginx

容器外檔案指向外部
假設有一
index.html
建立於根目錄
```html
<h1>1234</h1>
```
>docker run -d --name=nginx -p 8081:80 -v "$(pwd)/index.html:/usr/share/nginx/html/index.html" nginx
>
這樣意思就是
-v "$(pwd)/index.html:/usr/share/nginx/html/index.html
本機目錄 index.html 映射到 /usr/share/nginx/html/index.html

## 安裝 Pontainer
這個是主要來管理 docker 容器的，第一次進入請 選 local
![](https://i.imgur.com/P2Caqoq.png)

![](https://i.imgur.com/LSPkWA0.png)

>docker run -d -p 9000:9000 --name portainer --restart always -v /var/run/docker.sock:/var/run/docker.sock -v /home/Portainer:/data portainer/portainer

可以觀看 執行中的 container
![](https://i.imgur.com/sjivBiJ.png)

# Docker-Composr
以 docker-compose.yml 方式改寫我們的 nginx 範本
## add docker-compose.yml
```yml
version: '3'                      # 目前使用的版本

services:                         # services 固定字
  web:                            # 可以隨機命名，識別用
    image: nginx:1.12.1           # image 容器 + 版本號
    container_name: nginx-servie  # 容器名稱
    restart: always               # 當機器重新啟動時，服務會自動啟動
    ports:                        # 容器外與容器內的Port
      - 8081:80
    volumes:                      # 將容器外檔案掛載至容器內,如果容器內相同路徑已經存在相同檔案，則會覆蓋內容
      - ./default.conf:/etc/nginx/conf.d/default.conf
      - ./index.html:/home/project/index.html
```
## add default.conf
```conf
server {
    listen       80;
    server_name  localhost;

    location / {
        root   /home/project;
        index  index.html index.htm;
    }

}
```
## add index.html
```html
<h1>1234</h1>
```

啟動
> docker-compose up -d
>

## container 溝通
以範例來說，下面例子我隨便舉 反正就是兩個 docker-compose 互通網段 關鍵在 networks
## docker-compose.yml 1
```yml
version: '3'                      # 目前使用的版本

services:                         # services 固定字
  web:                            # 可以隨機命名，識別用
    image: nginx:1.12.1           # image 容器 + 版本號
    container_name: nginx-servie  # 容器名稱
    restart: always               # 當機器重新啟動時，服務會自動啟動
    ports:                        # 容器外與容器內的Port
      - 8081:80
    volumes:                      # 將容器外檔案掛載至容器內,如果容器內相同路徑已經存在相同檔案，則會覆蓋內容
      - ./default.conf:/etc/nginx/conf.d/default.conf
      - ./index.html:/home/project/index.html
# 表示服務用的網絡是用外部的網路，並且搜尋名稱為「web_service」 
# 若搜尋失敗，則會顯示該錯誤
# ERROR: Please create the network manually using `docker network create web_services` and try again.
networks:
  web_service:
    external: true
    
```
## docker-compose.yml 2
```yml
version: '3'                      # 目前使用的版本

services:                         # services 固定字
  web:                            # 可以隨機命名，識別用
    image: nginx:1.12.1           # image 容器 + 版本號
    container_name: nginx-servie  # 容器名稱
    restart: always               # 當機器重新啟動時，服務會自動啟動
    ports:                        # 容器外與容器內的Port
      - 8081:80
    volumes:                      # 將容器外檔案掛載至容器內,如果容器內相同路徑已經存在相同檔案，則會覆蓋內容
      - ./default.conf:/etc/nginx/conf.d/default.conf
      - ./index.html:/home/project/index.html
# 表示服務用的網絡是用外部的網路，並且搜尋名稱為「web_service」 
# 若搜尋失敗，則會顯示該錯誤
# ERROR: Please create the network manually using `docker network create web_services` and try again.
networks:
  web_service:
    external: true
```
因為照理來說container 建立的時候
![](https://i.imgur.com/LtlMjiN.png)
ip會自動遞增， 那麼假設 我們要在同一個 docker-compose 去共用一個網段怎麼辦呢

## web_service 表示該段名稱
> docker network create web_service

## 建置完畢後，可以透過以下指令查看
> docker network ls
>

![](https://i.imgur.com/IM96OGW.png)

## docker-compose example
```yml
version: "3"                        # docker-compose 版本號

services:                           # 開始撰寫 container 服務
  redis:                            # 可以隨意命名，通常以有意義的字串命名
    image: redis:5.0.5-alpine       # 服務容器，若無指定版號表示使用 latest 版本， alpine 容器佔用空間較小，通常建議使用
    volumes:                        # 掛載的撰寫方式，如果有多組不同路徑掛載，只需要在新增幾行條件即可。
      - ./redis.conf:/usr/local/etc/redis/redis.conf
    container_name: myredis         # 指容器名稱，這裡比較不同的是指令使用「--name」，但在yml應該使用「container_name」
    command: redis-server /usr/local/etc/redis/redis.conf # command 表示啟動容器後預備執行的動作
    environment:                    # 提供參數至容器內部，docker 指令是使用「-e 或者 --env」，但在yml應該使用「environment」 反正就是環境變數
      - ENV=develop
```

# Custom  自定義 docker image
假設我們要 重寫 在網上一個 發布的 container 額外增加其他 功能呢我們可以用到 dockerfile
## add Dockerfile
```Dockerfile
Dockerfile:
# 以 nginx 1.12.1 的版本作為基底
FROM nginx:1.12.1 AS builder

# Install logrotate
# RUN 指令可以協助安裝套件或者執行否些指令
RUN apt-get update && apt-get -y install logrotate

# 將logroate規則複製進容器(必須讓檔案為root用戶，才可以執行)
# COPY 指令可以協助將容器外部的檔案，複製到容器內某路徑
COPY ./nginx-logrotate /etc/logrotate.d/nginx

# CDM 指令指容器啟動後，需要做的行為
# 該範例為啟動 cron 背景服務 + nginx 服務
CMD service cron start && nginx -g 'daemon off;'
```

## add default.conf
```default.conf
server {
    listen       80;
    server_name  localhost;

    location / {
        root   /home/project;
        index  index.html index.htm;
    }

}
```
## add index.html
```html
<h1>1234</h1>
```

## nginx-logrotate
```
/var/log/nginx/*.log {
        daily
        missingok
        rotate 7
        compress
        dateext
        notifempty
        create
        sharedscripts
        postrotate
                if [ -f /var/run/nginx.pid ]; then
                        kill -USR1 `cat /var/run/nginx.pid`
                fi
        endscript
}
```

## docker-compose.yml
```yml
version: '3'

services:
  web:
    build: 
      context: .                                       # 讀取當前路徑的 Dockerfile
    restart: always                                    # 虛擬機會實體機重起後，容器服務自動帶起
    container_name: nginx                              # 容器名稱
    volumes:
      - ./default.conf:/etc/nginx/conf.d/default.conf  # 掛載 nginx 設定檔，可自由操控nginx設定檔
      - ./index.html:/home/project/index.html          # 掛載專案
    working_dir: /home/project                         # 進入容器後的預設路徑
    ports:                                             # 容器內與容器外 Port
      - 8899:80
    networks:                                          # 指定使用那一條網路
      - web_service

# 表示服務用的網絡是用外部的網路，並且搜尋名稱為 「web_service」 
# 搜尋成功後會自動與「webs」服務相連
networks:
  web_service:
    external: true
```
以上即可完成 nginx 服務建置。

# build 成 image
在推上 docker hub 或者私有 harbor (私有庫) 保存，日後直接使用

# 將 Dockerfile build 成 image 並加上 tag
> docker build -t x213212/nginx:1.12.1 .
> -t 表示替 image 打上 tag
> 因為接下來示範將 images 推至 docker hub
> 故 image tag 直接使用個人的 x213212/nginx (專案名稱) + 1.12.1 (版本號)
>
# 檢查是否 build 成功
>docker images | grep "x213212/nginx"

# 推至公開的 docker hub
> docker push x213212/nginx:1.12.1

