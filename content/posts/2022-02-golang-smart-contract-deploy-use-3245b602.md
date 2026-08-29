---
title: "golang smart contract deploy & use (ganache & geth)"
date: "2022-02-14T12:48:00.002+08:00"
updated: "2022-02-14T12:48:11.762+08:00"
permalink: "/2022/02/golang-smart-contract-deploy-use.html"
original_url: "https://x8795278.blogspot.com/2022/02/golang-smart-contract-deploy-use.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3078982947490767695"
tags: ["ganache", "geth"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Go_Logo_Blue.svg/1200px-Go_Logo_Blue.svg.png)

# golang geth  test
# deploy

![](https://i.imgur.com/fMa3QTo.png)

```go
func main (){
    pk, err := keyStoreToPrivateKey("/root/golang/mvc/UTC--2020-01-03T05-58-33.219268500Z--21d10c5e114a959e6e92c6f5f0ffcbe7df7785f1", "654321")
	if err != nil {
		log.Fatal(err)
	}
	privateKey, err := crypto.HexToECDSA(pk)
	if err != nil {
		log.Fatal("privateKey ", err)

	}

	publicKey := privateKey.Public()

	publicKeyECDSA, ok := publicKey.(*ecdsa.PublicKey)
	if !ok {
		log.Fatal("cannot assert type: publicKey is not of type *ecdsa.PublicKey")
	}

	fromAddress := crypto.PubkeyToAddress(*publicKeyECDSA)

	nonce, err := client.PendingNonceAt(context.Background(), fromAddress)
	if err != nil {
		log.Fatal(err)
	}

	gasPrice, err := client.SuggestGasPrice(context.Background())
	if err != nil {
		log.Fatal(err)
	}

	auth := bind.NewKeyedTransactor(privateKey)
	auth.Nonce = big.NewInt(int64(nonce))
	auth.Value = big.NewInt(0)     // in wei
	auth.GasLimit = uint64(300000) // in units
	auth.GasPrice = gasPrice

	input := "1.0"
	address, tx, instance, err := DeployStore(auth, client, input)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(address.Hex())   // 0x147B8eb97fD247D06C4006D269c90C1908Fb5D54
	fmt.Println(tx.Hash().Hex()) // 0xdae8ba5444eefdc99f4d45cd0c4f24056cba6a02cefbf78066ef9f4188ff7dc0
	fmt.Println(instance)
    
}
```
# load contract
![](https://i.imgur.com/AO0901y.png)

```go
	address := common.HexToAddress("0x3484dfb6aCED276ABC3b9824266f03295139507A")
	instance, err := NewStore(address, client)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("contract is loaded")
	fmt.Println(instance)
```

# golang ganache test
那麼要加速一個合約的部屬與debug我們來開始學習新的ganache
這樣我們就不用像在geth 要在挖礦讓我們的合約才能執行。
![](https://i.imgur.com/roAiyf5.png)
![](https://i.imgur.com/IGJbrIl.png)
![](https://i.imgur.com/lFnfj5W.png)
![](https://i.imgur.com/13g6pbV.png)
我們是run 在wsl 來重選一下網路
![](https://i.imgur.com/2fjcvGa.png)
確實連接到![](https://i.imgur.com/9J2JDcq.png)

https://medium.com/@daniel.mars622/%E9%96%8B%E7%99%BC%E8%88%87%E6%B8%AC%E8%A9%A6dapp%E5%85%8D%E8%A3%9D%E7%AF%80%E9%BB%9E-c9f446128da4
https://medium.com/my-blockchain-development-daily-journey/%E4%BB%8B%E7%B4%B9-truffle-suite-%E5%92%8Cdapp-development-7d747d13cf2b

那麼照前面的合約部屬我們要換成

privateKey
![](https://i.imgur.com/c9hahyX.png)

```go
func main (){
    client, err := ethclient.Dial("http://172.20.64.1:7545")
	if err != nil {
		log.Fatal(err)
	}
	privateKey, err := crypto.HexToECDSA("a1fbeac5c525dbe3c1bac85bd0f5ba369ec693282e22eb89e36e26059ad36e18")
	if err != nil {
		log.Fatal(err)
	}

	publicKey := privateKey.Public()
	publicKeyECDSA, ok := publicKey.(*ecdsa.PublicKey)
	if !ok {
		log.Fatal("cannot assert type: publicKey is not of type *ecdsa.PublicKey")
	}
	gasPrice, err := client.SuggestGasPrice(context.Background())
	if err != nil {
		log.Fatal(err)
	}

	auth := bind.NewKeyedTransactor(privateKey)
	auth.Nonce = big.NewInt(int64(nonce))
	auth.Value = big.NewInt(0) // in wei
	auth.GasLimit = uint64(0)  // in units
	auth.GasPrice = gasPrice

	input := "1.0"
	address, tx, instance, err := DeployStore(auth, client, input)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(address.Hex())   // 0x3B394d5cb1e395744DD99433619556351BE34689
	fmt.Println(tx.Hash().Hex()) // 0x3232ae7f29e6fb43aec8f49a8a4221a40a4854cc826cc90e556991efb7d4757e
	fmt.Println(instance)
    
}
```
部屬完可以看到 eth變了
![](https://i.imgur.com/pfvj3Zj.png)

# load smart contr

```go
	address := common.HexToAddress("0x3B394d5cb1e395744DD99433619556351BE34689")
	instance, err := NewStore(address, client)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("contract is loaded")
```

# get contract value

![](https://i.imgur.com/yLSXCgU.png)
```go
	address := common.HexToAddress("0x3B394d5cb1e395744DD99433619556351BE34689")
	instance, err := NewStore(address, client)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("contract is loaded")
	version, err := instance.Version(nil)
	if err != nil {
		log.Fatal(err)
	}
	// // _ = instance
	fmt.Println(instance)
	fmt.Println(version)
```
# write smart contract
換個人
 PRIVATE KEY
![](https://i.imgur.com/A91gHH1.png)
![](https://i.imgur.com/Gb1SyWz.png)
![](https://i.imgur.com/icE1A4G.png)

```go

	client, err := ethclient.Dial("http://172.20.64.1:7545")
	if err != nil {
		log.Fatal(err)
	}
	privateKey, err := crypto.HexToECDSA("38a30755101fb988c5568d4b50655249245bdf28d0ffae12d726a0d5654d0c2f")
	if err != nil {
		log.Fatal(err)
	}

	publicKey := privateKey.Public()
	publicKeyECDSA, ok := publicKey.(*ecdsa.PublicKey)
	if !ok {
		log.Fatal("cannot assert type: publicKey is not of type *ecdsa.PublicKey")
	}

	fromAddress := crypto.PubkeyToAddress(*publicKeyECDSA)
	nonce, err := client.PendingNonceAt(context.Background(), fromAddress)
	if err != nil {
		log.Fatal(err)
	}
	gasPrice, err := client.SuggestGasPrice(context.Background())
	if err != nil {
		log.Fatal(err)
	}

	auth := bind.NewKeyedTransactor(privateKey)
	auth.Nonce = big.NewInt(int64(nonce))
	auth.Value = big.NewInt(0) // in wei
	auth.GasLimit = uint64(0)  // in units
	auth.GasPrice = gasPrice

	address := common.HexToAddress("0x3B394d5cb1e395744DD99433619556351BE34689")
	instance, err := NewStore(address, client)
	if err != nil {
		log.Fatal(err)
	}

	key := [32]byte{}
	value := [32]byte{}
	copy(key[:], []byte("foo"))
	copy(value[:], []byte("bar"))

	tx, err := instance.SetItem(auth, key, value)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("tx sent: %s", tx.Hash().Hex()) 

	result, err := instance.Items(nil, key)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(string(result[:])) // "bar"

```
![](https://i.imgur.com/xqBJtNL.png)
![](https://i.imgur.com/Tp0zicx.png)

# get smart contract  binary code
![](https://i.imgur.com/f0w6KYe.png)
![](https://i.imgur.com/JUv9AiX.png)

```go
	contractAddress := common.HexToAddress("0x3B394d5cb1e395744DD99433619556351BE34689")
	bytecode, err := client.CodeAt(context.Background(), contractAddress, nil) // nil is latest block
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(hex.EncodeToString(bytecode)) // 60806...10029

```

