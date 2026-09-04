---
title: "OpenResty + nginx + redis + spring 如何達到高吞吐量伺服器的架構? (四) 負載平衡下的 session 共存"
date: "2019-07-10T17:26:00.005+08:00"
updated: "2019-07-14T00:03:01.559+08:00"
permalink: "/2019/07/openresty-nginx-redis-spring-session.html"
original_url: "https://x8795278.blogspot.com/2019/07/openresty-nginx-redis-spring-session.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6197663141039367647"
tags: ["nginx", "openresty", "Redis", "spring boot", "Tutorial"]
layout: post
---

在一般的傳統下最簡單的方法就是 跟伺服器 登入帳號密碼就取得一個 key 然後伺服器返回 一個 hash 然後我們的 就可以 照著這個 key 去判斷到底是 不是維持這組帳號 是不是 中斷，然後 我們伺服器後端 也必須要去記錄到底 是誰使用這個 cookie，這組帳號 能不能 從其他地放登入等等， 為什麼要使用 spring boot + redis 去設計，比較可能的原因就是 在每一個 method 的請求 都必須要夾帶 cookie 去判別到底是否維持登入的狀態 類似簽章的功能那我們的系統大致上來模擬一下，比較需要注意的是下面 nginx 我們要做的功能有大致上這些 首先我們要到 - vue axios 開啟每次請求都夾帶cookie - install redis - 配置 spring boot - 編譯 spring boot 成 兩個 port (以提供測試 - 搭配 nginx 使用負載平衡 觀看 key 值是否有不同 - 在 login 的頁面 同一個瀏覽器下，是否可以達到 不用 登入帳號密碼直接導向內部畫面

![](https://i.imgur.com/dEb8XQX.png)

這個 chrome 插件已經用很久了 <https://www.one-tab.com/page/Kp3ClDzwTRyFcfL8NACpKQ>

# Install redis

apt-get install redis ![](https://i.imgur.com/E483xmK.png) redis-server ![](https://i.imgur.com/iCJ3PKy.png) redis-cli ![](https://i.imgur.com/irC7T1e.png) ![](https://i.imgur.com/Gb0M0B4.png) <https://www.cnblogs.com/haoliansheng/p/5866149.html> [https://qbgbook.gitbooks.io/spring-boot-reference-guide-zh/II. Getting started/11.5. Creating an executable jar.html?q=](https://qbgbook.gitbooks.io/spring-boot-reference-guide-zh/II.%20Getting%20started/11.5.%20Creating%20an%20executable%20jar.html?q=) mvnw.cmd package

```
<?xml version="1.0" encoding="UTF-8"?> <project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd"> <modelVersion>4.0.0</modelVersion> <parent> <groupId>org.springframework.boot</groupId> <artifactId>spring-boot-starter-parent</artifactId> <version>2.0.5.RELEASE</version> <relativePath/> <!-- lookup parent from repository --> <!-- 2.1.5.RELEASE--> </parent> <groupId>com.example</groupId> <artifactId>demo</artifactId> <version>0.0.1-SNAPSHOT</version> <name>demo</name> <description>Demo project for Spring Boot</description> <properties> <java.version>1.8</java.version> </properties> <dependencies> <dependency> <groupId>org.springframework.boot</groupId> <artifactId>spring-boot-starter-web</artifactId> </dependency> <dependency> <groupId>org.springframework.boot</groupId> <artifactId>spring-boot-starter-test</artifactId> <scope>test</scope> </dependency> <dependency> <groupId>org.springframework.boot</groupId> <artifactId>spring-boot-starter-thymeleaf</artifactId> </dependency> <dependency> <groupId>org.springframework.boot</groupId> <artifactId>spring-boot-starter-data-redis</artifactId> </dependency> <dependency> <groupId>org.springframework.session</groupId> <artifactId>spring-session-data-redis</artifactId> </dependency> </dependencies> <build> <defaultGoal>compile</defaultGoal> <plugins> <plugin> <groupId>org.springframework.boot</groupId> <artifactId>spring-boot-maven-plugin</artifactId> </plugin> <plugin> <groupId>org.apache.maven.plugins</groupId> <artifactId>maven-surefire-plugin</artifactId> <version>2.19.1</version> </plugin> </plugins> </build> </project>
```

![](https://i.imgur.com/HZeGPqU.png) ![](https://i.imgur.com/lVFdN8f.png) ![](https://i.imgur.com/LGFm2kG.png) ![](https://i.imgur.com/NbPp1dN.png) ![](https://i.imgur.com/LQmd2Co.png) ![](https://i.imgur.com/LTE4YAQ.png) <https://www.one-tab.com/page/y3Ow6xcVT06xSAEdn46kmg> 使用vue anios 模組必須要注意 需要再 axios.defaults.withCredentials=true;//让ajax携带cookie 這樣才能 讓 spring boot 內建 的 redis 共享內存工作 然後 我們也要讓後端 的 ![](https://i.imgur.com/1E4mNJz.png) 這邊 加上 再來 就是配上 nginx 共享內存就完成囉!

# 由 spring boot 幫我們管理 session

```
///跨網域 @Bean public WebMvcConfigurer corsConfigurer() { return new WebMvcConfigurer() { @Override public void addCorsMappings(CorsRegistry registry) { registry.addMapping("/httpMethod/**") .allowCredentials(true) .allowedOrigins("*");//允许域名访问，如果*，代表所有域名 //.allowedOrigins("http://localhost:9527");//允许域名访问，如果*，代表所有域名 registry.addMapping("/httpMethod2**") .allowedMethods("GET") .allowCredentials(true) .allowedOrigins("http://localhost:8080");//允许域名访问，如果*，代表所有域名 registry.addMapping("/setSession") .allowCredentials(true) .allowedOrigins("*");//允许域名访问，如果*，代表所有域名 //.allowedOrigins("http://localhost:9527");//允许域名访问，如果*，代表所有域名 registry.addMapping("/getSession") .allowCredentials(true) .allowedMethods("GET") .allowedOrigins("*");//允许域名访问，如果*，代表所有域名 registry.addMapping("/removeSession") .allowCredentials(true) .allowedMethods("GET") .allowedOrigins("*");//允许域名访问，如果*，代表所有域名 } }; } @RequestMapping(value = "/setSession", method = RequestMethod.GET) @CrossOrigin public void setSession(HttpServletRequest request, HttpServletResponse response) { System.out.println(request.getSession().getId().toString()); request.getSession().setAttribute("name", "test"); // request.getSession().setAttribute("name2", "tom2"); } @RequestMapping(value = "/getSession", method = RequestMethod.GET) @CrossOrigin public List getInterestPro(HttpServletRequest request, HttpServletResponse response) throws JsonProcessingException{ System.out.println(request.getSession().getId().toString()); System.out.println(request.getSession().getAttribute("name")); ObjectMapper objectMapper = new ObjectMapper(); if( request.getSession().getAttribute("name") != null) listest2.setCode(200); else listest2.setCode(404); //select 所有 redis Set<byte[]> keys = jedisConnectionFactory().getConnection().keys("*sessions:expires*".getBytes()); Iterator<byte[]> it = keys.iterator(); while(it.hasNext()){ byte[] data = (byte[])it.next(); System.out.println(new String(data, 0, data.length)); } String userJsonStr = objectMapper.writeValueAsString(listest2); //System.out.print(userJsonStr); return listest2; } @Bean JedisConnectionFactory jedisConnectionFactory() { JedisConnectionFactory jedisConFactory = new JedisConnectionFactory(); jedisConFactory.setHostName("localhost"); jedisConFactory.setPort(6379); return jedisConFactory; } @Bean public RedisTemplate<String, Object> redisTemplate() { RedisTemplate<String, Object> template = new RedisTemplate<>(); template.setConnectionFactory(jedisConnectionFactory()); return template; }
```

# 進階

這邊比較進階的是除了 在 spring boot 內建的 session 可以操作 redis 的話 我們可能要考慮後期配置，我們在 加開一個 可以額外操作key 的地方，或許 可以達到監控，那我們可以做到 一個 key 只能登入 一台電腦的效果 那麼實際運作的圖就是 ![](https://i.imgur.com/o5yOhhe.png)

```
//select 所有 redis Set<byte[]> keys = jedisConnectionFactory().getConnection().keys("*sessions:expires*".getBytes()); Iterator<byte[]> it = keys.iterator(); while(it.hasNext()){ byte[] data = (byte[])it.next(); System.out.println(new String(data, 0, data.length)); }
```

# 配置檔案篇

pom.xml檔案已經也丟在 github 上面以提供瀏覽

```
<?xml version="1.0" encoding="UTF-8"?> <project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd"> <modelVersion>4.0.0</modelVersion> <parent> <groupId>org.springframework.boot</groupId> <artifactId>spring-boot-starter-parent</artifactId> <version>2.0.5.RELEASE</version> <relativePath/> <!-- lookup parent from repository --> <!-- 2.1.5.RELEASE--> </parent> <groupId>com.example</groupId> <artifactId>demo</artifactId> <version>0.0.1-SNAPSHOT</version> <name>demo</name> <description>Demo project for Spring Boot</description> <properties> <java.version>1.8</java.version> </properties> <dependencies> <dependency> <groupId>org.springframework.boot</groupId> <artifactId>spring-boot-starter-web</artifactId> </dependency> <dependency> <groupId>org.springframework.boot</groupId> <artifactId>spring-boot-starter-test</artifactId> <scope>test</scope> </dependency> <dependency> <groupId>org.springframework.boot</groupId> <artifactId>spring-boot-starter-thymeleaf</artifactId> </dependency> <dependency> <groupId>org.springframework.boot</groupId> <artifactId>spring-boot-starter-data-redis</artifactId> </dependency> <dependency> <groupId>org.springframework.session</groupId> <artifactId>spring-session-data-redis</artifactId> </dependency> <dependency> <groupId>org.springframework.data</groupId> <artifactId>spring-data-redis</artifactId> <version>2.0.3.RELEASE</version> </dependency> <dependency> <groupId>redis.clients</groupId> <artifactId>jedis</artifactId> <version>2.9.0</version> <type>jar</type> </dependency> </dependencies> <build> <defaultGoal>compile</defaultGoal> <plugins> <plugin> <groupId>org.springframework.boot</groupId> <artifactId>spring-boot-maven-plugin</artifactId> </plugin> <plugin> <groupId>org.apache.maven.plugins</groupId> <artifactId>maven-surefire-plugin</artifactId> <version>2.19.1</version> </plugin> </plugins> </build> </project>
```

#
