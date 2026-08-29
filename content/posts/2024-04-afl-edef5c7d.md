---
title: "大致分析afl++"
date: "2024-04-05T13:44:00.003+08:00"
updated: "2024-04-05T13:44:56.749+08:00"
permalink: "/2024/04/afl.html"
original_url: "https://x8795278.blogspot.com/2024/04/afl.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2457544655873021810"
tags: ["afl++"]
layout: post
---

![](https://hackmd.io/_uploads/r1wJrV21R.png)

# 大致分析afl++
![image](https://hackmd.io/_uploads/r1wJrV21R.png)
研究一下 afl++ 內部工作原理
# Install
我的環境是docker並且在windows wsl2
https://github.com/AFLplusplus/AFLplusplus/blob/stable/docs/INSTALL.md
```bash
docker pull aflplusplus/aflplusplus:latest
docker run -ti -v [localfolder]:/src aflplusplus/aflplusplus
```
# Build afl++
```bash
cp -R /AFLplusplus/ /src
```
假設你在 wsl2 你要在docker maping 出來的資料夾透過vscode 修改source code 那你必須要在外面對著 container copy出來的 AFLplusplus資料夾在設定權限一次
```bash
# in wsl folder
chmod 777 /AFLplusplus
```
這樣就可以透過vscode 去修改source code 因為某寫檔案已經build 過所以可以很快的build 完整的source code
```bash
make
make install
```
# Example
## Source Tree
開始建立 example 首先先建立個testfolder
```bash
./testfolder
```
裡面大概要這些資料夾,fuzz_in裡面還要再產生一個testcase
```bash
-rwxr-xr-x  1 root root 19248 Apr  4 15:11 fuzzTest
-rwxrwxrwx  1 root root   186 Apr  4 14:02 fuzzTest.c
drwxrwxrwx  2 root root  4096 Apr  4 14:02 fuzz_in
```
## Script
```bash
touch fuzzTest.c
echo "1234567892&^$%^$#$@" > fuzz_in/testcase
mkdir fuzz_in
```
## Testcase
fuzzTest.c
```c
#include <stdio.h>  // 引入標準I/O庫
int main(int argc, char *argv[])
{
    char buf[100] = {0};  // 定義字符陣列
    gets(buf);   // 讀取輸入，存在栈溢出風險
    printf(buf); // 輸出字符串，存在格式化字符串風險
    return 0;
}
```
## Build
```bash
afl-gcc -g -o ./fuzzTest fuzzTest.c
```
## Fuzzy
```bash
afl-fuzz -i fuzz_in -o fuzz_out ./fuzzTest
```
## Run
![image](https://hackmd.io/_uploads/ByOLl-6yC.png)

# compiler instrumentation
在看afl++架構的時候，發先從編譯的時候他會對程式碼進行插樁，也就是埋code,這樣再配合afl-fuzz在runtime的時候可以控制binary 生命流程來達到探索路徑，那最簡單的就是
觀看afl-gcc 做了那些事情
```bash
afl-gcc -g -o ./fuzzTest fuzzTest.c
```
## afl-as.c
```bash
/home/x213212/afl/AFLplusplus/src/afl-as.c
```
在這個source code 可以找到 afl-gcc compiler entry point main function
```c
/* Main entry point */
int main(int argc, char **argv) {

  s32 pid;
  u32 rand_seed, i, j;
  int status;
  u8 *inst_ratio_str = getenv("AFL_INST_RATIO");

  struct timeval  tv;
  struct timezone tz;

  clang_mode = !!getenv(CLANG_ENV_VAR);

  if ((isatty(2) && !getenv("AFL_QUIET")) || getenv("AFL_DEBUG") != NULL) {

    SAYF(cCYA "afl-as" VERSION cRST " by Michal Zalewski\n");

  } else {

    be_quiet = 1;

  }

  if (argc < 2 || (argc == 2 && strcmp(argv[1], "-h") == 0)) {

    fprintf(
        stdout,
        "afl-as" VERSION
        " by Michal Zalewski\n"
        "\n%s [-h]\n\n"
        "This is a helper application for afl-fuzz. It is a wrapper around GNU "
        "'as',\n"
        "executed by the toolchain whenever using afl-gcc or afl-clang. You "
        "probably\n"
        "don't want to run this program directly.\n\n"

        "Rarely, when dealing with extremely complex projects, it may be "
        "advisable\n"
        "to set AFL_INST_RATIO to a value less than 100 in order to reduce "
        "the\n"
        "odds of instrumenting every discovered branch.\n\n"
        "Environment variables used:\n"
        "AFL_AS: path to assembler to use for instrumented files\n"
        "AFL_CC: fall back path to assembler\n"
        "AFL_CXX: fall back path to assembler\n"
        "TMPDIR: directory to use for temporary files\n"
        "TEMP: fall back path to directory for temporary files\n"
        "TMP: fall back path to directory for temporary files\n"
        "AFL_INST_RATIO: user specified instrumentation ratio\n"
        "AFL_QUIET: suppress verbose output\n"
        "AFL_KEEP_ASSEMBLY: leave instrumented assembly files\n"
        "AFL_AS_FORCE_INSTRUMENT: force instrumentation for asm sources\n"
        "AFL_HARDEN, AFL_USE_ASAN, AFL_USE_MSAN, AFL_USE_UBSAN, AFL_USE_LSAN:\n"
        "  used in the instrumentation summary message\n",
        argv[0]);

    exit(1);

  }

  gettimeofday(&tv, &tz);

  rand_seed = tv.tv_sec ^ tv.tv_usec ^ getpid();
  // in fast systems where pids can repeat in the same seconds we need this
  for (i = 1; (s32)i < argc; i++)
    for (j = 0; j < strlen(argv[i]); j++)
      rand_seed += argv[i][j];

  srandom(rand_seed);

  edit_params(argc, argv);

  if (inst_ratio_str) {

    if (sscanf(inst_ratio_str, "%u", &inst_ratio) != 1 || inst_ratio > 100) {

      FATAL("Bad value of AFL_INST_RATIO (must be between 0 and 100)");

    }

  }

  if (getenv(AS_LOOP_ENV_VAR)) {

    FATAL("Endless loop when calling 'as' (remove '.' from your PATH)");

  }

  setenv(AS_LOOP_ENV_VAR, "1", 1);

  /* When compiling with ASAN, we don't have a particularly elegant way to skip
     ASAN-specific branches. But we can probabilistically compensate for
     that... */

  if (getenv("AFL_USE_ASAN") || getenv("AFL_USE_MSAN")) {

    sanitizer = 1;
    if (!getenv("AFL_INST_RATIO")) { inst_ratio /= 3; }

  }

  if (!just_version) { add_instrumentation(); }

  if (!(pid = fork())) {

    execvp(as_params[0], (char **)as_params);
    FATAL("Oops, failed to execute '%s' - check your PATH", as_params[0]);

  }

  if (pid < 0) { PFATAL("fork() failed"); }

  if (waitpid(pid, &status, 0) <= 0) { PFATAL("waitpid() failed"); }

  if (!getenv("AFL_KEEP_ASSEMBLY")) { unlink(modified_file); }

  exit(WEXITSTATUS(status));

}
```
afl-as 首先會先執行 function edit_params() 來調整參數，而後會執行 function add_instrumentation() 做插樁，最後執行 as 做組譯
## add_instrumentation
```c

/* Process input file, generate modified_file. Insert instrumentation in all
   the appropriate places. */

static void add_instrumentation(void) {

  static u8 line[MAX_LINE];

  FILE *inf;
  FILE *outf;
  s32   outfd;
  u32   ins_lines = 0;

  u8 instr_ok = 0, skip_csect = 0, skip_next_label = 0, skip_intel = 0,
     skip_app = 0, instrument_next = 0;

#ifdef __APPLE__

  u8 *colon_pos;

#endif                                                         /* __APPLE__ */

  if (input_file) {

    inf = fopen(input_file, "r");
    if (!inf) { PFATAL("Unable to read '%s'", input_file); }

  } else {

    inf = stdin;

  }

  outfd = open(modified_file, O_WRONLY | O_EXCL | O_CREAT, DEFAULT_PERMISSION);

  if (outfd < 0) { PFATAL("Unable to write to '%s'", modified_file); }

  outf = fdopen(outfd, "w");

  if (!outf) { PFATAL("fdopen() failed"); }

  while (fgets(line, MAX_LINE, inf)) {

    /* In some cases, we want to defer writing the instrumentation trampoline
       until after all the labels, macros, comments, etc. If we're in this
       mode, and if the line starts with a tab followed by a character, dump
       the trampoline now. */

    if (!pass_thru && !skip_intel && !skip_app && !skip_csect && instr_ok &&
        instrument_next && line[0] == '\t' && isalpha(line[1])) {

      fprintf(outf, use_64bit ? trampoline_fmt_64 : trampoline_fmt_32,
              R(MAP_SIZE));

      instrument_next = 0;
      ins_lines++;

    }

    /* Output the actual line, call it a day in pass-thru mode. */

    fputs(line, outf);

    if (pass_thru) { continue; }

    /* All right, this is where the actual fun begins. For one, we only want to
       instrument the .text section. So, let's keep track of that in processed
       files - and let's set instr_ok accordingly. */

    if (line[0] == '\t' && line[1] == '.') {

      /* OpenBSD puts jump tables directly inline with the code, which is
         a bit annoying. They use a specific format of p2align directives
         around them, so we use that as a signal. */

      if (!clang_mode && instr_ok && !strncmp(line + 2, "p2align ", 8) &&
          isdigit(line[10]) && line[11] == '\n') {

        skip_next_label = 1;

      }

      if (!strncmp(line + 2, "text\n", 5) ||
          !strncmp(line + 2, "section\t.text", 13) ||
          !strncmp(line + 2, "section\t__TEXT,__text", 21) ||
          !strncmp(line + 2, "section __TEXT,__text", 21)) {

        instr_ok = 1;
        continue;

      }

      if (!strncmp(line + 2, "section\t", 8) ||
          !strncmp(line + 2, "section ", 8) || !strncmp(line + 2, "bss\n", 4) ||
          !strncmp(line + 2, "data\n", 5)) {

        instr_ok = 0;
        continue;

      }

    }

    /* Detect off-flavor assembly (rare, happens in gdb). When this is
       encountered, we set skip_csect until the opposite directive is
       seen, and we do not instrument. */

    if (strstr(line, ".code")) {

      if (strstr(line, ".code32")) { skip_csect = use_64bit; }
      if (strstr(line, ".code64")) { skip_csect = !use_64bit; }

    }

    /* Detect syntax changes, as could happen with hand-written assembly.
       Skip Intel blocks, resume instrumentation when back to AT&T. */

    if (strstr(line, ".intel_syntax")) { skip_intel = 1; }
    if (strstr(line, ".att_syntax")) { skip_intel = 0; }

    /* Detect and skip ad-hoc __asm__ blocks, likewise skipping them. */

    if (line[0] == '#' || line[1] == '#') {

      if (strstr(line, "#APP")) { skip_app = 1; }
      if (strstr(line, "#NO_APP")) { skip_app = 0; }

    }

    /* If we're in the right mood for instrumenting, check for function
       names or conditional labels. This is a bit messy, but in essence,
       we want to catch:

         ^main:      - function entry point (always instrumented)
         ^.L0:       - GCC branch label
         ^.LBB0_0:   - clang branch label (but only in clang mode)
         ^\tjnz foo  - conditional branches

       ...but not:

         ^# BB#0:    - clang comments
         ^ # BB#0:   - ditto
         ^.Ltmp0:    - clang non-branch labels
         ^.LC0       - GCC non-branch labels
         ^.LBB0_0:   - ditto (when in GCC mode)
         ^\tjmp foo  - non-conditional jumps

       Additionally, clang and GCC on MacOS X follow a different convention
       with no leading dots on labels, hence the weird maze of #ifdefs
       later on.

     */

    if (skip_intel || skip_app || skip_csect || !instr_ok || line[0] == '#' ||
        line[0] == ' ') {

      continue;

    }

    /* Conditional branch instruction (jnz, etc). We append the instrumentation
       right after the branch (to instrument the not-taken path) and at the
       branch destination label (handled later on). */

    if (line[0] == '\t') {

      if (line[1] == 'j' && line[2] != 'm' && R(100) < (long)inst_ratio) {

        fprintf(outf, use_64bit ? trampoline_fmt_64 : trampoline_fmt_32,
                R(MAP_SIZE));

        ins_lines++;

      }

      continue;

    }

    /* Label of some sort. This may be a branch destination, but we need to
       read carefully and account for several different formatting
       conventions. */

#ifdef __APPLE__

    /* Apple: L<whatever><digit>: */

    if ((colon_pos = strstr(line, ":"))) {

      if (line[0] == 'L' && isdigit(*(colon_pos - 1))) {

#else

    /* Everybody else: .L<whatever>: */

    if (strstr(line, ":")) {

      if (line[0] == '.') {

#endif                                                         /* __APPLE__ */

        /* .L0: or LBB0_0: style jump destination */

#ifdef __APPLE__

        /* Apple: L<num> / LBB<num> */

        if ((isdigit(line[1]) || (clang_mode && !strncmp(line, "LBB", 3))) &&
            R(100) < (long)inst_ratio) {

#else

        /* Apple: .L<num> / .LBB<num> */

        if ((isdigit(line[2]) ||
             (clang_mode && !strncmp(line + 1, "LBB", 3))) &&
            R(100) < (long)inst_ratio) {

#endif                                                         /* __APPLE__ */

          /* An optimization is possible here by adding the code only if the
             label is mentioned in the code in contexts other than call / jmp.
             That said, this complicates the code by requiring two-pass
             processing (messy with stdin), and results in a speed gain
             typically under 10%, because compilers are generally pretty good
             about not generating spurious intra-function jumps.

             We use deferred output chiefly to avoid disrupting
             .Lfunc_begin0-style exception handling calculations (a problem on
             MacOS X). */

          if (!skip_next_label) {

            instrument_next = 1;

          } else {

            skip_next_label = 0;

          }

        }

      } else {

        /* Function label (always instrumented, deferred mode). */

        instrument_next = 1;

      }

    }

  }

  if (ins_lines) { fputs(use_64bit ? main_payload_64 : main_payload_32, outf); }

  if (input_file) { fclose(inf); }
  fclose(outf);

  if (!be_quiet) {

    if (!ins_lines) {

      WARNF("No instrumentation targets found%s.",
            pass_thru ? " (pass-thru mode)" : "");

    } else {

      char modeline[100];
      snprintf(modeline, sizeof(modeline), "%s%s%s%s%s%s",
               getenv("AFL_HARDEN") ? "hardened" : "non-hardened",
               getenv("AFL_USE_ASAN") ? ", ASAN" : "",
               getenv("AFL_USE_MSAN") ? ", MSAN" : "",
               getenv("AFL_USE_TSAN") ? ", TSAN" : "",
               getenv("AFL_USE_UBSAN") ? ", UBSAN" : "",
               getenv("AFL_USE_LSAN") ? ", LSAN" : "");

      OKF("Instrumented %u locations (%s-bit, %s mode, ratio %u%%).", ins_lines,
          use_64bit ? "64" : "32", modeline, inst_ratio);

    }

  }

}
```
那這些插樁的asm 到底寫在哪個資料夾
可以在afl-as.h 看的到
```bash
/home/x213212/afl/AFLplusplus/include/afl-as.h
```
![image](https://hackmd.io/_uploads/rybHVb6yA.png)
像在這篇文章就有提到跳轉規則
https://zhuanlan.zhihu.com/p/583178410

* 插樁的模式:
    1. ^main - 函數入口點
    2. ^\..L0 - GCC跳轉標籤
    3. ^\..LBB0_0 - clang跳轉標籤
    4. ^\tjnz foo - 條件跳轉標籤
* 不希望捕獲的模式:
    1. ^# BB#0 - clang注釋
    2. ^ # BB#0 - clang注釋
    3. ^\..Ltmp0 - clang非分支標籤
    4. ^\..LC0 - GCC非分支標籤
    5. ^\..LBB0_0 - GCC非分支標籤（這條與想要捕獲的clang跳轉標籤相同，需確定context以做區分）
    6. ^\tjmp foo - 非條件跳轉

https://www.secpulse.com/archives/166956.html
在這邊文章也有敘述到 在路徑中 他會寫入到bitmap來記錄探索的路徑資料寫到shard memory
也就是後續要大概說一下fork_server運作原理
# fork_server
透過剛剛插樁，其實就是在控制程式的生命流程
https://ch4r1l3.github.io/2019/03/08/AFL%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%903%E2%80%94%E2%80%94afl-as-h%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/
這篇文章有對插入的asm進行詳細解釋了我們直接看
![image](https://hackmd.io/_uploads/Hkvhwb61C.png)
![image](https://hackmd.io/_uploads/BkihP-pkA.png)

```c
#include <stdio.h>
int main(void){

    //instrumentation A, 函数入口
    int a;
    scanf("%d", &a);

    if(a==0xdeadbeef)
        //instrumentation B, jnz 不執行
        *((char *)0)=1;

    //instrumentation C, jnz 執行
    return 0;
}
```
也就是說fork_server 透過 fork 先停在main function ,由於我們又用compiler 進行插樁，所以在遇到新的路徑的時候都會記錄在shard memory 來避免重複探索路徑，那透過這樣的方式 假設fork 出來的 child process 發生 timeout 或者 crash ,子父程序都可以藉由pipe 去傳遞彼此之間的狀態，透過這樣的方式不用每次從頭開始執行，假設發生crash 也只是fork 出來的child process ,fuzzer 隨時可以從上一個中斷點開始運行
# fuzzy
後續就是透過演算法不斷的探索新路徑，然後紀錄發生crash 再去看在修復程式碼，分析較為淺不過大致流程應該是這樣
https://bbs.kanxue.com/thread-254705.htm
# ref
https://tttang.com/user/f1tao
https://ch4r1l3.github.io/2019/03/05/AFL%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%901%E2%80%94%E2%80%94afl-gcc-c%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/
https://ch4r1l3.github.io/2019/03/06/AFL%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%902%E2%80%94%E2%80%94afl-as-c%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/
https://ch4r1l3.github.io/2019/03/08/AFL%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%903%E2%80%94%E2%80%94afl-as-h%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/
https://ch4r1l3.github.io/2019/03/09/AFL%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%904%E2%80%94%E2%80%94afl-fuzz-c%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%901/
https://ch4r1l3.github.io/2019/03/10/AFL%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%905%E2%80%94%E2%80%94afl-fuzz-c%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%902/
https://ithelp.ithome.com.tw/users/20151153/ironman/5164?page=1
https://ithelp.ithome.com.tw/articles/10288409

