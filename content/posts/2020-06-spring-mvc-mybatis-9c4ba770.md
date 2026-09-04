---
title: "草寫 Spring MVC + mybatis 簡單實現"
date: "2020-06-02T21:13:00.005+08:00"
updated: "2020-07-07T07:37:57.479+08:00"
permalink: "/2020/06/spring-mvc-mybatis.html"
original_url: "https://x8795278.blogspot.com/2020/06/spring-mvc-mybatis.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-4629861392465944570"
tags: ["Tutorial"]
layout: post
---

![](https://i.imgur.com/1BKpM7g.png)

# Spring MVC + mybatis

* aop 再次 停擺 xdd 改天再重寫 湊答案
* 新增 仿造 mybatis

https://github.com/x213212/minispring

![](https://i.imgur.com/DnOS0XP.png)
![](https://i.imgur.com/pqvCdvb.png)

# 使用jdk 動態代理
https://www.itread01.com/content/1543345520.html
由於我們的 interface 無法使用 annotation
我在一開始的時候 讀取 myConfiguration 和 SqlInvocationHandler 和 m.getAnnotation(Select.class).value()
分別是 讀 mysql 位置 帳號密碼等等，再來就是 我們要 對 interface 的函式去做攔截，再來就是 讀取 我們該 interface 裡面的註解 也就是 select.class 裡面的 值 這樣就是 不用再讀我們的 xml檔案啦~
![](https://i.imgur.com/VZgtv9F.png)

```java

    else if(classtmp.getMethods().length >0){
                        Method[] methods = classtmp.getDeclaredMethods() ;
                        for( Method m : methods){
                            if(m.isAnnotationPresent(Select.class)){

                                //UserDao tmp  = (UserDao) Proxy.newProxyInstance(UserDao.class.getClassLoader(),new Class[]{UserDao.class}, handler);
                                Map<String , Object>  map= new HashMap<>();
                                //map.put(tmp.getClass().getSimpleName() , tmp);
                                //Advice2 handler2 = new BeforeAdvice3();
                               // object = classtmp.newInstance();

                                SqlInvocationHandler handler  = new SqlInvocationHandler(myConfiguration,sqlsession ,m.getAnnotation(Select.class).value());
                                object  = Proxy.newProxyInstance(classtmp.getClassLoader(),new Class[]{classtmp},handler);
                               // ((UserDao)object).query();
                                //Proxy.newProxyInstance(UserDao.class.getClassLoader(),new Class[]{UserDao.class}, handler);
                              // object =classtmp.newInstance();
//                                Object f = Enhancer.create(UserDao.class, handler2);
                                //map.put(tempClass2.getSimpleName(), f);

                                map.put(className,object);
                                ioclist.add(map);
                            }
                        }
                    }
```

# SqlInvocationHandler
這邊對 所有 有 interface 裡面的函式 去做一個攔截的動作
```java
public class SqlInvocationHandler implements InvocationHandler {

    private Object bean;
    private Object o;
    private Method methodInvocation;
    private MySqlsession mySqlsession;

    private MyConfiguration myConfiguration;
    private String sql;
    public SqlInvocationHandler(MyConfiguration myConfiguration, MySqlsession mySqlsession , String sql) {
        this.myConfiguration=myConfiguration;
        this.mySqlsession=mySqlsession;
        this.sql = sql;
    }

    public SqlInvocationHandler(Object bean, Method methodInvocation, Object test) {
        this.bean = bean;
        this.methodInvocation = methodInvocation;
        this.o = test;
    }

    public SqlInvocationHandler() {

    }

    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        // 在目标方法执行前调用通知
        System.out.println( sql);
   
        return  mySqlsession.selectOne(sql, String.valueOf(args[0]));
    }
}
```

# MySqlsession
 指宣告一實體然後再載入到各處 代理
```java
public class MySqlsession {
	
	private Excutor excutor= new MyExcutor();  

    public <T> T selectOne(String statement, Object parameter){
        return excutor.query(statement, parameter);  
    }  

}

```

# MyExcutor
這邊是主體只要是透過 jdbc 去做 query 的動作
```java

public class MyExcutor implements Excutor{
	
	private MyConfiguration xmlConfiguration = new MyConfiguration();
	
	 @Override
	    public <T> T query(String sql, Object parameter) {
	        Connection connection=getConnection();
	        ResultSet set =null;
	        PreparedStatement pre =null;
	        try {  
	            pre = connection.prepareStatement(sql); 
	            //设置参数
	            pre.setString(1, parameter.toString());
	            set = pre.executeQuery();  
	            User u=new User();
	            //遍历结果集
	            while(set.next()){  
	                u.setId(set.getString(1));
	                u.setUsername(set.getString(2)); 
	                u.setPassword(set.getString(3));
	            }  
	            return (T) u;  
	        } catch (SQLException e) {
	            e.printStackTrace();  
	        } finally{
	               try{  
	                   if(set!=null){  
	                	   set.close();  
	                   }if(pre!=null){  
	                	   pre.close();  
	                   }if(connection!=null){  
	                	   connection.close();  
	                   }  
	               }catch(Exception e2){
	                   e2.printStackTrace();  
	               }  
	           }   
	        return null;  
	    }  
	  
	    private Connection getConnection() {
	        try {  
	            Connection connection =xmlConfiguration.build("config.xml");
	            return connection;  
	        } catch (Exception e) {
	            e.printStackTrace();  
	        }  
	        return null;  
	    }  
}

```

# IndexServiceimpl
這邊要直接跟一般 jpa 或 mybatis 一樣可以返回一個 entity
```java

@ComponentTest
public class IndexServiceimpl implements IndexService {
    @Autowired
    IndexDao dao;

    @Autowired
    UserDao dao2;
//    @Autowired
//    IndexDao2 dao2;
    public  IndexServiceimpl(){
        System.out.println("IndexServiceimpl init" );
    }
    @Override
    public User index() {
        System.out.println("IndexServiceimpl method call" );

       // System.out.println(  dao2.getUserById("1"));
        return  dao2.getUserById("1");

       // dao2.index();
    }
}

```

