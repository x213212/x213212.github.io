---
title: "Android Post json to PHP mysql"
date: "2018-03-30T15:04:00.000+08:00"
updated: "2018-09-05T07:46:03.492+08:00"
permalink: "/2018/06/android-post-json-to-php-mysql.html"
original_url: "https://x8795278.blogspot.com/2018/06/android-post-json-to-php-mysql.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3640229488937516580"
tags: ["Android", "Tutorial"]
layout: post
---

## 前置作業Android 透過post 去控制資料庫

---

Xampp <-- 先裝

首先呢我們要把資料庫的免密碼設定要帳號登入  

  

[![](https://i.imgur.com/r3dnEaG.png)](https://i.imgur.com/r3dnEaG.png)  

[![](https://i.imgur.com/iHyUUN2.png)](https://i.imgur.com/iHyUUN2.png)  

  

我們在來進到
## 尋找config.inc.php

---

[![](https://i.imgur.com/pU7FsC5.png)](https://i.imgur.com/pU7FsC5.png)
## [![](https://i.imgur.com/8GmdEmc.png)](https://i.imgur.com/8GmdEmc.png) [![](https://i.imgur.com/Hitkstx.png)](https://i.imgur.com/Hitkstx.png)

必須注意的是Android 的 Project Structure Dependencies 要設定並新增implementation 'org.jbundle.util.osgi.wrapped:org.jbundle.util.osgi.wrapped.org.apache.http.client:4.1.2'
##

##

**`executeQuery.java`**

```java
private String executeQuery(String query)
    {
        String result = "";
        try
        {
            HttpClient httpClient = new DefaultHttpClient();
            HttpPost post = new HttpPost("http://192.168.137.1/qeury.php");
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
            result = builder.toString();
        }
        catch (Exception e)
        {
            Log.e("log_tag", e.toString());
        }
        return result;
    }
```

**`qeury.php`**

```php
<?php
error_reporting(E_ALL ^ E_DEPRECATED);
$sql = $_POST['query_string'];
$db = mysqli_connect("127.0.0.1", "root", "1234", "test") or die('error');
//$db = mysqli_connect("mysql.hostinger.com.hk","u769530028_map","------","u769530028_map")or die('error');
mysqli_query($db,"set names utf8");

if (isset($_POST["query_string"]))
{

   $sql = $_POST['query_string'];

$res = mysqli_query($db,$sql);
if($res === FALSE) {
    die(mysqli_error()); // TODO: better error handling
}
while($r = mysqli_fetch_assoc($res))
   $output[]  = $r;
   print(json_encode($output)); //轉成json格式 ， android 會抓取整個頁面資烙

}
else 
{
  $sql = null;
 // echo "no username supplied";
}

mysqli_close($db);

?>	
```

**`renewListView.java`**

```java
 public final void renewListView(String input) {
        /*
         * SQL 結果有多筆資料時使用JSONArray
         * 只有一筆資料時直接建立JSONObject物件
         * JSONObject jsonData = new JSONObject(result);
         */
        String user=null;
        String password=null;
        try {
            JSONArray jsonArray = new JSONArray(input);
            //list.clear();
            //  setTitle(jsonArray.length() + "筆資料");

            //tx1.setText(jsonArray.length() + "筆資料");
            //adapter = new ArrayAdapter(this,
            // android.R.layout.simple_list_item_1);
            for (int i = 0; i < jsonArray.length(); i++) {
                JSONObject jsonData = jsonArray.getJSONObject(i);
                // Log.i("asd",  "name:" + jsonData.getString("user") + "\ndata:" + jsonData.getString("password"));
                time_arr.add(jsonData.getString("time"));
                name_arr.add(jsonData.getString("per_name"));
                address_arr.add(jsonData.getString("address"));
              //資料欄位名稱
                //password=jsonData.getString("password");
                //  tx1.setText("name:" + jsonData.getString("user") + "\ndata:" + jsonData.getString("password"));
                //  adapter.add("name:" + jsonData.getString("user") + "\ndata:" + jsonData.getString("password") + "\nlocation[" + jsonData.getString("longitude") + "," + jsonData.getString("latitude") + "]\ntime:" + jsonData.getString("time"));
                //   list.add("name:" + jsonData.getString("user") + "\ndata:" + jsonData.getString("password") + "\nlocation[" + jsonData.getString("longitude") + "," + jsonData.getString("latitude") + "]\ntime:" + jsonData.getString("time"));
            }

            //  adapter.add( );
            //  ed1.setText("");

            //   lv1.setAdapter(adapter);
        } catch (JSONException e) {
            // TODO 自動產生的 catch 區塊
            e.printStackTrace();
        }
    }
```
