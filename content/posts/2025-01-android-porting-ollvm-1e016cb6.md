---
title: "android porting ollvm 混淆"
date: "2025-01-20T21:56:00.004+08:00"
updated: "2025-01-20T21:56:35.957+08:00"
permalink: "/2025/01/android-porting-ollvm.html"
original_url: "https://x8795278.blogspot.com/2025/01/android-porting-ollvm.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8528236078580476849"
tags: ["Android", "ida"]
layout: post
---

![](https://hackmd.io/_uploads/SJahH0svkl.png)

# android porting ollvm 混淆
check clang version
```
C:\Users\x213212\AppData\Local\Android\Sdk\ndk\26.1.10909125\toolchains\llvm\prebuilt\windows-x86_64\bin\
```
```
C:\Users\x213212\AppData\Local\Android\Sdk\ndk\26.1.10909125\toolchains\llvm\prebuilt\windows-x86_64\bin>clang -v
Android (10552028, based on r487747d) clang version 17.0.2 (https://android.googlesource.com/toolchain/llvm-project d9f89f4d16663d5012e5c09495f3b30ece3d2362)
Target: x86_64-w64-windows-gnu
Thread model: posix
InstalledDir: C:/Users/x213212/AppData/Local/Android/Sdk/ndk/26.1.10909125/toolchains/llvm/prebuilt/windows-x86_64/bin

```

git clone --depth 1 --branch llvmorg-17.0.2 https://github.com/llvm/llvm-project.git

install visual studio
![image](https://hackmd.io/_uploads/r1RGWS9vkl.png)
![image](https://hackmd.io/_uploads/BJXwDB9w1e.png)

![image](https://hackmd.io/_uploads/S16pvH9wJl.png)
![image](https://hackmd.io/_uploads/BJ6kuB5Dkx.png)
![image](https://hackmd.io/_uploads/rkNw_BcDye.png)

# C:\llvm-project\llvm\lib\Passes\Obfuscation\IPObfuscationContext.cpp
```
    NF->getBasicBlockList().splice(NF->begin(), F->getBasicBlockList());
```
```
      NF->splice(NF->begin(), F);
```
# C:\llvm-project\llvm\lib\Passes\Obfuscation\Utils.cpp
```
static bool valueEscapes(const Instruction &Inst) {
  if (!Inst.getType()->isSized())
    return false;

  const BasicBlock *BB = Inst.getParent();
  for (const User *U : Inst.users()) {
    const Instruction *UI = cast<Instruction>(U);
    if (UI->getParent() != BB || isa<PHINode>(UI))
      return true;
  }
  return false;
}
```

# C:\llvm-project\llvm\lib\Passes\Obfuscation\Flattening.cpp
```
#include "Utils.h"
#include "CryptoUtils.h"
#include "Flattening.h"
#include "SplitBasicBlock.h"

// using namespace ...
using namespace llvm;
using std::vector;

#define DEBUG_TYPE "flattening"
// Stats
STATISTIC(Flattened, "Functions flattened");

// --------------------------------------------------
PreservedAnalyses FlatteningPass::run(Function &F, FunctionAnalysisManager &AM) {
    // 確認是否需要對此函式進行 Flatten
    if (toObfuscate(flag, &F, "fla")) {
        INIT_CONTEXT(F);
        if (flatten(F)) {
            ++Flattened;
        }
        return PreservedAnalyses::none();
    }
    return PreservedAnalyses::all();
}

// --------------------------------------------------
bool FlatteningPass::flatten(Function &F) {
    // 若基本塊數量 <= 1, 無需平坦化
    if (F.size() <= 1) {
        return false;
    }

    // 避免處理特定函式, 例如 basic_ostream
    if (F.getName().str().find("$basic_ostream") != std::string::npos) {
        outs() << "[obf] force_nofla: " << F.getName().str() << "\n";
        return false;
    }

    // 1. 收集除 entryBB 以外的基本塊
    std::vector<BasicBlock *> origBB;
    for (BasicBlock &BB : F) {
        origBB.push_back(&BB);
    }
    // 移除第一個 (entryBB)
    origBB.erase(origBB.begin());
    BasicBlock &entryBB = F.getEntryBlock();

    // 2. 若 entryBB 終結指令是條件跳轉，則嘗試 splitBasicBlock
    bool bEntryBB_isConditional = false;
    if (auto *br = dyn_cast<BranchInst>(entryBB.getTerminator())) {
        if (br->isConditional()) {
            // 檢查 terminator 之後是否還有其他指令
            Instruction *Term = entryBB.getTerminator();
            if (Instruction *NextI = Term->getNextNode()) {
                // 若 terminator 之後還有 IR 指令，才需要分割
                BasicBlock *newBB = entryBB.splitBasicBlock(NextI, "newBB");
                // 把新的 BB 插入陣列最前
                origBB.insert(origBB.begin(), newBB);
            }
            bEntryBB_isConditional = true;
        }
    }

    // 3. 建立分發 (dispatchBB) 與返回 (returnBB) 基本塊
    BasicBlock *dispatchBB = BasicBlock::Create(*CONTEXT, "dispatchBB", &F, &entryBB);
    BasicBlock *returnBB   = BasicBlock::Create(*CONTEXT, "returnBB",   &F, &entryBB);
    // 在 returnBB 裡插入一條無條件跳轉到 dispatchBB
    BranchInst::Create(dispatchBB, returnBB);

    // 將 entryBB 移到 dispatchBB 前
    entryBB.moveBefore(dispatchBB);

    // 4. 若 entryBB 原先是 conditional，則替換其 terminator
    if (bEntryBB_isConditional) {
        Instruction *OldTerm = entryBB.getTerminator();
        BranchInst::Create(dispatchBB, &entryBB);  // 插入新的無條件分支
        OldTerm->eraseFromParent();                // 安全刪除舊terminator
    } else {
        // 否則直接插入分支
        BranchInst::Create(dispatchBB, &entryBB);
    }

    // 5. 在 entryBB 末尾插入 alloca + store 初始化 switch 變數
    int randNumCase = rand();
    auto *brDispatchBB = dyn_cast<BranchInst>(entryBB.getTerminator());
    AllocaInst *swVarPtr = new AllocaInst(TYPE_I32, 0, "swVar.ptr", brDispatchBB);
    new StoreInst(CONST_I32(randNumCase), swVarPtr, brDispatchBB);

    // 6. 在 dispatchBB 裡 load 該 switch 變數
    LoadInst *swVar = new LoadInst(TYPE_I32, swVarPtr, "swVar", false, dispatchBB);

    // 建一個 switch 指令
    BasicBlock *swDefault = BasicBlock::Create(*CONTEXT, "swDefault", &F, returnBB);
    BranchInst::Create(returnBB, swDefault);
    SwitchInst *swInst = SwitchInst::Create(swVar, swDefault, 0, dispatchBB);

    // 7. 將原BB移到returnBB前 & 分配 case
    for (BasicBlock *BB : origBB) {
        BB->moveBefore(returnBB);
        swInst->addCase(CONST_I32(randNumCase), BB);
        randNumCase = rand();
    }

    // 8. 在每個原BB尾端更新switch 變數 & 跳轉到 returnBB
    for (BasicBlock *BB : origBB) {
        Instruction *Term = BB->getTerminator();
        unsigned numSucc  = Term->getNumSuccessors();

        // 若無 successors (e.g. ret), 不處理
        if (numSucc == 0) {
            continue;
        }
        // 若單一路徑
        if (numSucc == 1) {
            // 先取出舊 terminator
            Instruction *OldTerm = BB->getTerminator();
            BasicBlock *sucBB    = OldTerm->getSuccessor(0);

            // 找對應 case
            ConstantInt *numCase = swInst->findCaseDest(sucBB);
            new StoreInst(numCase, swVarPtr, BB);
            // 刪除舊 terminator
            OldTerm->eraseFromParent();
            // 新增無條件 branch 到 returnBB
            BranchInst::Create(returnBB, BB);

        // 若雙路徑(條件)
        } else if (numSucc == 2) {
            Instruction *OldTerm = BB->getTerminator();
            auto *br = dyn_cast<BranchInst>(OldTerm);
            if (!br || !br->isConditional()) {
                // 不是條件跳轉就略過
                continue;
            }
            // true/false 兩分支
            ConstantInt *numCaseTrue  = swInst->findCaseDest(br->getSuccessor(0));
            ConstantInt *numCaseFalse = swInst->findCaseDest(br->getSuccessor(1));

            // 用 select 決定要存哪個 case
            SelectInst *sel = SelectInst::Create(br->getCondition(), numCaseTrue, numCaseFalse, "", OldTerm);
            new StoreInst(sel, swVarPtr, BB);
            // 刪除舊 terminator
            OldTerm->eraseFromParent();
            // 新增無條件 branch
            BranchInst::Create(returnBB, BB);
        }
    }

    // 9. 呼叫 fixStack 來修復 PHI 與逃逸變數
    fixStack(F);

    return true;
}

// --------------------------------------------------
FlatteningPass *llvm::createFlattening(bool flag) {
    return new FlatteningPass(flag);
}

```

這邊把build 好的 llvm 直接替換到 android sdk
```
C:\llvm-project\build
```
```
C:\Users\x213212\AppData\Local\Android\Sdk\ndk\26.1.10909125\toolchains\llvm\prebuilt\windows-x86_64
```
![image](https://hackmd.io/_uploads/SJWT8s9vkl.png)

![image](https://hackmd.io/_uploads/HyPD7h9Pkx.png)
正常編譯成宮是不會有任何訊息這邊要把這些註解
![image](https://hackmd.io/_uploads/Hk2u7nqv1l.png)

# app
```
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
    external fun sub(a: Int, b: Int): Int
    external fun bcf(input: String): String
    external fun fla(x: Int, y: Int): String
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

            val subValue = sub(10, 3)
            Log.d("JNI_MESSAGE", "sub(10,3) = $subValue")

            val bcfValue = bcf("Hi")
            Log.d("JNI_MESSAGE", "bcf(\"Hi\") = $bcfValue")

            val flaValue = fla(2, 5)
            Log.d("JNI_MESSAGE", "fla(2,5) = $flaValue")

        }
    }

```
# jni
```
#include <jni.h>
#include <string>
#include <sstream>
#include <cstdio>  // for snprintf

extern "C" JNIEXPORT jstring JNICALL
Java_com_example_secchat_InputActivity_stringFromJNI(JNIEnv *env, jobject thiz) {
    std::string message = "Hello from C++!";
    return env->NewStringUTF(message.c_str());
}

extern "C" JNIEXPORT jint JNICALL
Java_com_example_secchat_InputActivity_sub(JNIEnv *env, jobject thiz, jint a, jint b) {
    return a - b;
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_example_secchat_InputActivity_bcf(JNIEnv *env, jobject thiz, jstring input) {
    const char* inputStr = env->GetStringUTFChars(input, nullptr);
    if (!inputStr) {
        return env->NewStringUTF("Invalid input");
    }
    std::string result = std::string("BCF: ") + inputStr;
    env->ReleaseStringUTFChars(input, inputStr);
    return env->NewStringUTF(result.c_str());
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_example_secchat_InputActivity_fla(JNIEnv *env, jobject thiz, jint x, jint y) {
    int sum = x + y;
    char buffer[128];
    if (sum < 5) {
        snprintf(buffer, sizeof(buffer), "x = %d, y = %d, x + y 小於 5", x, y);
    } else if (sum == 5) {
        snprintf(buffer, sizeof(buffer), "x = %d, y = %d, x + y 等於 5", x, y);
    } else {
        snprintf(buffer, sizeof(buffer), "x = %d, y = %d, x + y 大於 5", x, y);
    }
    return env->NewStringUTF(buffer);
}

```

![image](https://hackmd.io/_uploads/BkkuS0owyg.png)
![image](https://hackmd.io/_uploads/SJahH0svkl.png)

