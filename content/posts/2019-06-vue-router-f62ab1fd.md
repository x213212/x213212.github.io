---
title: "Vue-router 基礎"
date: "2019-06-22T17:34:00.002+08:00"
updated: "2019-06-22T20:02:34.221+08:00"
permalink: "/2019/06/vue-router.html"
original_url: "https://x8795278.blogspot.com/2019/06/vue-router.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-998295015305868154"
tags: ["spring boot", "Tutorial", "Vue.js"]
layout: post
---

![ãvue-routerãçåçæå°çµæ](https://kanboo.github.io/2018/08/06/VueRouter/vuerouter.jpg) vue-router 基礎

### router 基本參數

```
this.$router.go(-1)//跳转到上一次浏览的页面
this.$router.replace('/menu')//指定跳转的地址
this.$router.replace({name:'menuLink'})//指定跳转路由的名字下
this.$router.push('/menu')//通过push进行跳转
this.$router.push({name:'menuLink'})//通过push进行跳转路由的名字下
```
### router.js 應用

### 單頁 one router-view

![](https://i.imgur.com/oXDw0TG.png)

app.vue
```
<template>
  <div id="app">
    <p>{{$t('message.i1')}}</p>
    <img src="./assets/logo.png">
    //對應router.js 原本為default
    <router-view name="nav"></router-view>
    //對應router.js 此處為導覽 的上方條列 
    <router-view/>
    
  </div>
</template>
```
router.js
```
import Login from './components/login.vue'
import Header from './components/header.vue'
import Home from './components/home.vue'

export const routes = [
  {
    path: '/login',         //路由路徑
    component: Login,       //相對應comopnent
    name: 'login'           // 可以透過路由url 跳轉直接導向該相對應名稱
  },
  {
    path: '/',
    components: {
      default: Home,
      nav: Header
    },
    name: 'home'
  }
```
herader.vue
```
<template>
  <div>
  //對印到 相對應 name路由
    <router-link :to="{name:'home'}">Home</router-link>
    <router-link :to="{name:'userinfo'}">User Info</router-link>
    <router-link :to="{name:'test'}">test</router-link>

</template>
```
### 單頁 multi router-view

![](https://i.imgur.com/vlZrJJB.png)

> app.vue 照第一步走 往後新增下列程式碼

router.js
```
import test from './components/test.vue'
import test2 from './components/h1.vue'
import test3 from './components/h2.vue'
  {                          
    path: '/test',
    components: {
      default: test,
      nav: Header
    },
    name: 'test',

    children: [
      {
        path: '/h1',
        components: {
          nav2: test
        },
        name: 'h1'
      },
      {
        path: '/h2',
        components: { nav2: test3 },
        name: 'h2'
      }
    ]
  },
```
test.vue
```
<template>
  <div>
    <router-link :to="{name:'h1'}">h1</router-link>
    <router-link :to="{name:'h2'}">h2</router-link>

    <h1>test</h1>
    <router-view name="nav2" style="float:left;width:50%;background-color:#ccc;height:300px;"></router-view>

  </div>
</template>
```
h1.vue
```
<template>
  <h1>test2</h1>
</template>
```
