---
title: "Golang 搭建一個簡單Http Server"
date: "2018-09-26T22:49:00.002+08:00"
updated: "2018-09-30T04:47:33.391+08:00"
permalink: "/2018/09/golang-server.html"
original_url: "https://x8795278.blogspot.com/2018/09/golang-server.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-7469045311439688862"
tags: ["Go", "Tutorial"]
layout: post
---

上一次我們講到安裝Golang那麼今天我們來看如何架設一個跟網頁溝通的伺服器  
## Setting

## ---

```
go get -u github.com/gorilla/mux
```

## 安裝套件的過程它不會講話xd，套一句老師說的沒消息就是好消息  [![](https://i.imgur.com/lQ0H32U.png)](https://i.imgur.com/lQ0H32U.png)

## 放置檔案路徑，沒什麼難度，放到資料夾而已。

[![](https://i.imgur.com/NRdoHCu.png)](https://i.imgur.com/NRdoHCu.png)

上述相關文件安裝完後，沒想到的是，只要設定好route，仔細看整組搬過來就可以了這是比較正規的作法，當然網路上也有其他更暴力的方法(牛逼稍微進行一下小改裝 [Go语言实现简单的一个静态WEB服务器](https://studygolang.com/articles/5116)

[![](https://i.imgur.com/KfgAa6v.png)](https://i.imgur.com/KfgAa6v.png)

[![](https://i.imgur.com/C6MyOk8.png)](https://i.imgur.com/C6MyOk8.png)
##

##

##

##

##

**`details.html`**

```html

<!DOCTYPE html>
<html>
	<head>
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
		<script type="text/javascript" language="javascript">
		    $(document).ready(function () {
		    	var id = getParameterByName('id');
		        $.getJSON("http://localhost:9000/people/"+id, function (data) {
		            console.debug(data);
		            $('#city').html(data["address"].city);
		            $('#country').html(data["address"].country);
		            $('#id').html(data.id);
		            $('#name').html(data.name);
		        });
		    });
		    function getParameterByName(name) {
			    var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
			    return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
			}
		</script>
	</head>
	<body>
		Id : <span id="id"></span><br><br>
		Name : <span id="name"></span><br><br>
		Address : <span id="city"> , </span> <span id="country"></span>		
	</body>
</html>
```

**`index.html`**

```html
<!DOCTYPE html>
<html>
	<head>
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
		<script type="text/javascript" language="javascript">
		    $(document).ready(function () {
		    	var success = false;
		        $.getJSON('http://localhost:9000/people', function (schoolData) {
		            var tr;
		            success = true;
		            for (var i = 0; i < schoolData.length; i++) {
		                tr = $('<tr/>');
		                tr.append("<td>" + schoolData[i].id + "</td>");
		                tr.append("<td>" + schoolData[i].name + "</td>");
		                tr.append("<td><a href='details?id="+ schoolData[i].id +"'>Details</a></td>");
            			tr.append('<td><button type="button" class="btn btn-success">Edit</button></td>');
            			tr.append('<td><button type="button" class="btn btn-success">Delete</button></td>');
		                $('table').append(tr);
		            }
		        });
		        setTimeout(function() {
			    if (!success)
			    {
				// Handle error accordingly
				alert("Server Not Found"); // string was "Houston, we have a problem."
			    }
			}, 1000);
		    });
		</script>
	</head>
	<body>
		<button>Add</button>
		<table class="table">
		</table>
	</body>
</html>
```

**`main.go`**

```go
package main

import (
    "fmt"
    "log"
    "net/http"
    "github.com/gorilla/mux"
    "encoding/json"
)

var people []Person

type Person struct {
    ID string `json:"id,omitempty"`
    Name string `json:"name,omitempty"`
    Address *Address `json:"address,omitempty"`
}

type Address struct {
    Country string `json:"country,omitempty"`
    City string `json:"city,omitempty"`
}

func DefaultHandler(w http.ResponseWriter, r *http.Request)  {
    fmt.Fprint(w, "Home")
    fmt.Fprint(w, "Home")
    fmt.Fprint(w, "Home")
    
}


func PeopleHandler(w http.ResponseWriter, r *http.Request){

    w.Header().Set("Access-Control-Allow-Origin", "*")
    json.NewEncoder(w).Encode(people)
   
}

func PersonHandler(w http.ResponseWriter, r *http.Request)  {
    w.Header().Set("Access-Control-Allow-Origin", "*")
     params := mux.Vars(r)
     for _,item := range people{
         if item.ID == params["id"]{
            json.NewEncoder(w).Encode(item)
         }
     }

}
func HttpFileHandler(response http.ResponseWriter, request *http.Request) {
	//fmt.Fprintf(w, "Hi from e %s!", r.URL.Path[1:])
	http.ServeFile(response, request, "index.html")
}
func HttpFileHandler2(response http.ResponseWriter, request *http.Request) {
	//fmt.Fprintf(w, "Hi from e %s!", r.URL.Path[1:])
	http.ServeFile(response, request, "details.html")
}

func main()  {
    route := mux.NewRouter()
    people = append(people, Person{ID : "1", Name : "sojib", Address : &Address{Country : "bangladesh", City : "Dhaka"}})
    people = append(people, Person{ID : "2", Name : "hasan", Address : &Address{Country : "china", City : "C"}})
    people = append(people, Person{ID : "3", Name : "kamal", Address : &Address{Country : "japan", City : "J"}})
    route.HandleFunc("/", DefaultHandler).Methods("Get")
    route.HandleFunc("/people", PeopleHandler).Methods("Get")
    route.HandleFunc("/people/{id}", PersonHandler).Methods("Get")
    route.HandleFunc("/index", HttpFileHandler)
    route.HandleFunc("/details", HttpFileHandler2)
    //route.Handle("/details", http.FileServer(http.Dir("/mnt/c/golangtmp")))
    log.Fatal(http.ListenAndServe(":9000", route))
}
```

  
## 後續

## ---

整組搬來用是不錯啦，這樣的話我們做處理的時候可以在golange做處理了 之前在python寫的交易系統，在前段時間呢看到了一個 影片 [遺傳演算法最佳化高頻交易策略](https://youtu.be/r-FBtE5pOtQ) 沒錯很喜歡模擬的我們呢已經搭建好這框架了 至於資料庫呢，既然都是用新技術在做事了，學習一下用[redis](https://redis.io/)當作資料庫 讓我們速度起飛!

##
