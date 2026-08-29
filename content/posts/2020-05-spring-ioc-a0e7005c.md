---
title: "草寫 Spring IOC 簡易實現"
date: "2020-05-27T20:02:00.004+08:00"
updated: "2020-07-07T07:37:30.708+08:00"
permalink: "/2020/05/spring-ioc.html"
original_url: "https://x8795278.blogspot.com/2020/05/spring-ioc.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6959927071029471792"
tags: ["Tutorial"]
layout: post
---

![Spring mvc ,boot, application by Salaheddinesayd](https://fiverr-res.cloudinary.com/images/q_auto,f_auto/gigs/99937611/original/d1c6ac81f536b60b0df88472d3582cdc4ad644d4/spring-mvc-boot-application.png)

# spring ioc 自動注入 實現
![](https://i.imgur.com/YKc58mI.png)

掃描檔案目錄
```java

public class UtilsScan {
    public  static void doScan(){
        String packagePath =  "D:\\Programming\\spring\\simplespringioc\\src\\main\\java\\com\\spring\\demo";
        File file = new File (packagePath );
        String[] childFile = file.list();
        for (String fileName : childFile) {
            System.out.println(fileName);

        }

    }

    public static void main(String[] args) {
        UtilsScan.doScan();
    }
}

```
掃描目錄下class
![](https://i.imgur.com/RoqAOPE.png)

```java

public class UtilsScan {
    public  static void doScan(){
        String packagePath =  "D:\\Programming\\spring\\simplespringioc\\src\\main\\java\\com\\spring\\demo";
        File file = new File (packagePath );
        String[] childFile = file.list();
        for (String fileName : childFile) {
            //System.out.println(fileName);
            File childfiletmp = new File( packagePath +"\\" +fileName);
            String classFileName[] = childfiletmp.list();
            for (String className : classFileName ){
                className = className.substring(0,className.indexOf("."));
                try {
                    System.out.println("com.spring." + fileName +"." + className);
                   Object sprinobject =  Class.forName("com.spring.demo." + fileName +"." + className).newInstance();
                    System.out.println(sprinobject);
                } catch (InstantiationException e) {
                    e.printStackTrace();
                } catch (IllegalAccessException e) {
                    e.printStackTrace();
                } catch (ClassNotFoundException e) {
                    e.printStackTrace();
                }

            }
        }

    }

    public static void main(String[] args) {
        UtilsScan.doScan();
    }
}

```

自定義註解
延伸閱讀
https://www.itread01.com/content/1544578219.html
目錄結構
![](https://i.imgur.com/ZnAMYLA.png)

# Autowired
```java
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Autowired {
}
```
# ComponentTest
```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface ComponentTest {
}

```
# IndexDao
```java

@ComponentTest
public class IndexDao {
    public String  index(){
        return "dao init";
    }
}

```
# IndexService
```java
@ComponentTest
public class IndexService {
    @Autowired
    IndexDao dao;
    public void index() {
        System.out.println("service init" +dao.index());
    }
}
```
#  UtilsScan
註解掃描 針對 @ComponentTest 第一層 掃描
![](https://i.imgur.com/fJn48Z0.png)
```java
public class UtilsScan {
    public  static void doScan(){
        String packagePath =  "D:\\Programming\\spring\\simplespringioc\\src\\main\\java\\com\\spring\\demo";
        File file = new File (packagePath );
        String[] childFile = file.list();
        for (String fileName : childFile) {
            //System.out.println(fileName);
            File childfiletmp = new File( packagePath +"\\" +fileName);
            String classFileName[] = childfiletmp.list();
            for (String className : classFileName ){
                className = className.substring(0,className.indexOf("."));
                Object object = null;
                try {
                    System.out.println("com.spring." + fileName +"." + className);
                    Class classtmp  =  Class.forName("com.spring.demo." + fileName +"." + className);
                        if(classtmp.isAnnotationPresent(ComponentTest.class))
                        {
                            object = classtmp.newInstance();
                            System.out.println( "ADD ComponentTest 註解 :"+object.getClass().getSimpleName());
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

    }

    public static void main(String[] args) {
        UtilsScan.doScan();
    }
}

```

# 製作 ioc 容器
剛剛我們已經把有 ComponentTest 已經掃描出來了現在要把它放進去我們的 HashMap
![](https://i.imgur.com/KzE7LWL.png)
```java
public class UtilsScan {
    static List<Map <String , Object>> ioclist = new ArrayList<>();
    public  static void doScan(){
        String packagePath =  "D:\\Programming\\spring\\simplespringioc\\src\\main\\java\\com\\spring\\demo";
        File file = new File (packagePath );
        String[] childFile = file.list();
        for (String fileName : childFile) {
            //System.out.println(fileName);
            File childfiletmp = new File( packagePath +"\\" +fileName);
            String classFileName[] = childfiletmp.list();
            for (String className : classFileName ){
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
                            System.out.println( "ADD ComponentTest 註解 :"+object.getClass().getSimpleName()+"object :" +object);
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
    }

    public static void main(String[] args) {
        UtilsScan.doScan();
    }
}

```

# dao service 新增建構元

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

@ComponentTest
public class IndexService {
    @Autowired
    IndexDao dao;
    public IndexService(){
        System.out.println("IndexService init" );
    }
    public void index() {
//        System.out.println("IndexService method call" +dao.index());

    }
}

```
# AnnotationConfigApplicationContext
取得ioc 容器
```
public class AnnotationConfigApplicationContext {
    public  AnnotationConfigApplicationContext (){
        UtilsScan.doScan();
    }
    public Object getBean (String className)
    {
        for (Map<String, Object> map : UtilsScan.ioclist ){
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
# test
新增test 類
```
public class Test {
    public static void main(String[] args) {
        AnnotationConfigApplicationContext annotationConfigApplicationContext = new AnnotationConfigApplicationContext ();
        IndexService service = (IndexService) annotationConfigApplicationContext.getBean("IndexService");
        System.out.println(service);
    }
}

```

# 完成 IndexService  Autowired

![](https://i.imgur.com/VsxrH45.png)
找到加了 Autowired 註解 並根據 這個類的屬性 來初始化 該屬性的對象
# UtilsScan
```java

public class UtilsScan {
    public static List<Map <String , Object>> ioclist = new ArrayList<>();
    public  static void doScan(){
        String packagePath =  "D:\\Programming\\spring\\simplespringioc\\src\\main\\java\\com\\spring\\demo";
        File file = new File (packagePath );
        String[] childFile = file.list();
        for (String fileName : childFile) {
            //System.out.println(fileName);
            File childfiletmp = new File( packagePath +"\\" +fileName);
            String classFileName[] = childfiletmp.list();
            for (String className : classFileName ){
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
                            System.out.println( "ADD ComponentTest 註解 :"+object.getClass().getSimpleName()+"object :" +object);
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
        try {
            checkAutowried();
        } catch (IllegalAccessException e) {
            e.printStackTrace();
        }
    }
    public static void checkAutowried() throws IllegalAccessException {
        for (Map <String , Object>  annotations: ioclist ){
            for ( String annotationkv : annotations.keySet()){
                Object tempObject =   annotations.get(annotationkv);
                Class tempClass = tempObject.getClass();
                Field[] fields = tempClass.getDeclaredFields();
                for (Field tempfield :  fields ){
                    if(tempfield.isAnnotationPresent(Autowired.class)) {
                        String targetName = tempfield.getType().getSimpleName();

                        for (Map<String, Object>  annotationchilds : ioclist ){
                            for (String annotationchildkv : annotationchilds.keySet() ){
                                if(annotationchilds.get(annotationchildkv).getClass().getSimpleName().equals(targetName) ){
                                    tempfield.setAccessible(true);
                                    tempfield.set(tempObject,annotationchilds.get(targetName));
                                }
                            }
                        }

                    }
                }
            }
        }
    }
    public static void main(String[] args) {
        UtilsScan.doScan();
    }
}

```

# IndexService dao
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

@ComponentTest
public class IndexService {
    @Autowired
    IndexDao dao;
    public IndexService(){
        System.out.println("IndexService init" );
    }
    public void index() {
        System.out.println("IndexService method call" );
        dao.index();
    }
}

```
# AnnotationConfigApplicationContext
```java
public class AnnotationConfigApplicationContext {
    public  AnnotationConfigApplicationContext (){
        UtilsScan.doScan();
    }
    public Object getBean (String className)
    {
        for (Map<String, Object> map : UtilsScan.ioclist ){
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
# run
```java
public class Test {
    public static void main(String[] args) {
        AnnotationConfigApplicationContext annotationConfigApplicationContext = new AnnotationConfigApplicationContext ();
        IndexService service = (IndexService) annotationConfigApplicationContext.getBean("IndexService");
        service.index();
        System.out.println(service);
    }
}

```

![](https://i.imgur.com/pujvWfY.png)

