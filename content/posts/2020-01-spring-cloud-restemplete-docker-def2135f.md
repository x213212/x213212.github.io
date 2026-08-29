---
title: "Spring Cloud 微服務入門 (十二) restemplete 多層服務呼叫 docker - compose 構建 (二)"
date: "2020-01-02T07:00:00.000+08:00"
updated: "2020-01-16T10:59:24.591+08:00"
permalink: "/2020/01/spring-cloud-restemplete-docker.html"
original_url: "https://x8795278.blogspot.com/2020/01/spring-cloud-restemplete-docker.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-447956088382120250"
tags: ["Docker", "rabbitmq", "Spring Cloud", "Tutorial", "zipkin"]
layout: post
---

# 目前架構

![](https://i.imgur.com/RKIxarj.png) 可以看到我們下面 服務好像有固定的數據庫可能是集群或是什麼 在前面的學習好像沒看到更複雜的調用，分布式很多問題，像是數據不同步，光是鎖就有一大堆，就以認證中心設計成微服務的話， 資料庫就會變成多個，這樣就不能判斷你到底是到底在哪一台調用，而出現你有雙重的登入資料緩存在分散的資料庫解決方式可能有 一 分布式鎖 二共用同一個資料庫 這部分先以後有空再弄，目前就是先拓展為多層調用，今天是來實現多層的話服務溝通使用 restemplate 去溝通。

# 分析

# 我們把服務擴展為兩層一下 也就是我們要關注的 ![](https://i.imgur.com/MQSS36D.png) 好吧開始 目前我們的 service 已經有 5個 我們要來 新增了 2 個 也就是模擬第四層 一個是 EurekaServiceFeignConsumer2 EurekaServiceFeignProvider3 其中兩個各別都是從 也就是模擬第三層 EurekaServiceFeignProvider EurekaServiceFeignConsumer 複製出來 來看一下代碼 那麼我們原本的服務會變怎樣呢 EurekaServiceFeignProvider1 EurekaServiceFeignProvider2 要調用我們的 EurekaServiceFeignProvider3 所以調用順序就是 Zuul - > Consumer1 - > Provider1 or Provider2 -> Consumer2 > Provider3 所以先針對我們的 Consumer1 來修改

# 多層服務的呼叫方式

# 調用服務三 但是要取得服務四 的 response 才算調用完成 那就變成 要完成server3 呼叫就要 server3 -> server 4 多經過一層 server 4 這樣的話 可能會覺得我那就用我們上次 doget doposs 這兩種方法就好了那有沒有更優雅的方式呢有的歐， spring 幫我們把這些東西再往上封裝了一層也就是 restemplate (如果你想用到更複雜的調用你就自己從底層慢慢研究了)

# Consumer1 Controller

# 我們新增了 ``` @GetMapping("/helloEX/{id}/{id2}") public String helloEX(@PathVariable(name="id") Integer employeeId,@PathVariable(name="id2") Integer employeeId2) { System.out.print(employeeId2); String message = homeClient.home2(employeeId,employeeId2); logger.info("[eureka-fegin][ConsumerController][hello], message={}", message); // log.info("[eureka-ribbon][EurekaRibbonConntroller][syaHello], message={}", message); return message ; ``` 好了之後 我們要看要調用哪一層就是我們的

# Consumer1 homeClient

# ``` @GetMapping("/ep1") public String home2(@RequestParam (value="id", required = false) Integer employeeId,@RequestParam (value="id2", required = false) Integer employeeId2) ; ```

# Provider 1 or 2

# 這邊就要稍微用到前面的技巧了 我們知道有 resttemplete 有可以去跟我們 Eureka 去要我們已經註冊的節點的伺服器名字 整體調用在最下面 <https://openhome.cc/Gossip/Spring/RestTemplate.html> <https://www.jianshu.com/p/462790156554> 我們用到比較關鍵的是 預設的 restemplete 是沒有辦法呼叫負載平衡的，有印象的話在前幾天用過 [SPRING CLOUD 微服務入門 (三) EUREKA + CONSUMER (FEIGN) 調用 SERVICE](https://x8795278.blogspot.com/2019/12/spring-cloud-eureka-consumer-feign.html) 在這邊的話我們把 restemplete 注入一個有 loadblance 特性 <https://blog.csdn.net/qq_18416057/article/details/79432504> 這邊說的蠻清楚的 不過少了一些東西 ``` @LoadBalanced @Bean RestTemplate restTemplate() { return new RestTemplate(); } @Autowired private RestTemplate restTemplate; ``` 總而言之就是讓我們的 restemplete有可以 去 訪問 Eureka 的能力

# 配置 provider

# application.yml ``` eureka: client: serviceUrl: defaultZone: http://localhost:8761/eureka/ register-with-eureka : true <====就是這行 讓我們的 的 服務可以去請求其他已經註冊的伺服器 ``` 那麼現在我們的 restemplete loadblance 特性

# 細看 Provider

# 這邊要注意要跟我們的 Consumer1 homeClient 裡面的 method 相對應，這邊可以看到我們對伺服器的 ip已經不是像我們之前的在寫註冊中心那樣直接doget dopost 去呼叫，restemplete ,當然也可以用這種方式去呼叫我們的註冊中心，只不過，有空再寫好了這邊做兩個範例。 ``` @GetMapping("/ep1") public String home2(@RequestParam (value="id", required = false) final Integer employeeId,@RequestParam (value="id2", required = false) final Integer employeeId2) { final String message = "Hello world" + port+ employeeId+employeeId2; logger.info("[eureka-provide][EurekaServiceProviderApplication][home], message={}", message); // restTemplate = new RestTemplate(); final String fooResourceUrl = "http://feign-consumer2"; final ResponseEntity<String> response = restTemplate.getForEntity( fooResourceUrl + "/hello2/" + employeeId.toString() + "/" + employeeId2.toString(), String.class); //assertThat(response.getStatusCode(), equalTo(HttpStatus.OK)); System.out.println(response.getStatusCode().toString()+(HttpStatus.OK).toString()); System.out.println(response.getBody()+"test"); return response.getBody(); } ``` 好了之後複製到 Provider2 兩個 Controller 一樣。

# Provider3 Controller

# 反正 他是複製 Provider 我們直接看源碼 這邊很簡單沒做什麼我們看 Consumer2 ``` @GetMapping("/ep2") public String home(@RequestParam (value="id", required = false) Integer employeeId,@RequestParam (value="id2", required = false) Integer employeeId2) { String message = "Hello world" + port+ employeeId+employeeId2; logger.info("[eureka-provide2][EurekaServiceProviderApplication][home], message={}", message); return message; } ```

# Provider 3 配置文件

# 記得換為 eureka-provider2，以便讓我們的 Consumer2 可以調用到 ``` name: eureka-provider2 ```

# Consumer2 Controller

# 注意看 Url這邊可以看到 我們沒有再讓往Zuul 去訪問我們的 consumer2 了 因為我們是讓 Provider 去直接 調用 我們的 consumer2 , 可以注意 url 的調用 address 裡面的 hello2 ``` @RestController public class ConsumerController { private final Logger logger = LoggerFactory.getLogger(ConsumerController.class); @Autowired private HomeClient homeClient; @GetMapping("/hello2/{id}/{id2}") public String hello(@PathVariable(name="id") Integer employeeId,@PathVariable(name="id2") Integer employeeId2) { System.out.print(employeeId2); String message = homeClient.home(employeeId,employeeId2); logger.info("[eureka-fegin2][ConsumerController][hello], message={}", message); // log.info("[eureka-ribbon][EurekaRibbonConntroller][syaHello], message={}", message); return message ; } } ```

# Consumer2 homeClient

# 可以注意我們的 這邊就是填 Provider3 註冊到 Eureka的名字 也就是 eureka-provider2 ``` @FeignClient(value ="eureka-provider2",fallbackFactory=HystrixClientFallbackFactory.class) public interface HomeClient { @GetMapping("/ep2") public String home(@RequestParam (value="id", required = false) Integer employeeId,@RequestParam (value="id2", required = false) Integer employeeId2) ; } ``` 好了都沒問題的話 就 啟動 吧!

# 啟動

# 前面步驟就不說了 ![](https://i.imgur.com/dm2GHVg.png) 可以看到我訪問的是 helloEx ``` http://localhost:9000/feign-consumer/helloEX/1/12?token=Bearer%20eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1Nzc5MTUxNTksInVzZXJuYW1lIjoiamFjayJ9.UMUZWzh_ZTkhKxoSBfglSualToOTn9dm-WE9D3_huT4 ``` 這邊會覺得，有沒有更視覺化的東西可以看阿 別忘了我們的 Zipkin 就是在做這些事，我們打開 花了點時間 我把 zipkin 弄進去 docker-compose了，請注意 zipkin 啟動順序有差 ``` version: '2' services: elasticsearch: build: context: elasticsearch/ volumes: - ./elasticsearch/config/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml:ro ports: - "9200:9200" - "9300:9300" environment: ES_JAVA_OPTS: "-Xmx256m -Xms256m" networks: - elk logstash: build: context: logstash/ volumes: - ./logstash/config/logstash.yml:/usr/share/logstash/config/logstash.yml:ro - ./logstash/pipeline:/usr/share/logstash/pipeline:ro ports: - "5000:5000" environment: LS_JAVA_OPTS: "-Xmx256m -Xms256m" networks: - elk depends_on: - elasticsearch kibana: build: context: kibana/ volumes: - ./kibana/config/:/usr/share/kibana/config:ro ports: - "5601:5601" networks: - elk depends_on: - elasticsearch rabbitmq : build: context: rabbitmq / volumes: - ./rabbitmq/config/:/usr/share/rabbitmq/config:ro ports: - "5672:5672" - "15672:15672" networks: - elk depends_on: - elasticsearch zipkin: build: context: zipkin / volumes: - ./zipkin/config/:/usr/share/zipkin/config:ro # Environment settings are defined here https://github.com/openzipkin/zipkin/tree/1.19.0/zipkin-server#environment-variables environment: - RABBIT_ADDRESSES=192.168.99.100:5672 - RABBIT_USER=guest - RABBIT_PASSWORD=guest - RABBIT_QUEUE=zipkin - SELF_TRACING_ENABLED=false #- RABBIT_VIRTUAL_HOST=/admin_host - JAVA_OPTS=-Dlogging.level.zipkin #=DEBUG -Dlogging.level.zipkin2=DEBUG ports: # Port used for the Zipkin UI and HTTP Api - "9411:9411" # Uncomment if you set SCRIBE_ENABLED=true # - 9410:9410 networks: - elk depends_on: - elasticsearch networks: elk: driver: bridge ``` 應該每次初次啟動 zipkin都會找不到 rabbitmq 而退出 ``` docker start "zipkin name" ``` ![](https://i.imgur.com/937NaX4.png) 服務啟動 ![](https://i.imgur.com/DRqjfjS.png) ![](https://i.imgur.com/iARveAz.png) 好了之後 我們的追蹤鏈也很清楚 ![](https://i.imgur.com/4TdzDv6.png)
