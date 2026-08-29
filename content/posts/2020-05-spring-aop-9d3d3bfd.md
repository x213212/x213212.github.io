---
title: "草寫 Spring Aop 簡易實現"
date: "2020-05-28T09:40:00.004+08:00"
updated: "2020-07-07T07:37:20.813+08:00"
permalink: "/2020/05/spring-aop.html"
original_url: "https://x8795278.blogspot.com/2020/05/spring-aop.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3405791468976600992"
tags: ["Tutorial"]
layout: post
---

![Spring mvc ,boot, application by Salaheddinesayd](https://fiverr-res.cloudinary.com/images/q_auto,f_auto/gigs/99937611/original/d1c6ac81f536b60b0df88472d3582cdc4ad644d4/spring-mvc-boot-application.png)

# spring aop 簡單實現
https://blog.csdn.net/litianxiang_kaola/article/details/85335700
https://juejin.im/post/5dea583de51d4558437236cc
在上一個文章簡單實現了 ioc 現在嘗試以 spring aop 註解來看能不能模擬一個 aop
尚未重構，慢慢有框架的形狀出來了
# 掃註解 獨立出去checkAnnotation
```java
    public static List<Map <String , Object>> ioclist = new ArrayList<>();
    public static List<Map <String , Object>> proxyioclist = new ArrayList<>();
    public  static void doScan(){
        String packagePath =  "D:\\Programming\\spring\\simplespringioc\\src\\main\\java\\com\\spring\\demo";
        File file = new File (packagePath );
        String[] childFile = file.list();
        for (String fileName : childFile) {
            //System.out.println(fileName);
            File childfiletmp = new File( packagePath +"\\" +fileName);
            String classFileName[] = childfiletmp.list();
            for (String className : classFileName ){
                if(className.equals("aop") )
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

    }
```

# checkAnnotation
aop 依自己的意思和網路上的教學小改，思考方向就是假設判斷是要為aop切面
模擬spring aop，當然官網要比這些更複雜一些，我還沒看源碼先土炮比較好玩
只有實作before 和 after ,可以看到
![](https://i.imgur.com/B31NH7Z.png)
我這邊只是在處理註解然後既然我已經在一開始的時候初始化第一次實例
那麼我在檢查註解的時候我想是否可以學習 spring 去塞入參數
我既然已經取的實例那麼我在 檢查註解的時候 那時候就使用動態代理，那麼我要解決的是如何只通過註解
傳遞到我們的 spring core 順利地呼叫到我們的method 那麼我們就完成第一步了
的到我們的method 後 我們還要想辦法把它塞入我們的 動態代理 讓動態代理也可以呼叫到，
等到動態代理可以取的method 之後我們要把我們一開始的 ioc 容器初始化的 實例給蓋掉，這樣我們的 method 去呼叫的時候
才會是已經經過 aop 代理的實例

```java

                        Before[] filters =method.getAnnotationsByType(Before.class);
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
                                            AfterAdvice = new AfterAdvice(tempObject2,  aopmethod,tempObject);
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
```

```java

    public static void checkAnnotation()  {
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

                if (tempClassType.equals("Default") || tempClassType.equals("") ) {
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
                        Before[] filters =method.getAnnotationsByType(Before.class);
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
                                            AfterAdvice = new AfterAdvice(tempObject2,  aopmethod,tempObject);
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

    public static Object getProxy(Object bean, Advice advice) {
        return Proxy.newProxyInstance(UtilsScan.class.getClassLoader(),
                bean.getClass().getInterfaces(), advice);
    }
    public static void main(String[] args) {
        UtilsScan.doScan();
    }
```
# Advice
```java

public interface Advice extends InvocationHandler {
}

```
# BeforeAdvice
```java

public class BeforeAdvice implements Advice {

    private Object bean;
    private Object o;
    private Method methodInvocation;
    public BeforeAdvice(Object bean, Method methodInvocation,Object test) {
        this.bean = bean;
        this.methodInvocation = methodInvocation;
        this.o = test;
    }

    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        // 在目标方法执行前调用通知
        //methodInvocation.invoke(o,null);
        methodInvocation.invoke(o,null);

        Object result = method.invoke(bean, args);

        return result;
    }
}

```
# AfterAdvice
```java

public class AfterAdvice implements Advice {

    private Object bean;
    private Object o;
    private Method methodInvocation;
    public AfterAdvice(Object bean, Method methodInvocation,Object test) {
        this.bean = bean;
        this.methodInvocation = methodInvocation;
        this.o = test;
    }

    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        // 在目标方法执行前调用通知

        Object result = method.invoke(bean, args);
        methodInvocation.invoke(o,null);

        return result;
    }
}

```
# IndexService
```java
public interface IndexService {
     void index();
}
```

# IndexServiceimpl
```java

@ComponentTest
public class IndexServiceimpl implements IndexService {
    @Autowired
    IndexDao dao;
    public  IndexServiceimpl(){
        System.out.println("IndexServiceimpl init" );
    }
    @Override
    public void index() {
        System.out.println("IndexServiceimpl method call" );
        dao.index();
    }
}

```

# IndexDao
```java
@ComponentTest
public class IndexDao {
    public IndexDao(){
        System.out.println("IndexDao init" );
    }
    public String  index(){
        System.out.println("IndexDao index method call");
        return "dao init";
    }
}
```

# IndexAop
```java

@ComponentTest("Aspect")
public class IndexAop {

    @Before({"com.spring.demo.impl.IndexServiceimpl","test"})
    public void beforeMethod(){
        System.out.println("qwd");
    }
    @After({"com.spring.demo.impl.IndexServiceimpl","test"})
    public void AfterMethod(){
        System.out.println("qwd2");
    }
    public void test (){
        System.out.println("hahaha");
    }
}

```

# UtilsScan
```java

public class UtilsScan {
    public static List<Map <String , Object>> ioclist = new ArrayList<>();
    public static List<Map <String , Object>> proxyioclist = new ArrayList<>();
    public  static void doScan(){
        String packagePath =  "D:\\Programming\\spring\\simplespringioc\\src\\main\\java\\com\\spring\\demo";
        File file = new File (packagePath );
        String[] childFile = file.list();
        for (String fileName : childFile) {
            //System.out.println(fileName);
            File childfiletmp = new File( packagePath +"\\" +fileName);
            String classFileName[] = childfiletmp.list();
            for (String className : classFileName ){
                if(className.equals("aop") )
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

    }
    public static void checkAnnotation()  {
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

                if (tempClassType.equals("Default") || tempClassType.equals("") ) {
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
                        Before[] filters =method.getAnnotationsByType(Before.class);
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
                                            AfterAdvice = new AfterAdvice(tempObject2,  aopmethod,tempObject);
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

    public static Object getProxy(Object bean, Advice advice) {
        return Proxy.newProxyInstance(UtilsScan.class.getClassLoader(),
                bean.getClass().getInterfaces(), advice);
    }
    public static void main(String[] args) {
        UtilsScan.doScan();
    }

}

```

# run
![](https://i.imgur.com/oQR6rIU.png)

