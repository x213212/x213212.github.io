---
title: "微服務購物網站小紀錄 (一) 微服務授權中心預計優化"
date: "2020-04-11T13:15:00.001+08:00"
updated: "2020-04-12T15:37:24.209+08:00"
permalink: "/2020/04/blog-post.html"
original_url: "https://x8795278.blogspot.com/2020/04/blog-post.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6727664091867928001"
tags: ["Spring Cloud", "Tutorial"]
layout: post
---

參與規劃的時候遇到兩個功能，來小複習一下  

以Vue.js 和 spring boot實作後，後續可以根據下列功能進行優化  

離開公司一陣子又被叫回去開 遠端醫療的會議!?，順便問有沒有要外包好了。  

  

- SSO 單點登入前後端分離
- 綠界科技物流串接
- Elasticsearch 搜尋引擎  
  …

# 微服務授權中心預計優化

- 更改 Ehcache為 redis 集群
- 授權中心由後端頒發 cookise

後面想到再來這裡擴增，今天來複習一下 SSO單點登入那後續補足一些可優化的地方，先來用嘴巴寫程式一下。  

之前有透過我們  

<https://x8795278.blogspot.com/2019/12/spring-boot-spring-security-rest-api.html>  

最後發現其實在分析整個流程的時候發現只有在login 的時候 有實現二級快取，在戳api的時候 沒有呼叫springboot 預設的 cache 也就是Ehcache，後面 我有額外 去 仿造一個 UserCache 也就是 springzzz  

