---
title: "study riscv_emulator"
date: "2022-09-20T13:01:00.002+08:00"
updated: "2022-09-20T13:01:44.968+08:00"
permalink: "/2022/09/study-riscvemulator.html"
original_url: "https://x8795278.blogspot.com/2022/09/study-riscvemulator.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8600129805497162311"
tags: ["RISC-V"]
layout: post
---

![](https://i.imgur.com/Cu1w6sc.png)

https://michaeljclark.github.io/isa.html
https://github.com/x213212/riscv_emulator
# riscv_emulator
研讀一下riscv 架構的指令，找了一個模擬器來看實際要執行risc v指令內部會經過哪一些細節
# create riscv 架構的 binary
```makefile
test.bin: test.c
	/root/riscv-toolchain/bin/riscv64-unknown-elf-gcc -S test.c
	/root/riscv-toolchain/bin/riscv64-unknown-elf-gcc -Wl,-Ttext=0x0 -nostdlib -march=rv64i -mabi=lp64 -o test test.s
	/root/riscv-toolchain/bin/riscv64-unknown-elf-objcopy -O binary test test.bin

clean:
	rm -f test
	rm -f test.bin
	rm -f test.s

```
```c
int fact(int n);
int main() {
    int a = 10;
    /*return fact(a);*/
    return a-11;
}

int fact(int n) {
    if(n==1)
        return n;
    else
        return n * fact(n-1);
}

```
到時候就會產生一個起始位置在0的binary .-nostdlib 跟之前的文章一樣不添加任何lib
# read_file
把編譯過的 binary 讀入記憶體中
```c
void read_file(CPU *cpu, char *filename)
{
    FILE *file;
    uint8_t *buffer;
    unsigned long fileLen;

    // Open file
    file = fopen(filename, "rb");
    if (!file)
    {
        fprintf(stderr, "Unable to open file %s", filename);
    }

    // Get file length
    fseek(file, 0, SEEK_END);
    fileLen = ftell(file);
    fseek(file, 0, SEEK_SET);

    // Allocate memory
    buffer = (uint8_t *)malloc(fileLen + 1);
    if (!buffer)
    {
        fprintf(stderr, "Memory error!");
        fclose(file);
    }

    // Read file contents into buffer
    fread(buffer, fileLen, 1, file);
    fclose(file);

    // Print file contents in hex
    /*for (int i=0; i<fileLen; i+=2) {*/
    /*if (i%16==0) printf("\n%.8x: ", i);*/
    /*printf("%02x%02x ", *(buffer+i), *(buffer+i+1));*/
    /*}*/
    /*printf("\n");*/

    // copy the bin executable to dram
    memcpy(cpu->bus.dram.mem, buffer, fileLen * sizeof(uint8_t));
    free(buffer);
}
```
# start
```c

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        printf("Usage: rvemu <filename>\n");
        exit(1);
    }

    // Initialize cpu, registers and program counter
    struct CPU cpu;
    cpu_init(&cpu);
    // Read input file
    read_file(&cpu, argv[1]);

    // cpu loop
    while (1)
    {
        // fetch
        uint32_t inst = cpu_fetch(&cpu);
        // Increment the program counter
        // printf("next pc ->%x\n", cpu.pc);
        printf("next -> %#.8lx ",  cpu.pc ); // DEBUG
        cpu.pc += 4;
        // execute
        if (!cpu_execute(&cpu, inst))
            break;

        dump_registers(&cpu);

        if (cpu.pc == 0)
            break;
    }
    /*dump_registers(&cpu);*/
    return 0;
}

```
# init
進行初始化
```c
    struct CPU cpu;
    cpu_init(&cpu);
    // Read input file
    read_file(&cpu, argv[1]);

```
這邊可以和到cpu 第x0 register 始終為0
cpu->pc 起始我們從 0x80000000 開始
#define DRAM_BASE 0x80000000

```c

void cpu_init(CPU *cpu) {
    cpu->regs[0] = 0x00;                    // register x0 hardwired to 0
    cpu->regs[2] = DRAM_BASE + DRAM_SIZE;   // Set stack pointer
    cpu->pc      = DRAM_BASE;               // Set program counter to the base address
}

```
# start fetch
之後進入循環開始讀指令
```
 // cpu loop
    while (1)
    {
        // fetch
        uint32_t inst = cpu_fetch(&cpu);
        // Increment the program counter
        // printf("next pc ->%x\n", cpu.pc);
        printf("next -> %#.8lx ",  cpu.pc ); // DEBUG
        break;
        cpu.pc += 4;
        // execute
        if (!cpu_execute(&cpu, inst))
            break;

        dump_registers(&cpu);

        if (cpu.pc == 0)
            break;
    }
    /*dump_registers(&cpu);*/
```
cpu_fetch會經由bus 去存去記憶體位置，這邊跟gb模擬器差不多，記憶體在小的嵌入式可以切成更多塊進行應用
```c

uint32_t cpu_fetch(CPU *cpu) {
    uint32_t inst = bus_load(&(cpu->bus), cpu->pc, 32);
    return inst;
}
```

```c
uint64_t cpu_load(CPU* cpu, uint64_t addr, uint64_t size) {
    return bus_load(&(cpu->bus), addr, size);
}

void cpu_store(CPU* cpu, uint64_t addr, uint64_t size, uint64_t value) {
    bus_store(&(cpu->bus), addr, size, value);
}

```

```c
uint64_t bus_load(BUS* bus, uint64_t addr, uint64_t size) {
    return dram_load(&(bus->dram), addr, size);
}
void bus_store(BUS* bus, uint64_t addr, uint64_t size, uint64_t value) {
    dram_store(&(bus->dram), addr, size, value);
}

```

可以看到細節，mem大小為100mb or 4mb ?
#define DRAM_SIZE 1024*1024*1
typedef struct DRAM {
	uint8_t mem[DRAM_SIZE];     // Dram memory of DRAM_SIZE
} DRAM;
```c

uint64_t dram_load_8(DRAM* dram, uint64_t addr){
    return (uint64_t) dram->mem[addr - DRAM_BASE];
}
uint64_t dram_load_16(DRAM* dram, uint64_t addr){
    return (uint64_t) dram->mem[addr-DRAM_BASE]
        |  (uint64_t) dram->mem[addr-DRAM_BASE + 1] << 8;
}
uint64_t dram_load_32(DRAM* dram, uint64_t addr){
    return (uint64_t) dram->mem[addr-DRAM_BASE]
        |  (uint64_t) dram->mem[addr-DRAM_BASE + 1] << 8
        |  (uint64_t) dram->mem[addr-DRAM_BASE + 2] << 16 
        |  (uint64_t) dram->mem[addr-DRAM_BASE + 3] << 24;
}
uint64_t dram_load_64(DRAM* dram, uint64_t addr){
    return (uint64_t) dram->mem[addr-DRAM_BASE]
        |  (uint64_t) dram->mem[addr-DRAM_BASE + 1] << 8
        |  (uint64_t) dram->mem[addr-DRAM_BASE + 2] << 16
        |  (uint64_t) dram->mem[addr-DRAM_BASE + 3] << 24
        |  (uint64_t) dram->mem[addr-DRAM_BASE + 4] << 32
        |  (uint64_t) dram->mem[addr-DRAM_BASE + 5] << 40 
        |  (uint64_t) dram->mem[addr-DRAM_BASE + 6] << 48
        |  (uint64_t) dram->mem[addr-DRAM_BASE + 7] << 56;
}

uint64_t dram_load(DRAM* dram, uint64_t addr, uint64_t size) {
    switch (size) {
        case 8:  return dram_load_8(dram, addr);  break;
        case 16: return dram_load_16(dram, addr); break;
        case 32: return dram_load_32(dram, addr); break;
        case 64: return dram_load_64(dram, addr); break;
        default: ;
    }
    return 1;
}

void dram_store_8(DRAM* dram, uint64_t addr, uint64_t value) {
    dram->mem[addr-DRAM_BASE] = (uint8_t) (value & 0xff);
}
void dram_store_16(DRAM* dram, uint64_t addr, uint64_t value) {
    dram->mem[addr-DRAM_BASE] = (uint8_t) (value & 0xff);
    dram->mem[addr-DRAM_BASE+1] = (uint8_t) ((value >> 8) & 0xff);
}
void dram_store_32(DRAM* dram, uint64_t addr, uint64_t value) {
    dram->mem[addr-DRAM_BASE] = (uint8_t) (value & 0xff);
    dram->mem[addr-DRAM_BASE + 1] = (uint8_t) ((value >> 8) & 0xff);
    dram->mem[addr-DRAM_BASE + 2] = (uint8_t) ((value >> 16) & 0xff);
    dram->mem[addr-DRAM_BASE + 3] = (uint8_t) ((value >> 24) & 0xff);
}
void dram_store_64(DRAM* dram, uint64_t addr, uint64_t value) {
    dram->mem[addr-DRAM_BASE] = (uint8_t) (value & 0xff);
    dram->mem[addr-DRAM_BASE + 1] = (uint8_t) ((value >> 8) & 0xff);
    dram->mem[addr-DRAM_BASE + 2] = (uint8_t) ((value >> 16) & 0xff);
    dram->mem[addr-DRAM_BASE + 3] = (uint8_t) ((value >> 24) & 0xff);
    dram->mem[addr-DRAM_BASE + 4] = (uint8_t) ((value >> 32) & 0xff);
    dram->mem[addr-DRAM_BASE + 5] = (uint8_t) ((value >> 40) & 0xff);
    dram->mem[addr-DRAM_BASE + 6] = (uint8_t) ((value >> 48) & 0xff);
    dram->mem[addr-DRAM_BASE + 7] = (uint8_t) ((value >> 56) & 0xff);
}

void dram_store(DRAM* dram, uint64_t addr, uint64_t size, uint64_t value) {
    switch (size) {
        case 8:  dram_store_8(dram, addr, value);  break;
        case 16: dram_store_16(dram, addr, value); break;
        case 32: dram_store_32(dram, addr, value); break;
        case 64: dram_store_64(dram, addr, value); break;
        default: ;
    }
}

```
可以看細節 存取addr 進來後-去DRAM_BASE 進行存取
讀取則使用or 組合後再丟出uint64_t型態variable給呼叫端
再重新看這個fucntion
```c

uint32_t cpu_fetch(CPU *cpu) {
    uint32_t inst = bus_load(&(cpu->bus), cpu->pc, 32);
    return inst;
}
```
每次讀4個bytes ,pc += 4
我們就可以每次得到一條指令
到這裡就可以看到pc每次都會+4直到cpu_execute執行異常才會跳出
```c
  printf("next -> %#.8lx ",  cpu.pc ); // DEBUG
        cpu.pc += 4;
        // execute
        if (!cpu_execute(&cpu, inst))
            break;
```
# execute
執行一條指令
cpu_execute 這邊就要查詢riscv的 規格書
初始六個bits可以得出opcode，根據opcode可以對指令做出第一層分類，JAL、B_TYPE、S_TYPE
等等funct3、funct7 又可以在分一層最後才會找到最終指令並執行 exec_BEQ、exec_JAL

```c
int cpu_execute(CPU *cpu, uint32_t inst) {
    int opcode = inst & 0x7f;           // opcode in bits 6..0
    int funct3 = (inst >> 12) & 0x7;    // funct3 in bits 14..12
    int funct7 = (inst >> 25) & 0x7f;   // funct7 in bits 31..25

    cpu->regs[0] = 0;                   // x0 hardwired to 0 at each cycle

    printf("%s\n%#.8lx -> Inst: %#.8x <OpCode: %#.2x, funct3:%#x, funct7:%#x> %s",
            ANSI_YELLOW, cpu->pc-4, inst, opcode, funct3, funct7, ANSI_RESET);
             // DEBUG*/
    // printf("%s\n%#.8lx -> %s", ANSI_YELLOW, cpu->pc-4, ANSI_RESET); // DEBUG

    switch (opcode) {
        case LUI:   exec_LUI(cpu, inst); break;
        case AUIPC: exec_AUIPC(cpu, inst); break;

        case JAL:   exec_JAL(cpu, inst); break;
        case JALR:  exec_JALR(cpu, inst); break;

        case B_TYPE:
            switch (funct3) {
                case BEQ:   exec_BEQ(cpu, inst); break;
                case BNE:   exec_BNE(cpu, inst); break;
                case BLT:   exec_BLT(cpu, inst); break;
                case BGE:   exec_BGE(cpu, inst); break;
                case BLTU:  exec_BLTU(cpu, inst); break;
                case BGEU:  exec_BGEU(cpu, inst); break;
                default: ;
            } break;

        case LOAD:
            switch (funct3) {
                case LB  :  exec_LB(cpu, inst); break;  
                case LH  :  exec_LH(cpu, inst); break;  
                case LW  :  exec_LW(cpu, inst); break;  
                case LD  :  exec_LD(cpu, inst); break;  
                case LBU :  exec_LBU(cpu, inst); break; 
                case LHU :  exec_LHU(cpu, inst); break; 
                case LWU :  exec_LWU(cpu, inst); break; 
                default: ;
            } break;

        case S_TYPE:
            switch (funct3) {
                case SB  :  exec_SB(cpu, inst); break;  
                case SH  :  exec_SH(cpu, inst); break;  
                case SW  :  exec_SW(cpu, inst); break;  
                case SD  :  exec_SD(cpu, inst); break;  
                default: ;
            } break;

        case I_TYPE:  
            switch (funct3) {
                case ADDI:  exec_ADDI(cpu, inst); break;
                case SLLI:  exec_SLLI(cpu, inst); break;
                case SLTI:  exec_SLTI(cpu, inst); break;
                case SLTIU: exec_SLTIU(cpu, inst); break;
                case XORI:  exec_XORI(cpu, inst); break;
                case SRI:   
                    switch (funct7) {
                        case SRLI:  exec_SRLI(cpu, inst); break;
                        case SRAI:  exec_SRAI(cpu, inst); break;
                        default: ;
                    } break;
                case ORI:   exec_ORI(cpu, inst); break;
                case ANDI:  exec_ANDI(cpu, inst); break;
                default:
                    fprintf(stderr, 
                            "[-] ERROR-> opcode:0x%x, funct3:0x%x, funct7:0x%x\n"
                            , opcode, funct3, funct7);
                    return 0;
            } break;

        case R_TYPE:  
            switch (funct3) {
                case ADDSUB:
                    switch (funct7) {
                        case ADD: exec_ADD(cpu, inst);
                        case SUB: exec_ADD(cpu, inst);
                        default: ;
                    } break;
                case SLL:  exec_SLL(cpu, inst); break;
                case SLT:  exec_SLT(cpu, inst); break;
                case SLTU: exec_SLTU(cpu, inst); break;
                case XOR:  exec_XOR(cpu, inst); break;
                case SR:   
                    switch (funct7) {
                        case SRL:  exec_SRL(cpu, inst); break;
                        case SRA:  exec_SRA(cpu, inst); break;
                        default: ;
                    }
                case OR:   exec_OR(cpu, inst); break;
                case AND:  exec_AND(cpu, inst); break;
                default:
                    fprintf(stderr, 
                            "[-] ERROR-> opcode:0x%x, funct3:0x%x, funct7:0x%x\n"
                            , opcode, funct3, funct7);
                    return 0;
            } break;

        case FENCE: exec_FENCE(cpu, inst); break;

        case I_TYPE_64:
            switch (funct3) {
                case ADDIW: exec_ADDIW(cpu, inst); break;
                case SLLIW: exec_SLLIW(cpu, inst); break;
                case SRIW : 
                    switch (funct7) {
                        case SRLIW: exec_SRLIW(cpu, inst); break;
                        case SRAIW: exec_SRLIW(cpu, inst); break;
                    } break;
            } break;

        case R_TYPE_64:
            switch (funct3) {
                case ADDSUB:
                    switch (funct7) {
                        case ADDW:  exec_ADDW(cpu, inst); break;
                        case SUBW:  exec_SUBW(cpu, inst); break;
                        case MULW:  exec_MULW(cpu, inst); break;
                    } break;
                case DIVW:  exec_DIVW(cpu, inst); break;
                case SLLW:  exec_SLLW(cpu, inst); break;
                case SRW:
                    switch (funct7) {
                        case SRLW:  exec_SRLW(cpu, inst); break;
                        case SRAW:  exec_SRAW(cpu, inst); break;
                        case DIVUW: exec_DIVUW(cpu, inst); break;
                    } break;
                case REMW:  exec_REMW(cpu, inst); break;
                case REMUW: exec_REMUW(cpu, inst); break;
                default: ;
            } break;

        case CSR:
            switch (funct3) {
                case ECALLBREAK:    exec_ECALLBREAK(cpu, inst); break;
                case CSRRW  :  exec_CSRRW(cpu, inst); break;  
                case CSRRS  :  exec_CSRRS(cpu, inst); break;  
                case CSRRC  :  exec_CSRRC(cpu, inst); break;  
                case CSRRWI :  exec_CSRRWI(cpu, inst); break; 
                case CSRRSI :  exec_CSRRSI(cpu, inst); break; 
                case CSRRCI :  exec_CSRRCI(cpu, inst); break; 
                default:
                    fprintf(stderr, 
                            "[-] ERROR-> opcode:0x%x, funct3:0x%x, funct7:0x%x\n"
                            , opcode, funct3, funct7);
                    return 0;
            } break;

        case AMO_W:
            switch (funct7 >> 2) { // since, funct[1:0] = aq, rl
                case LR_W      :  exec_LR_W(cpu, inst); break;  
                case SC_W      :  exec_SC_W(cpu, inst); break;  
                case AMOSWAP_W :  exec_AMOSWAP_W(cpu, inst); break;  
                case AMOADD_W  :  exec_AMOADD_W(cpu, inst); break; 
                case AMOXOR_W  :  exec_AMOXOR_W(cpu, inst); break; 
                case AMOAND_W  :  exec_AMOAND_W(cpu, inst); break; 
                case AMOOR_W   :  exec_AMOOR_W(cpu, inst); break; 
                case AMOMIN_W  :  exec_AMOMIN_W(cpu, inst); break; 
                case AMOMAX_W  :  exec_AMOMAX_W(cpu, inst); break; 
                case AMOMINU_W :  exec_AMOMINU_W(cpu, inst); break; 
                case AMOMAXU_W :  exec_AMOMAXU_W(cpu, inst); break; 
                default:
                    fprintf(stderr, 
                            "[-] ERROR-> opcode:0x%x, funct3:0x%x, funct7:0x%x\n"
                            , opcode, funct3, funct7);
                    return 0;
            } break;

        case 0x00:
            return 0;

        default:
            fprintf(stderr, 
                    "[-] ERROR-> opcode:0x%x, funct3:0x%x, funct3:0x%x\n"
                    , opcode, funct3, funct7);
            return 0;
            /*exit(1);*/
    }
    return 1;
}

```

指令進來後一些常用要取得type某些特定的bit 區間再返回
```c

//=====================================================================================
// Instruction Decoder Functions
//=====================================================================================

uint64_t rd(uint32_t inst) {
    return (inst >> 7) & 0x1f;    // rd in bits 11..7
}
uint64_t rs1(uint32_t inst) {
    return (inst >> 15) & 0x1f;   // rs1 in bits 19..15
}
uint64_t rs2(uint32_t inst) {
    return (inst >> 20) & 0x1f;   // rs2 in bits 24..20
}

uint64_t imm_I(uint32_t inst) {
    // imm[11:0] = inst[31:20]
    return ((int64_t)(int32_t) (inst & 0xfff00000)) >> 20; // right shift as signed?
}
uint64_t imm_S(uint32_t inst) {
    // imm[11:5] = inst[31:25], imm[4:0] = inst[11:7]
    return ((int64_t)(int32_t)(inst & 0xfe000000) >> 20)
        | ((inst >> 7) & 0x1f); 
}
uint64_t imm_B(uint32_t inst) {
    // imm[12|10:5|4:1|11] = inst[31|30:25|11:8|7]
    return ((int64_t)(int32_t)(inst & 0x80000000) >> 19)
        | ((inst & 0x80) << 4) // imm[11]
        | ((inst >> 20) & 0x7e0) // imm[10:5]
        | ((inst >> 7) & 0x1e); // imm[4:1]
}
uint64_t imm_U(uint32_t inst) {
    // imm[31:12] = inst[31:12]
    return (int64_t)(int32_t)(inst & 0xfffff000);
}
uint64_t imm_J(uint32_t inst) {
    // imm[20|10:1|11|19:12] = inst[31|30:21|20|19:12]
    return (uint64_t)((int64_t)(int32_t)(inst & 0x80000000) >> 11)
        | (inst & 0xff000) // imm[19:12]
        | ((inst >> 9) & 0x800) // imm[11]
        | ((inst >> 20) & 0x7fe); // imm[10:1]
}

uint32_t shamt(uint32_t inst) {
    // shamt(shift amount) only required for immediate shift instructions
    // shamt[4:5] = imm[5:0]
    return (uint32_t) (imm_I(inst) & 0x1f); // TODO: 0x1f / 0x3f ?
}

uint64_t csr(uint32_t inst) {
    // csr[11:0] = inst[31:20]
    return ((inst & 0xfff00000) >> 20);
}
```
# jump
jump 的時候以exec_JAL來說
cpu->regs[rd(inst)] = cpu->pc;
會儲存當前的記憶體位置也就是跳躍的指令
實際上跳的時候
cpu->pc = cpu->pc + (int64_t) imm - 4;
這邊-4變成跳躍的前一行指令，再加上立即數完成跳躍
a=a+1
jump main <== store address

a=a+1 pc-4 ,address + imm address
jump main <== store address

以這個模擬器來說還有其他文章有看到imm 可能要左移，這邊應該是compiler會處理好。
```c
void exec_JAL(CPU* cpu, uint32_t inst) {
    uint64_t imm = imm_J(inst);
    cpu->regs[rd(inst)] = cpu->pc;
    /*print_op("JAL-> rd:%ld, pc:%lx\n", rd(inst), cpu->pc);*/
    cpu->pc = cpu->pc + (int64_t) imm - 4;
    print_op("jal\n");

    if (ADDR_MISALIGNED(cpu->pc)) {
        fprintf(stderr, "JAL pc address misalligned");
        exit(0);
    }
  
}
```
exec_JALR常常搭配jal有跳就要跳回來，也可以看到
uint64_t tmp = cpu->pc;會儲存當前的指令位置
cpu->pc = (cpu->regs[rs1(inst)] + (int64_t) imm) & 0xfffffffe;
讀register再加上立即數進行跳躍。
cpu->regs[rd(inst)] = tmp;
```c
void exec_JALR(CPU* cpu, uint32_t inst) {
    uint64_t imm = imm_I(inst);
    uint64_t tmp = cpu->pc;
    cpu->pc = (cpu->regs[rs1(inst)] + (int64_t) imm) & 0xfffffffe;
    cpu->regs[rd(inst)] = tmp;
    /*print_op("NEXT -> %#lx, imm:%#lx\n", cpu->pc, imm);*/
    print_op("jalr\n");
    if (ADDR_MISALIGNED(cpu->pc)) {
        fprintf(stderr, "JAL pc address misalligned");
        exit(0);
    }
}
```
# beq、、、
這邊就比對register值，一樣是從比對的上一條指令加上立即數在跳躍

a=a+1 pc-4 ,address + imm address
if(rs1==rs2 )jump main <== store address

```c

void exec_BEQ(CPU* cpu, uint32_t inst) {
    uint64_t imm = imm_B(inst);
    if ((int64_t) cpu->regs[rs1(inst)] == (int64_t) cpu->regs[rs2(inst)])
        cpu->pc = cpu->pc + (int64_t) imm - 4;

    // -> a=1
    // -> if(a == b )jump main

    // main
    print_op("beq\n");
}
void exec_BNE(CPU* cpu, uint32_t inst) {
    uint64_t imm = imm_B(inst);
    if ((int64_t) cpu->regs[rs1(inst)] != (int64_t) cpu->regs[rs2(inst)])
        cpu->pc = (cpu->pc + (int64_t) imm - 4);
    print_op("bne\n");
}
```
後面就是一些左移右移，原子操作的東西，要快速學習risc v asm可以看這邊的範例
https://github.com/x213212/riscv-operating-system-mooc/tree/main/code/asm
裡面有配合gdb可以進行debug,作者最終想在這個模擬器上運行一個linux
```c
int fact(int n);
int main() {
    int a = 10;
    /*return fact(a);*/
    return a-11;
}

int fact(int n) {
    if(n==1)
        return n;
    else
        return n * fact(n-1);
}

```
有可能如果在這進行加載os，裡面一些fucntion，如print有呼叫這些function,我們的模擬器就要解析這段asm然後我們把它對接我們外部系統的printf,這樣就可以從模擬器再去call glibc的lib 在進一步顯示到termial.

在研究有無虛擬指令也可先透過tests的測試檔案進行編譯查看.s檔案
![](https://i.imgur.com/MPwB0MC.png)
例如
sext.w	他是被等效成 addiw rd, rs, 0
```asm
	addiw	a5,a5,-12
	sext.w	a5,a5
```

![](https://i.imgur.com/Z64rQ8w.png)
也就是

```asm
	addiw	a5,a5,-12
	addiw	a5,a5,0
```
運行模擬器可以看到實際指令結果
![](https://i.imgur.com/Z21yuDK.png)

