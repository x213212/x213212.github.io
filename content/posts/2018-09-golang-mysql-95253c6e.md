---
title: "Golang 數據處理與 Mysql 基礎語法"
date: "2018-09-29T05:29:00.002+08:00"
updated: "2018-09-30T04:47:33.272+08:00"
permalink: "/2018/09/golang-mysql.html"
original_url: "https://x8795278.blogspot.com/2018/09/golang-mysql.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-718578078047606833"
tags: ["Go", "Stock", "Tutorial"]
layout: post
---

打造股票回測/盯盤網頁  
## 目標

## ---

昨天有說到要打造一個用redis資料庫，後來想一想這是用在有快取場合的方面，那麼 我們能做到什麼呢，我打算用golang mongodb jquery來實現我們的框架初步回測的框架 那麼我們可能需要完成下列清單不過我們先用mysql搭起來熟悉一下環境吧~ 整個流程跑完苦 - 數據的導入 - 架設伺服器回傳json - 畫折線圖 - 新增回測按鈕與篩選條件 - 打造一個盯盤軟體

## 數據的處理

## ---

##

### 看著我你CSV你才能動->>>>[CSV檔案下載](https://gist.github.com/x213212/98d9a7d371caa114ac2a011393313e80)

就是說這一次的話沒想過要弄爬蟲，相信大家可以在很多地方找到股票的歷史資料，  

我們今天就對數據做一個處理吧首先我們先來直上程式碼  

這邊程式碼我們把檔案讀進去了接下來看要怎樣對上傳CSV檔案到SQL資料庫吧  

```go
package main

import (
    "encoding/csv"
    "fmt"
    "io"
    "os"
)

func main() {
    file, err := os.Open("names.txt")
    if err != nil {
        fmt.Println("Error:", err)
        return
    }
    defer file.Close()
    reader := csv.NewReader(file)
    for {
        record, err := reader.Read()
        if err == io.EOF {
            break
        } else if err != nil {
            fmt.Println("Error:", err)
            return
        }

        fmt.Println(record) // record has the type []string
    }
}
```

  
## Mysql 的 常用函式

## ---

**`createtable.go`**

```go
func create(name string) {

   db, err := sql.Open("mysql", "admin:admin@tcp(127.0.0.1:3306)/")
   if err != nil {
       panic(err)
   }
   defer db.Close()

   _,err = db.Exec("CREATE DATABASE "+name)
   if err != nil {
       panic(err)
   }

   _,err = db.Exec("USE "+name)
   if err != nil {
       panic(err)
   }

   _,err = db.Exec("CREATE TABLE example ( id integer, data varchar(32) )")
   if err != nil {
       panic(err)
   }
}
```

**`insert.go`**

```go
func insert() {
    db, err := sql.Open("mysql", "root:1234@tcp(localhost:3306)/mysql?charset=utf8")

    stmt, err := db.Prepare(`INSERT user (Host,user,password) values (?,?,?)`)
	if err != nil {
		panic(err)
	}
    res, err := stmt.Exec("tony", 20, 1)
	if err != nil {
		panic(err)
	}
    id, err := res.LastInsertId()
	if err != nil {
		panic(err)
	}
    fmt.Println(id)
}
```

**`remove.go`**

```go
func remove() {
    db, err := sql.Open("mysql", "root:1234@tcp(localhost:3306)/mysql?charset=utf8")
	if err != nil {
		panic(err)
	}
    stmt, err := db.Prepare(`DELETE FROM user WHERE user_id=?`)
	if err != nil {
		panic(err)
	}
    res, err := stmt.Exec(1)
	if err != nil {
		panic(err)
	}
    num, err := res.RowsAffected()
	if err != nil {
		panic(err)
	}
    fmt.Println(num)
}
```

**`select.go`**

```go
func getFromdatabase() {

	db, e := sql.Open("mysql", "root:1234@tcp(localhost:3306)/mysql?charset=utf8")
    if e != nil { 
        print("ERROR?")
        return
    }
   
    _, e2 := db.Query("select 1")
    if e2 == nil {
        println("DB OK")
        rows, e := db.Query("select user,password,host from mysql.user")
        if e != nil {
            fmt.Print("query error!!%v\n", e)
            return
        }
        if rows == nil {
            print("Rows is nil")   
            return
        }
        for rows.Next() { 
            user := new(User)
         
            row_err := rows.Scan(&user.User,&user.Password, &user.Host)
            if row_err != nil {
                print("Row error!!")
                return
            }
            b, _ := json.Marshal(user)
            fmt.Println(string(b)) 
        }

    }

}
```

