---
title: "Android GoogleMap Key申請 和定位"
date: "2018-08-26T13:54:00.002+08:00"
updated: "2018-09-05T07:45:41.919+08:00"
permalink: "/2018/08/android-googlemap-key.html"
original_url: "https://x8795278.blogspot.com/2018/08/android-googlemap-key.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5318795331371155307"
tags: ["Android", "Tutorial"]
layout: post
---

# Android GoogleMap Key申請 和定位

執行畫面  

![](https://i.imgur.com/9iGaypc.png)

打開  

[android studio](https://developer.android.com/studio/index.html)

![](https://i.imgur.com/dMJqkk0.png)

  

已經進入專案 new一個新專案

![](https://i.imgur.com/tP44eck.png)

  

老樣子下一步

![](https://i.imgur.com/mcEygCV.png)

  

這選大眾用 4.03
這邊可以選擇

![](https://i.imgur.com/u5QDy0H.png)

這邊選google Map 表單  

![](https://i.imgur.com/o0xkc4h.png)

  

![](https://i.imgur.com/DdVToUW.png)

![](https://i.imgur.com/ptFkTmy.png)

有看到你們專案??  

![](https://i.imgur.com/HdXlGLX.png)

# 產生金鑰

被反白這條把它複製下來貼到你的垃圾瀏覽器
用google 帳號登入  

![](https://i.imgur.com/tHgZAIj.png)

![](https://i.imgur.com/DMXOiA2.png)

  

這邊點繼續
好了以後  

![](https://i.imgur.com/KOb8Dss.png)

按下建立api金鑰
這邊會產生一把金鑰  

![](https://i.imgur.com/kCL8wA7.png)

  

把它複製下來  

AIzaSyDNyN…ksRg  

你們複製你們的  

等等跟你們獎  

![](https://i.imgur.com/ljeLTe6.png)

  

這邊貼上你們的key
回到這邊  

![](https://i.imgur.com/xvzN3sI.png)

  

這邊你有看到剛剛那畫面 右下角有一個限制金鑰  

把它點下去

![](https://i.imgur.com/xGd5JhC.png)

  

這邊點選android 應用程式
這邊可以看到  

![](https://i.imgur.com/FC5iECF.png)

  

程式碼已經幫你產生好了  

DC:47:4E:F0:AD:26:81:24:9C:EB:54:34:56:3B:B7:28:07:1E:B5:2D;com.example.x2132.myapplication  

程式的package名稱 和一組sha1
好了按儲存 這邊別人要用你的key的話
sha1 值 跟 packet name 錯誤除非他程式 package name 跟你取一樣  

就沒辦法去呼叫google api  

你開起來會空白

![](https://i.imgur.com/sG68ws2.png)

切到這裡
# 設定程式經緯度

![](https://i.imgur.com/KC0ZsRO.png)

MapsActivity.java
```
public void onMapReady(GoogleMap googleMap) {
        mMap = googleMap;

        // Add a marker in Sydney and move the camera
        LatLng sydney = new LatLng(-34, 151);
        //看到上面這行就是經緯度 現在來找一下
        mMap.addMarker(new MarkerOptions().position(sydney).title("Marker in Sydney"));
        mMap.moveCamera(CameraUpdateFactory.newLatLng(sydney));
    }
```

![](https://i.imgur.com/lNVHwwO.png)

gps經緯度 跟google map 經緯度會相反  

GPS(經度：120.225435 緯度：23.023535)
# cmd看sha1值(非必要

你的ˊ程式碼已經存了 知道啦還有ㄎㄎ 如果要用cmd看的話  

你的按鍵旗標+r 輸入cmd

![](https://i.imgur.com/8FiWVY3.png)

  

![](https://i.imgur.com/gY74dko.png)

  

裡面有一個隱藏資料夾.android  

![](https://i.imgur.com/pFqPldS.png)

  

打dir顯示所有檔案  

![](https://i.imgur.com/e5sekVs.png)

  

這邊的話看到他有一行
```
keytool -list -v -keystore mystore.keystore
```

![](https://i.imgur.com/LbClGxA.png)

```
keytool -list -v -keystore debug.keystore
```
ㄎㄎ這台電腦沒有裝keytool你們應該有  

反正就是可以看到你們 sha1 值
現在拿起你們得傳輸線插進去你們的手機  

![](https://i.imgur.com/Lm0AaVz.png)

  

點那個撥放  

![](https://i.imgur.com/TiwjOWL.png)

  

差你的手機 直接選你的垃圾手機 我傳輸線壞了 選了直接ok手機就可以直接跑你的app
記得手機要開location 不行的話 裡面的gps把高精準度調成用wifi
沒傳輸線的可以用這方法  

![](https://i.imgur.com/XGn4AaU.png)

這邊可以編譯成apk  

跑跑跑  

![](https://i.imgur.com/La3Yc9k.png)

ㄎㄎ這邊我的電腦裝了google map會發生錯誤  

![](https://i.imgur.com/fTtHfYT.png)

  

以下你們可能會
# MAP空白可能原因如下

## GPS定位錯誤

檢查gps 調成wifi定位再來就是
## 缺少google play service

檢查google play service 有沒有加載  

![](https://i.imgur.com/mTCsV7W.png)

  

![](https://i.imgur.com/M2skDZy.png)

  

記得打勾  

按下apply  

![](https://i.imgur.com/m4yPoin.png)

  

ok  

![](https://i.imgur.com/6tfICt6.png)

  

![](https://i.imgur.com/Q24RLxO.png)

  

跑跑跑  

![](https://i.imgur.com/gXSBolH.png)

  

跑好了  

finish 然後 ok  

![](https://i.imgur.com/Gx98vf1.png)

  

重建專案一 下
## GOOGLE PLAY SERVICE 再次確認

為了以防萬一

![](https://i.imgur.com/YMyJATQ.png)

選左邊app  

![](https://i.imgur.com/xGI34SZ.png)

  

然後再跳到dependccies那邊

![](https://i.imgur.com/mYqDyCz.png)

  

檢查有沒有存在這沒有的話

![](https://i.imgur.com/JsOrjCD.png)

  

按這個
選到一樣的  

![](https://i.imgur.com/1wKix86.png)

  

套用 ok
老樣子  

![](https://i.imgur.com/vNQ69Dv.png)

  

重建專案  

![](https://i.imgur.com/aVDQ9SQ.png)

編譯apk 燒到你的手機
## 編譯APK失敗

如果你的電腦真的跟我依樣這麼特殊

![](https://i.imgur.com/halHDPf.png)

還是會錯  

這錯誤就是因為這個app加載了太多函示庫沒辦法編譯成2進位檔  

所以要在一個地方加個幾行  

解決方案:  

<http://stackoverflow.com/questions/15209831/unable-to-execute-dex-method-id-not-in-0-0xffff-65536>

![](https://i.imgur.com/XZ4vqS3.png)

  

進到這裡面
```
android {
   defaultConfig {
      ...
      multiDexEnabled  true  <<插入這行
   }
}
```
然後  

在
```
dependencies {
  ...
  compile 'com.android.support:multidex:1.0.0' <<插入這行
}
```
插入這行
所以看起來會  

![](https://i.imgur.com/fRyxoRr.png)

  

和  

![](https://i.imgur.com/dctNAXL.png)

這時候再來

![](https://i.imgur.com/roHTwYq.png)

  

重建專案
在一次  

![](https://i.imgur.com/8OKexyR.png)

  

產生apk看看
這邊可以看到  

![](https://i.imgur.com/QYegwg3.png)

  

已經可以編譯成功了
接下來呢怎樣把apk拿出來點選專案的資料夾右鍵

![](https://i.imgur.com/KADhV8d.png)

  

這邊可以把專案資料夾給丟出來

![](https://i.imgur.com/sXh2HMe.png)

  

這樣子  

在這邊打 *.apk

![](https://i.imgur.com/OJX9e6a.png)

找到了我們剛剛編譯個apk
現在你的手機安裝玩這apk 還是直接燒入到手機
