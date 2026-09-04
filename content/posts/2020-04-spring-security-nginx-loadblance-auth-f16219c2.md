---
title: "Spring Security 認證中心 重構新增 Nginx loadblance 與 auth 集群"
date: "2020-04-19T17:20:00.001+08:00"
updated: "2020-05-18T13:04:38.903+08:00"
permalink: "/2020/04/spring-security-nginx-loadblance-auth.html"
original_url: "https://x8795278.blogspot.com/2020/04/spring-security-nginx-loadblance-auth.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-4277022494435094304"
tags: ["Redis", "Tutorial"]
layout: post
---

![](https://i.imgur.com/uK1g78i.png)

## 特性

- 使用 JWT 進行鑑權，支持 token 過期
- 使用 Ehcache 進行快取，減少每次鑑權對資料庫的壓力
- 盡可能貼合 Spring Security 的設計
- 實現註解權限控制
- 未來可能再加一個 redis Cluster 有空再加了

## add

- add header filter example
- change Ehcache to redis single cache
- change auth Cluster
- use nginx loadblance
- add nginx loadblance confg

## call function

```
private static void sendRequest() throws Exception{ HttpPost post = new HttpPost("http://192.168.0.146:8080/login"); // add request parameter, form parameters List<NameValuePair> urlParameters = new ArrayList<>(); urlParameters.add(new BasicNameValuePair("username", "jack")); urlParameters.add(new BasicNameValuePair("password", "jack123")); //urlParameters.add(new BasicNameValuePair("custom", "secret")); post.setEntity(new UrlEncodedFormEntity(urlParameters)); try (CloseableHttpClient httpClient = HttpClients.createDefault(); CloseableHttpResponse response = httpClient.execute(post)) { System.out.println(EntityUtils.toString(response.getEntity())); } } private static void sendGet() throws ClientProtocolException, IOException { HttpGet request = new HttpGet("http://192.168.0.146:8080/user"); // add request headers request.addHeader("Authorization", "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1Nzc0MjI0NDYsInVzZXJuYW1lIjoiamFjayJ9.iOLivJ6D2L9Ot7IznfSlp-TRgDSAvE53UIUo3c0PBQo"); // request.addHeader(HttpHeaders.USER_AGENT, "Googlebot"); try (CloseableHttpResponse response = httpClient.execute(request)) { // Get HttpResponse Status System.out.println(response.getStatusLine().toString()); HttpEntity entity = response.getEntity(); Header headers = entity.getContentType(); System.out.println(headers); if (entity != null) { // return it as a String String result = EntityUtils.toString(entity); System.out.println(result); } } }
```

# Quick start

# ./start.bat

# server port

# nginx :port 9800nginx client1 :port 9801nginx client2:port 9802auth1 :port 9803auth2 :port 9804

# Postman

# login/post <http://localhost:8080/login> ![](https://i.imgur.com/Ao5W3my.png) user/get <http://localhost:8080/user> ![](https://i.imgur.com/0wB5IiK.png)

# redis

![](https://i.imgur.com/KZv2T3i.png) ![](https://i.imgur.com/zP5MrLW.png)

# Original project

# <https://github.com/Smith-Cruise/Spring-Boot-Security-JWT-SPA>
