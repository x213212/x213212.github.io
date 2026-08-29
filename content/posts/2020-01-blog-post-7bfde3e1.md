---
title: "區塊鏈 初探 (一) 架設 乙太坊 私有鍊 編寫智能合約"
date: "2020-01-04T06:31:00.000+08:00"
updated: "2020-02-27T18:37:58.997+08:00"
permalink: "/2020/01/blog-post.html"
original_url: "https://x8795278.blogspot.com/2020/01/blog-post.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-4119871192314301553"
tags: ["geth", "solidity", "Tutorial"]
layout: post
---

很早就想來實作了，來看一下大概大多數都是用 go/node.js 寫，java好像很少看到我們來針對 這個部分補一下，搞一個最初版來玩看看。  

總共需要  

Ethereum Wallet 錢包  

geth 架設私有鏈  

Remix 編寫 智能合約
總而言之呢，就是架設一個測試環境讓自己能開發區塊鏈，開始吧!
# Geth

<https://geth.ethereum.org/downloads/>  

直接下載最後一個版本就好囉!  

![](https://i.imgur.com/MYyWa74.png)

  

下載好後 全部解壓所到一個資料夾吧  

![](https://i.imgur.com/cvfLdJb.png)

# 配置參數

配置我們的創世塊，這邊大家可以去認識一下gasLimit 燃料，這邊手續費在弄智能合約的地方卡很多次以後再補。
```
{
    "config": {
        "chainId": 123,
        "homesteadBlock": 0,
  "eip150Block": 0,
        "eip155Block": 0,
        "eip158Block": 0
    },
    "nonce": "0x0000000000000042",
    "difficulty": "0x010",
    "mixhash": "0x0000000000000000000000000000000000000000000000000000000000000000",
    "coinbase": "0x0000000000000000000000000000000000000000",
    "timestamp": "0x00",
    "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
    "extraData": "0x0000000000000000000000000000000000000000000000000000000000000000",
    "gasLimit": "0xffffffff",
    "alloc": {
   "0x21d10c5e114a959e6e92c6f5f0ffcbe7df7785f1": {"balance": "99999999999999999999999999999999"},
   "0x0000000000000000000000000000000000000002": {"balance": "222222222"}
 }
}
```
geth --datadir data init testuser.json
# 啟動geth

這些參數都配好囉，比較關鍵的  

–ipcpath geth.ipc
這個可以讓你的 Ethereum Wallet 去抓你的網路  

變成provider network測試環境  

![](https://i.imgur.com/wllUqAG.png)

  

進去就看到我們的所有帳戶囉 詳細檔案都在你下面 的  

datadir裡面，你都沒調的話 預設就是挖礦，現在還有人在挖嗎哈哈

![](https://i.imgur.com/emFyv6u.png)

```
geth --datadir data --networkid 123 --rpc --rpccorsdomain "*" --nodiscover --rpcapi="db,eth,net,web3,personal " --allow-insecure-unlock console --ipcpath geth.ipc
這邊到這裡就大概ok了，想玩其他指令我下面會來整理一下。
```
# 指令

- 創建錢包

```
personal.newAccount()
```

- 創建用戶

```
personal.newAccount()
```

- 查看節點訊息

```
admin.nodeInfo
```

- 挖礦 裡面可以填參數，用 cpu 挖

```
miner.start()
miner.stop()
```

- 查看帳戶餘額

```
eth.getBalance(eth.accounts[0])
```

- 轉帳

```
eth.sendTransaction({from:”來源帳戶地址”, to:”目的地帳戶地址”, value:web3.toWei(金額, “ether”)})
```

- 帳戶交易解鎖

```
personal.unlockAccount(eth.accounts[0])
```

- 用交易查看區塊資訊

```
eth.getTransaction(“交易hash”)
```

- 通過區塊編號查看區塊資訊

```
eth.getBlock(區塊編號)
```

- 查看交易詳細資訊

```
getTransactionReceipt(“交易hash”)
```
# 智能合約編寫與啟動

Ethereum Wallet 錢包  

![](https://i.imgur.com/FZzp4J5.png)

  

Remix  

![](https://i.imgur.com/t6YmXiB.png)

  

好久沒進來要跑到這邊 去搜尋 run 和 compiler就可以  

![](https://i.imgur.com/Ntyr88H.png)

# 編寫合約

這個腳本可以先去看一下 solidity 是什麼，大家都知道有 jvm ,這個東西叫做EVM 類似跨平台編譯的東西也就是乙太虛擬機，  

這個合約是說產生一個虛擬的KV數據讓我們可以去練習操作一下。
```
pragma solidity 0.4.25;

contract Token {
    
    mapping(string => uint) balanceByName;
    event setBalanceEvent(string name,uint balance);
    
    function setBalance(string  memory _name, uint _balance) public {
        balanceByName[_name] = _balance;
        emit setBalanceEvent(_name,_balance);
    }
    function returnBalance (string memory _name)  public view returns (uint){
        return balanceByName[_name];
    }
}
```
更多合約  

<https://etherscan.io/>  

![](https://i.imgur.com/AmHSynb.png)

  

當然大家知道合約就是要給大家看的，所以這邊好像是接口的概念，  

我們隨便點進去一個  

![](https://i.imgur.com/D7NCLuT.png)

可以看到這些接口都是開放給大家看的後面會說怎麼用 JAVA 調用 智能合約，有了這個概念後我們來編譯我們的合約。  

![](https://i.imgur.com/RmhawpZ.png)

  

編譯完後，到我們這個畫面就可以看到我們的 執行合約的地方  

![](https://i.imgur.com/T8s6kYz.png)

當你把你的合約發佈上去，就可以發現你的 geth 有反應了  

不過會沒動作。  

當然你也要先 新增帳戶先，才能開始執行智能合約  

記得儲值!  

![](https://i.imgur.com/tUNrSQO.png)

看到這個畫面就是沒有解鎖帳戶
```
authentication needed: password or unlock
```
我們來解鎖帳戶
```
personal.unlockAccount(eth.accounts[0])

personal.unlockAccount(帳戶 hash)
```
解鎖帳戶  

![](https://i.imgur.com/1gVzUF1.png)

  

輸入完帳號密碼 出現 ture 就是沒問題了，會發現我們geth 有收到合約但是沒動作。  

![](https://i.imgur.com/Ux6gLSn.png)

  

這個時候就可以開始挖礦囉
```
miner.start()
```

![](https://i.imgur.com/RRuAYWS.png)

  

可以看到我們發佈剛剛的合約  

![](https://i.imgur.com/epwKZjj.png)

  

這個意思就知道  

有兩個按鈕，這兩個按鈕就是我們剛剛編寫的合約裡面兩個函數，  

要不要顯示就是取決於 函數後面的 view，更多語法我在這邊就不多講了。  

![](https://i.imgur.com/bHAuqqx.png)

我們回到上面去複製其他帳戶 的帳號在切回去本尊

![](https://i.imgur.com/A76zbFk.png)

  

我們填入數據
```
0x1c3f3c25928a0522c5c521e1c033f9d3ac409980,100
```
這邊數據要好好設置，不同版本可能發生記憶體溢位，被 hack利用就糟了
好了之後可以看到  

![](https://i.imgur.com/4vpAjL8.png)

  

我們在把我們的第二個用戶 address 放到下面  

可以看到我們存下了 100 塊。  

這邊就簡單的範例，還有帳戶對帳戶 互轉 更進階 運用可能 投票系統 … 衍生出 之前的我爬蟲弄得 bcoin水龍頭 賭博系統。
這一篇大概這樣 下一章節講調用，應該蠻簡單的。
