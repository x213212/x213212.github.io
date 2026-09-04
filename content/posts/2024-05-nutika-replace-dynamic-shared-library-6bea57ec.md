---
title: "nutika replace dynamic shared library path"
date: "2024-05-11T14:17:00.002+08:00"
updated: "2024-05-11T14:17:49.577+08:00"
permalink: "/2024/05/nutika-replace-dynamic-shared-library.html"
original_url: "https://x8795278.blogspot.com/2024/05/nutika-replace-dynamic-shared-library.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-7146092314772709812"
tags: ["Nuitka"]
layout: post
---

![](https://hackmd.io/_uploads/SkTu6KnzR.png)

# Nuitka 替換shardlib 路徑
看了幾篇文章只有找到這個
https://www.fournoas.com/posts/nuitka-inject-custom-c-code-at-compile-time/
像這篇文章有透過暫停的方式去介入 nuitka 編譯過程，但是這方法是改不動我們要做的事情，不過也大概知道 nuitka 的過程是什麼
然後嘗試用ld preload方式去替換shardlib ,但發現在編譯完的binary 的 shardlib 引用太少了，大部分還是透過 dlopen 去載入 shardlib，那麼在實際要變成一個產品的話又有需要要嘗試改動 nuitka 載入 dynamic shared library 的路徑怎麼辦呢，來研究一下
先假設你要編譯的source code為
# source code
## test.py
```python
import matplotlib
import mymodule

myclass = mymodule.MyClass1()
mymodule.function2()
import math
print(math.nan == math.nan)
print(float('nan') == float('nan'))
print(math.isnan(math.nan))
print(math.isnan(float('nan')))
```
## nuitka command
```
nuitka --standalone --onefile --show-memory --show-progress --static-libpython=yes --nofollow-imports --output-dir=out --mingw64 ./test.py
```
nuitka編譯後目錄下會產生out/test.build , out/test.dist
可以發現 out/test.dist 透過ldd 裡面跟編譯後的目錄下那麼多.so 對應不起來
```
 ldd testcase
        linux-vdso.so.1 (0x00007ffdf4de7000)
        libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007fbf6c226000)
        libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007fbf6c0d7000)
        libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007fbf6c0b4000)
        libutil.so.1 => /lib/x86_64-linux-gnu/libutil.so.1 (0x00007fbf6c0af000)
        librt.so.1 => /lib/x86_64-linux-gnu/librt.so.1 (0x00007fbf6c0a5000)
        libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fbf6beb3000)
        /lib64/ld-linux-x86-64.so.2 (0x00007fbf6c23f000)
```
那大概可以得知就是他們載入 shard lib 是透過動態載入 dlopen
這邊先處理編譯時期的shardlib
那麼已經知道都是會有一個起始點 scons 去編譯，找到了Backend.scons
```
 /usr/local/lib/python3.9/site-packages/nuitka/build/Backend.scons
```

```
# Set load libpython from binary directory default
if env.gcc_mode and not isMacOS() and not os.name == "nt" and not module_mode:
    if env.standalone_mode:
        rpath = "$$ORIGIN"
    else:
        rpath = python_lib_path
    local_lib_path = os.path.join(os.getcwd(), 'lib')
    print(local_lib_path)
 
    env.Append(LINKFLAGS=["-Wl,-R,'%s'" % rpath, "-Wl,-L'%s'" % local_lib_path])

    # The rpath is no longer used unless we do this on modern Linux. The
    # option name is not very revealing, but basically without this, the
    # rpath in the binary will be ignored by the loader.
    if "linux" in sys.platform:
        env.Append(LINKFLAGS=["-Wl,--disable-new-dtags","-Wl,-R,'%s'" % rpath, "-Wl,-L'%s'" % local_lib_path])

```
這邊僅限於一些需要編譯時期已經加入的shard lib，
然後解決完編譯時期的shard lib 在找看看從動態的呼叫 dlopen 載入 shard lib 的程式碼在哪。
那麼去到source code
 grep -r "dlopen" /usr/local/lib/python3.9/site-packages/nuitka

搜尋看看
```
[root@328103204ad4 out]# grep -r "dlopen" /usr/local/lib/python3.9/site-packages/nuitka
/usr/local/lib/python3.9/site-packages/nuitka/build/static_src/MetaPathBasedLoader.c:    // spell-checker: ignore getdlopenflags,dlopenflags
/usr/local/lib/python3.9/site-packages/nuitka/build/static_src/MetaPathBasedLoader.c:    static PyObject *dlopenflags_object = NULL;
/usr/local/lib/python3.9/site-packages/nuitka/build/static_src/MetaPathBasedLoader.c:    if (dlopenflags_object == NULL) {
/usr/local/lib/python3.9/site-packages/nuitka/build/static_src/MetaPathBasedLoader.c:        dlopenflags_object = CALL_FUNCTION_NO_ARGS(tstate, Nuitka_SysGetObject("getdlopenflags"));
/usr/local/lib/python3.9/site-packages/nuitka/build/static_src/MetaPathBasedLoader.c:    int dlopenflags = PyInt_AsLong(dlopenflags_object);
/usr/local/lib/python3.9/site-packages/nuitka/build/static_src/MetaPathBasedLoader.c:        PySys_WriteStderr("import %s # dlopen(\"%s\", %x);\n", full_name, filename, dlopenflags);
/usr/local/lib/python3.9/site-packages/nuitka/build/static_src/MetaPathBasedLoader.c:    void *handle = dlopen(filename, dlopenflags);
/usr/local/lib/python3.9/site-packages/nuitka/build/static_src/MetaPathBasedLoader.c:            error = "unknown dlopen() error";
```

```
vim  /usr/local/lib/python3.9/site-packages/nuitka/build/static_src/MetaPathBasedLoader.c
```
定位到這邊可以看到說，估計也是透過
  void *handle = dlopen(filename, dlopenflags);
  載入 .so 那麼就往上追
```
      // This code would work for all versions, we are avoiding access to interpreter
    // structure internals of 3.8 or higher.
    // spell-checker: ignore getdlopenflags,dlopenflags

    static PyObject *dlopenflags_object = NULL;
    if (dlopenflags_object == NULL) {
        dlopenflags_object = CALL_FUNCTION_NO_ARGS(tstate, Nuitka_SysGetObject("getdlopenflags"));
    }
    int dlopenflags = PyInt_AsLong(dlopenflags_object);

    if (isVerbose()) {
        PySys_WriteStderr("import %s # dlopen(\"%s\", %x);\n", full_name, filename, dlopenflags);
    }

    void *handle = dlopen(filename, dlopenflags);
```

往上追後 callIntoExtensionModule 這支function 是負責載入單一shardlib 的c function
```
#ifdef _WIN32
static PyObject *callIntoExtensionModule(PyThreadState *tstate, char const *full_name, const wchar_t *filename) {
#else
static PyObject *callIntoExtensionModule(PyThreadState *tstate, char const *full_name, const char *filename) {
#endif
```
透過一陣printf 大法 找到 filename 為我們要載入的lib 位置
```
// Pointers to bytecode data.
static char **_bytecode_data = NULL;

static PyObject *loadModule(PyThreadState *tstate, PyObject *module, PyObject *module_name,
                            struct Nuitka_MetaPathBasedLoaderEntry const *entry) {
#ifdef _NUITKA_STANDALONE
    if ((entry->flags & NUITKA_EXTENSION_MODULE_FLAG) != 0) {
        // Append the the entry name from full path module name with dots,
        // and translate these into directory separators.
#ifdef _WIN32
        wchar_t filename[MAXPATHLEN + 1] = {0};

        appendWStringSafeW(filename, getBinaryDirectoryWideChars(true), sizeof(filename) / sizeof(wchar_t));
        appendCharSafeW(filename, SEP, sizeof(filename) / sizeof(wchar_t));
        appendModuleNameAsPathW(filename, entry->name, sizeof(filename) / sizeof(wchar_t));
        appendStringSafeW(filename, ".pyd", sizeof(filename) / sizeof(wchar_t));
#else
        char filename[MAXPATHLEN + 1] = {0};

        appendStringSafe(filename, getBinaryDirectoryHostEncoded(true), sizeof(filename));
        appendCharSafe(filename, SEP, sizeof(filename));
        appendModuleNameAsPath(filename, entry->name, sizeof(filename));
        appendStringSafe(filename, ".so", sizeof(filename));
    printf("%s",filename);
#endif

        // Set "__spec__" and "__file__", some modules expect it early.
        setModuleFileValue(tstate, module, filename);
#if PYTHON_VERSION >= 0x350
        PyObject *spec_value =
            createModuleSpec(tstate, module_name, LOOKUP_ATTRIBUTE(tstate, module, const_str_plain___file__), false);

        SET_ATTRIBUTE(tstate, module, const_str_plain___spec__, spec_value);
#endif

        callIntoExtensionModule(tstate, entry->name, filename);
    } else
#endif
        if ((entry->flags & NUITKA_BYTECODE_FLAG) != 0) {
        // TODO: Do node use marshal, but our own stuff, once we
        // can do code objects too.

        PyCodeObject *code_object =
            (PyCodeObject *)PyMarshal_ReadObjectFromString(_bytecode_data[entry->bytecode_index], entry->bytecode_size);

        // TODO: Probably a bit harsh reaction.
        if (unlikely(code_object == NULL)) {
            PyErr_Print();
            abort();
        }

        return loadModuleFromCodeObject(module, code_object, entry->name, (entry->flags & NUITKA_PACKAGE_FLAG) != 0);
    } else {
        assert((entry->flags & NUITKA_EXTENSION_MODULE_FLAG) == 0);
        assert(entry->python_initfunc);

        {
            NUITKA_MAY_BE_UNUSED bool res = Nuitka_SetModule(module_name, module);
            assert(res != false);
        }

        // Run the compiled module code, we get the module returned.
#if PYTHON_VERSION < 0x300
        NUITKA_MAY_BE_UNUSED
#endif
        PyObject *result = entry->python_initfunc(tstate, module, entry);
        CHECK_OBJECT_X(result);

#if PYTHON_VERSION >= 0x300
        if (likely(result != NULL)) {
            _fixupSpecAttribute(tstate, result);
        }
#endif
    }

    if (unlikely(HAS_ERROR_OCCURRED(tstate))) {
        return NULL;
    }

    if (isVerbose()) {
        PySys_WriteStderr("Loaded %s\n", entry->name);
    }

    return Nuitka_GetModule(tstate, module_name);
}
```

所以我們是在這邊組合 .so 的路徑
```
#else
        char filename[MAXPATHLEN + 1] = {0};

        appendStringSafe(filename, getBinaryDirectoryHostEncoded(true), sizeof(filename));
        appendCharSafe(filename, SEP, sizeof(filename));
        appendModuleNameAsPath(filename, entry->name, sizeof(filename));
        appendStringSafe(filename, ".so", sizeof(filename));
    printf("%s",filename);
#endif
```

來加料一下

```
#ifdef _WIN32
        wchar_t filename[MAXPATHLEN + 1] = {0};

        appendWStringSafeW(filename, getBinaryDirectoryWideChars(true), sizeof(filename) / sizeof(wchar_t));
        appendCharSafeW(filename, SEP, sizeof(filename) / sizeof(wchar_t));
        appendModuleNameAsPathW(filename, entry->name, sizeof(filename) / sizeof(wchar_t));
        appendStringSafeW(filename, ".pyd", sizeof(filename) / sizeof(wchar_t));
#else
        char filename[MAXPATHLEN + 1] = {0};

        appendStringSafe(filename, getBinaryDirectoryHostEncoded(true), sizeof(filename));
if (strlen(filename) + strlen("lib") < sizeof(filename)) {
        strcat( filename, "/lib");
    } else {
        printf("Not enough space in 'filename' to append 'lib'\n");
    }
        appendCharSafe(filename, SEP, sizeof(filename));
        appendModuleNameAsPath(filename, entry->name, sizeof(filename));

        appendStringSafe(filename, ".so", sizeof(filename));

#endif
        printf("%s\n",filename);
```
那麼預設 我們編譯出來的test.bin
Nuitka build command
```
nuitka --standalone --onefile --show-memory --show-progress --static-libpython=yes --nofollow-imports --output-dir=out --mingw64 ./test.py
```
我們查看out 目錄下的 test.dist 裡面應該有一個test.bin
```
test.dist
```
先看一下目錄結構
```
 out/test.dist/
_codecs_cn.so  _codecs_iso2022.so  _codecs_kr.so  _datetime.so        _pickle.so  _sha512.so  binascii.so  test.bin        zlib.so
_codecs_hk.so  _codecs_jp.so       _codecs_tw.so  _multibytecodec.so  _random.so  _struct.so  math.so      unicodedata.so
```
直接執行

 out/test.dist/test.bin

```
qweeeeeeeeeeeeeeeeeeeee/shared_data/out/test.dist/test.bin
qweeeeeeeeeeeeeeeeeeeee/shared_data/out/test.dist/test.bin
inspect
ast
contextlib
_collections_abc
collections
heapq
keyword
operator
reprlib
functools
enum
dis
opcode
collections.abc
importlib.machinery
linecache
os
stat
posixpath
genericpath
tokenize
re
sre_compile
sre_parse
sre_constants
copyreg
token
__main__
math
/shared_data/Tuning_automation/out/test.dist/lib/math.so
/shared_data/Tuning_automation/out/test.dist/lib/math.so
Traceback (most recent call last):
  File "/shared_data/Tuning_automation/out/test.dist/test.py", line 1, in <module>
ImportError: /shared_data/Tuning_automation/out/test.dist/lib/math.so: cannot open shared object file: No such file or directory
```

```
/shared_data/Tuning_automation/out/test.dist/lib/math.so: cannot open shared object file: No such file or directory
```
這邊可以發現路徑已經多一層lib 也算替換成功
那麼接下來就是 將dist 裡面的.so 往裡面移動一層到lib

```
[root@328103204ad4 test.dist]# ls -all
total 6488
drwxr-xr-x 3 root root    4096 May 11 06:13 .
drwxr-xr-x 9 root root    4096 May 11 05:49 ..
drwxr-xr-x 2 root root    4096 May 11 06:13 lib
-rwxr-xr-x 1 root root 6630352 May 11 05:48 test.bin
```
到這邊就算改完了，目錄下就蠻乾淨的
![image](https://hackmd.io/_uploads/SkTu6KnzR.png)

額外加碼，假設在 python 需要載入 package 的 module 的話你的目錄結構會變這樣

```
PIL   test.bin  contourpy  kiwisolver  lib  markupsafe  matplotlib  numpy  pandas  pytz
```

# source code
## test.py
```python
import sys
import pytz
from datetime import datetime

# Create a time zone-aware datetime object in UTC
utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
 
# Convert to a specific time zone (e.g., New York)
local_timezone = pytz.timezone('America/New_York')
local_time = utc_now.astimezone(local_timezone)
 
print(f'UTC Time: {utc_now}')
print(f'Local Time (New York): {local_time}')

```
## nuitka command
```
nuitka --standalone --onefile --show-memory --show-progress --static-libpython=yes --nofollow-imports --output-dir=out --mingw64 ./test.py
```

以我們的情況來說，剛剛我們動的是最後 link time 和 c code，所以只有動到 動態和靜態的 shardlib 的路徑，所以，一些有關於 nuitka 架構，比如說 python 轉成 c++後，他是怎麼 import 對應到 c++ dlopen載入 lib 這情況我不清楚，這會導致架構上的東西是沒辦法動的，也就是載入so 確實都移動到 lib裡面了，但是最外層還是要保留一些package的folder 目錄結構，裡面是 nuitka 原本的架構設計，所以可能要維持他 python package 的目錄結構，但是裡面的.so都可以刪除.
所以lib 裡面 和 根目錄都有 python package name的資料夾，差別在 ./lib 裡面的是有 .so 的
# root list
ex.matplotlib裡面只有一些package預設的module 設定檔案
```
PIL test.bin  contourpy  kiwisolver  lib  markupsafe  matplotlib  numpy  pandas  pytz
```
# lib list
ex.matplotlib裡面有 .so
```
PIL contourpy  kiwisolver markupsafe  matplotlib  numpy  pandas  pytz
```
# total list
實際開發環境的 tree ,可以看到 matplotlib目錄下的差別
```
tree -L 3
.
├── PIL
├── test.bin
├── contourpy
├── kiwisolver
├── lib
│   ├── PIL
│   │   ├── _imaging.so
│   │   ├── _imagingcms.so
│   │   ├── _imagingmath.so
│   │   └── _webp.so
│   ├── _asyncio.so
│   ├── _blake2.so
│   ├── _bz2.so
│   ├── _codecs_cn.so
│   ├── _codecs_hk.so
│   ├── _codecs_iso2022.so
│   ├── _codecs_jp.so
│   ├── _codecs_kr.so
│   ├── _codecs_tw.so
│   ├── _contextvars.so
│   ├── _csv.so
│   ├── _ctypes.so
│   ├── _datetime.so
│   ├── _decimal.so
│   ├── _elementtree.so
│   ├── _hashlib.so
│   ├── _heapq.so
│   ├── _md5.so
│   ├── _multibytecodec.so
│   ├── _multiprocessing.so
│   ├── _opcode.so
│   ├── _pickle.so
│   ├── _posixshmem.so
│   ├── _posixsubprocess.so
│   ├── _queue.so
│   ├── _random.so
│   ├── _sha1.so
│   ├── _sha256.so
│   ├── _sha3.so
│   ├── _sha512.so
│   ├── _socket.so
│   ├── _ssl.so
│   ├── _statistics.so
│   ├── _struct.so
│   ├── array.so
│   ├── binascii.so
│   ├── contourpy
│   │   └── _contourpy.so
│   ├── grp.so
│   ├── kiwisolver
│   │   ├── _cext.cpython-39-x86_64-linux-gnu.so
│   │   └── _cext.so
│   ├── libXau-00ec42fe.so.6.0.0
│   ├── libbz2.so.1
│   ├── libcrypto.so.1.1
│   ├── libffi.so.6
│   ├── libgfortran-040039e1.so.5.0.0
│   ├── libjpeg-cec335f2.so.62.4.0
│   ├── liblcms2-8d000061.so.2.0.16
│   ├── liblzma-d1e41b3a.so.5.4.5
│   ├── libopenblas64_p-r0-0cf96a72.3.23.dev.so
│   ├── libopenjp2-98a646ca.so.2.5.0
│   ├── libquadmath-96973f99.so.0.0.0
│   ├── libsharpyuv-652b6057.so.0.0.1
│   ├── libssl.so.1.1
│   ├── libtiff-f683b479.so.6.0.2
│   ├── libwebp-8a0843dd.so.7.1.8
│   ├── libwebpdemux-f9b98349.so.2.0.14
│   ├── libwebpmux-b067bc14.so.3.0.13
│   ├── libxcb-ac5351d8.so.1.1.0
│   ├── markupsafe
│   │   └── _speedups.so
│   ├── math.so
│   ├── matplotlib
│   │   ├── _c_internal_utils.so
│   │   ├── _image.so
│   │   ├── _path.so
│   │   ├── _qhull.so
│   │   ├── _tri.so
│   │   ├── backends
│   │   ├── ft2font.so
│   │   └── mpl-data
│   ├── mmap.so
│   ├── numpy
│   │   ├── core
│   │   ├── fft
│   │   ├── linalg
│   │   └── random
│   ├── pandas
│   │   ├── _libs
│   │   └── io
│   ├── pyexpat.so
│   ├── pytz
│   │   └── zoneinfo
│   ├── select.so
│   ├── termios.so
│   ├── unicodedata.so
│   └── zlib.so
├── markupsafe
├── matplotlib
│   ├── backends
│   └── mpl-data
│       ├── fonts
│       ├── images
│       ├── kpsewhich.lua
│       ├── matplotlibrc
│       ├── plot_directive
│       └── stylelib
├── numpy
│   ├── core
│   ├── fft
│   ├── linalg
│   └── random
├── pandas
│   ├── _libs
│   │   ├── tslibs
│   │   └── window
│   └── io
│       └── formats
└── pytz
    └── zoneinfo
        ├── Africa
        ├── America
        ├── Antarctica
        ├── Arctic
        ├── Asia
        ├── Atlantic
        ├── Australia
        ├── Brazil
        ├── CET
        ├── CST6CDT
        ├── Canada
        ├── Chile
        ├── Cuba
        ├── EET
        ├── EST
        ├── EST5EDT
        ├── Egypt
        ├── Eire
        ├── Etc
        ├── Europe
        ├── Factory
        ├── GB
        ├── GB-Eire
        ├── GMT
        ├── GMT+0
        ├── GMT-0
        ├── GMT0
        ├── Greenwich
        ├── HST
        ├── Hongkong
        ├── Iceland
        ├── Indian
        ├── Iran
        ├── Israel
        ├── Jamaica
        ├── Japan
        ├── Kwajalein
        ├── Libya
        ├── MET
        ├── MST
        ├── MST7MDT
        ├── Mexico
        ├── NZ
        ├── NZ-CHAT
        ├── Navajo
        ├── PRC
        ├── PST8PDT
        ├── Pacific
        ├── Poland
        ├── Portugal
        ├── ROC
        ├── ROK
        ├── Singapore
        ├── Turkey
        ├── UCT
        ├── US
        ├── UTC
        ├── Universal
        ├── W-SU
        ├── WET
        ├── Zulu
        ├── iso3166.tab
        ├── leapseconds
        ├── tzdata.zi
        ├── zone.tab
        ├── zone1970.tab
        └── zonenow.tab
```
最外層目錄最終就變成比較不會那麼亂了
```
tree -L 1
.
├── PIL
├── pytz
├── contourpy
├── kiwisolver
├── lib
├── markupsafe
├── matplotlib
├── numpy
├── pandas
└── test.bin
```

# nuitka add option "--onefile"
這邊有找到官方的option
result=subprocess.run([f"{args.pp}", "-m", "nuitka", "--standalone","--onefile", "--show-memory","--show-progress","--static-libpython=yes", "--nofollow-imports", "--output-dir=out","--mingw64","./custom.py"])
假設加上 onfile的情況下，nuitka可以先將依些shard lib 打包到成一個binary runtime 在解壓縮 temp資料夾
Example python code
```
import sys
import os

current_directory = os.path.dirname(os.path.abspath(__file__))

lib_directory = os.path.join(current_directory, 'lib')

sys.path = [lib_directory]

print("sys.path:", sys.path)

try:
    import pytz
    print("Custom pytz module loaded from:", pytz.__file__)
except ImportError as e:
    print("Failed to import pytz:", e)

from datetime import datetime

# Create a time zone-aware datetime object in UTC
utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
 
# Convert to a specific time zone (e.g., New York)
local_timezone = pytz.timezone('America/New_York')
local_time = utc_now.astimezone(local_timezone)
 
print(f'UTC Time: {utc_now}')
print(f'Local Time (New York): {local_time}')
```

在linux
```
sys.path: ['/tmp/onefile_61131_1715670463_304893']
Custom pytz module loaded from: /tmp/onefile_61131_1715670463_304893/pytz/__init__.py
UTC Time: 2024-05-14 07:07:43.516114+00:00
Local Time (New York): 2024-05-14 03:07:43.516114-04:00
```
和
```
sys.path: ['C:\\Users\\rex603\\AppData\\Local\\Temp\\ONEFIL~1']
Custom pytz module loaded from: C:\Users\rex603\AppData\Local\Temp\ONEFIL~1\lib\pytz\__init__.py
UTC Time: 2024-05-14 06:29:22.284119+00:00
Local Time (New York): 2024-05-14 02:29:22.284119-04:00
```

這跟根據ONEFIL 去搜一下source code 這樣可以看到
/usr/local/lib/python3.9/site-packages/nuitka/Options.py
C:\Users\rex603\AppData\Local\Programs\Python\Python39\Lib\site-packages\nuitka\Options.py
可以改動他解壓縮的路徑
```
def getOnefileTempDirSpec():
    """*str* = ``--onefile-tempdir-spec``"""
    result = (
        options.onefile_tempdir_spec or "{TEMP}" + os.path.sep + "onefile_{PID}_{TIME}"
    )
    result = "./lib"
    # This changes the '/' to '\' on Windows at least.
    return os.path.normpath(result)
```
```
[root@5a1c68e4daa2 lib]# ls
_blake2.so          _codecs_jp.so    _ctypes.so    _md5.so              _random.so  _socket.so      custom_genetic_algorithm.bin  libssl.so.1.1   zlib.so
_bz2.so             _codecs_kr.so    _datetime.so  _multibytecodec.so   _sha1.so    _statistics.so  grp.so                        math.so
_codecs_cn.so       _codecs_tw.so    _decimal.so   _opcode.so           _sha256.so  _struct.so      libbz2.so.1                   pytz
_codecs_hk.so       _contextvars.so  _hashlib.so   _pickle.so           _sha3.so    array.so        libcrypto.so.1.1              select.so
_codecs_iso2022.so  _csv.so          _heapq.so     _posixsubprocess.so  _sha512.so  binascii.so     libffi.so.6                   unicodedata.so
```
```
[root@5a1c68e4daa2 dist]# ls
test  lib
```
這樣打包後的binaty 就可以解壓縮到使用者根目錄lib這樣，要指定其他目錄也可以。

