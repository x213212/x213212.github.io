---
title: "Android Update Photo php"
date: "2018-03-31T15:06:00.000+08:00"
updated: "2018-09-05T07:46:03.582+08:00"
permalink: "/2018/06/android-update-photo-php.html"
original_url: "https://x8795278.blogspot.com/2018/06/android-update-photo-php.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6700820291509775569"
tags: ["Android", "Tutorial"]
layout: post
---

## 我們來上傳檔案

---

對一次的專案內容我們透過@來分類和創建資料夾分類範例  
##

**`FileUpload.java`**

```java
package com.example.x2132.myapplication;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;

public class FileUpload {
    private String mResponseMsg;
    private boolean isSucess;

    public interface OnFileUploadListener{
        void onFileUploadSuccess(String msg);
        void onFileUploadFail(String msg);
    }

    private OnFileUploadListener mOnFileUploadListener;

    public void setOnFileUploadListener(OnFileUploadListener listener){
        mOnFileUploadListener = listener;
    }

    public boolean isSucess() {
        return isSucess;
    }

    public FileUpload(){
        mResponseMsg = "";
        isSucess = false;
    }

    public void doFileUpload(String path,String filename) {
        HttpURLConnection conn = null;
        DataOutputStream dos = null;
        DataInputStream inStream = null;
        String existingFileName = path;
        String lineEnd = "\r\n";
        String twoHyphens = "--";
        String boundary = "*****";
        int bytesRead, bytesAvailable, bufferSize;
        byte[] buffer;
        int maxBufferSize = 1 *6000* 6000;
        String urlString = "http://192.168.137.1/UploadToServer.php";

        try {
            //------------------ CLIENT REQUEST
            FileInputStream fileInputStream = new FileInputStream(new File(existingFileName));
            // open a URL connection to the Servlet
            URL url = new URL(urlString);
            // Open a HTTP connection to the URL
            conn = (HttpURLConnection) url.openConnection();
            // Allow Inputs
            conn.setDoInput(true);
            // Allow Outputs
            conn.setDoOutput(true);
            // Don't use a cached copy.
            conn.setUseCaches(false);
            // Use a post method.
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Connection", "Keep-Alive");
            conn.setRequestProperty("Content-Type", "multipart/form-data;boundary=" + boundary);
            dos = new DataOutputStream(conn.getOutputStream());
            dos.writeBytes(twoHyphens + boundary + lineEnd);
            dos.writeBytes("Content-Disposition: form-data; name=\"uploadedfile\";filename=\"" +filename+".jpg" + "\"" + lineEnd);
            dos.writeBytes(lineEnd);
            // create a buffer of maximum size
            bytesAvailable = fileInputStream.available();
            bufferSize = Math.min(bytesAvailable, maxBufferSize);
            buffer = new byte[bufferSize];
            // read file and write it into form...
            bytesRead = fileInputStream.read(buffer, 0, bufferSize);

            while (bytesRead > 0) {

                dos.write(buffer, 0, bufferSize);
                bytesAvailable = fileInputStream.available();
                bufferSize = Math.min(bytesAvailable, maxBufferSize);
                bytesRead = fileInputStream.read(buffer, 0, bufferSize);

            }

            // send multipart form data necesssary after file data...
            dos.writeBytes(lineEnd);
            dos.writeBytes(twoHyphens + boundary + twoHyphens + lineEnd);
            // close streams
            fileInputStream.close();
            dos.flush();
            dos.close();
            isSucess = true;
        } catch (MalformedURLException e){
            isSucess = false;
        } catch (IOException e) {
            isSucess = false;
        }

        try {
            inStream = new DataInputStream(conn.getInputStream());
            String str;
            while ((str = inStream.readLine()) != null) {
                mResponseMsg = str;
            }
            inStream.close();

        } catch (IOException e) {
            isSucess = false;
            mResponseMsg = e.getMessage();
        }
        if(mOnFileUploadListener != null) {
            if (isSucess) {
                mOnFileUploadListener.onFileUploadSuccess(mResponseMsg);
            } else{
                mOnFileUploadListener.onFileUploadFail(mResponseMsg);
            }
        }
    }
}
```

**`UploadToServer.php`**

```php
<?php
    $target_path = "img/";
	 $target_path2 = "img/";
	$source = $_FILES['uploadedfile']['name'];//按逗号分离字符串 
	$hello = explode('@',$source); 
		mkdir( "img/".$hello[0]);
			
		mkdir($hello[0]);
    $target_path = $target_path .$hello[0]."/" . $hello[1]; 
	

    if(move_uploaded_file($_FILES['uploadedfile']['tmp_name'], $target_path)) {
        echo "The file ".  basename( $_FILES['uploadedfile']['name'])." has been uploaded";
		//rename(  "img/tmp@2/tmp@2.jpg", "img/tmp@2/2.jpg");
		$source=realpath("img/tmp"."02"."/tmp@2.jpg");
		rename( "img/".$hello[0]."/tmp@2.jpg","img/".$hello[0]."/".$hello[1]);
    } else{
        echo "There was an error uploading the file, please try again!";
        echo "filename: " .  basename( $_FILES['uploadedfile']['name']);
        echo "target_path: " .$target_path;
    }
	
?>
```
