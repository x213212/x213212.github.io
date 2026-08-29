---
title: "Crc checker"
date: "2021-01-13T04:21:00.002+08:00"
updated: "2021-01-13T04:54:09.518+08:00"
permalink: "/2021/01/crc-checker.html"
original_url: "https://x8795278.blogspot.com/2021/01/crc-checker.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6363230035013997422"
tags: ["crc", "server"]
layout: post
---

![](https://user-images.githubusercontent.com/9297254/103471262-13b74b00-4db9-11eb-9994-13c07cebab0e.png)

![image](https://user-images.githubusercontent.com/9297254/103471259-0c903d00-4db9-11eb-9939-875f7ca38bd5.png)

![image](https://user-images.githubusercontent.com/9297254/103471262-13b74b00-4db9-11eb-9994-13c07cebab0e.png)
上課聽到一個熟悉的CRC演算法，這跟以前寫外掛bypassCrc或許有關係!?，想說去GITHUB 搜尋一下 以前遊戲看有沒有私服，看一下以前 SERVER 是怎麼傳輸資料的剛好找到一個有BUG的不能啟動的私服，稍微升級一下 MYSQL，暫時註解掉其他的功能就可以改動了，目前好像只有流出有DEUBG資訊，算五年前的一個SERVER了，看到以前的人寫的code還蠻有趣的，可能工程版流出(?
https://github.com/york8817612/Ghost

\Ghost-1.0\Server\GameServer\Ghost\Characters\Character.cs -->Load
```
 //this.Storages.Load();
```
\download\Ghost-1.0\Server\GameServer\Net\Handler\GameHandler.cs -->Game_Log_Req
```
//StoragePacket.getStoreInfo(gc);
//StoragePacket.getStoreMoney(gc);
```
and
![image](https://user-images.githubusercontent.com/9297254/103471196-40b72e00-4db8-11eb-8372-5ab2089715e4.png)
in
```
\Ghost-1.0\Server\CharServer\Net\CharHandler.cs
\Ghost-1.0\Server\GameServer\Net\Handler\GameHandler.cs
\Ghost-1.0\Server\LoginServer\Net\LoginHandler.cs
```
add
```
 password = gc.Account.Password;
or
 password = c.Account.Password;

```
InPacket seen not working debuging...
![image](https://user-images.githubusercontent.com/9297254/103471234-bb804900-4db8-11eb-93c4-5b46ec7b04d3.png)
![image](https://user-images.githubusercontent.com/9297254/103471238-c89d3800-4db8-11eb-9e97-5e69adac8865.png)

可以發現在 common/security/發現這邊就是檢查封包要經過的地方，我們以前bypass 就是這邊(?
![](https://i.imgur.com/Oh6jsk6.png)

只是目前還是不知道debug 訊息從哪裡來的是透過傳輸資料的時候可以控制開關還是是原作者透過其他反編譯工具進行修改，最近再複習一下以前的工具好了，
單純學習研究用途請24小時刪除

