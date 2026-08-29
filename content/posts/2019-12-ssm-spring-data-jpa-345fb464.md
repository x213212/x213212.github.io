---
title: "以 Spring Boot 搭建一個 API Server (二) 集成 Spring Data JPA數據層篇"
date: "2019-12-11T06:26:00.000+08:00"
updated: "2019-12-11T09:52:58.739+08:00"
permalink: "/2019/12/ssm-spring-data-jpa.html"
original_url: "https://x8795278.blogspot.com/2019/12/ssm-spring-data-jpa.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2515031169244000498"
tags: ["Java", "spring boot", "spring mvc", "Tutorial"]
layout: post
---

# 搭建Spring data jpa 數據層

在開始之前要先了解一下目錄架構擺放位置，上一次 mybatis 數據層篇，位置沒有照規定擺，這次來以  

Spring MVC架構 來進行擺放，mybatis 也可以這樣擺看看，今天是以 Spring Data Jpa 來集合 數據層，應該對理解 MVC 比較不會抽象了吧)? XD
# DAO層，Service層，Controller層、View層詳解

- MVC  
  
  ![](https://i.imgur.com/firxHSC.png)

- Spring MVC  
  
  ![](https://i.imgur.com/cew4RZv.png)
  
    
  差不多像上述的圖，懶的話 XD

- 1、Dao層

Dao層主要是做資料持久層的工作，負責與資料庫進行聯絡的一些任務都封裝在此，Dao層的設計首先是設計Dao的介面，然後在Spring的配置檔案中定義此介面的實現類，然後就可在模組中呼叫此介面來進行資料業務的處理，而不用關心此介面的具體實現類是哪個類，顯得結構非常清晰，Dao層的資料來源配置，以及有關資料庫連線的引數都在Spring的配置檔案中進行配置。

- 2、Service層

Service層主要負責業務模組的邏輯應用設計。同樣是首先設計介面，再設計其實現的類，接著再Spring的配置檔案中配置其實現的關聯。這樣我們就可以在應用中呼叫Service介面來進行業務處理。Service層的業務實現，具體要呼叫到已定義的Dao層的介面，封裝Service層的業務邏輯有利於通用的業務邏輯的獨立性和重複利用性，程式顯得非常簡潔。

- 3、Controller層

Controller層負責具體的業務模組流程的控制，在此層裡面要呼叫Service層的介面來控制業務流程，控制的配置也同樣是在Spring的配置檔案裡面進行，針對具體的業務流程，會有不同的控制器，我們具體的設計過程中可以將流程進行抽象歸納，設計出可以重複利用的子單元流程模組，這樣不僅使程式結構變得清晰，也大大減少了程式碼量。

- 4、View層

View層與控制層結合比較緊密，需要二者結合起來協同工作。View層主要負責網頁前臺的Jsp頁面的表示。
View 方面 就是 使用者觸發 Controller，然後 Controller 處理完資料再填入 View  
這邊可以暫時理解為使用者觸發 Restful Api
```
http://localhost:8080/users/findall
http://localhost:8080/users/a/2
```
所以以上述例子觸發的流程就是  

![](https://i.imgur.com/EJa2sDV.png)

# 新建專案

![](https://i.imgur.com/OldUlke.png)

# 目錄擺放位置

![](https://i.imgur.com/riAA3mu.png)

# 新增 配置檔案 application.properties

```
spring.datasource.url = jdbc:mysql://localhost:3306/mybatis?serverTimezone=UTC
spring.datasource.username = root

spring.datasource.password = root

# Keep the connection alive if idle for a long time (needed in production)
spring.datasource.testWhileIdle = true
spring.datasource.validationQuery = SELECT 1

# Show or not log for each sql query
spring.jpa.show-sql = true

# Hibernate ddl auto (create, create-drop, update)
spring.jpa.hibernate.ddl-auto = update

# Naming strategy
spring.jpa.hibernate.naming-strategy = org.hibernate.cfg.ImprovedNamingStrategy

# Use spring.jpa.properties.* for Hibernate native properties (the prefix is
# stripped before adding them to the entity manager)

# The SQL dialect makes Hibernate generate better SQL for the chosen database
spring.jpa.properties.hibernate.dialect = org.hibernate.dialect.MySQL5Dialect
```
# 新建 Entity

此資料庫對應的是 上一次的 mybatis 資料庫結構
```
package com.example.demo.entity;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.Table;

@Entity

@Table(name = " users", catalog = "mybatis")

public class UserEntity {
 @Id
 @Column (name = "id")
 @GeneratedValue(strategy = GenerationType.AUTO)
 private Integer id;
 @Column (name = "name")
 private String Name ;
    @Column (name = "age")
 private Integer age;
 
 public Integer getId() {
  return id;
 }
 public void setId(Integer id) {
  this.id = id;
 }
 public String getName() {
  return Name;
 }
 public void setName(String name) {
  Name = name;
 }
 public Integer getAge() {
  return age;
 }
 public void setAge(Integer age) {
  this.age = age;
 }
}
```
# 新增 Dao 層

```
package com.example.demo.dao;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import org.springframework.web.bind.annotation.PathVariable;

import com.example.demo.entity.UserEntity;

@Repository
public interface UsersDao  extends JpaRepository <UserEntity,Integer>{

}
```
# 新增 Service 層 interface

```
package com.example.demo.service;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PathVariable;

import com.example.demo.entity.UserEntity;

public interface IUserService {

 
 public List<UserEntity> findAllUser();
 public UserEntity getEmplpyee(Integer employeeId);
}
```
# 新增 Service implements

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
 public List<UserEntity> findAllUser() {
  // TODO Auto-generated method stub
  return userDao.findAll();
 }

 @Override
 public UserEntity getEmplpyee(Integer employeeId) {
  // TODO Auto-generated method stub
 
  return userDao.findById(employeeId).get();
 }
}
```
# 新增 Controller

```
package com.example.demo.web.controller;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
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
 
 @GetMapping("/findall")
 public List<UserEntity> getAll()
 {
  return   userService.findAllUser();
 }
 
 @GetMapping("/a/{id}")
 public  UserEntity getEmplpyee(@PathVariable(name = "id") Integer employeeId)
 {

  return  userService.getEmplpyee(employeeId);
 }

}
```
# Restful api

```
http://localhost:8080/users/findall
http://localhost:8080/users/a/2
```
# 執行結果

![](https://i.imgur.com/gOterxE.png)

![](https://i.imgur.com/FP9f5PA.png) 這樣的話大概API Server 雛型就完成了，下面幾章可能補足 Crud，或者引用現有前端框架 拿Vue.js 來做結合，包括一些權限，部屬到 tomacat上。
