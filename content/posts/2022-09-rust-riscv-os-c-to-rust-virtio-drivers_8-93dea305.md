---
title: "rust-riscv-os c to rust virtio-drivers lib callback succ"
date: "2022-09-08T02:32:00.004+08:00"
updated: "2022-09-08T02:32:30.711+08:00"
permalink: "/2022/09/rust-riscv-os-c-to-rust-virtio-drivers_8.html"
original_url: "https://x8795278.blogspot.com/2022/09/rust-riscv-os-c-to-rust-virtio-drivers_8.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6607943936962553285"
tags: ["rust"]
layout: post
---

![](https://i.imgur.com/O68sSSw.png)

# rust-riscv-os c to rust virtio-drivers lib callback success
昨天有說到是否有可能rust 去 call c 或者 c 去call rust，假設其中一項成立都有利於更加快速的開發我們的系統，我們就可以把一些寫好的c 給 rust 用，rust有寫的 c直接呼叫，看了太多程式碼都沒有看到具體實現的過程有沒有可能來實驗一下就知道.

首先我們先研究
virtio-drivers
/virtio-drivers/examples/riscv/Cargo.toml
```toml
[package]
name = "riscv"
version = "0.1.0"
authors = ["Runji Wang <wangrunji0408@163.com>"]
edition = "2018"
build = "build.rs"

[build-dependencies]
cc = "1.0"
# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
log = "0.4"
riscv = "0.6"
libc = "0.2"
#opensbi-rt = { git = "https://github.com/rcore-os/opensbi-rt.git", rev = "1308cc5" }
opensbi-rt = {  path = "../../../mod/opensbi-rt" }
device_tree = { git = "https://github.com/rcore-os/device_tree-rs", rev = "2fa8411" }
virtio-drivers = { path = "../.." }
lazy_static = { version = "1.4", features = ["spin_no_std"] }
```

上一次版本把opensbi-rt 拿掉應該是沒辦法動的，但是引用這個lib 又會說_start 重複定義，
那我們進一步的去看opensbi-rt rev 1308cc5版本的 source code
#opensbi-rt = { git = "https://github.com/rcore-os/opensbi-rt.git", rev = "1308cc5"
https://github.com/rcore-os/riscv-sbi-rt/actions/runs/732046668
也就是這個版本的source code
https://github.com/rcore-os/riscv-sbi-rt/tree/1308cc5cbe7665dc0e6c515377c1e0bdd305fa93

載下來我們就可以把opensbi-rt git 替換成 path
```
#opensbi-rt = { git = "https://github.com/rcore-os/opensbi-rt.git", rev = "1308cc5" }
opensbi-rt = {  path = "../../../mod/opensbi-rt" }
```
這樣以後我們完全客製化opensbi-rt 就都ok了

opensbi-rt/src/runtime.rs
```
global_asm!(
    r#"
    .section .text.entry
    .globl _start
_start:
    la sp, bootstacktop
    call init
    .section .bss.stack
    .align 12
    .global bootstack
bootstack:
    .space 4096 * 16
    .global bootstacktop
bootstacktop:
"#
);
```
就是這個地方導致_start重複定義，以後想用opensbi firmware/payloads/的defalut直接改我想也是ok的
https://github.com/riscv-software-src/opensbi
https://github.com/riscv-software-src/opensbi/tree/master/firmware/payloads

下面我們還是把引導還是交給 rust來引導，主要是看rust引導完 再去call c function,然後c也要同時也能回call rust，這樣我就可以選擇要在c開發os 或者 rust 開發os .

Cargo.toml
```toml
build = "build.rs"
```
build.rs
```rs
extern crate cc;

fn main() {
    cc::Build::new()
        .file("src/double.c")
        .compile("libdouble.a");
        
        cc::Build::new()
        .file("src/test.c")
        .compile("libtest.a");
}
```
這邊到時候要把這兩個c靜態連結，寫兩個c和一個h
double.c
```c
extern void test(); <===c 呼叫 rust

int double_input(int input) { <===rust 呼叫 c
    uart_init();
    uart_puts("Hello, RVOS!\n");
  
    test(); <=== c call rust
    test2(); <===c call c
    return input * 2;
}
```
![](https://i.imgur.com/J77gn7R.png)

```rust
宣告c funciotn
extern {
    fn double_input(input: i32) -> i32;
}

#[no_mangle]
pub extern "C" fn test() {
    info!("hello c call rust");
}

#[no_mangle]
extern "C" fn main2(_hartid: usize, device_tree_paddr: usize) {
    log::set_max_level(LevelFilter::Info);
    init_dt(device_tree_paddr);
    info!("test end");
    let input = 4;
    let output = unsafe { double_input(input) }; <== rust call c 
    info!("hello rust call @ {:#x}", output);
    loop{};
}
```

![](https://i.imgur.com/O68sSSw.png)
到這邊那麼我們就可以專心看要在c 寫os ,驅動的部分就藉由傳參數給rust 讓他去負責，
或者反過來 rust 寫os ,c 來專門開發其他的驅動等等之類的
不過rust 沒像c\c++ 可以隨意初始化變數，然後指向，這邊可能要涉及use lazy_static::lazy_static;
當然rust要直接去改global vaiable也要處理一些鎖的問題 https://github.com/x213212/virtio-drivers

