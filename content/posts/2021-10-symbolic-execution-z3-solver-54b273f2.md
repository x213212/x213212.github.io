---
title: "symbolic execution & z3 solver"
date: "2021-10-19T01:51:00.006+08:00"
updated: "2021-10-19T01:52:48.029+08:00"
permalink: "/2021/10/symbolic-execution-z3-solver.html"
original_url: "https://x8795278.blogspot.com/2021/10/symbolic-execution-z3-solver.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6566407710282053137"
tags: ["symbolic execution"]
layout: post
---

![](https://www.nuget.org/profiles/Z3Prover/avatar?imageSize=512)

# symbolic execution

在論文最後的report 中，嘗試去添加 path constraint，得以進一步讓使用者更清晰的顯示 colect table 里相同 stmt 分支 模糊的地帶
因為 gimpler ir 有可能會有相同的 gimple stmt 名稱
可能要等最終論文發表後才可以公布我目前的程式碼，我的論文主要是實做一個靜態分析器去檢測memory leak ,pthread resource leak 等等相關研究，因為論文目標 可能 不用 smt solver 就可以得出較好的結果，這邊紀錄一下 smt & sat 的一些概念。

版权声明：本文为CSDN博主「swy_swy_swy」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/swy_swy_swy/article/details/104889142
原文链接：https://blog.csdn.net/swy_swy_swy/article/details/104979621
原文链接：https://blog.csdn.net/swy_swy_swy/article/details/105019684

一些概念的補充
https://etd.lis.nsysu.edu.tw/ETD-db/ETD-search-c/getfile?URN=etd-1031111-020007&filename=etd-1031111-020007.pdf

https://blog.csdn.net/as604049322/article/details/120279521
在這一篇文章中有紀錄z3-solver 一連串的範例我這邊來稍微整理一下。

https://blog.csdn.net/qq_37400312/article/details/108962459
AND OR IF 一些補充

https://arabelatso.github.io/2018/06/14/Z3%20API%20in%20Python/

這邊針對約束的部分去研究我們跳過前的一些數學的例子，
針對數獨這個部份去拆解

```python
from z3 import *

# 9x9 整数变量矩阵
X = [[Int(f"x_{i}_{j}") for j in range(9)]
             for i in range(9)]
#print (X)
# 每个单元格在 1,2,3,...8,9 中包含一个值
cells_c = [And(1 <= X[i][j], X[i][j] <= 9)
                   for i in range(9) for j in range(9)]
#print (cells_c)
# 每行每个数字最多出现一次
rows_c = [Distinct(X[i]) for i in range(9)]
#print (rows_c)
# 每列每个数字最多出现一次
cols_c = [Distinct([X[i][j] for i in range(9)])
                  for j in range(9)]

# 每个 3x3 方格每个数字最多出现一次
sq_c = [Distinct([X[3*i0 + i][3*j0 + j]
                      for i in range(3) for j in range(3)])
                              for i0 in range(3) for j0 in range(3)]
# 数独完整约束条件
sudoku_c = cells_c + rows_c + cols_c + sq_c

board = [
    [0, 0, 0, 6, 0, 0, 0, 3, 0],
    [5, 0, 0, 0, 0, 0, 6, 0, 0],
    [0, 9, 0, 0, 0, 5, 0, 0, 0],
    [0, 0, 4, 0, 1, 0, 0, 0, 6],
    [0, 0, 0, 4, 0, 3, 0, 0, 0],
    [8, 0, 0, 0, 9, 0, 5, 0, 0],
    [0, 0, 0, 7, 0, 0, 0, 4, 0],
    [0, 0, 5, 0, 0, 0, 0, 0, 8],
    [0, 3, 0, 0, 0, 8, 0, 0, 0]
]

def solveSudoku(board: list):
    board_c = [If(board[i][j] == 0,
                  True,
                  X[i][j] == board[i][j])
               for i in range(9) for j in range(9)]
    path = 'output.txt'
    f = open(path, 'w')
    s = Solver()
    s.add(sudoku_c + board_c)
    if s.check() == sat:
        m = s.model()
        print(str(m))
        f.write(str(m))
        f.write(str(sudoku_c + board_c))
        f.close()

        r = [[m[X[i][j]].as_long() for j in range(9)]
             for i in range(9)]
    
        return r

print (solveSudoku(board))

```
我們詳細拆解其實就是去建立每一個規則
```
And(x_0_0 >= 1, x_0_0 <= 9), And(x_0_1 >= 1, x_0_1 <= 9), And(x_0_2 >= 1, x_0_2 <= 9), And(x_0_3 >= 1, x_0_3 <= 9), And(x_0_4 >= 1, x_0_4 <= 9), And(x_0_5 >= 1, x_0_5 <= 9), And(x_0_6 >= 1, x_0_6 <= 9), And(x_0_7 >= 1, x_0_7 <= 9), And(x_0_8 >= 1, x_0_8 <= 9), And(x_1_0 >= 1, x_1_0 <= 9), And(x_1_1 >= 1, x_1_1 <= 9), And(x_1_2 >= 1, x_1_2 <= 9), And(x_1_3 >= 1, x_1_3 <= 9), And(x_1_4 >= 1, x_1_4 <= 9), And(x_1_5 >= 1, x_1_5 <= 9), And(x_1_6 >= 1, x_1_6 <= 9), And(x_1_7 >= 1, x_1_7 <= 9), And(x_1_8 >= 1, x_1_8 <= 9), And(x_2_0 >= 1, x_2_0 <= 9), And(x_2_1 >= 1, x_2_1 <= 9), And(x_2_2 >= 1, x_2_2 <= 9), And(x_2_3 >= 1, x_2_3 <= 9), And(x_2_4 >= 1, x_2_4 <= 9), And(x_2_5 >= 1, x_2_5 <= 9), And(x_2_6 >= 1, x_2_6 <= 9), And(x_2_7 >= 1, x_2_7 <= 9), And(x_2_8 >= 1, x_2_8 <= 9), And(x_3_0 >= 1, x_3_0 <= 9), And(x_3_1 >= 1, x_3_1 <= 9), And(x_3_2 >= 1, x_3_2 <= 9), And(x_3_3 >= 1, x_3_3 <= 9), And(x_3_4 >= 1, x_3_4 <= 9), And(x_3_5 >= 1, x_3_5 <= 9), And(x_3_6 >= 1, x_3_6 <= 9), And(x_3_7 >= 1, x_3_7 <= 9), And(x_3_8 >= 1, x_3_8 <= 9), And(x_4_0 >= 1, x_4_0 <= 9), And(x_4_1 >= 1, x_4_1 <= 9), And(x_4_2 >= 1, x_4_2 <= 9), And(x_4_3 >= 1, x_4_3 <= 9), And(x_4_4 >= 1, x_4_4 <= 9), And(x_4_5 >= 1, x_4_5 <= 9), And(x_4_6 >= 1, x_4_6 <= 9), And(x_4_7 >= 1, x_4_7 <= 9), And(x_4_8 >= 1, x_4_8 <= 9), And(x_5_0 >= 1, x_5_0 <= 9), And(x_5_1 >= 1, x_5_1 <= 9), And(x_5_2 >= 1, x_5_2 <= 9), And(x_5_3 >= 1, x_5_3 <= 9), And(x_5_4 >= 1, x_5_4 <= 9), And(x_5_5 >= 1, x_5_5 <= 9), And(x_5_6 >= 1, x_5_6 <= 9), And(x_5_7 >= 1, x_5_7 <= 9), And(x_5_8 >= 1, x_5_8 <= 9), And(x_6_0 >= 1, x_6_0 <= 9), And(x_6_1 >= 1, x_6_1 <= 9), And(x_6_2 >= 1, x_6_2 <= 9), And(x_6_3 >= 1, x_6_3 <= 9), And(x_6_4 >= 1, x_6_4 <= 9), And(x_6_5 >= 1, x_6_5 <= 9), And(x_6_6 >= 1, x_6_6 <= 9), And(x_6_7 >= 1, x_6_7 <= 9), And(x_6_8 >= 1, x_6_8 <= 9), And(x_7_0 >= 1, x_7_0 <= 9), And(x_7_1 >= 1, x_7_1 <= 9), And(x_7_2 >= 1, x_7_2 <= 9), And(x_7_3 >= 1, x_7_3 <= 9), And(x_7_4 >= 1, x_7_4 <= 9), And(x_7_5 >= 1, x_7_5 <= 9), And(x_7_6 >= 1, x_7_6 <= 9), And(x_7_7 >= 1, x_7_7 <= 9), And(x_7_8 >= 1, x_7_8 <= 9), And(x_8_0 >= 1, x_8_0 <= 9), And(x_8_1 >= 1, x_8_1 <= 9), And(x_8_2 >= 1, x_8_2 <= 9), And(x_8_3 >= 1, x_8_3 <= 9), And(x_8_4 >= 1, x_8_4 <= 9), And(x_8_5 >= 1, x_8_5 <= 9), And(x_8_6 >= 1, x_8_6 <= 9), And(x_8_7 >= 1, x_8_7 <= 9), And(x_8_8 >= 1, x_8_8 <= 9), 
```

```
Distinct(x_0_0,
         x_0_1,
         x_0_2,
         x_0_3,
         x_0_4,
         x_0_5,
         x_0_6,
         x_0_7,
         x_0_8), Distinct(x_1_0,
         x_1_1,
         x_1_2,
         x_1_3,
         x_1_4,
         x_1_5,
         x_1_6,
         x_1_7,
         x_1_8), Distinct(x_2_0,
         x_2_1,
         x_2_2,
         x_2_3,
         x_2_4,
         x_2_5,
         x_2_6,
         x_2_7,
         x_2_8), Distinct(x_3_0,
         x_3_1,
         x_3_2,
         x_3_3,
         x_3_4,
         x_3_5,
         x_3_6,
         x_3_7,
         x_3_8), Distinct(x_4_0,
         x_4_1,
         x_4_2,
         x_4_3,
         x_4_4,
         x_4_5,
         x_4_6,
         x_4_7,
         x_4_8), Distinct(x_5_0,
         x_5_1,
         x_5_2,
         x_5_3,
         x_5_4,
         x_5_5,
         x_5_6,
         x_5_7,
         x_5_8), Distinct(x_6_0,
         x_6_1,
         x_6_2,
         x_6_3,
         x_6_4,
         x_6_5,
         x_6_6,
         x_6_7,
         x_6_8), Distinct(x_7_0,
         x_7_1,
         x_7_2,
         x_7_3,
         x_7_4,
         x_7_5,
         x_7_6,
         x_7_7,
         x_7_8), Distinct(x_8_0,
         x_8_1,
         x_8_2,
         x_8_3,
         x_8_4,
         x_8_5,
         x_8_6,
         x_8_7,
         x_8_8), Distinct(x_0_0,
         x_1_0,
         x_2_0,
         x_3_0,
         x_4_0,
         x_5_0,
         x_6_0,
         x_7_0,
         x_8_0), Distinct(x_0_1,
         x_1_1,
         x_2_1,
         x_3_1,
         x_4_1,
         x_5_1,
         x_6_1,
         x_7_1,
         x_8_1), Distinct(x_0_2,
         x_1_2,
         x_2_2,
         x_3_2,
         x_4_2,
         x_5_2,
         x_6_2,
         x_7_2,
         x_8_2), Distinct(x_0_3,
         x_1_3,
         x_2_3,
         x_3_3,
         x_4_3,
         x_5_3,
         x_6_3,
         x_7_3,
         x_8_3), Distinct(x_0_4,
         x_1_4,
         x_2_4,
         x_3_4,
         x_4_4,
         x_5_4,
         x_6_4,
         x_7_4,
         x_8_4), Distinct(x_0_5,
         x_1_5,
         x_2_5,
         x_3_5,
         x_4_5,
         x_5_5,
         x_6_5,
         x_7_5,
         x_8_5), Distinct(x_0_6,
         x_1_6,
         x_2_6,
         x_3_6,
         x_4_6,
         x_5_6,
         x_6_6,
         x_7_6,
         x_8_6), Distinct(x_0_7,
         x_1_7,
         x_2_7,
         x_3_7,
         x_4_7,
         x_5_7,
         x_6_7,
         x_7_7,
         x_8_7), Distinct(x_0_8,
         x_1_8,
         x_2_8,
         x_3_8,
         x_4_8,
         x_5_8,
         x_6_8,
         x_7_8,
         x_8_8), Distinct(x_0_0,
         x_0_1,
         x_0_2,
         x_1_0,
         x_1_1,
         x_1_2,
         x_2_0,
         x_2_1,
         x_2_2), Distinct(x_0_3,
         x_0_4,
         x_0_5,
         x_1_3,
         x_1_4,
         x_1_5,
         x_2_3,
         x_2_4,
         x_2_5), Distinct(x_0_6,
         x_0_7,
         x_0_8,
         x_1_6,
         x_1_7,
         x_1_8,
         x_2_6,
         x_2_7,
         x_2_8), Distinct(x_3_0,
         x_3_1,
         x_3_2,
         x_4_0,
         x_4_1,
         x_4_2,
         x_5_0,
         x_5_1,
         x_5_2), Distinct(x_3_3,
         x_3_4,
         x_3_5,
         x_4_3,
         x_4_4,
         x_4_5,
         x_5_3,
         x_5_4,
         x_5_5), Distinct(x_3_6,
         x_3_7,
         x_3_8,
         x_4_6,
         x_4_7,
         x_4_8,
         x_5_6,
         x_5_7,
         x_5_8), Distinct(x_6_0,
         x_6_1,
         x_6_2,
         x_7_0,
         x_7_1,
         x_7_2,
         x_8_0,
         x_8_1,
         x_8_2), Distinct(x_6_3,
         x_6_4,
         x_6_5,
         x_7_3,
         x_7_4,
         x_7_5,
         x_8_3,
         x_8_4,
         x_8_5), Distinct(x_6_6,
         x_6_7,
         x_6_8,
         x_7_6,
         x_7_7,
         x_7_8,
         x_8_6,
         x_8_7,
         x_8_8),
```
這邊比較模糊的地帶是這裡

```
If(True, True, x_0_0 == 0), If(True, True, x_0_1 == 0), If(True, True, x_0_2 == 0), If(False, True, x_0_3 == 6), If(True, True, x_0_4 == 0), If(True, True, x_0_5 == 0), If(True, True, x_0_6 == 0), If(False, True, x_0_7 == 3), If(True, True, x_0_8 == 0), If(False, True, x_1_0 == 5), If(True, True, x_1_1 == 0), If(True, True, x_1_2 == 0), If(True, True, x_1_3 == 0), If(True, True, x_1_4 == 0), If(True, True, x_1_5 == 0), If(False, True, x_1_6 == 6), If(True, True, x_1_7 == 0), If(True, True, x_1_8 == 0), If(True, True, x_2_0 == 0), If(False, True, x_2_1 == 9), If(True, True, x_2_2 == 0), If(True, True, x_2_3 == 0), If(True, True, x_2_4 == 0), If(False, True, x_2_5 == 5), If(True, True, x_2_6 == 0), If(True, True, x_2_7 == 0), If(True, True, x_2_8 == 0), If(True, True, x_3_0 == 0), If(True, True, x_3_1 == 0), If(False, True, x_3_2 == 4), If(True, True, x_3_3 == 0), If(False, True, x_3_4 == 1), If(True, True, x_3_5 == 0), If(True, True, x_3_6 == 0), If(True, True, x_3_7 == 0), If(False, True, x_3_8 == 6), If(True, True, x_4_0 == 0), If(True, True, x_4_1 == 0), If(True, True, x_4_2 == 0), If(False, True, x_4_3 == 4), If(True, True, x_4_4 == 0), If(False, True, x_4_5 == 3), If(True, True, x_4_6 == 0), If(True, True, x_4_7 == 0), If(True, True, x_4_8 == 0), If(False, True, x_5_0 == 8), If(True, True, x_5_1 == 0), If(True, True, x_5_2 == 0), If(True, True, x_5_3 == 0), If(False, True, x_5_4 == 9), If(True, True, x_5_5 == 0), If(False, True, x_5_6 == 5), If(True, True, x_5_7 == 0), If(True, True, x_5_8 == 0), If(True, True, x_6_0 == 0), If(True, True, x_6_1 == 0), If(True, True, x_6_2 == 0), If(False, True, x_6_3 == 7), If(True, True, x_6_4 == 0), If(True, True, x_6_5 == 0), If(True, True, x_6_6 == 0), If(False, True, x_6_7 == 4), If(True, True, x_6_8 == 0), If(True, True, x_7_0 == 0), If(True, True, x_7_1 == 0), If(False, True, x_7_2 == 5), If(True, True, x_7_3 == 0), If(True, True, x_7_4 == 0), If(True, True, x_7_5 == 0), If(True, True, x_7_6 == 0), If(True, True, x_7_7 == 0), If(False, True, x_7_8 == 8), If(True, True, x_8_0 == 0), If(False, True, x_8_1 == 3), If(True, True, x_8_2 == 0), If(True, True, x_8_3 == 0), If(True, True, x_8_4 == 0), If(False, True, x_8_5 == 8), If(True, True, x_8_6 == 0), If(True, True, x_8_7 == 0), If(True, True, x_8_8 == 0)]
```
最終 output，可以看到 規則是最後一個的也就是假設
    board_c = [If(board[i][j] == 0,
                  True,
                  X[i][j] == board[i][j])
               for i in range(9) for j in range(9)]
我們會進行 sat 求解 只是 前提
這邊舉例
board[i][j] == 0
 x_i_j =  And(x_0_0 >= 1, x_0_0 <= 9)、、那些上述規則
否則的話 X[i][j] == board[i][j]
也就是X[i][j] 的解答只能是滿足 原本就填上去的數字
```
[x_6_6 = 9,
 x_4_2 = 7,
 x_1_8 = 7,
 x_3_1 = 2,
 x_0_5 = 9,
 x_2_8 = 1,
 x_4_1 = 5,
 x_7_5 = 4,
 x_6_5 = 2,
 x_8_2 = 9,
 x_5_2 = 3,
 x_4_7 = 1,
 x_6_0 = 1,
 x_7_3 = 9,
 x_7_6 = 1,
 x_0_0 = 7,
 x_4_4 = 8,
 x_6_8 = 3,
 x_4_6 = 2,
 x_2_4 = 7,
 x_5_3 = 2,
 x_3_7 = 8,
 x_5_7 = 7,
 x_1_5 = 1,
 x_0_2 = 1,
 x_2_3 = 8,
 x_8_7 = 5,
 x_3_5 = 7,
 x_6_4 = 5,
 x_1_3 = 3,
 x_3_6 = 3,
 x_6_2 = 8,
 x_8_0 = 4,
 x_3_0 = 9,
 x_8_6 = 7,
 x_4_8 = 9,
 x_1_7 = 9,
 x_7_7 = 6,
 x_8_3 = 1,
 x_2_6 = 4,
 x_7_0 = 2,
 x_0_8 = 5,
 x_5_8 = 4,
 x_0_1 = 4,
 x_0_4 = 2,
 x_5_5 = 6,
 x_2_2 = 6,
 x_4_0 = 6,
 x_8_8 = 2,
 x_6_1 = 6,
 x_2_0 = 3,
 x_3_3 = 5,
 x_7_1 = 7,
 x_1_4 = 4,
 x_7_4 = 3,
 x_8_4 = 6,
 x_0_6 = 8,
 x_2_7 = 2,
 x_1_2 = 2,
 x_5_1 = 1,
 x_1_1 = 8,
 x_8_5 = 8,
 x_8_1 = 3,
 x_7_8 = 8,
 x_7_2 = 5,
 x_6_7 = 4,
 x_6_3 = 7,
 x_5_6 = 5,
 x_5_4 = 9,
 x_5_0 = 8,
 x_4_5 = 3,
 x_4_3 = 4,
 x_3_8 = 6,
 x_3_4 = 1,
 x_3_2 = 4,
 x_2_5 = 5,
 x_2_1 = 9,
 x_1_6 = 6,
 x_1_0 = 5,
 x_0_7 = 3,
 x_0_3 = 6]
```
整個可以把它理解是在對 這個  x_x_y = ans 去求解

