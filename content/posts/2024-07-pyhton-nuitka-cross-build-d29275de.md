---
title: "pyhton nuitka cross build 可行性與反編譯"
date: "2024-07-28T11:07:00.003+08:00"
updated: "2024-07-28T11:07:17.224+08:00"
permalink: "/2024/07/pyhton-nuitka-cross-build.html"
original_url: "https://x8795278.blogspot.com/2024/07/pyhton-nuitka-cross-build.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-540732309946425338"
tags: ["Nuitka", "Python"]
layout: post
---

![](https://hackmd.io/_uploads/B1zRrVmYA.png)

# pyhton nuitka cross build 可行性與反編譯
在開發產品中，遇到了要在 linux 上面 build 出 windows 版本 和 linux 版本，經過實驗來講找了蠻多資料
nuitka 其實在 windows 版本和 linux 版本 產生出來的 c code 是不一樣的，大概從幾個地方去切入，

下面打包 比較常見的 大型 lib numpy, matplotlib,pandas
```python
import os
import sys
import numpy
import matplotlib
import pandas
def main():
  
    print("NumPy version:", numpy.__version__)

    a = numpy.array([1, 2, 3])
    print(a)
    mydataset = {
      'cars': ["BMW", "Volvo", "Ford"],
      'passings': [3, 7, 2]
    }

    myvar = pandas.DataFrame(mydataset)
    print(myvar)

if __name__ == "__main__":
    main()

```

# 常見問題
https://nuitka.net/user-documentation/common-issue-solutions.html
這幾個參數嘗試過，在比較大型的程式碼規模--low-memory 可以降低記憶體使用率不然極有可能會遇到
cc1.exe: out of memory allocating 65536 bytes

```bash
python3 -m nuitka --standalone --onefile --show-memory --show-progress --nofollow-imports --low-memory --mingw64 --show-scons --output-dir=out ./test.py 
```

# 克制化 scons build command
```bash
但是要直接下 scons command 不透過Nuitka 編譯可能要繞過一些地方
File "/usr/local/lib/python3.9/site-packages/nuitka/build/SconsUtils.py", line 644:
def createDefinitionsFile(source_dir, filename, definitions):
    print(os.environ["_NUITKA_BUILD_DEFINITIONS_CATALOG"])
    #for env_name in os.environ["_NUITKA_BUILD_DEFINITIONS_CATALOG"].split(","): <== 這邊先關掉才算ok ，才可以不用加載 nuitka 可以直接透過 scons command 進行編譯
    #    definitions[env_name] = os.environ[env_name]
```
# linux
```bash
export NUITKA_PACKAGE_DIR=/usr/local/lib/python3.9/site-packages/nuitka
export _NUITKA_BUILD_DEFINITIONS_CATALOG=/usr/local/lib/python3.9/site-packages/nuitka/build/include
/usr/local/bin/python3 -W ignore /usr/local/lib/python3.9/site-packages/nuitka/build/inline_copy/bin/scons.py     -f /usr/local/lib/python3.9/site-packages/nuitka/build/Backend.scons     --jobs 12 --warn=no-deprecated --no-site-dir --debug=stacktrace     result_name=/shared_data/mingw-w64-build/output/test     source_dir=. nuitka_python=false debug_mode=false debugger_mode=false     python_debug=false module_mode=false full_compat=false experimental=     trace_mode=false file_reference_mode=original module_count=1     result_exe=/shared_data/mingw-w64-build/output/test.bin     python_sysflag_utf8=true nuitka_src=/usr/local/lib/python3.9/site-packages/nuitka/build     python_version=3.9 python_prefix=/usr/local no_deployment= show_scons=true target_arch=x86_64
```

# windows
```bash
set NUITKA_PACKAGE_DIR=C:\Users\x213212\AppData\Local\Programs\Python\Python39\Lib\site-packages\nuitka  rams\Python\Python39\python.exe -W ignore C:\Users\ x213212\AppData\Local\Programs\Python\Python39\Lib\site-packages\nuitka\build\inline_copy\bin\scons.py -f C:\Users\ x213212\AppData\Local\Programs\Python\Python39\Lib\site-packages\nuitka\build\Backend.scons --jobs 12 --warn=no-deprecated --no-site-dir --debug=stacktrace result_name=C:\Users\ x213212\AppData\Local\Programs\Python\Python39\output\test source_dir=. nuitka_python=false debug_mode=false debugger_mode=false python_debug=false module_mode=false full_compat=false experimental= trace_mode=false file_reference_mode=original module_count=1 result_exe=C:\Users\ x213212\AppData\Local\Programs\Python\Python39\output\test.exe uninstalled_python=true nuitka_src=C:\Users\ x213212\AppData\Local\Programs\Python\Python39\Lib\site-packages\nuitka\build python_version=3.9 python_prefix=C:\Users\ x213212\AppData\Local\Programs\Python\Python39 no_deployment= show_scons=true mingw_mode=true noelf_mode=true target_arch=x86_64
```

# env vaiable
```
AS=as
CC="C:/msys64/home/rex603/ddddd/AUTOTU~1/NUITKA~1/DOWNLO~1/gcc/x86_64/13.2.0-16.0.6-11.0.1-msvcrt-r1/mingw64/bin/ccache.exe" "C:/msys64/home/rex603/ddddd/AUTOTU~1/NUITKA~1/DOWNLO~1/gcc/x86_64/13.2.0-16.0.6-11.0.1-msvcrt-r1/mingw64/bin/gcc.exe"
CCACHE_DIR=C:/msys64/home/rex603/ddddd/AUTOTU~1/NUITKA~1/ccache
CCACHE_LOGFILE=C:/msys64/home/rex603/ddddd/AUTOTU~1/out/ANDES_~1.ONE/ccache-29308.txt
CCCOM=$CC -o $TARGET -c $CFLAGS $CCFLAGS $_CCCOMCOM $SOURCES
CFILESUFFIX=.c
CPPDEFINES=['_WIN32_WINNT=0x0501', '__NUITKA_NO_ASSERT__', 'MS_WIN64', '_NUITKA_ONEFILE_MODE', '_NUITKA_PLUGIN_MULTIPROCESSING_ENABLED=1']
CPPDEFPREFIX=-D
CPPDEFSUFFIX=
CPPPATH=['C:/msys64/mingw64/lib/python3.11/SITE-P~1/nuitka/build/inline_copy/zlib', '.', 'C:/msys64/mingw64/lib/python3.11/SITE-P~1/nuitka/build/include', 'C:/msys64/mingw64/lib/python3.11/SITE-P~1/nuitka/build/static_src', 'C:/msys64/mingw64/lib/python3.11/SITE-P~1/nuitka/build/inline_copy/zstd']
CPPSUFFIXES=['.c', '.C', '.cxx', '.cpp', '.c++', '.cc', '.h', '.H', '.hxx', '.hpp', '.hh', '.F', '.fpp', '.FPP', '.m', '.mm', '.S', '.spp', '.SPP', '.sx']
CXX="C:/msys64/home/rex603/ddddd/AUTOTU~1/NUITKA~1/DOWNLO~1/gcc/x86_64/13.2.0-16.0.6-11.0.1-msvcrt-r1/mingw64/bin/ccache.exe" "C:/msys64/home/rex603/ddddd/AUTOTU~1/NUITKA~1/DOWNLO~1/gcc/x86_64/13.2.0-16.0.6-11.0.1-msvcrt-r1/mingw64/bin/gcc.exe"
CXXCOM=$CXX -o $TARGET -c $CXXFLAGS $CCFLAGS $_CCCOMCOM $SOURCES
CXXFILESUFFIX=.cc
HOST_ARCH=x86_64
HOST_OS=win32
INCPREFIX=-I
INCSUFFIX=
LDMODULE=$SHLINK
LDMODULEFLAGS=$SHLINKFLAGS
LDMODULENAME=${LDMODULEPREFIX}$_get_ldmodule_stem${_LDMODULESUFFIX}
LDMODULEPREFIX=$SHLIBPREFIX
LDMODULESUFFIX=$SHLIBSUFFIX
LDMODULEVERSION=$SHLIBVERSION
LDMODULE_NOVERSION_SYMLINK=$_get_shlib_dir${LDMODULEPREFIX}$_get_ldmodule_stem${LDMODULESUFFIX}
LDMODULE_SONAME_SYMLINK=$_get_shlib_dir$_LDMODULESONAME
LIBDIRPREFIX=-L
LIBDIRSUFFIX=
LIBLINKPREFIX=-l
LIBLINKSUFFIX=
LIBPATH=[]
LIBPREFIX=lib
LIBPREFIXES=['$LIBPREFIX']
LIBS=[]
LIBSUFFIX=.a
LIBSUFFIXES=['$LIBSUFFIX']
LINK="C:/msys64/home/rex603/ddddd/AUTOTU~1/NUITKA~1/DOWNLO~1/gcc/x86_64/13.2.0-16.0.6-11.0.1-msvcrt-r1/mingw64/bin/gcc.exe"
LINKCOM=$LINK -o $TARGET $LINKFLAGS $__RPATH @"./@link_input.txt" $_LIBDIRFLAGS $_LIBFLAGS
OBJPREFIX=
OBJSUFFIX=.o
PLATFORM=win32
PROGPREFIX=
PROGSUFFIX=.exe
RC=windres
RCCOM=$RC $_CPPDEFFLAGS $RCINCFLAGS ${RCINCPREFIX} ${SOURCE.dir} $RCFLAGS -i $SOURCE -o $TARGET
RCINCFLAGS=${_concat(RCINCPREFIX, CPPPATH, RCINCSUFFIX, __env__, RDirs, TARGET, SOURCE, affect_signature=False)}
RCINCPREFIX=--include-dir 
RCINCSUFFIX=
RPATHPREFIX=-Wl,-rpath=
RPATHSUFFIX=
SHCC=$CC
SHCCCOM=$SHCC -o $TARGET -c $SHCFLAGS $SHCCFLAGS $_CCCOMCOM $SOURCES
SHCXX=$CXX
SHCXXCOM=$SHCXX -o $TARGET -c $SHCXXFLAGS $SHCCFLAGS $_CCCOMCOM $SOURCES
SHELL=C:\Windows/System32\cmd.exe
SHLIBNAME=${_get_shlib_dir}${SHLIBPREFIX}$_get_shlib_stem${_SHLIBSUFFIX}
SHLIBPREFIX=
SHLIBSONAMEFLAGS=-Wl,-soname=$_SHLIBSONAME
SHLIBSUFFIX=.dll
SHLIB_NOVERSION_SYMLINK=${_get_shlib_dir}${SHLIBPREFIX}$_get_shlib_stem${SHLIBSUFFIX}
SHLIB_SONAME_SYMLINK=${_get_shlib_dir}$_SHLIBSONAME
SHLINK=$LINK
SHOBJPREFIX=$OBJPREFIX
SHOBJSUFFIX=.o
TARGET_ARCH=x86_64
TEMPFILEARGJOIN= 
TEMPFILEPREFIX=@
TOOLS=['mingw', 'gcc', 'g++', 'gnulink']
WINDOWSDEFPREFIX=
WINDOWSDEFSUFFIX=.def
gcc_mode=True
clang_mode=False
msvc_mode=False
mingw_mode=True
clangcl_mode=False
PATH=C:/msys64/home/rex603/ddddd/AUTOTU~1/NUITKA~1/DOWNLO~1/gcc/x86_64/13.2.0-16.0.6-11.0.1-msvcrt-r1/mingw64\bin;C:\msys64\mingw64\bin;C:\msys64\usr\local\bin;C:\msys64\usr\bin;C:\msys64\usr\bin;C:\Windows\System32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0\;C:\msys64\usr\bin\site_perl;C:\msys64\usr\bin\vendor_perl;C:\msys64\usr\bin\core_perl
TARGET=C:/msys64/home/rex603/ddddd/AUTOTU~1/out/andes_autotuning.exe
```

看到這邊就可以實現從中間干擾 build command ,就是假設今天要修改 cross compiler mingw 版本
```
export CC="WWWW"
```
然後在目錄下的
\out\{test}.onefile-build\ 再重下剛剛的scons build ,就可以override compiler cfags
,也就是其實可以在這邊cflags 再去插入一些混淆的lib 比如說換成ollvm
https://heroims.github.io/2019/01/06/OLLVM%E4%BB%A3%E7%A0%81%E6%B7%B7%E6%B7%86%E7%A7%BB%E6%A4%8D%E4%B8%8E%E4%BD%BF%E7%94%A8/

昨天看到這種方式的混用也是相當不錯哈哈
https://youtu.be/L2PK7hrCxjA

或者在跨平台的時候引入https://github.com/jart/cosmopolitan
也可以讓你的c/c++ 編譯一次 放到任何平台上

