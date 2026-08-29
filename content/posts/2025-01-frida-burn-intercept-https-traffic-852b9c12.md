---
title: "frida + burp Intercept https traffic"
date: "2025-01-18T16:56:00.004+08:00"
updated: "2025-02-19T09:58:56.357+08:00"
permalink: "/2025/01/frida-burn-intercept-https-traffic.html"
original_url: "https://x8795278.blogspot.com/2025/01/frida-burn-intercept-https-traffic.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-797564958628170495"
tags: ["frida"]
layout: post
---

![](https://hackmd.io/_uploads/Hyass1Yw1x.png)

# frida + burp Intercept https traffic

det to cert
openssl x509 -inform DER -in test -out burp_cert.crt
![image](https://hackmd.io/_uploads/Syfvo0Owyx.png)

adb push .\burp_cert.crt /data/local/tmp
adb shell mv /data/local/tmp/burp_cert.crt /sdcard/Download/
![image](https://hackmd.io/_uploads/S1OWC0OwJl.png)
![image](https://hackmd.io/_uploads/rJIJiAdvyg.png)
![image](https://hackmd.io/_uploads/SkhxjAuvyg.png)

![image](https://hackmd.io/_uploads/SJPs3Cuw1x.png)
![image](https://hackmd.io/_uploads/ryasnAdP1e.png)
![image](https://hackmd.io/_uploads/S1Wh30OPyg.png)
![image](https://hackmd.io/_uploads/Hk4phAdwkl.png)

![image](https://hackmd.io/_uploads/H1R-pAdv1x.png)
![image](https://hackmd.io/_uploads/ryO_00_Pkl.png)

![image](https://hackmd.io/_uploads/Skf7TR_wyg.png)
# gen ssl key
```
openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt -days 365 -nodes
```
# simple python server
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import json

class CustomHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 解析傳入的數據
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # 將數據解碼為 JSON
        try:
            data = json.loads(post_data)
            username = data.get("username")
            password = data.get("password")
            response = {"status": "success", "message": f"Hello {username}!"}
        except Exception as e:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())
            return

        # 返回結果
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

def run_server():
    # 設置伺服器地址和端口
    host = '0.0.0.0'
    port = 8443
    server = HTTPServer((host, port), CustomHandler)
    
    # 綁定 SSL 證書和密鑰
    server.socket = ssl.wrap_socket(server.socket,
                                    certfile='server.crt',
                                    keyfile='server.key',
                                    server_side=True)
    print(f"Serving on https://{host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()

```
# app
```java
package com.example.secchat

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.secchat.databinding.ActivityInputBinding
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import retrofit2.Call
import retrofit2.Callback

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.UUID
import okhttp3.Response
import java.security.cert.X509Certificate
import javax.net.ssl.SSLContext
import javax.net.ssl.TrustManager
import javax.net.ssl.X509TrustManager

class InputActivity : AppCompatActivity() {

    private lateinit var binding: ActivityInputBinding
    private lateinit var apiService: ApiService
    // 靜態加載 secchat 庫
    companion object {
        // 靜態加載 secchat 庫
        init {
            System.loadLibrary("secchat")
        }
    }

    object ApiClient {
        private const val TAG = "ApiClient"
        private const val API_URL = "https://172.22.100.167:8443"

        private fun getUnsafeOkHttpClient(): OkHttpClient {
            try {
                val trustAllCerts = arrayOf<TrustManager>(object : X509TrustManager {
                    override fun checkClientTrusted(chain: Array<X509Certificate>, authType: String) {}
                    override fun checkServerTrusted(chain: Array<X509Certificate>, authType: String) {}
                    override fun getAcceptedIssuers(): Array<X509Certificate> = arrayOf()
                })

                val sslContext = SSLContext.getInstance("SSL")
                sslContext.init(null, trustAllCerts, java.security.SecureRandom())

                val sslSocketFactory = sslContext.socketFactory
                return OkHttpClient.Builder()
                    .sslSocketFactory(sslSocketFactory, trustAllCerts[0] as X509TrustManager)
                    .hostnameVerifier { _, _ -> true }
                    .build()
            } catch (e: Exception) {
                throw RuntimeException(e)
            }
        }

        fun sendCredentials(username: String?, password: String?) {
            val client = getUnsafeOkHttpClient()

            val json = """{"username": "$username", "password": "$password"}"""
            val mediaType = "application/json; charset=utf-8".toMediaType()
            val body = json.toRequestBody(mediaType)

            val request = Request.Builder()
                .url(API_URL)
                .post(body)
                .build()

            Thread {
                try {
                    val response: Response = client.newCall(request).execute()
                    if (response.isSuccessful) {
                        Log.i(TAG, "Response: ${response.body?.string()}")
                    } else {
                        Log.e(TAG, "Request failed: ${response.code}")
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error sending request", e)
                }
            }.start()
        }
    }

    // 聲明 native 方法
    external fun stringFromJNI(): String
    // 使用 UUID 類生成有效的 UUID
    private fun generateRandomUserId(): String {
        return UUID.randomUUID().toString()
    }

    override fun onCreate(savedInstanceState: Bundle?) {

        val message = stringFromJNI()
        Log.d("JNI_MESSAGE", message)
        super.onCreate(savedInstanceState)

        binding = ActivityInputBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // 初始化 Retrofit
        val retrofit = Retrofit.Builder()
            .baseUrl("http://192.168.30.100:8080") // 替换为你的API服务器地址
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        apiService = retrofit.create(ApiService::class.java)

        // 设置按钮点击事件
        binding.btnSubmit.setOnClickListener {
            // 調用 native 方法
            val message = stringFromJNI()
            Log.d("JNI_MESSAGE", message)
            ApiClient.sendCredentials("testuser", "testpassword")
            val title = binding.etTitle.text.toString()
            val userId = generateRandomUserId() // 确保生成的 user_id 是有效的 UUID

            // 检查用户是否输入了标题
            if (title.isNotEmpty()) {
                // 创建标题请求对象
                val titleRequest = TitleEntryRequest(title, userId)

                // 通过 API 提交标题
                submitTitle(titleRequest)
            } else {
                binding.etTitle.error = "請輸入標題"
            }
        }
    }

```
# hook.js
```
Java.perform(() => {
    console.log("Hooking OkHttpClient.Builder...");

    const OkHttpClientBuilder = Java.use("okhttp3.OkHttpClient$Builder");
    const Proxy = Java.use("java.net.Proxy");
    const InetSocketAddress = Java.use("java.net.InetSocketAddress");
    const ProxyType = Java.use("java.net.Proxy$Type");

    OkHttpClientBuilder.build.implementation = function () {
        console.log("Hooked OkHttpClient.Builder.build()");

        try {
            const proxyHost = "10.0.2.2"; // Burp Suite 的地址
            const proxyPort = 8099;      // Burp Suite 的代理端口

            // 初始化 InetSocketAddress
            console.log("Creating InetSocketAddress...");
            const socketAddress = InetSocketAddress.$new(proxyHost, proxyPort);
            console.log("InetSocketAddress created: " + socketAddress);

            // 確保 Proxy.Type.HTTP 初始化正確
            console.log("Creating Proxy...");
            const proxyType = ProxyType.valueOf("HTTP"); // 使用顯式方法初始化
            const proxy = Proxy.$new(proxyType, socketAddress);
            console.log("Proxy created: " + proxy);

            console.log("Redirecting traffic to proxy: " + proxyHost + ":" + proxyPort);

            this.proxy(proxy); // 設置代理
        } catch (e) {
            console.error("Error setting proxy: " + e.message);
        }

        return this.build();
    };
});

```

透過這種方式就可以當中間人看到底傳什麼
![image](https://hackmd.io/_uploads/rJdoj1KvJe.png)
![image](https://hackmd.io/_uploads/Hyass1Yw1x.png)
![image](https://hackmd.io/_uploads/Bygu2kYv1g.png)

