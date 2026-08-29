---
title: "build Huawei WiFi Iot"
date: "2024-01-27T22:00:00.001+08:00"
updated: "2024-01-27T22:00:16.900+08:00"
permalink: "/2024/01/build-huawei-wifi-iot.html"
original_url: "https://x8795278.blogspot.com/2024/01/build-huawei-wifi-iot.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3707763369535994566"
tags: ["porting"]
layout: post
---

![](https://hackmd.io/_uploads/H1ynoFz5a.png)

################################
#  Hi3861 Huawei WiFi Iot SDK  #
################################
Note (20220706):

1. Porting from code-1.0.tar.gz in https://repo.huaweicloud.com/harmonyos/os/1.0/code-1.0.tar.gz
2. You could also find the binary from wifiiot-1.0.tar.gz in https://repo.huaweicloud.com/harmonyos/os/1.0/
3. This repo has only ported the C source files including header files and excluding pre-built libraries and object files as source.txt
4. Copy the C related header files by using fast_cp.sh, which can automatic build and copy the missing headers

# python build.py wifiiot

```
No option 'riscv32-unknown-elf-gcc_path' in section: 'ndk'
usage:
  python build.py ipcamera_hi3516dv300
  python build.py ipcamera_hi3518ev300
  python build.py wifiiot

positional arguments:
  product               Name of the product

optional arguments:
  -h, --help            show this help message and exit
  -b BUILD_TYPE, --build_type BUILD_TYPE
                        release or debug version.
  -t [TEST [TEST ...]], --test [TEST [TEST ...]]
                        Compile test suit
  -n, --ndk             Compile ndk

```
# Installation Dependencies
```
sudo apt-get install -y ninja-build
```
# build gn
```
git clone https://github.com/timniederhausen/gn.git
cd gn
python build/gen.py # --allow-warning if you want to build with warnings.
ninja -C out
```
# Linker Script
```
vim ./vendor/hisi/hi3861/hi3861/build/build_tmp/scripts/link.lds
```
# Entry point:
riscv32-unknown-elf-readelf   -h  Hi3861_wifiiot_app.out
ELF Header:
  Magic:   7f 45 4c 46 01 01 01 00 00 00 00 00 00 00 00 00
  Class:                             ELF32
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              EXEC (Executable file)
  Machine:                           RISC-V
  Version:                           0x1
  Entry point address:               0x40d3c0
  Start of program headers:          52 (bytes into file)
  Start of section headers:          1528420 (bytes into file)
  Flags:                             0x1, RVC, soft-float ABI
  Size of this header:               52 (bytes)
  Size of program headers:           32 (bytes)
  Number of program headers:         11
  Size of section headers:           40 (bytes)
  Number of section headers:         27
  Section header string table index: 26

# check lwip default on :
./kernel/liteos_a/
 ![image](https://hackmd.io/_uploads/BJGFsYfca.png)

Build :
python build.py wifiiot

quick-start :
./docs/quick-start/搭建环境-0.md
./docs/quick-start/搭建环境-2.md
./docs/quick-start/搭建环境.md

# To run tests:
./out/wifiiot
![image](https://hackmd.io/_uploads/Hkjf3tM5p.png)

riscv32-unknown-elf-size  Hi3861_wifiiot_app.out
   text    data     bss     dec     hex filename
958736    4780   56100 1019616   f8ee0 Hi3861_wifiiot_app.out
![image](https://hackmd.io/_uploads/H1ynoFz5a.png)
./build/lite/toolchain/gcc.gni
Example

Default:
        tool("cc") {
            command = "$cc {{defines}} {{include_dirs}} {{cflags}} {{cflags_c}} -c {{source}} -o {{output}}"
            depsformat = "gcc"
            description = "cross compiler {{output}}"
            outputs = [
                "{{source_out_dir}}/{{source_name_part}}.o",
            ]
        }

Rewrite:
       tool("cc") {
            command = "$cc {{defines}} {{include_dirs}} {{cflags}} {{cflags_c}} -c {{source}} -o {{output}}"
            depsformat = "gcc"
            description = "'$command',"
            outputs = [
                "{{source_out_dir}}/{{source_name_part}}.o",
            ]
        }

Try using Andes toolchain:
![image](https://hackmd.io/_uploads/ryz6oFz5p.png)
Default:
riscv32-unknown-elf-gcc -D_XOPEN_SOURCE=700 -DLOS_COMPILE_LDM -DPRODUCT_USR_SOFT_VER_STR="None" -DCYGPKG_POSIX_SIGNALS -D__ECOS__ -D__RTOS_ -DPRODUCT_CFG_HAVE_FEATURE_SYS_ERR_INFO -D__LITEOS__ -DLIB_CONFIGURABLE -DLOSCFG_SHELL -DLOSCFG_CACHE_STATICS -DCUSTOM_AT_COMMAND -DLOS_CONFIG_IPERF3 -DCMSIS_OS_VER=2 -DSECUREC_ENABLE_SCANF_FILE=0 -DCONFIG_AT_COMMAND -DPRODUCT_CFG_CHIP_VER_STR="Hi3861V100" -DCHIP_VER_Hi3861 -DPRODUCT_CFG_SOFT_VER_STR="Hi3861" -DHI_BOARD_ASIC -DHI_ON_FLASH -DLITEOS_WIFI_IOT_VERSION -D__LITEOS_RISCV__ -I../../utils/native/lite/include -I../../base/iot_hardware/interfaces/kits/wifiiot_lite -I../../base/iot_hardware/hals/wifiiot_lite -I../../vendor/hisi/hi3861/hi3861/include -I../../vendor/hisi/hi3861/hi3861/platform/include -I../../vendor/hisi/hi3861/hi3861/platform/system/include -I../../vendor/hisi/hi3861/hi3861/config -I../../vendor/hisi/hi3861/hi3861/config/nv -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/kernel/base/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/targets/hi3861v100/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/kernel/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/arch/risc-v/rv32im -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/lib/libm/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/lib/libsec/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/net/wpa_supplicant-2.7/src/common -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/targets/hi3861v100/plat/riscv -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/kernel/extended/runstop -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/posix/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/linux/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/net/lwip_sack/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/lib/libc/musl/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/lib/libc/musl/arch/generic -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/lib/libc/musl/arch/riscv32 -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/lib/libc/hw/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/lib/libc/nuttx/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/targets/hi3861v100/config -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/targets/hi3861v100/user -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/targets/hi3861v100/plat -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/targets/hi3861v100/extend/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/arch -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/lib/libc/bionic/libm -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/shell/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/net/telnet/include -nostdlib -fno-common -fno-builtin -fno-strict-aliasing -fsigned-char -Werror -falign-functions=2 -msave-restore -fno-optimize-strlen -freorder-blocks-algorithm=simple -fno-schedule-insns -fno-inline-small-functions -fno-inline-functions-called-once -mtune=size -mno-small-data-limit=0 -fno-aggressive-loop-optimizations -std=c99 -Wpointer-arith -Wstrict-prototypes -fstack-protector-all -Os -ffunction-sections -fdata-sections -fno-exceptions -fno-short-enums -Wextra -Wall -Wundef -U PRODUCT_CFG_BUILD_TIME -mabi=ilp32 -march=rv32imc -fPIE -std=c99 -c ../../base/iot_hardware/frameworks/wifiiot_lite/src/wifiiot_adc.c -o ./wifiiot_adc.o
![image](https://hackmd.io/_uploads/HkwpjKf5a.png)

Rewrite:
riscv32-unknown-elf-gcc -D_XOPEN_SOURCE=700 -DLOS_COMPILE_LDM -DPRODUCT_USR_SOFT_VER_STR="None" -DCYGPKG_POSIX_SIGNALS -D__ECOS__ -D__RTOS_ -DPRODUCT_CFG_HAVE_FEATURE_SYS_ERR_INFO -D__LITEOS__ -DLIB_CONFIGURABLE -DLOSCFG_SHELL -DLOSCFG_CACHE_STATICS -DCUSTOM_AT_COMMAND -DLOS_CONFIG_IPERF3 -DCMSIS_OS_VER=2 -DSECUREC_ENABLE_SCANF_FILE=0 -DCONFIG_AT_COMMAND -DPRODUCT_CFG_CHIP_VER_STR="Hi3861V100" -DCHIP_VER_Hi3861 -DPRODUCT_CFG_SOFT_VER_STR="Hi3861" -DHI_BOARD_ASIC -DHI_ON_FLASH -DLITEOS_WIFI_IOT_VERSION -D__LITEOS_RISCV__ -I../../utils/native/lite/include -I../../base/iot_hardware/interfaces/kits/wifiiot_lite -I../../base/iot_hardware/hals/wifiiot_lite -I../../vendor/hisi/hi3861/hi3861/include -I../../vendor/hisi/hi3861/hi3861/platform/include -I../../vendor/hisi/hi3861/hi3861/platform/system/include -I../../vendor/hisi/hi3861/hi3861/config -I../../vendor/hisi/hi3861/hi3861/config/nv -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/kernel/base/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/targets/hi3861v100/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/kernel/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/arch/risc-v/rv32im -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/lib/libm/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/lib/libsec/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/net/wpa_supplicant-2.7/src/common -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/targets/hi3861v100/plat/riscv -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/kernel/extended/runstop -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/posix/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/linux/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/net/lwip_sack/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/lib/libc/musl/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/lib/libc/musl/arch/generic -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/lib/libc/musl/arch/riscv32 -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/lib/libc/hw/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/lib/libc/nuttx/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/targets/hi3861v100/config -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/targets/hi3861v100/user -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/targets/hi3861v100/plat -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/targets/hi3861v100/extend/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/arch -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/components/lib/libc/bionic/libm -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/shell/include -I../../vendor/hisi/hi3861/hi3861/platform/os/Huawei_LiteOS/net/telnet/include -nostdlib -fno-common -fno-builtin -fno-strict-aliasing -fsigned-char -Werror -falign-functions=2 -msave-restore -fno-optimize-strlen -freorder-blocks-algorithm=simple -fno-schedule-insns -fno-inline-small-functions -fno-inline-functions-called-once -mtune=size -mno-small-data-limit=0 -fno-aggressive-loop-optimizations -std=c99 -Wpointer-arith -Wstrict-prototypes -fstack-protector-all -Os -ffunction-sections -fdata-sections -fno-exceptions -fno-short-enums -Wextra -Wall -Wundef -U PRODUCT_CFG_BUILD_TIME -mabi=ilp32 -march=rv32imc -fPIE -std=c99 -c ../../base/iot_hardware/frameworks/wifiiot_lite/src/wifiiot_adc.c -o ./wifiiot_adc.o

