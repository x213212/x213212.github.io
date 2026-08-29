---
title: "golang dtm server"
date: "2022-02-12T09:24:00.004+08:00"
updated: "2022-02-12T09:24:57.638+08:00"
permalink: "/2022/02/golang-dtm-server.html"
original_url: "https://x8795278.blogspot.com/2022/02/golang-dtm-server.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-4735892657600981811"
tags: ["Go"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Go_Logo_Blue.svg/1200px-Go_Logo_Blue.svg.png)

# golang dtm server
```go
git clone https://github.com/dtm-labs/dtm && cd dtm
go run main.go

git clone https://github.com/dtm-labs/dtmcli-go-sample && cd dtmcli-go-sample
go run main.go
```

```go
// QsFireRequest quick start: fire request
func QsFireRequest() string {
	fmt.Println(mount)
	req := &gin.H{"amount": 30} // 微服務的載荷
	// DtmServer為DTM服務的地址
	saga := dtmcli.NewSaga(dtmServer, dtmcli.MustGenGid(dtmServer)).
		// 添加一個TransOut的子事務，正向操作為url: qsBusi+"/TransOut"， 逆向操作為url: qsBusi+"/TransOutCompensate"
		Add(qsBusi+"/TransOut", qsBusi+"/TransOutCompensate", req).
		// 添加一個TransIn的子事務，正向操作為url: qsBusi+"/TransOut"， 逆向操作為url: qsBusi+"/TransInCompensate"
		Add(qsBusi+"/TransIn", qsBusi+"/TransInCompensate", req)
	// 提交saga事務，dtm會完成所有的子事務/回滾所有的子事務
	err := saga.Submit()
	logger.FatalIfError(err)
	return saga.Gid
} 
```

```go
var mount = 30
func qsAddRoute(app *gin.Engine) {

	app.POST(qsBusiAPI+"/TransIn", func(c *gin.Context) {
		logger.Infof("TransIn")
		// c.JSON(200, "")
		mount += 60
		fmt.Println(mount)
		c.JSON(409, "") // Status 409 for Failure. Won't be retried
	})
	app.POST(qsBusiAPI+"/TransInCompensate", func(c *gin.Context) {
		logger.Infof("TransInCompensate")
		mount -= 60
		fmt.Println(mount)
		c.JSON(200, "")
	})
	app.POST(qsBusiAPI+"/TransOut", func(c *gin.Context) {
		logger.Infof("TransOut")
		mount -= 20
		fmt.Println(mount)
		c.JSON(200, "")
	})
	app.POST(qsBusiAPI+"/TransOutCompensate", func(c *gin.Context) {
		logger.Infof("TransOutCompensate")
		mount += 20
		fmt.Println(mount)
		c.JSON(200, "")
	})
}
```

當你的微服務都是http request 則在
```go
		Add(qsBusi+"/TransOut", qsBusi+"/TransOutCompensate", req).
		// 添加一個TransIn的子事務，正向操作為url: qsBusi+"/TransOut"， 逆向操作為url: qsBusi+"/TransInCompensate"
		Add(qsBusi+"/TransIn", qsBusi+"/TransInCompensate", req)
```
要確保這部分的業務邏輯一定要對否則rollback
```go
	app.POST(qsBusiAPI+"/TransIn", func(c *gin.Context) {
		logger.Infof("TransIn")
		// c.JSON(200, "")
		mount += 60
		fmt.Println(mount)
		c.JSON(409, "") // Status 409 for Failure. Won't be retried
	})
```
可以看到最終值可以維持不變
![](https://i.imgur.com/HDFUvBE.png)

