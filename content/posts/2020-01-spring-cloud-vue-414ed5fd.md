---
title: "區塊鏈 初探 (三) 結合Spring Cloud Vue 完成一個 簡單交易功能"
date: "2020-01-05T19:12:00.000+08:00"
updated: "2020-02-18T04:03:37.424+08:00"
permalink: "/2020/01/spring-cloud-vue.html"
original_url: "https://x8795278.blogspot.com/2020/01/spring-cloud-vue.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5851781334238105808"
tags: ["geth", "Spring Cloud", "Tutorial", "Vue.js"]
layout: post
---

# 基本交易

![](https://i.imgur.com/Xy8ueyo.png)

  

基本上就是跟我們的上次看到的合約差不多  

![](https://i.imgur.com/F6TNrrx.png)

  

算是仿造一個吧
花了一點時間寫了個最基本的交易demo
vue.js  

spring cloud  

geth
這邊可以看到
# 編寫智能合約

這邊可以看到 我們在 一開始建構元的時候 給了自己1000元，也就是最先一開始發布合約的人，再來就是簡單的 transfer 可以指定對方帳戶進行轉入
```
pragma solidity 0.4.25;

contract Token {
    uint INITIAL_SUPPLY = 10000;
    mapping(address => uint) public balances;
    //mapping (address => uint) public balances;
    mapping(string => uint) balanceByName;
    event setBalanceEvent(string name,uint balance);
    
    function setBalance(string  memory _name, uint _balance) public {
        balanceByName[_name] = _balance;
        emit setBalanceEvent(_name,_balance);
    }
    function returnBalance (string memory _name)  public view returns (uint){
        return balanceByName[_name];
    }

    
    function Token() public {
        balances[msg.sender] = 1000;
    }
  
      // transfer token for a specified address
    function transfer(address _to, uint _amount) public {
        require(balances[msg.sender] > _amount);
        balances[msg.sender] -= _amount;
        balances[_to] += _amount;
    }
    
      // Gets the balance of the specified address
    function balanceOf(address _owner) public constant returns (uint) {
        return balances[_owner];
    }
}
```

![](https://i.imgur.com/BkCco6s.png)

# spring cloud

這邊又是承接我們上次的教學，順便順一次坑
# 配置文件

可以看到重試機制那邊，當我們進行呼叫 method的時候，我們的fegin內建的負載平衡裡面有重試機制，這邊是因為我在交易的時候發生重複扣款，最後在這邊設置參數就ok了
```
eureka:
  client:
    serviceUrl:
      defaultZone: http://localhost:8761/eureka/

spring:
  application:
    name: feign-consumer
  zipkin:
    base-url:  http://192.168.0.146:9411
    sender:
      type: rabbit
    rabbitmq:
      addresses: 192.168.99.100:5672
      password: guest
      username: guest
      queue: zipkin
feign:
  hystrix:
    enabled: true
ribbon:
  # 同一实例最大重试次数，不包括首次调用。默认值为0
  MaxAutoRetries: 0
  # 同一个微服务其他实例的最大重试次数，不包括第一次调用的实例。默认值为1
  MaxAutoRetriesNextServer: 0
  # 是否所有操作（GET、POST等）都允许重试。默认值为false
  OkToRetryOnAllOperations: false

server:
  port: 9001
```
# consumer

```
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import javax.ws.rs.core.Response;

import com.example.demo.entity.UserEntity;
import com.example.demo.entity.UserEntityEx;
import org.springframework.web.bind.annotation.ResponseStatus;

import org.springframework.http.HttpStatus;
@RestController

public class ConsumerController {
   private final Logger logger = LoggerFactory.getLogger(ConsumerController.class);
  @Autowired
     private HomeClient homeClient;

 
   @GetMapping("/hello/{id}/{id2}")
     public String hello(@PathVariable(name="id") Integer employeeId,@PathVariable(name="id2") Integer employeeId2) {
      System.out.print(employeeId2);
      
         String message = homeClient.home(employeeId,employeeId2);
         
         logger.info("[eureka-fegin][ConsumerController][hello], message={}", message);
  // log.info("[eureka-ribbon][EurekaRibbonConntroller][syaHello], message={}", message);
         return message ;
         
     }
   
  @GetMapping("/helloEX/{id}/{id2}")
     public String helloEX(@PathVariable(name="id") Integer employeeId,@PathVariable(name="id2") Integer employeeId2) {
      System.out.print(employeeId2);
      
         String message = homeClient.home2(employeeId,employeeId2);
         
         logger.info("[eureka-fegin][ConsumerController][hello], message={}", message);
  // log.info("[eureka-ribbon][EurekaRibbonConntroller][syaHello], message={}", message);
         return message ;
         
  }
  

  
  @GetMapping("/getBlance/{id}")
     public String getblance(@PathVariable(name="id") String employeeId) {
      //System.out.print(employeeId2);
      
         String message = homeClient.getblance(employeeId);
         
         logger.info("[eureka-fegin][ConsumerController][getBlance], message={}", message);
  // log.info("[eureka-ribbon][EurekaRibbonConntroller][syaHello], message={}", message);
         return message ;
         
  }
  
  @GetMapping("/transfer/{id}/{id2}/{price}")
  @ResponseStatus(HttpStatus.OK)
     public String transfer(@PathVariable(name="id") String employeeId,@PathVariable(name="id2") String employeeId2 ,@PathVariable(name="price") Integer price) {
      //System.out.print(employeeId2);
      
         String message = homeClient.transfer(employeeId,employeeId2,price);
         
         logger.info("[eureka-fegin][ConsumerController][transfer], message={}", message);
  // log.info("[eureka-ribbon][EurekaRibbonConntroller][syaHello], message={}", message);
         return message ;
         
     }
  @PostMapping("/user")
   public String aveUser(@RequestBody UserEntity user) {
    return homeClient.aveUser(user);
  }
  @PostMapping("/login")
  @ResponseStatus(HttpStatus.OK)
   public String  login( UserEntityEx user) {
    //String message = Response.status(Response.Status.OK).entity("Entity not found for UUID: " ).build().toString();
    logger.info("[eureka-fegin][ConsumerController][login], message={}", user.toString());
    //System.out.println(message);
    return user.toString();
  }

}
```
# consumer homeclient

```
package com.example.demo.controller;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;

import com.example.demo.entity.UserEntity;

@FeignClient(value ="eureka-provider",fallbackFactory=HystrixClientFallbackFactory.class)
public interface HomeClient {
  @GetMapping("/")
  public String home(@RequestParam (value="id", required = false) Integer employeeId,@RequestParam (value="id2", required = false) Integer employeeId2) ;

  
  @GetMapping("/getblance")
  public String getblance(@RequestParam (value="id", required = false)  String employeeId) ;

  @GetMapping("/transfer")
  public String transfer(@RequestParam(value = "id", required = false)  String employeeId,
  @RequestParam(value = "id2", required = false)  String employeeId2 , @RequestParam(value = "price", required = false)  Integer price) ;
  
  
  
  @GetMapping("/ep1")
  public String home2(@RequestParam (value="id", required = false) Integer employeeId,@RequestParam (value="id2", required = false) Integer employeeId2) ;
  @PostMapping("/user")
  public String aveUser(@RequestBody UserEntity user);
}
```
# provider

這邊要注意 我作弊一下，我們是呼叫一個method 然後他就要回傳，現實情況是不能這樣用的因為geth 不管是佈署合約 還是 交易 這些都是需要等待 被打包的，這段時間是不同步的所以應該是  

![](https://i.imgur.com/i3ERdJg.png)

  

正確呼叫方法應該是這樣，  

我這邊作弊先在 一開始就完成 帳號的登入。也就是在 main 函數那邊
```
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.loadbalancer.LoadBalanced;
import org.springframework.cloud.netflix.eureka.EnableEurekaClient;
import org.springframework.context.annotation.Bean;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import com.example.demo.entity.UserEntity;

import springfox.documentation.swagger2.annotations.EnableSwagger2;

import java.io.IOException;
import java.math.BigInteger;
import java.util.concurrent.ExecutionException;

import org.web3j.crypto.CipherException;
import org.web3j.crypto.Credentials;
import org.web3j.crypto.WalletUtils;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.core.DefaultBlockParameterName;
import org.web3j.protocol.core.methods.request.EthFilter;
import org.web3j.protocol.core.methods.response.Web3ClientVersion;
import org.web3j.protocol.http.HttpService;
import org.web3j.tx.gas.DefaultGasProvider;

@SpringBootApplication
@EnableEurekaClient
@RestController
//@EnableSwagger2
public class EurekaServiceProviderApplication {
 private final static String PRIVATE_KEY = "eb239949bb46a187b4ff1645a13a9c0c146f7e0890d18426a639ae3add6b690a";
 private  static Web3j web3;
 private static Credentials credentials;
 private static Token exampleContract;
 private static Credentials getCredentialsFromPrivateKeyAddress() throws IOException, CipherException {
  final Credentials credentials = WalletUtils.loadCredentials("654321",
    "F:\\geth\\data\\keystore\\UTC--2020-01-03T05-58-33.219268500Z--21d10c5e114a959e6e92c6f5f0ffcbe7df7785f1");
  return credentials;
 }

 private static Credentials getCredentialsFromPrivateKey() {
  return Credentials.create(PRIVATE_KEY);
 }

 private final static BigInteger GAS_LIMIT = BigInteger.valueOf(210000000L);

 private final static BigInteger GAS_PRICE = BigInteger.valueOf(10000L);

 private static String deployContract(final Web3j web3j, final Credentials credentials) throws Exception {
  return Token.deploy(web3j, credentials, GAS_PRICE, GAS_LIMIT).send().getContractAddress();
 }

 private static Token loadContract(final String address, final Web3j web3j, final Credentials credentials) {
  return Token.load(address, web3j, credentials, GAS_PRICE, GAS_LIMIT);
 }

 private static void test(final String tmp) {
  System.out.println("hhhhhhhhhhhhhhhhhhhhh" + tmp);

 }

 private static void activateFilter(final Web3j web3j, final String contractAddress, final Token exampleContract) {
  final EthFilter filter = new EthFilter(DefaultBlockParameterName.EARLIEST, DefaultBlockParameterName.LATEST,
    contractAddress);
  exampleContract.setBalanceEventEventObservable(filter).subscribe(log -> test(log.toString()));
  // exampleContract.setBalanceEventEventObservable(filter).subscribe(log->
  // System.out.println("hello"+log.balance));

  web3j.ethLogObservable(filter).subscribe(log -> test(log.toString()));

 }

 @LoadBalanced
 @Bean
 RestTemplate restTemplate() {
  return new RestTemplate();
 }

 @Autowired
 private RestTemplate restTemplate;

 private final Logger logger = LoggerFactory.getLogger(EurekaServiceProviderApplication.class);

 @Value("${server.port}")
 String port;

 @GetMapping("/")
 public String home(@RequestParam(value = "id", required = false) final Integer employeeId,
   @RequestParam(value = "id2", required = false) final Integer employeeId2) {
  final String message = "Hello world" + port + employeeId + employeeId2;

  logger.info("[eureka-provide][EurekaServiceProviderApplication][home], message={}", message);
  return message;
 }

 @GetMapping("/ep1")
 public String home2(@RequestParam(value = "id", required = false) final Integer employeeId,
   @RequestParam(value = "id2", required = false) final Integer employeeId2) {
  final String message = "Hello world" + port + employeeId + employeeId2;

  logger.info("[eureka-provide][EurekaServiceProviderApplication][home], message={}", message);

  // restTemplate = new RestTemplate();
  final String fooResourceUrl = "http://feign-consumer2";
  final ResponseEntity<String> response = restTemplate.getForEntity(
    fooResourceUrl + "/hello2/" + employeeId.toString() + "/" + employeeId2.toString(), String.class);
  // assertThat(response.getStatusCode(), equalTo(HttpStatus.OK));
  System.out.println(response.getStatusCode().toString() + (HttpStatus.OK).toString());
  System.out.println(response.getBody() + "test");
  return response.getBody();
 }

 @RequestMapping("/test")
 public String test() {
  final String message = "Hello world ,port:" + port;
  logger.info("[eureka-provide][EurekaServiceProviderApplication][test], message={}", message);
  return message;
 }

 @PostMapping("/user")
 public String aveUser(@RequestBody final UserEntity user) {
  System.out.println(user.getId());
  System.out.println(user.getName());
  System.out.println(user.getAge());
  return "success!";
 }

 @GetMapping("/getblance")
 public String getblance(@RequestParam(value = "id", required = false) final String employeeId) throws Exception {
  final String message = "Hello world" + port + employeeId;

  System.out.println("ok");

  final Object ans = exampleContract.balanceOf(employeeId).send();
  System.out.println(message + ans.toString());
  logger.info("[eureka-provide][EurekaServiceProviderApplication][getblance], message={}",
    message + ans.toString());
  return ans.toString();
 }

 @GetMapping("/transfer")
 
 public String transfer(@RequestParam(value = "id", required = false) final String employeeId,
   @RequestParam(value = "id2", required = false) final String employeeId2,
   @RequestParam(value = "price", required = false) final Integer price) throws Exception {
  final String message = "Hello world" + port + employeeId + employeeId2 + price;
  final Object ans = exampleContract.transfer(employeeId2, BigInteger.valueOf(price)).send();

  logger.info("[eureka-provide][EurekaServiceProviderApplication][transfer], message={}",
    message );
  return message;
 }

 public static void main(final String[] args)
   throws IOException, CipherException, InterruptedException, ExecutionException {
  final String Contract = "0xFdBd1a96ac15dB4aD6cA59120a6643e1F45fcB35";
  web3 = Web3j.build(new HttpService());  // defaults to http://localhost:8545/
  //Web3ClientVersion web3ClientVersion = web3.web3ClientVersion().sendAsync().get();
  
  //String clientVersion = web3ClientVersion.getWeb3ClientVersion();
   credentials = getCredentialsFromPrivateKeyAddress();
  
 // String deployedContract = deployContract(web3, credentials).toString();
  //Thread.sleep(30000);
  
 // Token exampleContract = loadContract(deployedContract, web3, credentials);
   exampleContract = loadContract( Contract, web3, credentials);

  activateFilter(web3, Contract ,exampleContract);
  // Boolean result = exampleContract.isValid();
  // if(result == "false")
  //  return
  SpringApplication.run(EurekaServiceProviderApplication.class, args);
 }

}
```
# 呼叫 method

建議大家還是夾在 Post 比較 好看也比較安全
```
transfer
http://localhost:9010/feign-consumer/transfer/0x4d545c6c4f6e56c1defd223a8ff202dde9845b54/0x21d10c5e114a959e6e92c6f5f0ffcbe7df7785f1/1/?token=Bearer%20eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NzgyMTgzMDMsInVzZXJuYW1lIjoiamFjayJ9.q6dHI-rICqtIOlK8c_uGx3JalZEDetgc4iSCTYxanI8

getblance
http://localhost:9010/feign-consumer/getBlance/0x4d545c6c4f6e56c1defd223a8ff202dde9845b54/?token=Bearer%20eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NzgyMTgzMDMsInVzZXJuYW1lIjoiamFjayJ9.q6dHI-rICqtIOlK8c_uGx3JalZEDetgc4iSCTYxanI8
```
# Zuul 跨域配置

加這個就沒有 要求跨域請求了
```
zuul:
  ignored-headers: Access-Control-Allow-Credentials, Access-Control-Allow-Origin
```
好了之後 寫一下 vue.js吧
# Vue 畫面配置

90行收工
```
<template>

  <div>
     <!-- <h3>Smart contract</h3>
  <el-input v-model="inputvalue" placeholder="輸入交易 hash"   > </el-input>
  <el-button type="primary" icon="el-icon-search" @click="test3()">query</el-button> -->
  <h1>ETH DEMO</h1>
    <h3>account</h3>
    <el-input v-model="token" placeholder="交易token"   ></el-input>
   <el-select v-model="inputvalue" filterable placeholder="選擇帳戶">
     
    <el-option
      v-for="item in options"
      :key="item.value"
      :label="item.label"
      :value="item.value">
    </el-option>
  </el-select>
  

  <el-input v-model="inputvalue" placeholder="--"   ></el-input>
  
 <el-button type="primary" icon="el-icon-search" @click="test1()">query</el-button>
    <h3>UserInfo</h3>
    <h3>account:</h3>
    <p>{{ userName }}</p>
    <h3>blance:</h3>
    <p>{{ blance }}</p>
  
  <h1>Transfer</h1>
  <h5>Transfer history</h5>
  
  <el-input v-model="inputvalue" placeholder="交易帳號"   ></el-input>
  <el-input v-model="targetvalue" placeholder="目標帳號"   ></el-input>
  <el-input v-model="price" placeholder="轉帳金額"   ></el-input>
  <el-button type="primary" icon="el-icon-search" @click="test2()">transfer</el-button>
  </div>
  
</template>
<script>
export default {
  data() {
    return {
      userName: "",
      blance : 0,

       options: [{
          value: '0x21d10c5e114a959e6e92c6f5f0ffcbe7df7785f1',
          label: '0x21d10c5e114a959e6e92c6f5f0ffcbe7df7785f1'
        }, {
          value: '0x4d545c6c4f6e56c1defd223a8ff202dde9845b54',
          label: '0x4d545c6c4f6e56c1defd223a8ff202dde9845b54'
        }],
        value: '',
        inputvalue: '',
        targetvalue : '',
        price : '',
        token : ''
    };
    
  },
   methods: {
     

    test1() {
      console.log(this.value);
      this.$data.userName = this.$data.inputcopy
      this.getRequest("http://localhost:9010/feign-consumer/getBlance/"+this.$data.inputvalue+"/?token="+this.$data.token).then(resp => {
  
        this.$data.blance = resp.data;
        console.log(resp.data);
   
      });
    },
    test2(){
      
      this.getRequest("http://localhost:9010/feign-consumer/transfer/"+this.$data.inputvalue+"/"+this.$data.targetvalue+"/"+this.$data.price+"/?token="+this.$data.token).then(resp => {

        console.log(resp.data);

      });
      
    }
   }
  
};
</script>
```
# 啟動

查詢餘額  

![](https://i.imgur.com/gw5EDKD.png)

  

![](https://i.imgur.com/8UreVLB.png)

這邊可以看到504  

是我有對 axios 重新包裝  

![](https://i.imgur.com/d3PuSU6.png)

![](https://i.imgur.com/uKcqYbx.png)

  

![](https://i.imgur.com/iT8LG7A.png)

  

可以看到我們的交易已經成功了  

然後挖礦一下  

![](https://i.imgur.com/KDSsa1l.png)

  

![](https://i.imgur.com/oxr7aaC.png)

  

![](https://i.imgur.com/J8KQmRP.png)

看到 都可以完成扣款，  

最簡單的解釋方式什麼是智能合約就是  

我跟你互相 簽同一張合約，所有的資料 都寫在上面，當然不同的資料就可以衍生出不同的互動方式 像是 以太坊 養貓?  

![](https://i.imgur.com/fCGZTyk.png)

可以來查看一下  

![](https://i.imgur.com/UrOUBcg.png)

  

我們一開始的合約  

![](https://i.imgur.com/0GTEWDG.png)

  

這裡面就是在儲存我們智能合約的 變數 都寫在 data 裡
