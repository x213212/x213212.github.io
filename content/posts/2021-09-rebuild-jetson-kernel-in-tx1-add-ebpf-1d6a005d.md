---
title: "rebuild jetson kernel in tx1 add ebpf module"
date: "2021-09-10T15:26:00.002+08:00"
updated: "2021-09-10T15:26:38.941+08:00"
permalink: "/2021/09/rebuild-jetson-kernel-in-tx1-add-ebpf.html"
original_url: "https://x8795278.blogspot.com/2021/09/rebuild-jetson-kernel-in-tx1-add-ebpf.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8418716130050532632"
tags: ["eBPF"]
layout: post
---

![](https://i.imgur.com/Eo16dUX.png)

# rebuild jetson kernel in tx1
https://blog.kevmo314.com/compiling-custom-kernel-modules-on-the-jetson-nano.html
![](https://i.imgur.com/MHBkTH6.png)

## Build Kernel
Follow these instructions to build and install the kernel image and device tree.

1. Download and install the Toolchain
NVIDIA recommends using the Linaro 7.3.1 2018.05 toolchain for L4T 32.3 (Toolchain)

Download the pre-built toolchain binaries from: http://releases.linaro.org/components/toolchain/binaries/7.3-2018.05/aarch64-linux-gnu/gcc-linaro-7.3.1-2018.05-x86_64_aarch64-linux-gnu.tar.xz

wget http://releases.linaro.org/components/toolchain/binaries/7.3-2018.05/aarch64-linux-gnu/gcc-linaro-7.3.1-2018.05-x86_64_aarch64-linux-gnu.tar.xz
Execute the following commands to extract the toolchain:

```
mkdir $HOME/l4t-gcc
cd $HOME/l4t-gcc
tar xf gcc-linaro-7.3.1-2018.05-x86_64_aarch64-linux-gnu.tar.xz
```
2. Download the kernel sources
You can download the kernel source files and then manually extract them. it is recommended to instead sync with git.

In a browser, navigate to: https://developer.nvidia.com/embedded/downloads. Locate and download the L4T Sources for your release. (L4T Sources 32.3.1 2019/12/17) or run the command below:

wget https://developer.download.nvidia.com/embedded/L4T/r32-3-1_Release_v1.0/Sources/T210/public_sources.tbz2
Execute the following commands to extract the kernel:

```
tar -xvf public_sources.tbz2
cd Linux_for_Tegra/source/public
JETSON_NANO_KERNEL_SOURCE=$(pwd)
tar -xf kernel_src.tbz2
```
3. Compile kernel and dtb
Follow the steps:

```
cd $JETSON_NANO_KERNEL_SOURCE
TOOLCHAIN_PREFIX=$HOME/l4t-gcc/gcc-linaro-7.3.1-2018.05-x86_64_aarch64-linux-gnu/bin/aarch64-linux-gnu-
TEGRA_KERNEL_OUT=$JETSON_NANO_KERNEL_SOURCE/build
KERNEL_MODULES_OUT=$JETSON_NANO_KERNEL_SOURCE/modules
make -C kernel/kernel-4.9/ ARCH=arm64 O=$TEGRA_KERNEL_OUT LOCALVERSION=-tegra CROSS_COMPILE=${TOOLCHAIN_PREFIX} tegra_defconfig
make -C kernel/kernel-4.9/ ARCH=arm64 O=$TEGRA_KERNEL_OUT LOCALVERSION=-tegra CROSS_COMPILE=${TOOLCHAIN_PREFIX} -j8 --output-sync=target zImage
make -C kernel/kernel-4.9/ ARCH=arm64 O=$TEGRA_KERNEL_OUT LOCALVERSION=-tegra CROSS_COMPILE=${TOOLCHAIN_PREFIX} -j8 --output-sync=target modules
make -C kernel/kernel-4.9/ ARCH=arm64 O=$TEGRA_KERNEL_OUT LOCALVERSION=-tegra CROSS_COMPILE=${TOOLCHAIN_PREFIX} -j8 --output-sync=target dtbs
make -C kernel/kernel-4.9/ ARCH=arm64 O=$TEGRA_KERNEL_OUT LOCALVERSION=-tegra INSTALL_MOD_PATH=$KERNEL_MODULES_OUT modules_install
```

如果第一次編譯的時候，我們必須要用官方的 toolchain
換過核心後，假設要重編 可以直接指向  
```
 which aarch64-linux-gnu-gcc
 TOOLCHAIN_PREFIX = 剛剛的路徑
```
按下 make menuconfig 會有問題

會說要找 ncurses 的 lib

所以要安裝

在 終端機介面 鍵入

`#sudo apt-get install libncurses5-dev`

最後文章沒提到的如何換kernel
只要 切去 編譯完成的目錄
kernel/kernel.4.9
根據不同的板子和位元
以這塊板子就是arm64
```
kernel/kernel.4.9/arm64/boot/Image
cp kernel/kernel.4.9/arm64/boot/Image /boot/Image

```

非常要注意的是必須要到BUILD 後的目錄，主要讓MODULE 放到/lib/moduble by 編譯1個禮拜的 kernel 踩坑
```
$ sudo make modules_install
$ sudo cp arch/arm/boot/dts/*.dtb /boot/
```
重開即可更換核心，這次重編主要要讓板子支援bpf

```
sudo apt-get install bcc
sudo apt-get install bpfcc-tools 
```

