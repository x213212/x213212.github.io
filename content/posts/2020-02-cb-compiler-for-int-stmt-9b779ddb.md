---
title: "研究 cb compiler (二) 更改 FOR 與 INT STMT"
date: "2020-02-25T23:24:00.005+08:00"
updated: "2020-03-16T00:04:28.015+08:00"
permalink: "/2020/02/cb-compiler-for-int-stmt.html"
original_url: "https://x8795278.blogspot.com/2020/02/cb-compiler-for-int-stmt.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-4427785100122348162"
tags: ["cbc", "Compiler", "Tutorial"]
layout: post
---

# cbc

# 編譯器 Compiler、詞法分析器 Lexical Analyzer、語法分析器 Parser 該來往這邊把基本知識補足，在看到 <https://buzzorange.com/techorange/2020/01/21/coding-language-mulan-python/> 木蘭程式語言可能也是像 cbc 這種 基於高階語言實現的 二次complier 應該能更動到Stmt這一塊 ![](https://i.imgur.com/LrA5UgJ.png) 更改 vim net/loveruby/cflat/parser/Parser.jj ![](https://i.imgur.com/3vxqhOI.png) ``` import stdio; int main( int argc, char **argv) { god i = 0; for i = 0 in range(i=0,i<10,i++){ printf("how many god %d\n" , i); } return 0; } ``` ![](https://i.imgur.com/NCHnLKR.png) 經過測試 確實可以改動，下一階段該來針對上述幾個主題來進行研究了
