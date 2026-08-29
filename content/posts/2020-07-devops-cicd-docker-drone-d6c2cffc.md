---
title: "初探 DEVOPS 本地 CICD 部屬 使用 Docker 快速架設 Drone (四)"
date: "2020-07-10T08:06:00.001+08:00"
updated: "2020-07-11T11:25:15.031+08:00"
permalink: "/2020/07/devops-cicd-docker-drone.html"
original_url: "https://x8795278.blogspot.com/2020/07/devops-cicd-docker-drone.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5132141889966442000"
tags: ["drone", "Tutorial"]
layout: post
---

![](https://miro.medium.com/max/2560/1*IGIwDMV-uM-JOTQvecb4gQ.png)

# 使用 Docker 快速構建 Drone
填入我們上一回寫的 id 和key
![](https://i.imgur.com/1mdLUAQ.png)

# .env
```
DRONE_SERVER_HOST=172.24.229.236:8090
DRONE_SERVER_PROTO=http
DRONE_GITLAB_CLIENT_ID=b59ab915725beaa7332cbf93fc0c0a15f11332b6d6d2fa2bfd2d6f71c29eeac2
DRONE_GITLAB_CLIENT_SECRET=639fb3fced7d0f9f1d70021116b4537ade9c7bb00ad9b58ca2e1424b6f4c1816
GITLAB_SERVER=172.24.229.236

```
# docker-compose.yml
```yml
version: '2'

services:
  ### Drone Setting
  drone-server:
    image: drone/drone:1
    container_name: drone-server
    ports:
      - 8090:80
    extra_hosts:
      - "activate.adobe.com:172.24.229.236"
    volumes:
      - ./:/data
      - /var/run/docker.sock:/var/run/docker.sock
    restart: always
    environment:
      - DRONE_SERVER_HOST=${DRONE_SERVER_HOST}                       # Drone URL
      - DRONE_SERVER_PROTO=${DRONE_SERVER_PROTO}                     # http 或者 https 連線設定
      - DRONE_TLS_AUTOCERT=false                                     # 自動生成 ssl 證書，並接受 https 連線，末認為false
      - DRONE_RUNNER_CAPACITY=3                                      # 表示一次可執行 n 個 job
      - DRONE_GIT_ALWAYS_AUTH=false                                  # Drone clone 時，是否每次都驗證
      - DRONE_USER_FILTER=root                                       # 可操作 Drone 的用戶清單
      - DRONE_USER_CREATE=username:root:true                         # 可選擇特定帳號為使用者權限
      # GitLab Config
      - DRONE_GITLAB_CLIENT_ID=${DRONE_GITLAB_CLIENT_ID}             # OAuth 的 Application ID
      - DRONE_GITLAB_CLIENT_SECRET=${DRONE_GITLAB_CLIENT_SECRET}     # OAuth 的 Secret
      - DRONE_GITLAB_SERVER=http://${GITLAB_SERVER}:10080            # Gitlab Server
      - DRONE_LOGS_DEBUG=true                                        # 選擇是否開啟 debug 模式
      # - DRONE_LOGS_PRETTY=true                                     # Log 是否以json方式呈現
      - DRONE_LOGS_COLOR=true                                        # Log 啟用顏色辨識
      - DRONE_AGENTS_DISABLED=true

  drone-agent:
    image: drone/agent:1
    container_name: drone-agent
    restart: always
    depends_on:
      - drone-server
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - DRONE_RPC_SERVER=${DRONE_SERVER_HOST}
      - DRONE_RPC_SECRET=${DRONE_RPC_SECRET}
      - DRONE_RUNNER_CAPACITY=3
      - DRONE_LOGS_DEBUG=true

```

docker-comopse 啟動後可以發現被導向認證畫面

![](https://i.imgur.com/eQMonxb.png)

![](https://i.imgur.com/l34LV6n.png)

