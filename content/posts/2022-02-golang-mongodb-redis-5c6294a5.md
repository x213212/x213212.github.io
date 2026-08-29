---
title: "golang mongodb & redis"
date: "2022-02-11T07:13:00.002+08:00"
updated: "2022-02-11T07:13:41.361+08:00"
permalink: "/2022/02/golang-mongodb-redis.html"
original_url: "https://x8795278.blogspot.com/2022/02/golang-mongodb-redis.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-4440442351627404211"
tags: ["Go"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Go_Logo_Blue.svg/1200px-Go_Logo_Blue.svg.png)

# golang mongodb & redis
https://www.runoob.com/docker/docker-install-mongodb.html
```bash
docker pull mongo

$ docker exec -it mongo mongo admin

>  db.createUser({ user:'admin',pwd:'123456',roles:[ { role:'userAdminAnyDatabase', db: 'admin'},"readWriteAnyDatabase"]});

> db.auth('admin', '123456')
```
![](https://i.imgur.com/doG7TT9.png)
https://its304.com/article/pengpengzhou/105222504
```go
type TestStruct struct {
	Name string
	ID   primitive.ObjectID `bson:"_id"`
}

func main(){
	credential := options.Credential{
		Username: "admin",
		Password: "123456",
	}

	//1.建立連接
	if client, err = mongo.Connect(context.TODO(), options.Client().ApplyURI("mongodb://localhost:27017").SetAuth(credential).SetConnectTimeout(5*time.Second)); err != nil {
		fmt.Print(err)
		return
	}
	//2.選擇database
	db = client.Database("my_db")

	//3.選擇table
	collection = db.Collection("my_collection")
	collection = collection
	podcast := TestStruct{
		Name: "The Polyglot Developer",
		ID:   primitive.NewObjectID(),
    }
    	//insert 
	if iResult, err = collection.InsertOne(context.TODO(), podcast); err != nil {
		fmt.Print(err)
		return
	}
	//_id:id
	log.Println("collection.InsertOne: ", iResult.InsertedID)
    var results []TestStruct
	fmt.Println(`bson.M{“_id”: docID}:`, bson.M{"Name": "The Polyglot Developer"})
	fmt.Println(`bson.M{“_id”: docID}:`, bson.D{{"Name", "The Polyglot Developer"}})
	cur, err := collection.Find(context.TODO(), bson.M{"id": 999})
	if err != nil {
		// ErrNoDocuments means that the filter did not match any documents in the collection
		if err == mongo.ErrNoDocuments {
			return
		}
		log.Fatal(err)
	}
	if err = cur.All(context.TODO(), &results); err != nil {
		panic(err)
	}
	fmt.Println(results)
}
```

# redis
https://www.796t.com/article.php?id=173205
```go
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
	"time"

	"github.com/go-redis/redis/v8"

)
func main(){
        rdb := redis.NewClient(&redis.Options{
		Addr: "localhost:6379",
		// Password: "a12345", // no password set
		DB: 0, // use default DB
	})
	pong, err := rdb.Ping(context.Background()).Result()
	if err == nil {
		log.Println("redis 回應成功，", pong)
	} else {
		log.Fatal("redis 無法連線，錯誤為", err)
	}
	key := "go2key"
	//過期時間1小時
	err = rdb.Set(context.Background(), key, "我是值", time.Hour).Err()
	if err != nil {
		fmt.Println("set err", err)
		return
	}

	//獲取
	value, err := rdb.Get(context.Background(), key).Result()
	if err != nil {
		fmt.Println("Get err", err)
		return
	}
	fmt.Printf("key:%v value：%v \n", key, value)
}
```
![](https://i.imgur.com/GVxhdw7.png)

