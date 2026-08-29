---
title: "Spring Cloud 微服務入門 (七) Zuul + Spring Security 完成 獨立認證中心 Service 之 token +不專業 壓力測試"
date: "2019-12-28T17:08:00.002+08:00"
updated: "2020-01-16T10:59:24.650+08:00"
permalink: "/2019/12/spring-cloud-zuul-spring-security.html"
original_url: "https://x8795278.blogspot.com/2019/12/spring-cloud-zuul-spring-security.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5070460760590875448"
tags: ["JMeter", "Spring Cloud", "Tutorial", "Zuul"]
layout: post
---

![](https://i.imgur.com/gDsV4hC.png)

  

  

這邊呢我打算就乾脆拿我們上次已經做好的 Spring Security 範例來直接進行結合。  
# Spring Security

稍微研究了一下他在 JwtAuthenticationFilter  

裡面繼承了UsernamePasswordAuthenticationFilter  

在裡面有一段是  

super(new AntPathRequestMatcher("/login", “POST”));
改這一段應該就是 決定我們以前對 /login 進行 post 帳號密碼，如何不動到裡面，看了一下他是傳統的 Servlet?，不是 我們之前 實作的有接口可以調用，那麼我們就回歸到最原始的 Java 發動 HTTP Request  

這邊 又考慮到 註冊中心要不要是一個集群，如果要的話，  

Gateway 是不是又存在單點故障的問題，這邊我就沒詳細去探討有看到人說 要在 gateway 前面在加一層 nginx
先看看 如何post 格式是怎樣
```
curl -F "username=jack" -F "password=jack123" http://192.168.0.146:8080/login
```

![](https://i.imgur.com/pV4Wprq.png)

  

可以看到正確回傳  

![](https://i.imgur.com/qoKe4Fx.png)

  

所以我們等等 直街找 Java send HTTP Request 東西是不是就可以 發送了呢? 先來看看 Zuul 的邏輯吧
# Zuul Filter 介紹

![](https://i.imgur.com/ni9P1gZ.png)

- Zuul 是可以配置攔截器的
- Zuul中定義了典型的過濾器類型，這些過濾器類型對應於請求的典型生命週期。
- PRE：這種過濾器在請求被路由之前被調用。我們可以利用這種過濾器實現身份驗證，在轉換中選擇請求的微服務，記錄調試信息等。
- ROUTING：這種過濾器將請求路由發送到微服務。這種過濾器用於創建發送給微服務的請求，並使用Apache HttpClient或Netfilx Ribbon請求微服務。
- POST：這種過濾器在路由到微服務以後執行。這種過濾器可用於為響應添加標準的HTTP標頭，收集統計信息和指標，將響應從微服務發送給客戶端等。
- ERROR：在其他階段發生錯誤時執行該過濾器。

例如，我們可以定制一種STATIC類型的過濾器，直接在Zuul中生成響應，而不將請求轉發到此處的微服務。
# 順序

## 認證中心不是微服務狀況下

Zuul gateway -> POST username/password->  

Provider Service -> POST username/password -> auth 取得 respones
所以我們只要如何取得參數 並且 同步 發起http request 給 Provider 在 Provider 在同步的 發起Http request
## 假設認證中心也是微服務狀況下

Zuul gateway -> POST username/password-> Feign ConsumerController  

-> Consummerinterfact -> Provider Service -> POST username/password -> auth 取得 respones
所以我們只要如何取得參數 並且 同步 發起http request 傳給Consumer 在映射給 Provider 在 Provider 在同步的 發起Http request
# 認證中心不走微服務版

![](https://i.imgur.com/4NZl81a.png)

  

我也只看到這一篇有在講，還在前兩個月，應該沒什麼問題吧xdd，不過我還是想了下面的問題，沒有實際情況和場合只能隨便模擬一種。  

優點:response 時間 應該會快一點  

缺點:存在單點故障問題  

![](https://i.imgur.com/9c59oup.png)

  

可能後面會壓力測試一下
# 認證中心走為微服務

不走下面流程  

因為不確定是否業界這樣弄，我亂猜的xd  

優點:可以設置集群  

缺點:可能延遲，當集群一多共享同一個服務的時候有有數據分布式鎖的開發，可以用redis(還沒涉獵集群)  

1.存在著兩層以上呼叫 rest調用也就是  

應該沒少畫  

![](https://i.imgur.com/TBoSzFW.png)

  

後續每增加一個認證中心我就要多一個服務  

這是不動目前認證中心的架構  

共要呼叫四次，response 應該會更多延遲
# 不走微服務版分析

# 流程分析

# Simple Filter

TokenFilter
```
public class TokenFilter extends ZuulFilter {

    private final Logger LOGGER = LoggerFactory.getLogger(TokenFilter.class);

    @Override
    public String filterType() {
        return "pre"; //是否在路由前被調用
    }

    @Override
    public int filterOrder() {
        return 0; //filter 過濾權重
    }

    @Override
    public boolean shouldFilter() {
        return true;//是否請求過濾//
    }

    @Override
    public Object run() {
        RequestContext ctx = RequestContext.getCurrentContext();
        HttpServletRequest request = ctx.getRequest();

        LOGGER.info("--->>> TokenFilter {},{}", request.getMethod(), request.getRequestURL().toString());

        String token = request.getParameter("token");//請求token

        if (StringUtils.isNotBlank(token)) {
            ctx.setSendZuulResponse(true); //進行路由
            ctx.setResponseStatusCode(200);
            ctx.set("isSuccess", true);
            return null;
        } else {
            ctx.setSendZuulResponse(false); //不進行路由
            ctx.setResponseStatusCode(400);
            ctx.setResponseBody("token is empty");
            ctx.set("isSuccess", false);
            return null;
        }
    }

}
```
# EurekaServiceZuulApplication

```
@EnableZuulProxy
@SpringBootApplication
public class EurekaServiceZuulApplication {

 public static void main(String[] args) {
  SpringApplication.run(EurekaServiceZuulApplication.class, args);
 }
 @Bean
 public TokenFilter tokenFilter() {
  return new TokenFilter();
 }
}
```
這就意味著我們可以在這邊寫api gateway 邏輯
所以假設我們要在這邊寫邏輯就會遇到同步和非同步的問題  

來總結一下
我們請求 Provider 的 url 變化  

<http://localhost:9000/?id=987987&id2=489>  

就是要加上 token 才能訪問  

<http://localhost:9000/?id=987987&id2=489&token=token-uuid>
接下來就是 處理 如何去 調用認證中心服務這一塊  

間單的 post get
```
public class main {
  // one instance, reuse
    private final static CloseableHttpClient httpClient = HttpClients.createDefault();
 public static void main(String[] args) throws Exception {
  // TODO Auto-generated method stub
 // sendRequest();
   sendGet();
 }
    private static void sendRequest() throws Exception{
       HttpPost post = new HttpPost("http://192.168.0.146:8080/login");

          // add request parameter, form parameters
          List<NameValuePair> urlParameters = new ArrayList<>();
          urlParameters.add(new BasicNameValuePair("username", "jack"));
          urlParameters.add(new BasicNameValuePair("password", "jack123"));
          //urlParameters.add(new BasicNameValuePair("custom", "secret"));

          post.setEntity(new UrlEncodedFormEntity(urlParameters));

          try (CloseableHttpClient httpClient = HttpClients.createDefault();
               CloseableHttpResponse response = httpClient.execute(post)) {

              System.out.println(EntityUtils.toString(response.getEntity()));
          }
    }
    private static  void sendGet() throws ClientProtocolException, IOException  {

       HttpGet request = new HttpGet("http://192.168.0.146:8080/user");

          // add request headers
          request.addHeader("Authorization", "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1Nzc0MjE1NjgsInVzZXJuYW1lIjoiamFjayJ9.NF390iNY6KNUjGTsIHildCLmO2-lUhg_VDCRdvitiwE");
        //  request.addHeader(HttpHeaders.USER_AGENT, "Googlebot");

          try (CloseableHttpResponse response = httpClient.execute(request)) {

              // Get HttpResponse Status
              System.out.println(response.getStatusLine().toString());

              HttpEntity entity = response.getEntity();
              Header headers = entity.getContentType();
              System.out.println(headers);

              if (entity != null) {
                  // return it as a String
                  String result = EntityUtils.toString(entity);
                  System.out.println(result);
              }

          }
    }

}
```
# post

![](https://i.imgur.com/bUtoaMz.png)

# get

![](https://i.imgur.com/zhv5tbn.png)

上網查了一下 現在的認證流程圖好像認證中心 都是獨立出來的，我之前還在想怎麼併在api gateway 裡面，這樣就好辦了，壞處就是應該還存在著單點故障的問題，我這做法大量請求也不知道會不會掛掉畢竟沒有高可用，不然就是要把它寫成高可用，上次在板上聽到一句話
就算這家牛肉麵很好吃，你一次放1000人進去吃，老闆不罵死你才怪 xd,這就是大概為什麼要做限流這原因了，不過高併發又是另一種場合了，廢話說完了大概串接流程就這樣。
# Spring Security

我們上次寫的認證中心也已經知道，當驗證成功可以東西進去 reponese，這邊沒什麼毛病，所以流程就是簡單設定一個東西確認已經認證成功今天我判斷成功登陸的基準就是 status:200，懶得變動裡面的結構了

![](https://i.imgur.com/Tib56RR.png)

  

所以這邊已經ok了
如何觸發這段 post 和 get 就可以了上面已經有範例了  

我們把重點 拉回 Zuul Filter 看一看邏輯
# Zuul Filter

第一個重點 怎麼觸發? 意味著我們要對自己的服務發送 http request  

大家沒工具可以這樣自己查，我是這樣看比較方便一些
```
curl -F "username=jack" -F "password=jack123" http://192.168.0.146:8080/login
```
下面是我編寫的一個很簡陋的東西，流程就是對我們的認證中心發送http request get 夾帶 header，主要是去認證我們的 token 有沒有認證成功，這邊沒做帳號密碼就是怕大家混淆，所以這邊只做簡單的 token 認證!
# 不解析 url 取 header token

request.getHeader(“Authorization”))  

也可以直接對 header 做字串處理 看要分割字串還是怎樣  

還是 取代掉 Bearer%  

攔截結果  

![](https://i.imgur.com/1VVH6s3.png)

  

這邊就不做演示囉!
```
public class TokenFilter extends ZuulFilter {
 private final static CloseableHttpClient httpClient = HttpClients.createDefault();
    

    @Override
    public String filterType() {
        return "pre"; // 可以在请求被路由之前调用
    }

    @Override
    public int filterOrder() {
        return 0; // filter执行顺序，通过数字指定 ,优先级为0，数字越大，优先级越低
    }

    @Override
    public boolean shouldFilter() {
        return true;// 是否执行该过滤器，此处为true，说明需要过滤
    }

    @Override
    public Object run() {
     //sendRequest();
 
        RequestContext ctx = RequestContext.getCurrentContext();
        HttpServletRequest request = ctx.getRequest();
        System.out.println(request.getMethod());
        System.out.println( request.getRequestURL().toString());
        System.out.println( request.getHeader("Authorization"));
        // 分析我就可以了 
        

        String token = request.getParameter("token");// 获取请求的参数
//        try {
//   System.out.println(sendGet(token));
//  } catch (IOException e) {
//   // TODO Auto-generated catch block
//   e.printStackTrace();
//  }
        try {
   if (sendGet(token)) {
       ctx.setSendZuulResponse(true); //对请求进行路由
       ctx.setResponseStatusCode(200);
       ctx.set("isSuccess", true);
       return null;
   } else {
       ctx.setSendZuulResponse(false); //不对其进行路由
       ctx.setResponseStatusCode(400);
       ctx.setResponseBody("token is empty");
       ctx.set("isSuccess", false);
       return null;
   }
  } catch (ClientProtocolException e) {
   // TODO Auto-generated catch block
   e.printStackTrace();
  } catch (IOException e) {
   // TODO Auto-generated catch block
   e.printStackTrace();
  }
        return null;
    }

  // one instance, reuse
    

    private static void sendRequest() throws Exception{
       HttpPost post = new HttpPost("http://192.168.0.146:8080/login");

          // add request parameter, form parameters
          List<NameValuePair> urlParameters = new ArrayList<>();
          urlParameters.add(new BasicNameValuePair("username", "jack"));
          urlParameters.add(new BasicNameValuePair("password", "jack123"));
          //urlParameters.add(new BasicNameValuePair("custom", "secret"));

          post.setEntity(new UrlEncodedFormEntity(urlParameters));

          try (CloseableHttpClient httpClient = HttpClients.createDefault();
               CloseableHttpResponse response = httpClient.execute(post)) {

              System.out.println(EntityUtils.toString(response.getEntity()));
          }
    }
    private static  boolean sendGet(String token) throws ClientProtocolException, IOException  {

       HttpGet request = new HttpGet("http://192.168.0.146:8080/user");

          // add request headers
          request.addHeader("Authorization",token);
        //  request.addHeader(HttpHeaders.USER_AGENT, "Googlebot");

          try (CloseableHttpResponse response = httpClient.execute(request)) {

              // Get HttpResponse Status
              //System.out.println(response.getStatusLine().toString());

              HttpEntity entity = response.getEntity();
              Header headers = entity.getContentType();
             // System.out.println(headers);

              if (entity != null) {
                  // return it as a String
                  String result = EntityUtils.toString(entity);
                
                  System.out.println(result);
                  //readjson(result);
                  
                return readjson(result);
                  //readjson(result);
              }

          }
          return false;
    }
    public static boolean readjson (String tmp)
    {     
     
        //原数据
        String data=tmp;
        //创建一个ObjectMapper对象
        ObjectMapper objectMapper=new ObjectMapper();
        //读取json数据,返回一个JsonNode对象指向根节点
        try {
            JsonNode jsonNode=objectMapper.readTree(data);
            //利用JsonNode的path方法获取子节点,path方法的返回值也是JsonNode
            JsonNode subNode=jsonNode.path("details");//得到details节点
            //JsonNode对象的asInt(),asText()等方法用于获取值
            
            System.out.println(jsonNode.path("status").asText());//返回字符串,韩超
            System.out.println(jsonNode.path("msg").asText());//返回整形数据,18
            System.out.println(jsonNode.path("data").asText());//返回长整型数据,1507030123
            if(jsonNode.path("status").asText().equals("200")==true)
             return true;
//            //对于数组,可以使用size方法获取数组长度,get(index)获取索取为index的值
//            for(int i=0;i<jsonNode.path("hobbies").size();i++)
//                System.out.println(jsonNode.path("hobbies").get(i).asText());//输出hobbies对应的数组
//            
//            //获取details.birthday
//            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd-HH-mm");  
//            sdf.setTimeZone(TimeZone.getTimeZone("GMT+8"));
//            System.out.println(sdf.format(new Date(subNode.path("birthday").asLong()*1000)));
//            
//            for(int i=0;i<subNode.path("extar").size();i++)
//                System.out.println(subNode.path("extar").get(i).asText());//输出details.extar对应的数组
        } catch (JsonProcessingException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }   
        return false;
        }
     
    
}
```
# 解析 url 取 token

這邊可以看到我們是直接取 url 的參數，
```
public class TokenFilter extends ZuulFilter {
 private final static CloseableHttpClient httpClient = HttpClients.createDefault();
    

    @Override
    public String filterType() {
        return "pre"; // 可以在请求被路由之前调用
    }

    @Override
    public int filterOrder() {
        return 0; // filter执行顺序，通过数字指定 ,优先级为0，数字越大，优先级越低
    }

    @Override
    public boolean shouldFilter() {
        return true;// 是否执行该过滤器，此处为true，说明需要过滤
    }

    @Override
    public Object run() {
     //sendRequest();
 
        RequestContext ctx = RequestContext.getCurrentContext();
        HttpServletRequest request = ctx.getRequest();
        System.out.println(request.getMethod());
        System.out.println( request.getRequestURL().toString());
        

        String token = request.getParameter("token");// 获取请求的参数
//        try {
//   System.out.println(sendGet(token));
//  } catch (IOException e) {
//   // TODO Auto-generated catch block
//   e.printStackTrace();
//  }
        try {
   if (sendGet(token)) {
       ctx.setSendZuulResponse(true); //对请求进行路由
       ctx.setResponseStatusCode(200);
       ctx.set("isSuccess", true);
       return null;
   } else {
       ctx.setSendZuulResponse(false); //不对其进行路由
       ctx.setResponseStatusCode(400);
       ctx.setResponseBody("token is empty");
       ctx.set("isSuccess", false);
       return null;
   }
  } catch (ClientProtocolException e) {
   // TODO Auto-generated catch block
   e.printStackTrace();
  } catch (IOException e) {
   // TODO Auto-generated catch block
   e.printStackTrace();
  }
        return null;
    }

  // one instance, reuse
    

    private static void sendRequest() throws Exception{
       HttpPost post = new HttpPost("http://192.168.0.146:8080/login");

          // add request parameter, form parameters
          List<NameValuePair> urlParameters = new ArrayList<>();
          urlParameters.add(new BasicNameValuePair("username", "jack"));
          urlParameters.add(new BasicNameValuePair("password", "jack123"));
          //urlParameters.add(new BasicNameValuePair("custom", "secret"));

          post.setEntity(new UrlEncodedFormEntity(urlParameters));

          try (CloseableHttpClient httpClient = HttpClients.createDefault();
               CloseableHttpResponse response = httpClient.execute(post)) {

              System.out.println(EntityUtils.toString(response.getEntity()));
          }
    }
    private static  boolean sendGet(String token) throws ClientProtocolException, IOException  {

       HttpGet request = new HttpGet("http://192.168.0.146:8080/user");

          // add request headers
          request.addHeader("Authorization",token);
        //  request.addHeader(HttpHeaders.USER_AGENT, "Googlebot");

          try (CloseableHttpResponse response = httpClient.execute(request)) {

              // Get HttpResponse Status
              //System.out.println(response.getStatusLine().toString());

              HttpEntity entity = response.getEntity();
              Header headers = entity.getContentType();
             // System.out.println(headers);

              if (entity != null) {
                  // return it as a String
                  String result = EntityUtils.toString(entity);
                
                  System.out.println(result);
                  //readjson(result);
                  
                return readjson(result);
                  //readjson(result);
              }

          }
          return false;
    }
    public static boolean readjson (String tmp)
    {     
     
        //原数据
        String data=tmp;
        //创建一个ObjectMapper对象
        ObjectMapper objectMapper=new ObjectMapper();
        //读取json数据,返回一个JsonNode对象指向根节点
        try {
            JsonNode jsonNode=objectMapper.readTree(data);
            //利用JsonNode的path方法获取子节点,path方法的返回值也是JsonNode
            JsonNode subNode=jsonNode.path("details");//得到details节点
            //JsonNode对象的asInt(),asText()等方法用于获取值
            
            System.out.println(jsonNode.path("status").asText());//返回字符串,韩超
            System.out.println(jsonNode.path("msg").asText());//返回整形数据,18
            System.out.println(jsonNode.path("data").asText());//返回长整型数据,1507030123
            if(jsonNode.path("status").asText().equals("200")==true)
             return true;
//            //对于数组,可以使用size方法获取数组长度,get(index)获取索取为index的值
//            for(int i=0;i<jsonNode.path("hobbies").size();i++)
//                System.out.println(jsonNode.path("hobbies").get(i).asText());//输出hobbies对应的数组
//            
//            //获取details.birthday
//            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd-HH-mm");  
//            sdf.setTimeZone(TimeZone.getTimeZone("GMT+8"));
//            System.out.println(sdf.format(new Date(subNode.path("birthday").asLong()*1000)));
//            
//            for(int i=0;i<subNode.path("extar").size();i++)
//                System.out.println(subNode.path("extar").get(i).asText());//输出details.extar对应的数组
        } catch (JsonProcessingException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }   
        return false;
        }
     
    
}
```
# 解析 json

```
public static boolean readjson (String tmp)
    {     
     
        //原数据
        String data=tmp;
        //创建一个ObjectMapper对象
        ObjectMapper objectMapper=new ObjectMapper();
        //读取json数据,返回一个JsonNode对象指向根节点
        try {
            JsonNode jsonNode=objectMapper.readTree(data);
            //利用JsonNode的path方法获取子节点,path方法的返回值也是JsonNode
            JsonNode subNode=jsonNode.path("details");//得到details节点
            //JsonNode对象的asInt(),asText()等方法用于获取值
            
            System.out.println(jsonNode.path("status").asText());//返回字符串,韩超
            System.out.println(jsonNode.path("msg").asText());//返回整形数据,18
            System.out.println(jsonNode.path("data").asText());//返回长整型数据,1507030123
            if(jsonNode.path("status").asText().equals("200")==true)
             return true;
//            //对于数组,可以使用size方法获取数组长度,get(index)获取索取为index的值
//            for(int i=0;i<jsonNode.path("hobbies").size();i++)
//                System.out.println(jsonNode.path("hobbies").get(i).asText());//输出hobbies对应的数组
//            
//            //获取details.birthday
//            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd-HH-mm");  
//            sdf.setTimeZone(TimeZone.getTimeZone("GMT+8"));
//            System.out.println(sdf.format(new Date(subNode.path("birthday").asLong()*1000)));
//            
//            for(int i=0;i<subNode.path("extar").size();i++)
//                System.out.println(subNode.path("extar").get(i).asText());//输出details.extar对应的数组
        } catch (JsonProcessingException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }   
        return false;
        }
```
<https://blog.csdn.net/zhuge134/article/details/85470872>  

有的時候 json  jar會衝突  

新建 entity  

responese.class
```
public class responese {
 private String status;      
 private String msg;      
 private String data;
 public String getStatus() {
  return status;
 }
 public void setStatus(String status) {
  this.status = status;
 }
 public String getMsg() {
  return msg;
 }
 public void setMsg(String msg) {
  this.msg = msg;
 }
 public String getData() {
  return data;
 }
 public void setData(String data) {
  this.data = data;
 }

}
```
讀 json 要指定返回這些 java bean 這樣他才可以方便做分析  

可以看到我們還有讀寫 json，我用的是插件 jackson 我用 gson參數量太多會有錯誤的問題，我覺得原因就是最後一個 data  

![](https://i.imgur.com/lUGXiuu.png)

,可能要用我更早之前弄得 Java bean 在變數裡面加上 list 這個可能要看裡面的套件裡面的規則了，白話一點就是  

![](https://i.imgur.com/yG80vnX.png)

  

data2 裡面還有一層關於 data 的結構也就是
```
{
    "status": 200,
    "msg": "You are user",
    "data": {
        "authorities": [
            {
                "authority": "ROLE_USER"
            }
        ],
        "details": null,
        "authenticated": true,
        "principal": {
            "password": "$2a$10$AQol1A.LkxoJ5dEzS5o5E.QG9jD.hncoeCGdVaMQZaiYZ98V/JyRq",
            "username": "jack",
            "authorities": [
                {
                    "authority": "ROLE_USER"
                }
            ],
            "accountNonExpired": true,
            "accountNonLocked": true,
            "credentialsNonExpired": true,
            "enabled": true
        },
        "credentials": null,
        "name": "jack"
    }
}
```
data 裡面的
```
{
        "authorities": [
            {
                "authority": "ROLE_USER"
            }
        ],
        "details": null,
        "authenticated": true,
        "principal": {
            "password": "$2a$10$AQol1A.LkxoJ5dEzS5o5E.QG9jD.hncoeCGdVaMQZaiYZ98V/JyRq",
            "username": "jack",
            "authorities": [
                {
                    "authority": "ROLE_USER"
                }
            ],
            "accountNonExpired": true,
            "accountNonLocked": true,
            "credentialsNonExpired": true,
            "enabled": true
        },
        "credentials": null,
        "name": "jack"
    }
```
這邊不多做研究，那麼我們還有一種就是 Zuul 可不可以轉發 post 之類的東西呢，就是夾帶參數這邊我以後有空再補上，這邊跑完大概就可以run 起來了，整個認證流程就是  

![](https://i.imgur.com/gDsV4hC.png)

# 測試

![](https://i.imgur.com/F4aXnTv.png)

  

登入成功拿取token
```
http://localhost:9000/?id=987987&id2=489&token=Bearer%20eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1Nzc1MjM4OTgsInVzZXJuYW1lIjoiamFjayJ9.Leh-zyZ_wyA1jlTLQp_nPg0xQTl2ks-B-NkSKok65no
```
夾帶 token URL  

![](https://i.imgur.com/xvcpOji.png)

大量請求的話 xd 我最近發現一個 Jmater  

不專業測試，我是微服務是debug 模式 run 在 IDE 中，跟現實編譯出來 應該速度有差距?  

![](https://i.imgur.com/7A02iYm.png)

  

一秒 1000次請求，本地端不太準  

![](https://i.imgur.com/6cj7v66.png)

  

![](https://i.imgur.com/gdO5KGS.png)

  

![](https://i.imgur.com/kKWPro8.png)

  

應該沒錯ＸＤ，明天考慮補一下Zuul　post　夾帶參數 和　Zuul 限流規則
