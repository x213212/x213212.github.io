---
title: "Study ASLi"
date: "2023-10-29T11:15:00.005+08:00"
updated: "2023-10-31T23:51:43.798+08:00"
permalink: "/2023/10/install-asli.html"
original_url: "https://x8795278.blogspot.com/2023/10/install-asli.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5861928947848437304"
tags: ["arm", "asli"]
layout: post
---

![](https://hackmd.io/_uploads/HJelwrjz6.png)

# Using ASLi with Arm's v8.6-A ISA specification
https://alastairreid.github.io/using-asli/
在這篇文章有提到說怎麼安裝和使用ASLi 也就是
```
ASLi is an interpreter for Arm’s Architecture Specification Language.
```
實際上ASLi 版本已經 0.2.0了
![](https://hackmd.io/_uploads/HJelwrjz6.png)
一些安裝的步驟會發生改變來更新一下

這個網站的人使用done來管理專案了
```bash
git clone https://github.com/alastairreid/mra_tools.git
git clone https://github.com/alastairreid/asl-interpreter.git
make -C asl-interpreter asli
```
原版的可以讀這裡
https://github.com/ARM-software/asl-interpreter

# install asl-interpreter
安裝大概分兩塊先處理asl-interpreter,
其中ocaml 直接升級到 5.1.0以上，z3也一樣,pprint版本我是控制在pprint.20200226
```bash
# environment setup
opam init
eval $(opam env)
# install given version of the compiler
opam switch create 5.1.0
eval $(opam env)
# check you got what you want
which ocaml
ocaml -version
opam install z3
opam install menhir
opam install ocamlfind
opam install ott
opam install linenoise
opam install pprint
opam install zarith
opam install alcotest
eval `opam config env`
```
在找尋可用的軟體版本可以用
```bash
opam list pprint
opam install pprint.20200226
opam switch  pprint.20200226
```
查看opam lib 也可以查看
https://opam.ocaml.org/packages/z3/z3.4.12.2-1/找到相對應版本
在pprint.20200226這個版本是可以編譯完asl-interpreter.git
不然會遇到下列錯誤
```error
Error: This expression has type PPrintEngine.documentbut an expression was expected of type document
```
```bash
make install
            _____  _       _    ___________________________________
    /\     / ____|| |     (_)   ASL interpreter                    
   /  \   | (___  | |      _    Copyright Arm Limited (c) 2017-2019
  / /\ \   \___ \ | |     | |                                      
 / ____ \  ____) || |____ | |   ASL 0.2.0 alpha
/_/    \_\|_____/ |______||_|   ___________________________________

Type :? for help
ASLi> 1+1
2
ASLi> 2+2
4
ASLi> 3+3
6
ASLi> bits(32) x = ZeroExtend('11', 32);
ASLi> x
32'00000000000000000000000000000011'
ASLi> 
```
到這邊 asli 就安裝完畢了

# install mra_tools
再來是安裝mra_tools
```bash
git clone https://github.com/alastairreid/mra_tools
cd mra_tools
mkdir -p v8.6
cd v8.6

wget https://developer.arm.com/-/media/developer/products/architecture/armv8-a-architecture/2019-12/SysReg_xml_v86A-2019-12.tar.gz
wget https://developer.arm.com/-/media/developer/products/architecture/armv8-a-architecture/2019-12/A64_ISA_xml_v86A-2019-12.tar.gz
wget https://developer.arm.com/-/media/developer/products/architecture/armv8-a-architecture/2019-12/AArch32_ISA_xml_v86A-2019-12.tar.gz

tar zxf A64_ISA_xml_v86A-2019-12.tar.gz
tar zxf AArch32_ISA_xml_v86A-2019-12.tar.gz
tar zxf SysReg_xml_v86A-2019-12.tar.gz

cd ..

make all
```
順利的話會看到這些output
```bash
mkdir -p arch
bin/reg2asl.py v8.6/SysReg_xml_v86A-2019-12 -o arch/regs.asl
mkdir -p arch
bin/instrs2asl.py --altslicesyntax --demangle --verbose -oarch/arch v8.6/ISA_AArch32_xml_v86A-2019-12 v8.6/ISA_A64_xml_v86A-2019-12 
Selecting entire architecture
Reading decoder v8.6/ISA_A64_xml_v86A-2019-12/encodingindex.xml
Reading decoder v8.6/ISA_AArch32_xml_v86A-2019-12/t32_encindex.xml
Reading decoder v8.6/ISA_AArch32_xml_v86A-2019-12/a32_encindex.xml
Keeping entire specification
Writing instruction encodings to arch/arch.tag
Writing instructions to arch/arch_instrs.asl
Writing instruction decoder to arch/arch_decode.asl
Writing ASL definitions to arch/arch.asl
patch -Np0 < arch.patch
patching file arch/arch.asl
patching file arch/arch_instrs.asl
Hunk #1 succeeded at 20178 with fuzz 2 (offset 19948 lines).
```

# run ASLi
```bash
asli prelude.asl ../mra_tools/arch/regs.asl ../mra_tools/types.asl ../mra_tools/arch/arch.asl ../mra_tools/arch/arch_instrs.asl ../mra_tools/arch/arch_decode.asl ../mra_tools/support/aes.asl ../mra_tools/support/barriers.asl ../mra_tools/support/debug.asl ../mra_tools/support/feature.asl ../mra_tools/support/hints.asl ../mra_tools/support/interrupts.asl ../mra_tools/support/memory.asl ../mra_tools/support/stubs.asl ../mra_tools/support/fetchdecode.asl
            _____  _       _    ___________________________________
    /\     / ____|| |     (_)   ASL interpreter                    
   /  \   | (___  | |      _    Copyright Arm Limited (c) 2017-2019
  / /\ \   \___ \ | |     | |                                      
 / ____ \  ____) || |____ | |   ASL 0.2.0 alpha
/_/    \_\|_____/ |______||_|   ___________________________________

Type :? for help
ASLi> :project tests/test.prj
Loading ELF file tests/test_O2.elf.
Entry point = 0x400168
Test
Program exited by writing ^D to TUBE
Exception taken
ASLi> 
Fatal error: exception Stdlib.Sys.Break
```
這邊可以看到他可以以:project tests/test.prj 形式去開啟專案
這個專案很像bash ,只不過從 linux 的指令 變成 一連串的 ASLi的指令.
    
# asl code
```
root@HOME-X213212:~/x21321219/arm/mra_tools/arch# ll
total 9472
drwxr-xr-x 2 root root    4096 Oct 29 03:33 ./
drwxr-xr-x 7 root root    4096 Oct 29 03:32 ../
-rw-r--r-- 1 root root  678438 Oct 29 03:33 arch.asl
-rw-r--r-- 1 root root 1698510 Oct 29 03:33 arch.tag
-rw-r--r-- 1 root root  721260 Oct 29 03:33 arch_decode.asl
-rw-r--r-- 1 root root 3229167 Oct 29 03:33 arch_instrs.asl
-rw-r--r-- 1 root root 3229271 Oct 29 03:33 arch_instrs.asl.orig
-rw-r--r-- 1 root root  119022 Oct 29 03:33 regs.asl
```
```asl

__instruction aarch32_CSDB_A
    __encoding aarch32_CSDB_A1_A
        __instruction_set A32
        __field cond 28 +: 4
        __opcode 'xxxx0011 00100000 xxxxxxxx 00010100'
        __guard cond != '1111'
        __unpredictable_unless 15 == '1'
        __unpredictable_unless 14 == '1'
        __unpredictable_unless 13 == '1'
        __unpredictable_unless 12 == '1'
        __unpredictable_unless 11 == '0'
        __unpredictable_unless 10 == '0'
        __unpredictable_unless 9 == '0'
        __unpredictable_unless 8 == '0'
        __decode
            if cond != '1110' then UNPREDICTABLE;      // CSDB must be encoded with AL condition

    __encoding aarch32_CSDB_T1_A
        __instruction_set T32
        __opcode '11110011 1010xxxx 10x0x000 00010100'
        __guard TRUE
        __unpredictable_unless 19 == '1'
        __unpredictable_unless 18 == '1'
        __unpredictable_unless 17 == '1'
        __unpredictable_unless 16 == '1'
        __unpredictable_unless 13 == '0'
        __unpredictable_unless 11 == '0'
        __decode
            if InITBlock() then UNPREDICTABLE;

    __execute __conditional
        
        ConsumptionOfSpeculativeDataBarrier();

__instruction aarch32_VST3_m_A
    __encoding aarch32_VST3_m_T1A1_A
        __instruction_set A32
        __field D 22 +: 1
        __field Rn 16 +: 4
        __field Vd 12 +: 4
        __field itype 8 +: 4
        __field size 6 +: 2
        __field align 4 +: 2
        __field Rm 0 +: 4
        __opcode '11110100 0x00xxxx xxxx010x xxxxxxxx'
        __guard TRUE
        __decode
            if size == '11' || align[1] == '1' then UNDEFINED;
            case itype of
                when '0100'
                    inc = 1;
                when '0101'
                    inc = 2;
                otherwise
                    SEE "Related encodings";
            alignment = if align[0] == '0' then 1 else 8;
            ebytes = 1 << UInt(size);  elements = 8 DIV ebytes;
            d = UInt(D:Vd);  d2 = d + inc;  d3 = d2 + inc;  n = UInt(Rn);  m = UInt(Rm);
            wback = (m != 15);  register_index = (m != 15 && m != 13);
            if n == 15 || d3 > 31 then UNPREDICTABLE;

```
# asli.ml
```asl

let banner = [
    {|            _____  _       _    ___________________________________|};
    {|    /\     / ____|| |     (_)   ASL interpreter                    |};
    {|   /  \   | (___  | |      _    Copyright Arm Limited (c) 2017-2019|};
    {|  / /\ \   \___ \ | |     | |                                      |};
    {| / ____ \  ____) || |____ | |   |} ^ version;
    {|/_/    \_\|_____/ |______||_|   ___________________________________|}
]
let usage_msg =
    ( version
    ^ "\nusage: asl <options> <file1> ... <fileN>\n"
    )

let _ =
  Arg.parse options
    (fun s -> opt_filenames := (!opt_filenames) @ [s])
    usage_msg

let main () =
    if !opt_print_version then Printf.printf "%s\n" version
    else begin
        List.iter print_endline banner;
        print_endline "\nType :? for help";
        let t  = LoadASL.read_file "prelude.asl" true !opt_verbose in
        let ts = List.map (fun filename ->
            if Utils.endswith filename ".spec" then begin
                LoadASL.read_spec filename !opt_verbose
            end else if Utils.endswith filename ".asl" then begin
                LoadASL.read_file filename false !opt_verbose
            end else begin
                failwith ("Unrecognized file suffix on "^filename)
            end
        ) !opt_filenames
        in

        if !opt_verbose then Printf.printf "Building evaluation environment\n";
        let env = (try
            Eval.build_evaluation_environment (List.concat (t::ts))
        with
        | Value.EvalError (loc, msg) ->
            Printf.printf "  %s: Evaluation error: %s\n" (pp_loc loc) msg;
            exit 1
        ) in
        if !opt_verbose then Printf.printf "Built evaluation environment\n";

        LNoise.history_load ~filename:"asl_history" |> ignore;
        LNoise.history_set ~max_length:100 |> ignore;
        repl (TC.Env.mkEnv TC.env0) (Cpu.mkCPU env)
    end

let _ =ignore(main ())

(****************************************************************
 * End
 ****************************************************************)

```

```asl
__decode A64
    // A64
    case (29 +: 3, 24 +: 5, 0 +: 24) of
        when (_, '0000x', _) =>
            // reserved
            case (29 +: 3, 25 +: 4, 16 +: 9, 0 +: 16) of
                when ('000', _, '000000000', _) => // perm_undef
                    __field imm16 0 +: 16
                    case () of
                        when () => __encoding aarch64_udf // UDF_only_perm_undef
                when (_, _, !'000000000', _) => __UNPREDICTABLE
                when (!'000', _, _, _) => __UNPREDICTABLE
        when (_, '00011', _) => __UNPREDICTABLE
        when (_, '0010x', _) =>
            // sve
            case (29 +: 3, 25 +: 4, 23 +: 2, 22 +: 1, 17 +: 5, 16 +: 1, 10 +: 6, 0 +: 10) of
                when ('000', _, '0x', _, '0xxxx', _, 'x1xxxx', _) =>
                    // sve_int_muladd_pred
                    case (24 +: 8, 22 +: 2, 21 +: 1, 16 +: 5, 15 +: 1, 14 +: 1, 0 +: 14) of
                        when (_, _, _, _, '0', _, _) => // sve_int_mlas_vvv_pred
                            __field size 22 +: 2
                            __field Zm 16 +: 5
                            __field op 13 +: 1
                            __field Pg 10 +: 3
                            __field Zn 5 +: 5
                            __field Zda 0 +: 5
                            case (op) of
                                when ('0') => __encoding MLA_Z_P_ZZZ__ // mla_z_p_zzz_
                                when ('1') => __encoding MLS_Z_P_ZZZ__ // mls_z_p_zzz_
                        when (_, _, _, _, '1', _, _) => // sve_int_mladdsub_vvv_pred
                            __field size 22 +: 2
                            __field Zm 16 +: 5
                            __field op 13 +: 1
                            __field Pg 10 +: 3
                            __field Za 5 +: 5
                            __field Zdn 0 +: 5
                            case (op) of
                                when ('0') => __encoding MAD_Z_P_ZZZ__ // mad_z_p_zzz_
                                when ('1') => __encoding MSB_Z_P_ZZZ__ // msb_z_p_zzz_
```
在arm/asl-interpreter/bin/asli.ml
應該可以找到相對應的入口點
```
    | [":run"] ->
        (try
            while true do
                cpu.step ()
            done
        with
        | Value.Throw (_, Primops.Exc_ExceptionTaken) ->
            Printf.printf "Exception taken\n"
        )
```

# cpu.ml
```

let mkCPU (env : Eval.Env.t): cpu =
    let loc = AST.Unknown in

    let reset (_ : unit): unit =
        Eval.eval_proccall loc env (AST.FIdent ("__TakeColdReset", 0)) [] []

    and step (_ : unit): unit =
        Eval.eval_proccall loc env (AST.FIdent ("__InstructionExecute", 0)) [] []

    and getPC (_ : unit): Primops.bigint =
        let r = Eval.eval_funcall loc env (AST.FIdent ("__getPC", 0)) [] [] in
        Value.to_integer loc r

    and setPC (x : Primops.bigint): unit =
        let a = Value.VInt x in
        Eval.eval_proccall loc env (AST.FIdent ("__setPC", 0)) [] [a]

    and elfwrite (addr: Int64.t) (b: char): unit =
        let a = Value.VBits (Primops.mkBits 64 (Z.of_int64 addr)) in
        let b = Value.VBits (Primops.mkBits  8 (Z.of_int (Char.code b))) in
        Eval.eval_proccall loc env (AST.FIdent ("__ELFWriteMemory", 0)) [] [a; b]

    and opcode (iset: string) (opcode: Primops.bigint): unit =
        let op = Value.VBits (Primops.prim_cvt_int_bits (Z.of_int 32) opcode) in
        let decoder = Eval.Env.getDecoder env (Ident iset) in
        Eval.eval_decode_case AST.Unknown env decoder op
    in
    {
        env      = env;
        reset    = reset;
        step     = step;
        getPC    = getPC;
        setPC    = setPC;
        elfwrite = elfwrite;
        opcode   = opcode
    }

```
    

# 觀察專案進入點
前面大致了解架構來看一下內部
```
__TakeColdReset();

:elf tests/test_O2.elf
_PC  = 0x400168[63:0];
SP[] = 0x100000[63:0];

:set -trace:instr
:set -trace:fun
:set -trace:prim
:set -trace:write

:run
```
wsl 目前不能安裝arm toolchain 暫且用 ida pro 觀看elf執行檔案的 call flow,
作者說用 write 寫 ascii
    
    ```
    The example binary writes the word “Test” to a serial port and then writes the ASCII character EOT (end of transmission) to stop the interpreter. This produces output like this
    
    ```

![](https://hackmd.io/_uploads/r19NMmTz6.png)
Entry point = 0x400168
![](https://hackmd.io/_uploads/HykJm7pMT.png)

print_sting
![](https://hackmd.io/_uploads/SJ72QQTGp.png)

這邊可能發生 print_sting  inline 到 main function
![](https://hackmd.io/_uploads/SylRXQTfT.png)

實際上可能直接使用x2的值
  LDRB            W0, [X2],#1 ; "est\n"
目前沒arm toolchain 環境 大概研究這邊
    
# asli.ml
找尋如何解析elf
```
     | [":elf"; file] ->
        Printf.printf "Loading ELF file %s.\n" file;
        let entry = Elf.load_file file cpu.elfwrite in
        Printf.printf "Entry point = 0x%Lx\n" entry
```
# cpu.ml
```
        and elfwrite (addr: Int64.t) (b: char): unit =
        let a = Value.VBits (Primops.mkBits 64 (Z.of_int64 addr)) in
        let b = Value.VBits (Primops.mkBits  8 (Z.of_int (Char.code b))) in
        Eval.eval_proccall loc env (AST.FIdent ("__ELFWriteMemory", 0)) [] [a; b]

```
# memory.asl
```
    __ELFWriteMemory(bits(64) address, bits(8) val)
    __WriteRAM(52, 1, __Memory, address[0 +: 52], val);
    return;
```
設置 pc 和 stack 後 ,cpu 開始逐步往下執行
# cpu.ml
```
        and step (_ : unit): unit =
        Eval.eval_proccall loc env (AST.FIdent ("__InstructionExecute", 0)) [] []

```

# fetchdecode.asl
觀察怎麼fetchecode

```
    
__InstructionExecute()
    try
        __BranchTaken = FALSE;
        bits(64) pc   = ThisInstrAddr();
        (enc, instr)  = __FetchInstr(pc);
        __SetThisInstrDetails(enc, instr, __DefaultCond(enc));
        __DecodeExecute(enc, instr);

   
```
(enc, instr)  = __FetchInstr(pc);
這邊是處理 64,32,__T16,__T32
```
    
(__InstrEnc, bits(32)) __FetchInstr(bits(64) pc)
    __InstrEnc enc;
    bits(32)   instr;

    CheckSoftwareStep();

    if PSTATE.nRW == '0' then
        AArch64.CheckPCAlignment();
        enc = __A64;
        instr = AArch64.MemSingle[pc, 4, AccType_IFETCH, TRUE];
        AArch64.CheckIllegalState();
    else
        AArch32.CheckPCAlignment();
        if PSTATE.T == '1' then
            hw1 = AArch32.MemSingle[pc[31:0], 2, AccType_IFETCH, TRUE];
            isT16 = UInt(hw1[15:11]) < UInt('11101');
            if isT16 then
                enc = __T16;
                instr = Zeros(16) : hw1;
            else
                hw2 = AArch32.MemSingle[pc[31:0]+2, 2, AccType_IFETCH, TRUE];
                enc   = __T32;
                instr = hw1 : hw2;
        else
            enc   = __A32;
            instr = AArch32.MemSingle[pc[31:0], 4, AccType_IFETCH, TRUE];
        AArch32.CheckIllegalState();

    return (enc, instr);

```
                                            
# arch.asl
檢查 AArch64 alignment
```
    AArch64.CheckPCAlignment()
    bits(64) pc = ThisInstrAddr();
    if pc[1:0] != '00' then
        AArch64.PCAlignmentFault();
```
檢查 AArch32 alignment

```
    AArch32.CheckPCAlignment()

    bits(32) pc = ThisInstrAddr();
    if (CurrentInstrSet() == InstrSet_A32 && pc[1] == '1') || pc[0] == '1' then
        if AArch32.GeneralExceptionsToAArch64() then AArch64.PCAlignmentFault();

        // Generate an Alignment fault Prefetch Abort exception
        vaddress = pc;
        acctype = AccType_IFETCH;
        iswrite = FALSE;
        secondstage = FALSE;
        AArch32.Abort(vaddress, AArch32.AlignmentFault(acctype, iswrite, secondstage));

```
# __DefaultCond
```
給指令一個預設的 cond,可能最後會在某一個狀態更新掉cond裡面的值
// Default condition for an instruction with encoding 'enc'.
// This may be overridden for instructions with explicit condition field.
bits(4) __DefaultCond(__InstrEnc enc)
    if enc IN {__A64, __A32} || PSTATE.IT[3:0] == Zeros(4) then
        cond = 0xE[3:0];
    else
        cond = PSTATE.IT[7:4];
    return cond;
 __SetThisInstrDetails(enc, instr, __DefaultCond(enc));

```
# decode                    
到這邊已經知道 指令是否合法和 屬於哪一種指令集架構
   return (enc, instr);
```
__DecodeExecute(__InstrEnc enc, bits(32) instr)
    case enc of
        when __A64
            ExecuteA64(instr);
        when __A32
            ExecuteA32(instr);
        when __T16
            ExecuteT16(instr[15:0]);
        when __T32
            ExecuteT32(instr[31:16], instr[15:0]);
    return;
```
                                            
# Execute
```
ExecuteA64(bits(32) instr)
    __decode A64 instr;

ExecuteA32(bits(32) instr)
    __decode A32 instr;

ExecuteT32(bits(16) hw1, bits(16) hw2)
    __decode T32 (hw1 : hw2);

ExecuteT16(bits(16) instr)
    __decode T16 instr;

```

這邊應該是在ram/tool中將xml 轉成tree之類的東西，我們的inst丟進來進行查表，並更根據不同的指令操作ocaml 模擬出來的 register
                                            

# arch_decode.asl

```
__decode A64
    // A64
    case (29 +: 3, 24 +: 5, 0 +: 24) of
        when (_, '0000x', _) =>
            // reserved
            case (29 +: 3, 25 +: 4, 16 +: 9, 0 +: 16) of
                when ('000', _, '000000000', _) => // perm_undef
                    __field imm16 0 +: 16
                    case () of
                        when () => __encoding aarch64_udf // UDF_only_perm_undef
                when (_, _, !'000000000', _) => __UNPREDICTABLE
                when (!'000', _, _, _) => __UNPREDICTABLE
        when (_, '00011', _) => __UNPREDICTABLE
        when (_, '0010x', _) =>
....
                            when (_, _, _, _, '1', _, _) => // sve_int_mladdsub_vvv_pred
                            __field size 22 +: 2
                            __field Zm 16 +: 5
                            __field op 13 +: 1
                            __field Pg 10 +: 3
                            __field Za 5 +: 5
                            __field Zdn 0 +: 5
                            case (op) of
                                when ('0') => __encoding MAD_Z_P_ZZZ__ // mad_z_p_zzz_
                                when ('1') => __encoding MSB_Z_P_ZZZ__ // msb_z_p_zzz_
                when ('000', _, '0x', _, '0xxxx', _, '000xxx', _) =>
                                          
```
    

# arch_instrs.asl
可以看到最終是呼叫 __encoding ,從inst根據指令的type將該指令某幾個bit切到相對應的ocaml variable
```
    __instruction FMAD_Z_P_ZZZ__
    __encoding FMAD_Z_P_ZZZ__
        __instruction_set A64
        __field size 22 +: 2
        __field Za 16 +: 5
        __field Pg 10 +: 3
        __field Zm 5 +: 5
        __field Zdn 0 +: 5
        __opcode '01100101 xx1xxxxx 100xxxxx xxxxxxxx'
        __guard TRUE
        __decode
            if !HaveSVE() then UNDEFINED;
            if size == '00' then UNDEFINED;
            integer esize = 8 << UInt(size);
            integer g = UInt(Pg);
            integer dn = UInt(Zdn);
            integer m = UInt(Zm);
            integer a = UInt(Za);
            boolean op1_neg = FALSE;
            boolean op3_neg = FALSE;
```
在paser 有可能會有一段decode完 執行會做哪些操作__execute， __execute __conditional ,再根據前面設定的 ocmal 的 variable進行操作，以此來模擬操作cpu的 register

```
    __execute
        CheckSVEEnabled();
        integer elements = VL DIV esize;
        bits(PL) mask = P[g];
        bits(VL) operand1 = Z[dn];
        bits(VL) operand2 = Z[m];
        bits(VL) operand3 = Z[a];
        bits(VL) result;
        
        for e = 0 to elements-1
            bits(esize) element1 = Elem[operand1, e, esize];
            bits(esize) element2 = Elem[operand2, e, esize];
            bits(esize) element3 = Elem[operand3, e, esize];
            
            if ElemP[mask, e, esize] == '1' then
                if op1_neg then element1 = FPNeg(element1);
                if op3_neg then element3 = FPNeg(element3);
                Elem[result, e, esize] = FPMulAdd(element3, element1, element2, FPCR);
            else
                Elem[result, e, esize] = element1;
        
        Z[dn] = result;
```

到這邊大概了解怎麼執行一行指令
    
# 研究xml 與 ocaml 關聯
## instrs2asl.py
前面已經將大致流程致流程致流程走過一次，大概就是將 arm 將isa xml 進行 parsing 然後在模擬器decode完成時候查詢這些asl code 再來根據這些ocaml variable 來模擬操作register.     
```
bin/instrs2asl.py --altslicesyntax --demangle --verbose -oarch/arch v8.6/ISA_AArch32_xml_v86A-2019-12 v8.6/ISA_A64_xml_v86A-2019-12 
Selecting entire architecture
Reading decoder v8.6/ISA_A64_xml_v86A-2019-12/encodingindex.xml
Reading decoder v8.6/ISA_AArch32_xml_v86A-2019-12/t32_encindex.xml
Reading decoder v8.6/ISA_AArch32_xml_v86A-2019-12/a32_encindex.xml
Keeping entire specification
Writing instruction encodings to arch/arch.tag
Writing instructions to arch/arch_instrs.asl
Writing instruction decoder to arch/arch_decode.asl
Writing ASL definitions to arch/arch.asl
patch -Np0 < arch.patch
patching file arch/arch.asl
patching file arch/arch_instrs.asl
Hunk #1 succeeded at 20178 with fuzz 2 (offset 19948 lines).
```
改動一下print就可以看到instruction name                       
```
 def emit_asl_syntax(self, ofile):
        print("__instruction "+ deslash(self.name), file=ofile)
        print( deslash(self.name))
```
             
```
aarch64_vector_arithmetic_binary_uniform_div_fp16
0x101110 010xxxxx 001111xx xxxxxxxx
0x101110 0x1xxxxx 111111xx xxxxxxxx
aarch64_vector_arithmetic_binary_element_mul_acc_long
0xx01111 xxxxxxxx 0x10x0xx xxxxxxxx
aarch64_float_arithmetic_max_min
00011110 xx1xxxxx 01xx10xx xxxxxxxx
Writing instruction decoder to arch/arch_decode.asl
Writing ASL definitions to arch/arch.asl
patch -Np0 < arch.patch
patching file arch/arch.asl
patching file arch/arch_instrs.asl
Hunk #1 succeeded at 20178 with fuzz 2 (offset 19948 lines).
```
再查看 instrs2asl.py
可以看到 instr2asl讀取三個xml 格式檔案
```
Reading decoder v8.6/ISA_A64_xml_v86A-2019-12/encodingindex.xml
Reading decoder v8.6/ISA_AArch32_xml_v86A-2019-12/t32_encindex.xml
Reading decoder v8.6/ISA_AArch32_xml_v86A-2019-12/a32_encindex.xml
```
可以觀察到之前有假設的這是一個查表的tree
```
    when (_, '0010x', _) =>
            // sve
            case (29 +: 3, 25 +: 4, 23 +: 2, 22 +: 1, 17 +: 5, 16 +: 1, 10 +: 6, 0 +: 10) of
                when ('000', _, '0x', _, '0xxxx', _, 'x1xxxx', _) =>
                    // sve_int_muladd_pred
                    case (24 +: 8, 22 +: 2, 21 +: 1, 16 +: 5, 15 +: 1, 14 +: 1, 0 +: 14) of
                        when (_, _, _, _, '0', _, _) => // sve_int_mlas_vvv_pred
                            __field size 22 +: 2
                            __field Zm 16 +: 5
                            __field op 13 +: 1
                            __field Pg 10 +: 3
                            __field Zn 5 +: 5
                            __field Zda 0 +: 5
                            case (op) of
                                when ('0') => __encoding MLA_Z_P_ZZZ__ // mla_z_p_zzz_
                                when ('1') => __encoding MLS_Z_P_ZZZ__ // mls_z_p_zzz_
                        when (_, _, _, _, '1', _, _) => // sve_int_mladdsub_vvv_pred
                            __field size 22 +: 2
                            __field Zm 16 +: 5
                            __field op 13 +: 1
                            __field Pg 10 +: 3
                            __field Za 5 +: 5
                            __field Zdn 0 +: 5
                            case (op) of
                                when ('0') => __encoding MAD_Z_P_ZZZ__ // mad_z_p_zzz_
                                when ('1') => __encoding MSB_Z_P_ZZZ__ // msb_z_p_zzz_
```
也就是以sve_int_mlas_vvv_pred 來說可以對印到
```xml
    <iclass_sect id="sve_int_mlas_vvv_pred" title="SVE integer multiply-accumulate writing addend (predicated)">
    <regdiagram form="32" psname="">
      <box hibit="31" width="8" settings="8">
        <c>0</c>
        <c>0</c>
        <c>0</c>
        <c>0</c>
        <c>0</c>
        <c>1</c>
        <c>0</c>
        <c>0</c>
      </box>
      <box hibit="23" width="2" name="size" usename="1">
        <c colspan="2"></c>
      </box>
      <box hibit="21" settings="1">
        <c>0</c>
      </box>
      <box hibit="20" width="5" name="Zm" usename="1">
        <c colspan="5"></c>
      </box>
      <box hibit="15" width="2" settings="2">
        <c>0</c>
        <c>1</c>
      </box>
      <box hibit="13" name="op" usename="1">
        <c></c>
      </box>
      <box hibit="12" width="3" name="Pg" usename="1">
        <c colspan="3"></c>
      </box>
      <box hibit="9" width="5" name="Zn" usename="1">
        <c colspan="5"></c>
      </box>
      <box hibit="4" width="5" name="Zda" usename="1">
        <c colspan="5"></c>
      </box>
    </regdiagram>
    <instructiontable iclass="sve_int_mlas_vvv_pred" cols="3">
      <col colno="1" printwidth="15*" />
      <col colno="2" printwidth="18*" />
      <col colno="3" printwidth="10*" />
      <thead class="instructiontable">
        <tr id="heading1">
          <th colno="1" class="bitfields-heading">Decode fields</th>
          <th rowspan="2" class="iformname">Instruction page</th>
          <th rowspan="2" class="enctags">Encoding</th>
        </tr>
        <tr id="heading2">
          <th class="bitfields">op</th>
        </tr>
      </thead>
      <tbody>
        <tr class="instructiontable" encname="mla_z_p_zzz_" iformfile="mla_z_p_zzz.xml" first="t" last="t">
          <td bitwidth="1" class="bitfield">0</td>
          <td class="iformname" iformid="mla_z_p_zzz">MLA</td>
        </tr>
        <tr class="instructiontable" encname="mls_z_p_zzz_" iformfile="mls_z_p_zzz.xml" first="t" last="t">
          <td bitwidth="1" class="bitfield">1</td>
          <td class="iformname" iformid="mls_z_p_zzz">MLS</td>
        </tr>
      </tbody>
    </instructiontable>
  </iclass_sect>
  <iclass_sect id="sve_int_mladdsub_vvv_pred" title="SVE integer multiply-add writing multiplicand (predicated)">
    <regdiagram form="32" psname="">
      <box hibit="31" width="8" settings="8">
        <c>0</c>
        <c>0</c>
        <c>0</c>
        <c>0</c>
        <c>0</c>
        <c>1</c>
        <c>0</c>
        <c>0</c>
      </box>
      <box hibit="23" width="2" name="size" usename="1">
        <c colspan="2"></c>
      </box>
      <box hibit="21" settings="1">
        <c>0</c>
      </box>
      <box hibit="20" width="5" name="Zm" usename="1">
        <c colspan="5"></c>
      </box>
      <box hibit="15" width="2" settings="2">
        <c>1</c>
        <c>1</c>
      </box>
      <box hibit="13" name="op" usename="1">
        <c></c>
      </box>
      <box hibit="12" width="3" name="Pg" usename="1">
        <c colspan="3"></c>
      </box>
      <box hibit="9" width="5" name="Za" usename="1">
        <c colspan="5"></c>
      </box>
      <box hibit="4" width="5" name="Zdn" usename="1">
        <c colspan="5"></c>
      </box>
    </regdiagram>
    <instructiontable iclass="sve_int_mladdsub_vvv_pred" cols="3">
      <col colno="1" printwidth="15*" />
      <col colno="2" printwidth="18*" />
      <col colno="3" printwidth="10*" />
      <thead class="instructiontable">
        <tr id="heading1">
          <th colno="1" class="bitfields-heading">Decode fields</th>
          <th rowspan="2" class="iformname">Instruction page</th>
          <th rowspan="2" class="enctags">Encoding</th>
        </tr>
        <tr id="heading2">
          <th class="bitfields">op</th>
        </tr>
      </thead>
      <tbody>
        <tr class="instructiontable" encname="mad_z_p_zzz_" iformfile="mad_z_p_zzz.xml" first="t" last="t">
          <td bitwidth="1" class="bitfield">0</td>
          <td class="iformname" iformid="mad_z_p_zzz">MAD</td>
        </tr>
        <tr class="instructiontable" encname="msb_z_p_zzz_" iformfile="msb_z_p_zzz.xml" first="t" last="t">
          <td bitwidth="1" class="bitfield">1</td>
          <td class="iformname" iformid="msb_z_p_zzz">MSB</td>
        </tr>
      </tbody>
    </instructiontable>
  </iclass_sect>
```
也就是剛剛看到
```
    when ('000', _, '0x', _, '0xxxx', _, 'x1xxxx', _) 
    <c>0</c>
    <c>0</c>
    <c>0</c>
    <c>0</c>
    <c>0</c>
    <c>1</c>
    <c>0</c>
    <c>0</c>
    有可能滿足條件會被分到這一個分類
    00000x00
    x應該是任意數
```
在進一步查看
```xml
    case (24 +: 8, 22 +: 2, 21 +: 1, 16 +: 5, 15 +: 1, 14 +: 1, 0 +: 14) of
    when (_, _, _, _, '0', _, _) => // sve_int_mlas_vvv_pred
                            __field size 22 +: 2
                            __field Zm 16 +: 5
                            __field op 13 +: 1
                            __field Pg 10 +: 3
                            __field Zn 5 +: 5
                            __field Zda 0 +: 5
 
```
對印到instrs2asl.py 裡面的程式碼
```asl
     for (fnm, hi, wd) in fields:
        print("    "*level + "__field "+ fnm +" "+str(hi-wd+1) +" +: "+str(wd), file=ofile)
    print("    "*level +"case ("+ ", ".join(hdr) +") of", file=ofile)
```
也就是要求field = str(hi-wd+1) +" +: "+str(wd)
差不多就是有name 才進行處理
```
  __field size 22 +: 2   <box hibit="23" width="2" name="size" usename="1">
  __field Zm 16 +: 5    <box hibit="20" width="5" name="Zm" usename="1">
  __field op 13 +: 1  <box hibit="13" name="op" usename="1">
  __field Pg 10 +: 3   <box hibit="12" width="3" name="Pg" usename="1">
  __field Zn 5 +: 5 <box hibit="9" width="5" name="Za" usename="1">
  __field Zda 0 +: 5  <box hibit="4" width="5" name="Zdn" usename="1">
```
那麼在runtime可能這些值都會持續變動直到滿足走向到一個確切的分類為止
```
case (op) of
   when ('0') => __encoding MLA_Z_P_ZZZ__ // mla_z_p_zzz_
   when ('1') => __encoding MLS_Z_P_ZZZ__ // mls_z_p_zzz_
```
## reg2asl.py
應該也是根據不同的xml type來描述register之類的事
bin/reg2asl.py v8.6/SysReg_xml_v86A-2019-12 -o arch/regs.asl
首先先從main開始解析
```
   # read all the registers
    regs = {}
    for d in args.dir:
        for f in glob.glob(os.path.join(d, '*.xml')):
            print(f)
```
output
```
v8.6/SysReg_xml_v86A-2019-12/ext-gicv_aprn.xml
v8.6/SysReg_xml_v86A-2019-12/ext-gicr_partidr.xml
v8.6/SysReg_xml_v86A-2019-12/ext-cntfrq.xml
v8.6/SysReg_xml_v86A-2019-12/AArch64-mpamvpm7_el2.xml
v8.6/SysReg_xml_v86A-2019-12/ext-gicc_abpr.xml
v8.6/SysReg_xml_v86A-2019-12/AArch64-dc-gva.xml
v8.6/SysReg_xml_v86A-2019-12/AArch32-id_isar6.xml
v8.6/SysReg_xml_v86A-2019-12/ext-gicv_eoir.xml
v8.6/SysReg_xml_v86A-2019-12/ext-gicd_statusr.xml
v8.6/SysReg_xml_v86A-2019-12/AArch64-vmpidr_el2.xml
v8.6/SysReg_xml_v86A-2019-12/ext-pmlsr.xml
```

arm register
```python
                        if re.match('^[a-zA-Z_]\w*$', name):
                        # merge any new fields in (mostly to handle external views of regs)
                        if name in regs:
                            for f,ss in regs[name][2].items():
                                if f not in fields:
                                    fields[f] = ss
                        regs[name] = (long, length, fields, bounds)
                        print(regs[name])
```
arm register output
```
('Selected Error Record Miscellaneous Register 1', 64, {}, None)
('Debug OS Double Lock Register', 32, {'DLK': [('0', '0')]}, None)
('PL0 Read-Only Software Thread ID Register', 32, {}, None)
('SVE Control Register for EL2', 64, {'LEN': [('3', '0')]}, None)
('Cache Level ID Register', 32, {'ICB': [('31', '30')], 'LoUU': [('29', '27')], 'LoC': [('26', '24')], 'LoUIS': [('23', '21')]}, None)
('CPU Interface Non-secure Active Priorities Registers', 32, {}, ('0', '3'))
('Counter Scale Register', 32, {'ScaleVal': [('31', '0')]}, None)
('Virtual SError Exception Syndrome Register', 32, {'AET': [('15', '14')], 'ExT': [('12', '12')]}, None)
```
refer :
```
https://alastairreid.github.io/using-asli/
https://alastairreid.github.io/dissecting-ARM-MRA/
https://alastairreid.github.io/ARM-v8a-xml-release/
https://alastairreid.github.io/papers/FMCAD_16/
https://github.com/alastairreid/mra_tools#tools-to-extract-arms-machine-readable-architecture-specification
https://github.com/ARM-software/asl-interpreter
https://alastairreid.github.io/asl-lexical-syntax
https://v2.ocaml.org/docs/install.html
https://github.com/ARM-software/asl-interpreter/blob/master/utils.ml
    
```

