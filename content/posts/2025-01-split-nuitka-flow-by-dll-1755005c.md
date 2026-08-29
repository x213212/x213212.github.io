---
title: "split nuitka flow by dll"
date: "2025-01-04T01:56:00.006+08:00"
updated: "2025-01-04T01:57:02.105+08:00"
permalink: "/2025/01/split-nuitka-flow-by-dll.html"
original_url: "https://x8795278.blogspot.com/2025/01/split-nuitka-flow-by-dll.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5717600833564036614"
tags: ["Nuitka"]
layout: post
---

![](https://hackmd.io/_uploads/B1MIEoSUyl.png)

# split nuitka flow by dll
上次透過 ollvm 混淆，我發現這個網站感覺同個類型的不斷上傳會導致我的樣本數越檢測越多，這次再來透過一個方法來躲避看看，根據Nuitka的流程是 透過兩階段才能執行我的 binary 假設透過 --onefile 和 --standalone
壓出來exe被檢測的機率應該是蠻高的很大機率被識別為特洛伊木馬或者 Nuitka package 等等那其實
那假設希望下 --onefile又不想要核心主程式被刪掉或檢測 應該可以嘗試我的方法 目前實測應該都ok
那麼說一下nuitka 的 --onefile的行為好了，假設這樣編譯的話 nuitka最終會產生一個 執行檔，而 --standalone 一起下的會 這個執行檔執行的時候會解壓出相對應的 lib 相關文件等等，就是這個行為會導致被一堆防毒軟體檢測為有病毒，那我最後用的方法嘗試了兩個，第一我幫 nuitka 的 kernel.exe 壓縮進去 dll 檔案
然後再透過 另一個程式碼呼叫 這個dll 進行動態解壓縮，然後透過windows api 直接 load到記憶體中執行，這行為差不多就會被掃毒網站掃到一堆，另一個方法就是解壓縮到另一個目錄然後再執行，這樣的話就不會發生執行和解壓縮行為就會寫到dll ,而呼叫這個dll的程式碼也基本上不會被檢測到，
# compressor
```bash
gcc -c cm.c -o compressor
```
這個compressor會將elf 壓成 xxx.c 你的程式碼會變成一個char 陣列
```
compressor <target file> <outputfile>
compressor test.exe embedded.c
```
```c
#include <stdio.h>
#include <stdlib.h>
#include "zlib.h"

int main(int argc, char *argv[]) {
    if (argc != 3) {
        printf("Usage: %s <input_file> <output_c_file>\n", argv[0]);
        return 1;
    }

    const char *input_file = argv[1];
    const char *output_c_file = argv[2];
    FILE *in = fopen(input_file, "rb");
    if (!in) {
        perror("Failed to open input file");
        return 1;
    }
    fseek(in, 0, SEEK_END);
    size_t input_size = ftell(in);
    fseek(in, 0, SEEK_SET);

    unsigned char *input_data = malloc(input_size);
    fread(input_data, 1, input_size, in);
    fclose(in);

    size_t compressed_size = compressBound(input_size);
    unsigned char *compressed_data = malloc(compressed_size);

    if (compress(compressed_data, &compressed_size, input_data, input_size) != Z_OK) {
        printf("Compression failed.\n");
        free(input_data);
        free(compressed_data);
        return 1;
    }

    free(input_data);

    FILE *out = fopen(output_c_file, "w");
    if (!out) {
        perror("Failed to create output C file");
        free(compressed_data);
        return 1;
    }

    fprintf(out, "#include <stddef.h>\n\n");
    fprintf(out, "const unsigned char compressed_data[] = {");
    for (size_t i = 0; i < compressed_size; i++) {
        if (i % 16 == 0) fprintf(out, "\n    ");
        fprintf(out, "0x%02x, ", compressed_data[i]);
    }
    fprintf(out, "\n};\n");
    fprintf(out, "const size_t compressed_size = %zu;\n", compressed_size);

    fclose(out);
    free(compressed_data);

    printf("Generated embedded C file: %s\n", output_c_file);
    return 0;
}

```

# dll.c
而這邊透過 zlib 進行編譯 記得要加-lz
```bas
gcc -shared -o loader.dll dll.c embedded.c -lz
```
你會得到一個 loader.dll
```c
#include <windows.h>
#include "zlib.h"
#include <stdlib.h>
#include <stdio.h>

// Embedded compressed data (must be defined elsewhere)
extern const unsigned char compressed_data[];
extern const size_t compressed_size;

// Target file path
const char *target_file_path = "lib\\andes_autotuning.exe"; // Change '/' to '\\' for Windows compatibility

// Decompress compressed data into memory
void *decompress_to_memory(size_t *output_size) {
    unsigned long uncompressed_size = 250 * 1024 * 1024; // Assuming max decompression size is 250MB
    unsigned char *uncompressed_data = malloc(uncompressed_size);
    if (!uncompressed_data) {
        printf("Failed to allocate memory for decompression.\n");
        return NULL;
    }

    z_stream strm = {0};
    strm.next_in = (unsigned char *)compressed_data;
    strm.avail_in = compressed_size;
    strm.next_out = uncompressed_data;
    strm.avail_out = uncompressed_size;

    if (inflateInit(&strm) != Z_OK) {
        printf("Failed to initialize zlib for decompression.\n");
        free(uncompressed_data);
        return NULL;
    }

    int ret = inflate(&strm, Z_FINISH);
    if (ret != Z_STREAM_END) {
        printf("Decompression failed. Error code: %d\n", ret);
        free(uncompressed_data);
        inflateEnd(&strm);
        return NULL;
    }

    *output_size = strm.total_out;
    inflateEnd(&strm);

    return uncompressed_data;
}

// Write the decompressed binary to the target path
int write_to_target_file(const void *data, size_t size, const char *path) {
    FILE *file = fopen(path, "wb");
    if (!file) {
        printf("Failed to create target file: %s\n", path);
        return 0;
    }

    fwrite(data, 1, size, file);
    fclose(file);

    return 1;
}

void launch_binary(const char *file_path, const char *args) {
    STARTUPINFOA si = {0};
    PROCESS_INFORMATION pi = {0};
    si.cb = sizeof(si);

    // Construct the command line with multiple arguments
    char command_line[MAX_PATH + 1024];
    snprintf(command_line, sizeof(command_line), "\"%s\" %s", file_path, args);

    printf("Command Line: %s\n", command_line);

    if (!CreateProcessA(
            NULL,                // Application name
            command_line,        // Command line arguments
            NULL,                // Process security attributes
            NULL,                // Thread security attributes
            FALSE,               // Inherit handles
            0,                   // Creation flags
            NULL,                // Environment variables
            NULL,                // Current directory
            &si, &pi)) {         // Startup and process information
        printf("Failed to launch binary. Error: %lu\n", GetLastError());
        return;
    }

    printf("Binary launched successfully with arguments: %s\n", args);

    // Wait for the process to complete
    WaitForSingleObject(pi.hProcess, INFINITE);

    // Clean up handles
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
}

__declspec(dllexport) void RunBinary(const char *args) {
    printf("Received arguments: %s\n", args);

    size_t uncompressed_size;
    void *uncompressed_data = decompress_to_memory(&uncompressed_size);
    if (!uncompressed_data) {
        printf("Decompression failed.\n");
        return;
    }

    if (!write_to_target_file(uncompressed_data, uncompressed_size, target_file_path)) {
        printf("Failed to write decompressed file to target path.\n");
        free(uncompressed_data);
        return;
    }

    free(uncompressed_data);

    // Launch the binary with the arguments
    launch_binary(target_file_path, args);
}

```

# dll runner
```bash
gcc -o main_program dllrun.c
```
這樣的話就可以透過把核心邏輯寫在 dll了，實測下來效果還不錯
```c
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Update the typedef to pass multiple arguments as a single string
typedef void (*RunBinaryFn)(const char *);

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: andes_autotuning.exe --config <config_path>\n");
        return 1;
    }

    // Calculate total length of parameters
    size_t total_length = 0;
    for (int i = 1; i < argc; ++i) {
        total_length += strlen(argv[i]) + 1; // Include spaces or null terminators
    }

    // Allocate memory for the combined parameter string
    char *param = (char *)malloc(total_length);
    if (!param) {
        printf("Memory allocation failed.\n");
        return 1;
    }

    param[0] = '\0'; // Initialize the string

    // Combine all arguments into a single string
    for (int i = 1; i < argc; ++i) {
        strncat(param, argv[i], total_length - strlen(param) - 1);
        if (i < argc - 1) {
            strncat(param, " ", total_length - strlen(param) - 1); // Add a space between arguments
        }
    }

    // Load the DLL
    HMODULE hDll = LoadLibrary("loader.dll");
    if (!hDll) {
        printf("Failed to load DLL. Error: %lu\n", GetLastError());
        free(param);
        return 1;
    }

    // Get the exported function address
    RunBinaryFn runBinary = (RunBinaryFn)GetProcAddress(hDll, "RunBinary");
    if (!runBinary) {
        printf("Failed to find RunBinary function. Error: %lu\n", GetLastError());
        FreeLibrary(hDll);
        free(param);
        return 1;
    }

    // Call the DLL's function and pass the parameters
    printf("Calling RunBinary from DLL with parameters: %s\n", param);
    runBinary(param);

    // Unload the DLL and free resources
    FreeLibrary(hDll);
    free(param);

    return 0;
}

```
# load memory
這邊就是直接load 到memory 了不過沒什麼用哈哈
```c
#include <windows.h>
#include <stdio.h>
#include <zlib.h>
#include <stdlib.h>

// 嵌入的压缩数据
extern const unsigned char compressed_data[];
extern const size_t compressed_size;

// 解压缩数据到内存
void *decompress_to_memory(size_t *output_size) {
    unsigned long uncompressed_size = 10 * 1024 * 1024; // 假设最大解压大小为 10MB
    unsigned char *uncompressed_data = malloc(uncompressed_size);
    if (!uncompressed_data) {
        printf("Failed to allocate memory for decompression.\n");
        return NULL;
    }

    z_stream strm = {0};
    strm.next_in = (unsigned char *)compressed_data;
    strm.avail_in = compressed_size;
    strm.next_out = uncompressed_data;
    strm.avail_out = uncompressed_size;

    if (inflateInit(&strm) != Z_OK) {
        printf("Failed to initialize zlib for decompression.\n");
        free(uncompressed_data);
        return NULL;
    }

    int ret = inflate(&strm, Z_FINISH);
    if (ret != Z_STREAM_END) {
        printf("Decompression failed. Error code: %d\n", ret);
        free(uncompressed_data);
        inflateEnd(&strm);
        return NULL;
    }

    *output_size = strm.total_out;
    inflateEnd(&strm);

    return uncompressed_data;
}

// 在内存中加载并运行 PE 文件
void load_and_run_pe(const void *pe_data) {
    IMAGE_DOS_HEADER *dos_header = (IMAGE_DOS_HEADER *)pe_data;
    IMAGE_NT_HEADERS *nt_headers = (IMAGE_NT_HEADERS *)((BYTE *)pe_data + dos_header->e_lfanew);

    void *base_address = VirtualAlloc(NULL,
                                      nt_headers->OptionalHeader.SizeOfImage,
                                      MEM_RESERVE | MEM_COMMIT,
                                      PAGE_EXECUTE_READWRITE);
    if (!base_address) {
        printf("Failed to allocate memory for PE file.\n");
        return;
    }

    memcpy(base_address, pe_data, nt_headers->OptionalHeader.SizeOfHeaders);

    IMAGE_SECTION_HEADER *section = IMAGE_FIRST_SECTION(nt_headers);
    for (int i = 0; i < nt_headers->FileHeader.NumberOfSections; i++) {
        void *dest = (BYTE *)base_address + section[i].VirtualAddress;
        void *src = (BYTE *)pe_data + section[i].PointerToRawData;
        memcpy(dest, src, section[i].SizeOfRawData);
    }

    void (*entry_point)() = (void (*)())((BYTE *)base_address + nt_headers->OptionalHeader.AddressOfEntryPoint);
    printf("Jumping to entry point...\n");
    entry_point();

    VirtualFree(base_address, 0, MEM_RELEASE);
}

int main() {
    size_t uncompressed_size;

    void *uncompressed_data = decompress_to_memory(&uncompressed_size);
    if (!uncompressed_data) {
        printf("Decompression failed.\n");
        return 1;
    }

    load_and_run_pe(uncompressed_data);
    free(uncompressed_data);

    return 0;
}

```
![image](https://hackmd.io/_uploads/BJUXVoSIyg.png)
![image](https://hackmd.io/_uploads/B1MIEoSUyl.png)

