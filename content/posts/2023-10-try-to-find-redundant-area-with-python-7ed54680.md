---
title: "Try to find the redundant area with the Python gdb (riscv)"
date: "2023-10-15T11:17:00.003+08:00"
updated: "2023-10-15T11:17:51.100+08:00"
permalink: "/2023/10/try-to-find-redundant-area-with-python.html"
original_url: "https://x8795278.blogspot.com/2023/10/try-to-find-redundant-area-with-python.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3151652932668095333"
tags: ["RISC-V", "vector"]
layout: post
---

![](https://hackmd.io/_uploads/HyZHdA_WT.png)

# Try to find the redundant area with the Python gdb (riscv)
大概想統計出某個區域內的pc address所使用的 register 的使用次數與alias的register,和記錄所有regiser 在某個區域內的所有regiser的 狀態，先假設相同compiler來說在編譯加了某些option 導致某段code做不好的話，應該在某個區域內的register殘留的狀態應該有做好的register來的多.

# python
```python
import struct
import sys
import os
import argparse
import gdb
import subprocess

filepath="log.txt"
if os.path.isfile(filepath):
    os.remove(filepath)
f = open(filepath, "w")
f.close()

# Redirect the output stream to the log.txt file.
# sys.stdout = f

backup_cycle = 0
last_inst = 0
prev_addrees = 0
possiable_address = []
record ={}

# gdb.execute("source test_eembc-V5_LM.gdb", to_string=True)
# gdb.execute("source BTB_miss_rate_V5.gdb", to_string=True)

# gdb.execute("b demo/dhry_1.c:145 ")
# gdb.Breakpoint("demo/dhry_1.c:145")
# gdb.Breakpoint("foo at demo/dhry_1.c:145")
# gdb.Breakpoint('7')
# bp = gdb.Breakpoint("foo", gdb.BP_BREAKPOINT, temporary=True)
# gdb.Breakpoint.delete(gdb.lookup_breakpoint("my_breakpoint"))

gdb.execute("set logging redirect on")
gdb.execute("set logging file log.txt")
gdb.execute("set logging on")

init_bp = ["*0x11a4"]

print("start check")
times = globals()['times']
 
current_area =50
current_start=0
dual_issue=0
no_dual_issue=0
long_cycle=0
same_inst={}
rrecord_register_valid_by_register={}
rrecord_register_valid_by_register_count = {}
rrecord_pcaddress_register_status = {}
record_register_valid = {}
alias_chain = {}
history_get_valid_list=[]
active_range = {}
start_pc_address = ""
end_pc_address = ""
find_loop = -1
for bp in init_bp:
    gdb.Breakpoint(bp)
    gdb.execute("c")
    backpc = 0
    vtype = 0
    vtype_pc = 0
    
    for i in range(int(times)):
        # gdb.execute("nexti")
        gdb.execute("ni")

        # print address info
        frame = gdb.selected_frame()

        print("PC address:", hex(frame.pc()))
   
        if find_loop == -1:
            start_pc_address =str(hex(frame.pc()))
            if(start_pc_address not in active_range ):
                active_range[start_pc_address] = []
            find_loop = 0

        disassembly = gdb.execute("disassemble 0x{:x},+1".format(frame.pc()), to_string=True)
        opcode = disassembly.split()[2]
        arr = disassembly.split('=> ')
        get_asm_register = str(arr[1].split(" ")[1]).replace("\t"," ").split(" ")[-1].replace("\nEnd","")
        get_asm_register_list = get_asm_register.split(",")
        get_valid_list = []
        process_register = []
        for register in get_asm_register_list:
            offset = 0
            if "(" in register:
                result = register[register.index("("):].replace("(","").replace(")","")
                offset = register[:register.index("(")]
                # print(offset)
            else:
                result = register
            if result not in process_register:
                if not str(result).isdigit() and  str(result).find("-") <0 and  str(result).find("0x") <0 and  str(result).find("ret") <0 and  str(result).find("e") <0  and  str(result).find("m") <0 and  str(result).find("ta") <0 and  str(result).find("tu") <0:
                    if(str(offset).isdigit() and offset != 0):
                        check_invalid_register = gdb.execute("p /x $" + result +" + "+ str(offset), to_string=True).replace("\t"," ")
                        get_register = register
                        get_register_value = str( check_invalid_register.split("=")[1]).strip().strip()
                        check_pass =1

                    else:
                        check_invalid_register = gdb.execute("info register " + result, to_string=True).replace("\t"," ")
                        get_register = check_invalid_register.split(" ")[0]
                        if check_invalid_register.find("Invalid") < 0 :
                            get_register_value =  str(  check_invalid_register).replace("\n","").replace(str( get_register).strip() , "").strip()
                            check_pass =1

                    if check_pass == 1:
                        
                        record_register_valid[str(hex(frame.pc()))] = str(  check_invalid_register)
                        rrecord_register_valid_by_register[str( get_register).strip()] = str(  get_register_value)
                   
                        pc_address =  str(hex(frame.pc())).strip()
                        if pc_address not in rrecord_pcaddress_register_status:
                            rrecord_pcaddress_register_status[pc_address] = []
                        find_pc_address_record =0

                        for get_pc_address_register_status in rrecord_pcaddress_register_status[pc_address] :
                            for get_recored_register in get_pc_address_register_status:
                                if (get_register in get_recored_register):
                                    find_pc_address_record = 1

                        if find_pc_address_record == 0:
                            rrecord_pcaddress_register_status[pc_address].append({str(get_register):[]})
                            # print(rrecord_pcaddress_register_status[pc_address])

                        for get_pc_address_register_status in rrecord_pcaddress_register_status[pc_address] :
                            # print(get_pc_address_register_status)
                            for get_recored_register in get_pc_address_register_status:
                                if (str(get_register) in get_recored_register):
                                    get_pc_address_register_status[str(get_recored_register)].append (str( get_register_value))
                                    
                                    # print(str(get_register))
                                    # for get_register_status in  get_pc_address_register_status[str(get_recored_register)]:
                                    #     print(get_register_status)
   
 
                        # rrecord_pcaddress_register_status [str(hex(frame.pc()))] = collect_memory
                        if( str( get_register).strip() in rrecord_register_valid_by_register_count):
                            rrecord_register_valid_by_register_count[ str( get_register).strip()] += 1
                        else:
                            rrecord_register_valid_by_register_count[ str( get_register)] = 1
                        get_valid_list.append(str( get_register).strip())
                        if(str(get_register).strip() not in history_get_valid_list):
                            history_get_valid_list.append(str( get_register).strip())
                process_register.append (result)

            if  str(result).find("ta") >=0 or  str(result).find("tu") >=0:
                check_invalid_register = gdb.execute("p $vtype" , to_string=True).replace("\t"," ")
                now_vtype =str( check_invalid_register.split("=")[1]).strip()
                now_vtype_pc = frame.pc()
               
                if vtype == 0:
                    vtype = now_vtype
                    vtype_pc = now_vtype_pc
                if(vtype_pc != now_vtype_pc ):
                    if(vtype == now_vtype):
                        print("vtype same PC prev_address:", hex(vtype_pc))
                        print("vtype same PC prev_vtype:", vtype)
                        print("vtype same PC now_address:", hex(now_vtype_pc))
                        print("vtype same PC now_vtype:", now_vtype)
                    else:
                        print("vtype diff PC prev_address:", hex(vtype_pc))
                        print("vtype diff PC prev_vtype:", vtype)
                        print("vtype diff PC now_address:", hex(now_vtype_pc))
                        print("vtype diff PC now_vtype:", now_vtype)
                        vtype = now_vtype
                        vtype_pc = now_vtype_pc  
                else:
                    vtype = now_vtype
                    vtype_pc = now_vtype_pc

                    
        no_duplication_case_list = []
        for y in get_valid_list:
            for x in rrecord_register_valid_by_register:
                if(x != y ):
                    if(str(rrecord_register_valid_by_register[str(x)])  == str(rrecord_register_valid_by_register[str(y)])):
                        if(str("\t"+x+" same value " + y ) not in no_duplication_case_list):
                            if(str("\t"+y+" same value " + x ) not in no_duplication_case_list):
                                # print("\t"+x+" same value " + y )
                                alias_chain[x] = y
                                alias_chain[y] = x
                                
                                no_duplication_case_list.append (str("\t"+x+" same value " + y ) )

        if( frame.pc() <= backpc):
            print("find loop")
            if find_loop == 0 :
                find_loop = 1
           
            print("===========================")
        
            for x in history_get_valid_list:
                print(str(x)+ " usages : " + str( rrecord_register_valid_by_register_count[x]))
               
            print("alias")
            print("===========================")
            for x in history_get_valid_list:
                test = []
                test.append(x)
                find = x
                while True:
                    if ( find  in alias_chain):
                        if ( alias_chain[find] not in test):
                            test.append(alias_chain[find])
                            find = alias_chain[find]
                        else:
                            break
                    else:
                            break
                if(len(test)>=1):
                    print("========")
                    print("register : " + x)
                    # print("alias 3")
                    print(test)
                    for y in test:
                        print(str(y)+ " usages : " + str( rrecord_register_valid_by_register_count[y]))
            alias_chain = {}
            history_get_valid_list= []
                    
            record_register_valid = {}
            rrecord_register_valid_by_register= {}
            rrecord_register_valid_by_register_count = {}
            backpc = frame.pc()
            print("============next basic block===============")
        
        backpc = frame.pc()
        if find_loop == 1:
            if end_pc_address not in active_range[start_pc_address]:
                active_range[start_pc_address].append (end_pc_address)
            find_loop = -1
        end_pc_address = str(hex(frame.pc()))

print("print range")
active_range = dict(sorted(active_range.items(), key=lambda item: int(item[0], 16)))
for x in active_range:
    print(x)
    print(active_range[x])
    
print("print record")
print(type(rrecord_pcaddress_register_status))
rrecord_pcaddress_register_status = dict(sorted(rrecord_pcaddress_register_status.items(), key=lambda item: int(item[0], 16)))
no_duplication_case_list = []
rootcause_range = {}
for get_pc_address in rrecord_pcaddress_register_status :
    for get_pc_address2 in rrecord_pcaddress_register_status :
        # print(get_pc_address)
        check_range = 0
        for search_active_range in active_range:
            if  (int(get_pc_address2, 16) >int(search_active_range, 16)  ):
                check_active_range = active_range[search_active_range]
                for range in check_active_range:
                    a= int(search_active_range, 16)
                    b= int(get_pc_address, 16)
                    c= int(get_pc_address2, 16)
                    d= int(range, 16) 
                    if( d> b and b >a and d > a ):
                        if(d > c and c >a and d > a ):
                            check_range=1
                            break
            if check_range == 1:
                break
                     
        if(check_range == 1):
            if(get_pc_address != get_pc_address2):
                for get_pc_address_register_status in rrecord_pcaddress_register_status[get_pc_address] :
                    for twt in get_pc_address_register_status:
                        for get_pc_address_register_status2 in rrecord_pcaddress_register_status[get_pc_address2] :
                            for twt2 in get_pc_address_register_status2:
                                if(twt != twt2):
          
                                    check_same = get_pc_address_register_status[twt] == get_pc_address_register_status2[twt2]
                   
                                    if(str("\t"+get_pc_address+" same value " + get_pc_address2 ) not in no_duplication_case_list):
                                        if(str("\t"+get_pc_address2+" same value " + get_pc_address ) not in no_duplication_case_list):
                                            if (check_same) :
                                                # print(c > b and b >a and c > a )
                                                # print(active_range[search_active_range])
                                                # print(search_active_range)
                                                # print(get_pc_address2)
                                                # print(range)
                                                if (search_active_range+ "-" + range ) not in rootcause_range :
                                                    rootcause_range[str( (search_active_range+ "-" + range) )] = 1
                                                else :
                                                    rootcause_range[str( (search_active_range+ "-" + range) )] +=1
                                                # if ("(" + get_pc_address+ ","+ get_pc_address2 + ") in "+search_active_range+ "-" + range ) not in rootcause_range :
                                                #     rootcause_range[str( ("(" + get_pc_address+ ","+ get_pc_address2 + ") in "+search_active_range+ "-" + range ))] = 1
                                                # else :
                                                #     rootcause_range[str( ("(" + get_pc_address+ ","+ get_pc_address2 + ") in "+search_active_range+ "-" + range ) )] +=1
                                                print("same value same block")
                                                print(get_pc_address)
                                                print(twt)
                                                print(get_pc_address_register_status[twt])
                                                print(get_pc_address2)
                                                print(twt2)
                                                print(get_pc_address_register_status2[twt2])
                                                no_duplication_case_list.append (str("\t"+get_pc_address+" same value " + get_pc_address2 ) )
print("=================================")
print("rootcause_range")
for range in rootcause_range:
    print("range:")
    print(range)
    print("redunent count:")
    print(rootcause_range[range])

gdb.execute("set logging off")
gdb.execute("interrupt")

```

# run
```bash
python exec(open('gdb_si_by_time copy.py').read(), {'times': '40000'})
```
跑個四萬次 ni,
由於要考慮register最多可以傳播到多遠，所以要定義active_range ,而在最後比對不同的 pc address 中, register的所有記憶體狀態就可以找到某些register是否有alias關係.
```bash
PC address: 0x11a6
PC address: 0x11aa
PC address: 0x11ae
PC address: 0x11b0
PC address: 0x11b2
PC address: 0x11b4
PC address: 0x11b6
PC address: 0x11b8
PC address: 0x11ba
PC address: 0x11bc
PC address: 0x11be
PC address: 0x11c0
PC address: 0x11c2
PC address: 0x11c4
PC address: 0x11c6
PC address: 0x11c8
PC address: 0x11cc
PC address: 0x11d0
PC address: 0x11d2
PC address: 0x11d6
PC address: 0x11d8
PC address: 0x11da
PC address: 0x11dc
PC address: 0x11de
PC address: 0x11e0
PC address: 0x11e4
PC address: 0x11e8
PC address: 0x11ec
PC address: 0x11ee
PC address: 0x11f0
PC address: 0x11f4
vtype diff PC prev_address: 0x11e4
vtype diff PC prev_vtype: 192
vtype diff PC now_address: 0x11f4
vtype diff PC now_vtype: 200
PC address: 0x11f8
PC address: 0x11fc
vtype diff PC prev_address: 0x11f4
vtype diff PC prev_vtype: 200
vtype diff PC now_address: 0x11fc
vtype diff PC now_vtype: 199
PC address: 0x1200
PC address: 0x1202
PC address: 0x1206
vtype diff PC prev_address: 0x11fc
vtype diff PC prev_vtype: 199
vtype diff PC now_address: 0x1206
vtype diff PC now_vtype: 200
PC address: 0x120a
PC address: 0x120e
PC address: 0x1212
PC address: 0x1216
PC address: 0x1218
PC address: 0x121c
PC address: 0x121e
PC address: 0x1222
PC address: 0x1224
PC address: 0x11ec
find loop
===========================
t0 usages : 2
t1 usages : 2
ra usages : 1
120(sp) usages : 1
s0 usages : 1
112(sp) usages : 1
s1 usages : 3
104(sp) usages : 1
s2 usages : 4
96(sp) usages : 1
s3 usages : 1
88(sp) usages : 1
s4 usages : 4
80(sp) usages : 1
s5 usages : 3
72(sp) usages : 1
s6 usages : 1
64(sp) usages : 1
s7 usages : 2
56(sp) usages : 1
s8 usages : 1
48(sp) usages : 1
s9 usages : 2
40(sp) usages : 1
s10 usages : 2
32(sp) usages : 1
s11 usages : 2
24(sp) usages : 1
sp usages : 1
a0 usages : 8
a1 usages : 5
a2 usages : 7
a3 usages : 4
v8 usages : 2
a4 usages : 1
a5 usages : 8
v1 usages : 3
alias
===========================
========
register : t0
['t0']
t0 usages : 2
========
register : t1
['t1']
t1 usages : 2
========
register : ra
['ra']
ra usages : 1
========
register : 120(sp)
['120(sp)']
120(sp) usages : 1
========
register : s0
['s0']
s0 usages : 1
========
register : 112(sp)
['112(sp)']
112(sp) usages : 1
========
register : s1
['s1', 's6']
s1 usages : 3
s6 usages : 1
========
register : 104(sp)
['104(sp)']
104(sp) usages : 1
========
register : s2
['s2', 'a2']
s2 usages : 4
a2 usages : 7
========
register : 96(sp)
['96(sp)']
96(sp) usages : 1
========
register : s3
['s3']
s3 usages : 1
========
register : 88(sp)
['88(sp)']
88(sp) usages : 1
========
register : s4
['s4', 'a5', 's11']
s4 usages : 4
a5 usages : 8
s11 usages : 2
========
register : 80(sp)
['80(sp)']
80(sp) usages : 1
========
register : s5
['s5']
s5 usages : 3
========
register : 72(sp)
['72(sp)']
72(sp) usages : 1
========
register : s6
['s6', 's1']
s6 usages : 1
s1 usages : 3
========
register : 64(sp)
['64(sp)']
64(sp) usages : 1
========
register : s7
['s7']
s7 usages : 2
========
register : 56(sp)
['56(sp)']
56(sp) usages : 1
========
register : s8
['s8']
s8 usages : 1
========
register : 48(sp)
['48(sp)']
48(sp) usages : 1
========
register : s9
['s9']
s9 usages : 2
========
register : 40(sp)
['40(sp)']
40(sp) usages : 1
========
register : s10
['s10']
s10 usages : 2
========
register : 32(sp)
['32(sp)']
32(sp) usages : 1
========
register : s11
['s11', 'a5']
s11 usages : 2
a5 usages : 8
========
register : 24(sp)
['24(sp)']
24(sp) usages : 1
========
register : sp
['sp']
sp usages : 1
========
register : a0
['a0', 'a1']
a0 usages : 8
a1 usages : 5
========
register : a1
['a1', 'a0']
a1 usages : 5
a0 usages : 8
========
register : a2
['a2', 's2']
a2 usages : 7
s2 usages : 4
========
register : a3
['a3', 'a0', 'a1']
a3 usages : 4
a0 usages : 8
a1 usages : 5
========
register : v8
['v8']
v8 usages : 2
========
register : a4
['a4']
a4 usages : 1
========
register : a5
['a5', 's11']
a5 usages : 8
s11 usages : 2
========
register : v1
['v1']
v1 usages : 3
```

active_range
當pc address發生折返的情況會記錄折返點
```python
print range
0x1368
['0x1390', '0x13ac', '0x1446']
0x5c0
['0x610']
0x5cc
['0x5d4']
0x1466
['0x1498']
0x27dc
['0x2894']
0x1bc
['0x1de']
0x158a
['0x15c8']
0x1502
['0x156e']
0x5d0
['0x610']
0x11a6
['0x1224']
0x14c
['0x1224', '0x212']
0x13ee
['0x1446']
0x13f6
['0x1446', '0x1456', '0x14a4']
0x25c
['0x262', '0x25c']
0x1b0
['0x1de']
0x15f2
['0x1628', '0x28a2', '0x2894']
0x135e
['0x1390']
0x130a
['0x1350', '0x1390']
0x176
['0x60e']
0x244
['0x248']
0x59e
['0x1224', '0x604', '0x60e']
0x1480
['0x14a4', '0x1498']
0x150a
['0x156e', '0x157e', '0x15c8']
0x11ee
['0x1224', '0x127a']
0x1298
['0x12c8']
0x1470
['0x14a4', '0x1498', '0x14b4', '0x156e']
0x12aa
['0x12c8', '0x12d8', '0x1350']
0x123e
['0x127a', '0x12c8']
0x15a4
['0x15c8', '0x15d8', '0x1628']
0x5c2
['0x5e8']
```

print record
在檢查不同pc address的時候，會額外檢查pc address是否在合理的 active_range
```bash
<class 'dict'>
same value same block
0x121c
a0
['0x21fa9c 2226844', '0x21faae 2226862', '0x21fac0 2226880', '0x21fad2 2226898', '0x21fae4 2226916', '0x21faf6 2226934', '0x21fb08 2226952', '0x21fb1a 2226970', '0x21fb2c 2226988', '0x21fa9c 2226844', '0x21faae 2226862', '0x21fac0 2226880', '0x21fad2 2226898', '0x21fae4 2226916', '0x21faf6 2226934', '0x21fb08 2226952', '0x21fb1a 2226970', '0x21fb2c 2226988', '0x21fa9c 2226844', '0x21faae 2226862', '0x21fac0 2226880', '0x21fad2 2226898', '0x21fae4 2226916', '0x21faf6 2226934', '0x21fb08 2226952', '0x21fb1a 2226970', '0x21fb2c 2226988', '0x21fa9c 2226844', '0x21faae 2226862', '0x21fac0 2226880', '0x21fad2 2226898', '0x21fae4 2226916', '0x21faf6 2226934', '0x21fb08 2226952', '0x21fb1a 2226970', '0x21fb2c 2226988']
0x1212
a3
['0x21fa9c 2226844', '0x21faae 2226862', '0x21fac0 2226880', '0x21fad2 2226898', '0x21fae4 2226916', '0x21faf6 2226934', '0x21fb08 2226952', '0x21fb1a 2226970', '0x21fb2c 2226988', '0x21fa9c 2226844', '0x21faae 2226862', '0x21fac0 2226880', '0x21fad2 2226898', '0x21fae4 2226916', '0x21faf6 2226934', '0x21fb08 2226952', '0x21fb1a 2226970', '0x21fb2c 2226988', '0x21fa9c 2226844', '0x21faae 2226862', '0x21fac0 2226880', '0x21fad2 2226898', '0x21fae4 2226916', '0x21faf6 2226934', '0x21fb08 2226952', '0x21fb1a 2226970', '0x21fb2c 2226988', '0x21fa9c 2226844', '0x21faae 2226862', '0x21fac0 2226880', '0x21fad2 2226898', '0x21fae4 2226916', '0x21faf6 2226934', '0x21fb08 2226952', '0x21fb1a 2226970', '0x21fb2c 2226988']
same value same block
0x121c
a0
['0x21fa9c 2226844', '0x21faae 2226862', '0x21fac0 2226880', '0x21fad2 2226898', '0x21fae4 2226916', '0x21faf6 2226934', '0x21fb08 2226952', '0x21fb1a 2226970', '0x21fb2c 2226988', '0x21fa9c 2226844', '0x21faae 2226862', '0x21fac0 2226880', '0x21fad2 2226898', '0x21fae4 2226916', '0x21faf6 2226934', '0x21fb08 2226952', '0x21fb1a 2226970', '0x21fb2c 2226988', '0x21fa9c 2226844', '0x21faae 2226862', '0x21fac0 2226880', '0x21fad2 2226898', '0x21fae4 2226916', '0x21faf6 2226934', '0x21fb08 2226952', '0x21fb1a 2226970', '0x21fb2c 2226988', '0x21fa9c 2226844', '0x21faae 2226862', '0x21fac0 2226880', '0x21fad2 2226898', '0x21fae4 2226916', '0x21faf6 2226934', '0x21fb08 2226952', '0x21fb1a 2226970', '0x21fb2c 2226988']
0x120e
a1
['0x21fa9c 2226844', '0x21faae 2226862', '0x21fac0 2226880', '0x21fad2 2226898', '0x21fae4 2226916', '0x21faf6 2226934', '0x21fb08 2226952', '0x21fb1a 2226970', '0x21fb2c 2226988', '0x21fa9c 2226844', '0x21faae 2226862', '0x21fac0 2226880', '0x21fad2 2226898', '0x21fae4 2226916', '0x21faf6 2226934', '0x21fb08 2226952', '0x21fb1a 2226970', '0x21fb2c 2226988', '0x21fa9c 2226844', '0x21faae 2226862', '0x21fac0 2226880', '0x21fad2 2226898', '0x21fae4 2226916', '0x21faf6 2226934', '0x21fb08 2226952', '0x21fb1a 2226970', '0x21fb2c 2226988', '0x21fa9c 2226844', '0x21faae 2226862', '0x21fac0 2226880', '0x21fad2 2226898', '0x21fae4 2226916', '0x21faf6 2226934', '0x21fb08 2226952', '0x21fb1a 2226970', '0x21fb2c 2226988']
```

最後再輸出的時候，將前面的active_range內發生的記憶體相似的情況給複製下來
![](https://hackmd.io/_uploads/HyZHdA_WT.png)

```bash
=================================
rootcause_range
range:
0x27dc-0x2894
redunent count:
6
range:
0x15f2-0x28a2
redunent count:
55
range:
0x130a-0x1350
redunent count:
14
range:
0x11a6-0x1224
redunent count:
39
range:
0x1502-0x156e
redunent count:
22
range:
0x15f2-0x1628
redunent count:
21
range:
0x1470-0x156e
redunent count:
5
range:
0x13f6-0x14a4
redunent count:
2
range:
0x135e-0x1390
redunent count:
1
range:
0x15a4-0x1628
redunent count:
18
range:
0x12aa-0x1350
redunent count:
8
range:
0x123e-0x12c8
redunent count:
1
range:
0x14c-0x1224
redunent count:
25
range:
0x5c0-0x610
redunent count:
1
range:
0x11ee-0x127a
redunent count:
79
range:
0x1368-0x1446
redunent count:
28
```

例如慢慢看可以看出在某個區間內的a1和a3可以替換成一個register
before
```asm
       11d0: 8a2a      c.mv       s4,a0 
       11d2: 00151493  slli       s1,a0,0x1 
       11d6: 8d2e      c.mv       s10,a1 
       11d8: 8db2      c.mv       s11,a2 
       11da: 8cb6      c.mv       s9,a3 
       11dc: 8bb2      c.mv       s7,a2 
       11de: 8532      c.mv       a0,a2 
       11e0: 00000913  li         s2,0 
       11e4: 0c807ad7  vsetvli    s5,zero,e16,m1,ta,ma 
       11e8: 5e074457  vmv.v.x    v8,a4 
       11ec: 85aa      c.mv       a1,a0 
       11ee: 8652      c.mv       a2,s4 
       11f0: 00050693  mv         a3,a0 
       11f4: 0c7677d7  vsetvli    a5,a2,e8,mf2,ta,ma 
       11f8: 0205d087  vle16.v    v1,(a1) 
       11fc: 0c807ad7  vsetvli    s5,zero,e16,m1,ta,ma 
       1200: 8e1d      c.sub      a2,a5 
       1202: 021400d7  vadd.vv    v1,v1,v8 
       1206: 0c87f057  vsetvli    zero,a5,e16,m1,ta,ma 
       120a: 0206d0a7  vse16.v    v1,(a3) 
       120e: 0af585db  lea.h      a1,a1,a5 
       1212: 0af686db  lea.h      a3,a3,a5 
       1216: fe79      c.bnez     a2,0x11f4 <matrix_test+0x50> 
```
after
```asm
       11d0: 8a2a      c.mv       s4,a0 
       11d2: 00151493  slli       s1,a0,0x1 
       11d6: 8d2e      c.mv       s10,a1 
       11d8: 8db2      c.mv       s11,a2 
       11da: 8cb6      c.mv       s9,a3 
       11dc: 8bb2      c.mv       s7,a2 
       11de: 8532      c.mv       a0,a2 
       11e0: 00000913  li         s2,0 
       11e4: 0c807ad7  vsetvli    s5,zero,e16,m1,ta,ma 
       11e8: 5e074457  vmv.v.x    v8,a4 
       11ec: 85aa      c.mv       a1,a0 
       11ee: 8652      c.mv       a2,s4 
       11f4: 0c7677d7  vsetvli    a5,a2,e8,mf2,ta,ma 
       11f8: 0205d087  vle16.v    v1,(a1) 
       11fc: 0c807ad7  vsetvli    s5,zero,e16,m1,ta,ma 
       1200: 8e1d      c.sub      a2,a5 
       1202: 021400d7  vadd.vv    v1,v1,v8 
       1206: 0c87f057  vsetvli    zero,a5,e16,m1,ta,ma 
       120a: 0206d0a7  vse16.v    v1,(a1) 
       120e: 0af585db  lea.h      a1,a1,a5 
       1216: fe79      c.bnez     a2,0x11f4 <matrix_test+0x50> 
```
如何影響編譯後的 asm ,可以找出 build 成 .o的那段c code在改成輸出成.s 再用as 去合成.o ,就可以異動 asm 的順序和code gen ,在異動後coremark 的 crc check 也沒出錯.

