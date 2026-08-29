---
title: "初探 DEVOPS 本地 CICD 部屬 wsl2 直上 Harbor 架設私有 Docker 倉庫 (二)"
date: "2020-07-09T06:51:00.005+08:00"
updated: "2020-07-11T11:25:14.928+08:00"
permalink: "/2020/07/devops-cicd-wsl2-harbor-docker.html"
original_url: "https://x8795278.blogspot.com/2020/07/devops-cicd-wsl2-harbor-docker.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-1014145781250809824"
tags: ["Docker", "Tutorial"]
layout: post
---

![](https://miro.medium.com/max/871/1*zYNBpVXtxGID9rttcSYklQ.jpeg)

# 架設私有 Docker 倉庫
在用wsl直上一次Harbor
由於呢，不想再開VM 所以也找不到有 wsl 架設的目前只是測試用，不過可以順利RUN 起 WSL

# 安裝 harbor
https://github.com/goharbor/harbor/releases

目前是下載
![](https://i.imgur.com/NRZ5YYR.png)
>wget https://github.com/goharbor/harbor/releases/download/v2.0.1/harbor-offline-installer-v2.0.1.tgz
>
解壓縮
> tar xvf https://github.com/goharbor/harbor/releases/download/v2.0.1/harbor-offline-installer-v2.0.1.tgz
切至harbor 目錄
>修改裡面的harbor yml 檔案
>

# add harbor.yml
```yml
# Configuration file of Harbor

# The IP address or hostname to access admin UI and registry service.
# DO NOT use localhost or 127.0.0.1, because Harbor needs to be accessed by external clients.
hostname: activate.adobe.com <<  目前的 位於 etc/hosts 裡面的 這個代表指向 hostname

# http related config
http:
  # port for http, default is 80. If https enabled, this port will redirect to https port
  port: 80

# https related config
https:
  # https port for harbor, default is 443
  port: 443
  # The path of cert and key files for nginx
  certificate: /home/x213212/harbor/ca.crt
  private_key: /home/x213212/harbor/ca.key

```
# 產生憑證

https://ivanzz1001.github.io/records/post/docker/2018/04/09/docker-harbor-https
> openssl req \
    -newkey rsa:4096 -nodes -sha256 -keyout ca.key \
    -x509 -days 365 -out ca.crt
>

# 開始安裝
> sudo ./install.sh
>
這邊可以發現
![](https://i.imgur.com/eNaZfX2.png)
![](https://i.imgur.com/aeeBPem.png)
# 修改 hostname
因為 docker desktop 預設 ip 是浮動的，我是不曉得有沒有其他方式可以固定下來應該有 目前只應急

![](https://i.imgur.com/yqJChBk.png)
這邊是我的可以看到根本不行，我之前修改過一次存檔後，他下一次把我覆蓋掉所以測試用途我直接使用 activate.adobe.com 去做測試
# 修改配置 vim /etc/docker/daemon.json
這時候你會發現 外面的 docker desktop 掛掉了
可能是腳本那邊有複寫到 docker desktop daemon
查閱官網技術文件說 docker desktop 沒有 daemon (??)
> sudo vim /etc/docker/daemon.json
>
![](https://i.imgur.com/4suiW6F.png)

可以看到中間那個insecure-registries 我把他指向 activate.adobe.com，正常來說 ip 也是可以它的用意好像是
>The IP address or hostname to access admin UI and registry service.
>DO NOT use localhost or 127.0.0.1, because Harbor needs to be accessed by external clients.
>
可能會被其他使用者訪問的意思，這邊我們只有我所以指定自己

> {
>           "registry-mirrors": [],
>             "insecure-registries": [
>                         "activate.adobe.com"  ],
>                             "debug": true,
>                               "experimental": false
>                               }
# WSL2: docker: Error response from daemon: cgroups: cannot find cgroup mount destination: unknown.
>sudo mkdir /sys/fs/cgroup/systemd
sudo mount -t cgroup -o none,name=systemd cgroup /sys/fs/cgroup/systemd
https://github.com/microsoft/WSL/issues/4189
# docker 重啟 vim /etc/docker/daemon.json
因為我們的 docker 跑去讀
> sudo dockerd &
>
![](https://i.imgur.com/YJtDdA9.png)

# 重新執行配置檔 vim /etc/docker/daemon.json
預設docker desktop 是沒有的所以
因為我們的docker 掛掉了，所以我們乾脆重裝一次看正不正常
> sudo ./install.sh

這邊我當初怕麻煩所以又重裝一下

 這時候可以看到剛剛那個畫面
 ![](https://i.imgur.com/aeeBPem.png)
 成功我們來瀏覽一下

# 進入 harbor
這邊可以看到我還是用 ip 去做瀏覽，不知道為什麼我們的 https://activate.adobe.com/ 並沒有生效
![](https://i.imgur.com/ozc3RzJ.png)
進入後我們來申請一下腳色權限

![](https://i.imgur.com/p9Mee1h.png)
申請一組 管理員帳號 等等 docker login 要用
![](https://i.imgur.com/wDntIOy.png)

# docker login
![](https://i.imgur.com/MsktqeG.png)

![](https://i.imgur.com/5nCQgth.png)
我剛剛已經登入過了
>docker login activate.adobe.com
>第一次登入 要你輸入 username 和 password
>

# 嘗試推上我們的私有倉庫
這邊要注意我們的project name 很重要
![](https://i.imgur.com/qCimKxN.png)

![](https://i.imgur.com/UWgofVP.png)
這邊有寫如果要推送 image 到這個 project 要下哪一些指令
Docker Push Command
Tag an image for this project:
>docker tag SOURCE_IMAGE[:TAG] 172.24.232.224/library/REPOSITORY[:TAG]

Push an image to this project:
> docker push 172.24.232.224/library/REPOSITORY[:TAG]

# 推送範例
![](https://i.imgur.com/gkJphbD.png)

>docker pull nginx:1.12.1
>docker tag nginx:1.12.1 activate.adobe.com/library/nginx:1.12.1
>docker push activate.adobe.com/library/nginx:1.12.1
>

# received unexpected HTTP status: 500 Internal Server Error
假設我們的insecure-registries 沒有填入我們的正確ip和 hostname  或者是 project name錯誤可能會出現
received unexpected HTTP status: 500 Internal Server Error

# 拉取範例
Pull Image
>docker pull activate.adobe.com/library/nginx:1.12.1
>

![](https://i.imgur.com/VelDkis.png)

假設不想搞東搞西的話 這樣是最好的要回歸最初的 docker 只要
![](https://i.imgur.com/uBImKPg.png)
按下去 就好了我們的 docker 配置檔就回歸到最初配置了

# 接入 portainer 看看
![](https://i.imgur.com/5Bgrt5L.png)
> docker container ls 這邊可以看到 我們的 harbor 其實就是 docker-compose
>
我們來安裝
 docker run -d -p 9000:9000 --name portainer --restart always -v /var/run/docker.sock:/var/run/docker.sock -v /home/Portainer:/data portainer/portainer
![](https://i.imgur.com/K5SVnxT.png)

![](https://i.imgur.com/xgwUtS0.png)
可以看到也可以正常使用了

