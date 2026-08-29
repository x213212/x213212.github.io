---
title: "learn rust"
date: "2022-01-26T20:57:00.006+08:00"
updated: "2022-01-26T20:57:57.511+08:00"
permalink: "/2022/01/learn-rust.html"
original_url: "https://x8795278.blogspot.com/2022/01/learn-rust.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-744721046061612481"
tags: ["rust"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Rust_programming_language_black_logo.svg/2048px-Rust_programming_language_black_logo.svg.png)

# learn rust
紀錄一下學習rust 筆記，目前大概會以寫web可能會用到的業務邏輯來看大概會用到rust什麼特性。
https://doc.rust-lang.org/stable/std/string/struct.String.html
http://jxz1.j9p.com/pc/rustqwzn.pdf
https://course.rs/basic/result-error/result.html
https://lotabout.me/2017/rust-error-handling/
https://rustmagazine.github.io/rust_magazine_2021/chapter_3/rust-design-pattern-factory.html
https://ithelp.ithome.com.tw/articles/10202889
https://shihyu.github.io/RustPrimerBook/rcarc/cell.html
https://electronic.blue/blog/2017/04/30-rust-an-introduction-in-oop/
# hello cargo
```rust
cargo new hello_cargo 
```
# hello rust
```rust
println!("Hello, world! {}", test);
```
# variable area
可以看到 第二個花括號裡面的test 的時候外層的 test 記憶體位置空間已經被清除
其中mut 代表 variable 為可變。
```rust
fn main() {
    let mut test = 0;

    test = 120;
    {
        let test = 200;
        println!("Hello, world! {}", test);
    }
}
```
當variable 脫離作用域可以發現test 值是無法再次被使用類似c/c++ 傳值或者傳址，某些形況類似泛型好像需要特殊處理後面再說。

```rust
fn five(x: i32) -> i32 {
    x + 1
}

fn main() {
    let test=1;
    let test2 =five( test);
    println!("p.x = {}",test2 );
}
```

為什麼要用&，原因有可能 x假設傳入到 function 後，出來後x 這個 value 可能會被銷毀。
```rust
fn five(x: &i32) -> i32 {
    x + 1
}

fn main() {
    let test=1;
    let test2 =five( &test);
    println!("p.x = {}",test2 );
}
```

# declare variable
當variable 有明顯變數型態則compiler 則會再編譯階段自動推理變數型態。
```rust
let guess:
```

```rust
let guess="test":
let mut guess = String::new();
let guess = 1;
```

強指 i32 type
```rust
let guess:i32 = 1;
```
# match
這邊可以看到variable guess， 其中又對 guess.trim().parse()返回值使用match做處理，其中trim () 為把 guess 字串空白清空，parse 則把 string 自動推理成int，而match 讓 function 回傳的value 只有兩種狀態
ok和 err  假設真的fucntion 沒有任何問題則 正確地返回 num 這個value 並賦予 guess
否則err (_)則代表任意狀態，則把 guess 設為-1。
```rust
use std::io;
let mut guess = String::new();
io::stdin().read_line(&mut guess).expect("test"); //test
let guess: i32 = match guess.trim().parse() {
        Ok(num) => num,
        Err(_) => -1,
};
```
# match function
```rust
    match test_function() {
        Ok(num) => println!("result: Is OK: {}", num),

        Err(_) => println!("result: Failed te"),
    }
```
# panic
程式強迫終止
```rust
    match test_function() {
        Ok(num) => println!("result: Is OK: {}", num),
        Err(_) => panic!(),
    }
```
透過設定環境變數可以發生程式強迫終止可以顯示目前的call stack
RUST_BACKTRACE=1
# custom panic
發生異常中斷則顯示Custom panic hook
```rust
    panic::set_hook(Box::new(|_| {
        println!("Custom panic hook");
    }));
```
# catch all exception
某些情況可能程式碼有問題但是rust編譯器檢測不出來，我一直在找有相關
類似try catch 功能實現，如下
假設程式在while 迴圈裡 嘗試索引 b[test]則會發生 異常中斷則，我們可以嘗試去攔截這段前間所發生的事再來做處理，當然官方是不建議使用下列程式碼片段。
```rust
  let result = panic::catch_unwind(|| {

        let b: [i32; 5] = [1, 2, 3, 4, 5];
        // b[4];
        // let a = [10, 20, 30, 40, 50];
        let mut test = 0;
        while test < 6 {
            println!("the value is: {}", b[test]);
            test = test + 1;
        }
        for element in b.iter() {
            print!("test {}\n", element);
        }
        for number in (1..4).rev() {
            println!("{}!", number);
        }
        println!("LIFTOFF!!!");
    });

    match result {
        Ok(()) => println!("every thing goes OK"),
        Err(_) => println!("catch panic"),
    }
```
# 引入外部  rand 包
```toml
[package]
name = "hello-rust"
version = "0.1.0"
edition = "2018"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
rand = "0.5.5"
```
產生亂數
```rust
use rand::Rng;
let secret_number = rand::thread_rng().gen_range(1, 101);
println!("rand {}", secret_number);
```

