---
title: "golang nft 原理與呼叫 & ipfs"
date: "2022-02-14T16:50:00.001+08:00"
updated: "2022-02-14T16:51:18.322+08:00"
permalink: "/2022/02/golang-ntf-ipfs.html"
original_url: "https://x8795278.blogspot.com/2022/02/golang-ntf-ipfs.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5589963865175405337"
tags: ["Go", "ntf"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Go_Logo_Blue.svg/1200px-Go_Logo_Blue.svg.png)

# golang nft
在快速上手的文章內已經有大致介紹怎麼去產生一個ntf,今天background 補一補就可以來寫一下了，在網路上找了一下都是nodejs 去呼叫，能不能用golang呼叫呢我們來看一下
https://ithelp.ithome.com.tw/articles/10269418
https://blog.aotoki.me/posts/2021/09/21/getting-started-nft/

https://blog.csdn.net/qq_37133717/article/details/80516917

https://ksin751119.medium.com/%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8-golang-%E5%91%BC%E5%8F%AB-solidity-contract-call-function-%E4%B8%8D%E6%9C%83%E7%9C%9F%E6%AD%A3%E5%9F%B7%E8%A1%8C-transaction-269648eb4a5

https://www.twblogs.net/a/5f04eaa0ca069a6e811d298f
# Hardhat
經過幾年的發展區塊鏈相關的開發工具越來越成熟，我們可以直接透過 Hardhat 這個套件撰寫測試、部署智慧型合約。
```bahs
mkdir MyNFT
yarn add -D hardhat && npx hardhat
```
![](https://i.imgur.com/AUdnmVB.png)

# OpenZeppelin 實作 ECR721 非常的簡單，我們先將基礎合約加入專案。
```bahs
yarn add @openzeppelin/contracts
```
在部屬的方面我們使用nodejs 來部屬

# deploy
```bash
.
├── README.md
├── artifacts
│   ├── @openzeppelin
│   ├── build-info
│   ├── contracts
│   └── hardhat
├── cache
│   └── solidity-files-cache.json
├── contracts
│   ├── Greeter.sol
│   ├── MyNFT.sol
│   ├── README.md
│   └── package.json
├── hardhat.config.js
├── package-lock.json
├── package.json
├── scripts
│   ├── deploy.js
│   ├── mint.js
│   └── sample-script.js
├── sol
│   └── output 
├── sources
│   ├── MyNFT.sol
│   ├── Store.sol
│   ├── contracts
│   ├── golangMyNFT.sol
│   └── output
├── test
│   └── sample-test.js
└── yarn.lock
```
# OpenZeppelin gen ECR721 nodejs

```bash
yarn add @openzeppelin/contracts
```
```solidity
pragma solidity ^0.8.0;
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
contract MyNFT is ERC721, Ownable {
  using Counters for Counters.Counter;
  using Strings for uint256;
  Counters.Counter private _tokenIds;
  mapping (uint256 => string) private _tokenURIs;

  constructor() ERC721("MyNFT", "MNFT") {}
  function _setTokenURI(uint256 tokenId, string memory _tokenURI)
    internal
    virtual
  {
    _tokenURIs[tokenId] = _tokenURI;
  }

  function tokenURI(uint256 tokenId)
    public
    view
    virtual
    override
    returns (string memory)
  {
    require(_exists(tokenId), "ERC721Metadata: URI query for nonexistent token");
    string memory _tokenURI = _tokenURIs[tokenId];
    return _tokenURI;
  }

  function mint(address recipient, string memory uri)
    public
    returns (uint256)
  {
    _tokenIds.increment();
    uint256 newItemId = _tokenIds.current();
    _mint(recipient, newItemId);
    _setTokenURI(newItemId, uri);
    return newItemId;
  }
}
```
# gen ECR721 nodejs to golang
OpenZeppelin  因為安全因素寫了模板那麼這些模板
```solidity
import "@openzeppelin\....
```
實際上就是nodejs專案里的sol
![](https://i.imgur.com/d0tQqRV.png)
那麼我們只要移出來基本上就可以進行編譯
```solidity
pragma solidity ^0.8.0;
import "/contracts/token/ERC721/ERC721.sol";
import "/contracts/utils/Counters.sol";
import "/contracts/access/Ownable.sol";
contract MyNFT is ERC721, Ownable {
  using Counters for Counters.Counter;
  using Strings for uint256;
  Counters.Counter private _tokenIds;
  mapping (uint256 => string) private _tokenURIs;

  constructor() ERC721("MyNFT", "MNFT") {}
  function _setTokenURI(uint256 tokenId, string memory _tokenURI)
    internal
    virtual
  {
    _tokenURIs[tokenId] = _tokenURI;
  }

  function tokenURI(uint256 tokenId)
    public
    view
    virtual
    override
    returns (string memory)
  {
    require(_exists(tokenId), "ERC721Metadata: URI query for nonexistent token");
    string memory _tokenURI = _tokenURIs[tokenId];
    return _tokenURI;
  }

  function mint(address recipient, string memory uri)
    public
    returns (uint256)
  {
    _tokenIds.increment();
    uint256 newItemId = _tokenIds.current();
    _mint(recipient, newItemId);
    _setTokenURI(newItemId, uri);
    return newItemId;
  }
}
```
照以前的編譯流程
```bash
 docker run -v ~/golang/nodejs/sources:/sources ethereum/solc:stable -o /sources/output --abi --bin /sources/Store.sol
 abigen --bin=MyNFT.bin --abi=MyNFT.abi --pkg=store --out=MyNFT.go
```
到這邊我們就得到了合約檔案
![](https://i.imgur.com/6VrvES3.png)

# hardhat.config.js
我們先用nodejs 進行部屬
![](https://i.imgur.com/RlIhMrF.png)

```jsx
require("@nomiclabs/hardhat-waffle");

// This is a sample Hardhat task. To learn how to create your own go to
// https://hardhat.org/guides/create-task.html
const PRIVATE_KEY = process.env.PRIVATE_KEY;
task("accounts", "Prints the list of accounts", async (taskArgs, hre) => {
  const accounts = await hre.ethers.getSigners();

  for (const account of accounts) {
    console.log(account.address);
  }
});

// You need to export an object to set up your config
// Go to https://hardhat.org/config/ to learn more

/**
 * @type import('hardhat/config').HardhatUserConfig
 */
module.exports = {
  solidity: "0.8.3",
  // defaultNetwork: "hardhat",
  networks: {
    matic: {
      url: "http://172.20.64.1:7545", //這邊填入我們的ganache server
      accounts: ["f34d7cf0277f16e5b3a17a6f4997447c95e15510dacaa7b584171a75c45d7a7e"],
        //accounts 填入我們的  ganache 的帳號
    },
  }
};

```
# /script/deploy.js
包括之前的目錄架構 我們還要把智能合約編成 golang
部屬合約
```bash
const hre = require("hardhat");

async function main() {
  const NFT = await hre.ethers.getContractFactory("MyNFT");
  const nft = await NFT.deploy();
	await nft.deployed();

	console.log("NFT deployed to:", nft.address);
}

main().then(() => process.exit(0)).catch(error => {
  console.error(error);
  process.exit(1);
});
```
![](https://i.imgur.com/9Ln7KS8.png)
![](https://i.imgur.com/Z0aHy3u.png)
# /script/mint.js
其中 url使用的一般的網址
https://cf.shopee.tw/file/fa65fb72e2b17594b3f1f5b6dec89382_tn
```
npx hardhat run scripts/mint.js --network matic
```
進行發布 nft
![](https://i.imgur.com/OxxsxB3.png)
![](https://i.imgur.com/tMdl0hO.png)

```bash
const hre = require("hardhat");
require("dotenv").config();

const WALLET_ADDRESS ="0x2ae127Cc29590d09A72B40F00b9802163aB3B248"; //我們的錢包
const CONTRACT_ADDRESS = "0x66Ed606D1359468258fd60267D0D4041CDBD13f8" //我們的合約地址

async function main() {
  const NFT = await hre.ethers.getContractFactory("MyNFT");

  const URI = "https://cf.shopee.tw/file/fa65fb72e2b17594b3f1f5b6dec89382_tn" //test

	const contract = NFT.attach(CONTRACT_ADDRESS);
	await contract.mint(WALLET_ADDRESS, URI);

  console.log("NFT minted:", contract);
  
}

main().then(() => process.exit(0)).catch(error => {
  console.error(error);
  process.exit(1);
});
```

# check ntf smart Contracts
https://blockcast.it/2019/10/21/mica-research-1-min-intro-of-ipfs/
我們知道最夯的 ntf 它裡面只是把url 換成 ipfs那麼我們來看怎麼取得 剛才ECR721合約裡的 url

```go
func main (){
    address := common.HexToAddress("0x66Ed606D1359468258fd60267D0D4041CDBD13f8")
	instance, err := NewStore(address, client)
	if err != nil {
		log.Fatal(err)
	}
	// var number []byte
	// number = abi.U256(big.NewInt(0))
	fmt.Println("contract is loaded")
	a := big.NewInt(1)
	// CallOpts := new(bind.CallOpts)
	fmt.Println(a)

	geturl, err := instance.TokenURI(nil, a)
	if err != nil {
		log.Fatal(err)
	}
	// // _ = instance
	fmt.Println(instance)
	fmt.Println(geturl)
    
}
```
![](https://i.imgur.com/gcjzFop.png)
到此比較新型的區塊鏈技術應該就完成，ipfs 應該也可以自己架設，一個類似nft dapp 原理大致是這樣，其他應用就看大家的創意了，更多技術原理看這篇 for nodejs
https://ithelp.ithome.com.tw/articles/10278782
它裡面包含應用的原理與實現我覺得講得很讚
大致上的意思就是大家挖的礦變成其他東西給替代，類似於抽獎大家每次挖的地方都不一樣，到最後可能合約某些value 會對應到某個帳號，有看到幾篇文章就是你可以識別那些eth 是你的。
https://medium.com/7sevencoin/erc20%E5%92%8Cerc721%E4%B8%8D%E4%B8%80%E6%A8%A3%E5%9C%A8%E5%93%AA%E8%A3%A1-2e550bb0bea3

