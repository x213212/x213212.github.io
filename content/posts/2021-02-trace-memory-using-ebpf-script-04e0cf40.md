---
title: "trace memory using ebpf script"
date: "2021-02-06T18:08:00.003+08:00"
updated: "2021-02-06T18:08:42.061+08:00"
permalink: "/2021/02/trace-memory-using-ebpf-script.html"
original_url: "https://x8795278.blogspot.com/2021/02/trace-memory-using-ebpf-script.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8590260162013096977"
tags: ["eBPF", "linux kernel"]
layout: post
---

![](https://miro.medium.com/max/1024/1*ABo4dTsrgA7UboVI7c6yIA.jpeg)

# 前些天記錄了關於mtrace 一些東西
實驗室同學提到了一些方式，找到了切入 malloc 的一些方法，跟當初猜想的一樣動態攔截可能遇到這些情況可以透過加鎖的方式去達成攔截但是效率就不太敢保證了
http://firewof5566.blogspot.com/2015/04/mtrace3thread-safety.html
https://stackoverflow.com/questions/2020997/using-glibc-malloc-hooks-in-a-thread-safe-manner
透過交替原生kernel.so 去過濾 caller 方式就可以進行攔截。

不過我有找到另一個東西以後當維運應該會用到
為此寫個預備方法想辦法去攔截

 sudo bash -c 'PYTHONPATH=/usr/lib/python2.7/site-packages python ~/bcc/examples/test_mem.py -p 6472'
https://hackmd.io/@sysprog/linux-ebpf?type=view#%E5%AF%A6%E9%9A%9B%E6%93%8D%E4%BD%9C
https://www.youtube.com/watch?v=UmCnh6mELwA&t=1345s
大大都解釋的很清楚了，主要就是能在 uprobe 地方，去做攔截，而不是去 malloc 的地方去直接更改 code上述兩篇文章有寫的是總不可能再大量的 malloc 地方加上鎖這樣對這些程式的效率或者可能會變動原本程式的流程也說不定，使用 bcc這樣好處是在系統的 cost 開銷會比較小，也可在非侵入的方式去撈取可用訊息...
https://github.com/iovisor/bcc/blob/master/INSTALL.md#ubuntu---source
在安裝的時候，遇到一些問題，我是透過重新編譯 bcc 才可以呼叫
```
# Trusty (14.04 LTS) and older
VER=trusty
echo "deb http://llvm.org/apt/$VER/ llvm-toolchain-$VER-3.7 main
deb-src http://llvm.org/apt/$VER/ llvm-toolchain-$VER-3.7 main" | \
  sudo tee /etc/apt/sources.list.d/llvm.list
wget -O - http://llvm.org/apt/llvm-snapshot.gpg.key | sudo apt-key add -
sudo apt-get update

# For Bionic (18.04 LTS)
sudo apt-get -y install bison build-essential cmake flex git libedit-dev \
  libllvm6.0 llvm-6.0-dev libclang-6.0-dev python zlib1g-dev libelf-dev

# For Eoan (19.10) or Focal (20.04.1 LTS)
sudo apt install -y bison build-essential cmake flex git libedit-dev \
  libllvm7 llvm-7-dev libclang-7-dev python zlib1g-dev libelf-dev libfl-dev

# For other versions
sudo apt-get -y install bison build-essential cmake flex git libedit-dev \
  libllvm3.7 llvm-3.7-dev libclang-3.7-dev python zlib1g-dev libelf-dev

# For Lua support
sudo apt-get -y install luajit luajit-5.1-dev
Install and compile BCC
git clone https://github.com/iovisor/bcc.git
mkdir bcc/build; cd bcc/build
cmake ..
make
sudo make install
cmake -DPYTHON_CMD=python3 .. # build python3 binding
pushd src/python/
make
sudo make install
popd

```
```
 sudo bash -c 'PYTHONPATH=/usr/lib/python2.7/site-packages python ~/bcc/tools/memleak.py -p 6472'
```

也有人寫相對應的memleak
 sudo bash -c 'PYTHONPATH=/usr/lib/python2.7/site-packages python ~/bcc/examples/test_mem.py -p 6472'

這可能在遇到追蹤 linux kernel 會很重要!

