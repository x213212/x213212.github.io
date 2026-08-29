---
title: "Spring Security 認證中心 重寫為 Redis cache 單台 (一)"
date: "2020-04-16T15:39:00.000+08:00"
updated: "2020-05-18T13:04:48.090+08:00"
permalink: "/2020/04/spring-security-redis-cache.html"
original_url: "https://x8795278.blogspot.com/2020/04/spring-security-redis-cache.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3764317131533006430"
tags: ["Redis", "spring boot", "Spring Cloud", "spring security", "Tutorial"]
layout: post
---

上次說要去重寫我們的 認證中心  

  

- jwt 結合 rsa
- 改為 redis 集群

# 驗證流程

也就是說我們的認證中心 以前的話會變成走這樣子的流程  

那麼的話就可以發現其實我們的授權中心壓力有點大  

網路上找到這幾種流程圖
# 普通 jwt

![](https://i.imgur.com/pKWlm3E.png)

1、用戶請求登錄  

2、Zuul將請求轉發到授權中心，請求授權  

3、授權中心校驗完成，頒發JWT憑證  

4、客戶端請求其它功能，攜帶JWT  

5、Zuul將JWT交給授權中心校驗，通過後放行  

6、用戶請求到達微服務  

7、微服務將JWT交給鑑權中心，鑑權同時解析用戶信息  

8、鑑權中心返回用戶數據給微服務  

9、微服務處理請求，返迴響應
# 結合 rsa

![](https://i.imgur.com/oi24l2Y.png)

1. 我們首先利用RSA生成公鑰和私鑰。私鑰保存在授權中心，公鑰保存在Zuul和各個微服務
2. 用戶請求登錄
3. 授權中心校驗，通過後用私鑰對JWT進行簽名加密
4. 返回JWT給用戶
5. 用戶攜帶JWT訪問
6. Zuul直接通過公鑰解密JWT，進行驗證，驗證通過則放行
7. 請求到達微服務，微服務直接用公鑰解析JWT，獲取用戶信息，無需訪問授權中心

可能只會有共同一組密鑰問題，不過這樣就不能進行分開鑑權了。  

![](https://i.imgur.com/9hy3QD8.png)

  

那我們只能這樣動刀了  

直接把 ehcache 換成 redis  

那麼授權中心就負責頒發 jwt，在zuul網關訪問服務的時候我們可以把緩存在 redis 的 password 和 username 拿來查詢  

假設查詢到代表在頒發jwt的時候 將會進行加密，用自己的密碼去加密，解密的時候將會解碼我們的jwt token 去解碼中間payloadJson 取得 我們的 username 再來就是拿我們的 username 再去查詢我們的 redis 看有沒有緩存，有的話代表已經登入過 那麼我們就可以直接去用我們的 username
> if (! JwtUtil.verify(token, username, userDetails.getPassword()))

拿我們傳過來的 token 配合 剛剛查詢的 username 在去從我們緩存在 userDetails 裡面的 password 再去重簽一次  

![](https://i.imgur.com/dktBMSA.png)

  

也就是說你偽造jwt也沒用，假設你沒登入過，你就不會緩存在 redis，你的token 又是透過你的 password 去簽的  

所以 偽造jwt 要先猜對你的 password 然後又要在你猜對帳號然後又已經登入帳號的時候 也就是 redis seession時間存活時，這樣才能剛好進去。
# SecurityConfiguration 新增 bean

- 新增 RedisTemplate
- 重寫我們的 SpringCacheBasedUserCache 為 springzzz
- 重寫 UserDetails 為 CustomUserDetails
- 傳入 RedisTemplate 去調用我們的 redis

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
    @Bean
    //指定我們的 redistemplate key 為 string value 為 CustomUserDetails
    public RedisTemplate<String, CustomUserDetails> redisTemplate(RedisConnectionFactory redisConnectionFactory) {
        RedisTemplate<String, CustomUserDetails> redisTemplate = new RedisTemplate<>();
        redisTemplate.setConnectionFactory(redisConnectionFactory);

        // 使用Jackson2JsonRedisSerialize 替换默认序列化
        Jackson2JsonRedisSerializer jackson2JsonRedisSerializer = new Jackson2JsonRedisSerializer(Object.class);

        ObjectMapper objectMapper = new ObjectMapper();
 //       objectMapper.setVisibility(PropertyAccessor.ALL, JsonAutoDetect.Visibility.ANY);
        objectMapper.enableDefaultTyping(ObjectMapper.DefaultTyping.NON_FINAL);
        ///
        //
        //
        //
        //
        //
        
        objectMapper.registerModule(new SimpleModule().addDeserializer(
                SimpleGrantedAuthority.class, new SimpleGrantedAuthorityDeserializer()));
        jackson2JsonRedisSerializer.setObjectMapper(objectMapper);

        // 设置value的序列化规则和 key的序列化规则
        redisTemplate.setKeySerializer(new StringRedisSerializer());
        redisTemplate.setValueSerializer(jackson2JsonRedisSerializer);
        redisTemplate.afterPropertiesSet();
        return redisTemplate;
    }
    @Autowired
    private    RedisTemplate<String, CustomUserDetails> redisTemplate;
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
    //在緩存 usercache 讀入我們的
    @Override
    protected void configure(AuthenticationManagerBuilder auth) throws Exception {
        // 对自己编写的 UserDetailsServiceImpl 进一步包装，实现缓存
        CachingUserDetailsService cachingUserDetailsService = cachingUserDetailsService(userDetailsServiceImpl);
        // jwt-cache 我们在 ehcache.xml 配置文件中有声明
        UserCache userCache = new springzz (cacheManager.getCache("jwt-cache"),  redisTemplate);
        
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
# SimpleGrantedAuthorityDeserializer

重寫 反向序列SimpleGrantedAuthorityDeserializer
```
class SimpleGrantedAuthorityDeserializer extends StdDeserializer<SimpleGrantedAuthority> {
    public SimpleGrantedAuthorityDeserializer() {
        super(SimpleGrantedAuthority.class);
    }
    @Override
    public SimpleGrantedAuthority deserialize(JsonParser p, DeserializationContext ctxt) throws IOException, JsonProcessingException {
        JsonNode tree = p.getCodec().readTree(p);
        return new SimpleGrantedAuthority(tree.get("authority").textValue());
    }
}
```
# springzzzz

使用構造好的 redistemplate  

這邊主要是控制 cache  

redisTemplate.opsForValue().set(customUserDetails.getUsername(),customUserDetails);
```
/*
 * Copyright 2002-2016 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.inlighting.security.security;

/**
 * Caches {@link UserDetails} instances in a Spring defined {@link Cache}.
 *
 * @author Marten Deinum
 * @since 3.2
 */
public class springzz implements UserCache {

 // ~ Static fields/initializers
 // =====================================================================================

 public static final Log logger = LogFactory.getLog(springzz.class);

 // ~ Instance fields
 // ================================================================================================
   
//  @Autowired
//     RedisTemplate<Object, Object> template ;
//  
//  @Bean
//     JedisConnectionFactory jedisConnectionFactory() {
//         return new JedisConnectionFactory();
//     }

  
//     @Bean
//     RedisTemplate< String, Object > redisTemplate() {
//         final RedisTemplate< String, Object > template =  new RedisTemplate< String, Object >();
//         template.setConnectionFactory( jedisConnectionFactory() );
//         template.setKeySerializer( new StringRedisSerializer() );
//      //   template.setHashValueSerializer( new GenericToStringSerializer< UserDetails >( UserDetails.class ) );
//    //     template.setValueSerializer( new GenericToStringSerializer< UserDetails >( UserDetails.class ) );
//
//
//         template.setValueSerializer(new springSessionDefaultRedisSerializer());
//         //template.setValueSerializer(new JsonRedisSerializer());
//
//         return template;
//     }
//  
//   @Bean
//      public RedisTemplate<Object, Object> redisTemplate(RedisConnectionFactory redisConnectionFactory) {
//          RedisTemplate<Object, Object> redisTemplate = new RedisTemplate<>();
//          redisTemplate.setConnectionFactory(redisConnectionFactory);
//
//          // 使用Jackson2JsonRedisSerialize 替换默认序列化
//          Jackson2JsonRedisSerializer jackson2JsonRedisSerializer = new Jackson2JsonRedisSerializer(Object.class);
//
//          ObjectMapper objectMapper = new ObjectMapper();
//   //       objectMapper.setVisibility(PropertyAccessor.ALL, JsonAutoDetect.Visibility.ANY);
//          objectMapper.enableDefaultTyping(ObjectMapper.DefaultTyping.NON_FINAL);
//
//          jackson2JsonRedisSerializer.setObjectMapper(objectMapper);
//
//          // 设置value的序列化规则和 key的序列化规则
//          redisTemplate.setKeySerializer(new StringRedisSerializer());
//          redisTemplate.setValueSerializer(jackson2JsonRedisSerializer);
//          redisTemplate.afterPropertiesSet();
//          return redisTemplate;
//      }
  
 public final Cache cache;
    public final RedisTemplate<String, CustomUserDetails> redisTemplate;
 // ~ Constructors
 // ===================================================================================================

 public springzz(Cache cache, RedisTemplate<String, CustomUserDetails> redisTemplate) throws Exception {
  Assert.notNull(cache, "cache mandatory");
  Assert.notNull(redisTemplate, "redisTemplate mandatory");
  this.redisTemplate = redisTemplate;
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
   System.out.println("no here"+username);
   return null;
  }
  else {
  System.out.println("im here");
     
  CustomUserDetails result = (CustomUserDetails) redisTemplate.opsForValue().get(username);
  System.out.println(result.getUsername());
   return (UserDetails) result;
//  return result;
  }
 }

 public void putUserInCache(UserDetails user) {
  if (logger.isDebugEnabled()) {
   logger.debug("Cache put: " + user.getUsername());
 
  }
//  System.out.println("Cache put:"+ user.getUsername());
//  System.out.println("Cache put:"+ user.getPassword());
//  System.out.println("Cache put:"+ user.getAuthorities());
  
  //UserDetails user2 = user;
  //重寫userdetails
  CustomUserDetails customUserDetails = new CustomUserDetails (user.getUsername(),user.getPassword(),user.getAuthorities());
 // Admin tmp = new CustomUserDetails(customUserDetails);
      System.out.println(customUserDetails.getUsername());
      System.out.println(customUserDetails.getAuthorities());
      
      redisTemplate.opsForValue().set(customUserDetails.getUsername(),customUserDetails);
         //原本opsForValue()是只能操作字符串的.现在就可以操作对象了
//         customUserDetails result = (customUserDetails) template.opsForValue().get(customUserDetails.getUsername()+"");
//         System.out.println(result.toString());
 // cache.put(user.getUsername(), user);
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
# 重寫後預設UserDetails

CustomUserDetails
```
@JsonSerialize
@JsonIgnoreProperties(ignoreUnknown = true)
public class CustomUserDetails extends Admin implements UserDetails {

    public CustomUserDetails() {
       super();
    }
//
//
    public CustomUserDetails(String username, String password, Collection<? extends GrantedAuthority> authorities) {
  // TODO Auto-generated constructor stub
     super( username, password, authorities);
 }
//
//    @Override
// public void setAuthorityList(Collection<? extends GrantedAuthority> authorityList) {
//        List<SimpleGrantedAuthority> listGrantedAuth = new ArrayList<>();
//        authorityList.forEach(auth -> {
//            listGrantedAuth.add(new SimpleGrantedAuthority(auth.toString()));
//        });
//        super.setAuthorityList(listGrantedAuth);
// }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        List<SimpleGrantedAuthority> listGrantedAuth = new ArrayList<>();
        super.getAuthorities().forEach(auth -> {
            listGrantedAuth.add(new SimpleGrantedAuthority(auth.toString()));
        });
        return listGrantedAuth;
    }
 

    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    @Override
    public boolean isAccountNonLocked() {
        return true;
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    @Override
    public boolean isEnabled() {
        return true;
    }

 @Override
 public String getPassword() {
  // TODO Auto-generated method stub
     return super.getPassword();
 }

 @Override
 public String getUsername() {
  // TODO Auto-generated method stub
  return super.getUsername();
 }
}
```
admin
```
public class Admin implements Serializable {

    private String username;
    private String password;
    private Collection<? extends GrantedAuthority> authorities;
    

 public Admin() {
  super();
  // TODO Auto-generated constructor stub
 }

 public Admin(String username, String password, Collection<? extends GrantedAuthority> authorities) {
  super();
  this.username = username;
  this.password = password;
  this.authorities = authorities;
 }

 public String getUsername() {
  return username;
 }
 public void setUsername(String username) {
  this.username = username;
 }
 public String getPassword() {
  return password;
 }
 public void setPassword(String password) {
  this.password = password;
 }

 public Collection<? extends GrantedAuthority> getAuthorities() {
  return authorities;
 }

    // default constructor

}
```
# 分析redis 分別存入重寫 CustomUserDetails 原本與預設UserDetails

原本與預設
# UserDetails

[“org.springframework.security.core.userdetails.User”,{“password”:"$2a1010AQol1A.LkxoJ5dEzS5o5E.QG9jD.hncoeCGdVaMQZaiYZ98V/JyRq",“username”:“jack”,“authorities”:[“java.util.Collections$UnmodifiableSet”,[[“org.springframework.security.core.authority.SimpleGrantedAuthority”,{“authority”:“ROLE_USER”}]]],“accountNonExpired”:true,“accountNonLocked”:true,“credentialsNonExpired”:true,“enabled”:true}]
# CustomUserDetails

[“org.inlighting.security.security.CustomUserDetails”,{“username”:“jack”,“password”:"$2a1010AQol1A.LkxoJ5dEzS5o5E.QG9jD.hncoeCGdVaMQZaiYZ98V/JyRq",“authorities”:[“java.util.ArrayList”,[[“org.springframework.security.core.authority.SimpleGrantedAuthority”,{“authority”:“ROLE_USER”}]]],“enabled”:true,“accountNonLocked”:true,“accountNonExpired”:true,“credentialsNonExpired”:true}]
預設 UserDetails
> Could not read JSON: Cannot construct instance of `org.springframework.security.core.authority.SimpleGrantedAuthority` (although at least one Creator exists):

No Creators, like default construct, exist): cannot deserialize from Object value (no delegate- or property-based Creator
報錯
# 分別原因

1. construct 忘記加 建構元
2. SimpleGrantedAuthority  不能進行反向序列org.springframework.core.codec.DecodingException: JSON decoding error: Cannot construct instance of org.springframework.security.core.authority.SimpleGrantedAuthority (although at least one Creator exists): cannot deserialize from Object value (no delegate- or property-based Creator);  
   
  我們的org.springframework.security.core.authority.SimpleGrantedAuthority 不能透過 json  
   
  <https://blog.csdn.net/m0_37893932/article/details/78259288>  
   
  進行反向序列。  
   
  <https://blog.csdn.net/weixin_34402408/article/details/92134715>

<https://rusyasoft.github.io/spring-security/2019/01/14/spring-security-session-redis-json/>  

  

![](https://i.imgur.com/Iwowkzg.png)

  

![](https://i.imgur.com/SbE3ShF.png)

![](https://i.imgur.com/APineku.png)

  

  

  

到此我們的 改動 ehcache 就改為 redis 接下來就是看 RedisTemplate 如何去讀 redis集群 (應該蠻簡單?  

也就是說我們把 db 的 二級緩存 ehcache 換成我們的 redis
新的問題來，我們的認證中心，是否可以換成集群，只要確保我們的 redis session 共享就可以了吧! 過幾天再來重構成 集群版。
