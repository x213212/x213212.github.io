---
title: "golang redis 分布式鎖的應用"
date: "2022-02-14T17:15:00.006+08:00"
updated: "2022-08-30T14:07:05.436+08:00"
permalink: "/2022/02/golang-redis.html"
original_url: "https://x8795278.blogspot.com/2022/02/golang-redis.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8520549789131568495"
tags: ["Redis"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Go_Logo_Blue.svg/1200px-Go_Logo_Blue.svg.png)

# golang redis 分布式鎖的應用
在業務邏輯可以看到就是redis 全部爭奪同一把鎖看誰先搶到
EXAMPLE_LOCK 還沒搶到的時候其他 goroutine 會重試再重試的過程中最多會嘗試五次還有每次的嘗試時間延遲多少，搶到鎖的會有一個守護process 等到任務結束，在任務執行過程中會一直延遲EXAMPLE_LOCK 的持有時間，原因就是任務不能中斷，直到任務結束才會釋出鎖給其他goroutine 去競爭。
https://cloud.tencent.com/developer/article/1820268
```go
func Testfucntion() string {
	go MockTest("A")
	go MockTest("B")
	go MockTest("C")
	go MockTest("D")
	go MockTest("E")
	// 用于测试goroutine接收到ctx.Done()信号后的打印
	// time.Sleep(time.Second * 2)
	return string("ok!")
}

// 重试次数
var retryTimes = 5

// 重试频率
var retryInterval = time.Millisecond * 50

// 锁的默认过期时间
var expiration time.Duration

// 模拟分布式业务加锁场景
func MockTest(tag string) {
	var ctx, cancel = context.WithCancel(context.Background())

	defer func() {
		// 停止goroutine
		cancel()
	}()

	// 随机value
	lockV := getRandValue()

	lockK := "EXAMPLE_LOCK"

	// 默认过期时间
	expiration = time.Millisecond * 200

	fmt.Println(tag + "尝试加锁")

	set, err := dao.RedisConn.SetNX(ctx, lockK, lockV, expiration).Result()

	if err != nil {
		panic(err.Error())
	}

	// 加锁失败,重试
	if set == false && retry(ctx, dao.RedisConn, lockK, lockV, expiration, tag) == false {
		fmt.Println(tag + " server unavailable, try again later")
		return
	}

	fmt.Println(tag + "成功加锁")

	// 加锁成功,新增守护线程
	go watchDog(ctx, dao.RedisConn, lockK, expiration, tag)
	amount--
	// 处理业务(通过随机时间延迟模拟)
	fmt.Println(tag + "等待业务处理完成...")

	time.Sleep(getRandDuration())
	fmt.Println(tag+"等待业务处理完成...%v", amount)
	// 业务处理完成
	// 释放锁
	val := delByKeyWhenValueEquals(ctx, dao.RedisConn, lockK, lockV)
	fmt.Println(tag+"释放结果:", val)
}

// 释放锁
func delByKeyWhenValueEquals(ctx context.Context, rdb *redis.Client, key string, value interface{}) bool {
	lua := `
-- 如果当前值与锁值一致,删除key
if redis.call('GET', KEYS[1]) == ARGV[1] then
	return redis.call('DEL', KEYS[1])
else
	return 0
end
`
	scriptKeys := []string{key}

	val, err := dao.RedisConn.Eval(ctx, lua, scriptKeys, value).Result()
	if err != nil {
		panic(err.Error())
	}

	return val == int64(1)
}

// 生成随机时间
func getRandDuration() time.Duration {
	rand.Seed(time.Now().UnixNano())
	min := 50
	max := 100
	return time.Duration(rand.Intn(max-min)+min) * time.Millisecond
}

// 生成随机值
func getRandValue() int {
	rand.Seed(time.Now().UnixNano())
	return rand.Int()
}

// 守护线程
func watchDog(ctx context.Context, rdb *redis.Client, key string, expiration time.Duration, tag string) {
	for {
		select {
		// 业务完成
		case <-ctx.Done():
			fmt.Printf("%s任务完成,关闭%s的自动续期\n", tag, key)
			return
			// 业务未完成
		default:
			// 自动续期
			dao.RedisConn.PExpire(ctx, key, expiration)
			// 继续等待
			time.Sleep(expiration / 2)
		}
	}
}

// 重试
func retry(ctx context.Context, rdb *redis.Client, key string, value interface{}, expiration time.Duration, tag string) bool {
	i := 1
	for i <= retryTimes {
		fmt.Printf(tag+"第%d次尝试加锁中...\n", i)
		set, err := dao.RedisConn.SetNX(ctx, key, value, expiration).Result()

		if err != nil {
			panic(err.Error())
		}

		if set == true {
			return true
		}

		time.Sleep(retryInterval)
		i++
	}
	return false
}

```

