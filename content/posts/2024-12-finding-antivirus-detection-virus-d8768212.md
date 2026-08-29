---
title: "Finding Antivirus Detection Virus Signatures (nuitka package)"
date: "2024-12-22T13:03:00.001+08:00"
updated: "2024-12-22T13:03:51.306+08:00"
permalink: "/2024/12/finding-antivirus-detection-virus.html"
original_url: "https://x8795278.blogspot.com/2024/12/finding-antivirus-detection-virus.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-531323686242376570"
tags: ["eset", "Nuitka"]
layout: post
---

![](https://hackmd.io/_uploads/B1DoTGSSye.png)

# Finding Antivirus Detection Virus Signatures (nuitka package)
最近在遇到 Nuitka 打包 會被eset 防毒軟體檢測的方式大概試了下面幾個方法
第一加殼，透過把 binary 壓縮 再套在另外一層的 c shell 來逃避 防毒軟體在 靜態分析掃描到相關特徵碼
第一種方法的話大部分防毒都會檢測到UPX 很早期的加殼，或著叫 chargpt 也可以產生一下簡單 aes 加殼 脫殼的方法 反正就是 將一些section 加密起來，因為是加密的，當 shell 啟動後會 decode 相關的 section 加載正確的 binary  data 這些東西當然就不存在於 病毒的資料庫裡面所以當然找不到。
第二移除特徵碼，之前對這個蠻感興趣，剛好有實際案例可以試試看，看了一些查找病毒特徵碼的tool,發現大概可以這樣來實現，大概就是保留原本的 exe pe 結構，然後分別對各個 section 去做分割的動作，每次分割出來的 分塊的section 都有可能涵蓋到一小片段特徵碼被防毒軟體偵測到，也有複合的特徵碼片段的情況，所以那些tool 做的事情就是 拆個片段的特徵碼，然後再掃描看防毒砍掉哪些片段，逐一縮小範圍
目前猜想是這樣，
所以第一個步驟是尋找有可能產生這些片段section 的排列組合至少存在一組以上
那我要反向查找特徵碼最小集合是，例如我要在local 不斷的呼叫 ESET 裡面的ecls.exe(掃描分割出來的檔案來檢測那些塊組合會導致被檢測到病毒)
比如說掃描一個 nuitka 的 編譯pyhton pe結構 大概會得出下列幾個section，
首先你要用 nuitka 編譯一個 python 並印出hello，這時候不管內容是什麼你會被 Eset 監測為
```
﻿Log
 a variant of Python/Packed.Nuitka.Y suspicious application - cleaned by deleting [1]
```
下面是窮舉nuitka編譯出來的 binary 所有section 並找到 最小集合的 section 會被eset 檢測到是 Python/Packed.Nuitka 組合得程式碼片段
```python
import os
import pefile
import subprocess
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor, as_completed

def scan_with_eset(file_path, eset_path="C:\\Program Files\\ESET\\ESET Security\\ecls.exe"):
    """
    使用 ESET 的命令行工具扫描文件
    """
    try:
        command = [eset_path, file_path]
        result = subprocess.run(command, capture_output=True, text=True)
        if  result.stdout.find("a variant of")>=0:
            return True
        return False
    except FileNotFoundError:
        print(f"ESET Command Line Scanner not found at {eset_path}.")
        return False

def generate_section_combination(pe, binary_data, section_names, fill_byte=0x00):
    """
    根据目标 sections，生成包含它们组合的新二进制文件
    """
    new_binary = bytearray(binary_data)

    for section in pe.sections:
        name = section.Name.decode().strip('\x00')
        start = section.PointerToRawData
        size = section.SizeOfRawData

        # 填充非目标 Sections
        if name not in section_names:
            new_binary[start:start + size] = bytes([fill_byte] * size)

    return new_binary

def scan_section_combinations(pe, binary_data, output_dir, eset_path, max_combination_size=3, max_workers=4):
    """
    扫描单独 sections 和它们的组合
    """
    section_names = [section.Name.decode().strip('\x00') for section in pe.sections]
    print(f"Available sections: {section_names}")

    trigger_combinations = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        # 扫描所有单独的 sections 和它们的组合
        for size in range(1, max_combination_size + 1):
            for combination in combinations(section_names, size):
                temp_file = os.path.join(output_dir, f"combination_{'_'.join(combination)}.bin")
                modified_binary = generate_section_combination(pe, binary_data, combination)

                # 保存临时文件
                with open(temp_file, "wb") as f:
                    f.write(modified_binary)

                # 提交扫描任务并存储 Future 和组合映射
                futures[executor.submit(scan_with_eset, temp_file, eset_path)] = combination

                print(f"Scanning combination: {combination}")

        # 收集结果
        for future in as_completed(futures):
            combination = futures[future]
            try:
                if future.result():
                    print(f"Threat detected in combination: {combination}")
                    trigger_combinations.append(combination)
            except Exception as e:
                print(f"Error scanning combination {combination}: {e}")

    return trigger_combinations

def main(input_file, output_dir, eset_path, max_workers=4):
    """
    主函数
    """
    # 读取二进制文件
    with open(input_file, "rb") as f:
        binary_data = f.read()

    # 初始化 PE 文件解析器
    pe = pefile.PE(data=binary_data)

    # 初始化输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 扫描单独 sections 和它们的组合
    print("Starting section and combination scanning...")
    trigger_combinations = scan_section_combinations(pe, binary_data, output_dir, eset_path, max_combination_size=4, max_workers=max_workers)

    # 输出结果
    if trigger_combinations:
        print("\n=== Threat Combinations Found ===")
        for combination in trigger_combinations:
            print(f"Combination: {combination}")
    else:
        print("No threats detected in any combination.")

if __name__ == "__main__":
    # 输入文件和输出目录
    input_file = "test.exe"  # 替换为你的实际文件路径
    output_dir = "./output"
    eset_path = "C:\\Program Files\\ESET\\ESET Security\\ecls.exe"
    max_workers = 4  # 控制线程池最大线程数

    # 启动分析
    main(input_file, output_dir, eset_path, max_workers)

```
#　output
![image](https://hackmd.io/_uploads/BJ8XjzrHkl.png)

```
Starting section and combination scanning...
Available sections: ['.text', '.data', '.rdata', '.eh_fram', '.pdata', '.xdata', '.bss', '.idata', '.CRT', '.tls', '.rsrc', '.reloc']
Scanning combination: ('.text',)
Scanning combination: ('.data',)
Scanning combination: ('.rdata',)
Scanning combination: ('.eh_fram',)
Scanning combination: ('.pdata',)
Scanning combination: ('.xdata',)
Scanning combination: ('.bss',)
Scanning combination: ('.idata',)
Scanning combination: ('.CRT',)
Scanning combination: ('.tls',)
Scanning combination: ('.rsrc',)
Scanning combination: ('.reloc',)
Scanning combination: ('.text', '.data')
Scanning combination: ('.text', '.rdata')
Scanning combination: ('.text', '.eh_fram')
Scanning combination: ('.text', '.pdata')
Scanning combination: ('.text', '.xdata')
Scanning combination: ('.text', '.bss')
Scanning combination: ('.text', '.idata')
Scanning combination: ('.text', '.CRT')
Scanning combination: ('.text', '.tls')
Scanning combination: ('.text', '.rsrc')
Scanning combination: ('.text', '.reloc')
Scanning combination: ('.data', '.rdata')
Scanning combination: ('.data', '.eh_fram')
Scanning combination: ('.data', '.pdata')
Scanning combination: ('.data', '.xdata')
Scanning combination: ('.data', '.bss')
```
這邊可以看到最終的得出這些section，可以看到這些組合裡面都有 .rdata
也就是我只要破壞其中一個 section 就可讓防毒軟體 識別不出來
```
=== Threat Combinations Found ===
Combination: ('.text', '.rdata', '.rsrc')
Combination: ('.text', '.data', '.rdata', '.rsrc')
Combination: ('.text', '.rdata', '.eh_fram', '.rsrc')
Combination: ('.text', '.rdata', '.pdata', '.rsrc')
Combination: ('.text', '.rdata', '.xdata', '.rsrc')
Combination: ('.text', '.rdata', '.bss', '.rsrc')
Combination: ('.text', '.rdata', '.idata', '.CRT')
Combination: ('.text', '.rdata', '.idata', '.rsrc')
Combination: ('.text', '.rdata', '.CRT', '.rsrc')
Combination: ('.text', '.rdata', '.tls', '.rsrc')
Combination: ('.text', '.rdata', '.rsrc', '.reloc')
```
所以透過這個方法，例如我接下來只要隨機對 .rdata填充 0x0 不斷的破壞數據在恢復，找到最小破壞的 byte 區間在對應到程式碼，假設沒影響就反向恢復數據，直到找到 eset 這個防毒軟體到底是針對哪一些 特徵來檢測到底是不是病毒，
```python
import os
import subprocess
import pefile

def scan_with_eset(file_path, eset_path="C:\\Program Files\\ESET\\ESET Security\\ecls.exe"):
    """
    使用 ESET 的命令行工具扫描文件
    """
    try:
        command = [eset_path, file_path]
        result = subprocess.run(command, capture_output=True, text=True)
        if "a variant of Python/Packed.Nuitka.Y suspicious application" in result.stdout:
            return True
        return False
    except FileNotFoundError:
        print(f"ESET Command Line Scanner not found at {eset_path}.")
        return False

def mutate_rdata_exact(pe, binary_data, section_name, start_offset, end_offset, fill_byte=0x00):
    """
    精确填充 .rdata 的指定范围内容为 fill_byte，并返回修改的差异
    """
    differences = []
    modified_binary = bytearray(binary_data)
    for section in pe.sections:
        name = section.Name.decode().strip('\x00')
        if name == section_name:
            start = section.PointerToRawData + start_offset
            end = section.PointerToRawData + end_offset

            # 修改指定范围并记录原始值
            for offset in range(start, end + 1):
                original_value = modified_binary[offset]
                if original_value != fill_byte:  # 仅修改非 fill_byte 的字节
                    modified_binary[offset] = fill_byte
                    differences.append((offset, original_value, fill_byte))
            return modified_binary, differences
    return binary_data, differences

def binary_search_rdata(pe, binary_data, output_dir, eset_path, section_name, start, end, fill_byte=0x00):
    """
    使用二分法在 .rdata 中找到最小影响范围
    """
    if start > end:
        return []

    # 当范围缩小到单个字节
    if start == end:
        print(f"Testing single byte at Offset: {start}")
        temp_binary, diff = mutate_rdata_exact(pe, binary_data, section_name, start, end, fill_byte)
        temp_file = os.path.join(output_dir, f"single_byte_{start}.bin")
        with open(temp_file, "wb") as f:
            f.write(temp_binary)

        if not scan_with_eset(temp_file, eset_path):
            print(f"Threat neutralized by modifying single byte at Offset: {start}")
            return diff  # 返回当前唯一的差异作为结果
        return []

    # 中间索引
    mid = (start + end) // 2
    print(f"Testing range {start}-{mid}")
    left_binary, left_diff = mutate_rdata_exact(pe, binary_data, section_name, start, mid, fill_byte)
    left_file = os.path.join(output_dir, f"rdata_left_{start}_{mid}.bin")
    with open(left_file, "wb") as f:
        f.write(left_binary)

    if not scan_with_eset(left_file, eset_path):
        print(f"Threat neutralized by modifying range {start}-{mid}")
        return binary_search_rdata(pe, binary_data, output_dir, eset_path, section_name, start, mid, fill_byte)

    print(f"Testing range {mid + 1}-{end}")
    right_binary, right_diff = mutate_rdata_exact(pe, binary_data, section_name, mid + 1, end, fill_byte)
    right_file = os.path.join(output_dir, f"rdata_right_{mid + 1}_{end}.bin")
    with open(right_file, "wb") as f:
        f.write(right_binary)

    if not scan_with_eset(right_file, eset_path):
        print(f"Threat neutralized by modifying range {mid + 1}-{end}")
        return binary_search_rdata(pe, binary_data, output_dir, eset_path, section_name, mid + 1, end, fill_byte)

    return left_diff + right_diff

def refine_to_byte_level(binary_data, effective_differences, output_dir, eset_path):
    """
    在已确定的范围内逐字节确认有效的修改字节
    """
    minimal_differences = []
    for offset, original, modified in effective_differences:
        temp_binary = bytearray(binary_data)
        temp_binary[offset] = modified

        temp_file = os.path.join(output_dir, f"test_byte_{offset}.bin")
        with open(temp_file, "wb") as f:
            f.write(temp_binary)

        if not scan_with_eset(temp_file, eset_path):
            print(f"Byte at offset {offset} is critical for neutralization.")
            minimal_differences.append((offset, original, modified))
        else:
            print(f"Byte at offset {offset} does not affect neutralization. Reverting.")

    return minimal_differences

def main(input_file, output_dir, eset_path):
    """
    主函数
    """
    # 读取二进制文件
    with open(input_file, "rb") as f:
        binary_data = f.read()

    # 初始化 PE 文件解析器
    pe = pefile.PE(data=binary_data)

    # 定义目标 Sections
    target_sections = ['.text', '.rdata', '.idata', '.CRT']

    # 初始化输出目录
    os.makedirs(output_dir, exist_ok=True)

    print("Checking if the base combination triggers a threat...")
    if not scan_with_eset(input_file, eset_path):
        print("Base combination does not trigger any threat. Exiting.")
        return

    print("Base combination triggers threat. Starting binary search...")

    for section in pe.sections:
        name = section.Name.decode().strip('\x00')
        if name in target_sections:
            print(f"Analyzing section: {name}")
            if name == ".rdata":
                start = 0
                size = section.SizeOfRawData

                # 使用二分法找到初步修改范围
                effective_differences = binary_search_rdata(pe, binary_data, output_dir, eset_path, name, start, size - 1)

                print("\n=== Refining to Byte Level ===")
                minimal_differences = refine_to_byte_level(binary_data, effective_differences, output_dir, eset_path)

                # 输出最终的最小修改结果
                log_file = os.path.join(output_dir, "minimal_modifications.log")
                with open(log_file, "w") as log:
                    log.write("=== Minimal Modifications ===\n")
                    for offset, original, modified in minimal_differences:
                        log.write(f"Offset: {offset}, Original: {hex(original)}, Modified: {hex(modified)}\n")

                print(f"Minimal modification log saved to {log_file}")

if __name__ == "__main__":
    # 输入文件和输出目录
    input_file = "test.exe"  # 替换为你的实际文件路径
    output_dir = "./output"
    eset_path = "C:\\Program Files\\ESET\\ESET Security\\ecls.exe"

    # 启动分析
    main(input_file, output_dir, eset_path)

```

![image](https://hackmd.io/_uploads/r1idoMrHkg.png)

也就是我最小異動這個 115496這個 offset 的 byte就可以導致 eset 判別不出來我這是什麼封裝的
記得條十進位 右上角 才可以匹配偏移量

![image](https://hackmd.io/_uploads/By8G3zHSJx.png)

修改為0x0 ,ctrl+s
![image](https://hackmd.io/_uploads/BJaL3zrHkg.png)

![image](https://hackmd.io/_uploads/B1DoTGSSye.png)

很好 你的程式就變木馬了xdd

cache.dir 應該對應到的是 nuitka 動態解壓縮的一些行為，
不過其實最開始我也有想過替換掉 mingw gcc 的 cflags -flto 或者一些方法不過還是沒辦法躲過eset檢測。

