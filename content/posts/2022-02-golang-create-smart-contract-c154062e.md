---
title: "golang create smart contract"
date: "2022-02-14T12:27:00.001+08:00"
updated: "2022-02-14T12:27:17.420+08:00"
permalink: "/2022/02/golang-create-smart-contract.html"
original_url: "https://x8795278.blogspot.com/2022/02/golang-create-smart-contract.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2804133945275435017"
tags: ["eth"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Go_Logo_Blue.svg/1200px-Go_Logo_Blue.svg.png)

# install solidity
https://docs.soliditylang.org/en/v0.8.11/installing-solidity.html
install solc

```bahs
docker run ethereum/solc:stable --help
You can also specify release build versions in the tag, for example, for the 0.5.4 release.

docker run ethereum/solc:0.5.4 --help
To use the Docker image to compile Solidity files on the host machine mount a local folder for input and output, and specify the contract to compile. For example.

docker run -v /local/path:/sources ethereum/solc:stable -o /sources/output --abi --bin /sources/Contract.sol
```

# create smart contract
```bahs

root@HOME-X213212:~/golang/nodejs/sources# tree
.
├── Store.sol
└── output
    ├── Store.abi
    ├── Store.bin
    └── Store.go

1 directory, 4 files
```

我們實際要先來撰寫合約
```solidity
pragma solidity ^0.8.3;
contract Store {
 event ItemSet(bytes32  key, bytes32  value);

  string public  version;
  mapping (bytes32 => bytes32) public items;

  constructor(string memory _version) public {
    version = _version;
  }

  function setItem(bytes32  key, bytes32  value) external {
    items[key] = value;
    emit ItemSet(key, value);
  }
}
```
# compiler contract
```bash
 docker run -v ~/golang/nodejs/sources:/sources ethereum/solc:stable -o /sources/output --abi --bin /sources/Store.sol
 abigen --bin=Store.bin --abi=Store.abi --pkg=store --out=Store.go
```
引入file 怪怪的 我直接從這裡複製到 main.go 檔案底下
![](https://i.imgur.com/Ow2HP7t.png)

![](https://i.imgur.com/K1Pc6Uf.png)

就目前理解 eth 在這些區塊鏈中實現一個虛擬機，那麼礦工中的挖礦可能可以類似虛擬機的指令執行，而達成指令的操作實現一個小型的程式。

