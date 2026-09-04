---
title: "antlr4ts Visitor & Listener example"
date: "2022-10-02T00:35:00.000+08:00"
updated: "2022-10-02T00:35:31.440+08:00"
permalink: "/2022/10/antlr4ts-visitor-listener-example.html"
original_url: "https://x8795278.blogspot.com/2022/10/antlr4ts-visitor-listener-example.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8100431008033922880"
tags: []
layout: post
---

![](https://i.imgur.com/Qdaibsr.png)

# antlr4ts
https://progate.com/docs/nodejs-new-application
https://github.com/Crtrpt/ts_calculator
https://github.com/tunnelvisionlabs/antlr4ts

# Getting started
Install antlr4ts as a runtime dependency using your preferred package manager.

> npm install antlr4ts --save
> yarn add antlr4ts
>
Install antlr4ts-cli as a development dependency using your preferred package manager.

> npm install antlr4ts-cli --save-dev
> yarn add -D antlr4ts-cli
>
Add a grammar to your project, e.g. path/to/MyGrammar.g4
這邊改為相對應的路徑

Add a script to package.json for compiling your grammar to TypeScript

"scripts": {
  // ...
  "antlr4ts": "antlr4ts -listener -visitor ./MyGrammar.g4 -o src/gen"
}
這邊改為對應的MyGrammar.g4 路徑
![](https://i.imgur.com/j7VSsqu.png)

```bash
npm init
```
生成Package.js檔案
這邊就可以來產生我們的主程式
目錄結構
```
root@HOME-X213212:~/antlr4ts# tree -L 1
.
├── MyGrammar.g4
├── node_modules
├── package-lock.json
├── package.json
├── path
├── src
│   ├── ANTLR
│   ├── app.ts
│   └── gen
└── views
```
app.ts於src目錄
目前範例顯示的是官方的教學範例
我們新增我們的MyGrammar
```g4
grammar MyGrammar;
INT    : [0-9]+;
DOUBLE : [0-9]+'.'[0-9]+;
PI     : 'pi';
E      : 'e';
POW    : '^';
NL     : '\n';
WS     : [ \t\r]+ -> skip;
ID     : [a-zA-Z_][a-zA-Z_0-9]*;

PLUS  : '+';
EQUAL : '=';
MINUS : '-';
MULT  : '*';
DIV   : '/';
LPAR  : '(';
RPAR  : ')';

input
    : setVar NL input     # ToSetVar
    | plusOrMinus NL? EOF # Calculate
    ;

setVar
    : ID EQUAL plusOrMinus # SetVariable
    ;

plusOrMinus 
    : plusOrMinus PLUS multOrDiv  # Plus
    | plusOrMinus MINUS multOrDiv # Minus
    | multOrDiv                   # ToMultOrDiv
    ;

multOrDiv
    : multOrDiv MULT pow # Multiplication
    | multOrDiv DIV pow  # Division
    | pow                # ToPow
    ;

pow
    : unaryMinus (POW pow)? # Power
    ;

unaryMinus
    : MINUS unaryMinus # ChangeSign
    | atom             # ToAtom
    ;

atom
    : PI                    # ConstantPI
    | E                     # ConstantE
    | DOUBLE                # Double
    | INT                   # Int
    | ID                    # Variable
    | LPAR plusOrMinus RPAR # Braces
    ;
```
新增我們npm run 的指令
```
npm run 
```
![](https://i.imgur.com/xNKSAWV.png)

我們要事先用
```
npm run antlr4ts 
```
去把garmer 轉成相對應的typescript
![](https://i.imgur.com/MJH7pPe.png)
到我們src/gen資料夾部分，準備就緒就可以來run官方的檔案

Use your grammar in TypeScript

```node.js
import { ANTLRInputStream, CommonTokenStream } from 'antlr4ts';
import { MyGrammarLexer } from "./gen/MyGrammarLexer";
import { MyGrammarParser } from "./gen/MyGrammarParser";

import { MyGrammarListener } from './gen/MyGrammarListener'
import { IntContext } from './gen/MyGrammarParser'
import { ParseTreeWalker } from 'antlr4ts/tree/ParseTreeWalker'

// Create the lexer and parser
let inputStream = new ANTLRInputStream("4+3+2-1*4/4");
let lexer = new  MyGrammarLexer(inputStream);
let tokenStream = new CommonTokenStream(lexer);
let parser = new MyGrammarParser(tokenStream);
parser.buildParseTree = true;
let tree = parser.input();
console.log(tree);
console.log(tree.toStringTree(parser));
```
toStringTree 是在antlr4權威指南看到，不知道typescript有沒有支援可以在github搜尋一下
![](https://i.imgur.com/pxTbRR6.png)
有些函式可以直接call也ok
這樣這個範例run 起來就可以看到我們的語法分析樹
![](https://i.imgur.com/dyyNWqM.png)

能不能有可視化的版本，不過我的wsl還沒辦法顯示gui 我們可能看一下windows 版本如何安裝.
![](https://i.imgur.com/OgjOSNW.png)

```bash
Windows
Download https://www.antlr.org/download/antlr-4.11.1-complete.jar.
Add antlr4-complete.jar to CLASSPATH, either:
Permanently: Using System Properties dialog > Environment variables > Create or append to CLASSPATH variable
Temporarily, at command line:
SET CLASSPATH=.;C:\Javalib\antlr4-complete.jar;%CLASSPATH%
Create batch commands for ANTLR Tool, TestRig in dir in PATH
 antlr4.bat: java org.antlr.v4.Tool %*
 grun.bat:   java org.antlr.v4.gui.TestRig %*
```
![](https://i.imgur.com/zlsWGKV.png)

在系統變數那邊新增，這樣我們的cmd才吃的到載下來的jar檔案，記得順便產生兩個bat。
設定臨時環境變數
```
SET CLASSPATH=.;D:\download\antlr4\antlr-4.11.1-complete.jar;%CLASSPATH%
```
也ok,
在windows一樣需要我們的garmmar 檔案

Expr.g4
```g4
grammar Expr;		
prog:	(expr NEWLINE)* ;
expr:	expr ('*'|'/') expr
    |	expr ('+'|'-') expr
    |	INT
    |	'(' expr ')'
    ;
NEWLINE : [\r\n]+ ;
INT     : [0-9]+ ;
```

```bash
antlr4 Expr.g4
javac Expr*.java
grun Expr prog -gui
```
prog為起始點,run 起簡單範例

當然我們範例直接選用前面的MyGrammar.g4在windows我們命名為
Expr2.g4
```g4
grammar MyGrammar;
INT    : [0-9]+;
DOUBLE : [0-9]+'.'[0-9]+;
PI     : 'pi';
E      : 'e';
POW    : '^';
NL     : '\n';
WS     : [ \t\r]+ -> skip;
ID     : [a-zA-Z_][a-zA-Z_0-9]*;

PLUS  : '+';
EQUAL : '=';
MINUS : '-';
MULT  : '*';
DIV   : '/';
LPAR  : '(';
RPAR  : ')';

input
    : setVar NL input     # ToSetVar
    | plusOrMinus NL? EOF # Calculate
    ;

setVar
    : ID EQUAL plusOrMinus # SetVariable
    ;

plusOrMinus 
    : plusOrMinus PLUS multOrDiv  # Plus
    | plusOrMinus MINUS multOrDiv # Minus
    | multOrDiv                   # ToMultOrDiv
    ;

multOrDiv
    : multOrDiv MULT pow # Multiplication
    | multOrDiv DIV pow  # Division
    | pow                # ToPow
    ;

pow
    : unaryMinus (POW pow)? # Power
    ;

unaryMinus
    : MINUS unaryMinus # ChangeSign
    | atom             # ToAtom
    ;

atom
    : PI                    # ConstantPI
    | E                     # ConstantE
    | DOUBLE                # Double
    | INT                   # Int
    | ID                    # Variable
    | LPAR plusOrMinus RPAR # Braces
    ;
```
我們進入點由prog改為input
```bash
antlr4 Expr2.g4
javac Expr*.java
grun Expr2 input -gui
```
![](https://i.imgur.com/pMxVwXZ.png)
輸入完畢4+3+2-1*4/4
windows 要按 ctrl+z中止輸入
![](https://i.imgur.com/sPtzB3l.png)
我們就可以看到可視化的gui,跟前面的nodejs 版本tree.toStringTree(parser)閱讀起來清晰多了.

然後官方的範例
Listener Approach 範例
```node.js
import { ANTLRInputStream, CommonTokenStream } from 'antlr4ts';
import { MyGrammarLexer } from "./gen/MyGrammarLexer";
import { MyGrammarParser } from "./gen/MyGrammarParser";

import { MyGrammarListener } from './gen/MyGrammarListener'
import { IntContext } from './gen/MyGrammarParser'
import { ParseTreeWalker } from 'antlr4ts/tree/ParseTreeWalker'

// Create the lexer and parser
let inputStream = new ANTLRInputStream("4+3+2-1*4/4");
let lexer = new  MyGrammarLexer(inputStream);
let tokenStream = new CommonTokenStream(lexer);
let parser = new MyGrammarParser(tokenStream);
parser.buildParseTree = true;
let tree = parser.input();
console.log(tree);

let test = parser;
console.log(test);
class EnterFunctionListener implements MyGrammarListener {
  // Assuming a parser rule with name: `functionDeclaration`
  enterInt(context: IntContext) {
    console.log(`Function start line number ${context._start.line}`)
    // ...
  }

  // other enterX functions...
}

// Create the listener
const listener: MyGrammarListener = new EnterFunctionListener();
// Use the entry point for listeners
ParseTreeWalker.DEFAULT.walk(listener, tree)
console.log(tree.toStringTree(parser));
```

```node.js
import { MyGrammarListener } from './gen/MyGrammarListener'
import { IntContext } from './gen/MyGrammarParser'
import { ParseTreeWalker } from 'antlr4ts/tree/ParseTreeWalker'
```
這些都是根據你的grammar自動生成
enterInt(context: IntContext)
這邊範例變成去攔截Int的變數就觸發，以antrl4權威指南中的範例，listener可以做為翻譯用途
![](https://i.imgur.com/5vE14Fj.png)
比較方便的是在node.js可以直接console.log(context);
我們就可以直接看,int context有多少成員直接用。

Visitor Approach
Note you must pass the -visitor flag to antlr4ts to get the generated visitor file.
visitor範例我們直接看
https://github.com/Crtrpt/ts_calculator
目錄結構
注意要run 他的範例
package.json
```json
  "wl": "ts-node src\\main.ts"
```
要改為
```json
  "wl": "ts-node ./src/main.ts"
```
這樣才找的到main.ts
```node.js
import { CharStreams, CommonTokenStream } from "antlr4ts";
import EvalVititor from "./EvalVititor";
import { MyGrammarLexer } from "./gen/MyGrammarLexer";
import { MyGrammarParser } from "./gen/MyGrammarParser";

var input = `4+3+2-1*4/4`;
console.log(input);
let inputStream = CharStreams.fromString(input);
let lexer = new MyGrammarLexer(inputStream);
let tokenStream = new CommonTokenStream(lexer);
let parser = new MyGrammarParser(tokenStream);
parser.buildParseTree = true;
let tree = parser.input();

let evalVititor = new EvalVititor();
let ret = evalVititor.visit(tree);
console.log("result");
console.log(ret);
```

前面跟官網的都大同小異

EvalVititor.ts
```node.js
import { MyGrammarVisitor } from "./gen/MyGrammarVisitor";
import { AbstractParseTreeVisitor } from 'antlr4ts/tree/AbstractParseTreeVisitor'
import { BracesContext, DivisionContext, IntContext, MinusContext, MultiplicationContext, MultOrDivContext, PlusContext, ToMultOrDivContext } from "./gen/MyGrammarParser";

export default class EvalVititor extends AbstractParseTreeVisitor<number>  implements MyGrammarVisitor<number>{
    
    protected defaultResult(): number {
       return 0;
    }

    aggregateResult(aggregate: number, nextResult: number) {
        return aggregate + nextResult
      }

    visitInt(ctx:IntContext):number{
        return parseInt(ctx.text);
    }
    visitBraces(ctx:BracesContext):number {
        console.log("最先访问");
        return this.visit(ctx.getChild(1));
    }
    visitPlus(ctx:PlusContext):number{
        console.log(ctx.getChild(1).text);
        var left=this.visit(ctx.getChild(0));
        var right=this.visit(ctx.getChild(2));
        console.log("当前值"+(left+right));
        return left+right;
    }

    visitMinus(ctx:MinusContext):number{
        console.log(ctx.getChild(1).text);
        var left=this.visit(ctx.getChild(0));
        var right=this.visit(ctx.getChild(2));
        console.log("当前值"+(left-right));
        return left-right;
    }

    visitMultiplication(ctx:MultiplicationContext):number{
        var left=this.visit(ctx.getChild(0));
        var right=this.visit(ctx.getChild(2));
        var ops=ctx.getChild(1).text;
        console.log(ops);
        return left*right;
    }

    visitDivision(ctx:DivisionContext):number{
        var left=this.visit(ctx.getChild(0));
        var right=this.visit(ctx.getChild(2));
        var ops=ctx.getChild(1).text;
        console.log(ops);
        console.log("当前值"+left/right);
        return left/right;
    }
}
```
按照剛剛的邏輯，當抓到+-*/就會進到這些fucntion，這些fucntion
對應的是
```
PLUS  : '+';
MINUS : '-';
MULT  : '*';
DIV   : '/';
```
我們要做處理對這些operator做出相對應的動作,antlr4後面兩個範例類似java的override，我們只要override想要的fucntion或者繼承在修改就可以。

![](https://i.imgur.com/Qdaibsr.png)
   console.log(ctx.getChild(1).text);
        var left=this.visit(ctx.getChild(0));
        var right=this.visit(ctx.getChild(2));
        
對應也就是
![](https://i.imgur.com/ixWw265.png)
根據+-*/語意對這些左子樹右子樹，進行相對應的處理。

Listener 比較像是攔截然後再轉翻譯成不一樣的程式碼
https://wizardforcel.gitbooks.io/antlr4-short-course/content/calculator-listener.html

token的開頭跟結尾都會觸發一個fucntion在攔截後做出相對應的事

Visitor 就是可以直接對連續輸入的表達式進行運算，
前面例子可以看到可以中途對分析樹進行額外的運算讓表達式有意義，更多範例可能就看其他語言 (c# java c、、)
應該都有相對應的fucntion。
比較有趣的例子就是看到
https://medium.com/@amazzal.elhabib
線上ide做到自動補足等等

## References

- Terence Parr, [*The Definitive ANTLR 4 Reference*](https://pragprog.com/titles/tpantlr2/the-definitive-antlr-4-reference/), Pragmatic Bookshelf, 2013, ISBN 978-1-934356-99-9.
- [ANTLR4 Short Course — Calculator Listener](https://wizardforcel.gitbooks.io/antlr4-short-course/content/calculator-listener.html) — 文中提及的 Listener 範例延伸閱讀。

