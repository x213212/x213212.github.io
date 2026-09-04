---
title: "Vue-router lazyloading (懶加載)"
date: "2019-07-02T09:23:00.000+08:00"
updated: "2019-07-14T00:03:01.142+08:00"
permalink: "/2019/07/vue-router-lazyloading.html"
original_url: "https://x8795278.blogspot.com/2019/07/vue-router-lazyloading.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-1355050845194317283"
tags: ["Tutorial", "Vue.js"]
layout: post
---

看圖才能大致了解原理 (比較喜歡)，畢竟太抽象
在切成各模組進入點的話，在一般進行 build 的時候 通常會直接編成一個 js 案，  

在 預設會將會讓 程式在一開始的時候，載入完全部的頁面  

所需要的js，可以經由配置這個，可以在載入該頁面的時候才載入 js 檔，這樣的話可以大幅減輕使用者等待頁面時間。
```
const Login = () => import(/* webpackChunkName: "group-foo7" */ './view/login.vue')
const Header = () => import(/* webpackChunkName: "group-foo7" */ './view/header.vue')
const Home = () => import(/* webpackChunkName: "group-foo6" */ './view/home.vue')
const UserInfo = () => import(/* webpackChunkName: "group-foo5" */ './view/userinfo.vue')
const test = () => import(/* webpackChunkName: "group-foo4" */ './view/test.vue')
const test2 = () => import(/* webpackChunkName: "group-foo3" */ './view/h1.vue')
const test3 = () => import(/* webpackChunkName: "group-foo2" */ './view/h2.vue')

Vue.use(VueRouter)

const routes = [
  {
    path: '/login',
    component: Login,
    name: 'login'
  },
```
這樣的時候，在經由 webpack 打包後的靜態檔案，在 瀏覽到 相對應的 url，  

才會載入相對應的js，也就是 .vue 檔案經由， webpack 編譯後的 js 檔案，  

在被瀏覽的時候才會下載其js  

必須注意
必須注意 各個模組的進入點的html 檔案 必須要移除其 js 檔案 也就是 import 後面那一段  

group-foo2，可以設置為 相同 為 group 檔案名稱 則 最後階段的時候 將會被打包 到最先  

被載入的 chunk name 必須要注意這一點。 ( 吧?

則 切換 url 之後 才會載入其相對應 js chunk  

可以經由 chrome 觀察  

這邊必須要先移除index 裡面的預先載入的 chunk (預設是載入所有js檔 ) 剛剛我們最後設置的 group-foo2 (需要注意 相同 group 會被包成相對應的js …以此類推)  

在這邊必須要先移除 方便觀察( 可能要經由 配置 webpack 編譯檔案 才可以知道 到底能不能每次編譯都可防止產生此段 javascript

![](https://i.imgur.com/6g0nB3g.png)

移除group-foo2此段 js  

![](https://i.imgur.com/DhTBJ.png)

![](https://i.imgur.com/3KAnvSO.png)

  

切換 h1 路由  

![](https://i.imgur.com/0Xm4okJ.png)

  

切換 h2 路由  

![](https://i.imgur.com/GLfWwF7.png)
