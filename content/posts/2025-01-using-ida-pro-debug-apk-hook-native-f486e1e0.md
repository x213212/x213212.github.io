---
title: "using ida pro debug apk & hook native function example"
date: "2025-01-18T14:16:00.006+08:00"
updated: "2025-01-18T14:16:42.302+08:00"
permalink: "/2025/01/using-ida-pro-debug-apk-hook-native.html"
original_url: "https://x8795278.blogspot.com/2025/01/using-ida-pro-debug-apk-hook-native.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8173036946380171178"
tags: ["frida"]
layout: post
---

![](https://hackmd.io/_uploads/S14FHndwyx.png)

# using ida pro debug apk & hook native function example

將IDAPro\dbgsrv內部的gdb server 透過 adb 傳到 虛擬機或手機內部
```
adb push android_x64_server /data/local/tmp
adb shell
su
cd /data/local/tmp
chmod 755 android_x64_server
./android_x64_server
```

![image](https://hackmd.io/_uploads/rk5xVudPkl.png)
這邊ida pro版本降到 8.3
![image](https://hackmd.io/_uploads/rJIdd5dwkg.png)

![image](https://hackmd.io/_uploads/ByUhw9Ow1l.png)
![image](https://hackmd.io/_uploads/ryxt_cOwkx.png)
![image](https://hackmd.io/_uploads/r1Xiu5_w1x.png)
這樣就可以debug app 的 so 了

# build so
這邊加入 sdk tool cmake
![image](https://hackmd.io/_uploads/BybWmidwyx.png)

然後你就可以在目錄創建一個c++ .so了
![image](https://hackmd.io/_uploads/S1-vQi_Pke.png)

# secchat
```cpp
#include <jni.h>
#include <string>

// 具體實現 native 方法
extern "C" JNIEXPORT jstring JNICALL
Java_com_example_secchat_MainActivity_stringFromJNI(JNIEnv* env, jobject /* this */) {
    std::string message = "Hello from C++!";
    return env->NewStringUTF(message.c_str());
}

```
# build.gradle.kts
```kts
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
}

android {
    namespace = "com.example.secchat"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.secchat"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        externalNativeBuild {
            cmake {
                cppFlags += "-std=c++17" <======
            }
        }
        ndk {
            abiFilters += listOf("armeabi-v7a", "arm64-v8a", "x86", "x86_64")
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = "1.8"
    }
    buildFeatures {
        viewBinding = true
    }
    externalNativeBuild {
        cmake {
            path = file("src/main/cpp/CMakeLists.txt")
            version = "3.22.1"
        }
    }
}

dependencies {

    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.appcompat)
    implementation(libs.material)
    implementation(libs.androidx.constraintlayout)
    implementation(libs.androidx.lifecycle.livedata.ktx)
    implementation(libs.androidx.lifecycle.viewmodel.ktx)
    implementation(libs.androidx.navigation.fragment.ktx)
    implementation(libs.androidx.navigation.ui.ktx)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)

    // Retrofit 依赖
    implementation("com.squareup.retrofit2:retrofit:2.9.0")

    // Gson 转换器，用于将 JSON 转换为 Kotlin 对象
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")

    // 如果你需要 OkHttp 作为网络库
    implementation("com.squareup.okhttp3:okhttp:4.9.0")
    implementation("org.java-websocket:Java-WebSocket:1.5.2")

}
```
# CMakelist
```make
cmake_minimum_required(VERSION 3.22.1)
project("secchat")

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(secchat SHARED
        secchat.cpp
)

find_library(log-lib log)
find_library(android-lib android)

target_link_libraries(secchat
        ${log-lib}
        ${android-lib}
)

```

# app
```java

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
    // 聲明 native 方法
    external fun stringFromJNI(): String

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // 調用 native 方法
        val message = stringFromJNI()
        Log.d("JNI_MESSAGE", message)

```

![image](https://hackmd.io/_uploads/rydkFidvJe.png)

```
app一開始啟動就加載這邊用 frida 啟動
```
adb shell
emu64xa:/ $  pm list packages | grep sec
package:com.example.secchat
emu64xa:/ $
```

# frida-gadget
https://github.com/frida/frida/releases/download/16.6.4/frida-gadget-16.6.4-freebsd-x86_64.so.xz

Failed to spawn: need Gadget to attach on jailed Android; its default location is: C:\Users\x213212\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\AC\INetCache\frida\gadget-android-arm64.so

複製貼過來
C:\Users\x213212\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\AC\INetCache\frida\

 am clear-debug-app
 frida -U -f com.example.secchat -l replacejnifunction.js --runtime=v8
 
```

 # replace so return value
```javascript
 Java.perform(function () {
    var moduleName = "libsecchat.so";
    var targetFunctionName = "Java_com_example_secchat_InputActivity_stringFromJNI";

    function hookFunction() {
        var targetFunction = Module.findExportByName(moduleName, targetFunctionName);
        if (targetFunction) {
            console.log("Target function found at: " + targetFunction);

            Interceptor.attach(targetFunction, {
                onEnter: function (args) {
                    console.log("Function called");
                },
                onLeave: function (retval) {
                    // 原始返回值
                    var originalString = Memory.readUtf8String(retval);
                    console.log("Original return value: " + originalString);

                    // 调用 JNI 分配新的字符串
                    var jniEnv = Java.vm.getEnv();
                    var newString = "Modified by Frida!";
                    var jstring = jniEnv.newStringUtf(newString);

                    // 替换返回值
                    retval.replace(jstring);
                    console.log("Modified return value to: " + newString);
                }
            });
        } else {
            console.log("Target function not found yet!");
        }
    }

    function waitForModule() {
        var module = Module.findBaseAddress(moduleName);
        if (module) {
            console.log("Module loaded at: " + module);
            hookFunction();
        } else {
            console.log("Module not loaded. Retrying...");
            setTimeout(waitForModule, 1000);
        }
    }

    waitForModule();
});

```

 到這邊就可以動態替換掉了
 ![image](https://hackmd.io/_uploads/S14FHndwyx.png)

# hook 某個 app class所有事件
```java
Java.perform(() => {
    const className = "com.example.secchat.InputActivity"; // 目标类名
    const targetClass = Java.use(className);

    console.log("[*] Hooking all methods in " + className);

    // 获取类中的所有方法
    const methods = targetClass.class.getDeclaredMethods();
    methods.forEach(method => {
        const methodName = method.getName();
        console.log("[+] Hooking method: " + methodName);

        try {
            // 动态 Hook 每个方法
            targetClass[methodName].overload().implementation = function (...args) {
                console.log(`[*] Method called: ${methodName}`);
                console.log(`    Arguments: ${args}`);

                // 打印调用栈
                console.log(`[+] Call Stack:\n${Java.use("android.util.Log").getStackTraceString(Java.use("java.lang.Exception").$new())}`);

                // 调用原始方法
                const result = this[methodName](...args);
                console.log(`[*] Method result: ${result}`);
                return result;
            };
        } catch (e) {
            console.error(`[!] Failed to hook method: ${methodName}`);
        }
    });
});

```

https://chan-shaw.github.io/2020/04/05/IDA-%E5%8A%A8%E6%80%81%E8%B0%83%E8%AF%95/

