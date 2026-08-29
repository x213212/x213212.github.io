---
title: "以 Spring Boot 搭建一個 API Server (三) 使用 Spring Data JPA 完成 Restful/CRUD"
date: "2019-12-11T10:12:00.001+08:00"
updated: "2019-12-11T11:54:16.202+08:00"
permalink: "/2019/12/spring-boot-api-server-spring-data-jpa.html"
original_url: "https://x8795278.blogspot.com/2019/12/spring-boot-api-server-spring-data-jpa.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8308403776915733694"
tags: ["Java", "spring boot", "spring mvc"]
layout: post
---

# 什麼是 Restful?

Representational State Transfer，簡稱REST，它是一種網路架構風格，他並不是一種標準。
而 RESTful 可以這樣子想像: 美麗 (Beauty) 的事物可以稱為 Beautiful; 設計為 REST 的系統就可以稱為 RESTful
以 API 而言，假設我們正在撰寫一組待辦事項的 API，  

可能會有以下方式來作為 API 的 interface:
獲取使用者資料 /getAllUsers  

獲取使用者資料 /getUser/1  

新增使用者資料 /createUser  

更新使用者資料 /updateUser/1  

刪除使用者資料 /deleteUser/1
若是以 REST 風格來開發 RESTful API 的話:
獲取使用者資料 /GET /users  

獲取使用者資料 /GET /user/1  

新增使用者資料 /POST /user  

更新使用者資料 /PUT /user/1  

刪除使用者資料 /DELETE /user/1
兩者差異是在於 RESTful API 充分地使用了 HTTP protocol (GET/POST/PUT/DELETE)，達到:
以直觀簡潔的資源 URI  

並且善用 HTTP Verb  

達到對資源的操作  

並使用 Web 所接受的資料類型: JSON, XML, YAML 等，最常見的是 JSON  

通常是使用 HTTP, URI, JSON, HTML 這些現有廣泛流行的協議和標準，且使用 HTTP status code 來代表該資源的狀態。  

框架中強制使用 REST 風格的最有名的應該就是 Ruby on Rails 了!  

p.s. 因為 REST 並非是一種標準，因此有時候也不一定非得要照著 REST 來做，  

只是在資源的操作面上，可以設計成這類的風格，以達到簡潔易懂，並且可重用。
# Restful 優缺點

RESTful 的優點如下所列:
瀏覽器即可以作為 client 端  

可以更高效地利用 cache 來達到更快的回應速度  

界面與資料分離  

節省伺服器的計算資源  

可重用! web/android/ios 都可以用, 無痛轉換!  

RESTful 的要求:

- client - server 架構  
  分層系統  
  利用快取機制增加效能

- server-side:  
  在 GET 資源時，若該資源並沒有被變更，就可以利用 cache 機制減少 query，並且加快回應速度

- client-side:  
  透過 client 端 cache 記錄 cache 版本，  
  若向 server 要求資源時發現 server 最新版與 cache 相同，  
  則 client 端直接取用本地資源即可，不需要再做一次查詢  
  省機器運算及流量 = 省錢  
  通訊協定具有無狀態性  
  不能讓兩隻 API 做同一個動作!  
  假設完成轉賬手續必須先 call A 再 call B 的話，  
  若做完 A 後斷線導致 B 無法執行，後續要處理 A -> B 的方式會很麻煩  
  且不應該假設伺服器知道目前的狀態!  
  因此設計出來的 API 不能有狀態性  
  統一界面  
  使用 HTTP Verb: GET/POST/PUT/DELETE  
  轉載 <https://ithelp.ithome.com.tw/articles/10157674>

# Service Interface

那麼我們把上一次的 service 升級為 restful 風格吧!
```
package com.example.demo.service;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PathVariable;

import com.example.demo.entity.UserEntity;

public interface IUserService {

     UserEntity saveUser(UserEntity userEntity);
     UserEntity updateUser(UserEntity userEntity);
     List<UserEntity> getdAllUser();
     UserEntity getUser(Integer userId);
     void delUser(Integer userId);

}
```
# Service Implements

```
package com.example.demo.service.impl;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.PathVariable;

import com.example.demo.dao.UsersDao;
import com.example.demo.entity.UserEntity;
import com.example.demo.service.IUserService;

@Service
public class UserServiceImpl implements IUserService {
 @Autowired
 private UsersDao userDao;

 @Override
 public UserEntity saveUser(UserEntity userEntity) {
  // TODO Auto-generated method stub
  return userDao.save(userEntity);
 }

 @Override
 public UserEntity updateUser(UserEntity userEntity) {
  // TODO Auto-generated method stub
  return userDao.saveAndFlush(userEntity);
 }

 @Override
 public List<UserEntity> getdAllUser() {
  // TODO Auto-generated method stub
  return userDao.findAll();
 }

 @Override
 public UserEntity getUser(Integer userId) {
  // TODO Auto-generated method stub
  return userDao.findById(userId).get();

 }

 @Override
 public void delUser(Integer userId) {
  // TODO Auto-generated method stub
  userDao.deleteById(userId);
 }
}
```
# Controller

```
package com.example.demo.web.controller;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.demo.dao.UsersDao;
import com.example.demo.entity.UserEntity;
import com.example.demo.service.IUserService;

@RestController
@RequestMapping("/users")
public class UserController {
 @Autowired
 IUserService userService;
 
 @PostMapping("/save")
 public UserEntity save (@RequestBody UserEntity userEntity)
 {
  return userService.saveUser(userEntity);
 }
 
 @PutMapping("/update") 
 public UserEntity update(@RequestBody UserEntity userEntity)
 {
  return  userService.updateUser(userEntity);
 }
 
 @GetMapping("/getAll")
 public List<UserEntity> getAllUser()
 {
  return   userService.getdAllUser();
 }
 
 @GetMapping("/get/{id}")
 public  UserEntity getUserById(@PathVariable(name = "id") Integer employeeId)
 {

  return  userService.getUser(employeeId);
 }
 @DeleteMapping("/del/{id}")
 public  void delUserById(@PathVariable(name = "id") Integer employeeId)
 {

   userService.delUser(employeeId);
 }

}
```
# PostMan

注意 Raw 那邊選用 json 格式
# Save

![](https://i.imgur.com/BUTxPJ5.png)

```
action : post
api url : http://localhost:8080/users/save
body : 
{
 "age" : 55,
 "name" : "test"
}
```
我們的 Entity 層有寫 @GeneratedValue(strategy = GenerationType.AUTO)
id會 自動遞增
```
@GeneratedValue(strategy = GenerationType.AUTO)
```
# Update

![](https://i.imgur.com/DZPvnDn.png)

```
action : put
api url : http://localhost:8080/users/update
body : 
{
 "age" : 56,
 "name" : "test"
}
```
我們的 Entity 層有寫 @GeneratedValue(strategy = GenerationType.AUTO)
# Get

![](https://i.imgur.com/DU7Xsht.png)

```
action : put
api url : http://localhost:8080/users/getAll
```

![](https://i.imgur.com/QARabfJ.png)

```
action : put
api url : http://localhost:8080/users/get/1
```
# Delete

![](https://i.imgur.com/CySIUSc.png)

```
action : delete
api url : http://localhost:8080/users/del/1
```
上述這些動作可以看到 Spring cosole 的動作  

![](https://i.imgur.com/owHA2kL.png)

這些所有動作都交給我的Spring Boot 去幫我操作 Crud 所以我們就不用 學習每個資料庫只要知道怎調用就好，常常有人說 這樣的話 在進行一些 資料上比較要細部調教的話 會有效能的問題，一般來說 可以用 Mybatis 自己寫 sql。
