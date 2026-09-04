---
title: "websocket 達到百萬連接?(二) Rabbitmq 基本安裝與設定"
date: "2019-08-14T09:42:00.001+08:00"
updated: "2019-09-13T08:49:06.406+08:00"
permalink: "/2019/08/websocket-rabbitmq.html"
original_url: "https://x8795278.blogspot.com/2019/08/websocket-rabbitmq.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5581518428200863492"
tags: ["erlang", "linux", "Tutorial", "websocket"]
layout: post
---

![](https://i.imgur.com/LHLy7oz.png)

<https://www.rabbitmq.com/which-erlang.html>  

<https://www.rabbitmq.com/which-erlang.html>  

![](https://i.imgur.com/UoxvaJL.png)

## install erlang

<https://github.com/rabbitmq/erlang-rpm/releases/download/v22.0.7/erlang-22.0.7-1.el7.x86_64.rpm>
# rabbitmq install

# 新增來源

```
rpm --import https://github.com/rabbitmq/signing-keys/releases/download/2.0/rabbitmq-release-signing-key.asc

#In order to use the Yum repository, a .repo file (e.g. rabbitmq.repo) has to 
#be added under the /etc/yum.repos.d/ directory. The contents of the file 
##will vary slightly between distributions (e.g. CentOS 7 vs. CentOS 6 vs. 
##OpenSUSE). The following example targets CentOS 7:

[bintray-rabbitmq-server]
name=bintray-rabbitmq-rpm
baseurl=https://dl.bintray.com/rabbitmq/rpm/rabbitmq-server/v3.7.x/el/7/
gpgcheck=0
repo_gpgcheck=0
enabled=1

yum clean all    #yum makecache

yum install rabbitmq-server
!!
```
# 基本設定

## 啟動服務

```
sudo systemctl start rabbitmq-server
```
## 查詢狀態

```
sudo systemctl status rabbitmq-server
```
## 設置為開機啟動

```
sudo systemctl enable rabbitmq-server
```

1. 添加用户并授权

# 新增使用者

```
sudo rabbitmqctl add_user admin pwd
```
# 設定使用者

```
sudo rabbitmqctl set_user_tags admin administrator

#tag（administrator，monitoring，policymaker，management）
```
# 設定使用者權限 (接收所有來自host 的所有操作)

```
sudo rabbitmqctl  set_permissions -p "/" admin '.*' '.*' '.*'
```
# 查詢使用者權限

```
sudo rabbitmqctl list_user_permissions admin
```

2. 設定使用者遠端訪問

# 修改配置相關文件

```
sudo vi /etc/rabbitmq/rabbitmq.config
```
# 儲存以下內容

```
[
{rabbit, [{tcp_listeners, [5672]}, {loopback_users, ["admin"]}]}
].
```
3、重啟 rabbitmq server
# 重新啟動服務

```
sudo systemctl restart rabbitmq-server
```
# 新增防火牆開放連接埠

```
sudo firewall-cmd --add-port=5672/tcp --permanent
```
# 重新載入防火牆設定

```
sudo firewall-cmd --reload
```
# 開啟後台

```
rabbitmq-plugins enable rabbitmq_management
```

![](https://i.imgur.com/f6ONYoZ.png)

# 教學參考

<https://blog.csdn.net/VirBird/article/details/20706159>  
<https://www.rabbitmq.com/which-erlang.html>
