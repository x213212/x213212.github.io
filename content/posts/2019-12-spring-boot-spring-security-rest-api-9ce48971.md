---
title: "使用 Spring Boot 集成 Spring security 保護我們的 REST API (分析源碼與實作)"
date: "2019-12-15T02:21:00.000+08:00"
updated: "2019-12-15T14:57:15.602+08:00"
permalink: "/2019/12/spring-boot-spring-security-rest-api.html"
original_url: "https://x8795278.blogspot.com/2019/12/spring-boot-spring-security-rest-api.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-1875001448905413598"
tags: ["Java", "spring boot", "Tutorial"]
layout: post
---

# 以 Spring Boot 集成 Spring Security 保護我們的 REST API

在我們前幾次的教學裡都已經造過一次輪子了，包括用Spring 操作 redis 實作 了 token 完成了權限的空共存等等，當然我來做一下總結
1.帳號密碼登入驗證 session 保存認證結果存在 server 做存取。  

2.使用OAuth進行帳號密碼驗證使用第三方帳號去做登入  

好像是要遵守這種流程去獲得token  

(?好像是一種框架  

3.使用 JWT
第一種就是利用 Session來記錄使用者狀態  

第二種和第三種都是基於 Token  

第二種在不屬於開放平台上，比如說可以用第三方帳號登入的系統，實作有點複雜  

下面會來介紹第三種 JWT，在現在有 移動端時代我們比較採用這種方法。
# JWT vs Session

- 什麼是 JWT?  
  
  JWT 是基於 JSON 的開放標準 (RFC 7519)  
  
  一般被用來在 身份提供者 和 服務提供者 間傳遞被 認證 的用戶身份訊息，以便於從資源伺服器獲取資源  
  
  同時也可以增加一些額外的聲明訊息，該 token 也可直接被用於認證，也可被加密  
  
  特別適用於分佈式站點的單點登錄（SSO）場景  
  
  先來瞭解一般 session 和 jwt 的差別

- 什麼是Session  
  
  Http 協議本身是無狀態的，所以無法知道每個 request 來的是誰? 因此用戶每次 request 就必須提供帳號密碼，以便證明身份，但每次都要另外輸入帳號密碼，豈不是很麻煩?  
  
  所以當用戶第一次發 request 過來後，就會產生一組 token 紀錄在 db 和 session，並且將這組 token 給用戶，告訴其保存在 cookie，當下次發 request 的時候，就直接帶這組 token 以便證明身份。

由此我們可以知道，我們使用JWT 和 Session最大的差別就是一個是  

請參考<https://juejin.im/post/5a437441f265da43294e54c3>  

  

- JWT  
  
  一種把是 解開 token 的算法在 server。

- Session  
  
  記錄使用者 認證 token 在 server

- JWT 工作流程

![](https://i.imgur.com/mPLyzDp.png)

所以我們的流程可以敘述成下列

1. 使用者登入帳號密碼到 Server
2. 伺服器根據 編寫驗證邏輯 如果用戶合法就產生 Token
3. 伺服器返回 Token
4. 用戶得到 Token，存於cookie 或 localStorage。
5. 使用請求任何 Api的時候 都會在 header 夾帶 Token
6. 伺服器認證其 Token，如果合法就 解析其內容，根據後端頁目邏輯輸出相對應結果
7. 用戶取得結果

# Token?

token 一般長成這樣
```
eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ3YW5nIiwiY3JlYXRlZCI6MTQ4OTA3OTk4MTM5MywiZXhwIjoxNDg5Njg0NzgxfQ.RC-BYCe_UZ2URtWddUpWXIp4NMsoeq2O6UF-8tVplqXY1-CI9u1-a-9DAAJGfNWkHE81mpnR3gXzfrBAB3WUAg
```
仔細看的話就會發現都會用.去做分隔，每一段都是用 Base64 編碼
<https://www.base64decode.org/>
# 三段分成解碼就是

# 第一段

`eyJhbGciOiJIUzUxMiJ9`  

解碼後
```
{
    "alg":"HS512"
}
```
# 第二段

`eyJzdWIiOiJ3YW5nIiwiY3JlYXRlZCI6MTQ4OTA3OTk4MTM5MywiZXhwIjoxNDg5Njg0NzgxfQ`
解碼後
```
{
    "sub":"wang",
    "created":1489079981393,
    "exp":1489684781
}
```
這邊可以看到 我們這個 Token 裡面有幾個數據包括是  

sub  

created  

exp  

相對應就是  

帳號、創建時間、過期時間
# 第三段

`RC-BYCe_UZ2URtWddUpWXIp4NMsoeq2O6UF-8tVplqXY1-CI9u1-a-9DAAJGfNWkHE81mpnR3gXzfrBAB3WUAg`  

解碼後
`DmYTeȧLUZcPZ0$gZAY_7wY@`
就會發現這是算一個簽名，client 要知道密鑰才能去解開這串算是 JWT 的安全保障，所以沒有密鑰的話應該是解不開，這邊要注意在Claim 也就是第二串不要放入密碼或敏感訊息。
所以組成JWT大概就 header、payload、signature
```
header.payload.signature
```
剛剛的第一段  

通常包含兩個部分一個就是 alg 還會有另一個是 typ  

就是不一定 只有 RFC75519 實現 token 機制所以還可以指定，這邊為什麼只有一個就是 預設就是 JWT
```
{
  "alg": "HS512",
  "typ": "JWT"
}
```
# JWT 產生 與 解析?

jjwt ( [github.com/jwtk/jjwt](http://github.com/jwtk/jjwt) )  

這邊就不多說  

產生過程大概就是  

放入 帳號 創建一個 Map 然後 put
解析就是 用 jjwt parser傳入 密鑰就可以解析 token了，上述就是 給 想造輪子的人看的 xd，  

下面會來用 Spring Security 來完成我們的 Restful Api 防護安全!
# Spring Security

準備要來分析一下開源專案的例子  

<https://github.com/Smith-Cruise/Spring-Boot-Security-JWT-SPA>
Spring-Boot-Security-JWT-SPA 解決方案  

這算是寫得蠻清楚的我們仔細順過一次
登入:  

POST 帳號密碼到 \login
其中它有幾個細節我來補充一下
# 目錄結構

![](https://i.imgur.com/ZkogvUy.png)

都是文字比較抽象我們來畫圖
# Test method

```
http://localhost:8080/login
http://localhost:8080/user
http://localhost:8080/user/a
```
# 模擬登入

```
http://localhost:8080/login
```

![](https://i.imgur.com/1AVnpQa.png)

  

得到 Token之後我們到下一個
# 請求 API

```
http://localhost:8080/user
```

![](https://i.imgur.com/eSLUZTd.png)

```
http://localhost:8080/user/a
```

![](https://i.imgur.com/ygyR4JE.png)

  

可以知道我們將要做三件事(廢話 XD  

我們要來細看，以一個 login 共要觸發哪些事情
# 初始化 SecurityConfiguration

首先我們要初始化 SecurityConfiguration
```
// 开启 Security
@EnableWebSecurity
// 开启注解配置支持
@EnableGlobalMethodSecurity(securedEnabled = true, prePostEnabled = true)
public class SecurityConfiguration extends WebSecurityConfigurerAdapter {

    @Autowired
    private UserDetailsServiceImpl userDetailsServiceImpl;

    // Spring Boot 的 CacheManager，这里我们使用 JCache
    @Autowired
    private CacheManager cacheManager;

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        // 开启跨域
        http.cors()
                .and()
                // security 默认 csrf 是开启的，我们使用了 token ，这个也没有什么必要了
                .csrf().disable()
                .authorizeRequests()
                // 默认所有请求通过，但是我们要在需要权限的方法加上安全注解，这样比写死配置灵活很多
                .anyRequest().permitAll()
                .and()
                // 添加自己编写的两个过滤器
                .addFilter(new JwtAuthenticationFilter(authenticationManager()))
                .addFilter(new JwtAuthorizationFilter(authenticationManager(), cachingUserDetailsService(userDetailsServiceImpl)))
                // 前后端分离是 STATELESS，故 session 使用该策略
                .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS);
    }

    // 此处配置 AuthenticationManager，并且实现缓存
    @Override
    protected void configure(AuthenticationManagerBuilder auth) throws Exception {
        // 对自己编写的 UserDetailsServiceImpl 进一步包装，实现缓存
        CachingUserDetailsService cachingUserDetailsService = cachingUserDetailsService(userDetailsServiceImpl);
        // jwt-cache 我们在 ehcache.xml 配置文件中有声明
        UserCache userCache = new springzz (cacheManager.getCache("jwt-cache"));
        cachingUserDetailsService.setUserCache(userCache);
        System.out.println("test");
        /*
        security 默认鉴权完成后会把密码抹除，但是这里我们使用用户的密码来作为 JWT 的生成密钥，
        如果被抹除了，在对 JWT 进行签名的时候就拿不到用户密码了，故此处关闭了自动抹除密码。
         */
        auth.eraseCredentials(false);
        auth.userDetailsService(cachingUserDetailsService);
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    /*
    此处我们实现缓存的时候，我们使用了官方现成的 CachingUserDetailsService ，但是这个类的构造方法不是 public 的，
    我们不能够正常实例化，所以在这里进行曲线救国。
     */
    private CachingUserDetailsService cachingUserDetailsService(UserDetailsServiceImpl delegate) {

        Constructor<CachingUserDetailsService> ctor = null;
        try {
            ctor = CachingUserDetailsService.class.getDeclaredConstructor(UserDetailsService.class);
        } catch (NoSuchMethodException e) {
            e.printStackTrace();
        }
        Assert.notNull(ctor, "CachingUserDetailsService constructor is null");
        ctor.setAccessible(true);
  
        return BeanUtils.instantiateClass(ctor, delegate);
    }
}
```
可以看到  

![](https://i.imgur.com/JTHmfpL.png)

  

增加了兩個Filter  

一個是  

JwtAuthenticationFilter  

另外一個是  

JwtAuthorizationFilter
# 登入處理

我們先著重於  

JwtAuthenticationFilter  

他做了什麼事呢在 attemptAuthentication  

裡取得 request 裡面我們POST到後端 的帳號密碼  

並包裝成  

UsernamePasswordAuthenticationToken  

再傳給AuthenticationManager ()的 authenticate() 去做處理 (這邊說是身分驗證還不到那裡),繼續往下看
# JwtAuthenticationFilter

```
public class JwtAuthenticationFilter extends UsernamePasswordAuthenticationFilter {

    /*
    过滤器一定要设置 AuthenticationManager，所以此处我们这么编写，这里的 AuthenticationManager
    我会从 Security 配置的时候传入
    */
    public JwtAuthenticationFilter(AuthenticationManager authenticationManager) {
        /*
        运行父类 UsernamePasswordAuthenticationFilter 的构造方法，能够设置此滤器指定
        方法为 POST [\login]
        */
        super();
        setAuthenticationManager(authenticationManager);
    }

    @Override
    public Authentication attemptAuthentication(HttpServletRequest request, HttpServletResponse response) throws AuthenticationException {
        // 从请求的 POST 中拿取 username 和 password 两个字段进行登入
        String username = request.getParameter("username");
        String password = request.getParameter("password");
        UsernamePasswordAuthenticationToken token = new UsernamePasswordAuthenticationToken(username, password);
        // 设置一些客户 IP 啥信息，后面想用的话可以用，虽然没啥用
        setDetails(request, token);
        System.out.println(token.toString());
        // 交给 AuthenticationManager 进行鉴权
        return getAuthenticationManager().authenticate(token);
    }

    /*
    鉴权成功进行的操作，我们这里设置返回加密后的 token
    */
    @Override
    protected void successfulAuthentication(HttpServletRequest request, HttpServletResponse response, FilterChain chain, Authentication authResult) throws IOException, ServletException {
        handleResponse(request, response, authResult, null);
    }

    /*
    鉴权失败进行的操作，我们这里就返回 用户名或密码错误 的信息
    */
    @Override
    protected void unsuccessfulAuthentication(HttpServletRequest request, HttpServletResponse response, AuthenticationException failed) throws IOException, ServletException {
        handleResponse(request, response, null, failed);
    }

    private void handleResponse(HttpServletRequest request, HttpServletResponse response, Authentication authResult, AuthenticationException failed) throws IOException, ServletException {
        ObjectMapper mapper = new ObjectMapper();
        ResponseEntity responseEntity = new ResponseEntity();
        response.setHeader("Content-Type", "application/json;charset=UTF-8");
        if (authResult != null) {
            // 处理登入成功请求
            User user = (User) authResult.getPrincipal();
            String token = JwtUtil.sign(user.getUsername(), user.getPassword());
            responseEntity.setStatus(HttpStatus.OK.value());
            responseEntity.setMsg("登入成功");
            responseEntity.setData("Bearer " + token);
            response.setStatus(HttpStatus.OK.value());
            response.getWriter().write(mapper.writeValueAsString(responseEntity));
        } else {
            // 处理登入失败请求
            responseEntity.setStatus(HttpStatus.BAD_REQUEST.value());
            responseEntity.setMsg("用户名或密码错误");
            responseEntity.setData(null);
            response.setStatus(HttpStatus.BAD_REQUEST.value());
            response.getWriter().write(mapper.writeValueAsString(responseEntity));
        }
    }
}
```
再來可以看到他 Overrride 兩個函數  

第一個是  

successfulAuthentication  

unsuccessfulAuthentication
請注意parameter authResult 參數有無 null
```
/*
    鉴权成功进行的操作，我们这里设置返回加密后的 token
    */
    @Override
    protected void successfulAuthentication(HttpServletRequest request, HttpServletResponse response, FilterChain chain, Authentication authResult) throws IOException, ServletException {
        handleResponse(request, response, authResult, null);
    }

    /*
    鉴权失败进行的操作，我们这里就返回 用户名或密码错误 的信息
    */
    @Override
    protected void unsuccessfulAuthentication(HttpServletRequest request, HttpServletResponse response, AuthenticationException failed) throws IOException, ServletException {
        handleResponse(request, response, null, failed);
    }
```
分別是成功和失敗要處理的是可以看到他們都共同呼叫* ** handleResponse 也就是 最下面的函數  

仔細看可以發現，請善用中斷點 xd  

他在  

![](https://i.imgur.com/Pbfjsj6.png)

  

根據我們的上一次我們包裝成  

UsernamePasswordAuthenticationToken  

裡面分別取得了
```
user.getUsername()
user.getPassword()
```
這兩個他要幹嘛呢? 他拿去 我們編寫好的  

JwtUtil  

裡面進行 JWT簽名，我們繼續往下看
```
private void handleResponse(HttpServletRequest request, HttpServletResponse response, Authentication authResult, AuthenticationException failed) throws IOException, ServletException {
        ObjectMapper mapper = new ObjectMapper();
        ResponseEntity responseEntity = new ResponseEntity();
        response.setHeader("Content-Type", "application/json;charset=UTF-8");
        if (authResult != null) {
            // 处理登入成功请求
            User user = (User) authResult.getPrincipal();
            String token = JwtUtil.sign(user.getUsername(), user.getPassword());
            responseEntity.setStatus(HttpStatus.OK.value());
            responseEntity.setMsg("登入成功");
            responseEntity.setData("Bearer " + token);
            response.setStatus(HttpStatus.OK.value());
            response.getWriter().write(mapper.writeValueAsString(responseEntity));
        } else {
            // 处理登入失败请求
            responseEntity.setStatus(HttpStatus.BAD_REQUEST.value());
            responseEntity.setMsg("用户名或密码错误");
            responseEntity.setData(null);
            response.setStatus(HttpStatus.BAD_REQUEST.value());
            response.getWriter().write(mapper.writeValueAsString(responseEntity));
        }
    }
```
這個  

JwtUtil  

分別有三個一個是sign另一個是verify 最後一個是 getUsername 這個等等會在另一個 Filter  

JwtAuthorizationFilter說到用途。
```
public class JwtUtil {

    // 过期时间5分钟
    private final static long EXPIRE_TIME = 5 * 60 * 1000;

    /**
     * 生成签名,5min后过期
     * @param username 用户名
     * @param secret 用户的密码
     * @return 加密的token
     */
    public static String sign(String username, String secret) {
        Date expireDate = new Date(System.currentTimeMillis() + EXPIRE_TIME);
        try {
            Algorithm algorithm = Algorithm.HMAC256(secret);
            return JWT.create()
                    .withClaim("username", username)
                    .withExpiresAt(expireDate)
                    .sign(algorithm);
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 校验token是否正确
     * @param token 密钥
     * @param secret 用户的密码
     * @return 是否正确
     */
    public static boolean verify(String token, String username, String secret) {
        try {
            Algorithm algorithm = Algorithm.HMAC256(secret);
            JWTVerifier verifier = JWT.require(algorithm)
                    .withClaim("username", username)
                    .build();
            DecodedJWT jwt = verifier.verify(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * 获得token中的信息无需secret解密也能获得
     * @return token中包含的用户名
     */
    public static String getUsername(String token) {
        try {
            DecodedJWT jwt = JWT.decode(token);
            return jwt.getClaim("username").asString();
        } catch (JWTDecodeException e) {
            return null;
        }
    }
}
```
回到JwtAuthenticationFilter，看到了responseEntity
```
public class ResponseEntity {

    public ResponseEntity() {
    }

    public ResponseEntity(int status, String msg, Object data) {
        this.status = status;
        this.msg = msg;
        this.data = data;
    }

    private int status;

    private String msg;

    private Object data;

    public int getStatus() {
        return status;
    }

    public void setStatus(int status) {
        this.status = status;
    }

    public String getMsg() {
        return msg;
    }

    public void setMsg(String msg) {
        this.msg = msg;
    }

    public Object getData() {
        return data;
    }

    public void setData(Object data) {
        this.data = data;
    }
}
```
這邊主要是統一處理 response 的狀態，接下來就是最後了，分為處理成功和失敗 可以看到是以authResult 有沒有 null 來進行判斷，可以得知 這個在上一步呼叫的時候就有講過了，這邊可能會覺得怎Spring Scurity 把我們的帳號密碼驗證儲存在哪?  

我們繼續往下看回到初始化
handleResponse
```
private void handleResponse(HttpServletRequest request, HttpServletResponse response, Authentication authResult, AuthenticationException failed) throws IOException, ServletException {
        ObjectMapper mapper = new ObjectMapper();
        ResponseEntity responseEntity = new ResponseEntity();
        response.setHeader("Content-Type", "application/json;charset=UTF-8");
        if (authResult != null) {
            // 处理登入成功请求
            User user = (User) authResult.getPrincipal();
            String token = JwtUtil.sign(user.getUsername(), user.getPassword());
            responseEntity.setStatus(HttpStatus.OK.value());
            responseEntity.setMsg("登入成功");
            responseEntity.setData("Bearer " + token);
            response.setStatus(HttpStatus.OK.value());
            response.getWriter().write(mapper.writeValueAsString(responseEntity));
        } else {
            // 处理登入失败请求
            responseEntity.setStatus(HttpStatus.BAD_REQUEST.value());
            responseEntity.setMsg("用户名或密码错误");
            responseEntity.setData(null);
            response.setStatus(HttpStatus.BAD_REQUEST.value());
            response.getWriter().write(mapper.writeValueAsString(responseEntity));
        }
    }
```
# 觀看資料庫

作者很貼心幫我們用 hashmap 模擬了一個資料庫方便我們做調用
```
用户名 密码 权限
jack  jack123 存 Bcrypt 加密后 ROLE_USER
```
實際上在資料庫是(ps 我沒有換行)
```
用户名
jack    
密码
$2a$10$AQol1A.LkxoJ5dEzS5o5E.QG9jD.hncoeCGdVaMQZaiYZ98V/JyRq
权限
ROLE_USER
```
有了這些觀念。
# 認證 Token 原理

到這一邊我們根據上面的步驟  

使用者已經得到一組 token 也就是 根據我們的帳號和密碼去做簽名的，這邊又可以得知作者在一開始的密碼就是用  

現在的 jack123 去做加密而成而得到
```
$2a$10$AQol1A.LkxoJ5dEzS5o5E.QG9jD.hncoeCGdVaMQZaiYZ98V/JyRq
```
所以我們有 密碼 jack123 就可以解出來是什麼了，如最上面我說的 JTW 共分為三段 header 我們主要先記住  

header
```
$2a$10$AQol1A.LkxoJ5dEzS5o5E.QG9jD.hncoeCGdVaMQZaiYZ98V/JyRq
```
回到我們的 初始化
# 初始化SecurityConfiguration

```
public class SecurityConfiguration extends WebSecurityConfigurerAdapter {

    @Autowired
    private UserDetailsServiceImpl userDetailsServiceImpl;

    // Spring Boot 的 CacheManager，这里我们使用 JCache
    @Autowired
    private CacheManager cacheManager;

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        // 开启跨域
        http.cors()
                .and()
                // security 默认 csrf 是开启的，我们使用了 token ，这个也没有什么必要了
                .csrf().disable()
                .authorizeRequests()
                // 默认所有请求通过，但是我们要在需要权限的方法加上安全注解，这样比写死配置灵活很多
                .anyRequest().permitAll()
                .and()
                // 添加自己编写的两个过滤器
                .addFilter(new JwtAuthenticationFilter(authenticationManager()))
                .addFilter(new JwtAuthorizationFilter(authenticationManager(), cachingUserDetailsService(userDetailsServiceImpl)))
                // 前后端分离是 STATELESS，故 session 使用该策略
                .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS);
    }

    // 此处配置 AuthenticationManager，并且实现缓存
    @Override
    protected void configure(AuthenticationManagerBuilder auth) throws Exception {
        // 对自己编写的 UserDetailsServiceImpl 进一步包装，实现缓存
        CachingUserDetailsService cachingUserDetailsService = cachingUserDetailsService(userDetailsServiceImpl);
        // jwt-cache 我们在 ehcache.xml 配置文件中有声明
        UserCache userCache = new springzz (cacheManager.getCache("jwt-cache"));
        cachingUserDetailsService.setUserCache(userCache);
        System.out.println("test");
        /*
        security 默认鉴权完成后会把密码抹除，但是这里我们使用用户的密码来作为 JWT 的生成密钥，
        如果被抹除了，在对 JWT 进行签名的时候就拿不到用户密码了，故此处关闭了自动抹除密码。
         */
        auth.eraseCredentials(false);
        auth.userDetailsService(cachingUserDetailsService);
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    /*
    此处我们实现缓存的时候，我们使用了官方现成的 CachingUserDetailsService ，但是这个类的构造方法不是 public 的，
    我们不能够正常实例化，所以在这里进行曲线救国。
     */
    private CachingUserDetailsService cachingUserDetailsService(UserDetailsServiceImpl delegate) {

        Constructor<CachingUserDetailsService> ctor = null;
        try {
            ctor = CachingUserDetailsService.class.getDeclaredConstructor(UserDetailsService.class);
        } catch (NoSuchMethodException e) {
            e.printStackTrace();
        }
        Assert.notNull(ctor, "CachingUserDetailsService constructor is null");
        ctor.setAccessible(true);
  
        return BeanUtils.instantiateClass(ctor, delegate);
    }
```
在下面原始碼可以看到JwtAuthorizationFilterr建構元，傳入authenticationManager()和  

構造了一個cachingUserDetailsService 函數裡面的參數又塞了userDetailsServiceImpl
```
.addFilter(new JwtAuthorizationFilter(authenticationManager(), cachingUserDetailsService(userDetailsServiceImpl)))
```
我們先得知我們等等要處理  

cachingUserDetailsService  

和  

userDetailsServiceImpl  

先看這個函數
# userDetailsServiceImpl

可以發現這不是我們的 service 層嗎 裡面綁著 數據層 dao
```
@Service
public class UserDetailsServiceImpl implements UserDetailsService {

    @Autowired
    private UserService userService;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        UserEntity userEntity = userService.getUserByUsername(username);
        if (userEntity == null) {
            throw new UsernameNotFoundException("This username didn't exist.");
        }
        return new User(userEntity.getUsername(), userEntity.getPassword(), userEntity.getRole());
    }
}
```
，這一個地方主要是在處理去資料庫撈我們使用者相當於 select
```
UserEntity jack = new UserEntity(
                    "jack",
                    "$2a$10$AQol1A.LkxoJ5dEzS5o5E.QG9jD.hncoeCGdVaMQZaiYZ98V/JyRq",
                    getGrants("ROLE_USER"));
            UserEntity danny = new UserEntity(
                    "danny",
                    "$2a$10$8nMJR6r7lvh9H2INtM2vtuA156dHTcQUyU.2Q2OK/7LwMd/I.HM12",
                    getGrants("ROLE_EDITOR"));
            UserEntity smith = new UserEntity(
                    "smith",
                    "$2a$10$E86mKigOx1NeIr7D6CJM3OQnWdaPXOjWe4OoRqDqFgNgowvJW9nAi",
                    getGrants("ROLE_ADMIN"));
            data.put("jack", jack);
            data.put("danny", danny);
            data.put("smith", smith);
```
好我們來看
# cachingUserDetailsService

我們暫時把它當作緩從解決方案我們再往上一層追
```
/*
    此处我们实现缓存的时候，我们使用了官方现成的 CachingUserDetailsService ，但是这个类的构造方法不是 public 的，
    我们不能够正常实例化，所以在这里进行曲线救国。
     */
    private CachingUserDetailsService cachingUserDetailsService(UserDetailsServiceImpl delegate) {

        Constructor<CachingUserDetailsService> ctor = null;
        try {
            ctor = CachingUserDetailsService.class.getDeclaredConstructor(UserDetailsService.class);
        } catch (NoSuchMethodException e) {
            e.printStackTrace();
        }
        Assert.notNull(ctor, "CachingUserDetailsService constructor is null");
        ctor.setAccessible(true);
  
        return BeanUtils.instantiateClass(ctor, delegate);
    }
```
# SecurityConfiguration

在 SecurityConfiguration中 可以發現 有一個地方也有 cachingUserDetailsService，那麼這個地方是在幹嘛呢，可以看到他的註解寫緩存處理  

CachingUserDetailsService 這個是幹嘛的呢?  

我們往下看，請留意loadUserByUsername 回傳類型UserDetails
```
// 此处配置 AuthenticationManager，并且实现缓存
    @Override
    protected void configure(AuthenticationManagerBuilder auth) throws Exception {
        // 对自己编写的 UserDetailsServiceImpl 进一步包装，实现缓存
        CachingUserDetailsService cachingUserDetailsService = cachingUserDetailsService(userDetailsServiceImpl);
        // jwt-cache 我们在 ehcache.xml 配置文件中有声明
        UserCache userCache = new springzz (cacheManager.getCache("jwt-cache"));
        cachingUserDetailsService.setUserCache(userCache);
        System.out.println("test");
        /*
        security 默认鉴权完成后会把密码抹除，但是这里我们使用用户的密码来作为 JWT 的生成密钥，
        如果被抹除了，在对 JWT 进行签名的时候就拿不到用户密码了，故此处关闭了自动抹除密码。
         */
        auth.eraseCredentials(false);
        auth.userDetailsService(cachingUserDetailsService);
    }
```
# CachingUserDetailsService

查了一下可以看到他裡面放的是 userCache我們先把它大致上算做控制 cache的東西，所以想自幹 驗證機制應該可以往這邊動手 (?。
```
/**
 *
 * @author Luke Taylor
 * @since 2.0
 */
public class CachingUserDetailsService implements UserDetailsService {
 private UserCache userCache = new NullUserCache();
 private final UserDetailsService delegate;

 CachingUserDetailsService(UserDetailsService delegate) {
  this.delegate = delegate;
 }

 public UserCache getUserCache() {
  return userCache;
 }

 public void setUserCache(UserCache userCache) {
  this.userCache = userCache;
 }

 public UserDetails loadUserByUsername(String username) {
  UserDetails user = userCache.getUserFromCache(username);

  if (user == null) {
   user = delegate.loadUserByUsername(username);
  }

  Assert.notNull(user, () -> "UserDetailsService " + delegate
    + " returned null for username " + username + ". "
    + "This is an interface contract violation");

  userCache.putUserInCache(user);

  return user;
 }
}
```
可以發現CachingUserDetailsService 在初始化的時候又把我們剛剛 取得資料庫所有使用者帳號密碼的地方也就是建構元CachingUserDetailsService
```
cachingUserDetailsService = cachingUserDetailsService(userDetailsServiceImpl);
```
這個地方把我們控制資料庫的地方給取的了，  

在繼續往下看UserCache?
```
UserCache userCache = new springzz (cacheManager.getCache("jwt-cache"));
   cachingUserDetailsService.setUserCache(userCache);
```
這不是在剛剛CachingUserDetailsService裡面有  

setUserCache,所以我們猜測正確可以確定CachingUserDetailsService就是在控制 cache了  

你會說不對阿，裡面沒有看到邏輯诶  

有看到springzz這個初始化函數?這個是我自己改的  

原本是SpringCacheBasedUserCache  

這兩個 class 差不多，指不國插在 一個被封在 jar包裡  

不能修改 我在這裡面加了幾條 printf，順便觀察 cache 的 動作。
# loadUserByUsername

再來看位於CachingUserDetailsService 裡面的  

loadUserByUsername  

可以發現這邊裡面的邏輯就是 先去 看 cache 有沒有 沒有的話再去跟資料庫要，這邊會等到後面才會講到 請記住大概邏輯。
```
public UserDetails loadUserByUsername(String username) {
  UserDetails user = userCache.getUserFromCache(username);

  if (user == null) {
   user = delegate.loadUserByUsername(username);
  }

  Assert.notNull(user, () -> "UserDetailsService " + delegate
    + " returned null for username " + username + ". "
    + "This is an interface contract violation");

  userCache.putUserInCache(user);

  return user;
 }
```
看到這邊告一個段落又回到 初始化那邊
繼續往下看
# springzz == SpringCacheBasedUserCache

```
public class springzz implements UserCache {

 // ~ Static fields/initializers
 // =====================================================================================

 public static final Log logger = LogFactory.getLog(springzz.class);

 // ~ Instance fields
 // ================================================================================================

 public final Cache cache;

 // ~ Constructors
 // ===================================================================================================

 public springzz(Cache cache) throws Exception {
  Assert.notNull(cache, "cache mandatory");
  this.cache = cache;
 }

 // ~ Methods
 // ========================================================================================================

 public UserDetails getUserFromCache(String username) {
  Cache.ValueWrapper element = username != null ? cache.get(username) : null;

  if (logger.isDebugEnabled()) {
   logger.debug("Cache hit: " + (element != null) + "; username: " + username);
   
  }
  //System.out.println("im here"+((UserDetails)cache.get(username)).getPassword().toString() );
  if (element == null) {
   System.out.println("im here"+username);
   return null;
  }
  else {
  System.out.println("im here");
   return (UserDetails) element.get();
  }
 }

 public void putUserInCache(UserDetails user) {
  if (logger.isDebugEnabled()) {
   logger.debug("Cache put: " + user.getUsername());
 
  }
  System.out.println("Cache put:"+ user.getUsername());
  cache.put(user.getUsername(), user);
 }

 public void removeUserFromCache(UserDetails user) {
  if (logger.isDebugEnabled()) {
   logger.debug("Cache remove: " + user.getUsername());
  }

  this.removeUserFromCache(user.getUsername());
 }

 public void removeUserFromCache(String username) {
  cache.evict(username);
 }
}
```
我們這邊就看到了它們兩個是互相對應的因為
```
UserCache userCache = new springzz (cacheManager.getCache("jwt-cache"));
```
因為 springzz implements UserCache  

這不就代表兩個是一樣的?  

一樣的話就可以理解成我把一個 cachemanger 採用  

jwt-cache 的模式給丟到 userCache做處理，我們繼續往 springzz看。
# springzz

springzz 裡面有什麼呢  

我們先專心研究這兩個  

getUserFromCache  

putUserInCache
後面這個下一章做登出  

removeUserFromCache
```
public class springzz implements UserCache {

 // ~ Static fields/initializers
 // =====================================================================================

 public static final Log logger = LogFactory.getLog(springzz.class);

 // ~ Instance fields
 // ================================================================================================

 public final Cache cache;

 // ~ Constructors
 // ===================================================================================================

 public springzz(Cache cache) throws Exception {
  Assert.notNull(cache, "cache mandatory");
  this.cache = cache;
 }

 // ~ Methods
 // ========================================================================================================

 public UserDetails getUserFromCache(String username) {
  Cache.ValueWrapper element = username != null ? cache.get(username) : null;

  if (logger.isDebugEnabled()) {
   logger.debug("Cache hit: " + (element != null) + "; username: " + username);
   
  }
  //System.out.println("im here"+((UserDetails)cache.get(username)).getPassword().toString() );
  if (element == null) {
   System.out.println("im here"+username);
   return null;
  }
  else {
  System.out.println("im here");
   return (UserDetails) element.get();
  }
 }

 public void putUserInCache(UserDetails user) {
  if (logger.isDebugEnabled()) {
   logger.debug("Cache put: " + user.getUsername());
 
  }
  System.out.println("Cache put:"+ user.getUsername());
  cache.put(user.getUsername(), user);
 }

 public void removeUserFromCache(UserDetails user) {
  if (logger.isDebugEnabled()) {
   logger.debug("Cache remove: " + user.getUsername());
  }

  this.removeUserFromCache(user.getUsername());
 }

 public void removeUserFromCache(String username) {
  cache.evict(username);
 }
}
```
# getUserFromCache

先研究getUserFromCache，他裡面就是在對 cache去做處理取得元素這個元素是什麼呢?
```
public UserDetails getUserFromCache(String username) {
    Cache.ValueWrapper element = username != null ? cache.get(username) : null;

    if (logger.isDebugEnabled()) {
     logger.debug("Cache hit: " + (element != null) + "; username: " + username);
     
    }
    //System.out.println("im here"+((UserDetails)cache.get(username)).getPassword().toString() );
    if (element == null) {
     System.out.println("im here"+username);
     return null;
    }
    else {
    System.out.println("im here");
     return (UserDetails) element.get();
    }
   }
```
# ehcache.xml

就是 Ehcache 這邊沒有理解錯的話她裡面就是 key-value 類型的資料庫，可以看他以使用者帳號來做 key
```
<ehcache:config
       xmlns:ehcache="http://www.ehcache.org/v3"
       xmlns:jcache="http://www.ehcache.org/v3/jsr107">

   <ehcache:cache alias="jwt-cache">
       <!-- 我们使用用户名作为缓存的 key，故使用 String -->
       <ehcache:key-type>java.lang.String</ehcache:key-type>
       <ehcache:value-type>org.springframework.security.core.userdetails.User</ehcache:value-type>
       <ehcache:expiry>
           <ehcache:ttl unit="days">1</ehcache:ttl>
       </ehcache:expiry>
       <!-- 缓存实体的数量 -->
       <ehcache:heap unit="entries">2000</ehcache:heap>
   </ehcache:cache>

</ehcache:config>
```
幾乎可以發現getUserFromCache就是 去 cache hit 看有沒有資料有資料就回傳 UserDetails 類型 沒有就 NULL
這邊可以看到UserDetails 這不是剛剛在控制  

cachingUserDetailsService 裡面函數loadUserByUsername函數有，我們來看看  

UserDetails，繼續往下看，所以我們暫時做個總結
```
public UserDetails getUserFromCache(String username) {
   Cache.ValueWrapper element = username != null ? cache.get(username) : null;

   if (logger.isDebugEnabled()) {
    logger.debug("Cache hit: " + (element != null) + "; username: " + username);
    
   }
   //System.out.println("im here"+((UserDetails)cache.get(username)).getPassword().toString() );
   if (element == null) {
    System.out.println("im here"+username);
    return null;
   }
   else {
   System.out.println("im here");
    return (UserDetails) element.get();
   }
  }
```
# UserDetailsServiceImpl loadUserByUsername

```
public UserDetails loadUserByUsername(String username) {
  UserDetails user = userCache.getUserFromCache(username);

  if (user == null) {
   user = delegate.loadUserByUsername(username);
  }

  Assert.notNull(user, () -> "UserDetailsService " + delegate
    + " returned null for username " + username + ". "
    + "This is an interface contract violation");

  userCache.putUserInCache(user);

  return user;
 }
```
我們可以得知  

在初始化  

SecurityConfiguration configure 裡面可以知道  

UserDetailsServiceImpl 控制著 userCache  

UserDetailsServiceImpl loadUserByUsername 控制著使否要去跟資料庫去做請求，假設沒有就去跟資料庫要然後記錄在 cache下一次就會抓到資料，這邊邏輯就出來了繼續往下看。
# UserDetails

我們來針對 UserDetails 幹嘛用的，  

看到上面說我們這邊其實就是存著使用者的帳號和密碼也就是當初我們輸入的 jack 和 jack123，所以把我當成是一個 bean可以這麼說?  

可以看到  

UserDetailsServiceImpl loadUserByUsername  

在這裡面最後是返回的那要返回去哪裡呢 我們回到最初
# JwtAuthorizationFilter

請注意名字，這邊可以看到 doFilterInternal 裡面，就是攔截每一次的 所有請求 GET/POST那些等等，進續看下去可以看到他 取得一個 Token 他呼叫了getAuthentication 我們繼續往下看
JwtAuthorizationFilter
```
public class JwtAuthorizationFilter extends BasicAuthenticationFilter {

    private UserDetailsService userDetailsService;

    // 会从 Spring Security 配置文件那里传过来
    public JwtAuthorizationFilter(AuthenticationManager authenticationManager, UserDetailsService userDetailsService) {
        super(authenticationManager);
        this.userDetailsService = userDetailsService;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain) throws IOException, ServletException {
        // 判断是否有 token，并且进行认证
        Authentication token = getAuthentication(request);
        if (token == null) {
            chain.doFilter(request, response);
            return;
        }
        // 认证成功
        SecurityContextHolder.getContext().setAuthentication(token);
        chain.doFilter(request, response);
    }

    private UsernamePasswordAuthenticationToken getAuthentication(HttpServletRequest request) {
        String header = request.getHeader("Authorization");
        if (header == null || ! header.startsWith("Bearer ")) {
            return null;
        }
//        request.getSession()
//        request.getMethod()
        String token = header.split(" ")[1];
        String username = JwtUtil.getUsername(token);
        UserDetails userDetails = null;
        try {
            userDetails = userDetailsService.loadUserByUsername(username);
        } catch (UsernameNotFoundException e) {
            return null;
        }
        if (! JwtUtil.verify(token, username, userDetails.getPassword())) {
            return null;
        }
        
        System.out.println();
        return new UsernamePasswordAuthenticationToken(userDetails, null, userDetails.getAuthorities());
    }
}
```
# getAuthentication

```
private UsernamePasswordAuthenticationToken getAuthentication(HttpServletRequest request) {
        String header = request.getHeader("Authorization");
        if (header == null || ! header.startsWith("Bearer ")) {
            return null;
        }
//        request.getSession()
//        request.getMethod()
        String token = header.split(" ")[1];
        String username = JwtUtil.getUsername(token);
        UserDetails userDetails = null;
        try {
            userDetails = userDetailsService.loadUserByUsername(username);
        } catch (UsernameNotFoundException e) {
            return null;
        }
        if (! JwtUtil.verify(token, username, userDetails.getPassword())) {
            return null;
        }
        
        System.out.println();
        return new UsernamePasswordAuthenticationToken(userDetails, null, userDetails.getAuthorities());
    }
```
我們先看到request.getHeader(“Authorization”);  

header.startsWith("Bearer ") 不就是
# 請求 API

```
http://localhost:8080/user
```

![](https://i.imgur.com/eSLUZTd.png)

  

裡面我們夾帶過去的?  

這邊沒問題的話繼續往下看
```
String token = header.split(" ")[1];
        String username = JwtUtil.getUsername(token);
        UserDetails userDetails = null;
        try {
            userDetails = userDetailsService.loadUserByUsername(username);
        } catch (UsernameNotFoundException e) {
            return null;
        }
        if (! JwtUtil.verify(token, username, userDetails.getPassword())) {
            return null;
        }
        
        System.out.println();
        return new UsernamePasswordAuthenticationToken(userDetails, null, userDetails.getAuthorities());
```
我們編寫的 JwtUtil.getUsername(token);  

出現了  

我們根據我們的 token 取得 username  

JwtUtil.getUsername(token);
那麼  

userDetailsService.loadUserByUsername(username);  

這邊又代表我們拿著 username 去查 cache 有沒有 我的名字有的話 返回一個 userDetails 裡面含著 username 和 password 等等資料。
這邊就是用我們的 編寫工具 JwtUtil 去 verify 拿我們的 token 去解碼 根據我們的帳號 和密碼 檢查是否 密鑰正確  

JwtUtil.verify(token, username, userDetails.getPassword())
正確的話 返回 Authentication 也就是 認證成功的 token 回到  

doFilterInternal  

可以看到 認證成功後他會SecurityContextHolder.getContext().setAuthentication(token);  

分別是 阻擋 你繼續訪問 restful API 的地方。
那麼我們最初阻擋的地方在那裏呢?
# MainController

@PreAuthorize(“hasAuthority(‘ROLE_USER’)”)  

透過設置這些 就可以達到控制權限的目的了
```
@RestController
public class MainController {

    // 任何人都可以访问，在方法中判断用户是否合法
    @GetMapping("everyone")
    public ResponseEntity everyone() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (! (authentication instanceof AnonymousAuthenticationToken)) {
            // 登入用户
            return new ResponseEntity(HttpStatus.OK.value(), "You are already login", authentication.getPrincipal());
        } else {
            return new ResponseEntity(HttpStatus.OK.value(), "You are anonymous", null);
        }
    }

    @GetMapping("user")
    @PreAuthorize("hasAuthority('ROLE_USER')")
    public ResponseEntity user(@AuthenticationPrincipal UsernamePasswordAuthenticationToken token) {
        return new ResponseEntity(HttpStatus.OK.value(), "You are user", token);
    }

    @GetMapping("admin")
    @IsAdmin
    public ResponseEntity admin(@AuthenticationPrincipal UsernamePasswordAuthenticationToken token) {
        return new ResponseEntity(HttpStatus.OK.value(), "You are admin", token);
    }
    
    @GetMapping("/user/a")
    @PreAuthorize("hasAuthority('ROLE_USER')")
    public ResponseEntity user2(@AuthenticationPrincipal UsernamePasswordAuthenticationToken token) {
        return new ResponseEntity(HttpStatus.OK.value(), "fuck", token);
    }
}
```
# CustomErrorController

和統一管理 error 的地方 他把 錯誤路徑 導向自己的 /error ResponseEntity 統一做管理
```
@RestController
public class CustomErrorController implements ErrorController {

    @Override
    public String getErrorPath() {
        return "/error";
    }

    @RequestMapping("/error")
    public ResponseEntity handleError(HttpServletRequest request, HttpServletResponse response) {
        return new ResponseEntity(response.getStatus(), (String) request.getAttribute("javax.servlet.error.message"), null);
    }
}
```
這樣分析完有沒有 對 Spring security 更有一個概念，這樣的話 我們應該已經完成前後端分離，我們只剩下 部屬 到 tomcat server 我們就結束了!
  

![](https://i.imgur.com/63c0xov.png)
