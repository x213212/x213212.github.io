---
title: "Spring Cloud 微服務入門 (五) Hystrix + Ribbon + feign 斷路器示範"
date: "2019-12-26T17:05:00.002+08:00"
updated: "2020-01-16T10:59:24.502+08:00"
permalink: "/2019/12/spring-cloud-hystrix-ribbon-feign.html"
original_url: "https://x8795278.blogspot.com/2019/12/spring-cloud-hystrix-ribbon-feign.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2001947793011751754"
tags: ["Hystrix", "Spring Cloud", "Tutorial"]
layout: post
---

![](https://i.imgur.com/rkLQudg.png)

  

在上次講了  

- Eureka + Consumer (Rest+Ribbon)
- Eureka + Consumer Feign

現在要為它們加上 斷路器  

![](https://i.imgur.com/7x28fyg.png)

# Hystrix 介紹

在微服務架構中，根據業務來拆分成一個個的服務，服務與服務之間可以相互調用（RPC），在Spring Cloud可以用RestTemplate+Ribbon和Feign來調用。為了保證其高可用，單個服務通常會集群部署。由於網絡原因或者自身的原因，服務並不能保證100%可用，如果單個服務出現問題，調用這個服務就會出現線程阻塞，此時若有大量的請求湧入，Servlet容器的線程資源會被消耗完畢，導致服務癱瘓。服務與服務之間的依賴性，故障會傳播，會對整個微服務系統造成災難性的嚴重後果，這就是服務故障的“雪崩”效應。
針對上述問題，在Spring Cloud Hystrix中實現了線程隔離、斷路器等一系列的服務保護功能。它也是基於Netflix的開源框架 Hystrix實現的，該框架目標在於通過控制那些訪問遠程系統、服務和第三方庫的節點，從而對延遲和故障提供更強大的容錯能力。 Hystrix具備了服務降級、服務熔斷、線程隔離、請求緩存、請求合併以及服務監控等強大功能。
# 什麼是斷路器

斷路器模式源於Martin Fowler的Circuit Breaker一文。 “斷路器”本身是一種開關裝置，用於在電路上保護線路過載，當線路中有電器發生短路時，“斷路器”能夠及時的切斷故障電路，防止發生過載、發熱、甚至起火等嚴重後果。
在分佈式架構中，斷路器模式的作用也是類似的，當某個服務單元發生故障（類似用電器發生短路）之後，通過斷路器的故障監控（類似熔斷保險絲），向調用方返回一個錯誤響應，而不是長時間的等待。這樣就不會使得線程因調用故障服務被長時間佔用不釋放，避免了故障在分佈式系統中的蔓延。
# 斷路器示意圖

SpringCloud Netflix實現了斷路器庫的名字叫Hystrix. 在微服務架構下，通常會有多個層次的服務調用. 下面是微服架構下, 瀏覽器端通過API訪問後台微服務的一個示意圖：  

![](https://i.imgur.com/Z7ZAMyL.png)

一個微服務的超時失敗可能導致瀑布式連鎖反映，下圖中，Hystrix通過自主反饋實現的斷路器， 防止了這種情況發生。  

![](https://i.imgur.com/FaNeSSy.png)

圖中的服務B因為某些原因失敗，變得不可用，所有對服務B的調用都會超時。當對B的調用失敗達到一個特定的閥值(5秒之內發生20次失敗是Hystrix定義的缺省值), 鏈路就會被處於open狀態， 之後所有所有對服務B的調用都不會被執行， 取而代之的是由斷路器提供的一個表示鏈路open的Fallback消息. Hystrix提供了相應機制，可以讓開發者定義這個Fallbak消息.
open的鏈路阻斷了瀑布式錯誤， 可以讓被淹沒或者錯誤的服務有時間進行修復。這個fallback可以是另外一個Hystrix保護的調用, 靜態數據，或者合法的空值. Fallbacks可以組成鍊式結構，所以，最底層調用其它業務服務的第一個Fallback返回靜態數據.
# 添加依賴

之前好像除了用 從pom.xml加Hystrix 好像沒有交其他地方引入，很早我加 pom.xml 就失效了不知道為什麼所以我用這種方式加。  

![](https://i.imgur.com/BN9eU9u.png)

  

![](https://i.imgur.com/0ZSlZji.png)

# Ribbon Hystrix

進入正題
# 添加Hystrix註解

EurekaServiceRibbonConsumer.class
```
@SpringBootApplication
@EnableDiscoveryClient
@EnableHystrix
public class EurekaServiceRibbonConsumer {
 
 @LoadBalanced
 @Bean
 RestTemplate restTemplate() {
        return new RestTemplate();
 }
 public static void main(String[] args) {
  SpringApplication.run(EurekaServiceRibbonConsumer.class, args);
 }

}
```
# Consumer Consumer

修改 ConsumerController 類的，hello 方法，加上註解@HystrixCommand(fallbackMethod = “defaultStores”) 該註解對該方法創建了熔斷器的功能  

,並指定了defaultStores熔斷方法，熔斷方法直接返回了一個String， “feign + hystrix ,Service die”
@HystrixCommand 表明該方法為hystrix包裹，可以對依賴服務進行隔離、降級、快速失敗、快速重試等等hystrix相關功能  

該註解屬性較多，下面講解其中幾個

- fallbackMethod 降級方法
- commandProperties 普通配置屬性，可以配置HystrixCommand對應屬性，例如採用線程池還是信號量隔離、熔斷器熔斷規則等等
- ignoreExceptions 忽略的異常，默認HystrixBadRequestException不計入失敗
- groupKey() 組名稱，默認使用類名稱
- commandKey 命令名稱，默認使用方法名

```
@RestController
public class ConsumerController {
     @Autowired
     private RestTemplate restTemplate;

     @HystrixCommand(fallbackMethod = "defaultStores")
     @GetMapping(value = "/test")
     public String test() {
     
         return restTemplate.getForEntity("http://eureka-provider/test", String.class).getBody();
     }
     public String defaultStores() {
         return "Ribbon + hystrix ,Service die";
     }
}
```
# Provider

```
@SpringBootApplication
@EnableEurekaClient
@RestController
public class EurekaServiceProviderApplication {
 
  @Value("${server.port}")
  String port;

  @RequestMapping("/test")
  public String test() {
       return "Hello world ,port:" + port;
  }
 public static void main(String[] args) {
  SpringApplication.run(EurekaServiceProviderApplication.class, args);
 }

}
```
# 運行一下

檢查Eureka註冊中心  

![](https://i.imgur.com/scAgDXV.png)

  

![](https://i.imgur.com/8pya2k9.png)

  

![](https://i.imgur.com/hAg75xa.png)

  

選擇關一個 Provider 或者 兩個全關  

![](https://i.imgur.com/WNjILPX.png)

  

不會像以前當掉那樣轉圈圈，可以依造自己的策略去做其他動作，  

接下來示範 fegin +Hystrix。
# feign Hystrix

他裡面已經內建 Hystrix  

所以我們去配置中心改一下  

application.yml
```
eureka:
  client:
    serviceUrl:
      defaultZone: http://localhost:8761/eureka/

spring:
  application:
    name: feign-consumer

feign:
  hystrix:
    enabled: true
    
server:
  port: 9000
```
# 開啟@EnableHystrix

```
@SpringBootApplication
@EnableDiscoveryClient
@EnableFeignClients
@EnableHystrix
public class EurekaServiceFeignConsumer {
 

 public static void main(String[] args) {
  SpringApplication.run(EurekaServiceFeignConsumer.class, args);
 }

}
```
# 修改接口

主要是在@FeignClient後面補上 fallbackFactory
```
@FeignClient(value ="eureka-provider",fallbackFactory=HystrixClientFallbackFactory.class)
public interface HomeClient {
  @GetMapping("/")
  public String home(@RequestParam (value="id", required = false) Integer employeeId,@RequestParam (value="id2", required = false) Integer employeeId2) ;
  @PostMapping("/user")
  public String aveUser(@RequestBody UserEntity user);
}
```
# ConsumerController

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
# 新增 FallBackFactory

這邊可以看你發生錯誤後再進行什麼處理  

詳細請參考  

<https://juejin.im/entry/5b20a2c25188257d6c047d2d>
```
@Component

public class HystrixClientFallbackFactory implements FallbackFactory<HomeClient> {

    @Override
    public HomeClient create(Throwable throwable) {
      String ERROR_MSG ="error:";
      String msg = throwable == null ? "" : throwable.getMessage();
         if (!StringUtils.isEmpty(msg)) {
             System.out.print(msg);
         }
         return new HomeClient() {

   @Override
   public String home(Integer employeeId, Integer employeeId2) {
    // TODO Auto-generated method stub
    
    return (ERROR_MSG+msg);
   }

   @Override
   public String aveUser(UserEntity user) {
    // TODO Auto-generated method stub
    return  (ERROR_MSG+msg);
   }
         };
    }
}
```
# 啟動

![](https://i.imgur.com/kMSM5wJ.png)

  

![](https://i.imgur.com/3qeTln7.png)

  

![](https://i.imgur.com/r31QA43.png)

  

兩個服務中止  

![](https://i.imgur.com/tZIRa9R.png)

  

  

  

接下來就是Zuul 閘道 介紹了 !  

  

參考:<https://www.ymq.io/2017/12/07/spring-cloud-hystrix-dashboard/>
