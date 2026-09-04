---
title: "以 Spring Boot 搭建一個 API Server (一) 集成 MyBatis 數據層篇"
date: "2019-12-07T00:41:00.001+08:00"
updated: "2019-12-11T07:28:58.474+08:00"
permalink: "/2019/12/ssm-spring-boot-mybatis.html"
original_url: "https://x8795278.blogspot.com/2019/12/ssm-spring-boot-mybatis.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5444652442320350544"
tags: ["Java", "MyBatis", "spring boot", "Tutorial"]
layout: post
---

![](https://i.imgur.com/jSgF4eS.png)

# 搭建一個簡單的 SSM 架構

框架上一定要有初步的認識，所以我們來快速熟悉一下本系列只是入門等哪天碰到應該就可以快速上手
## 基本概念

- Spring

Spring是一個開源框架，Spring是於2003 年興起的一個輕量級的Java 開發框架，由Rod Johnson 在其著作Expert One-On-One J2EE Development and Design中闡述的部分理念和原型衍生而來。它是為了解決企業應用開發的複雜性而創建的。Spring使用基本的JavaBean來完成以前只可能由EJB完成的事情。然而，Spring的用途不僅限於伺服器端的開發。從簡單性、可測試性和松耦合的角度而言，任何Java應用都可以從Spring中受益。 簡單來說，Spring是一個輕量級的控制反轉（IoC）和面向切面（AOP）的容器框架。

- SpringMVC

Spring MVC屬於SpringFrameWork的後續產品，已經融合在Spring Web Flow裡面。Spring MVC 分離了控制器、模型對象、分派器以及處理程序對象的角色，這種分離讓它們更容易進行定製。

- MyBatis

MyBatis 本是apache的一個開源項目iBatis, 2010年這個項目由apache software foundation 遷移到了google code，並且改名為MyBatis。MyBatis是一個基於Java的持久層框架。iBATIS提供的持久層框架包括SQL Maps和Data Access Objects（DAO）MyBatis 消除了幾乎所有的JDBC程式碼和參數的手工設置以及結果集的檢索。MyBatis 使用簡單的 XML或註解用於配置和原始映射，將介面和 Java 的POJOs（Plain Old Java Objects，普通的 Java對象）映射成資料庫中的記錄。
那麼我就開始搭建一個乾淨的 SSM專案吧!
# 整合 MyBatis 數據層篇

# 目錄結構

![](https://i.imgur.com/UYP6APo.png)

編寫一個簡單範例
# 新建專案

![](https://i.imgur.com/DrLFhZ2.png)

  

![](https://i.imgur.com/6qWNbOv.png)

![](https://i.imgur.com/nePcOca.png)

# 導入 jar

mysql-connector-java  

<https://jar-download.com/artifacts/mysql/mysql-connector-java>  

mybantis  

<https://github.com/mybatis/mybatis-3/releases>  

![](https://i.imgur.com/fZ9q7PR.png)

# 產生表

![](https://i.imgur.com/sPFM7cE.png)

```
CREATE DATABASE mybatis;
USE mybatis;
CREATE TABLE users (id INT PRIMARY KEY AUTO_INCREMENT, NAME VARCHAR(20),age INT);
INSERT INTO users(NAME , age) VALUES ('TOM',12);
INSERT INTO users(NAME , age) VALUES ('JACK',12);
```

![](https://i.imgur.com/qUfDBhN.png)

# 新增 Mybatis 設定檔 conf.xml

```
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE configuration
  PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
  "http://mybatis.org/dtd/mybatis-3-config.dtd">
<configuration>
 <environments default="development">
  <environment id="development">
   <transactionManager type="JDBC" />
   <dataSource type="POOLED">
    <property name="driver" value="com.mysql.jdbc.Driver" />
    <property name="url" value="jdbc:mysql://localhost:3306/mybatis" />
    <property name="username" value="root" />
    <property name="password" value="root" />
   </dataSource>
  </environment>
 </environments>
  <mappers>
    <mapper resource="com/exapmle/mybatis/test1/userMapper.xml"/>
  </mappers>
</configuration>
```
# 新增 對應資料庫 table entity class

User.java
```
package com.exapmle.mybatis.test1;

public class User {
 private int id ;
 private String name;
 private int age;
 public User() {
  super();
  // TODO Auto-generated constructor stub
 }
 public User(int id, String name, int age) {
  super();
  this.id = id;
  this.name = name;
  this.age = age;
 }
 public int getId() {
  return id;
 }
 public void setId(int id) {
  this.id = id;
 }
 public String getName() {
  return name;
 }
 public void setName(String name) {
  this.name = name;
 }
 public int getAge() {
  return age;
 }
 public void setAge(int age) {
  this.age = age;
 }
 @Override
 public String toString() {
  return "User [id=" + id + ", name=" + name + ", age=" + age + "]";
 }
 
}
```
# 定義 操作 users table sql 映射

userMaaper.xml

- namespace  
  這邊要注意對應的位置要跟 自己的目錄相互對應

- id  
  對應函式動作

- select  
  內部sql 可以自行定義為更複雜結構  
  多參數可以參考  
  <https://www.cnblogs.com/mingyue1818/p/3714162.html>
- resultType  
  返回一個 entity 物件

- parameterType  
  參數類型

```
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper
  PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
  "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.exapmle.mybatis.test1.userMapper">
  <select id="selectUser" resultType="com.exapmle.mybatis.test1.User" parameterType="int">
    select * from users where id = #{id}
  </select>
</mapper>
```
# conf.xml 註冊 sql 映射 xml

```
<mappers>
    <mapper resource="com/exapmle/mybatis/test1/userMapper.xml"/>
  </mappers>
```
# enjoy

```
package com.example.demo;

import java.io.InputStream;

import org.apache.ibatis.session.SqlSession;
import org.apache.ibatis.session.SqlSessionFactory;
import org.apache.ibatis.session.SqlSessionFactoryBuilder;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import com.exapmle.mybatis.test1.User;

@SpringBootApplication
public class Demo1Application {

 public static void main(String[] args) {
  SpringApplication.run(Demo1Application.class, args);
  String resource = "conf.xml";
  InputStream is =Demo1Application.class.getClassLoader().getResourceAsStream(resource);
  SqlSessionFactory factory = new SqlSessionFactoryBuilder().build(is);
  try (SqlSession session = factory.openSession()) {
     User user = (User) session.selectOne("com.exapmle.mybatis.test1.userMapper.selectUser", 1);

     System.out.println(user.getName());
   }
 }

}
```
# 執行結果

![](https://i.imgur.com/76gSTqy.png)
