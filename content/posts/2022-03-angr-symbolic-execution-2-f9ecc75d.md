---
title: "angr symbolic execution (2)"
date: "2022-03-19T22:04:00.006+08:00"
updated: "2022-08-30T14:06:34.287+08:00"
permalink: "/2022/03/angr-symbolic-execution-2.html"
original_url: "https://x8795278.blogspot.com/2022/03/angr-symbolic-execution-2.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-906020896102912676"
tags: ["angr"]
layout: post
---

![](https://i.imgur.com/c8SMfCs.png)

# angr
![](https://i.imgur.com/c8SMfCs.png)

```bash
root@HOME-X213212:~# tree angr_ctf/dist/
angr_ctf/dist/
├── 00_angr_find
├── 01_angr_avoid
├── 02_angr_find_condition
├── 03_angr_symbolic_registers
├── 04_angr_symbolic_stack
├── 05_angr_symbolic_memory
├── 06_angr_symbolic_dynamic_memory
├── 07_angr_symbolic_file
├── 08_angr_constraints
├── 09_angr_hooks
├── 10_angr_simprocedures
├── 11_angr_sim_scanf
├── 12_angr_veritesting
├── 13_angr_static_binary
├── 14_angr_shared_library
├── 15_angr_arbitrary_read
├── 16_angr_arbitrary_write
├── 17_angr_arbitrary_jump
├── lib14_angr_shared_library.so
├── scaffold00.py
├── scaffold01.py
├── scaffold02.py
├── scaffold03.py
├── scaffold04.py
├── scaffold05.py
├── scaffold06.py
├── scaffold07.py
├── scaffold08.py
├── scaffold09.py
├── scaffold10.py
├── scaffold11.py
├── scaffold12.py
├── scaffold13.py
├── scaffold14.py
├── scaffold15.py
├── scaffold16.py
└── scaffold17.py

0 directories, 37 files
```
# apt install checksec
```
apt install checksec
```
```bash
(env) root@HOME-X213212:~/angr_ctf/14_angr_shared_library# checksec --file=./14_angr_shared_library
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      Symbols         FORTIFY Fortified       Fortifiable     FILE
Partial RELRO   Canary found      NX enabled    No PIE          No RPATH   No RUNPATH   74) Symbols       No    0               2               ./14_angr_shared_library
```
# 10_angr_simprocedures
09 和 10 算是 我們手動構造新的fucntion
![](https://i.imgur.com/xjfN29p.png)
09還是算抽象，10算是另外一種方式讓使用者撰寫腳本更容易一點
![](https://i.imgur.com/Nwu0K4d.png)
![](https://i.imgur.com/7cRXu71.png)
可以看到我們的流程圖的路徑變得這麼多，意謂著angr要嘗試去走訪這些路徑找到唯一解變得越來越困難
不過我們還是先f5
![](https://i.imgur.com/TRyX4ia.png)
![](https://i.imgur.com/m9MUKwK.png)
目標路徑在這裡
![](https://i.imgur.com/KM91k2W.png)
```python
# This challenge is similar to the previous one. It operates under the same
# premise that you will have to replace the check_equals_ function. In this
# case, however, check_equals_ is called so many times that it wouldn't make
# sense to hook where each one was called. Instead, use a SimProcedure to write
# your own check_equals_ implementation and then hook the check_equals_ symbol
# to replace all calls to scanf with a call to your SimProcedure.
#
# You may be thinking:
#   Why can't I just use hooks? The function is called many times, but if I hook
#   the address of the function itself (rather than the addresses where it is
#   called), I can replace its behavior everywhere. Furthermore, I can get the
#   parameters by reading them off the stack (with memory.load(regs.esp + xx)),
#   and return a value by simply setting eax! Since I know the length of the
#   function in bytes, I can return from the hook just before the 'ret'
#   instruction is called, which will allow the program to jump back to where it
#   was before it called my hook.
# If you thought that, then congratulations! You have just invented the idea of
# SimProcedures! Instead of doing all of that by hand, you can let the already-
# implemented SimProcedures do the boring work for you so that you can focus on
# writing a replacement function in a Pythonic way.
# As a bonus, SimProcedures allow you to specify custom calling conventions, but
# unfortunately it is not covered in this CTF.

import angr
import claripy
import sys

def main(argv):
  path_to_binary = "/home/angr/angr-dev/test/10_angr_simprocedures" 
  project = angr.Project(path_to_binary)

  initial_state = project.factory.entry_state(
    add_options = { angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
                    angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS}
  )

  # Define a class that inherits angr.SimProcedure in order to take advantage
  # of Angr's SimProcedures.
  class ReplacementCheckEquals(angr.SimProcedure):
    # A SimProcedure replaces a function in the binary with a simulated one
    # written in Python. Other than it being written in Python, the function
    # acts largely the same as any function written in C. Any parameter after
    # 'self' will be treated as a parameter to the function you are replacing.
    # The parameters will be bitvectors. Additionally, the Python can return in
    # the ususal Pythonic way. Angr will treat this in the same way it would
    # treat a native function in the binary returning. An example:
    #
    # int add_if_positive(int a, int b) {
    #   if (a >= 0 && b >= 0) return a + b;
    #   else return 0;
    # }
    #
    # could be simulated with...
    #
    # class ReplacementAddIfPositive(angr.SimProcedure):
    #   def run(self, a, b):
    #     if a >= 0 and b >=0:
    #       return a + b
    #     else:
    #       return 0
    #
    # Finish the parameters to the check_equals_ function. Reminder:
    # int check_equals_AABBCCDDEEFFGGHH(char* to_check, int length) { ...
    # (!)
    def run(self, to_check, length):
      # We can almost copy and paste the solution from the previous challenge.
      # Hint: Don't look up the address! It's passed as a parameter.
      # (!)
      user_input_buffer_address = to_check
      user_input_buffer_length = length

      # Note the use of self.state to find the state of the system in a 
      # SimProcedure.
      user_input_string = self.state.memory.load(
        user_input_buffer_address,
        user_input_buffer_length
      )

      check_against_string = "ORSDDWXHZURJRBDH"
      
      # Finally, instead of setting eax, we can use a Pythonic return statement
      # to return the output of this function. 
      # Hint: Look at the previous solution.
      return claripy.If(
      user_input_string == check_against_string, 
      claripy.BVV(1, 32), 
      claripy.BVV(0, 32)
    )

  # Hook the check_equals symbol. Angr automatically looks up the address 
  # associated with the symbol. Alternatively, you can use 'hook' instead
  # of 'hook_symbol' and specify the address of the function. To find the 
  # correct symbol, disassemble the binary.
  # (!)
  check_equals_symbol = "check_equals_ORSDDWXHZURJRBDH" # :string
  project.hook_symbol(check_equals_symbol, ReplacementCheckEquals())

  simulation = project.factory.simgr(initial_state)

  def is_successful(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    print(stdout_output)
    return b'Good Job.' in stdout_output

  def should_abort(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return b'Try again.' in stdout_output  # :boolean

  simulation.explore(find=is_successful, avoid=should_abort)

  if simulation.found:
    solution_state = simulation.found[0]

    solution = solution_state.posix.dumps(0)
    print(solution)
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)

```
![](https://i.imgur.com/Xeo5IVS.png)

# 11_angr_sim_scanf
替換掉scanf 裡面的 argument 為 symbolic
```
# This time, the solution involves simply replacing scanf with our own version,
# since Angr does not support requesting multiple parameters with scanf.

import angr
import claripy
import sys

def main(argv):
  path_to_binary = "/home/angr/angr-dev/test/11_angr_sim_scanf" 
  project = angr.Project(path_to_binary)

  initial_state = project.factory.entry_state(
    add_options = { angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
                    angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS}
  )

  class ReplacementScanf(angr.SimProcedure):
    # Finish the parameters to the scanf function. Hint: 'scanf("%u %u", ...)'.
    # (!)
    def run(self, format_string, scanf0_address, scanf1_address):
      # Hint: scanf0_address is passed as a parameter, isn't it?
      scanf0 = claripy.BVS('scanf0', 32)
      scanf1 = claripy.BVS('scanf1', 32)
      # ...

      # The scanf function writes user input to the buffers to which the 
      # parameters point.
      self.state.memory.store(scanf0_address, scanf0, endness=project.arch.memory_endness)
      self.state.memory.store(scanf1_address, scanf1, endness=project.arch.memory_endness)
      # ...

      # Now, we want to 'set aside' references to our symbolic values in the
      # globals plugin included by default with a state. You will need to
      # store multiple bitvectors. You can either use a list, tuple, or multiple
      # keys to reference the different bitvectors.
      # (!)
      self.state.globals['solution'] = (scanf0,scanf1)

  scanf_symbol = "__isoc99_scanf"
  project.hook_symbol(scanf_symbol, ReplacementScanf())

  simulation = project.factory.simgr(initial_state)

  def is_successful(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    print(stdout_output)
    return b'Good Job.' in stdout_output

  def should_abort(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return b'Try again.' in stdout_output  # :boolean

  simulation.explore(find=is_successful, avoid=should_abort)

  if simulation.found:
    solution_state = simulation.found[0]

    # Grab whatever you set aside in the globals dict.
    stored_solutions0 = solution_state.globals['solution']
    # for x in stored_solutions0:
    solution = solution_state.solver.eval(stored_solutions0[0])
    solution2 = solution_state.solver.eval(stored_solutions0[1])
    # solution =stored_solutions0

    print('{} {}'.format(solution, solution2))
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)

```
![](https://i.imgur.com/Dnxpo4C.png)

# 12_angr_sim_scanf
參考:https://blog.csdn.net/A951860555/article/details/119102789#12_angr_veritesting_540
因此這道題就是使用veritesting參數來緩解路徑爆炸，原理簡單引用如下：從高層面來說，有兩種符號執行，一種是動態符號執行（Dynamic Symbolic Execution，簡稱 DSE），另一種是靜態符號執行（Static Symbolic Execution，簡稱 SSE）。動態符號執行會去執行程序然後為每一條路徑生成一個表達式。而靜態符號執行將程序轉換為表達式，每個表達式都表示任意條路徑的屬性。基於路徑的 DSE 在生成表達式上引入了很多的開銷，然而生成的表達式很容易求解。而 SSE 雖然生成表達式容易，但是表達式難求解。 veritesting 就是在這二者中做權衡，使得能夠在引入低開銷的同時，生成較易求解的表達式。
```python
# When you construct a simulation manager, you will want to enable Veritesting:
# project.factory.simgr(initial_state, veritesting=True)
# Hint: use one of the first few levels' solutions as a reference.

import angr
import claripy
import sys

def main(argv):
  path_to_binary = "/home/angr/angr-dev/test/12_angr_veritesting" 
  project = angr.Project(path_to_binary)

  initial_state = project.factory.entry_state(
    add_options = {}
  )

  simulation = project.factory.simgr(initial_state,veritesting=True)

  def is_successful(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    print(stdout_output)
    return b'Good Job.' in stdout_output

  def should_abort(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return b'Try again.' in stdout_output  # :boolean

  simulation.explore(find=is_successful, avoid=should_abort)

  if simulation.found:
    solution_state = simulation.found[0]
    solution = solution_state.posix.dumps(sys.stdin.fileno())
    print(solution)
    
    print('{}'.format(solution))
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)
```
![](https://i.imgur.com/3NMnp95.png)

# 13_angr_static_binary

https://www.anquanke.com/post/id/231460
![](https://i.imgur.com/UmrUdP0.png)
![](https://i.imgur.com/CgSdwxU.png)
![](https://i.imgur.com/wZjLjCb.png)
![](https://i.imgur.com/kp8RANk.png)
```python
project.hook(0x804ED40, angr.SIM_PROCEDURES['libc']['printf']())
    project.hook(0x804ED80, angr.SIM_PROCEDURES['libc']['scanf']())
    project.hook(0x804F350, angr.SIM_PROCEDURES['libc']['puts']())
    project.hook(0x8048D10, angr.SIM_PROCEDURES['glibc']['__libc_start_main']())
```

```python
# This challenge is the exact same as the first challenge, except that it was
# compiled as a static binary. Normally, Angr automatically replaces standard
# library functions with SimProcedures that work much more quickly.
#
# To solve the challenge, manually hook any standard library c functions that
# are used. Then, ensure that you begin the execution at the beginning of the
# main function. Do not use entry_state.
#
# Here are a few SimProcedures Angr has already written for you. They implement
# standard library functions. You will not need all of them:
# angr.SIM_PROCEDURES['libc']['malloc']
# angr.SIM_PROCEDURES['libc']['fopen']
# angr.SIM_PROCEDURES['libc']['fclose']
# angr.SIM_PROCEDURES['libc']['fwrite']
# angr.SIM_PROCEDURES['libc']['getchar']
# angr.SIM_PROCEDURES['libc']['strncmp']
# angr.SIM_PROCEDURES['libc']['strcmp']
# angr.SIM_PROCEDURES['libc']['scanf']
# angr.SIM_PROCEDURES['libc']['printf']
# angr.SIM_PROCEDURES['libc']['puts']
# angr.SIM_PROCEDURES['libc']['exit']
#
# As a reminder, you can hook functions with something similar to:
# project.hook(malloc_address, angr.SIM_PROCEDURES['libc']['malloc']())
#
# There are many more, see:
# https://github.com/angr/angr/tree/master/angr/procedures/libc
#
# Additionally, note that, when the binary is executed, the main function is not
# the first piece of code called. In the _start function, __libc_start_main is
# called to start your program. The initialization that occurs in this function
# can take a long time with Angr, so you should replace it with a SimProcedure.
# angr.SIM_PROCEDURES['glibc']['__libc_start_main']
# Note 'glibc' instead of 'libc'.

import angr
import claripy
import sys

def main(argv):
    bin_path = "/home/angr/angr-dev/test/13_angr_static_binary"
    project = angr.Project(bin_path)

    initial_state = project.factory.entry_state()

    simulation = project.factory.simgr(initial_state)

    project.hook(0x804ED40, angr.SIM_PROCEDURES['libc']['printf']())
    project.hook(0x804ED80, angr.SIM_PROCEDURES['libc']['scanf']())
    project.hook(0x804F350, angr.SIM_PROCEDURES['libc']['puts']())
    project.hook(0x8048D10, angr.SIM_PROCEDURES['glibc']['__libc_start_main']())

    def is_successful(state):
        stdout_output = state.posix.dumps(1)
        return b"Good Job." in stdout_output

    def should_abort(state):
        stdout_output = state.posix.dumps(1)
        return b"Try again." in stdout_output

    simulation.explore(find = is_successful, avoid = should_abort)

    if simulation.found:
        solution_state = simulation.found[0]
        print(solution_state.posix.dumps(0))
    else:
        raise(Exception("Could not find the solution"))

if __name__ == "__main__":
    main(sys.argv)

```
![](https://i.imgur.com/2peedDO.png)

# 14_angr_shared_library
大概分兩派 有兩篇文章
開啟PIE情況
對於開啟PIE的程序，程序的基址固定在0x400000處，提取使用時應該加上該值。
或者關閉時為
0x08048000 兩者都可以。

這部分可以假設是動態要操作的fucntion 是validate
但是他在
lib14_angr_shared_library.so
![](https://i.imgur.com/DTK33Mg.png)

程式主體
14_angr_shared_library
![](https://i.imgur.com/UbuM1Zx.png)
https://blog.csdn.net/RichardYSteven/article/details/4967359
![](https://i.imgur.com/P3bTKGe.png)
這邊只有找到 linux virtual memory address space
![](https://i.imgur.com/Xl8hrK6.png)

```
0x6d7
```

000006D7 進行偏移就會找到實際的 validate 在runtime的address
Script - ARGS
● Claripy frontends
# Create a 32-bit symbolic bitvector "x"
> claripy.BVS('x', 32)
# Create a 32-bit bitvectory with the value 0x12345678
> claripy.BVV(0x12345678, 32)
<BV32 BVV(0x12345678, 32)>

validate function end
```
0x783
```
![](https://i.imgur.com/4tVx9lm.png)
![](https://i.imgur.com/5243yCj.png)

s1為symbloic      buffer_pointer
a2直接填入8        claripy.BVV(8, 32)

![](https://i.imgur.com/K6KShOk.png)

```python
# The shared library has the function validate, which takes a string and returns
# either true (1) or false (0). The binary calls this function. If it returns
# true, the program prints "Good Job." otherwise, it prints "Try again."
#
# Note: When you run this script, make sure you run it on
# lib14_angr_shared_library.so, not the executable. This level is intended to
# teach how to analyse binary formats that are not typical executables.

import angr
import claripy
import sys

def main(argv):
  path_to_binary = "/home/angr/angr-dev/test/lib14_angr_shared_library.so"

  # The shared library is compiled with position-independent code. You will need
  # to specify the base address. All addresses in the shared library will be
  # base + offset, where offset is their address in the file.
  # (!)
  base = 0x08048000  
  project = angr.Project(path_to_binary, load_options={
    'main_opts' : {
      'base_addr' : base
    }
  })

  # Initialize any symbolic values here; you will need at least one to pass to
  # the validate function.
  # (!)
  buffer_pointer = claripy.BVV(0xC0000000, 32)

  # Begin the state at the beginning of the validate function, as if it was
  # called by the program. Determine the parameters needed to call validate and
  # replace 'parameters...' with bitvectors holding the values you wish to pass.
  # Recall that 'claripy.BVV(value, size_in_bits)' constructs a bitvector
  # initialized to a single value.
  # Remember to add the base value you specified at the beginning to the
  # function address!
  # Hint: int validate(char* buffer, int length) { ...
  # (!)
  validate_function_address = base + 0x6d7
  initial_state = project.factory.call_state(
                    validate_function_address,
                    buffer_pointer,
                    claripy.BVV(8, 32)
                  )

  # Inject a symbolic value for the password buffer into the program and
  # instantiate the simulation. Another hint: the password is 8 bytes long.
  # (!)
  password = claripy.BVS(  "password", 8*8 )
  initial_state.memory.store( buffer_pointer , password)
  
  simulation = project.factory.simgr(initial_state)

  # We wish to reach the end of the validate function and constrain the
  # return value of the function (stored in eax) to equal true (value of 1)
  # just before the function returns. We could use a hook, but instead we
  # can search for the address just before the function returns and then
  # constrain eax
  # (!)
  check_constraint_address = base + 0x783
  simulation.explore(find=check_constraint_address)

  if simulation.found:
    solution_state = simulation.found[0]

    # Determine where the program places the return value, and constrain it so
    # that it is true. Then, solve for the solution and print it.
    # (!)
    solution_state.add_constraints( solution_state.regs.eax != 0 )
    solution = solution_state.solver.eval(password, cast_to=bytes)
    print('solution is {0}'.format(solution))
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)

```
![](https://i.imgur.com/bxEFNqi.png)

# 15_angr_arbitrary_read
緩衝區溢位攻擊
https://blog.csdn.net/weixin_46196863/article/details/114630563
http://godleon.blogspot.com/2008/02/indirect-addressing-indirect-address.html
選取 puts address
![](https://i.imgur.com/b9Z33H4.png)
good job address
![](https://i.imgur.com/pg0ZNka.png)
這邊要注意這個細節
      # Warning: Endianness only applies to integers. If you store a string in
      # memory and treat it as a little-endian integer, it will be backwards.
      scanf0_address = key_address
      self.state.memory.store(scanf0_address, scanf0, endness=project.arch.memory_endness)
      scanf1_address = input_address
      self.state.memory.store(scanf1_address, scanf1)
      self.state.globals['solution0'] = scanf0
      self.state.globals['solution1'] = scanf1
      
```python
# This binary takes both an integer and a string as a parameter. A certain
# integer input causes the program to reach a buffer overflow with which we can
# read a string from an arbitrary memory location. Our goal is to use Angr to
# search the program for this buffer overflow and then automatically generate
# an exploit to read the string "Good Job."
#
# What is the point of reading the string "Good Job."?
# This CTF attempts to replicate a simplified version of a possible vulnerability
# where a user can exploit the program to print a secret, such as a password or
# a private key. In order to keep consistency with the other challenges and to
# simplify the challenge, the goal of this program will be to print "Good Job."
# instead.
#
# The general strategy for crafting this script will be to:
# 1) Search for calls of the 'puts' function, which will eventually be exploited
#    to print out "Good Job."
# 2) Determine if the first parameter of 'puts', a pointer to the string to be
#    printed, can be controlled by the user to be set to the location of the
#    "Good Job." string.
# 3) Solve for the input that prints "Good Job."
#
# Note: The script is structured to implement step #2 before #1.

# Some of the source code for this challenge:
#
# #include <stdio.h>
# #include <stdlib.h>
# #include <string.h>
# #include <stdint.h>
# 
# // This will all be in .rodata
# char msg[] = "${ description }$";
# char* try_again = "Try again.";
# char* good_job = "Good Job.";
# uint32_t key;
# 
# void print_msg() {
#   printf("%s", msg);
# }
#
# uint32_t complex_function(uint32_t input) {
#   ...
# }
# 
# struct overflow_me {
#   char buffer[16];
#   char* to_print;
# }; 
# 
# int main(int argc, char* argv[]) {
#   struct overflow_me locals;
#   locals.to_print = try_again;
# 
#   print_msg();
# 
#   printf("Enter the password: ");
#   scanf("%u %20s", &key, locals.buffer);
#
#   key = complex_function(key);
# 
#   switch (key) {
#     case ?:
#       puts(try_again);
#       break;
#
#     ...
#
#     case ?:
#       // Our goal is to trick this call to puts to print the "secret
#       // password" (which happens, in our case, to be the string
#       // "Good Job.")
#       puts(locals.to_print);
#       break;
#     
#     ...
#   }
# 
#   return 0;
# }

import angr
import claripy
import sys

def main(argv):
  path_to_binary = "/home/angr/angr-dev/test/15_angr_arbitrary_read"
  project = angr.Project(path_to_binary)

  # You can either use a blank state or an entry state; just make sure to start
  # at the beginning of the program.
  # (!)
  initial_state =  project.factory.entry_state()

  # Again, scanf needs to be replaced.
  class ReplacementScanf(angr.SimProcedure):
    # Hint: scanf("%u %20s")
    def run(self, format_string, key_address, input_address):
      # %u
      scanf0 = claripy.BVS('scanf0', 4*8)
      
      # %20s
      scanf1 = claripy.BVS('scanf1', 8*20)

      # The bitvector.chop(bits=n) function splits the bitvector into a Python
      # list containing the bitvector in segments of n bits each. In this case,
      # we are splitting them into segments of 8 bits (one byte.)
      for char in scanf1.chop(bits=8):
        # Ensure that each character in the string is printable. An interesting
        # experiment, once you have a working solution, would be to run the code
        # without constraining the characters to the printable range of ASCII.
        # Even though the solution will technically work without this, it's more
        # difficult to enter in a solution that contains character you can't
        # copy, paste, or type into your terminal or the web form that checks 
        # your solution.
        # (!)
        self.state.add_constraints(char >= 'A', char <= 'Z')

      # Warning: Endianness only applies to integers. If you store a string in
      # memory and treat it as a little-endian integer, it will be backwards.
      scanf0_address = key_address
      self.state.memory.store(scanf0_address, scanf0, endness=project.arch.memory_endness)
      scanf1_address = input_address
      self.state.memory.store(scanf1_address, scanf1)
      self.state.globals['solution0'] = scanf0
      self.state.globals['solution1'] = scanf1

  scanf_symbol = "__isoc99_scanf"  # :string
  project.hook_symbol(scanf_symbol, ReplacementScanf())

  # We will call this whenever puts is called. The goal of this function is to
  # determine if the pointer passed to puts is controllable by the user, such
  # that we can rewrite it to point to the string "Good Job."
  def check_puts(state):
    # Recall that puts takes one parameter, a pointer to the string it will
    # print. If we load that pointer from memory, we can analyse it to determine
    # if it can be controlled by the user input in order to point it to the
    # location of the "Good Job." string.
    #
    # Treat the implementation of this function as if puts was just called.
    # The stack, registers, memory, etc should be set up as if the x86 call
    # instruction was just invoked (but, of course, the function hasn't copied
    # the buffers yet.)
    # The stack will look as follows:
    # ...
    # esp + 7 -> /----------------\
    # esp + 6 -> |      puts      |
    # esp + 5 -> |    parameter   |
    # esp + 4 -> \----------------/
    # esp + 3 -> /----------------\
    # esp + 2 -> |     return     |
    # esp + 1 -> |     address    |
    #     esp -> \----------------/
    #
    # Hint: Look at level 08, 09, or 10 to review how to load a value from a
    # memory address. Remember to use the correct endianness in the future when
    # loading integers; it has been included for you here.
    # (!)
    puts_parameter = state.memory.load( state.regs.esp+4, 4, endness=project.arch.memory_endness)

    # The following function takes a bitvector as a parameter and checks if it
    # can take on more than one value. While this does not necessary tell us we
    # have found an exploitable state, it is a strong indication that the 
    # bitvector we checked may be controllable by the user.
    # Use it to determine if the pointer passed to puts is symbolic.
    # (!)
    if state.solver.symbolic(puts_parameter):
      # Determine the location of the "Good Job." string. We want to print it
      # out, and we will do so by attempting to constrain the puts parameter to
      # equal it. Hint: use 'objdump -s <binary>' to look for the string's
      # address in .rodata.
      # (!)
      good_job_string_address = 0x484F4A47 # :integer, probably hexadecimal

      # Create an expression that will test if puts_parameter equals
      # good_job_string_address. If we add this as a constraint to our solver,
      # it will try and find an input to make this expression true. Take a look
      # at level 08 to remind yourself of the syntax of this.
      # (!)
      is_vulnerable_expression = puts_parameter == good_job_string_address # :boolean bitvector expression

      # Have Angr evaluate the state to determine if all the constraints can
      # be met, including the one we specified above. If it can be satisfied,
      # we have found our exploit!
      #
      # When doing this, however, we do not want to edit our state in case we
      # have not yet found what we are looking for. To test if our expression
      # is satisfiable without editing the original, we need to clone the state.
      copied_state = state.copy()

      # We can now play around with the copied state without changing the
      # original. We need to add our vulnerable expression as a state to test it.
      # Look at level 08 and compare this call to how it is called there.
      copied_state.add_constraints(is_vulnerable_expression)

      # Finally, we test if we can satisfy the constraints of the state.
      if copied_state.satisfiable():
        # Before we return, let's add the constraint to the solver for real,
        # instead of just querying whether the constraint _could_ be added.
        state.add_constraints(is_vulnerable_expression)
        return True
      else:
        return False
    else: # not state.solver.symbolic(???)
      return False

  simulation = project.factory.simgr(initial_state)

  # In order to determine if we have found a vulnerable call to 'puts',  we need
  # to run the function check_puts (defined above) whenever we reach a 'puts'
  # call. To do this, we will look for the place where the instruction pointer,
  # state.addr, is equal to the beginning of the puts function.
  def is_successful(state):
    # We are looking for puts. Check that the address is at the (very) beginning
    # of the puts function. Warning: while, in theory, you could look for
    # any address in puts, if you execute any instruction that adjusts the stack
    # pointer, the stack diagram above will be incorrect. Therefore, it is
    # recommended that you check for the very beginning of puts.
    # (!)
    puts_address = 0x08048370
    print(state.addr)
    if state.addr == puts_address:
      # Return True if we determine this call to puts is exploitable.
      return check_puts(state)
    else:
      # We have not yet found a call to puts; we should continue!
      return False

  simulation.explore(find=is_successful)

  if simulation.found:
    solution_state = simulation.found[0]

    scanf0 =solution_state.globals["solution0"]
    scanf1 =solution_state.globals["solution1"]
    flag = str(solution_state.solver.eval(scanf0)).encode("utf-8")
    flag += b" " + solution_state.solver.eval(scanf1, cast_to=bytes)
    print(flag)
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)

```
![](https://i.imgur.com/PDPL4zM.png)

https://medium.com/@ktecv2000/%E7%B7%A9%E8%A1%9D%E5%8D%80%E6%BA%A2%E4%BD%8D%E6%94%BB%E6%93%8A%E4%B9%8B%E4%B8%80-buffer-overflow-83516aa80240

![](https://i.imgur.com/3VurMXp.png)
既然可以任意讀取那麼我們換成別的address
![](https://i.imgur.com/6SYCC3N.png)
![](https://i.imgur.com/6fJovQS.png)
好像要預設是 const char 才行。
![](https://i.imgur.com/gqq8Wxg.png)
# 16_angr_arbitrary_write

任意寫入
可以看到有機會可以蓋掉 dest的value

![](https://i.imgur.com/zIs95xI.png)
```python
# Essentially, the program does the following:
#
# scanf("%d %20s", &key, user_input);
# ...
#   // if certain unknown conditions are true...
#   strncpy(random_buffer, user_input);
# ...
# if (strncmp(secure_buffer, reference_string)) {
#   // The secure_buffer does not equal the reference string.
#   puts("Try again.");
# } else {
#   // The two are equal.
#   puts("Good Job.");
# }
#
# If this program has no bugs in it, it would _always_ print "Try again." since
# user_input copies into random_buffer, not secure_buffer.
#
# The question is: can we find a buffer overflow that will allow us to overwrite
# the random_buffer pointer to point to secure_buffer? (Spoiler: we can, but we
# will need to use Angr.)
#
# We want to identify a place in the binary, when strncpy is called, when we can:
#  1) Control the source contents (not the source pointer!)
#     * This will allow us to write arbitrary data to the destination.
#  2) Control the destination pointer
#     * This will allow us to write to an arbitrary location.
# If we can meet both of those requirements, we can write arbitrary data to an
# arbitrary location. Finally, we need to contrain the source contents to be
# equal to the reference_string and the destination pointer to be equal to the
# secure_buffer.

import angr
import claripy
import sys

def main(argv):
  path_to_binary =  "/home/angr/angr-dev/test/16_angr_arbitrary_write"
  project = angr.Project(path_to_binary)

  # You can either use a blank state or an entry state; just make sure to start
  # at the beginning of the program.
  initial_state =  project.factory.entry_state()

  # Again, scanf needs to be replaced.
  class ReplacementScanf(angr.SimProcedure):
    # Hint: scanf("%u %20s")
    def run(self, format_string, key_address, input_address):
      # %u
      scanf0 = claripy.BVS('scanf0', 4*8)
      
      # %20s
      scanf1 = claripy.BVS('scanf1', 8*20)

      # The bitvector.chop(bits=n) function splits the bitvector into a Python
      # list containing the bitvector in segments of n bits each. In this case,
      # we are splitting them into segments of 8 bits (one byte.)
      for char in scanf1.chop(bits=8):
        # Ensure that each character in the string is printable. An interesting
        # experiment, once you have a working solution, would be to run the code
        # without constraining the characters to the printable range of ASCII.
        # Even though the solution will technically work without this, it's more
        # difficult to enter in a solution that contains character you can't
        # copy, paste, or type into your terminal or the web form that checks 
        # your solution.
        # (!)
        self.state.add_constraints(char >= 48, char <= 96)

      # Warning: Endianness only applies to integers. If you store a string in
      # memory and treat it as a little-endian integer, it will be backwards.
      scanf0_address = key_address
      self.state.memory.store(scanf0_address, scanf0, endness=project.arch.memory_endness)
      scanf1_address = input_address
      self.state.memory.store(scanf1_address, scanf1)
      self.state.globals['solution0'] = scanf0
      self.state.globals['solution1'] = scanf1

  scanf_symbol = "__isoc99_scanf"  # :string
  project.hook_symbol(scanf_symbol, ReplacementScanf())

  # In this challenge, we want to check strncpy to determine if we can control
  # both the source and the destination. It is common that we will be able to
  # control at least one of the parameters, (such as when the program copies a
  # string that it received via stdin).
  def check_strncpy(state):
    # The stack will look as follows:
    # ...          ________________
    # esp + 15 -> /                \
    # esp + 14 -> |     param2     |
    # esp + 13 -> |      len       |
    # esp + 12 -> \________________/
    # esp + 11 -> /                \
    # esp + 10 -> |     param1     |
    #  esp + 9 -> |      src       |
    #  esp + 8 -> \________________/
    #  esp + 7 -> /                \
    #  esp + 6 -> |     param0     |
    #  esp + 5 -> |      dest      |
    #  esp + 4 -> \________________/
    #  esp + 3 -> /                \
    #  esp + 2 -> |     return     |
    #  esp + 1 -> |     address    |
    #      esp -> \________________/
    # (!)
    strncpy_dest = state.memory.load(state.regs.esp+4,4,endness=project.arch.memory_endness)
    strncpy_src = state.memory.load(state.regs.esp+8,4,endness=project.arch.memory_endness)
    strncpy_len = state.memory.load(state.regs.esp+12,4,endness=project.arch.memory_endness)

    # We need to find out if src is symbolic, however, we care about the
    # contents, rather than the pointer itself. Therefore, we have to load the
    # the contents of src to determine if they are symbolic.
    # Hint: How many bytes is strncpy copying?
    # (!)
    src_contents = state.memory.load(strncpy_src, strncpy_len)

    # Our goal is to determine if we can write arbitrary data to an arbitrary
    # location. This means determining if the source contents are symbolic
    # (arbitrary data) and the destination pointer is symbolic (arbitrary
    # destination).
    # (!)
    if state.solver.symbolic(strncpy_dest) and state.solver.symbolic(src_contents) :
      # Use ltrace to determine the password. Decompile the binary to determine
      # the address of the buffer it checks the password against. Our goal is to
      # overwrite that buffer to store the password.
      # (!)
      password_string = "NDYNWEUJ" # :string
      buffer_address = 0x57584344 # :integer, probably in hexadecimal

      # Create an expression that tests if the first n bytes is length. Warning:
      # while typical Python slices (array[start:end]) will work with bitvectors,
      # they are indexed in an odd way. The ranges must start with a high value
      # and end with a low value. Additionally, the bits are indexed from right
      # to left. For example, let a bitvector, b, equal 'ABCDEFGH', (64 bits).
      # The following will read bit 0-7 (total of 1 byte) from the right-most
      # bit (the end of the string).
      #  b[7:0] == 'H'
      # To access the beginning of the string, we need to access the last 16
      # bits, or bits 48-63:
      #  b[63:48] == 'AB'
      # In this specific case, since we don't necessarily know the length of the
      # contents (unless you look at the binary), we can use the following:
      #  b[-1:-16] == 'AB', since, in Python, -1 is the end of the list, and -16
      # is the 16th element from the end of the list. The actual numbers should
      # correspond with the length of password_string.
      # (!)
      does_src_hold_password = src_contents[-1:64] == password_string

      # Create an expression to check if the dest parameter can be set to
      # buffer_address. If this is true, then we have found our exploit!
      # (!)
      does_dest_equal_buffer_address = buffer_address==strncpy_dest

      # In the previous challenge, we copied the state, added constraints to the
      # copied state, and then determined if the constraints of the new state
      # were satisfiable. Since that pattern is so common, Angr implemented a
      # parameter 'extra_constraints' for the satisfiable function that does the
      # exact same thing.  Note that we can pass multiple expressions to
      # extra_constraints.
      if state.satisfiable(extra_constraints=(does_src_hold_password, does_dest_equal_buffer_address)):
        state.add_constraints(does_src_hold_password, does_dest_equal_buffer_address)
        return True
      else:
        return False
    else: # not state.solver.symbolic(???)
      return False

  simulation = project.factory.simgr(initial_state)

  def is_successful(state):
    strncpy_address = 0x08048410 
    if state.addr == strncpy_address:
      return check_strncpy(state)
    else:
      return False

  simulation.explore(find=is_successful)

  if simulation.found:
    solution_state = simulation.found[0]

    scanf0 =solution_state.globals["solution0"]
    scanf1 =solution_state.globals["solution1"]
    flag = str(solution_state.solver.eval(scanf0)).encode("utf-8")
    flag += b" " + solution_state.solver.eval(scanf1, cast_to=bytes)
    print(flag)
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)

```
![](https://i.imgur.com/FTl0ya5.png)

# 17_angr_arbitrary_jump
緩衝區溢出任意跳轉
我們要跳來這裡
![](https://i.imgur.com/72rnmzH.png)
input
![](https://i.imgur.com/ivE8dHh.png)

```pyhton
# An unconstrained state occurs when there are too many
# possible branches from a single instruction. This occurs, among other ways,
# when the instruction pointer (on x86, eip) is completely symbolic, meaning
# that user input can control the address of code the computer executes.
# For example, imagine the following pseudo assembly:
#
# mov user_input, eax
# jmp eax
#
# The value of what the user entered dictates the next instruction. This
# is an unconstrained state. It wouldn't usually make sense for the execution
# engine to continue. (Where should the program jump to if eax could be
# anything?) Normally, when Angr encounters an unconstrained state, it throws
# it out. In our case, we want to exploit the unconstrained state to jump to
# a location of our choosing. We will get to how to disable Angr's default
# behavior later.
#
# This challenge represents a classic stack-based buffer overflow attack to
# overwrite the return address and jump to a function that prints "Good Job."
# Our strategy for solving the challenge is as follows:
# 1. Initialize the simulation and ask Angr to record unconstrained states.
# 2. Step through the simulation until we have found a state where eip is
#    symbolic.
# 3. Constrain eip to equal the address of the "print_good" function.

import angr
import claripy
import sys

def main(argv):
  path_to_binary =  "/home/angr/angr-dev/test/17_angr_arbitrary_jump"
  project = angr.Project(path_to_binary)

  # Make a symbolic input that has a decent size to trigger overflow
  # (!)

  class ReplacementScanf(angr.SimProcedure):
    # Hint: scanf("%u %20s")
    def run(self, format_string,  input_address):
      # %u
      symbolic_input = claripy.BVS("input", 64 * 8)
      
      # The bitvector.chop(bits=n) function splits the bitvector into a Python
      # list containing the bitvector in segments of n bits each. In this case,
      # we are splitting them into segments of 8 bits (one byte.)
      for char in symbolic_input.chop(bits=8):
        # Ensure that each character in the string is printable. An interesting
        # experiment, once you have a working solution, would be to run the code
        # without constraining the characters to the printable range of ASCII.
        # Even though the solution will technically work without this, it's more
        # difficult to enter in a solution that contains character you can't
        # copy, paste, or type into your terminal or the web form that checks 
        # your solution.
        # (!)
        self.state.add_constraints(char >= 'A', char <= 'z')

      # Warning: Endianness only applies to integers. If you store a string in
      # memory and treat it as a little-endian integer, it will be backwards.
      
      self.state.memory.store(input_address, symbolic_input)
      self.state.globals['solution'] = symbolic_input

  scanf_symbol = "__isoc99_scanf"  # :string
  project.hook_symbol(scanf_symbol, ReplacementScanf())
  # Create initial state and set stdin to the symbolic input
  initial_state = project.factory.entry_state(
        
          add_options = {
              angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
              angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS
              }
          )

  # The save_unconstrained=True parameter specifies to Angr to not throw out
  # unconstrained states. Instead, it will move them to the list called
  # 'simulation.unconstrained'.  Additionally, we will be using a few stashes
  # that are not included by default, such as 'found' and 'not_needed'. You will
  # see how these are used later.
  # (!)
  simulation = project.factory.simgr(
    initial_state,
    save_unconstrained=True,
    stashes={
      'active' : [initial_state],
      'unconstrained' : [],
      'found' : [],
      'not_needed' : []
    }
  )

  # Explore will not work for us, since the method specified with the 'find'
  # parameter will not be called on an unconstrained state. Instead, we want to
  # explore the binary ourselves. To get started, construct an exit condition
  # to know when the simulation has found a solution. We will later move
  # states from the unconstrained list to the simulation.found list.
  # Create a boolean value that indicates a state has been found.
  def has_found_solution():
    return simulation.found

  # An unconstrained state occurs when there are too many possible branches
  # from a single instruction. This occurs, among other ways, when the
  # instruction pointer (on x86, eip) is completely symbolic, meaning
  # that user input can control the address of code the computer executes.
  # For example, imagine the following pseudo assembly:
  #
  # mov user_input, eax
  # jmp eax
  #
  # The value of what the user entered dictates the next instruction. This
  # is an unconstrained state. It wouldn't usually make sense for the execution
  # engine to continue. (Where should the program jump to if eax could be
  # anything?) Normally, when Angr encounters an unconstrained state, it throws
  # it out. In our case, we want to exploit the unconstrained state to jump to
  # a location of our choosing.  Check if there are still unconstrained states
  # by examining the simulation.unconstrained list.
  # (!)
  def has_unconstrained_to_check():
    return len(simulation.unconstrained) > 0

  # The list simulation.active is a list of all states that can be explored
  # further.
  # (!)
  def has_active():
    return len(simulation.active) > 0

  while (has_active() or has_unconstrained_to_check()) and (not has_found_solution()):
    for unconstrained_state in simulation.unconstrained:
        # Look for unconstrained states and move them to the 'found' stash.
        # A 'stash' should be a string that corresponds to a list that stores
        # all the states that the state group keeps. Values include:
        #  'active' = states that can be stepped
        #  'deadended' = states that have exited the program
        #  'errored' = states that encountered an error with Angr
        #  'unconstrained' = states that are unconstrained
        #  'found' = solutions
        #  anything else = whatever you want, perhaps you want a 'not_needed',
        #                  you can call it whatever you want
        # (!)
      simulation.move('unconstrained', 'found')

    # Advance the simulation.
    simulation.step()

  if simulation.found:
    solution_state = simulation.found[0]

    # Constrain the instruction pointer to target the print_good function and
    # (!)
    solution_state.add_constraints(solution_state.regs.eip == 0x42585249)

    # Constrain the symbolic input to fall within printable range (capital
    # letters) for the web UI.  Ensure UTF-8 encoding.
    # (!)
    # for byte in symbolic_input.chop(bits=8):
    #   solution_state.add_constraints(
    #           byte >= ???,
    #           byte <= ???
    #   )

    # Solve for the symbolic_input
    # test =solution_state.state.globals['solution']
    # print(test)
    flag = solution_state.solver.eval(solution_state.globals["solution"], cast_to=bytes)
    print(flag)
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)

```
![](https://i.imgur.com/gX31e84.png)
17題理解還是怪怪的有空再來製作例子，再用angr跑一次
# 參考
https://lantern.cool/note-tool-angr/#%E8%84%9A%E6%9C%AC-13
https://icode.best/i/46761544756831
https://www.anquanke.com/post/id/231460
https://hitcon.org/2016/CMT/slide/day1-r1-a-1.pdf
https://blog.ycdxsb.cn/f7e7b79c.html
https://www.anquanke.com/post/id/216504

