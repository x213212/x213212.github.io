---
title: "golang grpc"
date: "2022-02-06T21:06:00.004+08:00"
updated: "2022-02-06T21:06:56.828+08:00"
permalink: "/2022/02/golang-grpc.html"
original_url: "https://x8795278.blogspot.com/2022/02/golang-grpc.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3397979329838942805"
tags: ["Go"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Go_Logo_Blue.svg/1200px-Go_Logo_Blue.svg.png)

# grpc
```
apt install protoc-gen-go    
apt install protobuf-compiler
```

# proto
https://www.coder.work/article/198885
https://blog.csdn.net/qq_33565142/article/details/109647937
https://www.codeleading.com/article/69695861845/
```
protoc --go_out=plugins=grpc:. test.proto
```
```protobuf
syntax = "proto3";

package mdfk2020;
option go_package="./mdfk2020";
//定義Service名稱，
service SaySomethingService{ 
  //定義api名稱，傳入參數與回傳值
  rpc MDFK2020 (MDFKRequest) returns (MDFKResponse) {}
}

//傳入參數的spec
message MDFKRequest {
  string name = 1;  
}

//回傳值的spec
message MDFKResponse {
  string data = 1;
}
```

# server
```go
package main

import (
	"context"
	"fmt"
	"log"
	"net"

	pb "hello/test"

	"google.golang.org/grpc"
)

const (
	port = ":8787"
)

type server struct{}

func main() {
	// Create gRPC Server
	lis, err := net.Listen("tcp", port)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	s := grpc.NewServer()
	log.Println("gRPC server is running.")

	pb.RegisterSaySomethingServiceServer(s, &server{})
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}

//
func (s *server) MDFK2020(ctx context.Context, in *pb.MDFKRequest) (*pb.MDFKResponse, error) {
	fmt.Println("i receive:", in.Name)
	return &pb.MDFKResponse{Data: "Hello " + in.Name}, nil
}

```

# client
```go
package main

import (
	"context"

	"log"
	"time"

	pb "hello/test"

	"google.golang.org/grpc"
)

const (
	address = "localhost:8787"
)

func main() {

	conn, err := grpc.Dial(address, grpc.WithInsecure(), grpc.WithBlock())
	if err != nil {
		log.Fatalf("did not connect: %v", err)
	}
	defer conn.Close()
	c := pb.NewSaySomethingServiceClient(conn)
	mdfk2020(c, "GG")

}

//
func mdfk2020(c pb.SaySomethingServiceClient, name string) {

	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	res, err := c.MDFK2020(ctx, &pb.MDFKRequest{Name: name})
	if err != nil {
		log.Fatalf("could not mkdfk2020: %v", err)
	}
	log.Printf("gRPC response: %s", res.Data)
}

```
![](https://i.imgur.com/hgIJHmu.png)

