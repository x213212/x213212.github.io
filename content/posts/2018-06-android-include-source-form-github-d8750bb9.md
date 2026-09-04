---
title: "Android include source form github (exoplayer) add funaction"
date: "2018-04-23T15:15:00.000+08:00"
updated: "2018-09-05T07:46:03.515+08:00"
permalink: "/2018/06/android-include-source-form-github.html"
original_url: "https://x8795278.blogspot.com/2018/06/android-include-source-form-github.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5172152772605441995"
tags: ["Android", "Tutorial"]
layout: post
---

## 引用

---

當一個專案只能透過，但又想改裡面的函數怎麼辦？  

下面會來用一個例子從引用到，修改其函數與新增  
com.google.android.exoplayer:exoplayer-ui:r2.7.4  

[![](https://i.imgur.com/2LtlJFI.png)](https://i.imgur.com/2LtlJFI.png)  

但是當你要修改裡面的源碼要怎麼辦呢?
## Java 反射調用(x)

---

  

```java
反射調用可以訪問並且修改其private的變數與方法
public class Private 
{ 
private String name = "张三"; 

private String getName() 
{ 
return name; 
} 
} 
package com.wangzhuo.reflect; 

import java.lang.reflect.Constructor; 
import java.lang.reflect.Field; 
import java.lang.reflect.Method; 

public class PrivateTest 
{ 
public static void main(String[] args)throws Exception 
{ 
//获取Private类的Class对象 
Class<?> classType = Class.forName("com.wangzhuo.reflect.Private"); 　＜－－目標如果是ｊａｒ等等之類的 

//获取其构造方法对应的Constructor对象 
Constructor con = classType.getDeclaredConstructor(new Class[]{}); 

//创建Private的对象 
Object object =con.newInstance(new Object[]{}); 

//获取Private类中name属性对应的Field对象 
Field field = classType.getDeclaredField("name"); ＜－－field是變數

//设置避开java访问控制检测 
field.setAccessible(true); 

//获取修改前的值 
Object str = field.get(object); 

System.out.println("修改之前name的值："+(String)str); 

//给name属性赋值 
field.set(object, "李四"); 

//获取getName方法对应的Method对象 
Method getNameMethod = classType.getDeclaredMethod("getName", new Class[]{}); ＜－－Method是方法 

//设置避开java访问控制检测 
getNameMethod.setAccessible(true); 

//调用方法，返回值 
Object o = getNameMethod.invoke(object, new Object[]{}); 
System.out.println("修改之后name的值："+(String)o); 
} 
} 
----------------------------------------
mAudioTrack =null;

try
{

Class<?> bookClass = Class.forName("com.google.android.exoplayer2.audio.DefaultAudioSink");//完整类名
Log.i("qsss",bookClass.getSimpleName());
Object book = bookClass.newInstance();//获得实例
Field getAuthor = bookClass.getDeclaredField("audioTrack");//获得私有方法
getAuthor.setAccessible(true);//调用方法前，设置访问标志

mAudioTrack = (AudioTrack) getAuthor.get(book);//使用方法
}
catch (Exception e)
{
e.printStackTrace();
}


mAudioTrack.setStereoVolume(0f,1f);
```

失敗＝　＝　可能要用下面方法引用在進行調用，才會成功改天再測試  

  

  

這邊簡單帶過，知道有這方法就好，大家自己去研究  
## Github取得舊的原始碼

---

[![](https://i.imgur.com/itXfIMU.png)](https://i.imgur.com/itXfIMU.png)  

  

[![](https://i.imgur.com/oJgjyHF.png)](https://i.imgur.com/oJgjyHF.png)  

這邊就可以嚕～  

## 新增一個funaction?

---

可不可行?當然可以　  

[![](https://i.imgur.com/RO5EU4Y.png)](https://i.imgur.com/RO5EU4Y.png)  

<https://github.com/google/ExoPlayer/>  

compile 'com.google.android.exoplayer:exoplayer:2.7.3　　　＜－－卡頓  

[![](https://i.imgur.com/BEHwNkv.png)](https://i.imgur.com/BEHwNkv.png)  

<https://github.com/yusufcakmak/ExoPlayerSample>  

compile 'com.google.android.exoplayer:exoplayer:r2.5.1　　＜－－卡頓  

找來找去還是一樣同一個source code，但是為什麼，後者執行沒問題，最新版執行卻是卡頓呢？  

大家第一個反應可能是函數有問題，會先降等級所以我就先降等級  

[![](https://i.imgur.com/gfXD6QB.png)](https://i.imgur.com/gfXD6QB.png)  

起初以為是build Tools version 有問題所以有四種可能性  

套件版本有問題　編譯器版本過高  

套件版本沒問題　編譯器版本過高  

套件版本沒問題　編譯器版本正常  

套件版本有問題　編譯器版本正常  

這邊全部試下來發現  

2.7.3編譯的時候　需要build Tools version為27 而且　compile 要改成implementation  

r2.5.1編譯的時候　build Tools version預設為25 條至27　也沒問題　  

初步判斷為　套件版本有問題  

這樣看來我們是要用下面的r2.5.1做為開發的基底了  

  

  

  

反射調用沒用的話怎麼辦?  

這時候就要把源碼弄到本地端進行程式碼修改了  

[![](https://i.imgur.com/TpsXJTb.png)](https://i.imgur.com/TpsXJTb.png)  

大家等級都很高我就不說怎樣調用了  

[![](https://i.imgur.com/Xk1aR5p.png)](https://i.imgur.com/Xk1aR5p.png)  

path的資料夾地點  

這時候我把r2.5.1，又生到了2.73　這時候很奇怪這個時候的話我在r2.51 build app 卻也沒發生問題?  

  

  

為了求證我們把兩個版本替換到我總共替換兩個  

2.73　失敗  

2.6 　成功  

2.54　成功(不考慮後續會說位啥不用  

引用成功後  

  

  

小插曲  

import com.google.android.exoplayer2.source　xxx有一個hls的包遺失，我們把她槓掉就沒事了  

  

  

當一個專案只能透過　  

深入解析  

當要修改別人的源碼呢，挖個link，上看千行怎麼辦?  

[![](https://i.imgur.com/N8eaKPh.png)](https://i.imgur.com/N8eaKPh.png)  

這邊可以做整個資源的搜尋，我們可以透過這個搜尋我們要尋找的某個程式碼片段  

大家可以看到我那時要開發一個升降key的，後來又發現要切換聲道，後來慢慢拆解後發現  

她是透過一層一層呼叫，各種神呼叫  

[![](https://i.imgur.com/3jHbG1F.png)](https://i.imgur.com/3jHbG1F.png)  

[![](https://i.imgur.com/C6Tnfjk.png)](https://i.imgur.com/C6Tnfjk.png)  

[![](https://i.imgur.com/13vNnea.png)](https://i.imgur.com/13vNnea.png)  

  

  

挖，要改到死诶，還不一定對，所以呢我們要盡量避開這種大改，我們小改就好  

在不破壞原先結構的函數，我們盡量找小的地方改就好所以呢？  

![](https://i.imgur.com/N8eaKPh.png)

  

setVolume 我們就單弄這幾個函數就好  

我們嘗試把它弄成  

setVolume2   

[![](https://i.imgur.com/2OE1NLz.png)](https://i.imgur.com/2OE1NLz.png)  

[![](https://i.imgur.com/1yFYqGl.png)](https://i.imgur.com/1yFYqGl.png)  

[![](https://i.imgur.com/EYYNKWx.png)](https://i.imgur.com/EYYNKWx.png)  

[![](https://i.imgur.com/LPc1s9n.png)](https://i.imgur.com/LPc1s9n.png)  

[![](https://i.imgur.com/tq2jstc.png)](https://i.imgur.com/tq2jstc.png)  

[![](https://i.imgur.com/nEWjFdc.png)](https://i.imgur.com/nEWjFdc.png)  

動這六個檔案，我們就可以產生一個函數了，為什麼要用這樣呢，因為我要改裡面  

AudioTrack裡面有一個函數  

原本是  

setVolume(volume);  

但是我要用下面的  

setStereoVolume(volume, volume2);  

  

  

可以切換左右聲道，需要傳遞兩個變數，可以看到  

handleMessage(int messageType, Object message) throws ExoPlaybackException {  

可能要改成  

handleMessage(int messageType, Object message, Object message) throws ExoPlaybackException {  

  

  

我以為Object可以傳遞陣列　結果也不行，懶得改的結果就想到了這個方法  

那麼我只要  

setVolume2(volume);  

this.volume2=volume  

存入class變數就好  

-----------------------------  

setVolume(volume);  

this.volume=volume  

的時候將會調用  

setStereoVolume(volume, volume2);  

這樣的話就可以切換左右聲道了  

[![](https://i.imgur.com/831VBwI.png)](https://i.imgur.com/831VBwI.png)  

源碼就不提供囉，保密(o  
## 為什麼不引用原先的r2.53的?

---

[![](https://i.imgur.com/FZiCcB2.png)](https://i.imgur.com/FZiCcB2.png)  

  

  

原先的缺少該目標DefaultAudioSink，沒辦法找到AudioTrack進行的修改
