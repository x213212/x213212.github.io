---
title: "QEMU 在 RISC-V 上跑 Ubuntu"
date: "2025-08-24T00:19:00.001+08:00"
updated: "2025-08-24T00:19:04.497+08:00"
permalink: "/2025/08/qemu-risc-v-ubuntu.html"
original_url: "https://x8795278.blogspot.com/2025/08/qemu-risc-v-ubuntu.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3216414747894794611"
tags: ["qemu"]
layout: post
---

![](https://hackmd.io/_uploads/SktJqDvKle.png)

# QEMU 在 RISC-V 上跑 Ubuntu

本筆記整合完整步驟與實驗心得，全部放在同一份，方便直接複製執行。涵蓋 QEMU + Ubuntu 啟動、QEMU / OpenSBI / U-Boot 最後正確編譯版本、網路/SSH、共享、NFS/CIFS/SSHFS、CoreMark 編譯、常見錯誤對應。
![image](https://hackmd.io/_uploads/SktJqDvKle.png)

---

安裝必要套件：

```bash
sudo apt update
sudo apt install -y build-essential git wget xz-utils qemu-utils gcc-riscv64-linux-gnu \
    libglib2.0-dev libfdt-dev libpixman-1-dev zlib1g-dev ninja-build meson \
    nfs-common cifs-utils sshfs flex bison pkg-config
```

---

### QEMU（正確編譯版本，支援 slirp 網路）

```bash
git clone https://gitlab.com/qemu-project/qemu.git ~/qemu-src
cd ~/qemu-src
git checkout v8.2.0   # 最後實測可用版本
./configure --target-list=riscv64-softmmu --enable-slirp --disable-werror
make -j$(nproc)
```

輸出檔案： `~/qemu-src/build/qemu-system-riscv64`

---

### OpenSBI（正確版本）

```bash
git clone https://github.com/riscv/opensbi.git ~/opensbi-src
cd ~/opensbi-src
git checkout v1.5
make CROSS_COMPILE=riscv64-linux-gnu- PLATFORM=generic -j$(nproc)
```

輸出檔案：

* `build/platform/generic/firmware/fw_jump.elf`
* `build/platform/generic/firmware/fw_dynamic.bin`

---

### U-Boot（正確版本）

```bash
git clone https://source.denx.de/u-boot/u-boot.git ~/u-boot
cd ~/u-boot
git checkout v2023.07
make distclean
make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- qemu-riscv64_smode_defconfig
make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- -j$(nproc)
```

輸出檔案：

* `~/u-boot/u-boot`
* `~/u-boot/u-boot.elf`

---

### 下載 Ubuntu riscv64 映像

```bash
wget https://cdimage.ubuntu.com/releases/24.04.3/release/ubuntu-24.04.3-preinstalled-server-riscv64.img.xz
xz -dk ubuntu-24.04.3-preinstalled-server-riscv64.img.xz
```

---

### 啟動 QEMU virt 平台

```bash
~/qemu-src/build/qemu-system-riscv64 \
  -machine virt -m 2G -smp 4 -nographic \
  -bios   ~/opensbi-src/build/platform/generic/firmware/fw_jump.elf \
  -kernel ~/u-boot/u-boot \
  -nic user,hostfwd=tcp::2222-:22 \
  -device virtio-rng-pci \
  -drive  file=ubuntu-24.04.3-preinstalled-server-riscv64.img,format=raw,if=virtio \
  -append "console=ttyS0"
```

登入方式：

```bash
ssh -p 2222 ubuntu@127.0.0.1   # 預設帳密 ubuntu/ubuntu
```

---

### WSL 轉發（如需從 Windows 連進去）

```powershell
wsl hostname -I   # 取得 WSL IP
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=2222 connectaddress=<WSL_IP> connectport=2222
New-NetFirewallRule -DisplayName "QEMU-WSL-SSH-2222" -Direction Inbound -LocalPort 2222 -Protocol TCP -Action Allow
```

---

### Host ↔ Guest 共享目錄 (9p virtfs)

啟動 QEMU 時加：

```bash
-virtfs local,path=/home/you/share,mount_tag=hostshare,security_model=passthrough,id=hostshare
```

Guest 掛載：

```bash
sudo mkdir -p /mnt/share
sudo mount -t 9p -o trans=virtio hostshare /mnt/share
```

---

### 區域網共享

NFS：

```bash
sudo mount -t nfs 192.168.1.100:/srv/nfs/share /mnt
```

CIFS：

```bash
sudo mount -t cifs //192.168.1.101/share /mnt/smb -o username=USER,password=PASS
```

SSHFS：

```bash
sshfs user@192.168.1.102:/remote/path /mnt/ssh
```

---

### 傳檔：scp / sftp / rsync

```bash
scp -P 2222 file ubuntu@127.0.0.1:/home/ubuntu/
sftp -P 2222 ubuntu@127.0.0.1
rsync -avz -e "ssh -p 2222" ubuntu@127.0.0.1:/remote ./local
```

---

### CoreMark 編譯

```bash
export CROSS_COMPILE=/path/to/toolchain/riscv64-linux-
make compile CC="${CROSS_COMPILE}gcc" \
    XCFLAGS="-march=rv64gc -mabi=lp64d -mcmodel=medany"
```

---

### 常見錯誤

* `Invalid read/write @0x0`：映像與 machine 不符，請確認用 `virt` 搭配通用 img。
* `SD card size has to be power of 2`：用 `qemu-img resize img 4G`。
* `network backend 'user' is not compiled`：需重編 QEMU 加 `--enable-slirp`。
* `Image 'itb' missing external blobs (fw_dynamic.bin)`：請先編譯 OpenSBI 並設 `OPENSBI=/path/to/fw_dynamic.bin`。

---

✅ 最後正確組合版本：

* QEMU v8.2.0 + `--enable-slirp`
* OpenSBI v1.5 (generic, fw\_jump.elf)
* U-Boot v2023.07 (qemu-riscv64\_smode\_defconfig)
* Ubuntu 24.04.3 preinstalled server riscv64 image

