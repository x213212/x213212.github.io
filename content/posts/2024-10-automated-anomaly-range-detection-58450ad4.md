---
title: "Automated Anomaly Range Detection"
date: "2024-10-27T02:29:00.002+08:00"
updated: "2024-10-27T02:29:19.795+08:00"
permalink: "/2024/10/automated-anomaly-range-detection.html"
original_url: "https://x8795278.blogspot.com/2024/10/automated-anomaly-range-detection.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-1172298622246231097"
tags: ["Python"]
layout: post
---

![](https://hackmd.io/_uploads/ryhqlhclkg.png)

假設在沒有模擬器的情況下要找出兩個elf 相同的compiler 但是不同cflags 的指令差異這部分在面對未知的benchmark 要實現自動找尋異常區間這部分可能要耗費大量的人力，這部分假設要做成自動化大概有幾個想法

大概步驟是想要根據benchmark 的時間長度與要檢測硬體counter 變化來下手，人工debug也大概流程是這樣概念，只不過透過 sim 來模擬找出 Hotspots 通常模擬越準就只能跑很久，我這邊是單純想透過 python 控制 gdb 使用硬體來找尋異常區間

![image](https://hackmd.io/_uploads/rkEnxh5e1x.png)
這邊是放大第一次分歧點的cycle 區間
![image](https://hackmd.io/_uploads/ryhqlhclkg.png)

記得編譯的時候要下-g
這樣我透過addr2line可以顯示 benchmark 行號

大概想法是找到第一個分歧點後不斷地放大該分歧點，就可以找到可疑區間了

#findarea.sh
核心主要是rollback.py,這邊要注意的是 max_rollback_time會決定放大區間的粗細程度

```sh
# 定義相同的變數
elf="linear_alg-sml-50x50_version1noinlinenobit.elf"
elf2="linear_alg-sml-50x50_version2noinlinenobit.elf"
outputname="roughly"
# [lm:cache]
rollback_type="lm"
rollback_mode=1
max_rollback_time=100
scop=40
ipaddress="-----:1111" # gdb ipaddress 
# auto find area
python3 rollback.py --elf $elf --type $rollback_type --mode $rollback_mode --max_rollback_time $max_rollback_time --ipaddress $ipaddress
python3 rollback.py --elf $elf2 --type $rollback_type --mode $rollback_mode --max_rollback_time $max_rollback_time --ipaddress $ipaddress
python3 draw2.py --elf $elf --elf2 $elf2  --outputname $outputname
rollback_mode=0
outputname="reduction"
python3 rollback.py --elf $elf --type $rollback_type --mode $rollback_mode --max_rollback_time $max_rollback_time --ipaddress $ipaddress --scop $scop
python3 rollback.py --elf $elf2 --type $rollback_type --mode $rollback_mode --max_rollback_time $max_rollback_time --ipaddress $ipaddress --scop $scop
python3 draw2.py --elf $elf --elf2 $elf2  --outputname $outputname
python3 rollback.py --elf $elf --type $rollback_type --mode $rollback_mode --max_rollback_time $max_rollback_time --ipaddress $ipaddress --scop $scop
python3 rollback.py --elf $elf2 --type $rollback_type --mode $rollback_mode --max_rollback_time $max_rollback_time --ipaddress $ipaddress --scop $scop
python3 draw2.py --elf $elf --elf2 $elf2  --outputname $outputname
```

# rollback.py
這邊大概透過控制thread 來中斷 gdb 可以達到 timeout 的功能，當然也可以拿來當定時中斷
```python
import os
import time
from datetime import datetime
import subprocess
import getpass
import argparse
def killfpga():
    fpga = 'ps -ef | grep '+getpass.getuser()+' | grep "gdb"  | awk '+'{print $2}'+' | xargs kill -9'
    status , result = subprocess.getstatusoutput(fpga)
    if(status!= 0):
        return -1 , result 
    return 0,result

def get_fpga_ouput():
    fpga = 'bash ./rollback.sh'
    status , result = subprocess.getstatusoutput(fpga)
    # debug output log
    print(result)
    if(status!= 0):
        return -1 , result 
    return 0,result 

def read_and_eval_elf(elf_name):
    # 確認檔案是否存在
    if not os.path.isfile(elf_name):
        print(f"Error: File {elf_name} does not exist.")
        return None
    try:
        # 讀取 ELF 檔案內容
        with open(elf_name, 'r') as file:
            content = file.read()
        
        # 將字串轉換成真正的 list
        result_list = list(eval(content))
        return result_list
    
    except Exception as e:
        print(f"Error occurred while reading or evaluating the file: {e}")
        return None
        
start = None
upper_limit = None
# 解析命令行參數
parser = argparse.ArgumentParser(description='Cycle comparison analysis script')
parser.add_argument('--elf', type=str, required=True, help='Path to the first ELF file')
parser.add_argument('--type', type=str, required=True, help='Analysis type')
parser.add_argument('--mode', type=int, required=True, help='Analysis mode')
parser.add_argument('--ipaddress', type=str, required=True, help='ipaddress')
# if mode = 0
parser.add_argument('--start', type=float, required=False, default=0.31619, help='Start value for the analysis')
parser.add_argument('--upper_limit', type=float, required=False, default=1.4, help='Upper limit value for the analysis')
# if mode = 1
parser.add_argument('--scop', type=float, required=False, default=1.4, help='scop')
parser.add_argument('--max_rollback_time', type=int, required=False, default=100, help='max rollback_time')

args = parser.parse_args()

if args.mode == 0:
    start = args.start
    upper_limit = args.upper_limit 
    scop_cut = float(args.upper_limit - args.start) / args.scop
    print(scop_cut)
    file_path ="reduction.txt"
    if os.path.exists(file_path):
        gescop =read_and_eval_elf(file_path)
        print(gescop )
        start =gescop[0]
        if start <=0.2 :
            start = start +0.2
        upper_limit = gescop[1]
        scop_cut = float(upper_limit - start) / args.scop
        print("update new scop")
        print(scop_cut)
    
    
gdb_script_path = 'gdb_script.gdb'
with open(gdb_script_path, 'r') as file:
    gdb_script_content = file.read()

gdb_script_content = gdb_script_content.replace('{ipaddress}', args.ipaddress)
if(args.type == "lm"):
    gdb_script_content = gdb_script_content.replace('{type}', "so ./test_eembc-V5_LM.gdb")
elif(args.type == "cache"):
      gdb_script_content = gdb_script_content.replace('{type}', "so ./test_eembc-V5_cache.gdb")
gdb_script_content = gdb_script_content.replace('{elf_name}', args.elf)

with open(gdb_script_path.replace("gdb_script","gdb_script_ex"), 'w') as file:
    file.write(gdb_script_content)
################
rollbacktime = 100
decrease = args.mode
# decrease == 0

# start -> start+1 .... upper_limit
# decrease ==1
# 10 -> 5 -> 2.5 ->1.25-> 0.625 ... until Counter ==0 or Other termination conditions
# Other termination conditions
stop_conditions = 0
################

# init
measurementcount_path = 'lastmeasurementcount.txt'
expectedtime_path = 'expectedtime.txt'
if(decrease == 1 ):
    if os.path.isfile(measurementcount_path) :
        os.remove(measurementcount_path)
    if os.path.isfile(expectedtime_path) :
        os.remove(expectedtime_path)
else :
    if os.path.isfile(measurementcount_path) :
        os.remove(measurementcount_path)
    if os.path.isfile(expectedtime_path) :
        os.remove(expectedtime_path)
    f = open(expectedtime_path, "a")
    f.write(str(start))
    f.close()
    f = open(measurementcount_path, "a")
    f.write(str(0))
    f.close()
    
# start 
now_pc = ""
record = []
for i in range(rollbacktime):
    killfpga()
    last_expectedtime = start
    prev_detect_count = 0    
    detect_count = 0
    print("Rollback Times:\t" , i+1)
    print(record)
    if(i+1 >=args.max_rollback_time):
        break
    st = time.time()
    status , result = get_fpga_ouput()

    # get fpga output
    for line in result.splitlines():
        # Detect Counter
        if(line.find("Cycles : "  )>= 0):
            x = line.split(":")
            detect_count =int (x[1])
            print("========")
            print("Detect Counter:\t" , detect_count)
            if( os.path.exists(measurementcount_path) == True):
                f = open(measurementcount_path, 'r')
                prev_detect_count = int(f.read())
                if(decrease == 0 and prev_detect_count == 0):
                    prev_detect_count  = detect_count
                f.close()
            else:
                # record first detect_count 
                f = open(measurementcount_path, "a")
                f.write(str(detect_count))
                f.close()
        # Detect Thread Rollback time
        if(line.find("last expectedtime"  )>= 0):
            x = line.split(":")
            last_expectedtime = float(x[1].strip())
        # Detect Pc Address
        if(line.find("PC   :"  )>= 0):
            x = line.split(":")
            print(x)
            now_pc = str(x[1].strip())

    et = time.time()
    elapsed_time = et - st
    elapsed_time = round(float(elapsed_time), 5)  
    
    # Prepare Next measurement time
    expectedtime = 0.0
    if( (os.path.exists(expectedtime_path) == True)): 
        f = open(expectedtime_path, 'r')
        get_output =f.read()
        f.close()
        # setting expectedtime
        if(get_output != ''):
            expectedtime = float(get_output)
        else:
            print("No Expectedtime")
            break
        
        if(last_expectedtime != 0):
            # detect_count equal 0 End of measurement
            if(detect_count == 0):
                break
            # Other termination conditions
            if(detect_count <stop_conditions ):
                break
            if(float(detect_count/prev_detect_count) >30):
                print("drop ! Measuring interval oscillation")
                if(start):
                    start = start +0.1
                    scop_cut = float(upper_limit - start) / args.scop
                    print("update new scop too short")
                    print(scop_cut)
                    f = open(expectedtime_path, "w")
                    f.write(str(start))
                    f.close()
                continue
            elif(decrease == 0 and float(detect_count/prev_detect_count) >4):
                print("drop ! Measuring interval oscillation")
                start = start +0.1
                scop_cut = float(upper_limit - start) / args.scop
                print("update new scop too short")
                print(scop_cut)
                f = open(expectedtime_path, "w")
                f.write(str(start))
                f.close()
                continue
            else:
                # No Exceptions Update detect_count to lastmeasurementcount.txt
                if(os.path.exists(measurementcount_path) == True):
                    os.remove(measurementcount_path)
                f = open(measurementcount_path, "a")
                f.write(str(detect_count))
                f.close()

                if(os.path.exists(expectedtime_path) == True):                    
                    os.remove(expectedtime_path)

                record.append([now_pc,detect_count,prev_detect_count,float(prev_detect_count/detect_count),last_expectedtime])
                print("Last Expectedtime:\t",last_expectedtime)
                f = open(expectedtime_path, "a")
                # Determine the next measurement time update expectedtime to last_expectedtime
                if(decrease == 0):
                    f.write(str( float(last_expectedtime)+scop_cut))
                else:
                    f.write(str( float(last_expectedtime)/2))
                f.close()
                if(decrease == 0):
                    if(last_expectedtime >=upper_limit):
                        break
          
    else:
        # first rollback time
        f = open(expectedtime_path, "a")
        # f.write(str( float(elapsed_time)/2))
        f.write(str( float(elapsed_time)))
        f.close()

f = open((args.elf).replace(".elf",".log"), "w")
f.write(str( record))
f.close()
import os
import time
from datetime import datetime
import subprocess
import getpass
import argparse
def killfpga():
    fpga = 'ps -ef | grep '+getpass.getuser()+' | grep "gdb"  | awk '+'{print $2}'+' | xargs kill -9'
    status , result = subprocess.getstatusoutput(fpga)
    if(status!= 0):
        return -1 , result 
    return 0,result

def get_fpga_ouput():
    fpga = 'bash ./rollback.sh'
    status , result = subprocess.getstatusoutput(fpga)
    # debug output log
    print(result)
    if(status!= 0):
        return -1 , result 
    return 0,result 

def read_and_eval_elf(elf_name):
    # 確認檔案是否存在
    if not os.path.isfile(elf_name):
        print(f"Error: File {elf_name} does not exist.")
        return None
    try:
        # 讀取 ELF 檔案內容
        with open(elf_name, 'r') as file:
            content = file.read()
        
        # 將字串轉換成真正的 list
        result_list = list(eval(content))
        return result_list
    
    except Exception as e:
        print(f"Error occurred while reading or evaluating the file: {e}")
        return None
        
start = None
upper_limit = None
# 解析命令行參數
parser = argparse.ArgumentParser(description='Cycle comparison analysis script')
parser.add_argument('--elf', type=str, required=True, help='Path to the first ELF file')
parser.add_argument('--type', type=str, required=True, help='Analysis type')
parser.add_argument('--mode', type=int, required=True, help='Analysis mode')
parser.add_argument('--ipaddress', type=str, required=True, help='ipaddress')
# if mode = 0
parser.add_argument('--start', type=float, required=False, default=0.31619, help='Start value for the analysis')
parser.add_argument('--upper_limit', type=float, required=False, default=1.4, help='Upper limit value for the analysis')
# if mode = 1
parser.add_argument('--scop', type=float, required=False, default=1.4, help='scop')
parser.add_argument('--max_rollback_time', type=int, required=False, default=100, help='max rollback_time')

args = parser.parse_args()

if args.mode == 0:
    start = args.start
    upper_limit = args.upper_limit 
    scop_cut = float(args.upper_limit - args.start) / args.scop
    print(scop_cut)
    file_path ="reduction.txt"
    if os.path.exists(file_path):
        gescop =read_and_eval_elf(file_path)
        print(gescop )
        start =gescop[0]
        if start <=0.2 :
            start = start +0.2
        upper_limit = gescop[1]
        scop_cut = float(upper_limit - start) / args.scop
        print("update new scop")
        print(scop_cut)
    
    
gdb_script_path = 'gdb_script.gdb'
with open(gdb_script_path, 'r') as file:
    gdb_script_content = file.read()

gdb_script_content = gdb_script_content.replace('{ipaddress}', args.ipaddress)
if(args.type == "lm"):
    gdb_script_content = gdb_script_content.replace('{type}', "so ./test_eembc-V5_LM.gdb")
elif(args.type == "cache"):
      gdb_script_content = gdb_script_content.replace('{type}', "so ./test_eembc-V5_cache.gdb")
gdb_script_content = gdb_script_content.replace('{elf_name}', args.elf)

with open(gdb_script_path.replace("gdb_script","gdb_script_ex"), 'w') as file:
    file.write(gdb_script_content)
################
rollbacktime = 100
decrease = args.mode
# decrease == 0

# start -> start+1 .... upper_limit
# decrease ==1
# 10 -> 5 -> 2.5 ->1.25-> 0.625 ... until Counter ==0 or Other termination conditions
# Other termination conditions
stop_conditions = 0
################

# init
measurementcount_path = 'lastmeasurementcount.txt'
expectedtime_path = 'expectedtime.txt'
if(decrease == 1 ):
    if os.path.isfile(measurementcount_path) :
        os.remove(measurementcount_path)
    if os.path.isfile(expectedtime_path) :
        os.remove(expectedtime_path)
else :
    if os.path.isfile(measurementcount_path) :
        os.remove(measurementcount_path)
    if os.path.isfile(expectedtime_path) :
        os.remove(expectedtime_path)
    f = open(expectedtime_path, "a")
    f.write(str(start))
    f.close()
    f = open(measurementcount_path, "a")
    f.write(str(0))
    f.close()
   
```

# rollback.sh
```sh
riscv64-unknown-elf-gdb -x 'gdb_script_ex.gdb'
```
# gdb_script.gdb
以該gdb script 作為 templete 生成 gdb_script_ex.gdb
```
target remote {ipaddress}
file {elf_name}
set pagination off
{type}
so ./BTB_miss_rate_V5.gdb
python import gdb; gdb.execute("source rollbacktimer.py")
cont
cont
so ./print_V5_BTB_embench.gdb
```
# gdb_script_ex.gdb
細部的gdb script 就看不同人怎麼設計了 看你要印出什麼硬體counter 進行夾擠
```
target remote ---------:1111
file blacks-sml-n500v20-sp_test2.elf
set pagination off
so ./test_eembc-V5_LM.gdb
so ./BTB_miss_rate_V5.gdb
cont
cont
so ./print_V5_BTB_embench.gdb
```

# rollbacktimer.py
這邊負責控制rollback.py 的每次中斷時間
```python
import time
import gdb
import os
import sched
import signal
import asyncio
from threading import Timer
import threading
expectedtime =0.0
first = 0

file_path = 'expectedtime.txt'

def send_signal():
    # print(f"Current process ID: {pid}")
    print("thread")
    time.sleep(round(float(expectedtime), 5)  )
    print("\nlast expectedtime : "+ str(round(float(expectedtime), 5)))
    gdb.execute("interrupt")

if(os.path.exists(file_path) == True):
    f = open(file_path, 'r')
    expectedtime = float(f.read())
    f.close()
    t = threading.Thread(target=send_signal)
    t.start()
    
print("hello word")

```

# draw
這邊還是要注意
```python
import subprocess
import matplotlib.pyplot as plt
import itertools
from collections import defaultdict
import os 
import argparse
def read_and_eval_elf(elf_name):
    # 確認檔案是否存在
    if not os.path.isfile(elf_name):
        print(f"Error: File {elf_name} does not exist.")
        return None
    
    try:
        # 讀取 ELF 檔案內容
        with open(elf_name, 'r') as file:
            content = file.read()
        
        # 將字串轉換成真正的 list
        result_list = list(eval(content))
        return result_list
    
    except Exception as e:
        print(f"Error occurred while reading or evaluating the file: {e}")
        return None
        

parser = argparse.ArgumentParser(description='Cycle comparison analysis script')
parser.add_argument('--elf', type=str, required=True, help='Path to the first ELF file')
parser.add_argument('--elf2', type=str, required=True, help='Path to the first ELF file')
parser.add_argument('--outputname', type=str, required=True, help='outputname')

args = parser.parse_args()

# 定義 ELF 文件的路徑
elf_name = args.elf
elf_name2 = args.elf2

# 假設這些是我們要查找的地址（從之前的數據中提取）
data1 =read_and_eval_elf(elf_name.replace(".elf",".log"))
data2 =read_and_eval_elf(elf_name2.replace(".elf",".log"))
print(elf_name.replace(".elf",".log"))
data1 = sorted(data1, key=lambda x: x[1])
data2 = sorted(data2, key=lambda x: x[1])
# 提取函數名稱的函數
def get_function_name(elf_file, address):
    try:
        result = subprocess.run(['/NOBACKUP/sqa3/NFSTest/build-astversion2/build-toolchain/linux/nds64le-elf-mculib-v5/bin/riscv64-elf-addr2line', '-e', elf_file, address, '-f', '-p'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return 'Unknown'
    except FileNotFoundError:
        return 'addr2line not found'

# 提取每個地址的函數名稱
def extract_function_names(elf_file, data):
    function_names = []
    for entry in data:
        address = entry[0]
        function_name = get_function_name(elf_file, address)
        function_names.append((function_name, entry[1], address, entry[4]))
    return function_names

# 提取每個地址的函數名稱
functions_version1 = extract_function_names(elf_name, data1)
functions_version2 = extract_function_names(elf_name2, data2)

# 比較兩個 ELF 文件中的函數
print("\nFunctions from version1 ELF:")
for func in functions_version1:
    print(f"Function: {func[0]}, Cycles: {func[1]}, PC Address: {func[2]}, Seconds: {func[3]}")

print("\nFunctions from version2 ELF:")
for func in functions_version2:
    print(f"Function: {func[0]}, Cycles: {func[1]}, PC Address: {func[2]}, Seconds: {func[3]}")

# 尋找分歧點
end_early_points = []
discrepancy_points = []
last_discrepancy_index = -1
for i in range(min(len(functions_version1), len(functions_version2))):
    cycle_version1 = functions_version1[i][1]
    cycle_version2 = functions_version2[i][1]
    if cycle_version1 == cycle_version2:
        end_early_points.append((functions_version1[i][0], functions_version1[i][3], functions_version2[i][3]))
    elif abs(cycle_version1 - cycle_version2) / max(cycle_version1, cycle_version2) >= 0.015:
        if not discrepancy_points or discrepancy_points[-1][1] != cycle_version1:
            discrepancy_points.append((functions_version1[i][0], functions_version1[i][3], functions_version2[i][3]))
        last_discrepancy_index = i

# 優化分歧點，只保留第一個和最後一個分歧點
if discrepancy_points:
    first_discrepancy_point = discrepancy_points[0]
    last_discrepancy_point = discrepancy_points[-1]
    # 檢查最後一個分歧點是否所有 cycle 都相同，若相同則取第一個相同的最後分歧點
    for i in range(last_discrepancy_index, len(functions_version1)):
        if functions_version1[i][1] == functions_version2[i][1]:
            last_discrepancy_point = (functions_version1[i][0], functions_version1[i][3], functions_version2[i][3])
        else:
            break
    discrepancy_points = [first_discrepancy_point, last_discrepancy_point]

# 打印分歧點的時間區間
if discrepancy_points:
    first_discrepancy_time = discrepancy_points[0][1]
    last_discrepancy_time = discrepancy_points[-1][2]
    print(f"\nTime Interval of Discrepancy: [{first_discrepancy_time}, {last_discrepancy_time}]")
    f = open("reduction.txt", "w")
    f.write(str([float(first_discrepancy_time), float(last_discrepancy_time)]))
    f.close()

# 繪製比較圖表
x = range(len(functions_version1))
cycles_version1 = [func[1] for func in functions_version1]
cycles_version2 = [func[1] for func in functions_version2]

plt.figure(figsize=(16, 10))

# 使用相同顏色表示相同函數名稱
color_cycle = itertools.cycle(['red', 'orange', 'green', 'blue', 'purple', 'cyan', 'magenta', 'lime', 'pink', 'teal', 'violet'])
function_colors = {}

# 初始化函數顏色
all_functions = set([f[0] for f in functions_version1] + [f[0] for f in functions_version2])
for func in all_functions:
    if func not in function_colors:
        function_colors[func] = next(color_cycle)

min_length = min(len(functions_version1), len(functions_version2))

for i in range(min_length - 1):
    func_version1 = functions_version1[i][0]
    func_version2 = functions_version2[i][0]
    color_version1 = function_colors[func_version1]
    color_version2 = function_colors[func_version2]
    plt.plot([i, i + 1], [functions_version1[i][1], functions_version1[i + 1][1]], color=color_version1)
    plt.plot([i, i + 1], [functions_version2[i][1], functions_version2[i + 1][1]], color=color_version2)

    if i == 0 or func_version1 != functions_version1[i - 1][0]:
        if functions_version1[i][3] != 'N/A':
            plt.text(i, functions_version1[i][1], f"{func_version1} ({functions_version1[i][2]}, {functions_version1[i][3]}s)", fontsize=8, color='black', rotation=45, verticalalignment='top')

    if i == 0 or func_version2 != functions_version2[i - 1][0]:
        plt.text(i, functions_version2[i][1], f"{func_version2} ({functions_version2[i][2]}, {functions_version2[i][3]}s)", fontsize=8, color='black', rotation=45, verticalalignment='bottom')

    # 標註分歧點
    if abs(functions_version1[i][1] - functions_version2[i][1]) / max(functions_version1[i][1], functions_version2[i][1]) >= 0.15:
        plt.scatter(i, max(functions_version1[i][1], functions_version2[i][1]), color='red', marker='x', s=100)

plt.xlabel('Function Index')
plt.ylabel('Cycle Count')
plt.title('Function Cycle Count Comparison Between version1 and version2')
plt.grid(True)
plt.tight_layout()

plt.savefig(f'{args.outputname}.png', format='png', bbox_inches='tight')
plt.close()
```

