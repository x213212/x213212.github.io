---
title: "Vue 建構一個 simple login/menu"
date: "2019-06-22T17:36:00.000+08:00"
updated: "2019-06-22T20:02:33.860+08:00"
permalink: "/2019/06/simple-loginmenu.html"
original_url: "https://x8795278.blogspot.com/2019/06/simple-loginmenu.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5467502339867118319"
tags: ["spring boot", "Tutorial", "Vue.js"]
layout: post
---

## 建構一個 simple login/menu

![](https://i.imgur.com/zYJiJda.png)

### 安裝各個套件

> 章節需用到 vuex , vue-router , vuei18n ,axios , element ui , vue-context  
>
> 如要安裝各個套件 可以透過 下載下面github 訪問  
>
> [17LearnVue.js](https://github.com/ChengYouFang/17LearnVue.js)  
>
> 下載完專案 使用 vscode 並 run 起專案

安裝完章節
> npm install

啟動伺服器
> npm run dev

![](https://i.imgur.com/AauITwP.png)

### 自訂一個額外 api cookies.js

/api/cookies.js
```
import Cookies from 'js-cookie'

const TokenKey = 'token'

export function getToken() {
  return Cookies.get(TokenKey)
}

export function setToken(token) {
  return Cookies.set(TokenKey, token)
}

export function removeToken() {
  return Cookies.remove(TokenKey)
}
```
/main.js
```
import { getToken } from './api/cookiesex'
 getToken() 可以取得 cookie 資料 
 
 ///也可以 ,,,,
import testmod  from './api/cookiesex'
 testmod.getToken() //一樣效果
```
### 客製化表格 改為分次傳送

程式碼為上述專案裡面 home 裡面 由於過於攏長  

寫下實現方式  

網頁表格 需要使用 虛擬渲染，以防頁面元素 dom 呼叫過多 事件  

導致記憶體過多

1. 取得相對應 data
2. 自定義變數 紀錄目前資料length 送至後端 目前筆數
3. data 重新顯示範圍 20 ~ 40

- currentIndex…

4. 透過ajax 像伺服器端請求下一份 data，不斷累加到 資料沒有
5. 判斷table scroll 是否到底 是的話 +20 否則 -20 回到步驟2

### 欄位篩選功能

### 新增右鍵選單

### main.js 入口點 篇

```
// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
///ui插件ㄐ
import { Message, Table } from 'element-ui'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import VueRouter from 'vue-router'
import { gettest } from './routes' //路由規則
//import routers from './routes' //路由規則
import axios from 'axios' // ajax 相對應模組
import i18n from './assets/i18n/i18n' //多國語言模組
import { getRequest } from './api/request' // 封裝 axios 為另一個模組
import { postRequest } from './api/request'
import { deleteRequest } from './api/request'
import { putRequest } from './api/request'
import { getToken } from './api/cookiesex'

Vue.config.productionTip = false
///這邊弄好完的xd 透過其他模組 而引用外部 js 變數
///請仔細 觀察 它們之間的關係 後面有關於個模組引用 有很大的關係
const routes2 = gettest() 
///////////router
const router = new VueRouter({
  routes: routes2,
  //routers
  mode: 'history'
})

// router
// 當有人沒有相對應 權限而進入
// 非法路徑 則 直接透過 router 導向 正常 login 畫面
router.beforeEach((to, from, next) => { 
 
  const isLogin = getToken() == 'ImLogin'
  if (isLogin) {
    next()
  } else {
    if (to.path !== '/login') next('/login')
    else next()
  }
})
Vue.use(VueRouter)

//引用 ui
Vue.use(ElementUI)

/////////// 全局引用 這邊引用過後可以透過讓底下各個模塊食用
Vue.prototype.getRequest = getRequest
Vue.prototype.postRequest = postRequest
Vue.prototype.deleteRequest = deleteRequest
Vue.prototype.putRequest = putRequest
Vue.prototype.$message = Message

///////////
/* eslint-disable no-new */
new Vue({
  el: '#app',
  router, //根據路由決定 components 位置
  i18n, //多國語系
  components: { App },
  template: '<App/>'
})
```
### router.js 路由篇

> 這邊仔細觀察 我們在 main.js new router 那一段 有呼叫一個  
>
> js函式 我們可以知道 我們額外呼叫了 gettest()  
>
> 這個函式，透過引用 外部 JS 一個小範例，也讓 我們的主 VUE 比較乾淨一點  
>
> 當然也可以 直接傳入 像 routes 那邊可以直接引用 js 變數  
>
> 可以 參考 VueRouter 的建構元 內部 所需傳遞的參數

> main 內部引用 額外 js 內部 變數 讓 main.js 乾淨  
>
> ![](https://i.imgur.com/LyUROse.png)

> router 對應相對應 components  
>
> ![](https://i.imgur.com/255FLz8.png)

```
import Login from './components/login.vue'
import Header from './components/header.vue'
import Home from './components/table.vue'
import UserInfo from './components/userInfo.vue'

export const routes = [
  {
    path: '/login',
    component: Login
  },
  {
    path: '/',
    components: {
      default: Home,
      nav: Header
    }
  },
  {
    path: '/userInfo',
    components: {
      default: UserInfo,
      nav: Header
    }
  },
  {
    path: '*',
    redirect: '/'
  }
]

export function gettest() {
  console.log(routes)
  return routes
}
```
<https://juejin.im/post/5b0281b851882542845257e7>
#### 攔截訪問非法路徑

<https://ithelp.ithome.com.tw/articles/10206041?sc=rss.qu>  

<https://segmentfault.com/a/1190000018173547>
