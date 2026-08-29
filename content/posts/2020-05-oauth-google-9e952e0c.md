---
title: "透過 OAuth2.0 使用 Google登入 範例"
date: "2020-05-09T16:21:00.001+08:00"
updated: "2020-05-18T13:04:38.903+08:00"
permalink: "/2020/05/oauth-google.html"
original_url: "https://x8795278.blogspot.com/2020/05/oauth-google.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6077847814385661175"
tags: ["google", "OAuth 2.0", "spring boot", "spring security", "Tutorial"]
layout: post
---

# OAuth2.0

簡介 OAuth 2.0  

在傳統的 Client-Server 架構裡， Client 要拿取受保護的資源 (Protected Resoruce) 的時候，要向 Server 出示使用者 (Resource Owner) 的帳號密碼才行。為了讓第三方應用程式也可以拿到這些 Resources，則 Resource Owner 要把帳號密碼給這個第三方程式，這樣子就會有以下的問題及限制：
第三方程式必須儲存 Resource Owner 的帳號密碼，通常是明文儲存。  

Server 必須支援密碼認證，即使密碼有天生的資訊安全上的弱點。  

第三方程式會得到幾乎完整的權限，可以存取 Protected Resources，而 Resource Owner 沒辦法限制第三方程式可以拿取 Resource 的時效，以及可以存取的範圍 (subset)。  

Resource Owner 無法只撤回單一個第三方程式的存取權，而且必須要改密碼才能撤回。  

任何第三方程式被破解 (compromized)，就會導致使用該密碼的所有資料被破解。  

OAuth 解決這些問題的方式，是引入一個認證層 (authorization layer)，並且把 client 跟 resource owner 的角色分開。在 OAuth 裡面，Client 會先索取存取權，來存取 Resource Owner 擁有的資源，這些資源會放在 Resource Server 上面，並且 Client 會得到一組不同於 Resource Owner 所持有的認證碼 (credentials)。
Client 會取得一個 Access Token 來存取 Protected Resources，而非使用 Resource Owner 的帳號密碼。Access Token 是一個字串，記載了特定的存取範圍 (scope)、時效等等的資訊。Access Token 是從 Authorization Server 拿到的，取得之前會得到 Resource Owner 的許可。Client 用這個 Access Token 來存取 Resource Server 上面的 Protected Resources。
實際使用的例子：使用者 (Resource Owner) 可以授權印刷服務 (Client) 去相簿網站 (Resource Server) 存取他的私人照片，而不需要把相簿網站的帳號密碼告訴印刷服務。這個使用者會直接授權透過一個相簿網站所信任的伺服器 (Authorization Server)，核發一個專屬於該印刷服務的認證碼 (Access Token)。
OAuth 是設計來透過 HTTP 使用的。透過 HTTP 以外的通訊協定來使用 OAuth 則是超出 spec 的範圍。
<https://blog.yorkxin.org/2013/09/30/oauth2-1-introduction.html>
目前我只想大概就是申請帳號這個流程不想再重新再辦一次那麼我有其他社群軟體網站的帳號可以去做登入的動作順便可以取得之前申請帳號所取得申請資料  

以下以google login 來作範例
# 申請 google Oauth憑證

![](https://i.imgur.com/NVv0ca6.png)

  

![](https://i.imgur.com/GP6b7iz.png)

```
已授權的重新導向 URL
http://localhost:8080/login/oauth2/code/google
```
# pom.xml

```
<dependencies>
  <dependency>
   <groupId>org.springframework.boot</groupId>
   <artifactId>spring-boot-starter-oauth2-client</artifactId>
  </dependency>
  <dependency>
   <groupId>org.springframework.boot</groupId>
   <artifactId>spring-boot-starter-security</artifactId>
  </dependency>
  <dependency>
   <groupId>org.springframework.boot</groupId>
   <artifactId>spring-boot-starter-web</artifactId>
  </dependency>

  <dependency>
   <groupId>org.springframework.boot</groupId>
   <artifactId>spring-boot-starter-test</artifactId>
   <scope>test</scope>
   <exclusions>
    <exclusion>
     <groupId>org.junit.vintage</groupId>
     <artifactId>junit-vintage-engine</artifactId>
    </exclusion>
   </exclusions>
  </dependency>
  <dependency>
   <groupId>org.springframework.security</groupId>
   <artifactId>spring-security-test</artifactId>
   <scope>test</scope>
  </dependency>
  <dependency>
      <groupId>org.springframework.security.oauth</groupId>
      <artifactId>spring-security-oauth2</artifactId>
      <version>2.3.3.RELEASE</version>
  </dependency>
  <dependency>
      <groupId>com.google.code.gson</groupId>
      <artifactId>gson</artifactId>
      <version>2.8.5</version>
  </dependency>
 </dependencies>
```
# Controller

```
import java.io.IOException;
import java.security.Principal;
import java.util.LinkedHashMap;

import org.codehaus.jackson.JsonGenerationException;
import org.codehaus.jackson.map.JsonMappingException;
import org.codehaus.jackson.map.ObjectMapper;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.provider.OAuth2Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

@RestController
public class Controller {

    @GetMapping("/")
    public String helloWorld() {
        return "you don't need to be logged in";
    }

    @GetMapping("/not-restricted")
    public String notRestricted() {
        return "you don't need to be logged in";
    }

    @GetMapping("/restricted")
    public String restricted() {
        return "if you see this you are logged in";
    }
    
    @RequestMapping(value = "/user")
    public Principal user(Principal principal) throws JsonGenerationException, JsonMappingException, IOException {
     System.out.println(principal.toString());
        ObjectMapper mapper = new ObjectMapper();
         String user = mapper.writeValueAsString(principal);
         System.out.println(user);
       return principal;
    }
    
    @RequestMapping(value = "/username", method = RequestMethod.GET)
    @ResponseBody
    public String currentUserName(Authentication authentication) {
        return authentication.toString();
    }
    
}
```
# OAuth2Demo

```
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class OAuth2Demo {

 public static void main(String[] args) {
  SpringApplication.run(OAuth2Demo.class, args);
 }

}
```
# SecurityConfig

```
@Configuration
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    @Override
    public void configure(HttpSecurity http) throws Exception {

        http
                .antMatcher("/**").authorizeRequests()
                .antMatchers(new String[]{"/", "/not-restricted"}).permitAll()
                .anyRequest().authenticated()
                .and()
                .oauth2Login();
    }
}
```
# application.yml

```
spring:
  security:
    oauth2:
      client:
        registration:
          google:
            client-id: 601203258465-sv867t=----
            client-secret: y9NP----
```
# demo

```
http://localhost:8080/#
http://localhost:8080/user
```

![](https://i.imgur.com/1NzZQfz.png)

  

![](https://i.imgur.com/ODwV7eD.png)

  

![](https://i.imgur.com/cuUjra7.png)

這邊就是google回傳給前端可以直接利用的資料了  

![](https://i.imgur.com/3T5SeMx.png)

  

![](https://i.imgur.com/0gK3Zxb.png)
