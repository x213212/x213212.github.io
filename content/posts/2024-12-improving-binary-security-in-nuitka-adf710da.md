---
title: "Improving Binary Security in Nuitka Compilation with OLLVM Obfuscation"
date: "2024-12-26T21:24:00.002+08:00"
updated: "2024-12-26T21:24:27.442+08:00"
permalink: "/2024/12/improving-binary-security-in-nuitka.html"
original_url: "https://x8795278.blogspot.com/2024/12/improving-binary-security-in-nuitka.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5943998040013352943"
tags: ["llvm", "Nuitka", "ollvm"]
layout: post
---

![](https://hackmd.io/_uploads/S1U7PRqBJg.png)

# 上一篇從特徵碼開始下手，這次從異動 nuitka 的 compiler 來下手

這篇網站在以前的時候就有嘗試去呼叫ollvm 去加密 binary
https://blog.threat.zone/create-more-complicated-binaries-with-nuitka-llvm-obfuscator/

那麼我們來透過 ollvm 去混淆 一些東西看能不能順便透過 Nuitka 進行編譯
目前 msys2 好像都沒看到人去編譯過，來移植一下
```
pacman -S --needed git wget mingw-w64-x86_64-gcc mingw-w64-x86_64-ninja mingw-w64-x86_64-cmake make mingw-w64-x86_64-python3
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
git config --global http.postBuffer 524288000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999
```
```
nuitka version 2.4.7 基本上編譯出來都會被一些知名防毒軟體偵測
$ gcc -v
Using built-in specs.
COLLECT_GCC=D:\res\msys64\msys64\mingw64\bin\gcc.exe
COLLECT_LTO_WRAPPER=D:/res/msys64/msys64/mingw64/bin/../lib/gcc/x86_64-w64-mingw32/13.2.0/lto-wrapper.exe
Target: x86_64-w64-mingw32
Configured with: ../gcc-13.2.0/configure --prefix=/mingw64 --with-local-prefix=/mingw64/local --build=x86_64-w64-mingw32 --host=x86_64-w64-mingw32 --target=x86_64-w6
4-mingw32 --with-native-system-header-dir=/mingw64/include --libexecdir=/mingw64/lib --enable-bootstrap --enable-checking=release --with-arch=nocona --with-tune=gene
ric --enable-languages=c,lto,c++,fortran,ada,objc,obj-c++,jit --enable-shared --enable-static --enable-libatomic --enable-threads=posix --enable-graphite --enable-fu
lly-dynamic-string --enable-libstdcxx-filesystem-ts --enable-libstdcxx-time --disable-libstdcxx-pch --enable-lto --enable-libgomp --disable-libssp --disable-multilib
 --disable-rpath --disable-win32-registry --disable-nls --disable-werror --disable-symvers --with-libiconv --with-system-zlib --with-gmp=/mingw64 --with-mpfr=/mingw6
4 --with-mpc=/mingw64 --with-isl=/mingw64 --with-pkgversion='Rev3, Built by MSYS2 project' --with-bugurl=https://github.com/msys2/MINGW-packages/issues --with-gnu-as
 --with-gnu-ld --disable-libstdcxx-debug --with-boot-ldflags=-static-libstdc++ --with-stage1-ldflags=-static-libstdc++
Thread model: posix
Supported LTO compression algorithms: zlib zstd
gcc version 13.2.0 (Rev3, Built by MSYS2 project)

```
# download llvm
```
export PATH=/mingw64/bin:$PATH
git clone -b llvmorg-17.0.6 https://github.com/llvm/llvm-project.git
cd llvm-project
mkdir build 
cd build 

cmake -G "MinGW Makefiles" \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLVM_ENABLE_RTTI=OFF \
  -DLLVM_ENABLE_EH=OFF \
  -DLLVM_INCLUDE_TESTS=OFF \
  -DLLVM_BUILD_TOOLS=OFF \
  -DLLVM_BUILD_LLVM_DYLIB=OFF \
  -DLLVM_ENABLE_ASSERTIONS=OFF \
  -DLLVM_ENABLE_PROJECTS="clang;lld" \
  -DCMAKE_C_FLAGS="-D__INTRINSIC_SETJMPEX__ /utf-8" \
  -DCMAKE_CXX_FLAGS="-D__INTRINSIC_SETJMPEX__ /utf-8" \
  ../llvm

這邊要編譯過程中可能會遇到一些權限的問題 chmod -R u+w ~/llvm-project/build
```
# ollvm
```
git clone https://github.com/DreamSoule/ollvm17
```

接下來你要把 LLVM-obfuscate 相關的 pass移動到 llvm-project
下面已經把一些編譯的bug 進行修正，一些新版的compiler 語法請chatgpt 進行修正了

注意過程中有些source code發生異動
\llvm-project\llvm\lib\Passes\Obfuscation\Utils.cpp
```c
static bool valueEscapes(const Instruction &I) {
    for (const Use &U : I.uses()) {
        const User *Usr = U.getUser();
        // 检查用户是否是指令，且是否在同一个基本块
        if (const Instruction *Inst = dyn_cast<Instruction>(Usr)) {
            if (Inst->getParent() != I.getParent())
                return true; // 逃逸到其他基本块
        } else {
            return true; // 逃逸到非指令的用户
        }
    }
    return false;
}

/** LLVM\llvm\lib\Transforms\Scalar\Reg2Mem.cpp
 * @brief 修复PHI指令和逃逸变量
 *
 * @param F
 */
void llvm::fixStack(Function &F) {
  // Insert all new allocas into entry block.
  BasicBlock *BBEntry = &F.getEntryBlock();
  assert(pred_empty(BBEntry) &&
         "Entry block to function must not have predecessors!");

  // Find first non-alloca instruction and create insertion point. This is
  // safe if block is well-formed: it always have terminator, otherwise
  // we'll get and assertion.
  BasicBlock::iterator I = BBEntry->begin();
  while (isa<AllocaInst>(I))
    ++I;

  CastInst *AllocaInsertionPoint = new BitCastInst(
      Constant::getNullValue(Type::getInt32Ty(F.getContext())),
      Type::getInt32Ty(F.getContext()), "fix_stack_point", &*I);

  // Find the escaped instructions. But don't create stack slots for
  // allocas in entry block.
  std::list<Instruction *> WorkList;
	for (Instruction &I : instructions(F)) {
    if (!(isa<AllocaInst>(I) && I.getParent() == BBEntry) && valueEscapes(I)) {
        WorkList.push_front(&I);
    }
}
  // Demote escaped instructions
  //NumRegsDemoted += WorkList.size();
  for (Instruction *I : WorkList)
    DemoteRegToStack(*I, false, AllocaInsertionPoint);

  WorkList.clear();

  // Find all phi's
  for (BasicBlock &BB : F)
    for (auto &Phi : BB.phis())
      WorkList.push_front(&Phi);

  // Demote phi nodes
  //NumPhisDemoted += WorkList.size();
  for (Instruction *I : WorkList)
    DemotePHIToStack(cast<PHINode>(I), AllocaInsertionPoint);
}
```

\llvm-project\llvm\lib\Passes\Obfuscation\IPObfuscationContext.cpp
```
        NF->getBasicBlockList().splice(NF->begin(), F->getBasicBlockList());
換成
        NF->splice(NF->begin(), F);
```

\llvm-project\llvm\lib\Support\CrashRecoveryContext.cpp
```c
#include "llvm/Support/CrashRecoveryContext.h"
#include "llvm/Config/llvm-config.h"
#include "llvm/Support/ErrorHandling.h"
#include "llvm/Support/ExitCodes.h"
#include "llvm/Support/Signals.h"
#include "llvm/Support/thread.h"
#include <cassert>
#include <mutex>
#include <setjmp.h>

using namespace llvm;
#if defined(__MINGW32__)
extern "C" int __intrinsic_setjmpex(_JBTYPE* buf, void* ctx) {
    // 提供一个空实现，直接返回 0
    return 0;
}
#endif
```
# build
```
mingw32-make -j$(nproc)
```
大概就可以順利編譯完成了，接下來要改 nuitka的 source 規避 一些compiler 額外印出來的資訊導致異常拋出錯誤

# rewrite nuitka source code

C:\nuitka_cache\SITE_PACKAGE\nuitka\build\SconsCaching.py
這邊我強迫替換成我們剛剛編譯完畢的 clang 位置，不然 Nuitka會動態去抓
```pyhton
def checkWindowsCompilerFound(
    env, target_arch, clang_mode, msvc_version, assume_yes_for_downloads
):
    """Remove compiler of wrong arch or too old gcc and replace with downloaded winlibs gcc."""
    # Many cases to deal with, pylint: disable=too-many-branches,too-many-statements

    if os.name == "nt":
        # On Windows, in case MSVC was not found and not previously forced, use the
        # winlibs MinGW64 as a download, and use it as a fallback.
        compiler_path = getExecutablePath(env["CC"], env=env)
        print(compiler_path)
       
        
        env["CC"] = f"D:\\res\\msys64\\msys64\\home\\rex603\\llvm-project\\build3\\bin\\clang.exe"
        print(env["CC"])

        #if env["CC"] is None:
        #    raiseNoCompilerFoundErrorExit()

    return env
```
![image](https://hackmd.io/_uploads/BkwRL09rJx.png)

C:\nuitka_cache\SITE_PACKAGE\nuitka\build\SconsSpawn.py,在編譯過成因為 ollvm 有會額外印出用那些pass的資訊 這些資訊會導致 nuitka 誤以為是編譯錯誤，對他而言，沒消息就是好消息
```python
      if data is not None and data.rstrip():
            my_print("Unexpected output from this command:", style="scons-unexpected")
            my_print(cmdline, style="scons-unexpected")

            if str is not bytes:
                data = decodeData(data)

            my_print(
                data, style="scons-unexpected", end="" if data.endswith("\n") else "\n"
            )
            print(data)
            # reportSconsUnexpectedOutput(env, cmdline, stdout=data, stderr=None)
#####################註解我
```
![image](https://hackmd.io/_uploads/r1rewC9SJe.png)

ok從這些scons 編譯的 script 來判斷 判斷有三個地方要進行 ollvm 混淆
![image](https://hackmd.io/_uploads/H1dyUR5r1g.png)
C:\nuitka_cache\SITE_PACKAGE\nuitka\build\Backend.scons
C:\nuitka_cache\SITE_PACKAGE\nuitka\build\CCompilerVersion.scons
C:\nuitka_cache\SITE_PACKAGE\nuitka\build\Onefile.scons
就實驗而言基本上我們只要對 onefile.scons 這個 shellcode 去混淆加密，有嘗試對 Backend source code 加密反而多更多時間，還被檢測到更多的病毒
```
env.Append(
    CCFLAGS=[
        "-mllvm", "-sobf",  # String Obfuscation
        "-mllvm", "-igv",    # Indirect Global Variable Obfuscation
        "-mllvm", "-sub",    # Substitution Obfuscation
        "-mllvm", "-bcf",
    ]
)
```
```
python -m nuitka test.py --clang --onefile --standalone
```

基本上一些知名的掃毒應該都可以略過了
https://www.virustotal.com/gui/file/e719c2124e2dadfb081ec6574a2416a556be452601f280469d78c6a96b8902c1

![image](https://hackmd.io/_uploads/S1U7PRqBJg.png)

收工!

