---
title: "walk asm call graph"
date: "2022-11-04T21:33:00.003+08:00"
updated: "2022-11-04T21:34:18.372+08:00"
permalink: "/2022/11/walk-asm-call-graph.html"
original_url: "https://x8795278.blogspot.com/2022/11/walk-asm-call-graph.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6705772659780063859"
tags: ["Assembly", "Control Flow Graph", "RISC-V"]
layout: post
---

![](https://i.imgur.com/lP63j57.png)

# walk asm call graph
改動後的asm2cfg大概可以直接接受objdump 直接輸出相對應的call graph
新增了svg的向量圖，增加了顏色判斷與no jump 和 jump 的顏色標記，增加了模糊搜尋走訪dfs

![](https://i.imgur.com/lP63j57.png)
改動最多的地方還是能夠呈現asm 的 source code的部分，原理大概就是把comment當作inst，並給予address

```bash
pipenv shell
python -m src.asm2cfg ./a.asm

```
增加了模糊搜尋走訪dfs,為走訪過的節點標註顏色
![](https://i.imgur.com/cVGjmue.png)

