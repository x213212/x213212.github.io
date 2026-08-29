---
title: "golang Gorm orm & original sqllite"
date: "2022-02-06T05:16:00.004+08:00"
updated: "2022-02-06T14:27:19.687+08:00"
permalink: "/2022/02/golang-gorm-orm-org-sqllite.html"
original_url: "https://x8795278.blogspot.com/2022/02/golang-gorm-orm-org-sqllite.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5696246811396346309"
tags: ["Go"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Go_Logo_Blue.svg/1200px-Go_Logo_Blue.svg.png)

# golang Gorm orm & org sqllite
# install sqlite3
```
go get -u github.com/mattn/go-sqlite3
http://tw.gitbook.net/sqlite/sqlite_create_database.html
```
# create sqlite3 database
```sql
CREATE TABLE `userinfo` (
    `uid` INTEGER PRIMARY KEY AUTOINCREMENT,
    `username` VARCHAR(64) NULL,
    `department` VARCHAR(64) NULL,
    `created` DATE NULL
);

CREATE TABLE `userdetail` (
    `uid` INT(10) NULL,
    `intro` TEXT NULL,
    `profile` TEXT NULL,
    PRIMARY KEY (`uid`)
);
```

![](https://i.imgur.com/XqCUkvO.png)

```go

func main() {
    	http.HandleFunc("/endpoint-2", handler2)
}
func handler2(w http.ResponseWriter, r *http.Request) {
	b, err := ioutil.ReadAll(r.Body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	fmt.Println("all nowgoroutine :", runtime.NumGoroutine())
	go func() {
		// Block until there are fewer than cap(smallPool) hard-work
		// goroutines running.
		smallPool <- struct{}{}
		defer func() { <-smallPool }() // Let everyone that we are done
		fmt.Println("working!")
		time.Sleep(5 * time.Second)

		fmt.Println("work done")
		processImage(b)
	}()
	// w.WriteHeader(http.StatusAccepted)
	a += 1
	// time.Sleep(2 * time.Second)

	if runtime.NumGoroutine() < 20 {

		db, err := sql.Open("sqlite3", "./foo.db")
		checkErr(err)
		rows, err := db.Query("SELECT * FROM userinfo")
		checkErr(err)
		var output string = ""
		for rows.Next() {
			var uid int
			var username string
			var department string
			var created time.Time
			err = rows.Scan(&uid, &username, &department, &created)
			checkErr(err)
			output += strconv.Itoa(uid) + "|" + username + "|" + department + "|" + created.Format("2006-01-02 15:04:05") + "\n"
		}

		w.Write([]byte(output))
		w.WriteHeader(http.StatusAccepted)
		db.Close()
	} else {
		// w.Write([]byte("pleass wait" + strconv.Itoa(a)))
		w.WriteHeader(http.StatusNotFound)
		return
		// http.ErrUseLastResponse
	}

}
```
# orm
https://blog.csdn.net/cnwyt/article/details/118904882
```
go get -u gorm.io/gorm
go get -u gorm.io/driver/sqlite
```
```go
func main (){
    db, err := gorm.Open(sqlite.Open("test.db"), &gorm.Config{})
	if err != nil {
		panic("failed to connect database")
	}

	// Migrate the schema
	db.AutoMigrate(&Product{})

	// 插入內容
	db.Create(&Product{Title: "新款手機", Code: "D42", Price: 1000})
	db.Create(&Product{Title: "新款電腦", Code: "D43", Price: 3500})

	// 讀取內容
	var product Product
	db.First(&product, 1)                 // find product with integer primary key
	db.First(&product, "code = ?", "D42") // find product with code D42
	fmt.Println("%v", product)
	// 更新操作： 更新單個字段
	db.Model(&product).Update("Price", 2000)

	// 更新操作： 更新多個字段
	db.Model(&product).Updates(Product{Price: 2000, Code: "F42"}) // non-zero fields
	db.Model(&product).Updates(map[string]interface{}{"Price": 2000, "Code": "F42"})

	// 刪除操作：
	db.Delete(&product, 1) 
}
```
# sql pool & http pool
https://codertw.com/%E4%BC%BA%E6%9C%8D%E5%99%A8/154458/
https://gorm.io/docs/connecting_to_the_database.html
實際上在經過查詢可以發現，預設的http 或者 sql 其實底層都是goroutines，則我們也不用像以前的程式去寫 pool 之類的我們只要全局的去宣告就好
global variable
```go
func connDB(lifeTime int, maxCon int, idle int) *gorm.DB {
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
	return db
}

func init() {
    DBConn = connDB(1, 200, 10)

	// Migrate the schema
	DBConn.AutoMigrate(&Product{})

	// 插入內容
	DBConn.Create(&Product{Title: "新款手機", Code: "D42", Price: 1000})
	DBConn.Create(&Product{Title: "新款電腦", Code: "D43", Price: 3500})

	// 讀取內容
	var product Product
	DBConn.First(&product, 1)                 // find product with integer primary key
	DBConn.First(&product, "code = ?", "D42") // find product with code D42
	fmt.Println("%v", product)
	// 更新操作： 更新單個字段
	DBConn.Model(&product).Update("Price", 2000)

	// 更新操作： 更新多個字段
	DBConn.Model(&product).Updates(Product{Price: 2000, Code: "F42"}) // non-zero fields
	DBConn.Model(&product).Updates(map[string]interface{}{"Price": 2000, "Code": "F42"})

	// 刪除操作：
	DBConn.Delete(&product, 1)
}
func main (){
    	http.HandleFunc("/endpoint-2", handler2)
    
}

func handler2(w http.ResponseWriter, r *http.Request) {
	b, err := ioutil.ReadAll(r.Body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	fmt.Println("all nowgoroutine :", runtime.NumGoroutine())
	go func() {
		// Block until there are fewer than cap(smallPool) hard-work
		// goroutines running.
		smallPool <- struct{}{}
		defer func() { <-smallPool }() // Let everyone that we are done
		fmt.Println("working!")
		time.Sleep(5 * time.Second)

		fmt.Println("work done")
		processImage(b)
	}()
	// w.WriteHeader(http.StatusAccepted)
	a += 1
	// time.Sleep(2 * time.Second)

	if runtime.NumGoroutine() < 20 {

		// 讀取內容
		var product Product
		DBConn.First(&product, 1)                 // find product with integer primary key
		DBConn.First(&product, "code = ?", "D42") // find product with code D42
		fmt.Println("%v", product)
		// 更新操作： 更新單個字段
		DBConn.Model(&product).Update("Price", 2000)
		b, err := json.Marshal(product)
		if err != nil {
			fmt.Println(err)
			return
		}

		w.Write([]byte(string(b)))
		w.WriteHeader(http.StatusAccepted)
		// db.Close()
	} else {
		// w.Write([]byte("pleass wait" + strconv.Itoa(a)))
		w.WriteHeader(http.StatusNotFound)
		return
		// http.ErrUseLastResponse
	}

}
```
這樣我們的grom 就可以有pool 了
https://ithelp.ithome.com.tw/articles/10238565
![](https://i.imgur.com/6uNFCSi.png)

# http request 阻塞(?
預設 golang 的 http 都是非阻塞，原因就是chrome or edge 會將當前頁面去做緩存之類的東西，所以假設同一個畫面不同分頁可能會出現順序返回，但是實際上是瀏覽器的關係，每一個request 都是 一個Goroutine則
下面畫面是同時訪問http://localhost:8080/endpoint-2 但是在同一個瀏覽器的畫面，可以看到右邊會有出現阻塞現象
![](https://i.imgur.com/JeugCZb.png)
下面是一個edge 和 chrome
同時訪問可以看到時間戳相差不遠
![](https://i.imgur.com/Sf1aXOq.png)

