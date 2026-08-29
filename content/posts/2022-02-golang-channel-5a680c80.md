---
title: "golang channel"
date: "2022-02-05T19:19:00.001+08:00"
updated: "2022-02-05T19:19:12.637+08:00"
permalink: "/2022/02/golang-channel.html"
original_url: "https://x8795278.blogspot.com/2022/02/golang-channel.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-1706482236569622901"
tags: ["Go"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Go_Logo_Blue.svg/1200px-Go_Logo_Blue.svg.png)

# golang channel
以下列例子假設 pump 為生產者， suck 為消費者，假設消費者 先執行的話則有可能 會阻塞，
所以預設buffer 為2的情況下，可以看到我們可以在suck function 透過按下 enter passue 繼續執行
可以看到buffer 永遠會先有值，則 suck 不會發生阻塞，
![](https://i.imgur.com/nhOJSBz.png)
這樣我們的程式就不會阻塞，可以嘗試更改 buffer 為1 or 0 則有可能出現suck 嘗試讀取卻發現buffer 沒有值，則發生死鎖，因為按下enter 的當下suck 先執行發現沒人傳送則阻塞，再換pump 假設又發現沒人接收 則阻塞

1）對於同一個通道，發送操作（協程或者函數中的），在接收者準備好之前是阻塞的：如果ch中的數據無
人接收，就無法再給通道傳入其他數據：新的輸入無法在通道非空的情況下傳入。所以發送操作會等待 ch
再次變為可用狀態：就是通道值被接收時（可以傳入變量）。

2）對於同一個通道，接收操作是阻塞的（協程或函數中的），直到發送者可用：如果通道中沒有數據，接
收者就阻塞了。
```go

func main() {
	ch1 := make(chan int, 2)
	go pump(ch1) // pump hangs
    // time.Sleep(1 * time.Second)
	go suck(ch1)
	http.ListenAndServe(":8080", nil)
}
func pump(ch chan int) {
	// time.Sleep(1 * time.Second)
	fmt.Println("12312")
	for i := 0; i < 10; i++ {
		
		ch <- i
        fmt.Println("chanel:", len(ch))

	}

	fmt.Println("finsh")
}
func suck(ch chan int) {
	// time.Sleep(1 * time.Second)
	fmt.Println("1231")
	i := 0
	for i < 1 {

		if len(ch) > 1 {
			i = 1
		}
	
		fmt.Println("pause")
		fmt.Scanln()
	}

	for {
		fmt.Println("chanel2:", len(ch))
		fmt.Println(<-ch)
       
	}

	fmt.Println("finsh2")

}

```
# 有緩衝
在緩衝區為1的情況下，buffer預存一個int，suck 則會一直讀到沒有緩衝 下一個就代表沒有資料並結束goroutine，沒有好好回收goroutine
![](https://i.imgur.com/Oc3cmyZ.png)

```go
func main (){
    ch1 := make(chan int, 1)
	go pump(ch1) // pump hangs

	// time.Sleep(2 * time.Second)
	go suck(ch1)
    
}
func pump(ch chan int) {
	// time.Sleep(1 * time.Second)
	fmt.Println("pump")
	for i := 0; i < 10; i++ {
		fmt.Println("chanel:", len(ch))
		ch <- i
		fmt.Println("buffer %d", i) // prints only 0
		// time.Sleep(1 * time.Second)
	}
	// fmt.Println(":", len(ch))
	fmt.Println("finsh")
}
func suck(ch chan int) {
	// time.Sleep(1 * time.Second)
	fmt.Println("suck")

	for {
		fmt.Println("chanel2:", len(ch))
		if len(ch) == 0 {
			break
		}
		fmt.Println(<-ch)
		fmt.Println("pause")
		fmt.Scanln()
		// fmt.Println(":", len(ch))
	}
	fmt.Println("finsh2")

}
```

# 監控 gorutine
 runtime.NumGoroutine()
 其他profting
https://studygolang.com/articles/14410
main function 可以延遲久一點 看最後存活的nowgoroutine 有幾個

```go
func main() {
	largePool = make(chan struct{}, 2)
	smallPool = make(chan struct{}, 10)

	ch1 := make(chan int, 1)
	fmt.Println("first nowgoroutine :", runtime.NumGoroutine())
	go pump(ch1) // pump hangs
	fmt.Println("pump nowgoroutine :", runtime.NumGoroutine())
	// time.Sleep(2 * time.Second)

	go suck(ch1)
	fmt.Println("suck nowgoroutine :", runtime.NumGoroutine())
	// for {

	// }
	// fmt.Println(<-ch1) // prints only 0
	time.Sleep(10 * time.Second)
	fmt.Println("all nowgoroutine :", runtime.NumGoroutine())
}
func pump(ch chan int) {
	// time.Sleep(1 * time.Second)
	fmt.Println("pump")
	for i := 0; i < 10; i++ {
		fmt.Println("chanel:", len(ch))
		ch <- i
		fmt.Println("buffer %d", i) // prints only 0
		
	}

	fmt.Println("finsh")
}
func suck(ch chan int) {
	// time.Sleep(1 * time.Second)
	fmt.Println("suck")

	for {
		fmt.Println("chanel2:", len(ch))

		fmt.Println(<-ch)

		fmt.Println("pause")
		fmt.Scanln()
		if len(ch) == 0 {
			break
		}
		
	}

	fmt.Println("finsh2")

}
```
好的程式設計應該可以讓程式最後結束 gorutine 為可控，不像可控thread 可能會有 resource leak的問題
![](https://i.imgur.com/RaqhGS8.png)

# WaitGroup
這邊有點像操作系統 切換 process or thread，單核心要切換 process or thread 則還是在同一個核心上
假設有多核心則可以看到process or thread 可以同時run 再多核心上實現平行。
  runtime.GOMAXPROCS(1)
![](https://i.imgur.com/9BDgpQk.png)
  runtime.GOMAXPROCS(2)
 ![](https://i.imgur.com/A26MGrh.png)

```go
func main(){
    runtime.GOMAXPROCS(1)

	// wg is used to wait for the program to finish.
	// Add a count of two, one for each goroutine.
	var wg sync.WaitGroup
	wg.Add(2)

	fmt.Println("Start Goroutines")
	fmt.Println("first nowgoroutine :", runtime.NumGoroutine())
	// Declare an anonymous function and create a goroutine.
	go func() {
		// Schedule the call to Done to tell main we are done.
		defer wg.Done()

		// Display the alphabet three times.
		for count := 0; count < 3; count++ {
			for char := 'a'; char < 'a'+26; char++ {
				fmt.Printf("%c ", char)
			}
		}
	}()
	fmt.Println("sec nowgoroutine :", runtime.NumGoroutine())
	// Declare an anonymous function and create a goroutine.
	go func() {
		// Schedule the call to Done to tell main we are done.
		defer wg.Done()

		// Display the alphabet three times.
		for count := 0; count < 3; count++ {
			for char := 'A'; char < 'A'+26; char++ {
				fmt.Printf("%c ", char)
			}
		}
	}()

	// Wait for the goroutines to finish.
	fmt.Println("Waiting To Finish")
	fmt.Println("all nowgoroutine :", runtime.NumGoroutine())
	wg.Wait()
	fmt.Println("all nowgoroutine :", runtime.NumGoroutine())
	fmt.Println("\nTerminating Program")
    
}
```

