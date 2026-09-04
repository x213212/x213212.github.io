---
title: "Face detection_抓小偷"
date: "2018-06-24T06:19:00.004+08:00"
updated: "2019-09-13T08:56:04.410+08:00"
permalink: "/2018/06/face-detection.html"
original_url: "https://x8795278.blogspot.com/2018/06/face-detection.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6491266282729651009"
tags: ["Android", "Java", "Tutorial", "Projects"]
layout: post
---

## 介紹

## --- 如果java client 端如果有偵測到人臉的話會儲存一張圖片到c:\\peoples.png 然後偵測到的人臉大於1的話則會將嫌疑人的照片儲存下來並發送一張圖片到 指定ip並告知可能有人在你家 Server 端如果有將會一直開著持續監聽 [![](https://i.imgur.com/FwW1OjL.png)](https://i.imgur.com/FwW1OjL.png)[![](https://i.imgur.com/C2Aeb2t.png)](https://i.imgur.com/C2Aeb2t.png)

## 環境設定

---

Javacv 1.2: <https://github.com/bytedeco/javacv>
Eclipse
Android studio
Opencv 2.49 or 48

<https://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.4.9/>
  

  
## Javacv 1.2建置

---

下載好javacv後建立一個eclipse 專案 選jse就可以了這邊要來做監控的client,記得把這些函示庫引入
[![](https://i.imgur.com/6Dlq3W9.png)](https://i.imgur.com/6Dlq3W9.png)
[![](https://i.imgur.com/YRHNAGM.png)](https://i.imgur.com/YRHNAGM.png)
## Opencv 建置

---

[![](https://i.imgur.com/aXzii5I.png)](https://i.imgur.com/aXzii5I.png)
[![](https://i.imgur.com/XhfkAde.png)](https://i.imgur.com/XhfkAde.png)
64位元就選x64,32位元就選x86
## Face detection.code

---

  

**`androidserver.java`**

```java
package com.example.jack.myapplication;
 
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.widget.ImageView;
import android.widget.ScrollView;
import android.widget.TextView;
 
public class MainActivity extends AppCompatActivity {
    ServerTcpListener Server=null;
    TextView IPVIEW,conter_tx;
    ScrollView sco1;
    ImageView img1;
    int conter;
    Thread t;
    @Override
 
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
//顯示你的ip這我拿來看手機連到wifi的ip才能指定socket 互傳檔案
        IPVIEW=(TextView) findViewById(R.id.textView);
        IPVIEW.setText( getMyIp() .toString());
//用在偵測到人要變換視窗顏色
        conter_tx=(TextView)findViewById(R.id.textView2) ;
        sco1=(ScrollView)findViewById(R.id.sco1) ;
//開啟一個thread去呼叫server並開啟
      t = new Thread(new ServerTcpListener(this));
        t.start();
        img1=(ImageView)findViewById(R.id.imageView);
        IPVIEW.setText( "server is start!!");
    }
    private String getMyIp(){
 
        //新增一個WifiManager物件並取得WIFI_SERVICE
 
        WifiManager wifi_service = (WifiManager)getSystemService(WIFI_SERVICE);
 
        //取得wifi資訊
 
        WifiInfo wifiInfo = wifi_service.getConnectionInfo();
 
        //取得IP，但這會是一個詭異的數字，還要再自己換算才行
 
        int ipAddress = wifiInfo.getIpAddress();
 
        //利用位移運算和AND運算計算IP
 
        String ip = String.format("%d.%d.%d.%d",(ipAddress & 0xff),(ipAddress >> 8 & 0xff),(ipAddress >> 16 & 0xff),(ipAddress >> 24 & 0xff));
 
        return ip;
 
    }
 
}
 
Android server : ServerTcpListener
package com.example.jack.myapplication;
 
import android.app.Activity;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Environment;
 
import java.io.DataInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.net.ServerSocket;
import java.net.Socket;
 
/**
 * Created by JACK on 2016/12/8.
 */
 
 
    public class ServerTcpListener implements Runnable {
    public MainActivity tmp;
    private static Context mContext;
 
        public static void main(String[] args) {
 
        }
public ServerTcpListener(MainActivity tmp)
{this.tmp=tmp;
    mContext=tmp;
}
        public void run() {
 
            try {
                final ServerSocket server = new ServerSocket(ClientTcpSend.port);
 
 
                while (true) {
 
                    try {
                        System.out.println("監聽中...");
                        Socket socket = server.accept();
                        System.out.println("有資料傳送!");
                        receiveFile(socket);
 
                    } catch (Exception e) {
                    }
 
                }
 
 
            } catch (Exception e) {
                e.printStackTrace();
            }
 
        }
 
 
 
    public  void receiveFile(Socket socket) {
 
            byte[] inputByte = null;
            int length = 0;
            DataInputStream dis = null;
            FileOutputStream fos = null;
            try {
                try {
 
                    dis = new DataInputStream(socket.getInputStream());
                    fos = new FileOutputStream(new 
////這邊要注意如果要取得內部sd卡位置
File( Environment.getExternalStorageDirectory().getAbsolutePath()+"//aa.png"));
                    inputByte = new byte[1024*4];
                    System.out.println("開始接收檔案...");
                    while ((length = dis.read(inputByte, 0, inputByte.length)) > 0) {
                        fos.write(inputByte, 0, length);
                        fos.flush();
                    }
                    System.out.println("完成接收");
 
                    Bitmap bMap = BitmapFactory.decodeFile(Environment.getExternalStorageDirectory().getAbsolutePath()+"//aa.png");
///畫面即時更新ui 
                    new Thread(new Runnable() {
                        public void run() {
                            //這邊是背景thread在運作, 這邊可以處理比較長時間或大量的運算
                            ((Activity) mContext).runOnUiThread(new Runnable() {
                                public void run() {
                                    //這邊是呼叫main thread handler幫我們處理UI部分
                                    Bitmap bMap = BitmapFactory.decodeFile(Environment.getExternalStorageDirectory().getAbsolutePath()+"//aa.png");
                                    tmp.img1.setImageBitmap( bMap);
                                    tmp.conter_tx.setText("可能被侵入次數:"+tmp.conter);
                                    tmp.conter+=1;
 
                                }
                            });
                        }
                    }).start();
 
 
 
 
                } finally {
                    if (fos != null)
                        fos.close();
                    if (dis != null)
                        dis.close();
                    if (socket != null)
                        socket.close();
                }
            } catch (Exception e) {
 
            }
        }
}
 
 
```

**`eclipeclient.java`**

```java
package test;
import javax.swing.*;
 
import java.awt.Toolkit;
import java.io.File;
import java.net.URL;
import org.bytedeco.javacpp.Loader;
import org.bytedeco.javacpp.opencv_core.IplImage;
import org.bytedeco.javacv.CanvasFrame;
import org.bytedeco.javacv.FrameGrabber;
import org.bytedeco.javacv.OpenCVFrameConverter;
import org.bytedeco.javacv.OpenCVFrameGrabber;
import static org.bytedeco.javacpp.opencv_core.*;
import static org.bytedeco.javacpp.opencv_imgproc.*;
import static org.bytedeco.javacpp.opencv_highgui.*;
import static org.bytedeco.javacpp.opencv_imgcodecs.*;
import static org.bytedeco.javacpp.helper.opencv_objdetect.cvHaarDetectObjects;
import org.bytedeco.javacpp.opencv_core.CvMemStorage;
import org.bytedeco.javacpp.opencv_core.CvRect;
import org.bytedeco.javacpp.opencv_core.CvScalar;
import org.bytedeco.javacpp.opencv_core.CvSeq;
import static org.bytedeco.javacpp.opencv_core.IPL_DEPTH_8U;
import static org.bytedeco.javacpp.opencv_core.cvClearMemStorage;
import static org.bytedeco.javacpp.opencv_core.cvGetSeqElem;
import static org.bytedeco.javacpp.opencv_core.cvLoad;
import static org.bytedeco.javacpp.opencv_core.cvPoint;
import static org.bytedeco.javacpp.opencv_imgproc.CV_BGR2GRAY;
import static org.bytedeco.javacpp.opencv_imgproc.cvCvtColor;
import org.bytedeco.javacpp.opencv_objdetect;
import static org.bytedeco.javacpp.opencv_objdetect.CV_HAAR_DO_CANNY_PRUNING;
import org.bytedeco.javacpp.opencv_objdetect.CvHaarClassifierCascade;
 
 
public class test {
          static OpenCVFrameConverter.ToIplImage converter = new OpenCVFrameConverter.ToIplImage();
          
          public static void main(String args[]) {
              System.out.println("ok");
 
                 //用 FrameGrabber 取得 得webcam
                 FrameGrabber grabber = new OpenCVFrameGrabber("");
 
                 //宣告一個CanvasFrame ，就把它當作是一個JFrame用。
                 CanvasFrame canvas = new CanvasFrame("Webcam", CanvasFrame.getDefaultGamma() / grabber.getGamma());
                 //設定這一個JFrame關閉時順便把程式結束。
                 canvas.setDefaultCloseOperation(
                         javax.swing.JFrame.EXIT_ON_CLOSE);
           
                 try {
                     //從網路上取得訓練好的檔案（不太建議用2.4版本的會有問題）
                     URL url = new URL("https://raw.github.com/Itseez/opencv/2.2/data/haarcascades/haarcascade_frontalface_alt.xml");
                     //把網頁上取回來的資料寫入本地端檔案
                     File file = Loader.extractResource(url, null, "classifier", ".xml");
                     //假如有相同檔名己存在則刪除舊友的
                     file.deleteOnExit();
                     //指定classifier檔案名稱（也就是剛才由網路上捉下來的檔案路徑）
                     String classifierName = file.getAbsolutePath();
 
                     // 預先載入 opencv_objdetect module .
                     Loader.load(opencv_objdetect.class);
                     //初始化HaarClassifierCascade
                     CvHaarClassifierCascade classifier = new CvHaarClassifierCascade(cvLoad(classifierName));
                     //假如載入HaarClassifierCascade 失敗則結束程式
                     if (classifier.isNull()) {
                         System.err.println("Error loading classifier file \"" + classifierName + "\".");
                         System.exit(1);
                     }
 
                     //啟動WebCam
                     grabber.start();
 
                     //定義一個IplImage 存放取出來的影像
                     IplImage img;
 
                     //先取一張畫面放入IplImage           
                     img = converter.convert(grabber.grab());
                     //取得影像的長寬
                     int width = img.width();
                     int height = img.height();
 
                     //建立一個灰階影像（用IPL_DEPTH_8U 原因為，灰階影像每一個pixel R,G,B值皆相等，只需要存一份即可）
                     IplImage grayImage = IplImage.create(width, height, IPL_DEPTH_8U, 1);
                     //建立一個CvMemStorage做運算用
                     CvMemStorage storage = CvMemStorage.create();
                    
                     //設定顯示用的CanvasFrame為取出的影像大小
                     canvas.setCanvasSize(grabber.getImageWidth(),
                             grabber.getImageHeight());
 
                     while (canvas.isVisible() && (img = converter.convert(grabber.grab())) != null) {
                         //重置運算用的CvMemStorage
                         cvClearMemStorage(storage);
 
                         // 把原始影像變成灰階
                         cvCvtColor(img, grayImage, CV_BGR2GRAY);
                         //偵測人臉
                         CvSeq faces = cvHaarDetectObjects(grayImage, classifier, storage,
                                 1.1, 3, CV_HAAR_DO_CANNY_PRUNING);
                         //取得捉到的人臉
 
//檢測到底有沒有一個人臉以上有的話則發送到server端
                         int total = faces.total();
                         if(total>0)
                           {
                         cvSaveImage("/peoples.png",img);
                         new ClientTcpSend();
                         }
                         //在人臉上畫一個綠色的矩型
                         for (int i = 0; i < total; i++) {
                             CvRect r = new CvRect(cvGetSeqElem(faces, i));
                             int x = r.x(), y = r.y(), w = r.width(), h = r.height();
                             cvRectangle(img, cvPoint(x, y), cvPoint(x + w, y + h), CvScalar.GREEN, 1, CV_AA, 0);
                         }
                         //顯示圖片
                         cvShowImage( "Detection...", img );
                         
                cvWaitKey(200);
                     Toolkit toolkit = Toolkit.getDefaultToolkit();
                 toolkit.beep();
 
                     }
                 }
                 catch(Exception e)
                 {
                    
                 }
                
 
             }
          
}
 
//這邊的話可以看到 可以選擇要不要定時發出蜂鳴器 引起嫌犯人看鏡頭
     Toolkit toolkit = Toolkit.getDefaultToolkit();
                 toolkit.beep();
 
```
