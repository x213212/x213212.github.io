---
title: "研究 cb compiler (一) 編譯 net/loveruby/cflat/ package"
date: "2020-01-22T17:32:00.001+08:00"
updated: "2020-03-16T00:04:28.066+08:00"
permalink: "/2020/01/cb-compiler-netloverubycflat-package.html"
original_url: "https://x8795278.blogspot.com/2020/01/cb-compiler-netloverubycflat-package.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-7818710184665180482"
tags: ["Compiler", "Tutorial"]
layout: post
---

最近要來研究一下compiler  

<https://github.com/leungwensen/cbc-ubuntu-64bit>  

cb是 基於 c語言的 簡化版，目前好像有看到cbc 編譯 cb 文件，看了官網也只有 make 檔，先來研究  

看到了build.properties build.xml，makefile 裡面也有 ant  

發現好像這部分的沒資料來幫忙補充一下  

所以complier 裡面需要有 jdk 和 jre 才能把 net 重新 編譯一次  

所以步驟就是
下載鏡像
> docker pull leungwensen/cbc-ubuntu-64bit

開啟鏡像
> docker run -t -i leungwensen/cbc-ubuntu-64bit

安裝 jdk
> apt-get install openjdk-8-jdk

安裝 ant
> apt-get install ant

安裝 javacc
> apt-get install javacc

設置 java home
> export JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64/"  
>
> export PATH=JAVAHOME/bin:JAVAHOME/bin:PATH

切到我們的目錄 我們動 compiler 裡面的
> cd net/loveruby/cflat/compiler/

Compiler.java
```
private Options parseOptions(String[] args) {
        try {
            return Options.parse(args);
        }
        catch (OptionParseError err) {
            errorHandler.error(err.getMessage());
            errorHandler.error("Try \"cbc --helphhh\" for usage");
            System.exit(1);
            return null;   // never reach
        }
    }
```
我們動裡面的 help 選項  

切到 /cbc 跟目錄
> cd cbc-ubuntu-64bit/  
>
> rm -rf build  
>
> ant

![](https://i.imgur.com/NArkkbN.png)

  

沒意外會看到開始編譯。  

![](https://i.imgur.com/PnUV8xT.png)

  

看到我們修改後的資料囉，接下來應該會對整個 cb compiler 研究一波。
