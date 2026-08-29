---
title: "WSL2 docker run pxc server + haporxy 負載平衡"
date: "2020-05-26T16:30:00.006+08:00"
updated: "2020-07-07T08:54:03.406+08:00"
permalink: "/2020/05/wsl2-docker-run-pxc-server-haporxy.html"
original_url: "https://x8795278.blogspot.com/2020/05/wsl2-docker-run-pxc-server-haporxy.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8772729529585505049"
tags: ["Docker", "mysql"]
layout: post
---

![Docker 基礎教學與介紹101 - HcwXd - Medium](https://uploads-ssl.webflow.com/5d3a7aed4e11720246d46f49/5eccb1e0fe9844687499ed40_docker%20logo.jpg)

# wsl2 docker run pxc server + haporxy
```
docker swarm init
docker network create -d overlay --attachable pxc-network

docker run -d   -p 9001:3306  -e MYSQL_ROOT_PASSWORD=abc123456   -e CLUSTER_NAME=cluster1   -e XTRABACKUP_PASSWORD=abc123456   -v pnv1:/var/lib/mysql --privileged   --name=node1   --net=pxc-network  percona/percona-xtradb-cluster
docker run -d   -p 9002:3306   -e MYSQL_ROOT_PASSWORD=abc123456   -e CLUSTER_NAME=cluster1   -e XTRABACKUP_PASSWORD=abc123456   -e CLUSTER_JOIN=node1   -v pnv2:/var/lib/mysql --privileged   --name=node2   --net=pxc-network   percona/percona-xtradb-cluster
docker run -d   -p 9003:3306   -e MYSQL_ROOT_PASSWORD=abc123456   -e CLUSTER_NAME=cluster1   -e XTRABACKUP_PASSWORD=abc123456   -e CLUSTER_JOIN=node1  -v pnv3:/var/lib/mysql --privileged   --name=node3   --net=pxc-network   percona/percona-xtradb-cluster

mysql -uroot -pabc123456 -h127.0.0.1 -P9001
mysql -uroot -pabc123456 -h127.0.0.1 -P9002
mysql -uroot -pabc123456 -h127.0.0.1 -P9003
```

![](https://i.imgur.com/ZnLhjSn.png)
隨便執行一條 sql 就可以完成同步了
![](https://i.imgur.com/4qgAVKc.png)

![](https://i.imgur.com/NynQxCm.png)

# 負載平衡

docker run -d   -p 9001:3306  -e MYSQL_ROOT_PASSWORD=abc123456   -e CLUSTER_NAME=cluster1   -e XTRABACKUP_PASSWORD=abc123456   -v pnv1:/var/lib/mysql --privileged   --name=node1   --net=pxc-network  percona/percona-xtradb-cluster
docker run -d   -p 9002:3306   -e MYSQL_ROOT_PASSWORD=abc123456   -e CLUSTER_NAME=cluster1   -e XTRABACKUP_PASSWORD=abc123456   -e CLUSTER_JOIN=node1   -v pnv2:/var/lib/mysql --privileged   --name=node2   --net=pxc-network   percona/percona-xtradb-cluster
docker run -d   -p 9003:3306   -e MYSQL_ROOT_PASSWORD=abc123456   -e CLUSTER_NAME=cluster1   -e XTRABACKUP_PASSWORD=abc123456   -e CLUSTER_JOIN=node1  -v pnv3:/var/lib/mysql --privileged   --name=node3   --net=pxc-network   percona/percona-xtradb-cluster

# install haporxy
嘗試用 docker 部屬失敗了
>docker run -d -it -p 4001:3306 -p 4002:8888 --name haproxy -v "/$(pwd)/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro" haproxy
docker run -d -it -p 4001:3388 -p 4002:8888 --name haproxy -v "/$(pwd)/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro" haproxy  --privileged  --net=pxc-network
>

採用原生安裝 haporxy
>
mysql -uroot -pabc123456 -h127.0.0.1 -P9001
mysql -uroot -pabc123456 -h127.0.0.1 -P9002
mysql -uroot -pabc123456 -h127.0.0.1 -P9003

CREATE USER 'haproxy'@'%' IDENTIFIED BY '';
FLUSH PRIVILEGES;
>

這個目的 是為了 haproxy 去做心跳檢測機制

 sudo docker exec -it -u root node1 /bin/bash

# checkconfig
haporxy debug模式
> /usr/sbin/haproxy -d -f /etc/haproxy/haproxy.cfg
>
![](https://i.imgur.com/k3kmzAQ.png)

![](https://i.imgur.com/Beus3hr.png)
對節點 9090進行創建表就會自己選擇 mysql
```confing
listen proxy-mysql
       bind 0.0.0.0:9090
       # 网络协议
       mode tcp
       # 负载均衡算法（轮询）
       balance roundrobin
       # 日志格式
       option tcplog
       # 心跳检测，需要在mysql中创建一个没有权限的haproxy用户，密码为空。Haproxy使用这个账户对MySQL进行心跳检测
       option mysql-check user haproxy
       server MYSQL_1 172.18.18.247:9001 check weight 1 maxconn 2000
       server MYSQL_2 172.18.18.247:9002 check weight 1 maxconn 2000
       server MYSQL_3 172.18.18.247:9003 check weight 1 maxconn 2000
       # 使用keepalive检测死链
       option tcpka
```

