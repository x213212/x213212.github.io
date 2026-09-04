---
title: "使用 Spring Boot 集成 Spring security 完成簡單 Login/Menu"
date: "2019-12-12T23:31:00.000+08:00"
updated: "2019-12-13T11:46:57.767+08:00"
permalink: "/2019/12/spring-boot-spring-security-loginmenu.html"
original_url: "https://x8795278.blogspot.com/2019/12/spring-boot-spring-security-loginmenu.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3903535865685232035"
tags: ["Java", "spring boot", "Tutorial"]
layout: post
---

![](https://miro.medium.com/max/2560/1*bQV578ujCEPGvy9ZVemdUg.jpeg)

  

  

  

參考 :[SpringBoot集成Spring Security（1）](https://blog.csdn.net/yuanlaijike/article/details/80249235)   

  

# 上述文章使用的是 Mybatits，那麼我們就來用 Spring Data JPA 實現吧!

這次入門文章主要是針對各種不同的帳號限制其瀏覽頁面的權限。
# Spring security 是什麼?

Spring security在安全方面所處的層次； 安全是一個不斷演進的目標，追求一個全面的、系統級別的安全方案是非常重要的。站在安全領域的角度，我們鼓勵分層的概念，每一層都只管理自己職責範圍內的安全問題，每一層的安全機制越嚴格，我們的應用就越健壯、越安全。 1、在最底層，我們需要處理傳輸層安全和系統識別。 2、接著我們會使用防火牆，可能會聯合VPN或者IP安全機制來保證只有被授權的系統才能進行連線。 3、在企業環境中，我們需要部署一個DMZ( demilitarized zone )服務來隔離對外提供訪問的介面的伺服器與內部資料庫和應用伺服器。 4、我們的作業系統也扮演了安全中的一環，例如使用不具有特定許可權的使用者執行程序，限制使用者最大可以操作的檔案數量等。作業系統通常也會配置自己的防火牆。 5、我們可能還會嘗試使阻止DDOS( Distributed DenialofService)分散式拒絕服務和暴力破解攻擊（brute force attacks）。一個入侵檢測系統對於攻擊的監控和響應是非常有用的，可以幫助我們實時的拒絕某些TPC/IP地址的訪問。 6、從更高的層面即JVM的層面來說，我們可以通過配置最小化一個Java類可以具有的許可權(譯者注：通過JAVA_HOME/jre/lib/security/java.policy檔案進行配置) 7、最後我們在應用層面新增一些領域特定的安全配置。 Spring Security可以讓最後一點，即應用相關的安全( application security )設定變得更加容易。

# 前言

一般一個帳號可以對應到很多組權限，今天先以一個帳號限制一個頁面來進行實作， Spring security 上手門檻覺得還蠻高的，我們來二次整理別人的文章加深一下印象，順便幫大家在採一次坑

![](https://i.imgur.com/0xPV2Km.png)

現實實際是要這樣 admin 可以同時擁有 role1 和 role2 頁面瀏覽權限 當然後面可以衍伸到API限制，和一些 session 一些咚咚，架設要自己寫的話xd，請參考之前的文章 規模較小的話，好像幾乎都是自己寫比較輕量化。

![](https://i.imgur.com/AAATFzD.png)

# 目錄結構

![](https://i.imgur.com/O6MYfVF.png)

# 導入依賴

```
<dependencies>
  <dependency>
   <groupId>org.springframework.boot</groupId>
   <artifactId>spring-boot-starter-data-jpa</artifactId>
  </dependency>
  <dependency>
   <groupId>org.springframework.boot</groupId>
   <artifactId>spring-boot-starter-security</artifactId>
  </dependency>
  <dependency>
   <groupId>org.springframework.boot</groupId>
   <artifactId>spring-boot-starter-web</artifactId>
  </dependency>

  <dependency>
   <groupId>mysql</groupId>
   <artifactId>mysql-connector-java</artifactId>
   <scope>runtime</scope>
  </dependency>
  <dependency>
   <groupId>org.springframework.boot</groupId>
   <artifactId>spring-boot-starter-test</artifactId>
   <scope>test</scope>
   <exclusions>
    <exclusion>
     <groupId>org.junit.vintage</groupId>
     <artifactId>junit-vintage-engine</artifactId>
    </exclusion>
   </exclusions>
  </dependency>
  <dependency>
   <groupId>org.springframework.security</groupId>
   <artifactId>spring-security-test</artifactId>
   <scope>test</scope>
  </dependency>
  <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-logging</artifactId>
  </dependency>
 </dependencies>
```
# 執行 SQL

- sys_user

```
CREATE TABLE `sys_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

- sys_role

```
CREATE TABLE `sys_role` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

- sys_user_role

```
CREATE TABLE `sys_user_role` (
  `user_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  PRIMARY KEY (`user_id`,`role_id`),
  KEY `fk_role_id` (`role_id`),
  CONSTRAINT `fk_role_id` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```
# 初始化數據

ROLE_XXX,是Spring Security 定義的，亂取會無效
```
INSERT INTO `sys_role` VALUES ('1', 'ROLE_ADMIN');
INSERT INTO `sys_role` VALUES ('2', 'ROLE_USER');

INSERT INTO `sys_user` VALUES ('1', 'admin', '123');
INSERT INTO `sys_user` VALUES ('2', 'x213212', '123');

INSERT INTO `sys_user_role` VALUES ('1', '1');
INSERT INTO `sys_user_role` VALUES ('2', '2');
```
# Login/Menu

login.html
```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>登入</title>
</head>
<body>
<h1>登入</h1>
<form method="post" action="/login">
    <div>
        帳號：<input type="text" name="username"> <=====看我的 NAME
    </div>
    <div>
        密碼：<input type="password" name="password">  <=====看我的 NAME
    </div>
    <div>
        <button type="submit">登入</button>
    </div>
</form>
</body>
</html>
```
menu.html
```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
    <h1>登入成功</h1>
    <a href="/admin">檢查ROLE_ADMIN 權限</a>
    <a href="/user">檢查 ROLE_USER 權限</a>
    <button onclick="window.location.href='/logout'">登出</button>
</body>
</html>
```
仔細看，路徑 /login，和 username,password 都是 Spring Security 默認定義的，亂取會無效
# 設定 application.properties

這部分照舊吧沒什麼改動的
```
spring.datasource.url = jdbc:mysql://localhost:3306/mybatis?serverTimezone=UTC
spring.datasource.username = root

spring.datasource.password = root
# Keep the connection alive if idle for a long time (needed in production)
spring.datasource.testWhileIdle = true
spring.datasource.validationQuery = SELECT 1
# Show or not log for each sql query
spring.jpa.show-sql = true
# Hibernate ddl auto (create, create-drop, update)
spring.jpa.hibernate.ddl-auto = update
# Naming strategy
spring.jpa.hibernate.naming-strategy = org.hibernate.cfg.ImprovedNamingStrategy
# Use spring.jpa.properties.* for Hibernate native properties (the prefix is
# stripped before adding them to the entity manager)
# The SQL dialect makes Hibernate generate better SQL for the chosen database
spring.jpa.properties.hibernate.dialect = org.hibernate.dialect.MySQL5Dialect
```
# Entity 層

1.SysRole
```
@Entity
@Table(name = "sys_role", catalog = "mybatis")
public class SysRole {
 @Id
 @Column (name = "id")
 @GeneratedValue(strategy = GenerationType.AUTO)
    private Integer id;
 @Column (name = "name")
    private String name;
 public Integer getId() {
  return id;
 }
 public void setId(Integer id) {
  this.id = id;
 }
 public String getName() {
  return name;
 }
 public void setName(String name) {
  this.name = name;
 }

}
```
2.SysUser
```
@Entity
@Table(name = "sys_user", catalog = "mybatis")

public class SysUser {
 @Id
 @Column (name = "id")
 @GeneratedValue(strategy = GenerationType.AUTO)
    private Integer id;
 @Column (name = "name")
    private String name;
 @Column (name = "password")
 private String password;
    // 省略getter/setter
 public Integer getId() {
  return id;
 }
 public void setId(Integer id) {
  this.id = id;
 }
 public String getName() {
  return name;
 }
 public void setName(String name) {
  this.name = name;
 }
 public String getPassword() {
  return password;
 }
 public void setPassword(String password) {
  this.password = password;
 }
 
}
```
3.SysUserRole
```
@Entity
@Table(name = "sys_user_role", catalog = "mybatis")
public class SysUserRole{

 @Id
 @Column (name = "userid")

    private Integer userid;
 @Column (name = "roleid")
    private Integer roleid;
 public Integer getUserid() {
  return userid;
 }
 public void setUserid(Integer userid) {
  this.userid = userid;
 }
 public Integer getRoleid() {
  return roleid;
 }
 public void setRoleid(Integer roleid) {
  this.roleid = roleid;
 }
}
```
# Dao 層

1.SysRoleDao
```
@Repository
public interface SysRoleDao  extends JpaRepository <SysRole,Integer>{
}
```
2.SysUserDao
```
@Repository
public interface SysUserDao extends JpaRepository <SysUser,Integer>{
 @Query(value ="SELECT * FROM sys_user WHERE name = ?1", nativeQuery = true)
 public SysUser findByName(String name);
}
```
3.SysUserRoleDao
```
@Repository
public interface SysUserRoleDao  extends JpaRepository <SysUserRole,Integer>{
 @Query(value = "SELECT * FROM sys_user_role WHERE userid = ?1" , nativeQuery = true)
 public  List<SysUserRole> listByUserId(Integer userId);
}
```
# Service Interface

*1.SysRoleService*
```
public interface SysRoleService {
    SysRole selectById(Integer Id);
}
```
*2.SysUserService*
```
public interface SysUserRoleService {
  List<SysUserRole> listByUserId(Integer userId);
}
```
*3.SysUserRoleService*
```
public interface SysUserService {
    SysUser selectById(Integer Id);
    SysUser selectByName(String  Name);
}
```
# Service Impl

*1.SysRoleServiceimpl*
```
@Service
public class SysRoleServiceimpl implements SysRoleService {
 
 @Autowired
 private SysRoleDao sysRoleDao;

 @Override
 public SysRole selectById(Integer Id) {
  // TODO Auto-generated method stub
  return sysRoleDao.findById(Id).get();
 }

}
```
*2.SysUserServiceimpl*
```
@Service
public class SysUserServiceimpl implements SysUserService {

 @Autowired
 private SysUserDao sysUserDao;
    
 @Override
 public SysUser selectById(Integer Id) {
 
  return sysUserDao.findById(Id).get();
 }
 @Override
 public SysUser selectByName(String Name) {
  
  return sysUserDao.findByName(Name);
 }
}
```
*3.SysUserRoleServiceimpl*
```
@Service
public class SysUserRoleServiceimpl implements SysUserRoleService {

 @Autowired
 private SysUserRoleDao sysUserRoleDao;

 @Override
 public List<SysUserRole> listByUserId(Integer userId) {
  // TODO Auto-generated method stub
  return sysUserRoleDao.listByUserId(userId);
 }

}
```
# Controller

*1.LoginController*
如代码所示，获取当前登录用户：SecurityContextHolder.getContext().getAuthentication()  

@PreAuthorize 用于判断用户是否有指定权限，没有就不能访问!!  

或許我們api限制也可以放在這?
```
@Controller
public class LoginController {
    private org.jboss.logging.Logger logger = LoggerFactory.logger(LoginController.class);

    @RequestMapping("/")
    public String showHome() {
        String name = SecurityContextHolder.getContext().getAuthentication().getName();
        logger.info("目前登入帳號：" + name);

        return "home.html";
    }

    @RequestMapping("/login")
    public String showLogin() {
        return "login.html";
    }

    @RequestMapping("/admin")
    @ResponseBody
    @PreAuthorize("hasRole('ROLE_ADMIN')")
    public String printAdmin() {
        return "如果你看见这句话，说明你有ROLE_ADMIN角色";
    }

    @RequestMapping("/user")
    @ResponseBody
    @PreAuthorize("hasRole('ROLE_USER')")
    public String printUser() {
        return "如果你看见这句话，说明你有ROLE_USER角色";
    }
}
```
# 配置 SpringSecurity

這邊我們要把 UserDetailsService 重寫裡面的函數，其中的 loadUserByUsername 函數  

参数是用户输入的用户名。返回值是UserDetails，这是一个接口，一般使用它的子类org.springframework.security.core.userdetails.User，它有三个参数，分别是用户名、密码和权限集。
這邊我重寫的大概意思就是先去查有沒有這個ID 有這個 ID 就把他加到權限清單裡大概就是這個意思
*1.CustomUserDetailsService*
```
@Service("userDetailsService")
public class CustomUserDetailsService implements UserDetailsService {
  private Logger LOG = LoggerFactory.getLogger(CustomUserDetailsService.class);

    @Autowired
    private SysUserService userService;

    @Autowired
    private SysRoleService roleService;

    @Autowired
    private SysUserRoleService userRoleService;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        Collection<GrantedAuthority> authorities = new ArrayList<>();
        // 从数据库中取出用户信息
        SysUser user = userService.selectByName(username);
   
        // 判断用户是否存在
        if(user == null) {
            throw new UsernameNotFoundException("用户名不存在");
        }

        // 添加权限
       
        List<SysUserRole> userRoles = userRoleService.listByUserId(user.getId());
        System.out.println("--------"+userRoles.get(0).getUserid());
        System.out.println("--------"+userRoles.get(0).getRoleid());
     
        for (SysUserRole userRole : userRoles) {
            System.out.println("--------"+userRole.getRoleid().toString());
         
            SysRole role = roleService.selectById( userRole.getRoleid());
            
            System.out.println("--------"+role.getName().toString());
            
            authorities.add(new SimpleGrantedAuthority(role.getName()));
        }
        System.out.println("--------"+userRoles.size());
     
        // 返回UserDetails实现类
        return new User(user.getName().toString(), user.getPassword(), authorities);
    }
}
```
*2.WebSecurityConfig*
還記得我們在編寫 html的時候 要留意的username 和 password login 這些可以在這邊進行細部調教  

包括一些密碼加密的模組
```
@Configuration
@EnableWebSecurity
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class WebSecurityConfig extends WebSecurityConfigurerAdapter {
    @Autowired
    private CustomUserDetailsService userDetailsService;

    @Override
    protected void configure(AuthenticationManagerBuilder auth) throws Exception {
        auth.userDetailsService(userDetailsService).passwordEncoder(new PasswordEncoder() {
            @Override
         public String encode(CharSequence charSequence) {
                return charSequence.toString();
            }

            @Override
            public boolean matches(CharSequence charSequence, String s) {
                return s.equals(charSequence.toString());
            }
        });
    }

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.authorizeRequests()
                // 如果有允许匿名的url，填在下面
//                .antMatchers().permitAll()
                .anyRequest().authenticated()
                .and()
                // 设置登陆页
                .formLogin().loginPage("/login")
                // 设置登陆成功页
                .defaultSuccessUrl("/").permitAll()
                // 自定义登陆用户名和密码参数，默认为username和password
//                .usernameParameter("username")
//                .passwordParameter("password")
                .and()
                .logout().permitAll();

        // 关闭CSRF跨域
        http.csrf().disable();
    }

    @Override
    public void configure(WebSecurity web) throws Exception {
        // 设置拦截忽略文件夹，可以对静态资源放行
        web.ignoring().antMatchers("/css/**", "/js/**");
    }
}
```
# 運行情況

情況 以admin 登入  

![](https://i.imgur.com/CIHMDgH.png)

  

![](https://i.imgur.com/mlNgywA.png)

  

成功訪問  

![](https://i.imgur.com/Xcgna0g.png)

  

訪問失敗，無此權限  

![](https://i.imgur.com/nmN7kGq.png)

  

登出  

![](https://i.imgur.com/PGZKHjn.png)

  

登入失敗注意 url  

![](https://i.imgur.com/mMO1zP4.png)

  

可以發現這個刪掉 你的 登入狀態就登出了，跟之前文章做的實驗一樣  

![](https://i.imgur.com/fFImcTm.png)

這個看書的話 Spring security 幫我們做了很多 包括 session 共存等等，再比較小的公司 這種功能幾乎都是自行實現，再現在這種狀態下一般來說幾乎都是前後端分離開發，當初在選用框架的時候 vue.js 在前端就可以自定義 router，所以下面幾則文章應該會先結合 vue.js，最後 部屬 到 tomcat 伺服器…
