---
title: "MYSQL PXC (docker for windows) 待續..."
date: "2020-05-26T00:50:00.003+08:00"
updated: "2020-07-07T08:54:11.844+08:00"
permalink: "/2020/05/mysql-pxc-docker-for-windows.html"
original_url: "https://x8795278.blogspot.com/2020/05/mysql-pxc-docker-for-windows.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5495170546945832898"
tags: ["Docker", "mysql"]
layout: post
---

![Docker 基礎教學與介紹101 - HcwXd - Medium](https://uploads-ssl.webflow.com/5d3a7aed4e11720246d46f49/5eccb1e0fe9844687499ed40_docker%20logo.jpg)

# MYSQL PXC (docker for windows)

常用的mysql集群設計方案

* Replication
速度快
弱一致性
低價值
場景：日誌、新聞、帖子

* PXC
速度慢
強一致性
高價值
場景：訂單、帳號、財務

PXC大致原理為：當有寫入修改操作時，將該操作在集群內所有機器上都執行一遍，只有所有機器都確認完成後，這條操作才算成功。大致可以總結為以下幾個特點：

強一致性，要么全成功，要么全失敗，保證每個節點數據一致
數據一致，意味著全部節點可讀可寫，常規讀寫分離變負載均衡
無同步延遲
因為所有節點都要執行一次寫操作，所以速度慢於主從方案
最後一個節點寫入後才算成功寫入，因此寫入速度取決於集群內最慢的那台機器
當集群中任意節點執行寫操作時，請求提交給PXC，PXC負責將寫操作在其他節點也執行一遍，當所有節點執行成功時，才會正式寫入。

綜上所述，PXC性能稍差但數據安全等級極高，適合對數據安全有要求的架構。

![](https://i.imgur.com/6nV5lwY.png)

# docker for windows
原因可能就是集群不能linux 映射 windows 檔案目錄可以考慮換個方向去弄，
照這樣弄下來可能就是正常的linux 這個配置檔是沒什麼問題的，等待後續再成熟一點應該可以(?
https://github.com/bitnami/bitnami-docker-mariadb-galera/issues/11#issuecomment-594452882
```
version: "3.4"

networks:
  testbridge:
      external:
        name: testbridge

services:
  mysql-pxc1:
    user: root
    image: percona/percona-xtradb-cluster
    command: "--innodb-flush-method=fsync --user=root &"
    deploy:
      mode: global
    environment:
      - MYSQL_ROOT_PASSWORD=abc123
      - CLUSTER_NAME=PXC
      - XTRABACKUP_PASSWORD=abc123
    volumes:
      
      - /c/Users/test/px1/:/tmp/
      - /c/Users/test/px1/:/var/lib/mysql/
    networks:
      - testbridge
    ports:
      - 3306:3306

  mysql-pxc2:
    user: root
    image: percona/percona-xtradb-cluster
    command: "--innodb-flush-method=fsync --user=root &"
    deploy:
      mode: global
    environment:
      - MYSQL_ROOT_PASSWORD=abc123
      - CLUSTER_NAME=PXC
      - XTRABACKUP_PASSWORD=abc123
      - CLUSTER_JOIN=192.168.99.100:3306
    volumes:
      
      - /c/Users/test/px2/tmp/:/tmp/
      - /c/Users/test/px2/:/var/lib/mysql/
    networks:
      - testbridge
    ports:
      - 3307:3306

  mysql-pxc3:
    user: root
    image: percona/percona-xtradb-cluster
    command: " --innodb-flush-method=fsync --user=root &"
    deploy:
      mode: global
    environment:
      - MYSQL_ROOT_PASSWORD=abc123
      - CLUSTER_NAME=PXC
      - XTRABACKUP_PASSWORD=abc123
      - CLUSTER_JOIN=192.168.99.100:3306
    volumes:
      
      - /c/Users/test/px3/tmp/:/tmp/
      - /c/Users/test/px3/:/var/lib/mysql/
    networks:
      - testbridge 
    ports:
      - 3308:3306

```
```
testbridge_mysql-pxc3.0.ere449z487mv@default    | + exec mysqld --innodb-flush-method=fsync --user=root
testbridge_mysql-pxc3.0.ere449z487mv@default    | 2020-05-25T11:44:12.451657Z 0 [Warning] TIMESTAMP with implicit DEFAULT value is deprecated. Please use --explicit_defaults_for_timestamp server option (see documentation for more details).
testbridge_mysql-pxc3.0.ere449z487mv@default    | 2020-05-25T11:44:12.459801Z 0 [Note] mysqld (mysqld 5.7.29-32-57) starting as process 1 ...
testbridge_mysql-pxc3.0.ere449z487mv@default    | 2020-05-25T11:44:12.467036Z 0 [Warning] Setting lower_case_table_names=2 because file system for /var/lib/mysql/ is case insensitive
testbridge_mysql-pxc3.0.ere449z487mv@default    | 2020-05-25T11:44:12.467791Z 0 [Note] WSREP: Setting wsrep_ready to false
testbridge_mysql-pxc3.0.ere449z487mv@default    | 2020-05-25T11:44:12.467876Z 0 [Note] WSREP: No pre-stored wsrep-start position found. Skipping position initialization.
testbridge_mysql-pxc3.0.ere449z487mv@default    | 2020-05-25T11:44:12.467918Z 0 [Note] WSREP: wsrep_load(): loading provider library '/usr/lib64/galera3/libgalera_smm.so'
testbridge_mysql-pxc3.0.ere449z487mv@default    | 2020-05-25T11:44:12.469789Z 0 [Note] WSREP: wsrep_load(): Galera 3.43(ra60e019) by Codership Oy <info@codership.com> loaded successfully.
testbridge_mysql-pxc3.0.ere449z487mv@default    | 2020-05-25T11:44:12.469891Z 0 [Note] WSREP: CRC-32C: using hardware acceleration.
testbridge_mysql-pxc3.0.ere449z487mv@default    | 2020-05-25T11:44:12.475806Z 0 [Note] WSREP: Found saved state: 00000000-0000-0000-0000-000000000000:-1, safe_to_bootstrap: 1
testbridge_mysql-pxc3.0.ere449z487mv@default    | 2020-05-25T11:44:12.483625Z 0 [ERROR] WSREP: mmap() on '/var/lib/mysql//galera.cache' failed: 22 (Invalid argument)
testbridge_mysql-pxc3.0.ere449z487mv@default    |        at galerautils/src/gu_mmap.cpp:MMap():46
testbridge_mysql-pxc3.0.ere449z487mv@default    | 2020-05-25T11:44:12.484393Z 0 [ERROR] WSREP: Failed to initialize wsrep_provider (reason:7). Must shutdown
testbridge_mysql-pxc3.0.ere449z487mv@default    | 2020-05-25T11:44:12.484418Z 0 [ERROR] Aborting
testbridge_mysql-pxc3.0.ere449z487mv@default    |
testbridge_mysql-pxc3.0.ere449z487mv@default    | 2020-05-25T11:44:12.484431Z 0 [Note] Binlog end
testbridge_mysql-pxc3.0.ere449z487mv@default    | 2020-05-25T11:44:12.485239Z 0 [Note] mysqld: Shutdown complete
```

# 不掛載 docker mount volume
ㄡ...我都忘了把windwos 升級到 pro 了 可能期待下篇了 wsl2 + docker
反正配置檔弄得差不多了(?
![](https://i.imgur.com/eDkgYNv.png)

