---
title: "angr symbolic execution"
date: "2022-03-13T02:32:00.007+08:00"
updated: "2022-08-30T14:06:40.676+08:00"
permalink: "/2022/03/angr-symbolic-execution.html"
original_url: "https://x8795278.blogspot.com/2022/03/angr-symbolic-execution.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3349010322867720654"
tags: ["angr", "z3"]
layout: post
---

![](https://i.imgur.com/c8SMfCs.png)

# angr
![](https://i.imgur.com/c8SMfCs.png)

我的環境位於wsl，不過我有docker
https://docs.angr.io/introductory-errata/install
```bash
# clone ctf project
git clone https://github.com/jakespringer/angr_ctf.git

# install docker
curl -sSL https://get.docker.com/ | sudo sh

# pull the docker image
sudo docker pull angr/angr

# run it
sudo docker run -it angr/angr

# 掛在我們clolne下的ctf目錄
sudo docker run  -it    -v /root/angr_ctf/00_angr_find/:/home/angr/angr-dev/test/   angr/angr
```
# Symbolic Execution
符號執行技術是一種白盒的靜態分析技術。即，分析程序可能的輸入需要能夠獲取到目標原始碼的支持。同時，它是靜態的，因為並沒有實際的執行程序本身，而是分析程序的執行路徑。
詳細原理請參考
https://bbs.pediy.com/thread-264878.htm

# ctf tree
clone 專案下來於angr_ctf/dist有編譯好的binary我們還需要使用ida進行分析。
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
# template

在每一題的目錄下可以看到` generate.py`，這邊可以稍微學習一下如何用python 隨機生成這種c程式碼。
```bash
-fno-pie -no-pie -fcf-protection=none 
```
https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html#Instrumentation-Options
可以看到使用gcc -fcf-protectionflag有對我們的執行檔做額外處理看敘述應該是關掉ROP攻擊等其他判斷，應該不是aslr那些，在後續文章，也會看到其他處理讓程式每次載入memory每次啟動都一樣。
# security
```
32位程序
開啟了Canary和NX，關閉了PIE ，那麼code段地址不會改變。
```

```python
#!/usr/bin/env python3
import sys, random, os, tempfile, jinja2

def generate(argv):
  if len(argv) != 3:
    print('Usage: ./generate.py [seed] [output_file]')
    sys.exit()

  seed = argv[1]
  output_file = argv[2]

  random.seed(seed)
  userdef_charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  userdef = ''.join(random.choice(userdef_charset) for _ in range(8))

  template = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '00_angr_find.c.jinja'), 'r').read()
  t = jinja2.Template(template)
  c_code = t.render(userdef=userdef, len_userdef=len(userdef), description = '')

  with tempfile.NamedTemporaryFile(delete=False, suffix='.c', mode='w') as temp:
    temp.write(c_code)
    temp.seek(0)
    os.system('gcc -fno-pie -no-pie -fcf-protection=none -m32 -o ' + output_file + ' ' + temp.name)

if __name__ == '__main__':
    generate(sys.argv)

```

```00_angr_find.c.jinja
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define USERDEF "{{ userdef }}"
#define LEN_USERDEF {{ len_userdef }}

char msg[] =
  "{{ description }}";

void print_msg() {
  printf("%s", msg);
}

int complex_function(int value, int i) {
#define LAMBDA 3
  if (!('A' <= value && value <= 'Z')) {
    printf("Try again.\n");
    exit(1);
  }
  return ((value - 'A' + (LAMBDA * i)) % ('Z' - 'A' + 1)) + 'A';
}

int main(int argc, char* argv[]) {
  char buffer[9];

  //print_msg();

  printf("Enter the password: ");
  scanf("%8s", buffer);

  for (int i=0; i<LEN_USERDEF; ++i) {
    buffer[i] = complex_function(buffer[i], i);
  }

  if (strcmp(buffer, USERDEF)) {
    printf("Try again.\n");
  } else {
    printf("Good Job.\n");
  }
}
```
# 根據 模板產生c code
於任意
/root/angr_ctf/題號目錄/generate.py
```bash
sudo python3 generate.py  04_angr_symbolic_stack.c.jinja  ./test
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define USERDEF0 2997776385
#define USERDEF1 1966343970

char msg[] = "";

void print_msg() {
  printf("%s", msg);
}

uint32_t complex_function0(uint32_t value) {
  value ^= 2533711732;value ^= 2593354591;value ^= 2343946690;value ^= 995143788;value ^= 3918799375;value ^= 2793389223;value ^= 3760967890;value ^= 2831565273;value ^= 1820446797;value ^= 980611347;value ^= 3230278687;value ^= 209927687;value ^= 2280613315;value ^= 2051206487;value ^= 4004020839;value ^= 3859445670;value ^= 1872572178;value ^= 170950821;value ^= 3677808046;value ^= 1437212780;value ^= 2686921896;value ^= 3847214437;value ^= 1299307166;value ^= 2364791306;value ^= 510873734;value ^= 1470206620;value ^= 3165490505;value ^= 2564832072;value ^= 539405512;value ^= 1391856955;value ^= 616548599;value ^= 329054243;
  return value;
}

uint32_t complex_function1(uint32_t value) {
  value ^= 3719196317;value ^= 2979048246;value ^= 968728659;value ^= 56966325;value ^= 1635704867;value ^= 164594016;value ^= 248282231;value ^= 2222561507;value ^= 3793834468;value ^= 4251205034;value ^= 882375839;value ^= 1827536944;value ^= 1749698508;value ^= 782058120;value ^= 2883770482;value ^= 2928618623;value ^= 3039571705;value ^= 314028640;value ^= 3510754512;value ^= 515637315;value ^= 1799264849;value ^= 2338999872;value ^= 2550244840;value ^= 2329154939;value ^= 3310465120;value ^= 3371939078;value ^= 2989903830;value ^= 3679244865;value ^= 4244655143;value ^= 917105375;value ^= 2349674148;value ^= 2722154001;
  return value;
}

void handle_user() {
  uint32_t user_int0;
  uint32_t user_int1;
  scanf("%u %u", &user_int0, &user_int1);
  user_int0 = complex_function0(user_int0);
  user_int1 = complex_function1(user_int1);
  if ((user_int0 ^ USERDEF0) || (user_int1 ^ USERDEF1)) {
    printf("Try again.\n");
  } else {
    printf("Good Job.\n");
  }
}

int main(int argc, char* argv[]) {
  //print_msg();
  printf("Enter the password: ");
  handle_user();
}
```
# 00_angr_find
裡面幾乎都有解題模板，我們只要理解意思再配合進行ida解析即可
使用ida進行解析
![](https://i.imgur.com/lOQZ2YP.png)
於第一題

因為我是使用docker 所以這邊使用的是 docker 裡面的目錄
`path_to_binary ="/home/angr/angr-dev/test/00_angr_find"  # :string`

這邊填入的是0x8048678
`print_good_address =0x8048678  # :integer(probably in hexadecimal)`
![](https://i.imgur.com/FkD78Km.png)
為什麼是0x8048678因為假設 Symbolic Execution 足夠強大其實是可以使用邏輯判斷式去推導實際上是否有分支會走到這個0x8048678，可以看到simulation.explore(find=print_good_address)
當找到這個分支則將當前的stdin 給印出來理所當然也就是輸入的也就是通過的key。
```python
print(solution_state.posix.dumps(sys.stdin.fileno()).decode())
```
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

from ctypes import sizeof
import angr
import sys

def main(argv):
  # Create an Angr project.
  # If you want to be able to point to the binary from the command line, you can
  # use argv[1] as the parameter. Then, you can run the script from the command
  # line as follows:
  # python ./scaffold00.py [binary]
  # (!)
  path_to_binary ="/home/angr/angr-dev/test/00_angr_find"  # :string
  project = angr.Project(path_to_binary)

  # Tell Angr where to start executing (should it start from the main()
  # function or somewhere else?) For now, use the entry_state function
  # to instruct Angr to start from the main() function.
  initial_state = project.factory.entry_state(
    add_options = { angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
                    angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS}
  )

  # Create a simulation manager initialized with the starting state. It provides
  # a number of useful tools to search and execute the binary.
  simulation = project.factory.simgr(initial_state)

  # Explore the binary to attempt to find the address that prints "Good Job."
  # You will have to find the address you want to find and insert it here. 
  # This function will keep executing until it either finds a solution or it 
  # has explored every possible path through the executable.
  # (!)
  print_good_address =0x8048678  # :integer (probably in hexadecimal)
  simulation.explore(find=print_good_address)

  # Check that we have found a solution. The simulation.explore() method will
  # set simulation.found to a list of the states that it could find that reach
  # the instruction we asked it to search for. Remember, in Python, if a list
  # is empty, it will be evaluated as false, otherwise true.
  if simulation.found:
    # The explore method stops after it finds a single state that arrives at the
    # target address.
    solution_state = simulation.found[0]
    print(len(simulation.found))
    #  print(solution_state.posix)
    # Print the string that Angr wrote to stdin to follow solution_state. This 
    # is our solution.
    print(solution_state.posix.dumps(sys.stdin.fileno()).decode())
  else:
    # If Angr could not find a path that reaches print_good_address, throw an
    # error. Perhaps you mistyped the print_good_address?
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)
```
可能需要一段時間才能跑解出來
![](https://i.imgur.com/EqGL8Ie.png)

## z3
上述是使用angr自動探索，我們使用z3來看看實際上是如何產生那些邏輯讓他們自己去跑解答出來。
使用ida載入dist/00_angr_find的檔案，按f5進行分析
### main
```
int __cdecl main(int argc, const char **argv, const char **envp)
{
  int i; // [esp+1Ch] [ebp-1Ch]
  char s1[9]; // [esp+23h] [ebp-15h] BYREF
  unsigned int v6; // [esp+2Ch] [ebp-Ch]

  v6 = __readgsdword(0x14u);
  printf("Enter the password: ");
  __isoc99_scanf("%8s", s1);
  for ( i = 0; i <= 7; ++i )
    s1[i] = complex_function(s1[i], i);
  if ( !strcmp(s1, "JACEJGCS") )
    puts("Good Job.");
  else
    puts("Try again.");
  return 0;
}
```
![](https://i.imgur.com/AgnbFFv.png)

### complex_function
直接看意思大概可以推斷就是傳入 0~7的值再去跟輸入的char做運算。

```
int __cdecl complex_function(int a1, int a2)
{
  if ( a1 <= 64 || a1 > 90 )
  {
    puts("Try again.");
    exit(1);
  }
  return (3 * a2 + a1 - 65) % 26 + 65;
}
```
那麼使用z3求解器來實踐這個程式碼片段，目前邏輯還不常，後面有需要才會使用到z3.
```python
x1=Int('x1')

char =['J','A','C','E','J','G','C','S']
ans  = []
s=Solver()
test = 0
for x in char:
    s.push()
    s.add( And(x1>65 ,x1<90 ))
    s.push()
    s.add(And(((3 * test + x1 - 65) % 26 + 65) ==(ord(x))))
    test = test+1
    s.check()
    m = s.model()
    ans.append(chr(m[x1].as_long()) )
    s.pop()
    s.pop()

print("".join(ans))
```
![](https://i.imgur.com/F70uPrP.png)
可以看到與自動跑解差不多，但是我們少了探索直接針對key這部分的邏輯進行推導，angr的前端也是使用z3求解器。

來驗證key
![](https://i.imgur.com/JCUONIj.png)

# 01_angr_avoid
![](https://i.imgur.com/XWzNPxl.png)
第一次載入執行檔案，ida轉到再繞圈圈
![](https://i.imgur.com/Zvf7dRG.png)
![](https://i.imgur.com/cQLGslx.png)

```python
import angr
import sys

def main(argv):
  path_to_binary = "/home/angr/angr-dev/test/01_angr_avoid"
  project = angr.Project(path_to_binary)
  initial_state = project.factory.entry_state(
    add_options = { angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
                    angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS}
  )
  simulation = project.factory.simgr(initial_state)

  # Explore the binary, but this time, instead of only looking for a state that
  # reaches the print_good_address, also find a state that does not reach 
  # will_not_succeed_address. The binary is pretty large, to save you some time,
  # everything you will need to look at is near the beginning of the address 
  # space.
  # (!)
  print_good_address = 0x80485E0
  will_not_succeed_address = 0x080485A8
  simulation.explore(find=print_good_address, avoid=will_not_succeed_address)

  if simulation.found:
    solution_state = simulation.found[0]
    print(solution_state.posix.dumps(sys.stdin.fileno()).decode())
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)
```
比起走不可能的分支
```
.text:080485F2                 push    offset s        ; "Try again."
```
我直接忽略
```
.text:080485A8 avoid_me        proc near               ; CODE XREF: main+1CA↓p
```
![](https://i.imgur.com/SKMtbZA.png)
整體解出的速度會快非常多

# 02_angr_find_condition
```pyhton
# It is very useful to be able to search for a state that reaches a certain
# instruction. However, in some cases, you may not know the address of the
# specific instruction you want to reach (or perhaps there is no single
# instruction goal.) In this challenge, you don't know which instruction
# grants you success. Instead, you just know that you want to find a state where
# the binary prints "Good Job."
#
# Angr is powerful in that it allows you to search for a states that meets an
# arbitrary condition that you specify in Python, using a predicate you define
# as a function that takes a state and returns True if you have found what you
# are looking for, and False otherwise.

import angr
import sys

def main(argv):
  path_to_binary = "/home/angr/angr-dev/test/02_angr_find_condition"
  project = angr.Project(path_to_binary)
  initial_state = project.factory.entry_state(
    add_options = { angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
                    angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS}
  )
  simulation = project.factory.simgr(initial_state)

  # Define a function that checks if you have found the state you are looking
  # for.
  def is_successful(state):
    # Dump whatever has been printed out by the binary so far into a string.
    stdout_output = state.posix.dumps(sys.stdout.fileno())

    # Return whether 'Good Job.' has been printed yet.
    # (!)
    print(stdout_output)
    return b'Good Job.\n' in stdout_output  # :boolean

  # Same as above, but this time check if the state should abort. If you return
  # False, Angr will continue to step the state. In this specific challenge, the
  # only time at which you will know you should abort is when the program prints
  # "Try again."
  def should_abort(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    print(stdout_output)
    return b'Try again.\n' in stdout_output  # :boolean

  # Tell Angr to explore the binary and find any state that is_successful identfies
  # as a successful state by returning True.
  simulation.explore(find=is_successful, avoid=should_abort)

  if simulation.found:
    solution_state = simulation.found[0]
    print(solution_state.posix.dumps(sys.stdin.fileno()).decode())
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)

```
這邊可以針對ouput不斷地進行求解

> b'Good Job.\n'
> b'Try again.\n'

![](https://i.imgur.com/LP6V2Zn.png)

# 03_angr_symbolic_registers
![](https://i.imgur.com/NHMFwOS.png)

```python
# Angr doesn't currently support reading multiple things with scanf (Ex: 
# scanf("%u %u).) You will have to tell the simulation engine to begin the
# program after scanf is called and manually inject the symbols into registers.

import angr
import claripy
import sys

def main(argv):
  path_to_binary = "/home/angr/angr-dev/test/03_angr_symbolic_registers"
  project = angr.Project(path_to_binary)

  # Sometimes, you want to specify where the program should start. The variable
  # start_address will specify where the symbolic execution engine should begin.
  # Note that we are using blank_state, not entry_state.
  # (!)
  start_address = 0x08048980  # :integer (probably hexadecimal)
  initial_state = project.factory.blank_state(
    addr=start_address,
    add_options = { angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
                    angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS}
  )

  # Create a symbolic bitvector (the datatype Angr uses to inject symbolic
  # values into the binary.) The first parameter is just a name Angr uses
  # to reference it. 
  # You will have to construct multiple bitvectors. Copy the two lines below
  # and change the variable names. To figure out how many (and of what size)
  # you need, dissassemble the binary and determine the format parameter passed
  # to scanf.
  # (!)
  password0_size_in_bits = 32  # :integer
  password0 = claripy.BVS('password0', password0_size_in_bits)
  password1_size_in_bits = 32  # :integer
  password1 = claripy.BVS('password1', password1_size_in_bits)
  password2_size_in_bits = 32  # :integer
  password2 = claripy.BVS('password2', password2_size_in_bits)

  # Set a register to a symbolic value. This is one way to inject symbols into
  # the program.
  # initial_state.regs stores a number of convenient attributes that reference
  # registers by name. For example, to set eax to password0, use:
  #
  # initial_state.regs.eax = password0
  #
  # You will have to set multiple registers to distinct bitvectors. Copy and
  # paste the line below and change the register. To determine which registers
  # to inject which symbol, dissassemble the binary and look at the instructions
  # immediately following the call to scanf.
  # (!)
  initial_state.regs.eax = password0
  initial_state.regs.ebx = password1
  initial_state.regs.edx = password2

  simulation = project.factory.simgr(initial_state)

  def is_successful(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return b'Good Job.\n' in stdout_output

  def should_abort(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return b'Try again.\n' in stdout_output  # :boolean

  simulation.explore(find=is_successful, avoid=should_abort)

  if simulation.found:
    solution_state = simulation.found[0]

    # Solve for the symbolic values. If there are multiple solutions, we only
    # care about one, so we can use eval, which returns any (but only one)
    # solution. Pass eval the bitvector you want to solve for.
    # (!)
    solution0 = solution_state.solver.eval(password0)
    solution1 = solution_state.solver.eval(password1)
    solution2 = solution_state.solver.eval(password2)
    # ...

    # Aggregate and format the solutions you computed above, and then print
    # the full string. Pay attention to the order of the integers, and the
    # expected base (decimal, octal, hexadecimal, etc).
    # solution = ???  # :string
    print("Solution:{:x} {:x} {:x}".format(solution0,solution1,solution2))
    # print(solution)
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)

```
```
.text:0804897B                 call    get_user_input
.text:08048980                 mov     [ebp+var_14], eax
.text:08048983                 mov     [ebp+var_10], ebx
.text:08048986                 mov     [ebp+var_C], edx
.text:08048989                 sub     esp, 0Ch
.text:0804898C                 push    [ebp+var_14]
```

symbolic execution 把eax ,ebx ,edx, 抽換成symbolic
![](https://i.imgur.com/IqEoL4J.png)

# 04_angr_symbolic_stack
https://wirelessr.gitbooks.io/working-life/content/gdbyu_objdump.htmlhttps://wirelessr.gitbooks.io/working-life/content/gdbyu_objdump.html

call stack
```
_somefunc:

  push ebp

  mov ebp, esp

  sub esp, ８
```
![](https://i.imgur.com/xkue5D4.png)
![](https://i.imgur.com/7iKJ6bV.png)

既然已經從ebp-0x10開始 那麼從v2起始位置就是ebp-0xc
再往前推一個byte 4 = ebp-0x8 開始
```
1. 在 _somefunc 函數回傳時用 ret 指令的另一種形式，其中包括要從堆疊中刪除的位元組數目：
   ret 8
2. 刪除 _main 函數中的清理動作：
   add esp, 8
```
依照文章好像windows api 會是ret 8
c code 會補回esp
https://sites.google.com/view/28-assembly-language/x86-assembly-%E7%9A%84-stack-frame-%E5%92%8C%E5%87%BD%E6%95%B8%E7%9A%84%E5%91%BC%E5%8F%AB%E6%85%A3%E4%BE%8B
```python
# This challenge will be more challenging than the previous challenges that you
# have encountered thus far. Since the goal of this CTF is to teach symbolic
# execution and not how to construct stack frames, these comments will work you
# through understanding what is on the stack.
#   ! ! !
# IMPORTANT: Any addresses in this script aren't necessarily right! Dissassemble
#            the binary yourself to determine the correct addresses!
#   ! ! !

import angr
import claripy
import sys

def main(argv):
  path_to_binary = "/home/angr/angr-dev/test/04_angr_symbolic_stack"
  project = angr.Project(path_to_binary)

  # For this challenge, we want to begin after the call to scanf. Note that this
  # is in the middle of a function.
  #
  # This challenge requires dealing with the stack, so you have to pay extra
  # careful attention to where you start, otherwise you will enter a condition
  # where the stack is set up incorrectly. In order to determine where after
  # scanf to start, we need to look at the dissassembly of the call and the
  # instruction immediately following it:
  #   sub    $0x4,%esp
  #   lea    -0x10(%ebp),%eax
  #   push   %eax
  #   lea    -0xc(%ebp),%eax
  #   push   %eax
  #   push   $0x80489c3
  #   call   8048370 <__isoc99_scanf@plt>
  #   add    $0x10,%esp
  # Now, the question is: do we start on the instruction immediately following
  # scanf (add $0x10,%esp), or the instruction following that (not shown)?
  # Consider what the 'add $0x10,%esp' is doing. Hint: it has to do with the
  # scanf parameters that are pushed to the stack before calling the function.
  # Given that we are not calling scanf in our Angr simulation, where should we
  # start?
  # (!)
  start_address = 0x8048697
  initial_state = project.factory.blank_state(
    addr=start_address,
    add_options = { angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
                    angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS}
  )

  # We are jumping into the middle of a function! Therefore, we need to account
  # for how the function constructs the stack. The second instruction of the
  # function is:
  #   mov    %esp,%ebp
  # At which point it allocates the part of the stack frame we plan to target:
  #   sub    $0x18,%esp
  # Note the value of esp relative to ebp. The space between them is (usually)
  # the stack space. Since esp was decreased by 0x18
  #
  #        /-------- The stack --------\
  # ebp -> |                           |
  #        |---------------------------|
  #        |                           |
  #        |---------------------------|
  #         . . . (total of 0x18 bytes)
  #         . . . Somewhere in here is
  #         . . . the data that stores
  #         . . . the result of scanf.
  # esp -> |                           |
  #        \---------------------------/
  #
  # Since we are starting after scanf, we are skipping this stack construction
  # step. To make up for this, we need to construct the stack ourselves. Let us
  # start by initializing ebp in the exact same way the program does.
  initial_state.regs.ebp = initial_state.regs.esp

  # scanf("%u %u") needs to be replaced by injecting two bitvectors. The
  # reason for this is that Angr does not (currently) automatically inject
  # symbols if scanf has more than one input parameter. This means Angr can
  # handle 'scanf("%u")', but not 'scanf("%u %u")'.
  # You can either copy and paste the line below or use a Python list.
  # (!)
  password0 = claripy.BVS('password0', 32)
  password1 = claripy.BVS('password1', 32)
  # Here is the hard part. We need to figure out what the stack looks like, at
  # least well enough to inject our symbols where we want them. In order to do
  # that, let's figure out what the parameters of scanf are:
  #   sub    $0x4,%esp
  #   lea    -0x10(%ebp),%eax
  #   push   %eax
  #   lea    -0xc(%ebp),%eax
  #   push   %eax
  #   push   $0x80489c3
  #   call   8048370 <__isoc99_scanf@plt>
  #   add    $0x10,%esp 
  # As you can see, the call to scanf looks like this:
  # scanf(  0x80489c3,   ebp - 0xc,   ebp - 0x10  )
  #      format_string    password0    password1
  #  From this, we can construct our new, more accurate stack diagram:
  #
  #            /-------- The stack --------\
  # ebp ->     |          padding          |
  #            |---------------------------|
  # ebp - 0x01 |       more padding        |
  #            |---------------------------|
  # ebp - 0x02 |     even more padding     |
  #            |---------------------------|
  #                        . . .               <- How much padding? Hint: how
  #            |---------------------------|      many bytes is password0?
  # ebp - 0x0b |   password0, second byte  |
  #            |---------------------------|
  # ebp - 0x0c |   password0, first byte   |
  #            |---------------------------|
  # ebp - 0x0d |   password1, last byte    |
  #            |---------------------------|
  #                        . . .
  #            |---------------------------|
  # ebp - 0x10 |   password1, first byte   |
  #            |---------------------------|
  #                        . . .
  #            |---------------------------|
  # esp ->     |                           |
  #            \---------------------------/
  #
  # Figure out how much space there is and allocate the necessary padding to
  # the stack by decrementing esp before you push the password bitvectors.
  padding_length_in_bytes = 8  # :integer
  initial_state.regs.esp -= padding_length_in_bytes

  # Push the variables to the stack. Make sure to push them in the right order!
  # The syntax for the following function is:
  #
  # initial_state.stack_push(bitvector)
  #
  # This will push the bitvector on the stack, and increment esp the correct
  # amount. You will need to push multiple bitvectors on the stack.
  # (!)
  initial_state.stack_push(password0)  # :bitvector (claripy.BVS, claripy.BVV, claripy.BV)
  initial_state.stack_push(password1) 

  simulation = project.factory.simgr(initial_state)

  def is_successful(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return b'Good Job.\n' in stdout_output

  def should_abort(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return b'Try again.\n' in stdout_output  # :boolean

  simulation.explore(find=is_successful, avoid=should_abort)

  if simulation.found:
    solution_state = simulation.found[0]

    solution0 = solution_state.solver.eval(password0)
    solution1 = solution_state.solver.eval(password1)
    

    solution = ' '.join(map(str, [ solution0, solution1 ]))
    print(solution)
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)
```
![](https://i.imgur.com/taMXFlz.png)

# 05_angr_symbolic_memory
```python
import angr
import claripy
import sys

def main(argv):
  path_to_binary = "/home/angr/angr-dev/test/05_angr_symbolic_memory"
  project = angr.Project(path_to_binary)

  start_address = 0x08048601
  initial_state = project.factory.blank_state(
    addr=start_address,
    add_options = { angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
                    angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS}
  )

  # The binary is calling scanf("%8s %8s %8s %8s").
  # (!)
  password0 = claripy.BVS('password0', 8*8)
  password1 = claripy.BVS('password1', 8*8)
  password2 = claripy.BVS('password2', 8*8)
  password3 = claripy.BVS('password3', 8*8)
  

  # Determine the address of the global variable to which scanf writes the user
  # input. The function 'initial_state.memory.store(address, value)' will write
  # 'value' (a bitvector) to 'address' (a memory location, as an integer.) The
  # 'address' parameter can also be a bitvector (and can be symbolic!).
  # (!)
  password0_address = 0x0A1BA1D8
  password1_address = 0x0A1BA1D0
  password2_address = 0x0A1BA1C8
  password3_address = 0x0A1BA1C0
  initial_state.memory.store(password0_address, password0)
  initial_state.memory.store(password1_address, password1)
  initial_state.memory.store(password2_address, password2)
  initial_state.memory.store(password3_address, password3)
  

  simulation = project.factory.simgr(initial_state)

  def is_successful(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return b'Good Job.\n' in stdout_output

  def should_abort(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return b'Try again.\n' in stdout_output  # :boolean
  
  simulation.explore(find=is_successful, avoid=should_abort)

  if simulation.found:
    solution_state = simulation.found[0]

    # Solve for the symbolic values. We are trying to solve for a string.
    # Therefore, we will use eval, with named parameter cast_to=bytes
    # which returns bytes that can be decoded to a string instead of an integer.
    # (!)
    solution0 = solution_state.solver.eval(password0,cast_to=bytes)
    solution1 = solution_state.solver.eval(password1,cast_to=bytes)
    solution2 = solution_state.solver.eval(password2,cast_to=bytes)
    solution3 = solution_state.solver.eval(password3,cast_to=bytes)
    # print("Solution:{:x} {:x} {:x} {:x}".format(solution0,solution1,solution2,solution3))
    # print("Solution:{} {} {} {}".format(solution0,solution1,solution2,solution3))
    print("Solution:{} {} {} {}".format(solution3.decode('utf-8'),solution2.decode('utf-8'),solution1.decode('utf-8'),solution0.decode('utf-8')))

    # print(solution)
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)

```
起始位置
![](https://i.imgur.com/re2CmH6.png)
求解四個value
![](https://i.imgur.com/QMpiLHy.png)
![](https://i.imgur.com/CTJIMJv.png)

# 06_angr_symbolic_dynamic_memory
```python
import angr
import claripy
import sys

def main(argv):
  path_to_binary = "/home/angr/angr-dev/test/06_angr_symbolic_dynamic_memory"
  project = angr.Project(path_to_binary)

  start_address = 0x08048699
  initial_state = project.factory.blank_state(
    addr=start_address,
    add_options = { angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
                    angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS}
  )

  # The binary is calling scanf("%8s %8s").
  # (!)
  password0 = claripy.BVS('password0', 8*8)
  password1 = claripy.BVS('password1', 8*8)
  # ...

  # Instead of telling the binary to write to the address of the memory
  # allocated with malloc, we can simply fake an address to any unused block of
  # memory and overwrite the pointer to the data. This will point the pointer
  # with the address of pointer_to_malloc_memory_address0 to fake_heap_address.
  # Be aware, there is more than one pointer! Analyze the binary to determine
  # global location of each pointer.
  # Note: by default, Angr stores integers in memory with big-endianness. To
  # specify to use the endianness of your architecture, use the parameter
  # endness=project.arch.memory_endness. On x86, this is little-endian.
  # (!)
  fake_heap_address0 = 0x7fff0000-0x100
  pointer_to_malloc_memory_address0 = 0x0ABCC8A4
  initial_state.memory.store(pointer_to_malloc_memory_address0, fake_heap_address0, endness=project.arch.memory_endness)
  fake_heap_address1 = 0x7fff0000-0x200
  pointer_to_malloc_memory_address1 =  0x0ABCC8AC 
  initial_state.memory.store(pointer_to_malloc_memory_address1, fake_heap_address1, endness=project.arch.memory_endness)

  # Store our symbolic values at our fake_heap_address. Look at the binary to
  # determine the offsets from the fake_heap_address where scanf writes.
  # (!)
  initial_state.memory.store(fake_heap_address0, password0)
  initial_state.memory.store(fake_heap_address1, password1)

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

    solution0 = solution_state.solver.eval(password0,cast_to=bytes)
    solution1 = solution_state.solver.eval(password1,cast_to=bytes)
    # solution = solution1+b" "+solution0;
    # solution = solution0 + b' ' + solution1
    # print(solution)
    print("Solution:{} {}".format(solution1,solution0))
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)

```
angr 也可以去偽造虛擬的 記憶體位置替換成 symbolic
```python
  fake_heap_address0 = 0x7fff0000-0x100
  pointer_to_malloc_memory_address0 = 0x0ABCC8A4
  initial_state.memory.store(pointer_to_malloc_memory_address0, fake_heap_address0, endness=project.arch.memory_endness)
  fake_heap_address1 = 0x7fff0000-0x200
  pointer_to_malloc_memory_address1 =  0x0ABCC8AC 
  initial_state.memory.store(pointer_to_malloc_memory_address1, fake_heap_address1, endness=project.arch.memory_endness)

```
![](https://i.imgur.com/1LlIpL9.png)

# 07_angr_symbolic_file
![](https://i.imgur.com/1glPl1C.png)
找到讀檔位置
```python
# This challenge could, in theory, be solved in multiple ways. However, for the
# sake of learning how to simulate an alternate filesystem, please solve this
# challenge according to structure provided below. As a challenge, once you have
# an initial solution, try solving this in an alternate way.
#
# Problem description and general solution strategy:
# The binary loads the password from a file using the fread function. If the
# password is correct, it prints "Good Job." In order to keep consistency with
# the other challenges, the input from the console is written to a file in the 
# ignore_me function. As the name suggests, ignore it, as it only exists to
# maintain consistency with other challenges.
# We want to:
# 1. Determine the file from which fread reads.
# 2. Use Angr to simulate a filesystem where that file is replaced with our own
#    simulated file.
# 3. Initialize the file with a symbolic value, which will be read with fread
#    and propogated through the program.
# 4. Solve for the symbolic input to determine the password.

import angr
import claripy
import sys

def main(argv):
  path_to_binary = "/home/angr/angr-dev/test/07_angr_symbolic_file"
  project = angr.Project(path_to_binary)

  start_address = 0x080488D6
  initial_state = project.factory.blank_state(
    addr=start_address,
    add_options = { angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
                    angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS}
  )

  # Specify some information needed to construct a simulated file. For this
  # challenge, the filename is hardcoded, but in theory, it could be symbolic. 
  # Note: to read from the file, the binary calls
  # 'fread(buffer, sizeof(char), 64, file)'.
  # (!)
  filename = "OJKSQYDP.txt"  # :string
  symbolic_file_size_bytes = 0x40

  # Construct a bitvector for the password and then store it in the file's
  # backing memory. For example, imagine a simple file, 'hello.txt':
  #
  # Hello world, my name is John.
  # ^                       ^
  # ^ address 0             ^ address 24 (count the number of characters)
  # In order to represent this in memory, we would want to write the string to
  # the beginning of the file:
  #
  # hello_txt_contents = claripy.BVV('Hello world, my name is John.', 30*8)
  #
  # Perhaps, then, we would want to replace John with a
  # symbolic variable. We would call:
  #
  # name_bitvector = claripy.BVS('symbolic_name', 4*8)
  #
  # Then, after the program calls fopen('hello.txt', 'r') and then
  # fread(buffer, sizeof(char), 30, hello_txt_file), the buffer would contain
  # the string from the file, except four symbolic bytes where the name would be
  # stored.
  # (!)
  password = claripy.BVS('password', symbolic_file_size_bytes * 8)

  # Construct the symbolic file. The file_options parameter specifies the Linux
  # file permissions (read, read/write, execute etc.) The content parameter
  # specifies from where the stream of data should be supplied. If content is
  # an instance of SimSymbolicMemory (we constructed one above), the stream will
  # contain the contents (including any symbolic contents) of the memory,
  # beginning from address zero.
  # Set the content parameter to our BVS instance that holds the symbolic data.
  # (!)
  password_file = angr.storage.SimFile(filename, content=password)
  
  # Add the symbolic file we created to the symbolic filesystem.
  initial_state.fs.insert(filename, password_file)

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

    solution = solution_state.solver.eval(password,cast_to=bytes).decode()

    print(solution)
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)

```
![](https://i.imgur.com/Ez8CTAv.png)

# 08_angr_constraints
重load 記憶體然後自行約束
![](https://i.imgur.com/MfGStRq.png)
![](https://i.imgur.com/zJD0eEN.png)
```python
# The binary asks for a 16 character password to which is applies a complex
# function and then compares with a reference string with the function
# check_equals_[reference string]. (Decompile the binary and take a look at it!)
# The source code for this function is provided here. However, the reference
# string in your version will be different than AABBCCDDEEFFGGHH:
#
# #define REFERENCE_PASSWORD = "AABBCCDDEEFFGGHH";
# int check_equals_AABBCCDDEEFFGGHH(char* to_check, size_t length) {
#   uint32_t num_correct = 0;
#   for (int i=0; i<length; ++i) {
#     if (to_check[i] == REFERENCE_PASSWORD[i]) {
#       num_correct += 1;
#     }
#   }
#   return num_correct == length;
# }
#
# ...
# 
# char* input = user_input();
# char* encrypted_input = complex_function(input);
# if (check_equals_AABBCCDDEEFFGGHH(encrypted_input, 16)) {
#   puts("Good Job.");
# } else {
#   puts("Try again.");
# }
#
# The function checks if *to_check == "AABBCCDDEEFFGGHH". Verify this yourself.
# While you, as a human, can easily determine that this function is equivalent
# to simply comparing the strings, the computer cannot. Instead the computer 
# would need to branch every time the if statement in the loop was called (16 
# times), resulting in 2^16 = 65,536 branches, which will take too long of a 
# time to evaluate for our needs.
#
# We do not know how the complex_function works, but we want to find an input
# that, when modified by complex_function, will produce the string:
# AABBCCDDEEFFGGHH.
#
# In this puzzle, your goal will be to stop the program before this function is
# called and manually constrain the to_check variable to be equal to the
# password you identify by decompiling the binary. Since, you, as a human, know
# that if the strings are equal, the program will print "Good Job.", you can
# be assured that if the program can solve for an input that makes them equal,
# the input will be the correct password.

import angr
import claripy
import sys

def main(argv):
  path_to_binary = "/home/angr/angr-dev/test/08_angr_constraints"
  project = angr.Project(path_to_binary)

  start_address = 0x08048625
  initial_state = project.factory.blank_state(
    addr=start_address,
    add_options = { angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
                    angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS}
  )

  password = claripy.BVS('password', 16*8)

  password_address = 0x0804A050
  initial_state.memory.store(password_address, password)

  simulation = project.factory.simgr(initial_state)

  # Angr will not be able to reach the point at which the binary prints out
  # 'Good Job.'. We cannot use that as the target anymore.
  # (!)
  address_to_check_constraint = 0x08048565
  simulation.explore(find=address_to_check_constraint)

  if simulation.found:
    solution_state = simulation.found[0]

    # Recall that we need to constrain the to_check parameter (see top) of the 
    # check_equals_ function. Determine the address that is being passed as the
    # parameter and load it into a bitvector so that we can constrain it.
    # (!)
    constrained_parameter_address = password_address
    constrained_parameter_size_bytes = 0x10
    constrained_parameter_bitvector = solution_state.memory.load(
      constrained_parameter_address,
      constrained_parameter_size_bytes
    )
    # We want to constrain the system to find an input that will make
    # constrained_parameter_bitvector equal the desired value.
    # (!)
    constrained_parameter_desired_value = "AUPDNNPROEZRJWKB" # :string (encoded)

    # Specify a claripy expression (using Pythonic syntax) that tests whether
    # constrained_parameter_bitvector == constrained_parameter_desired_value.
    # Add the constraint to the state to let z3 attempt to find an input that
    # will make this expression true.
    solution_state.add_constraints(constrained_parameter_bitvector == constrained_parameter_desired_value)

    # Solve for the constrained_parameter_bitvector.
    # (!)
    solution = solution_state.solver.eval(password,cast_to=bytes)
    

    print(solution)
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)

```
![](https://i.imgur.com/yU02EO4.png)

# 09_angr_hooks
![](https://i.imgur.com/j7ry5J8.png)
0x080485F2-0x080485A5=0x4d
這邊可以進行fucntion hook 感覺還蠻有用的
```python
# This level performs the following computations:
#
# 1. Get 16 bytes of user input and encrypt it.
# 2. Save the result of check_equals_AABBCCDDEEFFGGHH (or similar)
# 3. Get another 16 bytes from the user and encrypt it.
# 4. Check that it's equal to a predefined password.
#
# The ONLY part of this program that we have to worry about is #2. We will be
# replacing the call to check_equals_ with our own version, using a hook, since
# check_equals_ will run too slowly otherwise.

import angr
import claripy
import sys

def main(argv):
  path_to_binary = "/home/angr/angr-dev/test/09_angr_hooks"
  project = angr.Project(path_to_binary)

  # Since Angr can handle the initial call to scanf, we can start from the
  # beginning.
  initial_state = project.factory.entry_state(
    add_options = { angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
                    angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS}
  )

  # Hook the address of where check_equals_ is called.
  # (!)
  check_equals_called_address = 0x080485A5

  # The length parameter in angr.Hook specifies how many bytes the execution
  # engine should skip after completing the hook. This will allow hooks to
  # replace certain instructions (or groups of instructions). Determine the
  # instructions involved in calling check_equals_, and then determine how many
  # bytes are used to represent them in memory. This will be the skip length.
  # (!)
  instruction_to_skip_length = 0x4d
  @project.hook(check_equals_called_address, length=instruction_to_skip_length)
  def skip_check_equals_(state):
    # Determine the address where user input is stored. It is passed as a
    # parameter ot the check_equals_ function. Then, load the string. Reminder:
    # int check_equals_(char* to_check, int length) { ...
    user_input_buffer_address = 0x0804A054 # :integer, probably hexadecimal
    user_input_buffer_length = 0x10

    # Reminder: state.memory.load will read the stored value at the address
    # user_input_buffer_address of byte length user_input_buffer_length.
    # It will return a bitvector holding the value. This value can either be
    # symbolic or concrete, depending on what was stored there in the program.
    user_input_string = state.memory.load(
      user_input_buffer_address,
      user_input_buffer_length
    )
    
    # Determine the string this function is checking the user input against.
    # It's encoded in the name of this function; decompile the program to find
    # it.
    check_against_string = "XYMKBKUHNIQYNQXE" # :string

    # gcc uses eax to store the return value, if it is an integer. We need to
    # set eax to 1 if check_against_string == user_input_string and 0 otherwise.
    # However, since we are describing an equation to be used by z3 (not to be
    # evaluated immediately), we cannot use Python if else syntax. Instead, we 
    # have to use claripy's built in function that deals with if statements.
    # claripy.If(expression, ret_if_true, ret_if_false) will output an
    # expression that evaluates to ret_if_true if expression is true and
    # ret_if_false otherwise.
    # Think of it like the Python "value0 if expression else value1".
    state.regs.eax = claripy.If(
      user_input_string == check_against_string, 
      claripy.BVV(1, 32), 
      claripy.BVV(0, 32)
    )

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

    # Since we are allowing Angr to handle the input, retrieve it by printing
    # the contents of stdin. Use one of the early levels as a reference.
    # for i in simulation.found:
    #         solution_state = i
    #         solution = solution_state.posix.dumps(0)
    #         print("[+] Success! Solution is: {0}".format(solution.decode('utf-8')))
    solution = solution_state.posix.dumps(sys.stdin.fileno())
    print(solution)
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)

```
![](https://i.imgur.com/ffWGF0v.png)

之前看論文看到angr今天把它全部跑一次，這在找尋漏洞我覺得還蠻有用的，替換input 為symbolic，只要設定好終點在讓angr 進行約束求解，就可以讀到key還蠻有趣的，在我的靜態分析器或許可以加入這些功能。

# 參考
https://blog.csdn.net/doudoudouzoule/article/details/80899428
https://www.twblogs.net/a/5e915a8bbd9eee34209014d6
https://tyaoo.github.io/2021/03/19/Reverse%E4%B8%ADAngr%E7%9A%84%E5%88%A9%E7%94%A8/
https://www.cxyzjd.com/article/weixin_30394333/97971546
https://bbs.pediy.com/thread-264775.htm
https://bbs.pediy.com/thread-264878.htm
https://bbs.pediy.com/thread-268300.htm
https://bbs.pediy.com/thread-269990.htm
https://www.twblogs.net/a/5b8216b52b71772165af9731
https://blog.csdn.net/CSNN2019/article/details/115602659?spm=1001.2014.3001.5501
https://blog.csdn.net/A951860555/article/details/119102789#11_angr_sim_scanf_491
https://www.wangan.com/p/7fygfgbcefb38cfc