# tup
```rust
let tup: (i32, String, u8) = (500, "123qwe".to_string(), 1);
println!("float {}", tup.1);
```
# array
```rust
let a: [i32; 5] = [1, 2, 3, 4, 5];
let mut b = [3; 5];
```
# 2d array
```rust
//2D array
//https://t.codebug.vip/questions-2091964.htm
let mut state = [[0i32; 9]; 9];
for x in (0..9) {
    for y in (0..9) {
        let sum = i32::from(((x as i32) + 1) * ((y as i32) + 1));
        state[x][y] = sum;
        print!("{}:{} = {} ", x + 1, y + 1, state[x][y]);
    }
    println!("");
}
```
# string
```rust
let hello = "Здравствуйте";
let mut s2 = String::from(hello);
let mut s3 = String::new();
```
字串切片

```rust
let hello = "Здравствуйте";
let mut s = &hello[..];
```
逐一字元
```rust
for c in "Здравствуйте".chars() {
    println!("{}", c);
}
```
逐一字元byte
```rust
for c in "Здравствуйте".bytes() {
    println!("{}", c);
}
```
push char
```rust
s3.push(c);
```
push str
```rust
s3.push_str("orld!");
```
# vector
```rust
let mut v = Vec::new();
v.push(5);
v.push(6);
v.push(7);
v.push(8);
```
walk vector
```rust
for test in v.iter() {
    println!("test {}", test);
}
```
get vector by index
```rust
let third: &i32 = &v[2];
```
match 攔截index 越界錯誤
```rust
match v.get(2) {
    Some(third) => println!("The third element is {}", third),
    None => println!("There is no third element."),
}
```
可變 vector
```rust
let mut v = vec![100, 32, 57];
for i in &mut v {
    *i += 50;
}

for i in &v {
    println!("{}", i);
}
```
# hashmap
set hashmap value
```rust
let mut scores = HashMap::new();
scores.insert(String::from("Blue"), 10);
scores.insert(String::from("Yellow"), 50);
    cores.insert(String::from("Blue"), 20);
```
get hashmap value
```rust
let team_name = String::from("Blue");
let score = match scores.get(&team_name) {
    Some(val) => val, 
    None => panic!(),
};
```
# struct
```rust
pub struct Tweet {
    pub username: String,
    pub content: String,
    pub reply: bool,
    pub retweet: bool,
}
impl Summary for Tweet {
    fn summarize(&self) -> String {
        format!("{}: {}", self.username, self.content)
    }
}
pub trait Summary {
    fn summarize(&self) -> String;
}
pub fn notify<T: Summary>(item: T) {
    println!("Breaking news! {}", item.summarize());
}

let tweet = Tweet {
    username: String::from("horse_ebooks"),
    content: String::from("of course, as you probably already know, people"),
    reply: false,
    retweet: false,
};

println!("1 new tweet: {}", tweet.summarize());
notify(tweet);
```

