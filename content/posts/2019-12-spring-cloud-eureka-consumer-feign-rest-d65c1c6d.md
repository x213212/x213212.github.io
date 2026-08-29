---
title: "Spring Cloud 微服務入門 (四) Eureka + Consumer (Feign) Rest 傳遞參數"
date: "2019-12-26T10:39:00.001+08:00"
updated: "2020-01-16T10:59:24.757+08:00"
permalink: "/2019/12/spring-cloud-eureka-consumer-feign-rest.html"
original_url: "https://x8795278.blogspot.com/2019/12/spring-cloud-eureka-consumer-feign-rest.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8508576158879908974"
tags: ["feign", "Spring Cloud", "Tutorial"]
layout: post
---

![](https://i.imgur.com/PrtpDca.png) feign 如何調用 service 且傳入參數

比較常見就是這兩種  

@GetMapping  

@PostMapping  

這兩種又有  

@RequestMappin  

此文章沒討論用這個@RequestMapping 這算是比較舊的寫法，或許後續有空會補上
通常我們呼叫 restAPi可以用  

@GetMapping  

@PostMapping  

那麼又有分

- 無參數
- 單參數
- 多個參數
- 複雜對象

# 單參數

無參數就不多加實作了主要針對有參數的
## Provider Controller

```
@SpringBootApplication
@EnableEurekaClient
@RestController
public class EurekaServiceProviderApplication {
 
 @Value("${server.port}")
     String port;
  @GetMapping("/")
 public String home(@RequestParam (value="id", required = false) Integer employeeId) {
       return "Hello world" + port+ employeeId;
 }
 public static void main(String[] args) {
  SpringApplication.run(EurekaServiceProviderApplication.class, args);
 }

}
```
## Consumer 接口

```
@FeignClient("eureka-provider")
public interface HomeClient {
  @GetMapping("/")
  public String home(@RequestParam (value="id", required = false) Integer employeeId) ;
}
```
## Consumer Controller

```
@RestController
public class ConsumerController {
  @Autowired
     private HomeClient homeClient;

 
   @GetMapping("/hello/{id}")
     public String hello(@PathVariable(name="id") Integer employeeId) {
      System.out.print(employeeId);
         return homeClient.home(employeeId);
     }
}
```
# 多參數

## Provider Controller

```
@SpringBootApplication
@EnableEurekaClient
@RestController
public class EurekaServiceProviderApplication {
 
 @Value("${server.port}")
     String port;
  @GetMapping("/")
  public String home(@RequestParam (value="id", required = false) Integer employeeId,@RequestParam (value="id2", required = false) Integer employeeId2)  {
       return "Hello world" + port+ employeeId+employeeId2;
 }
 public static void main(String[] args) {
  SpringApplication.run(EurekaServiceProviderApplication.class, args);
 }

}
```
## Consumer 接口

```
@FeignClient("eureka-provider")
public interface HomeClient {
  @GetMapping("/")
  public String home(@RequestParam (value="id", required = false) Integer employeeId,@RequestParam (value="id2", required = false) Integer employeeId2) ;
}
```
## Consumer Controller

```
@RestController
public class ConsumerController {
  @Autowired
     private HomeClient homeClient;

 
   @GetMapping("/hello/{id}/{id2}")
     public String hello(@PathVariable(name="id") Integer employeeId,@PathVariable(name="id2") Integer employeeId2) {
      System.out.print(employeeId2);
         return homeClient.home(employeeId,employeeId2);
     }
}
```
詳細可以參考  

[SpringBoot 中常用注解@PathVaribale/@RequestParam/@GetMapping介绍](https://blog.csdn.net/u010412719/article/details/69788227)
<http://www.itmuch.com/spring-cloud-sum/feign-multiple-params/>
# 複雜對象

構建一個 entity  

UserEntity.class  

這邊好像在一個網站有看過這邊大小寫 windows 沒有限制，在linux 就嚴格 限制 大小寫，後面會來好好講解，  

然後這個 Entity 同時在 Provider 和 Consumer 裡。
```
public class UserEntity {
 
 private Integer id;

 private String Name ;

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
## Provider

```
public class UserEntity {
 
 private Integer id;

 private String Name ;

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
## Consumer 接口

```
@FeignClient("eureka-provider")
public interface HomeClient {
  @GetMapping("/")
  public String home(@RequestParam (value="id", required = false) Integer employeeId,@RequestParam (value="id2", required = false) Integer employeeId2) ;
  @PostMapping("/user")
  public String aveUser(@RequestBody UserEntity user);
}
```
## Consumer Controller

```
@RestController
public class ConsumerController {
  @Autowired
     private HomeClient homeClient;

 
   @GetMapping("/hello/{id}/{id2}")
     public String hello(@PathVariable(name="id") Integer employeeId,@PathVariable(name="id2") Integer employeeId2) {
      System.out.print(employeeId2);
         return homeClient.home(employeeId,employeeId2);
     }
   
  @PostMapping("/user")
   public String aveUser(@RequestBody UserEntity user) {
    return homeClient.aveUser(user);
  }

}
```
# 運行並測試

注意大小寫  

![](https://i.imgur.com/8j1cQGg.png)

  

![](https://i.imgur.com/KramyhN.png)

![](https://i.imgur.com/l55Fkhf.png)

  

![](https://i.imgur.com/ytAl9d7.png)

大概變化就這幾種  

接下來就輪到介紹我們的 Hystrix 斷路器。
