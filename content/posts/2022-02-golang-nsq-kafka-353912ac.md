---
title: "golang nsq & Kafka"
date: "2022-02-12T17:07:00.004+08:00"
updated: "2022-02-12T17:07:54.287+08:00"
permalink: "/2022/02/golang-nsq-kafka.html"
original_url: "https://x8795278.blogspot.com/2022/02/golang-nsq-kafka.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5245947669922764270"
tags: ["Go", "kafka", "nsq"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Go_Logo_Blue.svg/1200px-Go_Logo_Blue.svg.png)

# golang nsq & Kafka
https://cloud.tencent.com/developer/article/1820268
https://ithelp.ithome.com.tw/articles/10194183
https://iter01.com/547005.html

# docker compose
![](https://i.imgur.com/wCRDhn0.png)
docker compose
```yaml
version: '3'
services:
  nsqlookupd:
    image: nsqio/nsq
    command: /nsqlookupd
    ports:
      - "4160"
      - "4161"
  nsqd:
    image: nsqio/nsq
    command: /nsqd --lookupd-tcp-address=nsqlookupd:4160
    depends_on:
      - nsqlookupd
    ports:
      - "4150"
      - "4151"
  nsqadmin:
    image: nsqio/nsq
    command: /nsqadmin --lookupd-http-address=nsqlookupd:4161
    depends_on:
      - nsqlookupd  
    ports:
      - "4171"

```
```bash
docker compose up -d
docker compose down
docker compose ps
```
# nsq-consumer
```go
package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/nsqio/go-nsq"
)

type myMessageHandler struct{}

func (h *myMessageHandler) HandleMessage(m *nsq.Message) error {
	log.Printf("接收到了一個訊息：%v", m)
	log.Printf("這個訊息轉換成字串就是：%v", string(m.Body))
	return nil
}

func main() {
	//建立Consumer
	config := nsq.NewConfig()
	consumer, err := nsq.NewConsumer("GONSQ_TOPIC", "channel", config)
	if err != nil {
		log.Fatal(err)
	}
	//新增一個handler來處理收到訊息時動作
	consumer.AddHandler(&myMessageHandler{})

	//連線到NSQD
	err = consumer.ConnectToNSQD("localhost:56117")
	if err != nil {
		log.Fatal(err)
	}

	//卡住，不要讓main.go執行完就結束
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	<-sigChan

	consumer.Stop()
}

```
# nsq-producer
```go
package main

import (
	"log"

	"github.com/nsqio/go-nsq"
)

func main() {
	//建立一個Producer
	config := nsq.NewConfig()
	producer, err := nsq.NewProducer("127.0.0.1:56117", config)
	if err != nil {
		log.Fatal(err)
	}

	messageBody := []byte("hello")
	topicName := "GONSQ_TOPIC"
	//發佈到定義好的topic
	err = producer.Publish(topicName, messageBody)
	if err != nil {
		log.Fatal(err)
	}

	producer.Stop()
}

```
![](https://i.imgur.com/NRxzPdX.png)

# kafka
![](https://i.imgur.com/7OpsY67.png)
zookeeper 算是類似 spring eureka的東西
https://codeantenna.com/a/Ne1DCTJikV
https://cutejaneii.wordpress.com/2017/06/19/docker-7-%E7%94%A8docker%E5%BB%BA%E7%AB%8Bkafka%E6%9C%8D%E5%8B%99%E4%B8%8A/
https://www.cnblogs.com/swordfall/p/10014300.html
https://www.codeleading.com/article/56604973219/
# docker compose
```yaml
 
networks:
  kafka-cluster:
    name: kafka-cluster
    driver: bridge
 
services:
  zookeeper:
    image: bitnami/zookeeper:3.6.2
    container_name: zookeeper
    ports:
      - '2181:2181'
    environment:
      - ALLOW_ANONYMOUS_LOGIN=yes
    networks:
      - kafka-cluster
      
  kafka1:
    image: bitnami/kafka:2.7.0
    container_name: kafka1
    ports:
      - '9093:9093'
    environment:
      - KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper:2181
      - ALLOW_PLAINTEXT_LISTENER=yes
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CLIENT:PLAINTEXT,EXTERNAL:PLAINTEXT
      - KAFKA_CFG_LISTENERS=CLIENT://:9092,EXTERNAL://:9093
      - KAFKA_CFG_ADVERTISED_LISTENERS=CLIENT://kafka1:9092,EXTERNAL://localhost:9093
      - KAFKA_INTER_BROKER_LISTENER_NAME=CLIENT
      - KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE=true
    depends_on:
      - zookeeper
    networks:
      - kafka-cluster
      
  kafka2:
    image: bitnami/kafka:2.7.0
    container_name: kafka2
    ports:
      - '9094:9094'
    environment:
      - KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper:2181
      - ALLOW_PLAINTEXT_LISTENER=yes
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CLIENT:PLAINTEXT,EXTERNAL:PLAINTEXT
      - KAFKA_CFG_LISTENERS=CLIENT://:9092,EXTERNAL://:9094
      - KAFKA_CFG_ADVERTISED_LISTENERS=CLIENT://kafka2:9092,EXTERNAL://localhost:9094
      - KAFKA_INTER_BROKER_LISTENER_NAME=CLIENT
      - KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE=true
    depends_on:
      - zookeeper
    networks:
      - kafka-cluster
      
  kafka3:
    image: bitnami/kafka:2.7.0
    container_name: kafka3
    ports:
      - '9095:9095'
    environment:
      - KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper:2181
      - ALLOW_PLAINTEXT_LISTENER=yes
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CLIENT:PLAINTEXT,EXTERNAL:PLAINTEXT
      - KAFKA_CFG_LISTENERS=CLIENT://:9092,EXTERNAL://:9095
      - KAFKA_CFG_ADVERTISED_LISTENERS=CLIENT://kafka3:9092,EXTERNAL://localhost:9095
      - KAFKA_INTER_BROKER_LISTENER_NAME=CLIENT
      - KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE=true
    depends_on:
      - zookeeper
    networks:
      - kafka-cluster
      
  kafdrop:
    image: obsidiandynamics/kafdrop:latest
    container_name: kafdrop
    ports:
      - 9000:9000
    environment:
      - KAFKA_BROKERCONNECT=kafka1:9092,kafka2:9092,kafka3:9092
    depends_on: 
      - kafka1
    networks:
      - kafka-cluster

```

# kafka-consumer
```go
package main

import (
	"fmt"
	"sync"

	"github.com/Shopify/sarama"
)

var wg sync.WaitGroup

func main() {
	consumer, err := sarama.NewConsumer([]string{"127.0.0.1:9093"}, nil)
	if err != nil {
		fmt.Println("consumer connect error:", err)
		return
	}
	fmt.Println("connnect success...")
	defer consumer.Close()
	partitions, err := consumer.Partitions("revolution")
	if err != nil {
		fmt.Println("geet partitions failed, err:", err)
		return
	}

	for _, p := range partitions {
		partitionConsumer, err := consumer.ConsumePartition("revolution", p, sarama.OffsetOldest)
		if err != nil {
			fmt.Println("partitionConsumer err:", err)
			continue
		}
		wg.Add(1)
		go func() {
			for m := range partitionConsumer.Messages() {
				fmt.Printf("key: %s, text: %s, offset: %d\n", string(m.Key), string(m.Value), m.Offset)
			}
			wg.Done()
		}()
	}
	wg.Wait()
}

```
# kafka-producer
```go
package main

import (
	"fmt"

	"github.com/Shopify/sarama"
)

func main() {
	// 新建一个arama配置实例
	config := sarama.NewConfig()

	// WaitForAll waits for all in-sync replicas to commit before responding.
	config.Producer.RequiredAcks = sarama.WaitForAll

	// NewRandomPartitioner returns a Partitioner which chooses a random partition each time.
	config.Producer.Partitioner = sarama.NewRandomPartitioner

	config.Producer.Return.Successes = true

	// 新建一个同步生产者
	client, err := sarama.NewSyncProducer([]string{"localhost:9093"}, config)
	if err != nil {
		fmt.Println("producer close, err:", err)
		return
	}
	defer client.Close()

	// 定义一个生产消息，包括Topic、消息内容、
	msg := &sarama.ProducerMessage{}
	msg.Topic = "revolution"
	msg.Key = sarama.StringEncoder("miles")
	msg.Value = sarama.StringEncoder("hello world...")

	// 发送消息
	pid, offset, err := client.SendMessage(msg)

	msg2 := &sarama.ProducerMessage{}
	msg2.Topic = "revolution"
	msg2.Key = sarama.StringEncoder("monroe")
	msg2.Value = sarama.StringEncoder("hello world2...")
	pid2, offset2, err := client.SendMessage(msg2)

	if err != nil {
		fmt.Println("send message failed,", err)
		return
	}
	fmt.Printf("pid:%v offset:%v\n", pid, offset)
	fmt.Printf("pid2:%v offset2:%v\n", pid2, offset2)
}

```

