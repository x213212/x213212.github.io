---
title: "rust - build mutithread webserver"
date: "2022-01-27T15:59:00.006+08:00"
updated: "2022-01-27T16:00:04.392+08:00"
permalink: "/2022/01/learn-rust-build-mutithread-webserver.html"
original_url: "https://x8795278.blogspot.com/2022/01/learn-rust-build-mutithread-webserver.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5060830923026325184"
tags: ["rust", "webserver"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Rust_programming_language_black_logo.svg/2048px-Rust_programming_language_black_logo.svg.png)

# rust mutithread web-server
我們來創建一個signle thread 的 web-server
我們來監聽一下端口7878
```rust
use std::net::TcpListener;
fn main() {
let listener = TcpListener::bind("127.0.0.1:7878").unwrap();
    for stream in listener.incoming() {
    let stream = stream.unwrap();
    println!("Connection established!");
}
```
# Connection established!
![](https://i.imgur.com/BWELgoM.png)

![](https://i.imgur.com/KebfoGi.png)

# read web stream data
```rust
use std::io::prelude::*;
use std::net::TcpStream;
use std::net::TcpListener;

let listener = TcpListener::bind("127.0.0.1:7878").unwrap();
for stream in listener.incoming() {
    let stream = stream.unwrap();
    handle_connection(stream);
}

fn handle_connection(mut stream: TcpStream) {
    let mut buffer = [0; 512];
    stream.read(&mut buffer).unwrap();
    println!("Request: {}", String::from_utf8_lossy(&buffer[..]));
}

```
# Connection established! again
可以發現收到來自瀏覽器的http 請求
![](https://i.imgur.com/lfWThXo.png)

# return html
編寫要返回的html
```htmlembedded
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <title>Hello!</title>
</head>

<body>
    <h1>Hello!</h1>
    <p>Hi from Rust</p>
</body>

</html>
```

# rewrite handle_connection
新增要回傳的contents
```rust
fn handle_connection(mut stream: TcpStream) {
    let mut buffer = [0; 512];
    stream.read(&mut buffer).unwrap();
    let contents = fs::read_to_string("/root/rust/www/hello.html").unwrap();
    let response = format!("HTTP/1.1 200 OK\r\n\r\n{}", contents);
    stream.write(response.as_bytes()).unwrap();
    stream.flush().unwrap();
}
```
# Connection established! again
可以看到我們的回傳的資料了
![](https://i.imgur.com/ChhoChl.png)

# router
## filter
一個http 請求 有get/post/或者put、、
我們可以通過簡單的starts_with 查看發送過來的請求看有沒有get
else 在一般情況下假設無法處理其他請求 假設是post 則回傳error page

```rust

fn handle_connection(mut stream: TcpStream) {
    let mut buffer = [0; 512];
    stream.read(&mut buffer).unwrap();
    let get = b"GET / HTTP/1.1\r\n";
    let (status_line, filename) = if buffer.starts_with(get) {
        ("HTTP/1.1 200 OK\r\n\r\n", "/root/rust/www/hello.html")
    } else {
        (
            "HTTP/1.1 404 NOT FOUND\r\n\r\n",
            "/root/rust/www/error.html",
        )
    };
    let contents = fs::read_to_string(filename).unwrap();
    let response = format!("{}{}", status_line, contents);
    stream.write(response.as_bytes()).unwrap();
    stream.flush().unwrap();
}

```
## get
![](https://i.imgur.com/XD8YPgz.png)
## post
![](https://i.imgur.com/1sd7xYY.png)

# mutithread
從單執行緒到多執行可以發現假設要讓我們的server更快回應client的請求，我們把每一個request 並開啟一個thread進行處理

```rust
use std::thread;
let listener = TcpListener::bind("127.0.0.1:7878").unwrap();
for stream in listener.incoming() {
    let stream = stream.unwrap();
    for stream in listener.incoming() {
        let stream = stream.unwrap();
        thread::spawn(|| {
        handle_connection(stream);
        });
    }
}
```

# Arc 與 Mutex
還記得之前介紹 Rc 時提過 Arc 嗎？ Rc 與 Arc 很像，只是 Arc 能跨執行緒的共享資料，在使用多執行緒時我們必須要使用 Arc，而 Mutex 是什麼？ Mutex 中文為互斥鎖，功能是保護資料不會因為多個執行緒修改而發生資料競爭 (data racing) 或是其它競爭情況，這邊並不詳細解釋，有興趣可以看一下維基的說明， Rust 中跟其它語言不同，一個有趣的地方是 Mutex 也是個容器，讓你直接包裝需要保護的資料：
```rust
use std::thread;
use std::sync::{Arc, Mutex};
use std::time::Duration;

fn main() {
  // 這邊使用 Arc 來包裝 Mutex 這樣才能在執行緒間共享同一個 Mutex
  let data = Arc::new(Mutex::new(0));
  let mut children = Vec::new();
  let one_sec = Duration::from_secs(1);
  // 開 4 個執行緒，因為我的電腦是 4 核的，你可以自己決定要不要修改
  // 另外你也可以把數字改成 1 ，這樣就跟沒有平行化是一樣的，你可以比較一下速度的差別
  for i in 0..4 {
    // 使用 clone 來共享 Arc
    let data = data.clone();
    children.push(thread::spawn(move || loop {
      {
        // 鎖定資料
        let mut guard = data.lock().unwrap();
        // 如果大於 10 就結束
        if *guard >= 10 {
          println!("Thread[{}] exit", i);
          break;
        } else {
          // 處理資料
          *guard += 1;
        }
        println!("Thread[{}] data: {}", i, *guard);
        // 離開 scope 時會自動解鎖 Mutex
      }
      // 模擬處理的耗時
      thread::sleep(one_sec);
    }));
  }
  // 等所有執行緒結束
  for child in children {
    child.join().unwrap();
  }
}
```
上述場景架設遇到ddos我們的server可能會被癱瘓掉
改用thread pool
https://ithelp.ithome.com.tw/articles/10202523
下面程式碼大概就是我們的程式接受到一個request會有的相對應對做
首先我們再rust 創建pool 的時候宣告結構體，可以有多個worker 相對應 也就是有多個receiver
下次接收到請求的時候 呼叫sender.send(job).unwrap();

這段代碼首先調用了receiver的lock方法來請求互斥鎖，並接
著使用unwrap來處理可能出現的錯誤情形。請求獲取鎖的操作會在
互斥體被污染 時出錯，而互斥體會在某個持有鎖的線程崩潰而鎖沒有
被正常釋放時被污染。在這種情形下，調用unwrap觸發當前線程的
panic是非常恰當的行為。當然，你也可以將unwrap修改為expect來附
帶一個有意義的錯誤提示信息。
在互斥體上得到鎖以後，我們就可以通過調用recv來從通道中接
收Job了。與發送端的send方法類似，recv會在持有通道發送端的線
程關閉時出現錯誤，所以我們同樣使用了unwrap來攔截所有錯誤❹。
調用recv會阻塞當前線程，當通道中不存在任務時，當前線程就
會一直處於等待狀態。而Mutex則保證了一次只有一個Worker線程
嘗試請求任務。

channel
https://blog.csdn.net/mutourend/article/details/119424129
sender no-blocking , Receiver blocking
這樣請求超過4個的時候，receiver會一直等，並不會一直創thread，直到有一個revevier可以成功接收到 sender 的任務
而job 任務也就是我們包在 execute的 function  handle_connection(stream);

# thread pool
```rust

use std::sync::mpsc;
use std::sync::Arc;
use std::sync::Mutex;

type Job = Box<dyn FnOnce() + Send + 'static>;

use std::thread;
pub struct ThreadPool {
    workers: Vec<Worker>,
    sender: mpsc::Sender<Job>,
}

impl ThreadPool {
    pub fn new(size: usize) -> ThreadPool {
        assert!(size > 0);
        let (sender, receiver) = mpsc::channel();
        let receiver = Arc::new(Mutex::new(receiver));
        let mut workers = Vec::with_capacity(size);
        for id in 0..size {
            workers.push(Worker::new(id, Arc::clone(&receiver)));
        }
        ThreadPool { workers, sender }
    }

    pub fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
        let job = Box::new(f);
        self.sender.send(job).unwrap();
    }
}
struct Worker {
    id: usize,
    thread: thread::JoinHandle<()>,
}
impl Worker {    
    fn new(id: usize, receiver: Arc<Mutex<mpsc::Receiver<Job>>>) -> Worker {
        let thread = thread::spawn(move || loop {
            let job = receiver.lock().unwrap().recv().unwrap();
            println!("Worker {} got a job; executing.", id);
            job();
        });
        Worker { id, thread }
    }
}

fn main() {
    let listener = TcpListener::bind("127.0.0.1:7878").unwrap();
    let pool = ThreadPool::new(4);
    for stream in listener.incoming() {
        let stream = stream.unwrap();
        for stream in listener.incoming() {
            let stream = stream.unwrap();
            pool.execute(|| {
                handle_connection(stream);
            });
        }
    }
}
fn handle_connection(mut stream: TcpStream) {
    let mut buffer = [0; 512];
    stream.read(&mut buffer).unwrap();
    let get = b"GET / HTTP/1.1\r\n";
    let (status_line, filename) = if buffer.starts_with(get) {
        ("HTTP/1.1 200 OK\r\n\r\n", "/root/rust/www/hello.html")
    } else {
        (
            "HTTP/1.1 404 NOT FOUND\r\n\r\n",
            "/root/rust/www/error.html",
        )
    };
    let contents = fs::read_to_string(filename).unwrap();
    let response = format!("{}{}", status_line, contents);
    stream.write(response.as_bytes()).unwrap();
    stream.flush().unwrap();
}

```
# router
最後想來看一下結合orm 框架，和resturn json 格式那麼我們的小型rust webserver 就完成了
```rust

fn handle_connection(mut stream: TcpStream) {
    let mut buffer = [0; 512];
    stream.read(&mut buffer).unwrap();
    let get = b"GET / HTTP/1.1\r\n";
    let get2 = b"GET /test HTTP/1.1\r\n";
    let (status_line, filename) = 
    if buffer.starts_with(get) {
        ("HTTP/1.1 200 OK\r\n\r\n", "/root/rust/www/hello.html")
    } else  if buffer.starts_with(get2){
        ("HTTP/1.1 200 OK\r\n\r\n", "/root/rust/www/hello.html")
    }
    else {
        (
            "HTTP/1.1 404 NOT FOUND\r\n\r\n",
            "/root/rust/www/error.html",
        )
    };
    let contents = fs::read_to_string(filename).unwrap();
    let response = format!("{}{}", status_line, contents);
    stream.write(response.as_bytes()).unwrap();
    stream.flush().unwrap();
}

```