return struct
```rust

pub fn returns_summarizable() -> impl Summary {
    Tweet {
        username: String::from("horse_ebooks"),
        content: String::from("of course, as you probably already know, people"),
        reply: false,
        retweet: false,
    }
}

let tweet = returns_summarizable();
println!("1 new tweet: {}", tweet.summarize());
```
# enum
```rust
enum WebEvent {
    PageLoad,
    PageUnload,
    KeyPress(char),
    Paste(String),
    Click { x: i64, y: i64 },
}
fn inspect(event: WebEvent) {
    match event {
        WebEvent::PageLoad => println!("page loaded"),
        WebEvent::PageUnload => println!("page unloaded"),
        WebEvent::KeyPress(c) => println!("pressed '{}'.", c),
        WebEvent::Paste(s) => println!("pasted \"{}\".", s),
        WebEvent::Click { x, y } => {
            println!("clicked at x={}, y={}.", x, y);
        }
    }
}

let pressed = WebEvent::KeyPress('x');
let pasted = WebEvent::Paste(String::from("my text"));
let click = WebEvent::Click { x: 20, y: 80 };
let load = WebEvent::PageLoad;
let unload = WebEvent::PageUnload;

inspect(pressed);
inspect(pasted);
inspect(click);
inspect(load);
inspect(unload);
```
# unit test
```rust
 cargo test
```
```rust
#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
    #[test]
    fn it_works2() {
        assert_eq!(2 + 2, 4);
    }
    #[test]
    fn it_works3() -> Result<(), String> {
        if 2 + 2 == 4 {
            Ok(())
        } else {
            Err(String::from("two plus two does not equal four"))
        }
    }
}
```
# linked list
```rust
let mut lst = LinkedList::new();
// inserting at the back
lst.push_front('b'); //b
lst.push_front('l'); //l->b
lst.push_front('u'); //u->l->b
lst.push_front('f'); //f->u->l->b

// pop_back() 
println!("The element popped from back: {:?}", lst.pop_back());
// pop_front() 
println!("The element popped from front: {:?}", lst.pop_front());

```

# smart pointer

https://rust-algo.club/collections/singly_linked_list/
https://blog.csdn.net/wyansai/article/details/105152547
https://blog.gtwang.org/programming/cpp-smart-pointers/

我覺得這兩篇講得很清楚以C++ smart pointer
https://kheresy.wordpress.com/2012/03/03/c11_smartpointer_p1/
https://kheresy.wordpress.com/2012/03/05/c11_smartpointer_p2/

Box
是一種獨享智能指針，類似C++的unique_ptr
```rust
Box<T>
let x = Box::new(42);
```
  
Rc
是一種常見的共享指針，類似C++的shared_ptr
```rust
Rc<T>
use std::rc::Rc;

let a = Rc::new(42);
let b = Rc::clone(&a);
```
    
就是差不多的概念，也就是，所謂的所有權在使用完後會進行釋放，或者可以通過move轉移所有權，來避免造成memory 之類的問題。
    https://electronic.blue/blog/2016/12/03-rust-an-introduction-reference-and-borrow-checker-2/

Cell
```rust
use std::cell::Cell;

let num = Cell::new(42);
num.set(123);
assert_eq!(num.get(), 123);
```

refCell
```rust
use std::cell::RefCell;

let s = RefCell::new(String::from("Hello, "));

// 以可寫的方式 borrow
s.borrow_mut().push_str("World");

// 唯讀的 borrow
println!("{}", s.borrow());  
```

# command
```rust
use std::process::Command;

let mut cmd = Command::new("ls").spawn().expect("Fail to spawn");
cmd.wait().expect("Fail to wait");
```
# thread
```ruby
use std::thread;
use std::time::Duration;

fn main() {
  // 建立執行緒
  let handle = thread::spawn(move || {
    let half_sec = Duration::from_millis(500);
    for _ in 0..10 {
      println!("Thread");
      // 休息半秒
      thread::sleep(half_sec);
    }
  });
  let one_sec = Duration::from_secs(1);
  for _ in 0..5 {
    println!("Main");
    // 休息 1 秒
    thread::sleep(one_sec);
  }
  // 等待子執行緒結束
  handle.join().unwrap();
}
```

# unsafe
https://ithelp.ithome.com.tw/articles/10202889
只要使用 unsafe 這個關鍵字就能使用這些不安全的功能，這些功能有：

>直接存取指標
>修改全域變數
>被標記為不安全的方法與 trait

```rust
// 如果用 new 的話 Vec 是不會分配空間的
let vec = Vec::<i32>::with_capacity(1);
unsafe {
  vec.set_len(100);
}

// 這邊可以看到 vec 所分配的大小實際上還是只有 1
println!("{}", vec.capacity());
// 然而因為長度已經被設定成 100 了，所以可以看這邊印出了 100 個元素
println!("{:?}", vec);
```

