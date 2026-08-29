---
title: "Trying to get variable dependencies with libclang"
date: "2023-09-10T23:34:00.004+08:00"
updated: "2023-09-10T23:35:24.336+08:00"
permalink: "/2023/09/trying-to-get-variable-dependencies.html"
original_url: "https://x8795278.blogspot.com/2023/09/trying-to-get-variable-dependencies.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2440260228223850017"
tags: ["libclang"]
layout: post
---

![](https://hackmd.io/_uploads/B1t4zvjAn.png)

# Trying to get variable dependencies with libclang
![](https://hackmd.io/_uploads/B1t4zvjAn.png)

如何用 libclang 的前端解析所有的.c .cpp 展開ast tree,目前進度只有 callee 和caller 的關係，還有參數 ,function variable 的資訊
假設你有安裝llvm 應該會在
```bash
find /usr/lib/x86_64-linux-gnu -name libclang*
/usr/lib/x86_64-linux-gnu/libclang-10.so.1
/usr/lib/x86_64-linux-gnu/libclang-11.so.1
/usr/lib/x86_64-linux-gnu/libclang-cpp.so.10
/usr/lib/x86_64-linux-gnu/libclang-cpp.so.11
ln -s libclang.so.1 libclang.so
/usr/lib/x86_64-linux-gnu/libclang-10.so.1
/usr/lib/x86_64-linux-gnu/libclang-11.so.1
/usr/lib/x86_64-linux-gnu/libclang-cpp.so.10
/usr/lib/x86_64-linux-gnu/libclang-cpp.so.11
/usr/lib/x86_64-linux-gnu/libclang.so <=== 請產生這個檔案 ,到這邊libclang 應該就可以用了
```

透過 clang 前端本來想要找出 variable 之間的依賴關係，嘗試了蠻多種方式，後來發現有cindex.CompilationDatabase.fromDirectory
這邊也有用 compiledb 將 makefile 裡面的database 給libclang看建立有ast依賴關係的tree 不過還是不太行 ,不過可以得到該專案裡面的所有.c .cpp 建立call graph ,加上一些資訊應該可以更好的看出variable引用關係.
照理說應該在compiler處理應該比較正確哈哈
/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/compile_commands.json

```python
# Import necessary libraries
import clang.cindex as cindex
import json
import os

# Initialize libclang
function_name = ""
index = cindex.Index.create()

# Specify the path to the compile_commands.json file
compile_commands_file = '/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/compile_commands.json'

# Read the compile_commands.json file
with open(compile_commands_file, 'r') as f:
    compile_commands_data = json.load(f)

# Create a set to store all .c and .cpp files
source_files = set()

# Iterate through each compilation command
for command_data in compile_commands_data:
    # Get the source file path from the compilation command
    source_file = command_data['file']

    # Check if the file extension is .c or .cpp
    if source_file.endswith('.c') or source_file.endswith('.cpp'):
        source_files.add("/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/" + source_file)

# Create a dictionary to store function call relationships
function_calls = {}

# Iterate through the paths of all .c and .cpp files
for source_file in source_files:
    print(f"Analyzing {source_file}...")
    compile_commands = cindex.CompilationDatabase.fromDirectory('/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/')

    # Get the compilation commands
    commands = compile_commands.getCompileCommands(source_file)

    # Create a list to store compilation options
    file_args = []
    for command in commands:
        for argument in command.arguments:
            if str(argument).find("-I") >= 0:
                file_args.append(argument)

    # Parse the source code file
    translationUnit = index.parse(
        source_file,
        args=file_args,
        options=cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
    )

    if not translationUnit:
        print(f"Failed to parse translation unit for {source_file}")
    else:
        # Get the root node of the abstract syntax tree (AST)
        rootCursor = translationUnit.cursor

        # Recursive function for traversing every node in the AST
        def visit(cursor, depth=0):
            global function_name
            if cursor.kind == cindex.CursorKind.FUNCTION_DECL:
                # When a function declaration is found
                function_name = cursor.displayname
                if function_name not in function_calls:
                    function_calls[function_name] = set()

            # Print other functions called by this function
            for child in cursor.get_children():
                if child.kind == cindex.CursorKind.CALL_EXPR:
                    callee = child.referenced
                    if callee:
                        callee_name = callee.displayname
                        function_calls[function_name].add(callee_name)

            for child in cursor.get_children():
                visit(child, depth + 1)

        # Call the traversal function
        visit(rootCursor)

function_calls_record = []

# Function to print function calls
def print_function_calls(caller, depth=1):
    if caller in function_calls_record:
        return
    else:
        function_calls_record.append(caller)
    for callee in function_calls[caller]:
        if callee in function_calls_record:
            return
        else:
            function_calls_record.append(callee)

        indent = "  " * depth
        print(f"{indent}Function Declaration: {caller}")
        print(f"{indent}  Callee: {callee}")
        print_function_calls(callee, depth + 1)

total_call_record = []

# Function to print function call stacks
def print_function_calls(caller, depth=0):
    global function_calls_record
    if caller in function_calls_record:
        return
    else:
        function_calls_record.append(caller)
    indent = "  " * depth
    print(f"{indent}Caller: {caller}")
    if caller in function_calls:
        for callee in function_calls[caller]:
            if callee in function_calls_record:
                return
            else:
                function_calls_record.append(callee)

            indent = "  " * (depth+1)

            print(f"{indent}Callee: {callee}")
            if callee in function_calls:
                for x in function_calls[callee]:
                    print_function_calls(x, depth + 2)

# Traverse all functions and record function call stacks
function_calls_record = []
for caller in function_calls:
    function_calls_record = []
    print_function_calls(caller)
    total_call_record.append(function_calls_record)

# possible_callers = []  # Use a list to store possible callers

# Function to find possible callers of a target function
# def find_possible_callers(target_function):
#     global possible_callers
#     for call_record in total_call_record:
#         if target_function in call_record:
#             if target_function not in possible_callers:
#                 possible_callers.append(target_function)
#             for x in call_record[call_record.index(target_function):]:
#                 if x != target_function and x not in possible_callers:
#                     possible_callers.append(x)
#                     find_possible_callers(x)
#     return possible_callers

# # Example: Find possible callers of the "matrix_test" function
# target_function = 'matrix_test(ee_u32, MATRES *, MATDAT *, MATDAT *, MATDAT)'
# possible_callers = find_possible_callers(target_function)

# if possible_callers:
#     print(f"Possible callers of {target_function}:")
#     for caller in possible_callers:
#         print(f"  {caller}")
# else:
#     print(f"No possible callers found for {target_function}")

```
```outpu
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/platform/utils.c...
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/platform/stubs/isatty.c...
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/platform/stubs/fstat.c...
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/platform/stubs/read.c...
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/platform/stubs/write.c...
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/platform/reset.c...
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/platform/stubs/close.c...
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/platform/stubs/_exit.c...
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/platform/stubs/write_hex.c...
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/platform/uart.c...
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/platform/platform.c...
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_list_join.c...
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/platform/stubs/lseek.c...
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/platform/stubs/sbrk.c...
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_util.c...
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_state.c...
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_matrix.c...
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_portme.c...
Analyzing /home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_main.c...
Caller: remove(const char *)
Caller: rename(const char *, const char *)
Caller: renameat(int, const char *, int, const char *)
Caller: tmpfile()
Caller: tmpnam(char *)
Caller: tmpnam_r(char *)
Caller: tempnam(const char *, const char *)
Caller: fclose(FILE *)
Caller: fflush(FILE *)
Caller: fflush_unlocked(FILE *)
Caller: fopen(const char *restrict, const char *restrict)
Caller: freopen(const char *restrict, const char *restrict, FILE *restrict)
Caller: fdopen(int, const char *)
Caller: fmemopen(void *, int, const char *)
Caller: open_memstream(char **, int *)
Caller: setbuf(FILE *restrict, char *restrict)
Caller: setvbuf(FILE *restrict, char *restrict, int, int)
Caller: setbuffer(FILE *restrict, char *restrict, int)
Caller: setlinebuf(FILE *)
Caller: fprintf(FILE *restrict, const char *restrict, ...)
Caller: printf(const char *restrict, ...)
Caller: sprintf(char *restrict, const char *restrict, ...)
Caller: vfprintf(FILE *restrict, const char *restrict, int)
Caller: vprintf(const char *restrict, int)
Caller: vsprintf(char *restrict, const char *restrict, int)
Caller: snprintf(char *restrict, int, const char *restrict, ...)
Caller: vsnprintf(char *restrict, int, const char *restrict, int)
Caller: vdprintf(int, const char *restrict, int)
Caller: dprintf(int, const char *restrict, ...)
Caller: fscanf(FILE *restrict, const char *restrict, ...)
Caller: scanf(const char *restrict, ...)
Caller: sscanf(const char *restrict, const char *restrict, ...)
Caller: vfscanf(FILE *restrict, const char *restrict, int)
Caller: vscanf(const char *restrict, int)
Caller: vsscanf(const char *restrict, const char *restrict, int)
Caller: fgetc(FILE *)
Caller: getc(FILE *)
Caller: getchar()
Caller: getc_unlocked(FILE *)
Caller: getchar_unlocked()
Caller: fgetc_unlocked(FILE *)
Caller: fputc(int, FILE *)
Caller: putc(int, FILE *)
Caller: putchar(int)
Caller: fputc_unlocked(int, FILE *)
Caller: putc_unlocked(int, FILE *)
Caller: putchar_unlocked(int)
Caller: getw(FILE *)
Caller: putw(int, FILE *)
Caller: fgets(char *restrict, int, FILE *restrict)
Caller: __getdelim(char **restrict, int *restrict, int, FILE *restrict)
Caller: getdelim(char **restrict, int *restrict, int, FILE *restrict)
Caller: getline(char **restrict, int *restrict, FILE *restrict)
Caller: fputs(const char *restrict, FILE *restrict)
Caller: puts(const char *)
Caller: ungetc(int, FILE *)
Caller: fread(void *restrict, int, int, FILE *restrict)
Caller: fwrite(const void *restrict, int, int, FILE *restrict)
Caller: fread_unlocked(void *restrict, int, int, FILE *restrict)
Caller: fwrite_unlocked(const void *restrict, int, int, FILE *restrict)
Caller: fseek(FILE *, long, int)
Caller: ftell(FILE *)
Caller: rewind(FILE *)
Caller: fseeko(FILE *, __off_t, int)
Caller: ftello(FILE *)
Caller: fgetpos(FILE *restrict, fpos_t *restrict)
Caller: fsetpos(FILE *, const fpos_t *)
Caller: clearerr(FILE *)
Caller: feof(FILE *)
Caller: ferror(FILE *)
Caller: clearerr_unlocked(FILE *)
Caller: feof_unlocked(FILE *)
Caller: ferror_unlocked(FILE *)
Caller: perror(const char *)
Caller: fileno(FILE *)
Caller: fileno_unlocked(FILE *)
Caller: popen(const char *, const char *)
Caller: pclose(FILE *)
Caller: ctermid(char *)
Caller: flockfile(FILE *)
Caller: ftrylockfile(FILE *)
Caller: funlockfile(FILE *)
Caller: __uflow(FILE *)
Caller: __overflow(FILE *, int)
Caller: get_timer_freq()
Caller: get_timer_value()
Caller: access(const char *, int)
Caller: faccessat(int, const char *, int, int)
Caller: lseek(int, __off_t, int)
Caller: close(int)
Caller: read(int, void *, int)
Caller: write(int, const void *, int)
Caller: pread(int, void *, int, __off_t)
Caller: pwrite(int, const void *, int, __off_t)
Caller: pipe(int *)
Caller: alarm(unsigned int)
Caller: sleep(unsigned int)
Caller: ualarm(__useconds_t, __useconds_t)
Caller: usleep(__useconds_t)
Caller: pause()
Caller: chown(const char *, __uid_t, __gid_t)
Caller: fchown(int, __uid_t, __gid_t)
Caller: lchown(const char *, __uid_t, __gid_t)
Caller: fchownat(int, const char *, __uid_t, __gid_t, int)
Caller: chdir(const char *)
Caller: fchdir(int)
Caller: getcwd(char *, int)
Caller: getwd(char *)
Caller: dup(int)
Caller: dup2(int, int)
Caller: execve(const char *, char *const *, char *const *)
Caller: fexecve(int, char *const *, char *const *)
Caller: execv(const char *, char *const *)
Caller: execle(const char *, const char *, ...)
Caller: execl(const char *, const char *, ...)
Caller: execvp(const char *, char *const *)
Caller: execlp(const char *, const char *, ...)
Caller: nice(int)
Caller: _exit(int)
  Callee: write_hex(int, unsigned long)
Caller: pathconf(const char *, int)
Caller: fpathconf(int, int)
Caller: sysconf(int)
Caller: confstr(int, char *, int)
Caller: getpid()
Caller: getppid()
Caller: getpgrp()
Caller: __getpgid(__pid_t)
Caller: getpgid(__pid_t)
Caller: setpgid(__pid_t, __pid_t)
Caller: setpgrp()
Caller: setsid()
Caller: getsid(__pid_t)
Caller: getuid()
Caller: geteuid()
Caller: getgid()
Caller: getegid()
Caller: getgroups(int, __gid_t *)
Caller: setuid(__uid_t)
Caller: setreuid(__uid_t, __uid_t)
Caller: seteuid(__uid_t)
Caller: setgid(__gid_t)
Caller: setregid(__gid_t, __gid_t)
Caller: setegid(__gid_t)
Caller: fork()
Caller: vfork()
Caller: ttyname(int)
Caller: ttyname_r(int, char *, int)
Caller: isatty(int)
Caller: ttyslot()
Caller: link(const char *, const char *)
Caller: linkat(int, const char *, int, const char *, int)
Caller: symlink(const char *, const char *)
Caller: readlink(const char *restrict, char *restrict, int)
Caller: symlinkat(const char *, int, const char *)
Caller: readlinkat(int, const char *restrict, char *restrict, int)
Caller: unlink(const char *)
Caller: unlinkat(int, const char *, int)
Caller: rmdir(const char *)
Caller: tcgetpgrp(int)
Caller: tcsetpgrp(int, __pid_t)
Caller: getlogin()
Caller: getlogin_r(char *, int)
Caller: setlogin(const char *)
Caller: getopt(int, char *const *, const char *)
Caller: gethostname(char *, int)
Caller: sethostname(const char *, int)
Caller: sethostid(long)
Caller: getdomainname(char *, int)
Caller: setdomainname(const char *, int)
Caller: vhangup()
Caller: revoke(const char *)
Caller: profil(unsigned short *, int, int, unsigned int)
Caller: acct(const char *)
Caller: getusershell()
Caller: endusershell()
Caller: setusershell()
Caller: daemon(int, int)
Caller: chroot(const char *)
Caller: getpass(const char *)
Caller: fsync(int)
Caller: gethostid()
Caller: sync()
Caller: getpagesize()
Caller: getdtablesize()
Caller: truncate(const char *, __off_t)
Caller: ftruncate(int, __off_t)
Caller: brk(void *)
Caller: sbrk(intptr_t)
Caller: syscall(long, ...)
Caller: lockf(int, int, __off_t)
Caller: fdatasync(int)
Caller: crypt(const char *, const char *)
Caller: getentropy(void *, int)
Caller: write_hex(int, unsigned long)
Caller: _stub(int)
Caller: _isatty(int)
Caller: __errno_location()
Caller: stat(const char *restrict, struct stat *restrict)
Caller: fstat(int, struct stat *)
Caller: fstatat(int, const char *restrict, struct stat *restrict, int)
Caller: lstat(const char *restrict, struct stat *restrict)
Caller: chmod(const char *, __mode_t)
Caller: lchmod(const char *, __mode_t)
Caller: fchmod(int, __mode_t)
Caller: fchmodat(int, const char *, __mode_t, int)
Caller: umask(__mode_t)
Caller: mkdir(const char *, __mode_t)
Caller: mkdirat(int, const char *, __mode_t)
Caller: mknod(const char *, __mode_t, __dev_t)
Caller: mknodat(int, const char *, __mode_t, __dev_t)
Caller: mkfifo(const char *, __mode_t)
Caller: mkfifoat(int, const char *, __mode_t)
Caller: utimensat(int, const char *, const struct timespec *, int)
Caller: futimens(int, const struct timespec *)
Caller: __fxstat(int, int, struct stat *)
Caller: __xstat(int, const char *, struct stat *)
Caller: __lxstat(int, const char *, struct stat *)
Caller: __fxstatat(int, int, const char *, struct stat *, int)
Caller: __xmknod(int, const char *, __mode_t, __dev_t *)
Caller: __xmknodat(int, int, const char *, __mode_t, __dev_t *)
Caller: _fstat(int, struct stat *)
  Callee: isatty(int)
  Callee: _stub(int)
Caller: __bswap_16(__uint16_t)
Caller: __bswap_32(__uint32_t)
Caller: __bswap_64(__uint64_t)
Caller: __uint16_identity(__uint16_t)
Caller: __uint32_identity(__uint32_t)
Caller: __uint64_identity(__uint64_t)
Caller: select(int, fd_set *restrict, fd_set *restrict, fd_set *restrict, struct timeval *restrict)
Caller: pselect(int, fd_set *restrict, fd_set *restrict, fd_set *restrict, const struct timespec *restrict, const __sigset_t *restrict)
Caller: _read(int, void *, int)
  Callee: _stub(int)
Caller: memcpy(void *restrict, const void *restrict, int)
Caller: memmove(void *, const void *, int)
Caller: memccpy(void *restrict, const void *restrict, int, int)
Caller: memset(void *, int, int)
Caller: memcmp(const void *, const void *, int)
Caller: memchr(const void *, int, int)
Caller: strcpy(char *restrict, const char *restrict)
Caller: strncpy(char *restrict, const char *restrict, int)
Caller: strcat(char *restrict, const char *restrict)
Caller: strncat(char *restrict, const char *restrict, int)
Caller: strcmp(const char *, const char *)
Caller: strncmp(const char *, const char *, int)
Caller: strcoll(const char *, const char *)
Caller: strxfrm(char *restrict, const char *restrict, int)
Caller: strcoll_l(const char *, const char *, locale_t)
Caller: strxfrm_l(char *, const char *, int, locale_t)
Caller: strdup(const char *)
Caller: strndup(const char *, int)
Caller: strchr(const char *, int)
Caller: strrchr(const char *, int)
Caller: strcspn(const char *, const char *)
Caller: strspn(const char *, const char *)
Caller: strpbrk(const char *, const char *)
Caller: strstr(const char *, const char *)
Caller: strtok(char *restrict, const char *restrict)
Caller: __strtok_r(char *restrict, const char *restrict, char **restrict)
Caller: strtok_r(char *restrict, const char *restrict, char **restrict)
Caller: strlen(const char *)
Caller: strnlen(const char *, int)
Caller: strerror(int)
Caller: strerror_r(int, char *, int)
Caller: strerror_l(int, locale_t)
Caller: bcmp(const void *, const void *, int)
Caller: bcopy(const void *, void *, int)
Caller: bzero(void *, int)
Caller: index(const char *, int)
Caller: rindex(const char *, int)
Caller: ffs(int)
Caller: ffsl(long)
Caller: ffsll(long long)
Caller: strcasecmp(const char *, const char *)
Caller: strncasecmp(const char *, const char *, int)
Caller: strcasecmp_l(const char *, const char *, locale_t)
Caller: strncasecmp_l(const char *, const char *, int, locale_t)
Caller: explicit_bzero(void *, int)
Caller: strsep(char **restrict, const char *restrict)
Caller: strsignal(int)
Caller: __stpcpy(char *restrict, const char *restrict)
Caller: stpcpy(char *restrict, const char *restrict)
Caller: __stpncpy(char *restrict, const char *restrict, int)
Caller: stpncpy(char *restrict, const char *restrict, int)
Caller: _put_char(int)
Caller: _write(int, const void *, int)
  Callee: _stub(int)
Caller: c_startup()
  Callee: __builtin_memcpy(void *, const void *, unsigned long)
  Callee: __builtin_memset(void *, int, unsigned long)
Caller: system_init()
  Callee: uart_init(unsigned int)
Caller: main()
  Callee: portable_fini(core_portable *)
  Callee: core_init_matrix(ee_u32, void *, ee_s32, mat_params *)
  Callee: get_seed_32(int)
  Callee: core_init_state(ee_u32, ee_s16, ee_u8 *)
  Callee: stop_time()
    Caller: get_timer_value()
  Callee: start_time()
    Caller: printf(const char *restrict, ...)
Caller: reset_handler()
  Callee: c_startup()
    Caller: __builtin_memcpy(void *, const void *, unsigned long)
    Caller: __builtin_memset(void *, int, unsigned long)
  Callee: system_init()
    Caller: uart_init(unsigned int)
Caller: _close(int)
  Callee: _stub(int)
Caller: exit(int)
Caller: uart_init(unsigned int)
Caller: uart_putc(int)
Caller: uart_puts(const char *)
  Callee: uart_putc(int)
Caller: outbyte(int)
  Callee: uart_putc(int)
Caller: reset_vector()
Caller: memory_init()
  Callee: __builtin_constant_p()
Caller: portable_init(core_portable *, int *, char **)
Caller: portable_fini(core_portable *)
Caller: iterate(void *)
  Callee: core_bench_list(core_results *, ee_s16)
    Caller: core_list_find(list_head *, list_data *)
    Caller: core_list_remove(list_head *)
    Caller: core_list_reverse(list_head *)
    Caller: crc16(ee_s16, ee_u16)
      Callee: crcu16(ee_u16, ee_u16)
        Caller: crcu8(ee_u8, ee_u16)
    Caller: core_list_mergesort(list_head *, list_cmp, core_results *)
      Callee: cmp
    Caller: core_list_undo_remove(list_head *, list_head *)
Caller: start_time()
  Callee: printf(const char *restrict, ...)
  Callee: get_timer_value()
Caller: stop_time()
  Callee: get_timer_value()
Caller: get_time()
Caller: time_in_secs(uint64_t)
Caller: crcu8(ee_u8, ee_u16)
Caller: crc16(ee_s16, ee_u16)
  Callee: crcu16(ee_u16, ee_u16)
    Caller: crcu8(ee_u8, ee_u16)
Caller: crcu16(ee_u16, ee_u16)
  Callee: crcu8(ee_u8, ee_u16)
Caller: crcu32(ee_u32, ee_u16)
  Callee: crc16(ee_s16, ee_u16)
    Caller: crcu16(ee_u16, ee_u16)
      Callee: crcu8(ee_u8, ee_u16)
Caller: check_data_types()
  Callee: printf(const char *restrict, ...)
Caller: portable_malloc(ee_size_t)
Caller: portable_free(void *)
Caller: parseval(char *)
Caller: core_list_init(ee_u32, list_head *, ee_s16)
  Callee: core_list_insert_new(list_head *, list_data *, list_head **, list_data **, list_head *, list_data *)
    Caller: copy_info(list_data *, list_data *)
Caller: core_bench_list(core_results *, ee_s16)
  Callee: core_list_find(list_head *, list_data *)
  Callee: core_list_remove(list_head *)
  Callee: core_list_reverse(list_head *)
  Callee: crc16(ee_s16, ee_u16)
    Caller: crcu16(ee_u16, ee_u16)
      Callee: crcu8(ee_u8, ee_u16)
  Callee: core_list_mergesort(list_head *, list_cmp, core_results *)
    Caller: cmp
  Callee: core_list_undo_remove(list_head *, list_head *)
Caller: core_init_state(ee_u32, ee_s16, ee_u8 *)
Caller: core_bench_state(ee_u32, ee_u8 *, ee_s16, ee_s16, ee_s16, ee_u16)
  Callee: crcu32(ee_u32, ee_u16)
    Caller: crc16(ee_s16, ee_u16)
      Callee: crcu16(ee_u16, ee_u16)
        Caller: crcu8(ee_u8, ee_u16)
  Callee: core_state_transition(ee_u8 **, ee_u32 *)
    Caller: ee_isdigit(ee_u8)
Caller: core_init_matrix(ee_u32, void *, ee_s32, mat_params *)
Caller: core_bench_matrix(mat_params *, ee_s16, ee_u16)
  Callee: matrix_test(ee_u32, MATRES *, MATDAT *, MATDAT *, MATDAT)
    Caller: matrix_sum(ee_u32, MATRES *, MATDAT)
    Caller: matrix_mul_const(ee_u32, MATRES *, MATDAT *, MATDAT)
    Caller: matrix_mul_matrix_bitextract(ee_u32, MATRES *, MATDAT *, MATDAT *)
    Caller: matrix_mul_matrix(ee_u32, MATRES *, MATDAT *, MATDAT *)
    Caller: crc16(ee_s16, ee_u16)
      Callee: crcu16(ee_u16, ee_u16)
        Caller: crcu8(ee_u8, ee_u16)
    Caller: matrix_add_const(ee_u32, MATDAT *, MATDAT)
    Caller: matrix_mul_vect(ee_u32, MATRES *, MATDAT *, MATDAT *)
Caller: core_list_find(list_head *, list_data *)
Caller: core_list_reverse(list_head *)
Caller: core_list_remove(list_head *)
Caller: core_list_undo_remove(list_head *, list_head *)
Caller: core_list_insert_new(list_head *, list_data *, list_head **, list_data **, list_head *, list_data *)
  Callee: copy_info(list_data *, list_data *)
Caller: core_list_mergesort(list_head *, list_cmp, core_results *)
  Callee: cmp
Caller: calc_func(ee_s16 *, core_results *)
  Callee: core_bench_state(ee_u32, ee_u8 *, ee_s16, ee_s16, ee_s16, ee_u16)
    Caller: crcu32(ee_u32, ee_u16)
      Callee: crc16(ee_s16, ee_u16)
        Caller: crcu16(ee_u16, ee_u16)
          Callee: crcu8(ee_u8, ee_u16)
    Caller: core_state_transition(ee_u8 **, ee_u32 *)
      Callee: ee_isdigit(ee_u8)
Caller: cmp_complex(list_data *, list_data *, core_results *)
  Callee: calc_func(ee_s16 *, core_results *)
    Caller: core_bench_state(ee_u32, ee_u8 *, ee_s16, ee_s16, ee_s16, ee_u16)
      Callee: crcu32(ee_u32, ee_u16)
        Caller: crc16(ee_s16, ee_u16)
          Callee: crcu16(ee_u16, ee_u16)
            Caller: crcu8(ee_u8, ee_u16)
      Callee: core_state_transition(ee_u8 **, ee_u32 *)
        Caller: ee_isdigit(ee_u8)
    Caller: core_bench_matrix(mat_params *, ee_s16, ee_u16)
      Callee: matrix_test(ee_u32, MATRES *, MATDAT *, MATDAT *, MATDAT)
        Caller: matrix_sum(ee_u32, MATRES *, MATDAT)
        Caller: matrix_mul_const(ee_u32, MATRES *, MATDAT *, MATDAT)
        Caller: matrix_mul_matrix_bitextract(ee_u32, MATRES *, MATDAT *, MATDAT *)
        Caller: matrix_mul_matrix(ee_u32, MATRES *, MATDAT *, MATDAT *)
        Caller: matrix_add_const(ee_u32, MATDAT *, MATDAT)
        Caller: matrix_mul_vect(ee_u32, MATRES *, MATDAT *, MATDAT *)
Caller: cmp_idx(list_data *, list_data *, core_results *)
Caller: copy_info(list_data *, list_data *)
Caller: _lseek(int, off_t, int)
  Callee: isatty(int)
  Callee: _stub(int)
Caller: _sbrk(int)
Caller: get_seed_32(int)
Caller: core_state_transition(ee_u8 **, ee_u32 *)
  Callee: ee_isdigit(ee_u8)
Caller: ee_isdigit(ee_u8)
Caller: matrix_test(ee_u32, MATRES *, MATDAT *, MATDAT *, MATDAT)
  Callee: matrix_sum(ee_u32, MATRES *, MATDAT)
  Callee: matrix_mul_const(ee_u32, MATRES *, MATDAT *, MATDAT)
  Callee: matrix_mul_matrix_bitextract(ee_u32, MATRES *, MATDAT *, MATDAT *)
  Callee: matrix_mul_matrix(ee_u32, MATRES *, MATDAT *, MATDAT *)
  Callee: crc16(ee_s16, ee_u16)
    Caller: crcu16(ee_u16, ee_u16)
      Callee: crcu8(ee_u8, ee_u16)
  Callee: matrix_add_const(ee_u32, MATDAT *, MATDAT)
  Callee: matrix_mul_vect(ee_u32, MATRES *, MATDAT *, MATDAT *)
Caller: matrix_sum(ee_u32, MATRES *, MATDAT)
Caller: matrix_mul_const(ee_u32, MATRES *, MATDAT *, MATDAT)
Caller: matrix_mul_vect(ee_u32, MATRES *, MATDAT *, MATDAT *)
Caller: matrix_mul_matrix(ee_u32, MATRES *, MATDAT *, MATDAT *)
Caller: matrix_mul_matrix_bitextract(ee_u32, MATRES *, MATDAT *, MATDAT *)
Caller: matrix_add_const(ee_u32, MATDAT *, MATDAT)
Caller: __ctype_get_mb_cur_max()
Caller: atof(const char *)
Caller: atoi(const char *)
Caller: atol(const char *)
Caller: atoll(const char *)
Caller: strtod(const char *restrict, char **restrict)
Caller: strtof(const char *restrict, char **restrict)
Caller: strtold(const char *restrict, char **restrict)
Caller: strtol(const char *restrict, char **restrict, int)
Caller: strtoul(const char *restrict, char **restrict, int)
Caller: strtoq(const char *restrict, char **restrict, int)
Caller: strtouq(const char *restrict, char **restrict, int)
Caller: strtoll(const char *restrict, char **restrict, int)
Caller: strtoull(const char *restrict, char **restrict, int)
Caller: l64a(long)
Caller: a64l(const char *)
Caller: random()
Caller: srandom(unsigned int)
Caller: initstate(unsigned int, char *, int)
Caller: setstate(char *)
Caller: random_r(struct random_data *restrict, int32_t *restrict)
Caller: srandom_r(unsigned int, struct random_data *)
Caller: initstate_r(unsigned int, char *restrict, int, struct random_data *restrict)
Caller: setstate_r(char *restrict, struct random_data *restrict)
Caller: rand()
Caller: srand(unsigned int)
Caller: rand_r(unsigned int *)
Caller: drand48()
Caller: erand48(unsigned short *)
Caller: lrand48()
Caller: nrand48(unsigned short *)
Caller: mrand48()
Caller: jrand48(unsigned short *)
Caller: srand48(long)
Caller: seed48(unsigned short *)
Caller: lcong48(unsigned short *)
Caller: drand48_r(struct drand48_data *restrict, double *restrict)
Caller: erand48_r(unsigned short *, struct drand48_data *restrict, double *restrict)
Caller: lrand48_r(struct drand48_data *restrict, long *restrict)
Caller: nrand48_r(unsigned short *, struct drand48_data *restrict, long *restrict)
Caller: mrand48_r(struct drand48_data *restrict, long *restrict)
Caller: jrand48_r(unsigned short *, struct drand48_data *restrict, long *restrict)
Caller: srand48_r(long, struct drand48_data *)
Caller: seed48_r(unsigned short *, struct drand48_data *)
Caller: lcong48_r(unsigned short *, struct drand48_data *)
Caller: malloc(int)
Caller: calloc(int, int)
Caller: realloc(void *, int)
Caller: reallocarray(void *, int, int)
Caller: free(void *)
Caller: alloca(int)
Caller: valloc(int)
Caller: posix_memalign(void **, int, int)
Caller: aligned_alloc(int, int)
Caller: abort()
Caller: atexit(void (*)(void))
Caller: at_quick_exit(void (*)(void))
Caller: on_exit(void (*)(int, void *), void *)
Caller: quick_exit(int)
Caller: _Exit(int)
Caller: getenv(const char *)
Caller: putenv(char *)
Caller: setenv(const char *, const char *, int)
Caller: unsetenv(const char *)
Caller: clearenv()
Caller: mktemp(char *)
Caller: mkstemp(char *)
Caller: mkstemps(char *, int)
Caller: mkdtemp(char *)
Caller: system(const char *)
Caller: realpath(const char *restrict, char *restrict)
Caller: bsearch(const void *, const void *, int, int, __compar_fn_t)
Caller: qsort(void *, int, int, __compar_fn_t)
Caller: abs(int)
Caller: labs(long)
Caller: llabs(long long)
Caller: div(int, int)
Caller: ldiv(long, long)
Caller: lldiv(long long, long long)
Caller: ecvt(double, int, int *restrict, int *restrict)
Caller: fcvt(double, int, int *restrict, int *restrict)
Caller: gcvt(double, int, char *)
Caller: qecvt(long double, int, int *restrict, int *restrict)
Caller: qfcvt(long double, int, int *restrict, int *restrict)
Caller: qgcvt(long double, int, char *)
Caller: ecvt_r(double, int, int *restrict, int *restrict, char *restrict, int)
Caller: fcvt_r(double, int, int *restrict, int *restrict, char *restrict, int)
Caller: qecvt_r(long double, int, int *restrict, int *restrict, char *restrict, int)
Caller: qfcvt_r(long double, int, int *restrict, int *restrict, char *restrict, int)
Caller: mblen(const char *, int)
Caller: mbtowc(int *restrict, const char *restrict, int)
Caller: wctomb(char *, int)
Caller: mbstowcs(int *restrict, const char *restrict, int)
Caller: wcstombs(char *restrict, const int *restrict, int)
Caller: rpmatch(const char *)
Caller: getsubopt(char **restrict, char *const *restrict, char **restrict)
Caller: getloadavg(double *, int)

```

再加料一下印出 variable 和 function param
```python
import clang.cindex as cindex
import json
import os

function_name = ""

# Initialize libclang
index = cindex.Index.create()

# Specify the path to the compile_commands.json file
compile_commands_file = '/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/compile_commands.json'

# Read the compile_commands.json file
with open(compile_commands_file, 'r') as f:
    compile_commands_data = json.load(f)

# Create a collection to store all .c and .cpp files
source_files = set()

# Iterate through each compilation command
for command_data in compile_commands_data:
    # Get the source file path from the compilation command
    source_file = command_data['file']

    # Check if the file extension is .c or .cpp
    if source_file.endswith('.c') or source_file.endswith('.cpp'):
        source_files.add("/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/" + source_file)

# Create a dictionary to store function call relationships
function_calls = {}
function_variable = {}
function_param = {}

# Iterate through the paths of all .c and .cpp files
for source_file in source_files:
    print(f"Analyzing {source_file}...")

    # Create a CompilationDatabase for the specified directory
    compile_commands = cindex.CompilationDatabase.fromDirectory('/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/')

    # Get the compilation commands
    commands = compile_commands.getCompileCommands(source_file)

    # Create a list to store compilation options
    file_args = []
    for command in commands:
        for argument in command.arguments:
            if str(argument).find("-I") >= 0:
                file_args.append(argument)

    # Parse the source code file
    translationUnit = index.parse(
        source_file,
        args=file_args,
        options=cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
    )

    if not translationUnit:
        print(f"Failed to parse translation unit for {source_file}")
    else:
        # Get the root node of the abstract syntax tree
        rootCursor = translationUnit.cursor

        # Recursive function to traverse each node in the abstract syntax tree
        def visit(cursor, depth=0):
            global function_name
            if cursor.kind == cindex.CursorKind.FUNCTION_DECL:
                # When a function declaration is found
                function_name = cursor.displayname
                if function_name not in function_calls:
                    function_calls[function_name] = set()
                if function_name not in function_variable:
                    function_variable[function_name] = set()
                if function_name not in function_param:
                    function_param[function_name] = set()
                
                # Get function parameter information
                for param in cursor.get_children():
                    if param.kind == cindex.CursorKind.PARM_DECL:
                        param_name = param.displayname
                        param_type = param.type.spelling
                        param_info = f" Parameter Name: {param_name} | Parameter Type: {param_type}"
                        function_param[function_name].add(param_info)
                    
            # Print other functions called by this function
            for child in cursor.get_children():
                if child.kind == cindex.CursorKind.CALL_EXPR:
                    callee = child.referenced
                    if callee:
                        callee_name = callee.displayname
                        function_calls[function_name].add(callee_name)
                if child.kind:
                    # Get variable declarations referenced by DECL_REF_EXPR
                    var_decl = child.get_definition()
                    if var_decl and var_decl.kind == cindex.CursorKind.VAR_DECL:
                        output = " Variable Name:"+ str(child.displayname) + "|Variable Location:"+ str(var_decl.location.file.name)+ ":"+  str(var_decl.location.line)+ ":"+ str(var_decl.location.column)
                        function_variable[function_name].add(output)

            for child in cursor.get_children():
                visit(child, depth + 1)

        # Call the traversal function
        visit(rootCursor)

# Record of function calls
function_calls_record = []

def print_function_calls(caller, depth=1):
    if caller in function_calls_record:
        return
    else:
        function_calls_record.append(caller)
    for callee in function_calls[caller]:
        if callee in function_calls_record:
            return
        else:
            function_calls_record.append(callee)

        indent = "  " * depth
        print(f"{indent}Function Declaration: {caller}")
        print(f"{indent}  Callee: {callee}")
        print_function_calls(callee, depth + 1)

total_call_record = []
def print_function_param(function_name, depth):
    if function_name in function_param:
        get_function_param= function_param[function_name]
        indent = "  " * depth
        for x in get_function_param:
            print(f"{indent} {x}")

def print_function_variable(function_name, depth):
    if function_name in function_variable:
        get_function_variable = function_variable[function_name]
        indent = "  " * depth
        for x in get_function_variable:
            print(f"{indent} {x}")

def print_function_calls(caller, depth=0):
    global function_calls_record
    if caller in function_calls_record:
        return
    else:
        function_calls_record.append(caller)
    indent = "  " * depth
    print(f"{indent} Caller: {caller}")
    print_function_param(caller, depth)
    print_function_variable(caller, depth)
    if caller in function_calls:
        for callee in function_calls[caller]:
            if callee in function_calls_record:
                return
            else:
                function_calls_record.append(callee)

            indent = "  " * (depth + 1)
            print(f"{indent} Callee: {callee}")
            print_function_param(callee, depth+ 1)
            print_function_variable(caller, depth+ 1)
            if callee in function_calls:
                for x in function_calls[callee]:
                    print_function_calls(x, depth + 2)

# Iterate through all functions and record function call stacks
function_calls_record = []
for caller in function_calls:
    function_calls_record = []
    print_function_calls(caller)
    print("------------------------------------------------")
    total_call_record.append(function_calls_record)

```
output
```
------------------------------------------------
 Caller: calc_func(ee_s16 *, core_results *)
  Parameter Name: pdata | Parameter Type: ee_s16 *
  Parameter Name: res | Parameter Type: core_results *
  Variable Name:data|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_list_join.c:72:12
  Variable Name:flag|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_list_join.c:81:16
  Variable Name:retval|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_list_join.c:73:12
  Variable Name:dtype|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_list_join.c:82:16
  Variable Name:optype|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_list_join.c:74:12
   Callee: core_bench_matrix(mat_params *, ee_s16, ee_u16)
    Parameter Name: crc | Parameter Type: ee_u16
    Parameter Name: seed | Parameter Type: ee_s16
    Parameter Name: p | Parameter Type: mat_params *
    Variable Name:data|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_list_join.c:72:12
    Variable Name:flag|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_list_join.c:81:16
    Variable Name:retval|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_list_join.c:73:12
    Variable Name:dtype|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_list_join.c:82:16
    Variable Name:optype|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_list_join.c:74:12
     Caller: crc16(ee_s16, ee_u16)
      Parameter Name: crc | Parameter Type: ee_u16
      Parameter Name: newval | Parameter Type: ee_s16
       Callee: crcu16(ee_u16, ee_u16)
        Parameter Name: crc | Parameter Type: ee_u16
        Parameter Name: newval | Parameter Type: ee_u16
         Caller: crcu8(ee_u8, ee_u16)
          Parameter Name: crc | Parameter Type: ee_u16
          Parameter Name: data | Parameter Type: ee_u8
          Variable Name:i|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_util.c:167:11
          Variable Name:carry|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_util.c:167:27
          Variable Name:x16|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_util.c:167:18
     Caller: matrix_test(ee_u32, MATRES *, MATDAT *, MATDAT *, MATDAT)
      Parameter Name: val | Parameter Type: MATDAT
      Parameter Name: B | Parameter Type: MATDAT *
      Parameter Name: N | Parameter Type: ee_u32
      Parameter Name: A | Parameter Type: MATDAT *
      Parameter Name: C | Parameter Type: MATRES *
      Variable Name:crc|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_matrix.c:132:12
      Variable Name:clipval|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_matrix.c:133:12
       Callee: matrix_mul_matrix_bitextract(ee_u32, MATRES *, MATDAT *, MATDAT *)
        Parameter Name: B | Parameter Type: MATDAT *
        Parameter Name: N | Parameter Type: ee_u32
        Parameter Name: A | Parameter Type: MATDAT *
        Parameter Name: C | Parameter Type: MATRES *
        Variable Name:crc|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_matrix.c:132:12
        Variable Name:clipval|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_matrix.c:133:12
       Callee: matrix_mul_vect(ee_u32, MATRES *, MATDAT *, MATDAT *)
        Parameter Name: B | Parameter Type: MATDAT *
        Parameter Name: N | Parameter Type: ee_u32
        Parameter Name: A | Parameter Type: MATDAT *
        Parameter Name: C | Parameter Type: MATRES *
        Variable Name:crc|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_matrix.c:132:12
        Variable Name:clipval|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_matrix.c:133:12
       Callee: matrix_mul_const(ee_u32, MATRES *, MATDAT *, MATDAT)
        Parameter Name: val | Parameter Type: MATDAT
        Parameter Name: N | Parameter Type: ee_u32
        Parameter Name: A | Parameter Type: MATDAT *
        Parameter Name: C | Parameter Type: MATRES *
        Variable Name:crc|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_matrix.c:132:12
        Variable Name:clipval|Variable Location:/home/x213212/cpptest/cppcheck/addons/CoreMark-V5/demo/core_matrix.c:133:12
------------------------------------------------
```

