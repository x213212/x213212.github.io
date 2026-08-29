---
title: "草寫 Spring Mvc v2"
date: "2020-06-01T16:58:00.004+08:00"
updated: "2020-07-07T07:37:48.670+08:00"
permalink: "/2020/06/spring-mvc-boot-application-by.html"
original_url: "https://x8795278.blogspot.com/2020/06/spring-mvc-boot-application-by.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8152527451458164250"
tags: ["Tutorial"]
layout: post
---

![Spring mvc ,boot, application by Salaheddinesayd](https://fiverr-res.cloudinary.com/images/q_auto,f_auto/gigs/99937611/original/d1c6ac81f536b60b0df88472d3582cdc4ad644d4/spring-mvc-boot-application.png)

# Spring MVC V2
https://zhuanlan.zhihu.com/p/37886319
https://github.com/x213212/minispring

* 修正jdk 動態代理改為 cglib
* 修正 servlet controller 攔截不到 AOP 問題
草寫
https://github.com/x213212/minispring

![](https://i.imgur.com/fG8wO2u.png)
![](https://i.imgur.com/Caf90Le.png)

![](https://i.imgur.com/q6sFjwF.png)
![](https://i.imgur.com/aZLVTaK.png)
![](https://i.imgur.com/jrR2MbX.png)
![](https://i.imgur.com/s0ahkwL.png)
![](https://i.imgur.com/3oFzmhI.png)
![](https://i.imgur.com/PFldqsw.png)
# Untils init
我首先先找出 ScanAOP 裡面所要代理的 目標 bean 和 method
再來就是 在 AOPMapping 取得子節點
BeanAopMapping 對 子節點 不需要動態代理 和 動態代理 bean 做替換
Switchbean 將 ioclist 父節點 換為 proxyioclist( Controller 攔截 aop)

```
  public static void checkAnnotation()  {
        //scan aop
        ScanAOP(ioclist);
        AOPMapping(proxyioclist);
        BeanAopMapping(ioclist);
        Switchbean();

        }
```
# Untils.java
```java
package com.spring.demo.utils;

import com.spring.demo.anno.*;
import com.spring.demo.anno.aop.*;
import com.spring.demo.servlet.MyDispatcherServlet;
import net.sf.cglib.proxy.Enhancer;
import org.apache.catalina.Context;
import org.apache.catalina.LifecycleException;
import org.apache.catalina.startup.Tomcat;

import javax.servlet.http.HttpServlet;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.lang.annotation.Annotation;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.util.*;

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
                    Class tempClass = tempObject.getClass() ;
                    ComponentTest[] tempType = (ComponentTest[]) tempClass.getAnnotationsByType(ComponentTest.class);
                    String tempClassType=null;
                    String baseUrl ="";
                    try {
                        tempClassType = tempType[0].value()[0];

                        System.out.println(tempType[0].value()[0]);
                    } catch ( Exception e){
                        tempClass = tempObject.getClass().getSuperclass();
                        tempType = (ComponentTest[])       tempClass.getAnnotationsByType(ComponentTest.class);
                        tempClassType =tempType[0].value()[0];
                    }
                    if (tempClassType.equals("Controller")  ) {

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
                    }

                }
            }

        } catch (Exception e) {
            e.printStackTrace();
        }

    }
    public static  List<Map <String , Object>> BeanAopMapping( List<Map <String , Object>> master) {
        List<Map<String, Object>> tmp =   new ArrayList<>() ;

        for (Map<String, Object> annotations : master) {
            for (String annotationkv : annotations.keySet()) {
                Object tempObject = annotations.get(annotationkv);
                Class tempClass = tempObject.getClass();
                ComponentTest[] tempType = (ComponentTest[]) tempClass.getAnnotationsByType(ComponentTest.class);
                String tempClassType = null;
                try {
                    tempClassType = tempType[0].value()[0];
                    System.out.println(tempType[0].value()[0]);

                } catch (Exception e) {
                    tempClassType = "";
                }

                if (tempClassType.equals("Default") || tempClassType.equals("") || tempClassType.equals("Controller")    ) {
                    Field[] fields = tempClass.getDeclaredFields();

                    if (fields.length >0  ) {
                        for (Field tempfield : fields) {
                  //  System.out.println(tempfield.getType() +"2112");

                            if (tempfield.isAnnotationPresent(Autowired.class)) {
                                String targetName = tempfield.getType().getSimpleName();

                                for (Map<String, Object> annotationchilds : ioclist) {
                                    for (String annotationchildkv : annotationchilds.keySet()) {
                                        if (annotationchilds.get(annotationchildkv).getClass().getSimpleName().equals(targetName)) {
// && 'annotationchildkv.equals(targetName)'
                                            tempfield.setAccessible(true);
                                            try {
                                                Map<String, Object> map = new HashMap<>();
                                                map.put(targetName, annotationchilds.get(targetName));
//
                                                int k =0;
                                                boolean find = false;
                                                for (Map<String, Object> proxyio : proxyioclist) {
                                                    for (String proxyiokv : proxyio.keySet()) {
                                                        if(proxyiokv.equals(targetName)){
                                                            tempfield.set(tempObject, proxyio.get(targetName));
                                                                find =true;
                                                          //  proxyioclist.remove(k);
                                                            break;
                                                        }
                                                        k++;
                                                    }

                                                }
                                                if(find == false)
                                                {
                                                    tempfield.set(tempObject, annotationchilds.get(targetName));

                                                }
                                                tmp.add(map);
                                                BeanAopMapping(tmp);

                                            } catch (IllegalAccessException e) {
                                                e.printStackTrace();
                                            }
                                            break;
                                        }

                                    }
                                }

                            }
                        }
                    } else
                        return tmp;

                }

            }
        }

        return master;
    }

    public static  List<Map <String , Object>> ScanAOP( List<Map <String , Object>> master) {
        List<Map<String, Object>> tmp =   new ArrayList<>() ;
        for (Map <String , Object>  annotations: master ){
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

                if( tempClassType.equals("Aspect")) {
                    Method[] Methods = tempClass.getMethods();
                    for (Method method : Methods) {
                        List<Map <String , Object>> methodlist =  new ArrayList<>();
                        Before[] filters = null;
                        if(method.getAnnotationsByType(Before.class).length >0){
                         filters = method.getAnnotationsByType(Before.class);

                            Advice2 AfterAdvice = null;

                            for (Before filter : filters) {
                                for (int i = 0; i < filter.value().length; i++) {
                                    System.out.println(filter.value()[i]);
                                }

                                try {
                                    for (Map<String, Object> annotations2 : ioclist) {
                                        for (String annotationkv2 : annotations2.keySet()) {
                                            Object tempObject2 = annotations2.get(annotationkv2);
                                            Class tempClass2 = tempObject2.getClass();
                                            if (tempClass2.getName().equals(filter.value()[0].toString())) {

                                                Method aopmethod = tempClass.getMethod(filter.value()[1].toString(), null);

                                                Map<String, Object> map = new HashMap<>();
                                               // Map<Object, Object> map2 = new HashMap<>();

                                                Advice2 handler = new BeforeAdvice2(tempObject2, aopmethod,null, tempObject);
                                                Object f = Enhancer.create(tempClass2, handler);
                                                //map.put(tempClass2.getSimpleName(), f);

                                                map.put(tempClass2.getSimpleName(), f);
                                                //map2.put(tempObject2, aopmethod);
                                               // methodlist.add( map2);
                                                proxyioclist.add(map);

                                                tmp.add(map);

                                              //  ScanAOP(tmp);
                                                break;
                                            }
                                            //ScanAOP(tmp);

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

        return master;
    }
    public static  List<Map <String , Object>> AOPMapping (List<Map <String , Object>> master) {
        List<Map <String , Object>> tmp = new ArrayList<>() ;
        for( int s = 0 ; s < master.size();s ++){
            Set set =((HashMap) master.get(s)).entrySet();
            Iterator i =set.iterator();
            // Display elements
            while(i.hasNext()) {
                Map.Entry me = (Map.Entry)i.next();
                System.out.print(me.getKey() + ": ");
                if(me.getValue()!= null)
                if( me.getValue().getClass().getSuperclass().getDeclaredFields().length >0 ){
                    Map <String , Object> tst = new HashMap<>();
                    Field[] fields = me.getValue().getClass().getSuperclass().getDeclaredFields();
                    for (Field tempfield : fields) {
                        String targetName = tempfield.getType().getSimpleName();
                        for (Map<String, Object> annotationchilds : proxyioclist) {

                                    if ( annotationchilds.keySet().contains(targetName) ){
                                      tempfield.setAccessible(true);
                                        try {
                                            Map<String, Object> map = new HashMap<>();
                                            map.put( targetName, annotationchilds.get(targetName));
                                            tempfield.set(me.getValue(), annotationchilds.get(targetName));
                                            tmp.add(map);
                                        } catch (IllegalAccessException e) {
                                            e.printStackTrace();
                                        }
                                        break;
                                    }
                        }
                    }
                }
            }
        }
        return master;
    }
    public static  void Switchbean(){

        for(int i = 0 ; i <ioclist.size() ; i++)
            for(int j = 0 ; j <proxyioclist.size() ; j++){
                if(ioclist.get(i).keySet().toString().equals(proxyioclist.get(j).keySet().toString()) ){
                    ioclist.set(i,proxyioclist.get(j));
                    break;
                }
            }
    }
    public static void checkAnnotation()  {
        //scan aop
        ScanAOP(ioclist);
        AOPMapping(proxyioclist);
        BeanAopMapping(ioclist);
        Switchbean();

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
    public static Object getProxy2(Object bean, Advice advice) {
        return Proxy.newProxyInstance(UtilsScan.class.getClassLoader(),
                bean.getClass().getInterfaces(), advice);
    }

}

```

# aop  advice預計拓展為
```Java
public class BeforeAdvice2 implements Advice2 {

    private Object bean;
    private Object o;
    private Method methodInvocation;
    private Method BeforeMethodInvocation;
    private Method AfterMethodInvocation;

    private Object original;
    public BeforeAdvice2(Object bean,Method BeforeMethodInvocation , Method AfterMethodInvocation, Object test ) {
        this.bean = bean;
        this.methodInvocation = methodInvocation;
        this.BeforeMethodInvocation = BeforeMethodInvocation;
        this.AfterMethodInvocation = AfterMethodInvocation;
        this.o = test;

    }

    @Override
    public Object intercept(Object o, Method method, Object[] args, MethodProxy methodProxy) throws Throwable {
       // System.out.println("BEFORE");
      //  methodInvocation.invoke(o,null);
        //methodInvocation.invoke(this.o,null);
        if(BeforeMethodInvocation != null)
        BeforeMethodInvocation.invoke(this.o,null);
        Object result = method.invoke(bean, args);
        if(AfterMethodInvocation != null)
        AfterMethodInvocation.invoke(this.o,null);
       // System.out.println(method.getName());

     //   method.invoke(o, null);
     //   System.out.println("AFTER");
        return result;
    }

  
}

```

手寫 aop 或許可以用來拓展 手寫 mybatis (?

