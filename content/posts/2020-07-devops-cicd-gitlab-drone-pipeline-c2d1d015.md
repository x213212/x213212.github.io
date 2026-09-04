---
title: "初探 DEVOPS 本地 CICD 部屬 Gitlab 觸發 Drone 執行 pipeline 事件 (五)"
date: "2020-07-10T08:45:00.001+08:00"
updated: "2020-07-11T11:25:15.107+08:00"
permalink: "/2020/07/devops-cicd-gitlab-drone-pipeline.html"
original_url: "https://x8795278.blogspot.com/2020/07/devops-cicd-gitlab-drone-pipeline.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-7247429847504697754"
tags: ["Docker", "Tutorial"]
layout: post
---

![](https://miro.medium.com/max/2560/1*IGIwDMV-uM-JOTQvecb4gQ.png)

# Gitlab 觸發 Drone 執行 pipeline 事件。
## 構建 project
這邊測試設為 demo
![](https://i.imgur.com/ickIPmb.png)
![](https://i.imgur.com/U9bKKBm.png)

# 開啟本地端 hook
如果是「本機」環境測試用，記得要開啟 Gitlab 本地端的 webhook
「Settings --> Network --> Outbound requests」

* 勾選Allow requests to the local network from web hooks and services

![](https://i.imgur.com/YVsq0SJ.png)

![](https://i.imgur.com/eRe7ndO.png)
刷新
![](https://i.imgur.com/laOzl7c.png)
可以看到我的 gitlab 專案囉
# 啟用 drone 專案
當啟用成功後會看見以下話面，且表示 Gitlab 與drone 的 webhook 已經建立成功。
>root/demo
>

![](https://i.imgur.com/ab6D5ZR.png)

![](https://i.imgur.com/x5q14rz.png)

下載專案至目錄
> git clone http://172.24.231.23:10080/root/demo.git

![](https://i.imgur.com/U1CCxx6.png)
> vim ./drone/.drone.yml
>
# 撰寫 .drone.yml
以上的步驟就完成了，接著可以開始撰寫 .drone.yml 官方教學文件

備註:Drone 0.8 與 1.0 後的 yaml 檔案撰寫差異很大，需要在依據官方文件做參考，以下示範1.0之後的版本 Drone 0.8 文件

在 yaml檔案中，除了原本的 clone 事件外，還有三個事件分別是「host、echo、dev_action」，

https://0-8-0.docs.drone.io/getting-started/

host: 列印出容器內 /etc/hosts 內容
echo: 印出 78523 內容
dev-action: 印出 111111 內容

```yml
kind: pipeline
type: docker      # 在 Docker 內部執行管道命令
name: clone       # 可自行定義的名稱

steps:
  # 事件一
  - name: host                           # 事件一：可自行定義的名稱
    image: alpine                        # 使用 alpine 容器
    commands:                            # 預執行的 shell 指令，這邊印出 hosts 內容
      - cat /etc/hosts
    when:                                # 無論 clone 成功或失敗，都會跑該事件
      status: [ success, failure ]
  # 事件二
  - name: echo                           # 事件二：可自行定義的名稱
    image: plugins/git                   # 使用 plugins/git  容器
    commands:                            # 預執行的 shell 指令，這邊印出 78523 內容
    - echo "78523"
    when:                                # 當觸發條件為 master 分支時會執行的動作
      branch:
      - master
  # 事件三
  - name: dev_action                     # 事件三：可自行定義的名稱
    image: plugins/git                   # 使用 plugins/git  容器
    commands:                            # 預執行的 shell 指令，這邊印出 111111 內容
    - echo "111111"
    when:                                # 當觸發條件為 develop 分支時會執行的動作
      branch:
      - develop

trigger:     # 觸發 pipeline 條件，分支為 master，且進行 push 行為
  branch: 
  - master
  event:
  - push
撰寫完 yaml 檔案後，只需要在 master 分支執行 push 行為，接下來 Gitlab 會自動 tigger Drone 執行事件。
```

![](https://i.imgur.com/I2OAVhp.png)

上述編寫完成後當撰寫完 yaml 檔案後，只需要在 master 分支執行 push 行為，接下來 Gitlab 會自動 tigger Drone 執行事件。
![](https://i.imgur.com/ijO2vrA.png)

# drone pull private registry
抓取來自 私有 docker 一樣填入我們的 docker全部名稱也就是

```yml
kind: pipeline
type: docker      # 在 Docker 內部執行管道命令
name: clone       # 可自行定義的名稱

steps:
  # 事件一
  - name: hoste                           # 事件一：可自行定義的名稱
    image: activate.adobe.com/library/alpine                        # 使用 alpine 容器
    commands:                            # 預執行的 shell 指令，這邊印出 hosts 內容
      - cat /etc/hosts
    when:                                # 無論 clone 成功或失敗，都會跑該事件
      status: [ success, failure ]
  # 事件二
  - name: echo                           # 事件二：可自行定義的名稱
    image: activate.adobe.com/library/plugins/git                   # 使用 plugins/git  容器
    commands:                            # 預執行的 shell 指令，這邊印出 78523 內容
    - echo "78523"
    when:                                # 當觸發條件為 master 分支時會執行的動作
      branch:
      - master
  # 事件三
  - name: dev_action                     # 事件三：可自行定義的名稱
    image: activate.adobe.com/library/plugins/git                   # 使用 plugins/git  容器
    commands:                            # 預執行的 shell 指令，這邊印出 111111 內容
    - echo "111111cs"
    when:                                # 當觸發條件為 develop 分支時會執行的動作
      branch:
      - develop

trigger:     # 觸發 pipeline 條件，分支為 master，且進行 push 行為
  branch: 
  - master
  event:
  - push

```
commit 送出
![](https://i.imgur.com/cTPIkd3.png)
構建中
![](https://i.imgur.com/A9d25ya.png)
構建完成!

# 單機測試額外狀況 無限pending
runner: polling queue
本來是開啟 docker-compose debug 模式去看
![](https://i.imgur.com/URfujsE.png)
發現這個後來去查 為什麼會 pending 可能是為 預設是多台 所以有 http proxy 導致無法 pull image?
![](https://i.imgur.com/CvQFwEk.png)
後來我把這參數加上

docker-compose.yml
![](https://i.imgur.com/jbvb7J6.png)

```yml
....
      - DRONE_AGENTS_DISABLED=true
```

問題就解決囉!，到現在為止我們就已經完成搭建一個 gitlab 去觸發  Drone pipeline  事件囉。

