---
title: "Spring Cloud 微服務入門 (八) Zuul + Spring Security 完成 獨立認證中心 Service 之 Login +不專業 壓力測試"
date: "2019-12-29T00:40:00.003+08:00"
updated: "2020-01-16T10:59:24.784+08:00"
permalink: "/2019/12/spring-cloud-zuul-spring-security_29.html"
original_url: "https://x8795278.blogspot.com/2019/12/spring-cloud-zuul-spring-security_29.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-859964600021597871"
tags: ["Spring Cloud", "Tutorial", "Zuul"]
layout: post
---

# Zuul Filter

又是我，今天乾脆就寫一寫好了，Zuul 到底能不能攔截 post 來測試看看大牛寫的  

這篇寫得很好  

<https://blog.csdn.net/q1009020096/article/details/86313601>  

![](https://i.imgur.com/NEm1opN.png)

![](https://i.imgur.com/CnKdS5F.png)

```
@Override
    public Object run() {
     //sendRequest();
 
        RequestContext ctx = RequestContext.getCurrentContext();
        HttpServletRequest request = ctx.getRequest();
      
        System.out.println(request.getMethod());
        System.out.println( request.getRequestURL().toString());
        System.out.println( request.getHeader("Authorization"));
        System.out.println(request.getParameter("test"));
        HttpServletRequestWrapper httpServletRequestWrapper = (HttpServletRequestWrapper) request;
       String token2 = httpServletRequestWrapper.getRequest().getParameter("test");
      
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
```
這樣就可以來區分到底要在Zuul 邏輯和 要在 service 寫邏輯的問題了。
那麼帳號密碼的流程也很簡單  

既然我們可以在 filter 攔截到 post 帳號密碼那麼就簡單一點了
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
        System.out.println(request.getParameter("test"));
        HttpServletRequestWrapper httpServletRequestWrapper = (HttpServletRequestWrapper) request;
        String username = httpServletRequestWrapper.getRequest().getParameter("username");
        String password = httpServletRequestWrapper.getRequest().getParameter("password");
      
        String token = request.getParameter("token");// 获取请求的参数
//        try {
//   System.out.println(sendGet(token));
//  } catch (IOException e) {
//   // TODO Auto-generated catch block
//   e.printStackTrace();
//  }
        
        if(StringUtils.isNotBlank(username)&& StringUtils.isNotBlank(password) && request.getRequestURL().toString().indexOf("login") >0)
        {
         try {
    if(sendRequest(username,password))
    {
        ctx.setSendZuulResponse(true); //对请求进行路由
        ctx.setResponseStatusCode(200);
     ctx.setResponseBody("123");
        ctx.set("isSuccess", true);
     
        return null;
    }
    else
    {
     ctx.setSendZuulResponse(false); //不对其进行路由
     ctx.setResponseStatusCode(400);
     ctx.setResponseBody("驗證帳號密碼成失敗");
     ctx.set("isSuccess", false);
     
      return null;
    }
   } catch (Exception e) {
    // TODO Auto-generated catch block
    e.printStackTrace();
   }
        }else {
         
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
        }
        return null;
    }

  // one instance, reuse
    

    private static boolean sendRequest(String username,String password) throws Exception{
       HttpPost post = new HttpPost("http://192.168.0.146:8080/login");

          // add request parameter, form parameters
          List<NameValuePair> urlParameters = new ArrayList<>();
          urlParameters.add(new BasicNameValuePair("username", username));
          urlParameters.add(new BasicNameValuePair("password", password));
          //urlParameters.add(new BasicNameValuePair("custom", "secret"));

          post.setEntity(new UrlEncodedFormEntity(urlParameters));

          try (CloseableHttpClient httpClient = HttpClients.createDefault();
               CloseableHttpResponse response = httpClient.execute(post)) {
           String result = EntityUtils.toString(response.getEntity());
              System.out.println();
              httpClient.close();
              response.close();
              return readjson(result);
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
                  response.close();
                  
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
            //JsonNode subNode=jsonNode.path("details");//得到details节点
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
不負責任埋坑  

比較關鍵的點就是
```
if(StringUtils.isNotBlank(username)&& StringUtils.isNotBlank(password) && request.getRequestURL().toString().indexOf("login") >0)
```
路由規則 我還沒看 Zuul 應該是攔截不到除非你真的有這個服務，要不然就要寫成註冊中心了，那就會變成微服務版  

這裡主要就是看我們的路由規則  

![](https://i.imgur.com/ZCpdIIz.png)

  

我們幾乎是攔下所有的eureka-provider  

裡面的路徑，因為我們每一個服務要進行註冊，  

怎麼換掉呢?  

更改 驗證中心 post 那個路徑這個應該也沒什麼用 因為我們主要請求是先經過 Zuul，目前想不到 先用路徑判斷吧哈哈 實戰應該不能這樣用。
# 運行

登入成功  

![](https://i.imgur.com/UFlpt2i.png)

  

![](https://i.imgur.com/ZtlK1j3.png)

  

當然你也可以直接返回token  

Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1Nzc1NTAxMTIsInVzZXJuYW1lIjoiamFjayJ9.WMYt2CPXuXtpem9Tb6VLG6l6IPd-Osfb73d3i-GaMAc  

登入失敗  

![](https://i.imgur.com/HIFKwXl.png)

攜帶token 請求  

![](https://i.imgur.com/nKb8GfF.png)

  

![](https://i.imgur.com/eVlysWe.png)

  

攜帶錯誤token 請求  

![](https://i.imgur.com/sZBmOms.png)

  

![](https://i.imgur.com/5DcQ4jN.png)

最後又再亂測試  

我們的認證中心是獨立服務要測試也只能這樣測試了  

![](https://i.imgur.com/WzVCmmH.png)

![](https://i.imgur.com/PnESMGz.png)

  

我買的ai 開發版記憶體只有 4g xd，這也考慮到很多因素像數據機傳輸速度也有關係，我相信這種業界應該不是用這種方法應該是走 rpc 或者 驗證邏輯不使用框架也說不定，不過考慮分布式的話，這又關連到 分布式鎖的問題了，有空再寫看看微服務版，不過現成的認證中心就要整個移除掉了，下個文章記錄一下 日誌中心和 api監控看看。
