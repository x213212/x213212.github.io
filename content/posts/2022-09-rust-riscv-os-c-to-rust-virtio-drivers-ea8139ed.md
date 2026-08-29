---
title: "rust-riscv-os c to rust virtio-drivers lib callback"
date: "2022-09-06T07:02:00.001+08:00"
updated: "2022-09-06T07:02:06.205+08:00"
permalink: "/2022/09/rust-riscv-os-c-to-rust-virtio-drivers.html"
original_url: "https://x8795278.blogspot.com/2022/09/rust-riscv-os-c-to-rust-virtio-drivers.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-7477693806976976008"
tags: ["rust", "virtio"]
layout: post
---

![](https://i.imgur.com/4PJM3yu.png)

# rust-riscv-os c to rust virtio-drivers lib callback
https://learningos.github.io/rust-based-os-comp2022/chapter8/index.html
https://zhuanlan.zhihu.com/p/344819263
https://avacariu.me/writing/2014/calling-rust-from-c
http://rcore-os.cn/rCore-Tutorial-deploy/docs/lab-4/guide/part-6.html
https://docs.oasis-open.org/virtio/virtio/v1.1/cs01/virtio-v1.1-cs01.pdf
https://cloud.tencent.com/developer/article/1770529
https://youtu.be/vkvZ7ohx-84
https://mindchasers.com/dev/rv-getting-started
https://github.com/riscv-collab/riscv-gnu-toolchain
https://ithelp.ithome.com.tw/articles/10257612
https://ppfocus.com/0/au628a911.html
https://cloud.tencent.com/developer/article/1770529
https://magiclen.org/rust-no-std/

看了一些文章，原本想從qemu vga動手，後來越看越多可能要整合opensbi,驅動還要是virtio還是找不到有關於最新的opensbi virtio 的驅動範例，不過有找到rust 版本的
https://github.com/rcore-os/virtio-drivers
主要嘗試在
https://github.com/plctlab/riscv-operating-system-mooc
是否有可能在link 階段靜態編譯，讓實驗用的os用c語言開機去call rust函數在返回

參考一下原版的virtio-drivers
![](https://i.imgur.com/lMgOukk.png)
可以看到一些步驟我就省略，virtio透過加載opensbi 可以抓到驅動，算是一層interface
這個專案已經寫了一些test driver.

| Device   | Status              |
| --- | --- |
| Queue    | ✅                 |
| Block    | ✅                 |
| Net      | ✅                 |
| GPU      | ✅                 |
| Input    | ✅                 |
| Console  | ✅                 |
| ...      | ❌ Not implemented |

我覺得驅動寫到這邊已經蠻充足的了，今天我想要完成一個gui的介面也只要透過
![](https://i.imgur.com/FJ5AxlN.png)
即可以對qemu的記憶體區段寫入資料，
![](https://i.imgur.com/rckyGf4.png)
稍微修改一下
![](https://i.imgur.com/se8hH8S.png)
問題來了能不能把它當成強制改成靜態連結進行編譯，用c call rust 的fucntion，來嘗試一下

大概會拆成兩個步驟，但是共同的第一步都要是降成相同位元的compiler
riscv-operating-system-mooc
virtio-drivers
virtio-drivers我們委屈一下，riscv64  降成riscv32

但是riscv64 預設qemu的bios 有支援 opensbi所以又要重編一下 opensbi

git clone https://github.com/riscv/opensbi.git

FW_JUMP_ADDR是我們開機完第一個要跳轉的address我們這邊寫死，因為要順應LD的起始位置0x80200000

這兩個有預設opensbi寫好的加載範例
```
/home/x213212/opensbi/firmware/
```

![](https://i.imgur.com/vEYsBO5.png)
```
/home/x213212/opensbi/firmware/payloads
```

![](https://i.imgur.com/iMRSBhb.png)

我們在把os riscv-operating-system-mooc第三章的部分的printf 改入這個範例

![](https://i.imgur.com/LMq7ugG.png)

進行編譯
```
export CROSS_COMPILE=riscv64-unknown-elf-
make PLATFORM=generic clean
make PLATFORM=generic FW_JUMP_ADDR=0x80200000

```

位於課程的riscv-operating-system-mooc
/riscv-operating-system-mooc/code/common.mk
編譯和qemu都要降為32位元
```
CROSS_COMPILE = riscv32-unknown-elf-
CFLAGS = -nostdlib -fno-builtin -march=rv32imafdc -mabi=ilp32 -g -Wall
# qemu-system-riscv64 \
#   --machine virt \
#   --nographic \
#   --bios default
#QEMU = qemu-system-riscv32 
#QFLAGS = --nographic -smp 1 -machine  virt -bios none
QEMU = qemu-system-riscv32
QFLAGS = --nographic -smp 1 -machine  virt -bios fw_jump.elf  -device loader,file=test.bin,addr=0x80200000  -device virtio-gpu-device
GDB = gdb-multiarch
CC = ${CROSS_COMPILE}gcc
OBJCOPY = ${CROSS_COMPILE}objcopy
OBJDUMP = ${CROSS_COMPILE}objdump
~                                    
```
opensbi編出來的是sivefive的韌體
make run 進行啟動qemu
```
-device loader,file=test.bin,addr=0x80200000
```
跳轉位置記得設定好
把剛剛編譯出來的test.elf ,test.bin,fw_jump.elf 都copy到其中一個riscv-operating-system-mooc 的章節我們選選01-helloRVOS 章節
![](https://i.imgur.com/XX48siI.png)

到這邊我們就可以讓課程riscv-operating-system-mooc 加載 opensbi進行啟動。

第二個部分就是c在沒有std環境到底能不能去呼叫rust的東西，這邊我直接把
https://github.com/rcore-os/virtio-drivers
改成靜態連結，目前還在嘗試可以編譯的過，唯一要注意的是很多文章都沒有明確指出到底編譯成std lib 會報錯的問題有那些
# Cargo.toml
```toml
[package]
name = "riscv"
version = "0.1.0"
authors = ["Runji Wang <wangrunji0408@163.com>"]
edition = "2018"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[lib]
name = "double_input"
crate-type = ["staticlib"]

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html
[profile.dev]
panic = "abort"

[profile.release]
panic = "abort"

[dependencies]

log = "0.4"
riscv = "0.6"
opensbi-rt = { git = "https://github.com/rcore-os/opensbi-rt.git", rev = "1308cc5" }
device_tree = { git = "https://github.com/rcore-os/device_tree-rs", rev = "2fa8411" }
virtio-drivers = { path = "../.." }
lazy_static = { version = "1.4", features = ["spin_no_std"] }
spin = "0.9.2"
linked_list_allocator = "0.10.1"
spinning_top = "0.2.4"

buddy_system_allocator =  "0.6"
```
# lib.rs
```rs
#![no_std]
#![no_main]
#![crate_type = "staticlib"]
#![feature(llvm_asm)]
#![feature(default_alloc_error_handler)]

extern crate alloc;

use alloc::vec;
use device_tree::util::SliceRead;
use device_tree::{DeviceTree, Node};
use log::{info, warn};
use virtio_drivers::*;
use virtio_impl::HalImpl;
mod virtio_impl;
use buddy_system_allocator::LockedHeap;
#[global_allocator]
static HEAP_ALLOCATOR: LockedHeap = LockedHeap::empty();
#[no_mangle]

pub extern "C" fn double_input() {
    info!("device tree ");
    let hi = "hi";
    let mut count = 0;
   
    // let _ret: usize;
    // let arg0: usize = b'O' as usize;
    // let arg1: usize = 0;
    // let arg2: usize = 0;
    // let which: usize = 1;
    // unsafe {
    //     llvm_asm!("ecall"
    //          : "={x10}" (_ret)
    //          : "{x10}" (arg0), "{x11}" (arg1), "{x12}" (arg2), "{x17}" (which)
    //          : "memory"
    //          : "volatile"
    //     );
    // }
    while count < 100000 {
        // println!("{}, count: {}", hi, count);
        count += 1;
    }
    // loop {}
}
use core::panic::PanicInfo;

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {}
}

fn init_dt(dtb: usize) {
    info!("device tree @ {:#x}", dtb);
    #[repr(C)]
    struct DtbHeader {
        be_magic: u32,
        be_size: u32,
    }
    let header = unsafe { &*(dtb as *const DtbHeader) };
    let magic = u32::from_be(header.be_magic);
    const DEVICE_TREE_MAGIC: u32 = 0xd00dfeed;
    assert_eq!(magic, DEVICE_TREE_MAGIC);
    let size = u32::from_be(header.be_size);
    let dtb_data = unsafe { core::slice::from_raw_parts(dtb as *const u8, size as usize) };
    let dt = DeviceTree::load(dtb_data).expect("failed to parse device tree");
    walk_dt_node(&dt.root);
}

fn walk_dt_node(dt: &Node) {
    if let Ok(compatible) = dt.prop_str("compatible") {
        if compatible == "virtio,mmio" {
            virtio_probe(dt);
        }
    }
    for child in dt.children.iter() {
        walk_dt_node(child);
    }
}

fn virtio_probe(node: &Node) {
    if let Some(reg) = node.prop_raw("reg") {
        let paddr = reg.as_slice().read_be_u64(0).unwrap();
        let size = reg.as_slice().read_be_u64(8).unwrap();
        let vaddr = paddr;
        info!("walk dt addr={:#x}, size={:#x}", paddr, size);
        let header = unsafe { &mut *(vaddr as *mut VirtIOHeader) };
        info!(
            "Detected virtio device with vendor id {:#X}, device type {:?}",
            header.vendor_id(),
            header.device_type(),
        );
        info!("Device tree node {:?}", node);
        match header.device_type() {
            DeviceType::Block => virtio_blk(header),
            DeviceType::GPU => virtio_gpu(header),
            DeviceType::Input => virtio_input(header),
            DeviceType::Network => virtio_net(header),
            t => warn!("Unrecognized virtio device: {:?}", t),
        }
    }
}

fn virtio_blk(header: &'static mut VirtIOHeader) {
    let mut blk = VirtIOBlk::<HalImpl>::new(header).expect("failed to create blk driver");
    let mut input = vec![0xffu8; 512];
    let mut output = vec![0; 512];
    for i in 0..32 {
        for x in input.iter_mut() {
            *x = i as u8;
        }
        blk.write_block(i, &input).expect("failed to write");
        blk.read_block(i, &mut output).expect("failed to read");
        assert_eq!(input, output);
    }
    info!("virtio-blk test finished");
}

fn virtio_gpu(header: &'static mut VirtIOHeader) {
    let mut gpu = VirtIOGpu::<HalImpl>::new(header).expect("failed to create gpu driver");
    let fb = gpu.setup_framebuffer().expect("failed to get fb");
    for y in 0..768 {
        for x in 0..1024 {
            let idx = (y * 1024 + x) * 4;
            fb[idx] = x as u8;
            fb[idx + 1] = y as u8;
            fb[idx + 2] = (x + y) as u8;
        }
    }
    gpu.flush().expect("failed to flush");
    info!("virtio-gpu test finished");
}

fn virtio_input(header: &'static mut VirtIOHeader) {
    //let mut event_buf = [0u64; 32];
    let mut _input = VirtIOInput::<HalImpl>::new(header).expect("failed to create input driver");
    // loop {
    //     input.ack_interrupt().expect("failed to ack");
    //     info!("mouse: {:?}", input.mouse_xy());
    // }
    // TODO: handle external interrupt
}

fn virtio_net(header: &'static mut VirtIOHeader) {
    let mut net = VirtIONet::<HalImpl>::new(header).expect("failed to create net driver");
    let mut buf = [0u8; 0x100];
    let len = net.recv(&mut buf).expect("failed to recv");
    info!("recv: {:?}", &buf[..len]);
    net.send(&buf[..len]).expect("failed to send");
    info!("virtio-net test finished");
}

```

移植會遇到的雷
```
#![feature(default_alloc_error_handler)]
#[global_allocator]
static HEAP_ALLOCATOR: LockedHeap = LockedHeap::empty();
```
記得cargo.toml
```
buddy_system_allocator =  "0.6"
```
這邊主要嘗試把 virtio-drivers編譯成靜態連結，還不理功能是否正常。

最後我們下cargo build
我們會在相對應的平台找到生成的靜態連結檔案
![](https://i.imgur.com/rNVErfI.png)

一樣我們選01-helloRVOS 章節

 libdouble_input.a -Wl,--gc-sections
 記得在link階段進行連結
```bash
riscv32-unknown-elf-gcc -nostdlib -fno-builtin -march=rv32imafdc -mabi=ilp32 -g -Wall  -c -o start.o start.S
riscv32-unknown-elf-gcc -nostdlib -fno-builtin -march=rv32imafdc -mabi=ilp32 -g -Wall  -c -o kernel.o kernel.c
riscv32-unknown-elf-gcc -nostdlib -fno-builtin -march=rv32imafdc -mabi=ilp32 -g -Wall  -c -o uart.o uart.c
riscv32-unknown-elf-gcc -nostdlib -fno-builtin -march=rv32imafdc -mabi=ilp32 -g -Wall  -Ttext=0x80000000 -o os.elf start.o kernel.o uart.o  libdouble_input.a -Wl,--gc-sections 
riscv32-unknown-elf-objcopy -O binary os.elf os.bin

```
這邊比較注意的是我目前吧extern crate opensbi_rt;
移除，不然會出現重複 _start，這是位於這個opensbi_rt應該是寫驅動的作者應該也是開機加載跟程式綁再一起，目前前面階段是ok的，那麼我們在rust應該可以直接呼叫相對應的lib應該Ok(吧，這個問題以後再探討，當前主要任務是觸發用kernel.c再去呼叫rust寫的fucntion
![](https://i.imgur.com/lnkx43L.png)

這邊要注意又再改回然後預設起始位置是0x80000000
/riscv-operating-system-mooc/code/common.mk
```
CROSS_COMPILE = riscv32-unknown-elf-
CFLAGS = -nostdlib -fno-builtin -march=rv32imafdc -mabi=ilp32 -g -Wall 
# qemu-system-riscv64 \
#   --machine virt \
#   --nographic \
#   --bios default
QEMU = qemu-system-riscv32 
QFLAGS = --nographic -smp 1 -machine  virt -bios none
#QEMU = qemu-system-riscv32 
#QFLAGS = --nographic -smp 1 -machine  virt -bios fw_jump.elf  -device loader,file=test.bin,addr=0x80200000  -device #virtio-gpu-device 
GDB = gdb-multiarch
CC = ${CROSS_COMPILE}gcc
OBJCOPY = ${CROSS_COMPILE}objcopy
OBJDUMP = ${CROSS_COMPILE}objdump
```
# double_input function

https://github.com/alexcrichton/rust-ffi-examples
相關靜態連結的範例，可以跟著改修改返回值
![](https://i.imgur.com/FpGbFhB.png)
![](https://i.imgur.com/ZtvLZSI.png)

![](https://i.imgur.com/rWpiDhe.png)
可以看到會稍微延遲在觸發第二個print
![](https://i.imgur.com/4PJM3yu.png)

到這邊我們的c就可以call rust的fucntion,主要還是因為找不到可以有人專門在寫這部分的driver想說能不能移花接木一下進行呼叫，那麼我只要驅動的部分呼叫rust的就好了，這樣改可能可以成功，後面第三部可能要
riscv-operating-system-mooc移植到剛剛的opensbi的範例啟動，再來要考慮的是這樣方式的link是否有可能會產生衝突，因為rust的lib移除掉opensbi_rt不知正常啟用的話lib功能會不會有問題.

## References

- [PLCT Lab / riscv-operating-system-mooc](https://github.com/plctlab/riscv-operating-system-mooc) — 文中使用的 RISC-V OS 課程與範例。
- [rCore-Tutorial-Book-v3](https://rcore-os.cn/rCore-Tutorial-Book-v3/) — RISC-V Rust OS 教材。
- [OASIS Virtio specification v1.1](https://docs.oasis-open.org/virtio/virtio/v1.1/cs01/virtio-v1.1-cs01.pdf) — Virtio 裝置介面規格。