**`update.go`**

```go
func update() {
    db, err := sql.Open("mysql", "root:1234@tcp(localhost:3306)/mysql?charset=utf8")
	if err != nil {
		panic(err)
	}
    stmt, err := db.Prepare(`UPDATE user SET user_age=?,user_sex=? WHERE user_id=?`)
	if err != nil {
		panic(err)
	}
    res, err := stmt.Exec(21, 2, 1)
	if err != nil {
		panic(err)
	}
    num, err := res.RowsAffected()
	if err != nil {
		panic(err)
	}
    fmt.Println(num)
}
```

**`解構體.go`**

```go
// 定义一个结构体, 需要大写开头哦, 字段名也需要大写开头哦, 否则json模块会识别不了
// 结构体成员仅大写开头外界才能访问
type User struct {
    User      string    `json:"user"`
    Password string `json:"password"`
    Host   string `json:"host"`
}
```

  
##

我大致上把它整理一下  
## 讀csv檔與上傳到資料庫

## ---

##

每一檔股票都它其編號，所以呢我們可以create一個table名稱對應股票的代號這邊先做個簡易版  

先來讀一下檔  

[![](https://i.imgur.com/C2bxSJd.png)](https://i.imgur.com/C2bxSJd.png)
  

```go
package main

import (
    "encoding/csv"
    "fmt"
    "io"
	"os"	
	"database/sql"
)
import _ "github.com/go-sql-driver/mysql"
func typeof(v interface{}) string {
    return fmt.Sprintf("%T", v)
}
func create(name string) {

	db, err := sql.Open("mysql", "root:1234@tcp(localhost:3306)/mysql?charset=utf8")
	if err != nil {
		panic(err)
	}
	defer db.Close()
 

 
	_,err = db.Exec("USE stock")
	if err != nil {
		panic(err)
	}
	var  query string
	
	query="CREATE TABLE "+name+"  (date date ,open float, high float, low float ,close float , volume float)"

	fmt.Println(query)

	_,err = db.Exec(query)
	if err != nil {
		//panic(err)
		print (err)
	}
 }
 

//插入demo
func insert(name string,date string,open string,high string,low string,close string,volume string) {
    db, err := sql.Open("mysql", "root:1234@tcp(localhost:3306)/mysql?charset=utf8")
	if err != nil {
		panic(err)
	}
	_,err = db.Exec("USE stock")
	if err != nil {
		panic(err)
	}
    stmt, err := db.Prepare("INSERT "+name+" (date,open,high,low,close,volume) values (?,?,?,?,?,?)")
	if err != nil {
		panic(err)
	}
    res, err := stmt.Exec(date,open,high,low,close,volume)
	if err != nil {
		panic(err)
	}
	
    id, err := res.LastInsertId()
	if err != nil {
		fmt.Println(id)
	}
	
	db.Close()
}
func main() {
    file, err := os.Open("2015正新.csv")
    if err != nil {
        fmt.Println("Error:", err)
        return
	}
	create("2015tw")
	
    defer file.Close()
    reader := csv.NewReader(file)
    for {
        record, err := reader.Read()
        if err == io.EOF {
            break
        } else if err != nil {
			fmt.Println("Error:", err)
			
            return
        }
		insert("2015tw",record[0],record[1],record[2],record[3],record[4],record[5])
		//fmt.Println(record) // record has the type []string
		//fmt.Println("get:", record[0])
		//fmt.Println(strings.Replace(string(record), " ", ",", 2))
	}
	//insert("2015tw","1","1","1","1","1","1")
	fmt.Println("ok")
	
}
```

綜合下
  

[![](https://i.imgur.com/ONFPRF5.png)](https://i.imgur.com/ONFPRF5.png)
[![](https://i.imgur.com/lNnwyYL.png)](https://i.imgur.com/lNnwyYL.png)
在資料的insert速度超快跟python比差一大截
