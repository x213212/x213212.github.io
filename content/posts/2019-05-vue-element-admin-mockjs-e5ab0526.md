---
title: "Vue element admin 自定義 後端 (二)"
date: "2019-05-31T16:11:00.004+08:00"
updated: "2019-06-22T20:02:34.176+08:00"
permalink: "/2019/05/vue-element-admin-mockjs.html"
original_url: "https://x8795278.blogspot.com/2019/05/vue-element-admin-mockjs.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-9041533968414357784"
tags: ["spring boot", "Tutorial", "Vue.js"]
layout: post
---

[![](https://i.imgur.com/MhGYVU1.png)](https://i.imgur.com/MhGYVU1.png)
#

# vue element admin mock.js 換為spring boot

spring boot 首先必須熟悉一下json格式  

<https://segmentfault.com/a/1190000017372916>  

這邊可以返回簡單範例， 下一章將針對 table 進行深入探討.....。
```
{"id":1,"age":18,"user-name":"Java技术栈"}
```
我們可以運行 vue element admin 進行 觀察  

在目錄底下
```
src/api/user.js
```
這個檔案裡  

![](https://i.imgur.com/XFsj6OS.png)

我們要把官方的 mock.js 原封不動 的 轉換為自訂 後段 spring boot
mock.js 就是一種 在 後端 method 還沒完成的時候，前端可以自行模擬後端 產生資料  

所以在開發的時候，相當方便。  

怎麼做呢? 來看一下 原生 dev 環境 運行畫面。
按下 login  

![](https://i.imgur.com/fxB0Fmh.png)

![](https://i.imgur.com/XrhaJyF.png)

  

可以看到 login這個地方產生了 json 也就是 token 看是否給予權限?  

這邊可以看到 伺服器預設返回為
```
admin-token
```
那麼 我們來追一下程式碼
在 path
```
src/store/modules/user.js
```
可以看到這邊是 login 呼叫事件並且產生cookies  

![](https://i.imgur.com/W89gm9U.png)

  

我們來看一下 settoken是否為cookies  

對的沒錯  

![](https://i.imgur.com/m4Mit0F.png)

那我們只要村造他的規則，基本上 只要 改
```
src/api/user.js
```
就可以進行無痛從 mock.js 改為 其他 後端restful，只要 符合他的規則  

(當然後面比較熟悉一點可以對她進行更深入的改動。
那我們可以看到  

![](https://i.imgur.com/PUyrgI0.png)

在這邊的話  

![](https://i.imgur.com/K5Y4kD1.png)

  

我們更動為
```
return request({
    url: 'http://localhost:9990/httpMethod',
    method: 'post',
    data: {
      name: data.username,
      pwd: data.password
    }
  })
```
在這個部分的話，我傳了 使用者id，與 password 給伺服器，伺服器在 根據 所分配的權限 給予前端再來根據權限來決定畫面如何呈現。

---

url的部分 我們更改為 我們自己後端， 這邊需要 根據 自行選用後端進行相關 設定與配置  

例如我們上一章，所說的 跨網域 等等，相關設定。
這邊我們來看 spring boot 如何設定
```
@ComponentScan(basePackages = {"com.demo.controller"}) 

@Controller

@RestController
@RequestMapping("/")
@EnableAutoConfiguration
@CrossOrigin(origins = "http://172.16.7.21:9527", maxAge = 3600)
public class DemoApplication {

// //    跨網域
   @Bean
     public WebMvcConfigurer corsConfigurer() {
         return new WebMvcConfigurer() {
             @Override
             public void addCorsMappings(CorsRegistry registry) {
                 registry.addMapping("/httpMethod/**")
                         .allowedOrigins("http://localhost:9528");//允许域名访问，如果*，代表所有域名
                 //.allowedOrigins("http://localhost:9527");//允许域名访问，如果*，代表所有域名
                 registry.addMapping("/httpMethod2/**")
                    .allowedOrigins("http://localhost:9527");//允许域名访问，如果*，代表所有域名
             }
         };
     }

 Login memberAccount;
 @CrossOrigin
 @PostMapping(value = "/httpMethod", produces = "application/json")
 @ResponseBody
 public Login  httpMethod(@RequestBody Map<String, Object> params) throws JsonProcessingException{
 System.out.println("sent name is "+  params.get("name").toString());
 System.out.println("sent pwd is "+  params.get("pwd").toString());
 if( params.get("name").equals("admin")   &&  params.get("pwd").equals("111111" ) ) {
  Login memberAccount = new Login();
     
  memberAccount.setCode(20000);
  Token test = new Token();
  memberAccount.setData(test);
  ObjectMapper objectMapper = new ObjectMapper();
 
  String userJsonStr = objectMapper.writeValueAsString(memberAccount);
  System.out.print(userJsonStr);
  return memberAccount;
 }
 return memberAccount;
 }

 @CrossOrigin
    @GetMapping("/httpMethod2")
 @ResponseBody
 public String httpMethod2(){
 System.out.println("sent name is ");
 System.out.println("sent pwd is ");
 return "success";
 }

}
```
# Json 與 CORS 跨網域 紀錄

![](https://i.imgur.com/EDDOugD.png)

  

![](https://i.imgur.com/jmIDRra.png)

  

![](https://i.imgur.com/pBQC17k.png)

這邊稍微紀錄 如何使用 跨網域 和 jackson java  

在 spring boot 所以用的 json 好像是 fastjson 他好像跟jackson 差不多  

<https://segmentfault.com/a/1190000005717319>  

來介紹一下 如後 透過 java class to json 很簡單，  

只要
```
Login memberAccount = new Login();
memberAccount.setCode(20000);
Token test = new Token();
memberAccount.setData(test);
    
    
    ///這邊是我 自己看能不能把 java 轉成 字串測試
    ObjectMapper objectMapper = new ObjectMapper();
String userJsonStr = objectMapper.writeValueAsString(memberAccount);
System.out.print(userJsonStr);
            
//到了 return 前端所接收到的就是一個 json 格式的字串了
return memberAccount;
```
後端 restful 好了之後 可以發現，已經可以移植成功!  

![](https://i.imgur.com/yp5wY0n.png)

後面會有詳細的git…
**`DemoApplication.java`**

```java
package com.demo;

import org.springframework.boot.SpringApplication;
import com.demo.*;

import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.web.servlet.ServletComponentScan;

import static org.junit.Assert.assertEquals;

import java.util.Arrays;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;

import org.apache.catalina.filters.CorsFilter;
import org.omg.CORBA.Environment;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.servlet.ModelAndView;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurerAdapter;

import com.demo.controller.HelloController;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.model.Dome;
import com.model.Dome2;
import com.model.Login;
import com.model.Shop;
import com.model.Token;


@ComponentScan(basePackages = {"com.demo.controller"}) 

@Controller

@RestController
@RequestMapping("/")
@EnableAutoConfiguration
@CrossOrigin(origins = "http://172.16.7.21:9527", maxAge = 3600)
public class DemoApplication {
//	  @RequestMapping("/test/{test}")
//	  @ResponseBody
//	    public String sayHello(@PathVariable("test") String test) {
//		   System.out.print("test");
//	        return   new HelloController().sayHello("hello");
//	    }

	  @RequestMapping(value = "/hello", method = RequestMethod.GET)
	  public ModelAndView hello(Map<String,Object> map){
	  map.put("key","value");
	  ModelAndView modelAndView = new ModelAndView();
	  modelAndView.setViewName("web");
	  modelAndView.addObject(map);
	  return modelAndView;
	  }
	  
	public static void main(String[] args) throws Exception  {
		SpringApplication.run(DemoApplication.class, args);
	
	}

	@RequestMapping("/add")
	public String addSession(HttpServletRequest httpServletRequest,
							@RequestParam("username")String username) {
		HttpSession session = httpServletRequest.getSession();
		session.setAttribute("username",username);
		session.setMaxInactiveInterval(10000);
		return "添加成功";
	}
	
	@RequestMapping("/show")
	// 跨網域
	public Object showSession(HttpServletRequest httpServletRequest) {
		HttpSession session = httpServletRequest.getSession();
		Object object = session.getAttribute("username");
		return object;
	}
//
//		@Configuration
//	   private CorsConfiguration buildConfig() {
//	        CorsConfiguration corsConfiguration = new CorsConfiguration();
//	        corsConfiguration.addAllowedOrigin("*"); // 1
//	        corsConfiguration.addAllowedHeader("*"); // 2
//	        corsConfiguration.addAllowedMethod("*"); // 3
//	        return corsConfiguration;
//	    }
//	 
//	    @Bean
//	    public CorsFilter corsFilter() {
//	        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
//	        source.registerCorsConfiguration("/**", buildConfig()); // 4
//	        return new CorsFilter();
//	    }
//	//    跨網域
	  @Bean
	    public WebMvcConfigurer corsConfigurer() {
	        return new WebMvcConfigurer() {
	            @Override
	            public void addCorsMappings(CorsRegistry registry) {
	                registry.addMapping("/httpMethod/**")
	                        .allowedOrigins("http://localhost:9528");//允许域名访问，如果*，代表所有域名
	                //.allowedOrigins("http://localhost:9527");//允许域名访问，如果*，代表所有域名
	                registry.addMapping("/httpMethod2/**")
                    .allowedOrigins("http://localhost:9527");//允许域名访问，如果*，代表所有域名
	            }
	        };
	    }


	Login memberAccount;
	@CrossOrigin
	@PostMapping(value = "/httpMethod", produces = "application/json")
	@ResponseBody
	public Login  httpMethod(@RequestBody Map<String, Object> params) throws JsonProcessingException{
	System.out.println("sent name is "+  params.get("name").toString());
	System.out.println("sent pwd is "+  params.get("pwd").toString());
	if( params.get("name").equals("admin")   &&  params.get("pwd").equals("111111" ) ) {
		Login memberAccount = new Login();
	    
		memberAccount.setCode(20000);
		Token test = new Token();
		memberAccount.setData(test);
		ObjectMapper objectMapper = new ObjectMapper();
	
		String userJsonStr = objectMapper.writeValueAsString(memberAccount);
		System.out.print(userJsonStr);
		return memberAccount;
	}
	return memberAccount;
	}

	@CrossOrigin
    @GetMapping("/httpMethod2")
	@ResponseBody
	public String httpMethod2(){
	System.out.println("sent name is ");
	System.out.println("sent pwd is ");
	return "success";
	}
	
//	@CrossOrigin
//	@RequestMapping(value = "/httpMethod")
//	@ResponseBody
//	public Shop httpMethod(){
////	System.out.println("sent name is "+  params.get("name").toString());
////	System.out.println("sent pwd is "+  params.get("pwd").toString());
////
////	  
//	  Shop memberAccount = new Shop();
//	  
////	if( params.get("name").equals("admin")   &&  params.get("pwd").equals("111111" ) ) {
////		
//		memberAccount.set_name( "test");
//		memberAccount.set_pwd ("test2");
//		
//		return memberAccount;
//		}
////	}
////	return memberAccount;
////	}
}
```

**`Login.java`**

```java
package com.model;

import java.awt.print.Book;

public class Login {

    private Integer code;
    private Token data;

    public Login(){

    }

    public Login(Integer code, String data,String name,String[] tmp) {
        super();
        this.code = code;

    }

    public Integer getCode() {
        return code;
    }

    public void setCode(Integer code) {
        this.code = code;
    }

 
	public Token getData() {
		return data;
	}
	public void setData(Token data) {
		this.data = data;
	}
}
```

**`Token.java`**

```java
package com.model;

public class Token {
	
    private String token="admin-token";

    
//	private List<Author> author = new ArrayList<Author>();

    public void settoken (String token){
    	this.token = token;
    }
    public String gettoken(){
    	return  token;
    }

	
    public Token(){

    }


	
//	public List<Author> getAuthor() {
//		return author;
//	}
//	public void setAuthor(List<Author> author) {
//		this.author = author;
//	}

}
```
