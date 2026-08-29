---
title: "草寫 Spring Mvc 簡單實現"
date: "2020-05-30T05:51:00.003+08:00"
updated: "2020-07-07T07:37:39.739+08:00"
permalink: "/2020/05/spring-mvc.html"
original_url: "https://x8795278.blogspot.com/2020/05/spring-mvc.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6004567186511445074"
tags: ["Tutorial"]
layout: post
---

![Spring mvc ,boot, application by Salaheddinesayd](https://fiverr-res.cloudinary.com/images/q_auto,f_auto/gigs/99937611/original/d1c6ac81f536b60b0df88472d3582cdc4ad644d4/spring-mvc-boot-application.png)

# Spring MVC 簡單實現
![](https://i.imgur.com/ze9pmDK.png)
![](https://i.imgur.com/t0Xos4U.png)
奮戰三天，差不多完成一些框架比較常用的功能，接下來是 mybitis 實現?

* 支持 get/post
* aop
* 自動注入
* 內建tomcat

# main
進入點
```java
public class Test {
    public static void main(String[] args) throws LifecycleException, InterruptedException, ServletException {
        AnnotationConfigApplicationContext annotationConfigApplicationContext = new AnnotationConfigApplicationContext ();}
        }
```
# MyRequestMapping
進入點
```java
@Target({ElementType.TYPE,ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface MyRequestMapping {

    String value() default "";

}
```
# MyRequestParam
進入點
```java
@Target({ElementType.TYPE,ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface MyRequestMapping {
    
    String value() default "";

}
```
# AnnotationConfigApplicationContext

```java
public class AnnotationConfigApplicationContext {
    public UtilsScan tmp = new UtilsScan();
    public  AnnotationConfigApplicationContext () throws LifecycleException {
        
    }
    public Object getBean (String className)
    {
        for (Map<String, Object> map : tmp.ioclist ){
            Object object = map.get(className);
            if(object!=null)
            {
                return object;
            }
        }
        return  null;
    }
}
```
# pom
仿照 spring boot
自我引入tomcat 注意與引入的 servlet 匹配
```xml
    <dependency>
            <groupId>javax.servlet</groupId>
            <artifactId>javax.servlet-api</artifactId>
            <version>3.1.0</version>
            <scope>provided</scope>

        <dependency>
            <groupId>org.apache.tomcat.embed</groupId>
            <artifactId>tomcat-embed-core</artifactId>
            <version>8.5.37</version>

        </dependency>
```
# UtilsScan
新增 initHandlerMapping，簡單來說就是 去掃相對的 註解和相對應的 class 和 method 然後把它個別塞到相對印的 map
這邊可以看到我是用 url 和 method 去做匹配
```java

public class UtilsScan {
    public static List<Map <String , Object>> ioclist = new ArrayList<>();
    public static List<Map <String , Object>> proxyioclist = new ArrayList<>();

    private Properties properties = new Properties();

    private static Map<String, Method> handlerMapping = new  HashMap<>();
    private static Map<String, Object> controllerMap  =new HashMap<>();
    public UtilsScan() throws LifecycleException {
        UtilsScan.doScan();
        java.io.File file = new java.io.File("." );
        int port = 8080;
        Tomcat tomcat = new Tomcat();
        tomcat.setBaseDir("temp");
        tomcat.setPort(port);

        String contextPath = "/";
        String docBase = file.getAbsolutePath();

        Context context = tomcat.addContext(contextPath, docBase);

        HttpServlet servlet = new MyDispatcherServlet(handlerMapping,controllerMap);
        String servletName = "MyDispatcherServlet";
        String urlPattern = "/*";

        tomcat.addServlet(contextPath, servletName, servlet);
        context.addServletMappingDecoded(urlPattern, servletName);

        tomcat.start();
        tomcat.getServer().await();

//        ServletConfig tmp =this.getServletConfig();
//        doLoadConfig(tmp.getInitParameter("contextConfigLocation"));
//
//        UtilsScan.doScan();
    }
    public  static void doScan(){
        String packagePath =  "D:\\Programming\\spring\\minispringcore\\minispring\\src\\main\\java\\com\\spring\\demo";
        File file = new File (packagePath );
        String[] childFile = file.list();
        for (String fileName : childFile) {
            System.out.println(fileName);
            File childfiletmp = new File( packagePath +"\\" +fileName);
            String classFileName[] = childfiletmp.list();
            for (String className : classFileName ){
                if(className.equals("aop") || className.equals("run") ||   className.equals("MyDispatcherServlet") )
                    continue;
                className = className.substring(0,className.indexOf("."));
                Object object = null;
                try {
                    System.out.println("com.spring." + fileName +"." + className);
                    Class classtmp  =  Class.forName("com.spring.demo." + fileName +"." + className);
                    if(classtmp.isAnnotationPresent(ComponentTest.class))
                    {
                        object = classtmp.newInstance();
                        Map<String , Object>  map= new HashMap<>();
                        map.put(classtmp.getSimpleName() , object);

                        ioclist.add(map);
                        // System.out.println( "ADD ComponentTest 註解 :"+object.getClass().getSimpleName()+"object :" +object);
                    }

                } catch(InstantiationException e) {
                    e.printStackTrace();
                } catch (IllegalAccessException e) {
                    e.printStackTrace();
                } catch (ClassNotFoundException e) {
                    e.printStackTrace();
                }

            }

        }
        System.out.println("ioclist hash map : "+ioclist);
        /*
            Autowired
         */

        checkAnnotation();
        initHandlerMapping();
    }

    private void  doLoadConfig(String location){
        //把web.xml中的contextConfigLocation对应value值的文件加载到流里面
        InputStream resourceAsStream = this.getClass().getClassLoader().getResourceAsStream(location);
        try {
            //用Properties文件加载文件里的内容
            properties.load(resourceAsStream);
        } catch (IOException e) {
            e.printStackTrace();
        }finally {
            //关流
            if(null!=resourceAsStream){
                try {
                    resourceAsStream.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }

    }
    private static void initHandlerMapping(){
        if(ioclist.isEmpty()){
            return;
        }
        try {
            for (Map <String , Object>  annotations: ioclist ){
                for ( String annotationkv : annotations.keySet()){
                    Object tempObject =   annotations.get(annotationkv);
                    Class tempClass = tempObject.getClass();
                    ComponentTest[] tempType = (ComponentTest[]) tempClass.getAnnotationsByType(ComponentTest.class);
                    String tempClassType=null;
                    String baseUrl ="";
                    try {
                        tempClassType = tempType[0].value()[0];

                        System.out.println(tempType[0].value()[0]);
                    } catch ( Exception e){
                        tempClassType ="";
                    }
                    if (tempClassType.equals("Controller") ) {

                        MyRequestMapping[] tempType2 = (MyRequestMapping[])  tempClass.getAnnotationsByType(MyRequestMapping.class);
                        baseUrl = tempType2[0].value();

                        Method[] methods = tempClass.getMethods();
                        for (Method method : methods) {
                            if(!method.isAnnotationPresent(MyRequestMapping.class)){
                                continue;
                            }
                            MyRequestMapping annotation = method.getAnnotation(MyRequestMapping.class);
                            String url = annotation.value();

                            url =(baseUrl+"/"+url).replaceAll("/+", "/");
                            handlerMapping.put(url,method);
                            controllerMap.put(url,tempObject);
                            System.out.println(url+","+method);
                        }
//                        if(tempClass.isAnnotationPresent(MyRequestMapping.class)){
//                            MyRequestMapping annotation = tempClass.getAnnotation(MyRequestMapping.class);
//                            baseUrl=annotation.value();
//                        }

                    }

                }
            }
//            for (Map.Entry<String, Object> entry: ioclist.entrySet()) {
//                Class<? extends Object> clazz = entry.getValue().getClass();
//                if(!clazz.isAnnotationPresent(ComponentTest.class)){
//                    continue;
//                }
//
//                //拼url时,是controller头的url拼上方法上的url
//                String baseUrl ="";
//                if(clazz.isAnnotationPresent(MyRequestMapping.class)){
//                    MyRequestMapping annotation = clazz.getAnnotation(MyRequestMapping.class);
//                    baseUrl=annotation.value();
//                }
//                Method[] methods = clazz.getMethods();
//                for (Method method : methods) {
//                    if(!method.isAnnotationPresent(MyRequestMapping.class)){
//                        continue;
//                    }
//                    MyRequestMapping annotation = method.getAnnotation(MyRequestMapping.class);
//                    String url = annotation.value();
//
//                    url =(baseUrl+"/"+url).replaceAll("/+", "/");
//                    handlerMapping.put(url,method);
//                    controllerMap.put(url,clazz.newInstance());
//                    System.out.println(url+","+method);
//                }
//
//            }

        } catch (Exception e) {
            e.printStackTrace();
        }

    }
    public static void checkAnnotation()  {
        //Autowired
        for (Map <String , Object>  annotations: ioclist ){
            for ( String annotationkv : annotations.keySet()){
                Object tempObject =   annotations.get(annotationkv);
                Class tempClass = tempObject.getClass();
                ComponentTest[] tempType = (ComponentTest[]) tempClass.getAnnotationsByType(ComponentTest.class);
                String tempClassType=null;
                try {
                    tempClassType = tempType[0].value()[0];
                    System.out.println(tempType[0].value()[0]);

                } catch ( Exception e){
                    tempClassType ="";
                }

                if (tempClassType.equals("Default") || tempClassType.equals("") || tempClassType.equals("Controller") ) {
                    Field[] fields = tempClass.getDeclaredFields();
                    for (Field tempfield : fields) {
//                    System.out.println(tempfield.value());
                        if (tempfield.isAnnotationPresent(Autowired.class)) {
                            String targetName = tempfield.getType().getSimpleName();

                            for (Map<String, Object> annotationchilds : ioclist) {
                                for (String annotationchildkv : annotationchilds.keySet()) {
                                    if (annotationchilds.get(annotationchildkv).getClass().getSimpleName().equals(targetName)) {

                                        tempfield.setAccessible(true);
                                        try {
                                            tempfield.set(tempObject, annotationchilds.get(targetName));
                                        } catch (IllegalAccessException e) {
                                            e.printStackTrace();
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

            }
        }

        //aop
        for (Map <String , Object>  annotations: ioclist ){
            for ( String annotationkv : annotations.keySet()){
                Object tempObject =   annotations.get(annotationkv);
                Class tempClass = tempObject.getClass();
                ComponentTest[] tempType = (ComponentTest[]) tempClass.getAnnotationsByType(ComponentTest.class);
                String tempClassType=null;
                try {
                    tempClassType = tempType[0].value()[0];
                    System.out.println(tempType[0].value()[0]);

                } catch ( Exception e){
                    tempClassType ="";
                }

                if(tempClassType.equals("Aspect")) {
                    Method[] Methods = tempClass.getMethods();
                    for (Method method : Methods)
                    {
                        Before[] filters = method.getAnnotationsByType(Before.class);
                        Annotation[][] tttt= method.getParameterAnnotations();
                        Parameter[] parameters = method.getParameters();
                        Class[] parameterTypes = method.getParameterTypes();
                        Advice AfterAdvice = null;
                        for(Before filter : filters) {
                            for (int i = 0 ; i <filter.value().length ; i ++){
                                System.out.println(filter.value()[i]);
                            }
                            Map<String , Object>  map= new HashMap<>();
                            try {
                                for (Map <String , Object>  annotations2: ioclist ){
                                    for ( String annotationkv2 : annotations2.keySet()){
                                        Object tempObject2 =   annotations2.get(annotationkv2);
                                        Class tempClass2 = tempObject2.getClass();
                                        if(tempClass2.getName().equals(filter.value()[0].toString())){
                                            //System.out.println(filter.value()[1].toString());
                                            Method aopmethod =  tempClass.getMethod(filter.value()[1].toString(),null);
                                            AfterAdvice = new BeforeAdvice(tempObject2,  aopmethod,tempObject);
                                            Object helloServiceProxy = UtilsScan.getProxy(tempObject2, AfterAdvice);

                                            map.put(tempClass2.getSimpleName() , helloServiceProxy);
                                            //ioclist.remove(tempObject2);
                                            for (int x =0 ; x < ioclist.size() ; x ++)
                                            {
                                                if(ioclist.get(x).keySet().equals( annotations2.keySet()))
                                                {
                                                    //System.out.println(map);
                                                    ioclist.set(x,map);
                                                    //System.out.println("ioclist hash map : "+ioclist);
                                                    break;
                                                }

                                            }

                                        }
                                    }
                                }

                            } catch (NoSuchMethodException e) {
                                e.printStackTrace();
                            }

                        }

                    }
                }

            }
        }
    }

    /**
     * 把字符串的首字母小写
     * @param name
     * @return
     */
    private String toLowerFirstWord(String name){
        char[] charArray = name.toCharArray();
        charArray[0] += 32;
        return String.valueOf(charArray);
    }

    public static Object getProxy(Object bean, Advice advice) {
        return Proxy.newProxyInstance(UtilsScan.class.getClassLoader(),
                bean.getClass().getInterfaces(), advice);
    }

//    public static void main(String[] args) {
//        doLoadConfig(config.getInitParameter("contextConfigLocation"));
//        UtilsScan.doScan();
//    }

}

```

#  MyDispatcherServlet
```java
package com.spring.demo.servlet;

import com.spring.demo.anno.ComponentTest;
import com.spring.demo.anno.MyRequestMapping;

import javax.servlet.ServletConfig;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.Method;
import java.net.URL;
import java.util.*;

public class MyDispatcherServlet extends HttpServlet{

    private Properties properties = new Properties();

    private List<String> classNames = new ArrayList<>();

    private Map<String, Object> ioc = new HashMap<>();

    private Map<String, Method> handlerMapping = new  HashMap<>();

    private Map<String, Object> controllerMap  =new HashMap<>();

    public MyDispatcherServlet (Map<String, Method> tmp ,Map<String, Object>  tmp2){
        this.handlerMapping = tmp;
        this.controllerMap = tmp2;

    }
    @Override
    public void init(ServletConfig config) throws ServletException {
        System.out.println("MyDispatcherServlet init");

    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
       // 統一攔截請求
        this.doPost(req,resp);
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        try {
            //統一攔截請求
            doDispatch(req,resp);
        } catch (Exception e) {
            resp.getWriter().write("500!! Server Exception");
        }

    }

    private void doDispatch(HttpServletRequest req, HttpServletResponse resp) throws Exception {
        if(handlerMapping.isEmpty()){
            return;
        }

        String url =req.getRequestURI();
        String contextPath = req.getContextPath();

        url=url.replace(contextPath, "").replaceAll("/+", "/");

        if(!this.handlerMapping.containsKey(url)){
            resp.getWriter().write("404 NOT FOUND!");
            return;
        }

        Method method =this.handlerMapping.get(url);

        //取得參數所有型態
        Class<?>[] parameterTypes = method.getParameterTypes();

        //取得請求參數
        Map<String, String[]> parameterMap = req.getParameterMap();

        //儲存請求參數
        Object [] paramValues= new Object[parameterTypes.length];

        Map<String, String> params = new  HashMap<>();
        //List keys = new ArrayList(parameterMap.keySet());
        String responseString ="";
        //方法的参数列表
        for (int i = 0; i<parameterTypes.length; i++){
            //處理參數
            String requestParam = parameterTypes[i].getSimpleName();

            if (requestParam.equals("HttpServletRequest")){
                //對參數做處理
                paramValues[i]=req;
                continue;
            }
            if (requestParam.equals("HttpServletResponse")){
                paramValues[i]=resp;
                continue;
            }

            if(requestParam.equals("String")){

                for (Map.Entry<String, String[]> param : parameterMap.entrySet()) {

                    String value =Arrays.toString(param.getValue()).replaceAll("\\[|\\]", "").replaceAll(",\\s", ",");
                    params.put(param.getKey(),value);

                }
            }

        }
        for (Map.Entry<String, String> param : params.entrySet()) {
            responseString+= param.getKey() +":" +param.getValue()  + "\n";

        }
        //反射調用
        try {
           Object tmp = method.invoke(this.controllerMap.get(url), paramValues);

            resp.getWriter().write( "doTest method success! \n"+responseString
                    +"return type :"+method.getReturnType() + ": value :" + (String)tmp);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}
```
# Controller
```java

@ComponentTest("Controller")
@MyRequestMapping("/test")
public class IndexController {

    @Autowired
    IndexServiceimpl service;

    @MyRequestMapping("/doTest")
    public String test1(@MyRequestParam("param") String param,
                      @MyRequestParam("param2") String param2){
        service.index();
        return "jojo";
    }
}

```

# run !
//get
![](https://i.imgur.com/vwB5GzJ.png)
//post
![](https://i.imgur.com/nP1VznY.png)
//error
![](https://i.imgur.com/DB6THlX.png)

![](https://i.imgur.com/PbKcq3G.png)

