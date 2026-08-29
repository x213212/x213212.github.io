---
title: "觀察gcc rtl合成"
date: "2023-07-02T02:08:00.002+08:00"
updated: "2023-07-02T02:08:08.356+08:00"
permalink: "/2023/07/gcc-rtl.html"
original_url: "https://x8795278.blogspot.com/2023/07/gcc-rtl.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2833456250385942749"
tags: ["GCC"]
layout: post
---

![](https://hackmd.io/_uploads/H1_dikA_n.png)

![](https://hackmd.io/_uploads/H1_dikA_n.png)

在gcc 可以下
```bash
-fdump-rtl-all-all 
```
得到gcc 執行rtl pass的優化結果，其中目前我的平台是 x86
那唯一看到rtl tree有真正執行 並且變化的 pass有三個
```
combine
reload
cprop_hardreg
```
這是在pass中所呈現的rtl tree
```rtl
(insn 31 30 32 5 (set (reg:DF 89 [ _8 ])
        (mem/u:DF (plus:DI (mult:DI (reg:DI 105)
                    (const_int 8 [0x8]))
                (symbol_ref:DI ("altitudeTable") [flags 0x2]  <var_decl 0x7f096528e120 altitudeTable>)) [1 altitudeTableD.3397[_7]+0 S8 A64])) "test.c":23:96 135 {*movdf_internal}
     (nil))
(insn 32 31 33 5 (set (reg:SI 107)
        (mem/c:SI (plus:DI (reg/f:DI 19 frame)
                (const_int -4 [0xfffffffffffffffc])) [2 iD.3409+0 S4 A32])) "test.c":23:119 75 {*movsi_internal}
     (nil))
(insn 33 32 34 5 (set (reg:DI 106)
        (sign_extend:DI (reg:SI 107))) "test.c":23:119 147 {*extendsidi2_rex64}
     (nil))
(insn 34 33 35 5 (set (reg:DF 90 [ _9 ])
        (mem/u:DF (plus:DI (mult:DI (reg:DI 106)
                    (const_int 8 [0x8]))
                (symbol_ref:DI ("altitudeTable") [flags 0x2]  <var_decl 0x7f096528e120 altitudeTable>)) [1 altitudeTableD.3397[i_15]+0 S8 A64])) "test.c":23:119 135 {*movdf_internal}
     (nil))

```
為了找出可以間接合成的指令，來寫一個pass
改良以前寫的修改gcc unroll pass的部分

```c
int plugin_init(struct plugin_name_args *plugin_info, struct plugin_gcc_version *version)
{

if (!plugin_default_version_check(version, &gcc_version))
{
printf("incompatible gcc/plugin versions\n");
return 1;
}

fprintf(stderr, "%s %s %s\n", plugin_info->full_name, version->basever, version->devphase);

detect_passinfo.pass = make_pass_detect(g);
detect_passinfo.reference_pass_name = "combine";
detect_passinfo.ref_pass_instance_number = 0;
detect_passinfo.pos_op = PASS_POS_INSERT_AFTER;

inline_passinfo.pass=make_pass_detect2(g);
inline_passinfo.reference_pass_name="combine";
inline_passinfo.ref_pass_instance_number=0;
inline_passinfo.pos_op=PASS_POS_INSERT_BEFORE;

register_callback("static_analyzer", PLUGIN_PASS_MANAGER_SETUP, NULL, &detect_passinfo);
register_callback("exinline", PLUGIN_PASS_MANAGER_SETUP, NULL, &inline_passinfo);
return 0;
}

```
簡單的插入這個plugin 在 gcc 裡面，觀察pass前後rtl tree的變化,
根據function -> basic block -> rtx
```c
fprintf(stderr, "\n===============Print ALL RTL IR BEFORE=================\n");
FOR_EACH_FUNCTION(node)
{
name = get_name(cfun->decl);

if (name != NULL)
{
fprintf(stderr, "=======Mapping node_fun:%s=========\n", name);
}
	….
calculate_dominance_info(CDI_DOMINATORS);
int count = 0;
FOR_EACH_BB_FN(bb, cfun)
{
rtx_insn *insn;
FOR_BB_INSNS(bb, insn)
if (NONDEBUG_INSN_P(insn))
{

rtx body = PATTERN(insn);
int code = INSN_CODE(insn);
fprintf(stderr, "\nbb index %d,rtl inst count %d\n", bb->index, count);
debug(insn);

expanded_location xloc = insn_location(insn);
fprintf(stderr, "source code : %s:%i\n", xloc.file, xloc.line);
count++;
}
}

pop_cfun();
}
fprintf(stderr, "\n===============Print ALL RTL IR BEFORE=================\n");

```
這是處理完的數據格式
```log
=======Mapping node_fun:main=========

bb index 2,rtl inst count 0
(insn 8 7 9 2 (set (reg:DI 5 di)
  (symbol_ref/f:DI ("*.LC0") [flags 0x2]  <var_decl 0x7febd94a02d0 *.LC0>)) "test.c":65:5 74 {*movdi_internal}
 (nil))
source code : test.c:65
Opcode number of insn: 74
Opcode of insn: *movdi_internal
===== of insn: *cmpqi_1

bb index 2,rtl inst count 1
(insn 9 8 10 2 (set (reg:QI 0 ax)
  (const_int 0 [0])) "test.c":65:5 77 {*movqi_internal}
 (nil))
source code : test.c:65
Opcode number of insn: 77
Opcode of insn: *movqi_internal
===== of insn: *cmpqi_1

```
基本上已經是比較可讀的狀況，到這邊再觀察rtl的tree就可讀，如果需要找那些pattern可以根據這些訊息來建立一個table

