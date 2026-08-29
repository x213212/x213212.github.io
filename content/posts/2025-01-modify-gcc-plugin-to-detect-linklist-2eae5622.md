---
title: "Modify the gcc plugin to detect linklist memory leaks"
date: "2025-01-04T02:08:00.006+08:00"
updated: "2025-01-04T02:19:04.293+08:00"
permalink: "/2025/01/modify-gcc-plugin-to-detect-linklist.html"
original_url: "https://x8795278.blogspot.com/2025/01/modify-gcc-plugin-to-detect-linklist.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-4220800231115776997"
tags: ["GCC"]
layout: post
---

![](https://hackmd.io/_uploads/rycJDsBLyx.png)

# Modify the gcc plugin to detect linklist memory leaks
最近又開始在看以前專案把想做的東西做完整，在以前檢測記憶體洩漏的時候有發現在linklist的部分memory leak好像沒有找到相對應的gimple 所以那大概新增這個 type就可以了
https://github.com/x213212/Static-analyzer-in-gccplugin/commit/e548d10ee978b05c0a2892b8cd4352f231ec2780
測資擴充為下面這樣
```c
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
int *foo(void);
#include <stdio.h>
#include <stdlib.h>

typedef struct Node
{
        int data;
        struct Node *next;
} Node;

Node *createNode(int value)
{
        Node *newNode = (Node *)malloc(sizeof(Node));
        if (!newNode)
        {
                printf("malloc failed\n");
                exit(EXIT_FAILURE);
        }
        newNode->data = value;
        newNode->next = NULL;
        return newNode;
}

int main()
{
        Node *head = NULL;
        Node *temp = NULL;

        for (int i = 1; i <= 5; i++)
        {
                Node *node = createNode(i);
                if (head == NULL)
                {

                        head = node;
                        temp = head;
                }
                else
                {

                        temp->next = node;
                        temp = node;
                }
        }

        temp = head;
        while (temp != NULL)
        {
                printf("%d ", temp->data);
                temp = temp->next;
        }
        printf("\n");

        temp = head;
        while (temp != NULL)
        {
                Node *next = temp->next;
                free(temp);
                temp = next;
        }
        srand(10);
        int *p;
        int test;
        for (int i = 0; i < 10; i++)
        {
                test = rand() % (10 - 0 + 1) + 0;
                p = (int *)malloc(sizeof(int) * 10);
                p[0] = 1;
                p[1] = 2;
                p[2] = 3;
                p[3] = 4;
                p[4] = 5;
                p[5] = 6;
                p[6] = 7;
                p[7] = 8;
                p[8] = 9;
                p[9] = 10;
                // printf("%d\n",p[0]);
                if (test > 5)
                        goto EXIT;
                free(p);
        }
EXIT:
        free(p);

        return 0;
}
```

![image](https://hackmd.io/_uploads/Hk-bUjSUyl.png)

其實在畫圖要開啟context sentive 這樣 我才可以走訪function去判斷返回的 value 是否為 heap-object
![image](https://hackmd.io/_uploads/rycJDsBLyx.png)
context secntive 遇到 function 是 heap-object 其實也算是一個分析點
順便修改一些makefile和一些以前寫的奇怪設定 xd

```c
 if (gimpleassignlhs && TREE_CODE(gimpleassignlhs) == COMPONENT_REF)
{
fprintf(stderr, "============COMPONENT_REF2==================\n");
tree base = TREE_OPERAND(gimpleassignlhs, 0);
tree ssaname = TREE_OPERAND(base, 0);
if (base && TREE_CODE(base) == MEM_REF)
{
// debug_tree(base);
gimple *def_stmt = SSA_NAME_DEF_STMT(ssaname);
// debug(def_stmt);
set_gimple_array(used_stmt, def_stmt, ssaname, target, NULL);
if (ssaname != target2 && !check_stmtStack2((def_stmt)))
new_search_imm_use(used_stmt, ssaname, ssaname);
}
}
if (gimpleassignrhs && TREE_CODE(gimpleassignrhs) == COMPONENT_REF)
{
fprintf(stderr, "============COMPONENT_REF3==================\n");
// debug_tree(gimpleassignrhs);
// debug(gimpleassignrhs);
tree base = TREE_OPERAND(gimpleassignrhs, 0);
if (base && TREE_CODE(base) == MEM_REF)
{
tree ssaname = TREE_OPERAND(base, 0);
// debug_tree(ssaname);
gimple *def_stmt = SSA_NAME_DEF_STMT(ssaname);
// debug(def_stmt);
set_gimple_array(used_stmt, def_stmt, ssaname, target, NULL);
if (ssaname != target2 && !check_stmtStack2((def_stmt)))
new_search_imm_use(used_stmt, ssaname, ssaname);
}
}
```
ok下一篇就來讓webassalbly gb模擬器可以support 音效

