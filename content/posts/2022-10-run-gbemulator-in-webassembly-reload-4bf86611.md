---
title: "run riscv_emulator in webassembly reload binary file"
date: "2022-10-10T03:12:00.003+08:00"
updated: "2022-10-10T12:24:28.960+08:00"
permalink: "/2022/10/run-gbemulator-in-webassembly-reload.html"
original_url: "https://x8795278.blogspot.com/2022/10/run-gbemulator-in-webassembly-reload.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-7514333933851039874"
tags: []
layout: post
---

![](https://i.imgur.com/G3Qrvy1.png)

# wasm 如何互動
https://github.com/x213212/wasm_riscv_emu
五年前wasm files系統很不友善只有編譯過，硬改後也沒什結果，這次再結合online ide一下打算做一個類似debug的工具，今天就先把檔案系統給搞定.
https://openhome.cc/Gossip/WebAssembly/C2Wasm.html
https://www.itread01.com/hkcxxxe.html

```c
#include<emscripten/emscripten.h>
int EMSCRIPTEN_KEEPALIVE sum(){

printf("sum = %i\n", 100);

return 1;
}
```
![](https://i.imgur.com/zIn44eI.png)

編譯時
```
emcc main.c ./src/bus.c ./src/cpu.c ./src/csr.c ./src/dram.c -o main -I ./include -s WASM=1  -o hello2.html  --preload-file ./addi.bin -s "EXTRA_EXPORTED_RUNTIME_METHODS=['ccall']"

```
-s "EXTRA_EXPORTED_RUNTIME_METHODS=['ccall']" 應該也是不用下，除非要對到其他fucntion

```javascript
var Module = typeof Module != 'undefined' ? Module : {};
var back;
```

```javascript
      back.then(prog => {
        console.log(prog.instance.exports.sum()); 
      });
      back.then(prog => {
        console.log(prog.instance.exports.sum()); 
      });
```
這樣就可以進行呼叫c 語言

![](https://i.imgur.com/zWY6NOi.png)
因為模組導出也是module
![](https://i.imgur.com/Y3lp38w.png)

```htmlmixed
    function sampleClick() {
      back.then(prog => {
        console.log(prog.instance.exports.sum()); 
      });
      back.then(prog => {
        console.log(prog.instance.exports.sum()); 
      });
      back.then(prog => {
        console.log(prog.instance.exports.sum2(1,5)); 
      });
    }
  </script>
  <script async type="text/javascript" src="hello2.js"></script>
  <button type="button" id="btn" onclick="sampleClick()">Click Here!</button>
```

![](https://i.imgur.com/oVzdIFv.png)
在js裡面找到一樣把back
```javascript
   var result = WebAssembly.instantiateStreaming(response, info);

        return result.then(
          receiveInstantiationResult,
```
改為
```javascript
    back = WebAssembly.instantiateStreaming(response, info);

        return back.then(
          receiveInstantiationResult,
```
並在最上層加入
```
var back;
```
讓上層fucntion可以呼叫

https://www.cnblogs.com/xuanhun/p/9963082.html

https://medium.com/@scalevectors/webassembly-c-pointers-strings-part-2-8e173e50912b
從c語言讀值，這部分是ok但我們更多想知道的是把js的value 傳至 c code

找到一個範例
https://github.com/dudeofx/webassembly-IDBFS-barebones/blob/main/index.html
不過這wasm 版本基本上經過大改
這樣傳值可能會出錯(或者我沒找到更好方法

基本上idbfs已經廢除
```bash
 emcc main.c ./src/bus.c ./src/cpu.c ./src/csr.c ./src/dram.c -o main -I ./include -s WASM=1  -o hello2.html  --preload-file ./addi.bin  -lidbfs.js -s "EXTRA_EXPORTED_RUNTIME_METHODS=['UTF8ToString', 'getValue','stringToUTF8','lengthBytesUTF8']" 
```
後面的是我修改過後的code
```
 -lidbfs.js -s "EXTRA_EXPORTED_RUNTIME_METHODS=['UTF8ToString', 'getValue','stringToUTF8','lengthBytesUTF8']" 
```

那麼這個example
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <errno.h>
#include <emscripten.h>

//-----------------------------------------------------------------------
EMSCRIPTEN_KEEPALIVE 
char *LoadData() {
   int fd;
   int size;
   char *buff;

   fd = open("/data/textfile.txt", O_RDONLY);

   if (fd == -1) return strerror(errno);

   size = lseek(fd, 0, SEEK_END);
   lseek(fd, 0, SEEK_SET);
   buff = (char *) malloc(size+1);
   read(fd, buff, size);
   buff[size] = '\0';
   close(fd); 

   return buff;
}
//-----------------------------------------------------------------------
EMSCRIPTEN_KEEPALIVE
void SaveData(char *data) {
   int fd;
   int size;

   if (data == NULL) return;

   fd = open("/data/textfile.txt", O_CREAT | O_WRONLY, 0666);
   if (fd == -1) {
       printf("ERROR: could not open the file for writing!\n, %s\n", strerror(errno));
       return;
   }
   size = strlen(data);
   printf("saving %i bytes... %s\n", size, data);
   write(fd, data, size);
   ftruncate(fd, size);
   close(fd);

   EM_ASM ( FS.syncfs(false, function (err) {} ); );
}
//-----------------------------------------------------------------------
int main() {
   EM_ASM(
      FS.mkdir('/data');
      FS.mount(IDBFS, {}, '/data');

      FS.syncfs(true, function (err) { 
         // provide the DOM side a way to execute code after directory is mounted
         if (typeof Module.OnDataMounted !== 'undefined') {
            Module.OnDataMounted();
         }
      } );
   );

   emscripten_exit_with_live_runtime();
}
//-----------------------------------------------------------------------
```
沒意外可以編譯成功，接下來我們假設怎麼從
js的輸入框讀value
和讀出buffer的值呢

```js
<script type='text/javascript'>

  function InboxHandler() {

    var str= document.getElementById('inbox').value;
    var strLen =  Module.lengthBytesUTF8(str);
    var strPtr = Module._malloc(strLen + 1);
    Module.stringToUTF8(str, strPtr, strLen + 1);
    console.log(strLen);
    
    back.then(prog => {
    
      // prog.instance.exports.queryString(ppcStr); 

      var pcStr = Module.getValue(strPtr, "i32");
      var jsStr = Module.UTF8ToString(pcStr);
      console.log("_queryString: " + jsStr);
   
      // var jsStr = Module.UTF8ToString(pcStr);
      // console.log("_queryString: " + ppcStr);
        prog.instance.exports.SaveData(strPtr); 
      });
  //  /
  }

  function OutboxHandler() {
    back.then(prog => {
      var jsStr = Module.UTF8ToString( document.getElementById('outbox').value =prog.instance.exports.LoadData());
      console.log("_queryString2: " + jsStr);
      document.getElementById('outbox').value =jsStr;
        // console.log(prog.instance.exports.LoadData()); 
      });
  }

  // Module.OnDataMounted = OutboxHandler;
</script>
<input id="inbox" type="text" /><br>
<input id="outbox" type="text" readonly /><br>
```

![](https://i.imgur.com/tVVnTS0.png)

這樣就可以完成非同步的讀入/讀出file的資訊

在更複雜一點前端是binary輸入我們要轉成Uint8Array怎辦
```javascript

  <input id="file-input" type="file" />
  <script>

    // var worker = new Worker('worker.js');
    var inputElement = document.getElementById("file-input");
    inputElement.addEventListener("change", handleFiles, false);
    function handleFiles() {
      var fileList = this.files[0];
      console.log(fileList)
      let buffer = fileList;
      let u = new Uint8Array(buffer);
      // console.log(this.files[0].size);
      // console.log(this.files[0].arrayBuffer);
      const reader = new FileReader();
      const fileByteArray = [];
      reader.readAsArrayBuffer(this.files[0]);
      reader.onloadend = (evt) => {
        if (evt.target.readyState === FileReader.DONE) {
          const arrayBuffer = evt.target.result,
            array = new Uint8Array(arrayBuffer);
          for (const a of array) {
            fileByteArray.push(a);
          }
          console.log(fileByteArray)
        }
      }

    }

  </script>
```

![](https://i.imgur.com/YlwHRc0.png)
實測後轉成blob比較方便
https://yahone-chow.medium.com/file-blob-arraybuffer-576a8e99de0d

再從blob 轉成hex
```javascript
function buf2hex(buffer) { // buffer is an ArrayBuffer
  return [...new Uint8Array(buffer)]
      .map(x => x.toString(16).padStart(2, '0'))
      .join('');

     function handleFiles() {
    
      var fileList = this.files[0];
      console.log(fileList)
      let buffer = fileList;
      let u = new Uint8Array(buffer);
      // console.log(this.files[0].size);
      // console.log(this.files[0].arrayBuffer);
      const reader = new FileReader();
      const fileByteArray = [];
      var reader2 = new FileReader();
      reader2.onload = function (event) {
        var content = reader2.result;//内容就在这里
        alert(content);
        console.log(content);
        var blob = new Blob([content], {
          type: ''
        });
        // console.info(blob);
        // console.info(blob.slice(1, 3, 'text/plain'));
      };
      reader.readAsArrayBuffer(this.files[0]);
      reader.onloadend = (evt) => {
        if (evt.target.readyState === FileReader.DONE) {
          const arrayBuffer = evt.target.result,
            array = new Uint8Array(arrayBuffer);
          for (const a of array) {
            fileByteArray.push(a);
          }
          console.log(fileByteArray)
          console.log(array)
          var after = Uint8ArrayToString(array)

          var blob = new Blob([array])
          console.info(blob);
          var href = URL.createObjectURL(blob);
          // 從 Blob 取出資料
          // var link = document.createElement("a");
          // document.body.appendChild(link);
          // link.href = href;
          // link.download = "fileName";
          // link.click();

          // reader2.readAsText(blob);
          console.log(fileByteArray.length)
          console.log(sumUp(fileByteArray));
          console.log(buf2hex(fileByteArray))
          document.getElementById('inbox').value=buf2hex(fileByteArray)
        }

      }
   
    }
    
 
```
![](https://i.imgur.com/9NZ2NOp.png)
我們hex在to string
到這邊可以轉成string後，我們傳達字元陣列給c
這邊本來要用uint8array進行傳值
不過試到後面還是轉hex再轉string 進行存取比較方便

```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include<emscripten/emscripten.h>
#include <emscripten.h>
#include "includes/cpu.h"
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <inttypes.h>
#include "test.h"
EMSCRIPTEN_KEEPALIVE
void tesqwe(char *input2);
// ANSI colors
#define ANSI_RED     "\x1b[31m"
#define ANSI_GREEN   "\x1b[32m"
#define ANSI_YELLOW  "\x1b[33m"
#define ANSI_BLUE    "\x1b[34m"
#define ANSI_MAGENTA "\x1b[35m"
#define ANSI_CYAN    "\x1b[36m"
#define ANSI_RESET   "\x1b[0m"

void read_file(CPU* cpu, char *filename)
{
	FILE *file;
	uint8_t *buffer;
	unsigned long fileLen;

	//Open file
	file = fopen(filename, "rb");
	if (!file)
	{
		fprintf(stderr, "Unable to open file %s", filename);
	}

	//Get file length
	fseek(file, 0, SEEK_END);
	fileLen=ftell(file);
	fseek(file, 0, SEEK_SET);

	//Allocate memory
	buffer=(uint8_t *)malloc(fileLen+1);
	if (!buffer)
	{
		fprintf(stderr, "Memory error!");
        fclose(file);
	}

	//Read file contents into buffer
	fread(buffer, fileLen, 1, file);
	fclose(file);

    // Print file contents in hex
    for (int i=0; i<fileLen; i+=2) {
        if (i%16==0) printf("\n%.8x: ", i);
        printf("%02x%02x ", *(buffer+i), *(buffer+i+1));
    }
    /*printf("\n");*/

    // copy the bin executable to dram
    memcpy(cpu->bus.dram.mem, buffer, fileLen*sizeof(uint8_t));
	free(buffer);
}
int EMSCRIPTEN_KEEPALIVE sum(){

printf("sum = %i\n", 100);

return 1;
}

int EMSCRIPTEN_KEEPALIVE sum2(int a,int b){

printf("sum2 = %i\n",a+b);

return 0;
}

//-----------------------------------------------------------------------
EMSCRIPTEN_KEEPALIVE 
char *LoadData() {
   int fd;
   int size;
   char *buff;

   fd = open("/data/textfile.txt", O_RDONLY);

   if (fd == -1) return strerror(errno);

   size = lseek(fd, 0, SEEK_END);
   lseek(fd, 0, SEEK_SET);
   buff = (uint8_t *) malloc(size+1);
   read(fd, buff, size);
   buff[size] = '\0';
       for (int i=0; i<size; i+=2) {
        if (i%16==0) printf("\n%.8x: ", i);
        printf("%02x%02x ", *(buff+i), *(buff+i+1));
    }
   close(fd); 
   printf("read %s bytes...\n",buff);
   struct CPU cpu;
    cpu_init(&cpu);
    // Read input file
    read_file(&cpu,"/data/textfile2.txt");
    while (1) {
        // fetch
        uint32_t inst = cpu_fetch(&cpu);
        // Increment the program counter
        cpu.pc += 4;
        // execute
        if (!cpu_execute(&cpu, inst))
            break;

        // dump_registers(&cpu);

        if(cpu.pc==0)
            break;
    }
   return buff;
}

//-----------------------------------------------------------------------
EMSCRIPTEN_KEEPALIVE
void SaveData(char *data) {
   int fd;
   int size;

   if (data == NULL) return;

   fd = open("/data/textfile.txt", O_CREAT | O_WRONLY, 0666);
   if (fd == -1) {
       printf("ERROR: could not open the file for writing!\n, %s\n", strerror(errno));
       return;
   }
   size = strlen(data);
   printf("saving %i bytes... %s\n", size, data);
   write(fd, data, size);
   ftruncate(fd, size);
   tesqwe(data);
   close(fd);
   EM_ASM ( FS.syncfs(false, function (err) {} ); );
}

static char g_str[256] = "Hello, world!";
void EMSCRIPTEN_KEEPALIVE queryString(char** ppStr) {
   *ppStr = g_str;
}

void printArry(unsigned char arr[], int n)
{
    int i;
    for (i = 0; i < n; i++)
    {
        printf("%x ", arr[i]);
    }

    printf("\n");
}
void float2u8Arry(uint8_t *u8Arry, float *floatdata)
{
    uint8_t farray[4];
    *(float *)farray = *floatdata;
 
      u8Arry[3] = farray[0];
        u8Arry[2] = farray[1];
        u8Arry[1] = farray[2];
        u8Arry[0] = farray[3];
 
}
float EMSCRIPTEN_KEEPALIVE sum_up(float vals[], int size) {
  float res = 0;
  for(int i=0; i<size; i++){
    res += vals[i];

    printf("%f \n",vals[i]);
    uint8_t u8data[4];
    float2u8Arry(u8data, &vals[i]);
    printArry(u8data, 4);
    //    printf("saving %d bytes... %s\n",  vals[i]);
    }
 
    // write_to_file()
  return res;
}

//-----------------------------------------------------------------------
int main(int argc, char* argv[]) {
    // if (argc != 2) {
    //     printf("Usage: rvemu <filename>\n");
    //     exit(1);
    // }
 EM_ASM(
      FS.mkdir('/data');
      FS.mount(IDBFS, {}, '/data');

      FS.syncfs(true, function (err) { 
         // provide the DOM side a way to execute code after directory is mounted
         if (typeof Module.OnDataMounted !== 'undefined') {
            Module.OnDataMounted();
         }
      } );
   );

    // Initialize cpu, registers and program counter
    struct CPU cpu;
    cpu_init(&cpu);
    // Read input file
    read_file(&cpu,"addi.bin");
    while (1) {
        // fetch
        uint32_t inst = cpu_fetch(&cpu);
        // Increment the program counter
        cpu.pc += 4;
        // execute
        if (!cpu_execute(&cpu, inst))
            break;

        // dump_registers(&cpu);

        if(cpu.pc==0)
            break;
    }
    
    emscripten_exit_with_live_runtime();
    return 0;
}

```

主要異動SaveData和LoadData各自存去不同的檔案
/data/textfile.txt
/data/textfile2.txt
SaveData 的部分還有去呼叫tesqwe(data);
這邊順便體驗一下link,c++ hex 轉 bin 檔案很簡單

```bash
emcc -c test.cpp -o test
```
link ,多了./test
```bash
emcc  main.c ./test  ./src/bus.c ./src/cpu.c ./src/csr.c ./src/dram.c -o main -I ./include -s WASM=1  -o hello2.html  --preload-file ./addi.bin  -lidbfs.js -s "EXTRA_EXPORTED_RUNTIME_METHODS=['UTF8ToString', 'getValue','stringToUTF8','lengthBytesUTF8']" 
```
到這邊c就可以去呼叫c++的fucntion了!
```cpp
#include <string>
#include <sstream>
#include <iostream>
#include <fstream>
#include <ios>
#include "test.h"
std::string wut = "6f008004732f2034930f80006308ff03930f90006304ff03930fb0006300ff03130f000063040f0067000f00732f203463540f006f00400093e19153171f000023223ffc6ff09fff93000000130100009301000013020000930200001303000093030000130400009304000013050000930500001306000093060000130700009307000013080000930800001309000093090000130a0000930a0000130b0000930b0000130c0000930c0000130d0000930d0000130e0000930e0000130f0000930f0000732540f16310050097020000938202017390523073500018970200009382020273905230b70200809382f2ff7390023b9302f0017390023a73504030970200009382420173905230735020307350303093010000970200009382c2ee73905230130510001315f501634c05000f00f00f930110009308d005130500007300000093020000638a020073905210b7b20000938292107390223073500030970200009382420173901234732540f17300203093000000138700009303000093012000631c7726930010001387100093032000930130006312772693003000138770009303a000930140006318772493000000138700809303008093015000631e7722b700008013870000b70300809301600063147722b700008013870080b7030080938303809301700063187720930000001387f07f9303f07f93018000631e771eb70000809380f0ff13870000b70300809383f3ff930190006310771eb70000809380f0ff1387f07fb70300809383e37f9301a0006312771cb70000801387f07fb70300809383f37f9301b0006316771ab70000809380f0ff13870080b7f3ff7f9383f37f9301c00063187718930000001387f0ff9303f0ff9301d000631e77169300f0ff13871000930300009301e000631477169300f0ff1387f0ff9303e0ff9301f000631a7714b70000809380f0ff13871000b703008093010001631e77129300d0009380b000930380019301100163947012130200009300d0001387b000130307001302120093022000e31652fe930380019301200163107310130200009300d0001387a00013000000130307001302120093022000e31452fe9303700193013001631a730c130200009300d000138790001300000013000000130307001302120093022000e31252fe93036001930140016312730a130200009300d0001387b0001302120093022000e31852fe930380019301500163107708130200009300d000130000001387a0001302120093022000e31652fe9303700193016001631c7704130200009300d0001300000013000000138790001302120093022000e31452fe930360019301700163167702930000029303000293018001639e70009300100213802003930300009301900163147000631030020f00f00f638001009391110093e111009308d00513850100730000000f00f00f930110009308d0051305000073000000731000c00000000000000000000000000000000000000000000000000";
void tesqwe(char *input2){
	std::ofstream datafile("/data/textfile2.txt", std::ios_base::binary | std::ios_base::out);

    char buf[3];
    buf[2] = 0;
    // std::string s = input2;
    std::string str(input2);
    // std::string rjo(1,input2);
    std::stringstream input(str);
    input.flags(std::ios_base::hex);
    while (input)
    {
        input >> buf[0] >> buf[1];
        long val = strtol(buf, nullptr, 16);
        datafile << static_cast<unsigned char>(val & 0xff);
    }
    std::cout<< "ok"<<std::endl;
}
```

到這邊我們就可以透過tesqwe 把前端的hex char array轉為string
存入前面掛載的目錄，如果要讀出來呢，那就反向一下

```cpp

//-----------------------------------------------------------------------
EMSCRIPTEN_KEEPALIVE 
char *LoadData() {
   int fd;
   int size;
   char *buff;

   fd = open("/data/textfile.txt", O_RDONLY);

   if (fd == -1) return strerror(errno);

   size = lseek(fd, 0, SEEK_END);
   lseek(fd, 0, SEEK_SET);
   buff = (uint8_t *) malloc(size+1);
   read(fd, buff, size);
   buff[size] = '\0';
       for (int i=0; i<size; i+=2) {
        if (i%16==0) printf("\n%.8x: ", i);
        printf("%02x%02x ", *(buff+i), *(buff+i+1));
    }
   close(fd); 
   /////////////////////////////////////////////////////////////
   struct CPU cpu;
    cpu_init(&cpu);
    // Read input file
    read_file(&cpu,"/data/textfile2.txt");
    while (1) {
        // fetch
        uint32_t inst = cpu_fetch(&cpu);
        // Increment the program counter
        cpu.pc += 4;
        // execute
        if (!cpu_execute(&cpu, inst))
            break;

        // dump_registers(&cpu);

        if(cpu.pc==0)
            break;
    }
   return buff;
}
```
在第二個分隔線就可以讓我們的模擬器去讀前端載入的elf檔案，實現動態加載分析檔案的功能
 read_file(&cpu,"/data/textfile2.txt");
 並呼叫載入elf執行模擬指令。
 ![](https://i.imgur.com/G3Qrvy1.png)
到這邊如果換成是gb模擬器，應該就完全可以在瀏覽器實現讀檔案寫檔案的功能。
目前看來emcc在編譯過程中把datatype某些部分給優化掉導致指令沒辦法正常顯示

計算結果正確，應該是wasm把某些datatype給轉換調導致printf無法判斷。
```c
    printf("\n%#.8lx -> Inst: %llx ",
            cpu->pc-4, inst); // DEBUG*/
    printf("\n<OpCode: %#.2x, funct3:%#x, funct7:%#x> ", opcode, funct3, funct7);

   for (int i=0; i<8; i++) {
        printf("   %4s:%llx ", abi[i],    cpu->regs[i]);
        printf("   %2s:%llx  ", abi[i+8],  cpu->regs[i+8]);
        printf("   %2s:%llx  ", abi[i+16], cpu->regs[i+16]);
        printf("   %3s:%llx\n", abi[i+24], cpu->regs[i+24]);
    }
```
![](https://i.imgur.com/gXOcBdM.png)
上述c code重寫後就可以正常顯示

# debug
更多時候等待並不是c很慢是
![](https://i.imgur.com/yszgDXw.png)
這邊註解output就不會一直拉到最下導致瀏覽器速度降低
```
 // element.scrollTop = element.scrollHeight; // focus on bottom
```

