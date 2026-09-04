---
title: "Android 工具人app"
date: "2018-04-09T15:31:00.000+08:00"
updated: "2019-09-13T08:56:03.923+08:00"
permalink: "/2018/06/android-app.html"
original_url: "https://x8795278.blogspot.com/2018/06/android-app.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5222335496588391565"
tags: ["Android", "Tutorial", "Projects"]
layout: post
---

## 功能介紹

---

以前的課專，忘記上傳解說一波。
[![](https://i.imgur.com/V22mAMS.png)](https://i.imgur.com/V22mAMS.png)[![](https://i.imgur.com/OuFyxsd.png)](https://i.imgur.com/OuFyxsd.png)  

  

  

  

  

一個類似UBER的APP可以延伸運用  

但是不向UBER只侷限開車也很像神奇寶貝GO的抓寶地圖  

[![](https://i.imgur.com/K8Gqtcj.png)](https://i.imgur.com/K8Gqtcj.png)  

  

  

這APP打算用資料庫和GPS Or WIFI定位和GOOGLE MAP地圖  

功能的基本:就是可以任意在地圖上留下訊息，在下面欄位那邊可以搜尋之前的人所留留下的訊息點擊該marker可以觀看在該點下更多訊息，搜尋提供直觀的你的位置到對方位置在你搜尋時可以動態的觀看到線該線可以很清楚的看到你與留下訊息的人的距離  

## 功能

---

在地圖上點及任何一點，可以對該點設置你想說的話，將會插入一筆資料  

此筆資料可以有你的姓名和你想留下的資料，系統會產生時間戳記到這筆  

資料下方也有搜尋欄位我們可以透過搜尋欄位對所有留下資料的做搜尋，  

而點擊下方搜尋欄位將會產生一條線和移動至該點，在搜尋欄位中做搜尋  

的話可以將繪畫多條線到目前你的位置，可以很直觀的看到位於你最近的  

人或服務在哪。  
## 如何呼叫mysql

---

Android 呼叫 網頁php 透過post將指令送出 到mysql，mysql 回傳資料json  

則我們將對這串資料做處理。  
## 重要功能

---

負責呼叫mysql 指令  

製作動態搜尋，並畫線  

為搜尋欄位新增監聽事件  

Init()  

searchitem(String textToSerch)  

點擊地圖上marker則會顯示該點會下所有的訊息(可以該點多筆資料  

點擊該點則會顯示該點座標位置。  

  
## query.php

---

```php
<?php
error_reporting(E_ALL ^ E_DEPRECATED);
$db = mysql_pconnect("mysql.hostinger.com.hk","u769530028_map","-----")or die('error');
//$db = mysqli_connect("mysql.hostinger.com.hk","u769530028_map","------","u769530028_map")or die('error');
mysql_select_db("u769530028_map");
mysql_query("set names utf8");
$sql ="";
if (isset($_POST['query_string']))
{
  $sql = $_POST['query_string'];
} 
else 
{  $sql = $_POST['query_string'];}//這邊取得android 傳過來的sql指令
$res = mysql_query($sql);
if($res === FALSE) { 
    die(mysql_error()); // TODO: better error handling
}
while($r = mysql_fetch_assoc($res))
   $output[]  = $r;
   print(json_encode($output)); //轉成json格式 ， android 會抓取整個頁面資烙
mysql_close();
?> 
```

  

  
## MapsActivity.java layout

---

[![](https://i.imgur.com/DwKGtmI.png)](https://i.imgur.com/DwKGtmI.png)  
## MainActivity.java layout

---

[![](https://i.imgur.com/kLLbvSt.png)](https://i.imgur.com/kLLbvSt.png)  
## 負責呼叫mysql 指令

---

```java
private String executeQuery(String query)

{

    String result = "";

    try

    {

        HttpClient httpClient = new DefaultHttpClient();

        HttpPost post = new HttpPost("http://x213212.esy.es/qeury.php");//如上面

        ArrayList<NameValuePair> nameValuePairs = new ArrayList<NameValuePair>();

        nameValuePairs.add(new BasicNameValuePair("query_string", query));

        post.setEntity(new UrlEncodedFormEntity(nameValuePairs, HTTP.UTF_8));//防止亂馬

        HttpResponse httpResponse = httpClient.execute(post);

        HttpEntity httpEntity = httpResponse.getEntity();

        InputStream inputStream = httpEntity.getContent();

        BufferedReader bufReader = new BufferedReader(new InputStreamReader(inputStream, "utf-8"), 8);

        StringBuilder builder = new StringBuilder();

        String line = null;

        while ((line = bufReader.readLine()) != null)

        {

            builder.append(line + "\n");



        }

        inputStream.close();

        result = builder.toString();//儲存所有頁面資料

    }

    catch (Exception e)

    {

        Log.e("log_tag", e.toString());

    }

    return result;//回傳

}
}
```

  

  
## 製作動態搜尋，並畫線

---

如果點擊所有訊息則將會將會去跟mysql取的資料，然後將取得的資料丟到list <string> list裡面  

製作list搜尋欄位呢，我們要一個搜尋框，和所有資料，  

我們將會回傳資料存到list然後必須在搜尋框那邊新增一個監聽事件。  
## 回傳資料存到list

---

```java
public final void renewListView(String input)

   {
       try

       {

           JSONArray jsonArray = new JSONArray(input);

           list.clear();

           setTitle(jsonArray.length() + "筆資料");

           //tx1.setText(jsonArray.length() + "筆資料");

           adapter = new ArrayAdapter(this,

                   android.R.layout.simple_list_item_1);

           for (int i = 0; i < jsonArray.length(); i++)

           {

               JSONObject jsonData = jsonArray.getJSONObject(i); //一次讀一筆讀到尾

               LatLng sydney = new LatLng(Float.valueOf( jsonData.getString("latitude")), Float.valueOf(jsonData.getString("longitude")));

               mMap.addMarker(new MarkerOptions().position(sydney).title(jsonData.getString("name")) .snippet(jsonData.getString("data")));

               adapter.add("name:"+jsonData.getString("name")+"\ndata:"+jsonData.getString("data") +"\nlocation["+jsonData.getString("longitude")+","+jsonData.getString("latitude")+"]\ntime:"+jsonData.getString("time"));//插入一筆到adapter

               list.add("name:"+jsonData.getString("name")+"\ndata:"+jsonData.getString("data") +"\nlocation["+jsonData.getString("longitude")+","+jsonData.getString("latitude")+"]\ntime:"+jsonData.getString("time"));//插入一比到list string 型態

           }


           //  adapter.add( );

           ed1.setText("");//搜尋欄位清空

           init();

           lv1.setAdapter(adapter);//新增陣列到下方所有訊息

       }

       catch (JSONException e)

       {

           // TODO 自動產生的 catch 區塊

           e.printStackTrace();

       }

   }
```

  

  
## 為搜尋欄位新增監聽事件

---

```java

ed1.addTextChangedListener(new TextWatcher() {

    @Override

    public void beforeTextChanged(CharSequence s, int start, int count, int after) {

    }

    @Override

    public void onTextChanged(CharSequence s, int start, int before, int count) {

        if(s.toString().equals(""))

        {

            init();}

        else

        {searchitem(s.toString());



        }
//如果使用者的搜尋框沒有東西的話則初始化，如果有東西則做篩選動作

    }



    @Override

    public void afterTextChanged(Editable s) {



    }

});
```

  

  
## Init()

---

```java
public void init ()

{



    if(selectpolyline!=null)//把地圖上所有的線清除

    {for(Polyline line : selectpolyline)

    {

        line.remove();

    }

        selectpolyline.clear();

    }


    list2 = new ArrayList<String>();//將list <string> list2

    adapter2=new ArrayAdapter<String>(this,

            android.R.layout.simple_list_item_1);



    for(String s : list) {//這邊list已經將所有訊息裡面資料存進去了

        adapter2.add(s);//為了讓listview 動態更新

        list2.add(s);//新增一筆備份做沒有資料的時候還原

    }





    Toast.makeText(this, "ok", Toast.LENGTH_LONG).show();

    lv1.setAdapter(adapter2);

}
```

  

  
## searchitem(String textToSerch)

---

```java
public void searchitem(String textToSerch)

{

    try {

        String[] stockArr = new String[list2.size()];//轉成string 陣列

        stockArr = list2.toArray(stockArr);



        for(String s : stockArr)

        {

            if(!s.contains(textToSerch))//如果再string s 裡面沒有找到跟 textToSerch 相關文字則從list2裡面移除

            {

                list2.remove(s);

            }

        }
//在一次adpter2做初始化

        adapter2=new ArrayAdapter<String>(this,

                android.R.layout.simple_list_item_1);
//這邊是第一次載入如果沒做搜尋則不會畫線

        if(selectpolyline!=null)

        {for(Polyline line : selectpolyline)

        {

            line.remove();

        }

            selectpolyline.clear();

        }
//這時候可以發現list2裡面剩下的都是做過搜尋的東西

        for(String s : list2) {

            String tmp=s;

            String subTest = tmp.substring(tmp.indexOf("location[")+9, tmp.indexOf("]"));

            String[] latlong = subTest.split(",");

            double latitude = Double.parseDouble(latlong[0])    ;

            double longitude = Double.parseDouble(latlong[1]);

            LatLng listtmp=  new LatLng(longitude,latitude);

//youmarker 裡面會是程式碼一開始加載的時候透過或wifi裡面將會取得你目前位置
//這個迴圈裡面總共會有list2 x筆
// selectpolyline 一樣用list型態 

            selectpolyline.add(   mMap.addPolyline(new PolylineOptions().

                    add(youmarker.getPosition(), listtmp).

                    width(10).//線寬度

                    color(Color.RED).//線顏色

                    geodesic(true)));

            adapter2.add(s);

        }

        Toast.makeText(this, "搜尋完畢", Toast.LENGTH_LONG).show();

        lv1.setAdapter(adapter2);//顯示

    }catch(Exception e) {

        Log.e("log_tag", e.toString());

    }

}
```

  

  
## 點擊地圖上marker則會顯示該點會下所有的訊息(可以該點多筆資料

---

```java

public boolean onMarkerClick(Marker marker) {

//先做格式化在mysql裡面的double欄位裡面最多只可五位所以在精準度上最高到五位

    tmp=marker.getPosition();

    BigDecimal bd= new BigDecimal( tmp.longitude);

    bd=bd.setScale(5, BigDecimal.ROUND_HALF_UP);// 小數後面四位, 四捨五入

    BigDecimal bd2= new BigDecimal(tmp.latitude);

    bd2=bd2.setScale(5, BigDecimal.ROUND_HALF_UP);// 小數後面四位, 四捨五入

    String result = executeQuery("SELECT * FROM  `test` WHERE  `longitude` = "+bd+" AND  `latitude` = "+bd2+"");

    //   tx1.setText(result);

    renewListView(result);

    

    Toast.makeText(getApplicationContext(),"Marker Clicked: " + bd2, Toast.LENGTH_LONG).show();

    return false;

}
```

  

  
## 點擊該點則會顯示該點座標位置

---

```
public void onMapClick(LatLng latLng) {

    if(marker!=null){

        marker.remove();

        touch=true;

        tmp=latLng;

    }

    Toast.makeText(getApplicationContext(),"You touch: [" + latLng.latitude+","+latLng.longitude+"]", Toast.LENGTH_LONG).show();

    marker = mMap.addMarker(new MarkerOptions().position(latLng).title("You touch here"));
}
```

  

  
##
