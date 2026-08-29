---
title: "llm cli idapro mcp server & 策略共振池+ga實驗"
date: "2025-09-06T22:26:00.000+08:00"
updated: "2025-09-06T22:26:29.244+08:00"
permalink: "/2025/09/llm-cli-idapro-mcp-server-ga.html"
original_url: "https://x8795278.blogspot.com/2025/09/llm-cli-idapro-mcp-server-ga.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-397226814669436253"
tags: ["ida", "llm", "Python"]
layout: post
---

![](https://hackmd.io/_uploads/rJJgz6F9ll.png)

# 最近在透過cli 全自動化開發
這次比較特別一次混合三種主題，主要最近還是探索怎麼用ai去改善，自己寫code的習慣
嘗試了google gemini pro，qwen，codex 其中兩個我有訂閱，直接長出三個分身
基本上只要遵守 規劃流程和驗證 讓他們自己去迭代就可以了，比如說驗證交易系統，自動化寫交易策略，比如說可以讓他們自己使用回測框架自我回測檢查績效，再反過來重複驗證他們的策略提升報酬率，目前弄下來寫了六百多隻策略想做策略共振，實驗下來還是算滿意，確實從共振回測可以觀察出一些提前的規律，最近也有聽演講這邊有看到自動化破解這部分我比較感興趣，看來離全自動化分析破解應該不遠了xd，不過目前好像只有靜態分析，只不過後面如果開發應該大家都要去完善 mcp server 用pyhton 寫一個然後用llm 當大腦，慢慢補足這些相關經驗讓他去呼叫這些tool 就可以。
# 策略共振
![image](https://hackmd.io/_uploads/rJJgz6F9ll.png)
![image](https://hackmd.io/_uploads/B1pxGTK9gx.png)
透過策略在不同時間框架下，量化成某格時間點的震盪指標
![image](https://hackmd.io/_uploads/r1VBG6Fqee.png)
包括每日就可以增量回測近300根k
```c
#!/usr/bin/env bash
# update_all.sh
# 一鍵更新 top_coins 資料、策略訊號、共振圖
# 使用: bash update_all.sh

set -e  # 出錯就中斷

TOP_COINS=(
  BTCUSDT ETHUSDT SOLUSDT XRPUSDT DOGEUSDT BNBUSDT ADAUSDT
)
END_UTC="$(date -u +%F)"        # 例如 2025-08-31（UTC）
for sym in "${TOP_COINS[@]}"; do
  echo "=== [SYNC] $sym ==="
  python3 sync_and_aggregate.py \
    --symbols "$sym" \
    --mode update \
    --start-date 2021-01-01 \
    --end-date "$END_UTC" \
    --csv-output "{symbol}_1m_2021_2025.csv" \
    --parquet-output "{symbol}_1m_2021_2025.parquet" \
    --threads 8 --drop-last-days 1\
    --parquet
done

# ========== STEP 2: 產生/更新策略訊號 (增量模式) ==========
for sym in "${TOP_COINS[@]}"; do
  echo "=== [SIGNALS] $sym ==="
  python3 gen_recoardex_incre.py \
    --symbols "$sym" \
    --incremental \
    --warmup-bars 300 \
    --max-workers 8
done

# ========== STEP 3: 去重清理 ==========
for sym in "${TOP_COINS[@]}"; do
  echo "=== [DEDUP] $sym ==="
  python3 dedupe_lite.py \
    --signals-root ./signals_raw \
    --symbol "$sym"
done

# ========== STEP 4: 畫共振圖 ==========
for sym in "${TOP_COINS[@]}"; do
  echo "=== [PLOT] $sym ==="
  python3 plot_resonance_fast.py --view-resample 1h\
    --symbol "$sym"
done

echo "✅ [DONE] 全部 top_coins 更新完成"

```
額外寫了一個ga 透過deap + vectorbt 透過基因演算法去組合目前策略作空作多最佳組合，
![image](https://hackmd.io/_uploads/BytEmTYcel.png)
起始10000usdt，回測73407 20 min線，在套上以前的交易機器人基本上就是無腦操作了，每天有三個機器人一直幫你作研究

# idapro mcp server
ida pro 沒有的話俄羅斯網站搞一套，網路上 llm 都是用 deepseek , claude 卻沒有人用google gemini 那這部分就用 gemini 來控制ida pro

那我在windows 那麼首先我在要安裝 ida mcp server
https://github.com/mrexodia/ida-pro-mcp?tab=readme-ov-file
在這邊透過
```cmd
pip uninstall ida-pro-mcp
pip install https://github.com/mrexodia/ida-pro-mcp/archive/refs/heads/main.zip
ida-pro-mcp --install
```
安裝
![image](https://hackmd.io/_uploads/B163R2Fqel.png)
你就可以在這邊看到你的mcp server run 起來
![image](https://hackmd.io/_uploads/SyZCAnKqgl.png)

windows 的port fording 給 wsl
![image](https://hackmd.io/_uploads/HkN3JaK9xg.png)
```
REM 將 172.22.96.1:13337 轉到 127.0.0.1:13337
netsh interface portproxy add v4tov4 ^
  listenaddress=172.22.96.1 listenport=13337 ^
  connectaddress=127.0.0.1 connectport=13337

netsh advfirewall firewall add rule name="MCP proxy 13337 (WSL)" dir=in action=allow protocol=TCP localport=13337 remoteip=172.22.96.0/20

之後若要移除：

netsh interface portproxy delete v4tov4 listenaddress=172.22.96.1 listenport=13337
```

```
netstat -ano | findstr LISTENING | findstr :13337
```

run 起 sse server

![image](https://hackmd.io/_uploads/Syew16F9eg.png)
```cmd
uv run ida-pro-mcp --transport http://172.22.96.1:8744/sse
```
gemini add mcp server
```
gemini mcp add --transport sse ida-ida http://172.22.96.1:8744/sse
gemini mcp list 
```

![image](https://hackmd.io/_uploads/SkE-g6t9el.png)
ctrl + t就可以顯示 mcp server tool有哪些可以呼叫了
![image](https://hackmd.io/_uploads/SkTEeaF9eg.png)

這邊嘗試了兩題

# Wyvern CTF Challenge Write-up

This document details the reverse engineering process used to find the password for the Wyvern CTF challenge.

## 1. Initial Analysis

The target file, `wyvern_c85f1be480808a9da350faaa6104a19b.exe`, is a Linux ELF executable despite its `.exe` extension, a common trick in CTF challenges. The program prompts the user for a "dragon's secret" and validates it. The goal is to find the correct secret.

## 2. Decompiling `main`

The analysis began with the `main` function to understand the program's overall structure.

```cpp
/* line: 0, address: 0x40e120 */ int __fastcall main(int argc, const char **argv, const char **envp)
/* line: 1 */ {
/* line: 2 */   __int64 v3; // rdx
/* line: 3 */   int started; // [rsp+24h] [rbp-19Ch] BYREF
/* line: 4 */   _BYTE v6[8]; // [rsp+80h] [rbp-140h] BYREF
/* line: 5 */   _BYTE v7[12]; // [rsp+88h] [rbp-138h] BYREF
/* line: 6 */   _BYTE v8[8]; // [rsp+A0h] [rbp-120h] BYREF
/* line: 7 */   _BYTE v9[8]; // [rsp+A8h] [rbp-118h] BYREF
/* line: 8 */   char s[268]; // [rsp+B0h] [rbp-110h] BYREF
/* line: 9 */   int v11; // [rsp+1BCh] [rbp-4h]
/* line: 10 */ 
/* line: 11, address: 0x40e12b */   v11 = 0;
/* line: 12, address: 0x40e14a */   std::operator<<<std::char_traits<char>>(&std::cout, (unsigned int)\n+-----------------------+\n, envp);
/* line: 13, address: 0x40e164 */   std::operator<<<std::char_traits<char>>(...);
/* line: 29 */   std::operator<<<std::char_traits<char>>(&std::cout, (unsigned int)"Enter the dragon's secret: ", ...);
/* line: 33, address: 0x40e1f5 */   fgets(s, 257, stdin);
/* line: 34, address: 0x40e212 */   std::allocator<char>::allocator(v8);
/* line: 35, address: 0x40e22c */   std::string::string(v9, s, v8);
/* line: 36, address: 0x40e23d */   std::allocator<char>::~allocator(v8);
/* line: 37, address: 0x40e250 */   std::string::string((std::string *)v7, (const std::string *)v9);
/* line: 38, address: 0x40e266 */   started = start_quest(v7);
/* line: 39, address: 0x40e292 */   std::string::~string((std::string *)v7);
/* line: 40, address: 0x40e2a4 */   if ( started == 4919 )
/* line: 41 */   {
/* line: 42, address: 0x40e2bd */     std::string::string((std::string *)v6, (const std::string *)v9);
/* line: 43, address: 0x40e2ce */     reward_strength(v6);
/* line: 44, address: 0x40e2df */     std::string::~string((std::string *)v6);
/* line: 45 */   }
/* line: 46 */   else
/* line: 47 */   {
/* line: 48, address: 0x40e37a */     std::operator<<<std::char_traits<char>>(&std::cout, (unsigned int)"\n[-] You have failed...\n", v3);
/* line: 52 */   }
/* line: 53, address: 0x40e397 */   v11 = 0;
/* line: 54, address: 0x40e3a8 */   std::string::~string((std::string *)v9);
/* line: 55, address: 0x40e3b0 */   return v11;
/* line: 56 */ }
```

**Finding:** The program reads user input, passes it to `start_quest`, and checks if the return value is exactly `4919`. This is the main bypass condition.

## 3. Analyzing `start_quest`

The next step was to decompile `start_quest` to understand how it generates its return value.

```cpp
/* line: 0, address: 0x404350 */ __int64 __fastcall start_quest(std::string *a1)
{
    // ... heavily obfuscated code ...
/* line: 49 */     v5 = std::string::length(v10) - 1LL != legend >> 2;
    // ...
/* line: 83 */   if ( v5 ) // This is the WRONG length path
/* line: 84 */   {
        // ... returns a failure value
/* line: 95 */   }
/* line: 96 */   else // This is the CORRECT length path
/* line: 97 */   {
        // ...
/* line: 108 */     v4 = sanitize_input(v6);
        // ...
/* line: 125 */   return v3; // v3 eventually gets the value from v4
/* line: 126 */   }
}
```

**Findings:**

1.  **Length Check:** The function first checks if the input length (minus the newline character) is equal to `legend >> 2`.
2.  **Content Check:** If the length is correct, the input is passed to another function, `sanitize_input`, whose return value becomes the return value of `start_quest`.

## 4. Finding the Password Length

To pass the length check, the value of the global variable `legend` was needed. Reading it by name or address failed, but reading the raw memory at its address (`0x610138`) succeeded.

- **Memory at `0x610138`:** `0x73 0x0 0x0 0x0 0x64 0x0 0x0 0x0`
- This was interpreted as two 32-bit integers: `115` and `100`.
- The code for populating the `hero` array (see below) contained 28 elements. This confirmed the correct `legend` value was `115`.
- **Calculation:** `115 >> 2` (115 divided by 4) is `28`. The required password length is **28**.

## 5. The Core Algorithm: `transform_input` and `sanitize_input`

Decompiling `sanitize_input` revealed a loop that called `transform_input` on an ever-growing prefix of the user's input and compared it to values from a `hero` array.

Decompiling `transform_input` revealed its simple purpose:

```cpp
/* line: 0, address: 0x4014b0 */ __int64 __fastcall transform_input(__int64 a1)
{
    // ... obfuscated loop ...
/* line: 71 */         *v15 += *v2; // *v15 is the accumulator, *v2 is the character
    // ...
/* line: 126 */   return v7; // returns the final sum
}
```

**Finding:** `transform_input` simply returns the sum of the ASCII values of the characters it receives.

This leads to the central validation logic in `sanitize_input`:
`sum(password[0...i]) == hero[i]` for `i` in `0..27`.

## 6. Deriving the Solution

The validation logic can be reversed to solve for each character of the password:

- `password[0]` = `hero[0]`
- `password[1]` = `hero[1] - hero[0]`
- `password[2]` = `hero[2] - hero[1]`
- **General Formula:** `password[i] = hero[i] - hero[i-1]`

## 7. Finding the `hero` Array

Reading the `hero` global variable from memory failed, showing it was uninitialized. Analysis of `start_quest` showed that it builds the `hero` vector at runtime by pushing a series of hardcoded values.

```cpp
/* line: 21, address: 0x4043f0 */     std::vector<int>::push_back(&hero, &secret_100);
/* line: 22, address: 0x404409 */     std::vector<int>::push_back(&hero, &secret_214);
/* line: 23, address: 0x404422 */     std::vector<int>::push_back(&hero, &secret_266);
// ... and so on
```

The values of the `hero` array were extracted directly from these variable names:
`[100, 214, 266, 369, 417, 527, 622, 733, 847, 942, 1054, 1106, 1222, 1336, 1441, 1540, 1589, 1686, 1796, 1891, 1996, 2112, 2165, 2260, 2336, 2412, 2498, 2575]`

## 8. Final Password Calculation

Applying the formula `password[i] = hero[i] - hero[i-1]` to the `hero` array:

- `p[0] = 100` -> 'd'
- `p[1] = 214 - 100 = 114` -> 'r'
- `p[2] = 266 - 214 = 52` -> '4'
- `p[3] = 369 - 266 = 103` -> 'g'
- `p[4] = 417 - 369 = 48` -> '0'
- `p[5] = 527 - 417 = 110` -> 'n'
- `p[6] = 622 - 527 = 95` -> '_'
- `p[7] = 733 - 622 = 111` -> 'o'
- `p[8] = 847 - 733 = 114` -> 'r'
- `p[9] = 942 - 847 = 95` -> '_'
- `p[10] = 1054 - 942 = 112` -> 'p'
- `p[11] = 1106 - 1054 = 52` -> '4'
- `p[12] = 1222 - 1106 = 116` -> 't'
- `p[13] = 1336 - 1222 = 114` -> 'r'
- `p[14] = 1441 - 1336 = 105` -> 'i'
- `p[15] = 1540 - 1441 = 99` -> 'c'
- `p[16] = 1589 - 1540 = 49` -> '1'
- `p[17] = 1686 - 1589 = 97` -> 'a'
- `p[18] = 1796 - 1686 = 110` -> 'n'
- `p[19] = 1891 - 1796 = 95` -> '_'
- `p[20] = 1996 - 1891 = 105` -> 'i'
- `p[21] = 2112 - 1996 = 116` -> 't'
- `p[22] = 2165 - 2112 = 53` -> '5'
- `p[23] = 2260 - 2165 = 95` -> '_'
- `p[24] = 2336 - 2260 = 76` -> 'L'
- `p[25] = 2412 - 2336 = 76` -> 'L'
- `p[26] = 2498 - 2412 = 86` -> 'V'
- `p[27] = 2575 - 2498 = 77` -> 'M'

### Final Password

**`dr4g0n_or_p4tric1an_it5_LLVM`**
# Baby Rev CTF Challenge Write-up

This document details the process used to solve the `baby_rev` CTF challenge.

## 1. Challenge Description

The goal of this challenge is to decompile the binary and inspect the code to find a Base64 encoded flag.

## 2. Solution Process

The analysis followed the provided solution steps, which proved to be a direct path to the flag.

### Step 1: Locating the `init` Function

Following the provided hints, the analysis focused on the `init` function, which was suspected of initializing the flag variable. The function's address was found using `get_function_by_name`.

- **Tool:** `get_function_by_name(name = "init")`
- **Result:** The address of `init` was found to be `0x1276`.

### Step 2: Decompiling `init` and Finding the Encoded Flag

The `decompile_function` tool was used on the address `0x1276`. The decompiled code immediately revealed a `qmemcpy` operation containing a long, suspicious string ending in `==`.

```cpp
/* line: 0, address: 0x1276 */ __int64 init()
{
  __int64 result; // rax
  _QWORD v1[16]; // [rsp+0h] [rbp-90h] BYREF
  int j; // [rsp+88h] [rbp-8h]
  int i; // [rsp+8Ch] [rbp-4h]
  __int64 savedregs; // [rsp+90h] [rbp+0h] BYREF

/* line: 8, address: 0x1288 */   qmemcpy(
    v1,
    "Y3Nhd2N0ZntOM3Yzcl9wcjA3M2M3X3MzbnMxNzF2M18xbmYwcm00NzEwbl91czFuZ19qdXM3XzNuYzBkMW5nIV8jM25jMGQxbmdfMXNfbjB0XzNuY3J5cDcxMG4hfQ==",
    sizeof(v1));
/* line: 12, address: 0x1356 */   result = 0x3D3D51666834474DLL;
/* line: 13, address: 0x1364 */   for ( i = 0; i <= 15; ++i )
  {
/* line: 15, address: 0x136d */     for ( j = 0; j <= 7; ++j )
    {
/* line: 17, address: 0x13af */       result = (__int64)&flag + 8 * i + j;
/* line: 18, address: 0x13b2 */       *(_BYTE *)result = *((_BYTE *)&savedregs + 8 * i + j - 144);
    }
  }
/* line: 21, address: 0x13ca */   return result;
}
```

The string `Y3Nhd2N0ZntOM3Yzcl9wcjA3M2M3X3MzbnMxNzF2M18xbmYwcm00NzEwbl91czFuZ19qdXM3XzNuYzBkMW5nIV8jM25jMGQxbmdfMXNfbjB0XzNuY3J5cDcxMG4hfQ==` was identified as the Base64 encoded flag.

### Step 3: Decoding the Flag

The final step was to decode the Base64 string. This was done using a simple Python command via the `run_shell_command` tool.

- **Command:**
```bash
python3 -c 'import base64; print(base64.b64decode("Y3Nhd2N0ZntOM3Yzcl9wcjA3M2M3X3MzbnMxNzF2M18xbmYwcm00NzEwbl91czFuZ19qdXM3XzNuYzBkMW5nIV8jM25jMGQxbmdfMXNfbjB0XzNuY3J5cDcxMG4hfQ==").decode("utf-8"))'
```

## 3. Conclusion

The decoded string revealed the final flag.

**Flag:** `csawctf{N3v3r_pr073c7_s3ns171v3_1nf0rm4710n_us1ng_jus7_3nc0d1ng!_#3nc0d1ng_1s_n0t_3ncryp710n!}`

The challenge serves as a reminder that encoding is not a form of security and can be easily reversed.

兩題ctf 都可以找到正解並且把步驟都列出來。還蠻扯，不知道是不是上網找解答哈哈，第二題也還好，定位到那一個function 按f5就可以轉成偽ccode 看到那串後在
```python
python3 -c 'import base64; print(base64.b64decode("Y3Nhd2N0ZntOM3Yzcl9wcjA3M2M3X3MzbnMxNzF2M18xbmYwcm00NzEwb…  csawctf{N3v3r_pr073c7_s3ns171v3_1nf0rm4710n_us1ng_jus7_3nc0d1ng!_#3nc0d1ng_1s_n0t_3ncryp710n!}  
```
![image](https://hackmd.io/_uploads/HyO0x6K5xx.png)

