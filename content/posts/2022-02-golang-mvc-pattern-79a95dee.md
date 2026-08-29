---
title: "golang mvc pattern"
date: "2022-02-11T07:17:00.003+08:00"
updated: "2022-02-11T07:17:30.465+08:00"
permalink: "/2022/02/golang-mvc-pattern.html"
original_url: "https://x8795278.blogspot.com/2022/02/golang-mvc-pattern.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-1740894110554082525"
tags: ["Go"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Go_Logo_Blue.svg/1200px-Go_Logo_Blue.svg.png)

# golang mvc pattern
只前只有學過spring cloud 框架來使用mvc架構來重構一下
```bash
root@HOME-X213212:~/golang/mvc# tree
.
├── controller
│   └── productController.go
├── dao
│   └── dao.go
├── entity
│   └── product.go
├── go.mod
├── go.sum
├── main.go
├── service
│   └── productService.go
└── test.db

4 directories, 8 files
```
# dao
```go
package dao

import (
	"database/sql"
	"time"

	// "gopkg.in/mgo.v2"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

var DBConn *gorm.DB
var SQLConn *sql.DB

func ConnDB(lifeTime int, maxCon int, idle int) (*gorm.DB, *sql.DB) {
	db, err := gorm.Open(sqlite.Open("test.db"), &gorm.Config{})
	if err != nil {
		panic("failed to connect database")
	}
	sqlDB, err := db.DB()
	if err != nil {
		panic(err)
	}

	sqlDB.SetConnMaxLifetime(time.Duration(lifeTime) * time.Second) // 每條連線的存活時間
	sqlDB.SetMaxOpenConns(maxCon)                                   // 最大連線數
	sqlDB.SetMaxIdleConns(idle)                                     // 最大閒置連線數

	return db, SQLConn
}

// func ConnMongodb() {
// 	session, err := mgo.Dial("127.0.0.1:27017")
// 	if err != nil {
// 		panic(err)
// 	}

// }

```

# entity
```go

package entity

import "gorm.io/gorm"

type Product struct {
	gorm.Model
	Title string
	Code  string
	Price uint
}

```
# service
```go
package service

import (
	"encoding/json"
	"fmt"
	"mvc/dao"
	"mvc/entity"
)

func GetProduct() string {
	var product entity.Product
	dao.DBConn.First(&product, 1)                 // find product with integer primary key
	dao.DBConn.First(&product, "code = ?", "D42") // find product with code D42
	fmt.Println("%v", product)
	b, err := json.Marshal(product)
	if err != nil {
		fmt.Println(err)
	}

	return string(b)
}

```

# controller
```go
package controller

import (
	"mvc/service"
	"net/http"
	"runtime"
)

func Handler(w http.ResponseWriter, r *http.Request) {
	if runtime.NumGoroutine() < 20 {
		w.Write([]byte(service.GetProduct()))
		w.WriteHeader(http.StatusAccepted)
		// db.Close()
	} else {
		w.WriteHeader(http.StatusNotFound)
		return
	}
}

```

# main
```go
package main

import (
	"context"
	"fmt"
	"log"
	"mvc/controller"
	"mvc/dao"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var mgoCli *mongo.Client

func initEngine() *mongo.Client {
	var err error
	credential := options.Credential{
		Username: "admin",
		Password: "123456",
	}
	clientOptions := options.Client().ApplyURI("mongodb://localhost:27017").SetAuth(credential)

	// 连接到MongoDB
	mgoCli, err = mongo.Connect(context.TODO(), clientOptions)
	if err != nil {
		log.Fatal(err)
	}
	// 检查连接
	err = mgoCli.Ping(context.TODO(), nil)
	if err != nil {
		log.Fatal(err)
	} else {
		fmt.Println("connection ok!")

	}
	return mgoCli
}
func GetMgoCli() *mongo.Client {
	mgoCli = initEngine()
	if mgoCli == nil {
		log.Fatal(err)
	}
	return mgoCli
}

type TimePorint struct {
	StartTime int64 `bson:"startTime"` //开始时间
	EndTime   int64 `bson:"endTime"`   //结束时间
}
type LogRecord struct {
	JobName string `bson:"jobName"` //任务名

}
type TestStruct struct {
	Name string
	ID   primitive.ObjectID `bson:"_id"`
}

var (
	client     *mongo.Client
	err        error
	db         *mongo.Database
	collection *mongo.Collection
	lr         *LogRecord
	iResult    *mongo.InsertOneResult
	id         primitive.ObjectID
	cursor     *mongo.Cursor
)

type FindByJobName struct {
	JobName string `bson:"jobName"` //任务名
}

func main() {
	exitChan := make(chan os.Signal)
	signal.Notify(exitChan, os.Interrupt, os.Kill, syscall.SIGTERM)
	go exitHandle(exitChan)

	http.HandleFunc("/endpoint-1", controller.Handler)
	http.ListenAndServe(":8080", nil)

}

func init() {
	dao.DBConn, dao.SQLConn = dao.ConnDB(1, 200, 10)

}
func exit() {
	dao.SQLConn.Close()

	fmt.Println("all close")
}
func exitHandle(exitChan chan os.Signal) {
	for {
		select {
		case sig := <-exitChan:
			fmt.Println("recive system interrupt", sig)
			exit()
			os.Exit(1)
		}
	}
}

```

