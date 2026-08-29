---
title: "pwn double free&use after free"
date: "2022-12-10T23:48:00.002+08:00"
updated: "2023-02-04T02:47:55.615+08:00"
permalink: "/2022/12/pwn-double-free-after-free.html"
original_url: "https://x8795278.blogspot.com/2022/12/pwn-double-free-after-free.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6433741938216726922"
tags: ["angr", "double free", "use after free"]
layout: post
---

![](https://i.imgur.com/Rr8YQSE.png)

# double free & use-after-free
https://bbs.pediy.com/thread-266757.htm
前天在寫llvm pass又重新看到的angr
想起以前看到有人寫
https://xz.aliyun.com/t/7275
 double free & use-after-free漏洞挖掘，他這種寫法可能導致z3求解狀態過多
https://bbs.pediy.com/thread-266757.htm
在第二題的地方有寫如何避開過多狀態，來改裝一下
# testfile
```c
#include <stdio.h>
#include <stdlib.h>

char bss[0x10]={0};
int main(int argc, char const *argv[])
{
    char buf[0x10]={0};
    int times=4;
    unsigned long *ptr=&bss;
    while(times--)
    {
        puts("input:");
        read(0,buf,8);
        switch(atoi(buf))
        {
            case 1: 
                puts("malloc!");
                *ptr=malloc(0x30);
                // printf("%p,%p,%p\n", &ptr,ptr,*ptr);
                break;
            case 2:
                if (*ptr)
                {
                    puts("free!");
                    free(*ptr);

                }
                else
                {
                    puts("fail to free");
                    return;
                }

                break;
            case 3:
                if (*ptr)
                {
                    puts("edit!");
                    read(0,*ptr,8);

                }
                else
                {
                    puts("fail to edit");
                    return;
                }
                break;

            case 4:
                if (*ptr)
                {
                    puts("show!");
                    write(1,*ptr,8);

                }
                else
                {
                    puts("fail to show");
                    return;
                }
                break;

        }

    }

    return 0;
}
```
# python
```python
# Before you begin, here are a few notes about these capture-the-flag
# challenges.
#
# Each binary, when run, will ask for a password, which can be entered via stdin
# (typing it into the console.) Many of the levels will accept many different
# passwords. Your goal is to find a single password that works for each binary.
#
# If you enter an incorrect password, the program will print "Try again." If you
# enter a correct password, the program will print "Good Job."
#
# Each challenge will be accompanied by a file like this one, named
# "scaffoldXX.py". It will offer guidance as well as the skeleton of a possible
# solution. You will have to edit each file. In some cases, you will have to
# edit it significantly. While use of these files is recommended, you can write
# a solution without them, if you find that they are too restrictive.
#
# Places in the scaffoldXX.py that require a simple substitution will be marked
# with three question marks (???). Places that require more code will be marked
# with an ellipsis (...). Comments will document any new concepts, but will be
# omitted for concepts that have already been covered (you will need to use
# previous scaffoldXX.py files as a reference to solve the challenges.) If a
# comment documents a part of the code that needs to be changed, it will be
# marked with an exclamation point at the end, on a separate line (!).
import angr
import claripy
from angr.sim_type import SimTypeTop,SimTypeLength
from angr import sim_options as so
from angrmanagement.utils.graph import to_supergraph
from binascii import b2a_hex
class malloc_hook(angr.procedures.libc.malloc.malloc):
    def run(self, sim_size):
        self.argument_types = {0: SimTypeLength(self.state.arch)}
        self.return_type = self.ty_ptr(SimTypeTop(sim_size))
        addr=self.state.heap._malloc(sim_size)
        size=self.state.solver.eval(sim_size)
        if "malloc_list" in self.state.globals:
            malloc_list=self.state.globals["malloc_list"]
        else:
            self.state.globals["malloc_list"]={}
            malloc_list=self.state.globals["malloc_list"]
        malloc_list[addr]=size
        return addr
class free_hook(angr.procedures.libc.free.free):
    def run(self, ptr):
        self.argument_types = {0: self.ty_ptr(SimTypeTop())}
        f_ptr=self.state.solver.eval(ptr)
        if "free_list" in self.state.globals:
            free_list=self.state.globals["free_list"]
            if f_ptr in free_list:
                print("double free:")
                print("stdout:\n",self.state.posix.dumps(1))
                print("stdin:\n",self.state.posix.dumps(0))
        else:
            self.state.globals["free_list"]={}
            free_list=self.state.globals["free_list"]
            if "malloc_list" in self.state.globals:
                malloc_list=self.state.globals["malloc_list"]
                if f_ptr in malloc_list:
                    free_list[f_ptr]=malloc_list[f_ptr]
        return self.state.heap._free(ptr)
'''
获取避免执行到的地址列表
关键！可以大大提高angr符号执行速度
'''
test = []

def get_avoid_list(cfg, start, target):
    print("cfg")
    # print(len(start))
    avoid_list=[]
    if start.addr == target:
        return (True,[])
  
    if len(list(cfg.successors(start))) == 0:
        return (False, [start.addr])
    else:
      if start not in test:
        test.append(start)
        succs = list(cfg.successors(start))  
        if len(succs) == 1:
            # print("cfg")
            print(start.addr)
            # avoid_list.append(start.addr)
    
            can_reach_target, avoid_list = get_avoid_list(cfg, succs[0], target)
            if can_reach_target:
                return (True, avoid_list)
            else:
                avoid_list.append(start.addr)
                return (False, avoid_list)
        elif len(succs) == 2:
            # print("cfg2")
            print(start.addr)
            
            can_reach_target0, avoid_list0 = get_avoid_list(cfg, succs[0], target)
          
            can_reach_target1, avoid_list1 = get_avoid_list(cfg, succs[1], target)

            if can_reach_target0 and can_reach_target1:
                return (True, [])
            elif not can_reach_target0 and not can_reach_target1:
                avoid_list = avoid_list0 + avoid_list1
                avoid_list.append(start.addr)
                return (False, avoid_list)
            else:
                avoid_list = avoid_list0 + avoid_list1
                return (True, avoid_list)
        else:
            
            exit(0)
      return (False, [])    
    return (False, [])    

def check_addr(state,act):
    addr=act.addr.ast
    if isinstance(addr,int):
        return addr
    if isinstance(addr,claripy.ast.bv.BV):
        return state.solver.eval(addr)
    return 0

def Check_UAF_R(state):
    if "free_list" not in state.globals:
        if "before_free" in state.globals:
            before_free=state.globals["before_free"]
        else:
            state.globals["before_free"]=[]
            before_free=state.globals["before_free"]
        action_now=reversed(state.history.actions.hardcopy)
        for act in action_now:
            if act not in before_free:
                before_free.append(act)
    else:
        before_free=state.globals["before_free"]
        action_now=reversed(state.history.actions.hardcopy)
        action=[i for i in action_now if i not in before_free]

        malloc_list=state.globals["malloc_list"]
        free_list=state.globals["free_list"]

        for act in action:
            if act.type=='mem' and act.action=='read' :
                addr=check_addr(state,act)
                if addr==0:
                    print("error addr:",act.addr)
                    break

                for f in free_list:
                    if f==addr:
                        print("\n[========find a UAF read========]")
                        print("[UAF-R]stdout:")
                        print(state.posix.dumps(1))
                        print("[UAF-R]trigger arbitrary read input:")
                        print(state.posix.dumps(0))
                        break

def Check_UAF_W(state):
    if "free_list" not in state.globals:
        if "before_free" in state.globals:
            before_free=state.globals["before_free"]
        else:
            state.globals["before_free"]=[]
            before_free=state.globals["before_free"]
        action_now=reversed(state.history.actions.hardcopy)
        for act in action_now:
            if act not in before_free:
                before_free.append(act)

    else:
        before_free=state.globals["before_free"]
        action_now=reversed(state.history.actions.hardcopy)
        action=[i for i in action_now if i not in before_free]

        malloc_list=state.globals["malloc_list"]
        free_list=state.globals["free_list"]

        for act in action:
            if act.type=='mem' and act.action=='write' :
                addr=check_addr(state,act)
                if addr==0:
                    print("error:",act.addr)
                    break

                for f in free_list:
                    if f==addr:
                        print("\n[========find a UAF write========]")
                        print("[UAF-W]stdout:")
                        print(state.posix.dumps(1))
                        print("[UAF-W]trigger arbitrary write input:")
                        print(state.posix.dumps(0))
                        break

'''
对目标函数进行符号执行，求解到达call system执行所需要的输入
'''
def explore_func(proj, target_func, target_block, target_cfg):
    new_list=[]
    payload_list = []
    avoid_list=[]
    for x in  target_cfg.nodes :
      new_list.append(x)
    try:
      # print(type(new_list[0]))
      can_reach_target, avoid_list = get_avoid_list(target_cfg,new_list[0], target_block)
      print(avoid_list)
      state = proj.factory.call_state(target_func)
      simgr = proj.factory.simgr(state,save_unconstrained=True)
  
      simgr.use_technique(angr.exploration_techniques.DFS())
      extras = {so.REVERSE_MEMORY_NAME_MAP, so.TRACK_ACTION_HISTORY,so.ZERO_FILL_UNCONSTRAINED_MEMORY}
      state=proj.factory.entry_state(add_options=extras)
      simgr.explore(find=target_block, avoid=avoid_list)
   
      while simgr.active:
        
        for act in simgr.active:
          Check_UAF_R(act)
          Check_UAF_W(act)

      
      # for found in simgr.found:
      #     payload_list.append(found.posix.dumps(0))
    except Exception as ex:
      print(ex)
      # exit(0)

    return payload_list

def get_system_addr(cfg):
    for func_addr in cfg.functions:
        func = cfg.functions.get(func_addr)
        if func.name == 'free':
            return func_addr+16
    return None

def explore_payload(bin_path):
    
    proj = angr.Project(bin_path, load_options={'auto_load_libs': False})
    
    proj_cfg = proj.analyses.CFGFast()
    proj.hook_symbol('malloc',malloc_hook())
    proj.hook_symbol('free',free_hook())
    system_addr = get_system_addr(proj_cfg)
    if system_addr == None:
        return []
    print(f'Found system function in {hex(system_addr)}.')
    payload_list=[]
    for func_addr in proj_cfg.functions:
            func = proj_cfg.functions.get(func_addr)
            cfg = func.transition_graph
            cfg = to_supergraph(cfg)
            print(func )
            for node in cfg.nodes:
                block = proj.factory.block(node.addr)
                for inst in block.capstone.insns:
                    print(inst)
                    print(inst.op_str == hex(system_addr))
                  
                    if inst.mnemonic == 'call' :
                      print(inst.mnemonic )
                      print(inst.op_str)
                    if inst.mnemonic == 'call' and inst.op_str == hex(system_addr):
                        target_func = func_addr
                        target_block = block.addr
                        target_cfg = cfg
                        print(f'Found target function in {hex(target_func)}')
                        print(f'Found target block in {hex(target_block)}')
                        payload_list += explore_func(proj, target_func, target_block, target_cfg)
      
    return payload_list
 
  
if __name__ == '__main__':
    filename="./a.out"
    # p = angr.Project(filename,auto_load_libs=False)#
    payload_list = explore_payload(filename)
    # print(payload_list)
    # for payload in payload_list:
    #     print('payload=' +  b2a_hex(payload).decode())
    # p.hook_symbol('malloc',malloc_hook())
    # p.hook_symbol('free',free_hook())
    # extras = {so.REVERSE_MEMORY_NAME_MAP, so.TRACK_ACTION_HISTORY,so.ZERO_FILL_UNCONSTRAINED_MEMORY}
    # state=p.factory.entry_state(add_options=extras)
    # simgr = p.factory.simulation_manager(state,save_unconstrained=True)
    # simgr.use_technique(angr.exploration_techniques.Spiller())
    # while simgr.active:
    #     simgr.step()
```
比較要注意的是main進入點，有稍微小改,
整體思考方向就是，先透過cfg然後走訪第一個cfg的節點，從這些節點找到free的節點，然後記錄不可能到達free路徑的節點
這樣可以大大的減少求解所需要的路徑。
這樣不到一分鐘就可以求解五個以上的double free的路徑，當然實際狀況要靠這個去找到double free和use after free,還是可能遇到路徑過多的情況狀況，可能要找新的方式去避免，改天有想到再來改一下.
![](https://i.imgur.com/Rr8YQSE.png)
缺點的話，我目前還是在wsl記憶體超過4g就會掛了
![](https://i.imgur.com/CgrOL9n.png)
記憶體狀態應該還可以更小不過，路徑狀態可能性太多了!

