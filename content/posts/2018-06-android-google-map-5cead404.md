---
title: "Android google map 路徑規劃與估計到達時間(一)"
date: "2018-03-06T18:00:00.000+08:00"
updated: "2018-09-05T07:46:03.403+08:00"
permalink: "/2018/06/android-google-map.html"
original_url: "https://x8795278.blogspot.com/2018/06/android-google-map.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2295703195370379508"
tags: ["Android", "Tutorial"]
layout: post
---

## 戰前Android工程師預備

在18號之前由於要去日本6天所以呢8號和9號要回家，所以呢剩今天有空，18號正式簽約在看了案子的內容可能要稍微複習一下以前的技能和了解新技能，學校教的到底有沒有用呢，公司給我的期限是四個月。  

  

## 案子大約內容

---

- 登入
- 註冊
- Google map
- 銀行Api串接
- 預約服務

## 目前作法（自己推測做法）

---

- 在登入的介面呢我想加入註冊的按鈕
- 然後使用google按鈕做一鍵登入（應該會用安卓就有google帳號了）
- 在銀行Api方面尚未接觸到所以暫且不做
- 預約服務可能是想透過銀行轉帳後再者掛入資料庫做預約的處理
- 可能後台方面要用網頁做

## 詢問工程師（尚未問）

---

- 想問在api串接的時候，透過普通的網頁傳遞資料是否會發生安全性問題
- 各個介面的連續串接與微調
- 後台方是否要以網頁內容來做

## 8:52AM

---

也差不多忘記了安桌在開發上的一些技巧先來建專案吧  

套入原生地login登入介面　ps.懶得拉介面  

