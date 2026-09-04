---
title: "react SQLite Collaboration Server (?)"
date: "2020-06-23T15:50:00.006+08:00"
updated: "2020-07-07T07:38:04.246+08:00"
permalink: "/2020/06/blog-post.html"
original_url: "https://x8795278.blogspot.com/2020/06/blog-post.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8286509143304654069"
tags: ["rabbitmq", "Tutorial"]
layout: post
---

![](https://miro.medium.com/max/3600/1*h8d-4wYLN9wwiEsLAA_5yg.jpeg)

# SQLite Collaboration Server (?)
近期github 收到來信說可以提供意見 給現有 專案 我只有小修 google drive
看了幾個 issue 其中一個比較有趣的
主要的功能就是
#https://github.com/UniversalDataTool/universal-data-tool/issues/86

Goals

* Users should be able to collaborate with other users to complete the labeling of a dataset together
* Users should receive notifications as work is completed or started by other users
* Users should receive "updates" from other users in less than 500ms
* The "Settings" should be able to be edited by any user
* New data uploaded should be supported by any user
* Collaborative links should be shareable
* The first time someone enters collaboration mode a dialog should explain how to share the link etc.

看到這邊我覺得 這邊或許可以用 rabbitmq來實作看看?
這禮拜來學 react
主要是這三種介面 技術選用的話是
react 腳手架， react router reract cookie rabbitmq，總體來說 react 比 vue 上手稍微難一點
以上述功能的話就是說 無須登入
這邊我先簡化成 可以登入 可能 瀏覽器可以產生一組 hash key
再來就是 登入 後 進入 jobpool 選取 標註任務後 跳轉頁面到 job 按下finsh 這樣應該是簡化版的 UniversalDataTool
再來就是說 其實我們只有一個伺服器 所以使用者當前目錄下存取數據的話可能會用 sqlite 或者其他
然後 我們預計使用 rabbitmq  他可以被 使用 websocket stomp 進行 呼叫 這邊考慮用 get post 來做簡單模擬 主要還是由伺服器
去做數據的投放， 連進來的話由 client 去訂閱 Queues
再來就是當我們使用者 進行 完成任務的時候，會跟其他使用者發生競爭的問題的話 這邊考慮用 樂觀鎖(?
https://github.com/x213212/sharejobpool

![](https://i.imgur.com/CuInslD.png)

![](https://i.imgur.com/g8YzGOy.png)
![](https://i.imgur.com/9sA8DVU.png)
![](https://i.imgur.com/4blrwo1.png)