![](https://i.imgur.com/AAu8gLX.png)

  

![](https://i.imgur.com/r7WBHB1.png)

  

可以發現UserCache 裡面 其實就是去呼叫我們的 預設的 Ehcache， 在 單點登入得時候 我在想是否可以直接把這個地方抽出來 用 redis 去做集群呢?  

<https://zhuanlan.zhihu.com/p/64366902> 這是 對比
# Ehcache

在Java项目广泛的使用。它是一个开源的、设计于提高在数据从RDBMS中取出来的高花费、高延迟采取的一种缓存方案。正因为Ehcache具有健壮性（基于java开发）、被认证（具有apache 2.0 license）、充满特色（稍后会详细介绍），所以被用于大型复杂分布式web application的各个节点中。
什么特色？

1. 够快

Ehcache的发行有一段时长了，经过几年的努力和不计其数的性能测试，Ehcache终被设计于large, high concurrency systems.

2. 够简单

开发者提供的接口非常简单明了，从Ehcache的搭建到运用运行仅仅需要的是你宝贵的几分钟。其实很多开发者都不知道自己用在用Ehcache，Ehcache被广泛的运用于其他的开源项目
比如：hibernate
3.够袖珍
关于这点的特性，官方给了一个很可爱的名字small foot print，一般Ehcache的发布版本不会到2M，V 2.2.3 才 668KB。

4. 够轻量

核心程序仅仅依赖slf4j这一个包，没有之一！
5.好扩展
Ehcache提供了对大数据的内存和硬盘的存储，最近版本允许多实例、保存对象高灵活性、提供LRU、LFU、FIFO淘汰算法，基础属性支持热配置、支持的插件多
6.监听器
缓存管理器监听器 （CacheManagerListener）和 缓存监听器（CacheEvenListener）,做一些统计或数据一致性广播挺好用的
如何使用？
够简单就是Ehcache的一大特色，自然用起来just so easy!
# redis

Redis是在memcache之后编写的，大家经常把这两者做比较，如果说它是个key-value store 的话但是它具有丰富的数据类型，我想暂时把它叫做缓存数据流中心，就像现在物流中心那样，order、package、store、classification、distribute、end。现在还很流行的LAMP PHP架构 不知道和 redis+MySQL 或者 redis + MongoDB的性能比较（听群里的人说mongodb分片不稳定）。
先说说reidis的特性

1. 支持持久化

redis的本地持久化支持两种方式：RDB和AOF。RDB 在redis.conf配置文件里配置持久化触发器，AOF指的是redis没增加一条记录都会保存到持久化文件中（保存的是这条记录的生成命令），如果不是用redis做DB用的话还会不要开AOF，数据太庞大了，重启恢复的时候是一个巨大的工程！
2.丰富的数据类型
redis 支持 String、Lists、sets、sorted sets、hashes 多种数据类型，新浪微博会使用redis做nosql主要也是它具有这些类型，时间排序、职能排序、我的微博、发给我的这些功能List 和 sorted set
的强大操作功能息息相关
3.高性能
这点跟memcache很想象，内存操作的级别是毫秒级的比硬盘操作秒级操作自然高效不少，较少了磁头寻道、数据读取、页面交换这些高开销的操作！这也是NOSQL冒出来的原因吧，应该是高性能
是基于RDBMS的衍生产品，虽然RDBMS也具有缓存结构，但是始终在app层面不是我们想要的那么操控的。
4.replication
redis提供主从复制方案，跟mysql一样增量复制而且复制的实现都很相似，这个复制跟AOF有点类似复制的是新增记录命令，主库新增记录将新增脚本发送给从库，从库根据脚本生成记录，这个过程非常快，就看网络了，一般主从都是在同一个局域网，所以可以说redis的主从近似及时同步，同事它还支持一主多从，动态添加从库，从库数量没有限制。 主从库搭建，我觉得还是采用网状模式，如果使用链式（master-slave-slave-slave-slave·····）如果第一个slave出现宕机重启，首先从master 接收 数据恢复脚本，这个是阻塞的，如果主库数据几TB的情况恢复过程得花上一段时间，在这个过程中其他的slave就无法和主库同步了。
5.更新快
这点好像从我接触到redis到目前为止 已经发了大版本就4个，小版本没算过。redis作者是个非常积极的人，无论是邮件提问还是论坛发帖，他都能及时耐心的为你解答，维护度很高。有人维护的话，让我们用的也省心和放心。目前作者对redis 的主导开发方向是redis的集群方向。
redis的安装
redis的安装其实还是挺简单的，总的来说就三步：下载tar包，解压tar包，安装。
不过最近我在2.6.7后用centos 5.5 32bit 时碰到一个安装问题，下面我就用图片分享下安装过程碰到的问题，在redis 文件夹内执行make时有个如下的错 undefined reference to ‘__sync_add_and_fetch_4’
# 應用場景

ehcache直接在jvm虚拟机中缓存，速度快，效率高；但是缓存共享麻烦，集群分布式应用不方便。  

redis是通过socket访问到缓存服务，效率比ecache低，比数据库要快很多，处理集群和分布式缓存方便，有成熟的方案。
如果是单个应用或者对缓存访问要求很高的应用，用ehcache。  

如果是大型系统，存在缓存共享、分布式部署、缓存内容很大的，建议用redis。
补充下：ehcache也有缓存共享方案，不过是通过RMI或者Jgroup多播方式进行广播缓存通知更新，缓存共享复杂，维护不方便；简单的共享可以，但是涉及到缓存恢复，大数据缓存，则不合适。  

————————————————  

版权声明：本文为CSDN博主「王卫东」的原创文章，遵循 CC 4.0 BY-SA 版权协议，转载请附上原文出处链接及本声明。  

原文链接：<https://blog.csdn.net/wwd0501/java/article/details/79229176>
# 再來就是 我們的 cookies

<https://www.mofish.work/thread/13310>  

<https://zhuanlan.zhihu.com/p/42918845>  

預設前後端分離：
登入  

前端請求 => 後端生成 token => 回應前端 => 前端多頁面則存到 localStorage  

退出登入  

前端請求 => 後端把 token 加入黑名單 => 回應前端 => 前端清楚 localStorage
沒有 token->進入登入失效流程  

有 token->訪問介面->介面返回 token 已失效->進入登入失效流程.
一般來說頁面的轉換都會伴隨網路請求，所以並不是每一次互動都檢查 token,都是和網路請求一起發生的.這樣就足夠了.主動退出時前端自己清掉 token 就行了.
綜合這些原因可以知道 我們只要把每次請求 都夾帶我們的 cookies 應該就行了吧。
也就是說 應該由後端去返回 給我們前端的 cookies 那麼我們要從  

jwt 檢測這個地方

![](https://i.imgur.com/7TwfzyP.png)

再來就是我們 login 的 response  

![](https://i.imgur.com/k6tSj5C.png)

  

這些地方都可以 返回 TOKEN
那麼我們設計的架構是  

![](https://i.imgur.com/i2p5d4v.png)

  

這樣子的話我們的認證中心以後可以拓展成集群，不過架設我們用 redis 的話 如同之前說的就是要 去做一個 session 共享的問題 <https://blog.csdn.net/qq_34561892/article/details/84921449>  

也有可能遇到 廣播風暴等等
# zuul 網關

那麼每次請求我們都會往 zuul 去做請求  

![](https://i.imgur.com/nZDATzj.png)

可以發現我其實是先去 訪問我們的 授權中心 確認攜帶的 token 是否有用 再來就是允許我們的 zuul 再讓他訪問 其他微服務 不知道這個設計架構有沒有問題這樣。  

![](https://i.imgur.com/xzWye58.png)

  

可以看到我之前是偷懶夾在 header 如果講求安全應該不開放讓 前端去寫我們的 後端 cookies http only?
# cookies 跨網域

<https://www.jianshu.com/p/d9b1c859bc99?fbclid=IwAR2_XMFaOtnsDTpuPL7bQg2CYuOx0xZ2cTNoC4Zkgm5rxmOZZi76g5kvyBM>  

可以發現就是說  

cookies 在同一個網域下可以去做一個共享也就是說
> [www.onmpw.com/site1](http://www.onmpw.com/site1)  
>
> [www.onmpw.com/site2](http://www.onmpw.com/site2)

# cookies 二級網域

> [sub1.onmpw.com](http://sub1.onmpw.com/)  
>
> [sub2.onmpw.com](http://sub2.onmpw.com/)

這樣的話我們可以通過設置 ##setDomain##
> cookie.setDomain(".onmpw.com");

理應就會達成我們 前端 cookies 共享  

或者呢可以考慮用 porxy 去代理成 同一個主網域?
# 前端封裝 axios

![](https://i.imgur.com/kKw50AS.png)

  

可以看到我們這一行  

axios.defaults.withCredentials=true;//讓 ajax 帶 cookie  

讓我們前端 在呼叫api 的時候 自動攜帶上我們的 cookies
# 後端跨域

![](https://i.imgur.com/Tt5xXR8.png)

  

這個可能就是要改多個 子網域  

<https://stackoverflow.com/questions/39623211/add-multiple-cross-origin-urls-in-spring-boot>  

… 大概要考慮上述這些，有空再改!