[![](https://i.imgur.com/rmtkCpK.png)](https://i.imgur.com/rmtkCpK.png)  

再加入一個空的原生介面  

[![](https://i.imgur.com/ctx07mw.png)](https://i.imgur.com/ctx07mw.png)  

並取名為registerActivity  

[![](https://i.imgur.com/6uCcq2h.png)](https://i.imgur.com/6uCcq2h.png)  

我有拉了一個button1在LoginActivitybut1= (Button) findViewById(R.id.button1);but1.setOnClickListener(new OnClickListener() {  

@Override public void onClick(View view) {  

register(); }  

});  

  

所以呢這是一個按鈕的呼叫，我寫了一個register()函式去做處理（不能隨便亂命名了呢private void register()  

{  

Intent intent = new Intent(); intent.setClass(LoginActivity.this, registerActivity.class); startActivity(intent); LoginActivity.this.finish();}  

  

然後可以發現這邊是做另一個介面的呼叫好的我們來看registerActivity  

裡面的程式碼在幹嘛  

[![](https://i.imgur.com/7SKaHxK.png)](https://i.imgur.com/7SKaHxK.png)  

沒錯非常的空我們來加上一條程式碼  

setTitle("register");  

  

更改該目標視窗為regitster  

然後目前我們程式已經到這裡了  

[![](https://i.imgur.com/iiUKFF9.png)](https://i.imgur.com/iiUKFF9.png)[![](https://i.imgur.com/GzqMhIv.png)](https://i.imgur.com/GzqMhIv.png)  

然後接下來呢我們要再拉一個介面算是主視窗  

[![](https://i.imgur.com/nDS1bGE.png)](https://i.imgur.com/nDS1bGE.png)  

我選這個看起來比較潮  

[![](https://i.imgur.com/1uE39gf.png)](https://i.imgur.com/1uE39gf.png)  

[![](https://i.imgur.com/IWHiB2s.png)](https://i.imgur.com/IWHiB2s.png)  

好了所以我們有這個介面了  

[![](https://i.imgur.com/sGjljdL.png)](https://i.imgur.com/sGjljdL.png)  

根據這裡的程式碼我們做一下追蹤attemptLogin();  

  

[![](https://i.imgur.com/gZgLtKe.png)](https://i.imgur.com/gZgLtKe.png)mAuthTask = new UserLoginTask(email, password);  

  

持續追  

[![](https://i.imgur.com/azX7P1u.png)](https://i.imgur.com/azX7P1u.png)  

初步判定登入成功的話將開啟畫面Thread.sleep(2000);  

  

我們可能會去讀取資料庫的這段程式碼寫在這邊去跟資料庫去做要資料比對程式寫在這  

[![](https://i.imgur.com/Afd5Z8B.png)](https://i.imgur.com/Afd5Z8B.png)  

Intent intent = new Intent();intent.setClass(LoginActivity.this, MainActivity.class);startActivity(intent);LoginActivity.this.finish();  

  

後者改成MainActivity  

確實可以登入到該主畫面了  

[![](https://i.imgur.com/bVyNnm1.png)](https://i.imgur.com/bVyNnm1.png)  

然後接下來這畫面該怎樣搭建呢我目前想用Table然後進行切換  

[![](https://i.imgur.com/GJavzGS.png)](https://i.imgur.com/GJavzGS.png)  

繼續追我們可以發現我們的主體在content_main  

[![](https://i.imgur.com/dDZUqRz.png)](https://i.imgur.com/dDZUqRz.png)  

然後呢接下來我想怎樣做目前  
## 9:19AM

---

![](https://i.imgur.com/eSi43Mj.png)

  

然後我們暫且把她取名子為table1，跑看看因為我記得這蠻麻煩得
  
## 起身懶腰

---

  
找tablewidget的資料  

<http://www.viralandroid.com/2015/09/simple-android-tabhost-and-tabwidget-example.html>  

  

  

所以呢在主體先宣告tableweidge  

  

[![](https://i.imgur.com/JrLzLqu.png)](https://i.imgur.com/JrLzLqu.png)  

[![](https://i.imgur.com/i5Urgi7.png)](https://i.imgur.com/i5Urgi7.png)  

算初始化之類的吧  

好像可以喔  

[![](https://i.imgur.com/w1YMexI.png)](https://i.imgur.com/w1YMexI.png)  

<http://www.learn-android-easily.com/2013/07/android-tabwidget-example.html>  

[![](https://i.imgur.com/ap8mWx9.png)](https://i.imgur.com/ap8mWx9.png)  

恩．．．還是錯呢ｄｅｕｂｇ地域開始  

[![](https://i.imgur.com/gmcMp7U.png)](https://i.imgur.com/gmcMp7U.png)  

[![](https://i.imgur.com/vqVODj5.png)](https://i.imgur.com/vqVODj5.png)  

有問題阿怎麼辦呢  

[![](https://i.imgur.com/pv4kOC2.png)](https://i.imgur.com/pv4kOC2.png)  

<http://blog.csdn.net/zingck/article/details/7454316>  

[![](https://i.imgur.com/2YVpehd.png)](https://i.imgur.com/2YVpehd.png)

## 11:01AM

---

[![](https://i.imgur.com/6BGl5vP.png)](https://i.imgur.com/6BGl5vP.png)  

找到一個方法不用移除titlebar  

[![](https://i.imgur.com/an5kszM.png)](https://i.imgur.com/an5kszM.png)[![](https://i.imgur.com/XDNvxIq.png)](https://i.imgur.com/XDNvxIq.png)[![](https://i.imgur.com/RQnnZke.png)](https://i.imgur.com/RQnnZke.png)  

  

  

這樣子一來應該就可以切換各種頁面了，然後接下來要處理的是可能的東西
  

## Google Map的引入

---

<https://youtu.be/CCZPUeY94MU>  

找到了這網站可以下載裡面的原始碼我們來進行一下移植手術  

[![](https://i.imgur.com/bQdrUJ1.png)](https://i.imgur.com/bQdrUJ1.png)  

這邊的話可以看到這專案已經有完成一堆功能了現在來進行移植  

GoogleMap方面我以前有做過如何申請apikey所以呢我們來看一下  

[![](https://i.imgur.com/yRx7Hvx.png)](https://i.imgur.com/yRx7Hvx.png)  

這裡是apikey，等正式開工我可能會替換這裡  

掀開一個Google Map activity  

[![](https://i.imgur.com/n62XvQP.png)](https://i.imgur.com/n62XvQP.png)  

系統可能幫你載入一些原件  

[![](https://i.imgur.com/FbeMvyw.png)](https://i.imgur.com/FbeMvyw.png)  

注意ａｐｉｋｅｙ　暫且用他的  

[![](https://i.imgur.com/6GHoOaF.png)](https://i.imgur.com/6GHoOaF.png)  

[![](https://i.imgur.com/mkIoPi3.png)](https://i.imgur.com/mkIoPi3.png)  

由於他設計ｕｉ太精美所以先用他的ｉｃｏ檔ｄｒａｗｂｌｅ全部複製過去  

[![](https://i.imgur.com/dIDCVXE.png)](https://i.imgur.com/dIDCVXE.png)  

可以發現  

[![](https://i.imgur.com/FJcQsHy.png)](https://i.imgur.com/FJcQsHy.png)  

ｍａｐ部分已經進行移植了現在我們再來加仔一下  

[![](https://i.imgur.com/Rp1WBIH.png)](https://i.imgur.com/Rp1WBIH.png)  

[![](https://i.imgur.com/QkdjcPF.png)](https://i.imgur.com/QkdjcPF.png)  

然後可以發現沒東西，是因為我記得ａｐｉ　ｋｅｙ　要根據專案名稱申請才可以使用  

所以來小回顧囉  

後來好像發現以前申請過後了  

[![](https://i.imgur.com/xQ2fPut.png)](https://i.imgur.com/xQ2fPut.png)  

好像是右下角的小圈圈的問題  

[![](https://i.imgur.com/jHOQmln.png)](https://i.imgur.com/jHOQmln.png)  

我們把它挖掉看看  

[![](https://i.imgur.com/d9ywb5E.png)](https://i.imgur.com/d9ywb5E.png)  

  

<https://stackoverflow.com/questions/26265526/what-makes-my-map-fragment-loading-slow>
## 睡午覺靈感時間6hr

---

  

## 9:05PM

---

感，初步判斷navigationView跟我的tabhost  

已經耗掉我4小時Debug囉卡到衝突，然後我想換個方式呈現  

  

[![](https://i.imgur.com/KAlbyqM.png)](https://i.imgur.com/KAlbyqM.png)[![](https://i.imgur.com/YHR4eWv.png)](https://i.imgur.com/YHR4eWv.png)  

  

  

<https://youtu.be/Cy4EraxUan4>  

然後呢  

[![](https://i.imgur.com/wjVss61.png)](https://i.imgur.com/wjVss61.png)  

先把tabhost槓掉  

<https://developers.google.com/maps/documentation/distance-matrix/get-api-key?hl=zh-tw>  

  

[![](https://i.imgur.com/7XU1bhv.png)](https://i.imgur.com/7XU1bhv.png)  

[![](https://i.imgur.com/5mJCsnW.png)](https://i.imgur.com/5mJCsnW.png)  

[![](https://i.imgur.com/rTvN6BU.png)](https://i.imgur.com/rTvN6BU.png)點選啟用  

  

[![](https://i.imgur.com/AH9mfMY.png)](https://i.imgur.com/AH9mfMY.png)  

[![](https://i.imgur.com/868aIZf.png)](https://i.imgur.com/868aIZf.png)可以看到下面已經啟用  

  

[![](https://i.imgur.com/ouFYv2s.png)](https://i.imgur.com/ouFYv2s.png)  

## 0:20

---

同學水管爆了，來找我聊天搶球鞋程式改日來寫一下好了  

ps.學校雲端網路每秒500mb的速度，應該亞於大公司ㄎㄎ  

算是把草案給弄出來了  

剩下的就是預約系統  

和透過json去跟資料庫要資料  

再新增一些map 附近地標搜尋  

  

話說我是不是少賺了200kxd
