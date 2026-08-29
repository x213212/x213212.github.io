---
title: "antlr4ts online ide auto-completion example"
date: "2022-10-02T14:00:00.005+08:00"
updated: "2022-10-04T22:45:58.832+08:00"
permalink: "/2022/10/antlr4ts-online-ide-auto-completion.html"
original_url: "https://x8795278.blogspot.com/2022/10/antlr4ts-online-ide-auto-completion.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-1566107211544697879"
tags: ["antlr4ts", "Node.js"]
layout: post
---

![](https://i.imgur.com/1cIhNqM.png)

https://segmentfault.com/a/1190000040712964
https://medium.com/better-programming/create-a-custom-web-editor-using-typescript-react-antlr-and-monaco-editor-bcfc7554e446
# antlr4
https://github.com/amazzalel-habib/TodoLangEditor
https://medium.com/better-programming/create-a-custom-web-editor-using-typescript-react-antlr-and-monaco-editor-bcfc7554e446
作者在最後有稍微提示要做自動補足要如何做，我們來補起來
直接run 專案可能會出錯
這邊我給修正過後的package.json
```json
{
  "name": "todolangeditor",
  "version": "1.0.0",
  "description": "TodoLang editor",
  "scripts": {
    "start": "webpack-dev-server --hot --open",
    "antlr4ts": "antlr4ts ./TodoLangGrammar.g4 -o ./src/ANTLR"
  },
  "author": "Open",
  "license": "ISC",
  "dependencies": {
    "antlr4ts": "^0.5.0-alpha.3",
    "monaco-editor-core": "^0.18.1",
    "react": "^16.8.6",
    "react-dom": "^16.8.6"
  },
  "devDependencies": {
    "@types/node": "7.0.7",
    "@types/react": "^16.8.12",
    "@types/react-dom": "^16.8.3",
    "@webpack-cli/serve": "^1.7.0",
    "antlr4ts-cli": "^0.5.0-alpha.3",
    "css-loader": "^3.3.0",
    "html-webpack-plugin": "^3.2.0",
    "style-loader": "^1.0.1",
    "ts-loader": "^5.3.3",
    "typescript": "^4.8.4",
    "webpack": "^4.29.6",
    "webpack-cli": "^4.10.0",
    "webpack-dev-server": "^4.11.1"
  }
}

```
我們從setupLanguage();進入修改
![](https://i.imgur.com/xcBNPyl.png)

新增TodoLangAutoCompletionProvider2
```nodejs

import * as monaco from "monaco-editor-core";
import { WorkerAccessor } from "./setup";

export default class TodoLangAutoCompletionProvider2 {
    private worker: WorkerAccessor;
    TodoLangAutoCompletionProvider2(worker: WorkerAccessor) {
        this.worker = worker;

    }
    // resolveCompletionItem?(model: editor.ITextModel, position: Position, item: CompletionItem, token: CancellationToken): ProviderResult<CompletionItem>{
    public async get_label(resource: monaco.Uri): Promise<Array<string | undefined> > {
        let suggestions = [];
        // get the worker proxy
        const worker = await this.worker(resource)
        // call the validate methode proxy from the langaueg service and get errors
        const formattedCode = await worker.get_label();
        console.log(formattedCode);

        return formattedCode;

    }
    
}
```
回到setup.ts新增
```node.js
export function setupLanguage() {
    (window as any).MonacoEnvironment = {
        getWorkerUrl: function (moduleId, label) {
            if (label === languageID)
                return "./todoLangWorker.js";
            return './editor.worker.js';
        }
    }
    monaco.languages.register(languageExtensionPoint);
    monaco.languages.onLanguage(languageID, () => {
        monaco.languages.setMonarchTokensProvider(languageID, monarchLanguage);
        monaco.languages.setLanguageConfiguration(languageID, richLanguageConfiguration);
        const client = new WorkerManager();

        const worker: WorkerAccessor = (...uris: monaco.Uri[]): Promise<TodoLangWorker> => {
            return client.getLanguageServiceWorker(...uris);
        };
        //Call the errors provider
        new DiagnosticsAdapter(worker);
        let tw = new TodoLangAutoCompletionProvider2();
        tw.TodoLangAutoCompletionProvider2(worker);

        // triggerCharacters.push('C');

        // let tmp =new TodoLangAutoCompletionProvider(worker);
        monaco.languages.registerDocumentFormattingEditProvider(languageID, new TodoLangFormattingProvider(worker));
        // monaco.languages.registerCompletionItemProvider(languageID,  new TodoLangAutoCompletionProvider(worker));
        monaco.languages.registerCompletionItemProvider(languageID, {
            triggerCharacters: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'],
            provideCompletionItems: async function (model, position, context) {
                let get_label;
                let suggestions=[];
                console.log(get_label);
                console.log(context.triggerCharacter);
                get_label = await tw.get_label(model.uri);
                for (let index = 0; index < get_label.length; ++index) {
                    const element = get_label[index];
                    // console.log(element);
                    if (element != undefined)
                        if (element.indexOf(context.triggerCharacter) > 0) {

                            console.log(element);
                            suggestions.push({
                                label: element,
                                insertText: element,
                                kind: 1,
                            });
                        }
                }
    
                return { suggestions };
            },
        });
    });

}

export type WorkerAccessor = (...uris: monaco.Uri[]) => Promise<TodoLangWorker>;
```

主要透過get_label
去跟worker.languageService去拿我們的ast define name
```js
    public get_label():Promise<Array<string | undefined>> {
        const code = this.getTextDocument();
        return Promise.resolve(this.languageService.get_label(code));
    }
```

```js
import { TodoExpressionsContext, AddExpressionContext, CompleteExpressionContext } from "../ANTLR/TodoLangGrammarParser";
import { parseAndGetASTRoot, parseAndGetSyntaxErrors, parseAndGetLable } from "./parser";
import { ITodoLangError } from "./TodoLangErrorListener";

export default class TodoLangLanguageService {
    public input:string;
    validate(code: string): ITodoLangError[] {
        const syntaxErrors: ITodoLangError[] = parseAndGetSyntaxErrors(code);
        const ast: TodoExpressionsContext = parseAndGetASTRoot(code);
        const get_label: Array<string | undefined> = parseAndGetLable(code);
        // console.log(ast.children);
        // console.log(syntaxErrors);
        // console.log(get_label);
      
        return syntaxErrors.concat(checkSemanticRules(ast, get_label));
    }
    get_label(code: string): Array<string | undefined> {
        const get_label: Array<string | undefined> = parseAndGetLable(code);
        return  get_label;
    }

    format(code: string): string {
        // if the code contains errors, no need to format, because this way of formating the code, will remove some of the code
        // to make things simple, we only allow formatting a valide code
        if (this.validate(code).length > 0)
            return code;
        let formattedCode = "";
        const ast: TodoExpressionsContext = parseAndGetASTRoot(code);
        ast.children.forEach(node => {
            if (node instanceof AddExpressionContext) {
                // if a Add expression : ADD TODO "STRING"
                const todo = node.STRING().text;
                formattedCode += `ADD TODO ${todo}\n`;
            } else if (node instanceof CompleteExpressionContext) {
                // If a Complete expression: COMPLETE TODO "STRING"
                const todoToComplete = node.STRING().text;
                formattedCode += `COMPLETE TODO ${todoToComplete}\n`;
            }
        });
        return formattedCode;
    }
}

function checkSemanticRules(ast: TodoExpressionsContext, get_label: Array<string | undefined>): ITodoLangError[] {
    const errors: ITodoLangError[] = [];
    const definedTodos: string[] = [];
    // console.log(definedTodos);
    // errors.forEach(element => {
    //     let serach =element.input;
    //     get_label.forEach(element2 => {
    //         if(  element2.indexOf(serach) >0)
    //         console.log(element2);
    //         // some.indexOf("fmpe");  //11
    //         // some.indexOf("ldaspojpoe"); //-1
    //     });
    // });
   
    ast.children.forEach(node => {

        if (node instanceof AddExpressionContext) {
            // if a Add expression : ADD TODO "STRING"
            const todo = node.STRING().text;
            // console.log(todo);
            // If a TODO is defined using ADD TODO instruction, we can re-add it.
            if (definedTodos.some(todo_ => todo_ === todo)) {
                // node has everything to know the position of this expression is in the code
                errors.push({
                    code: "2",
                    endColumn: node.stop.charPositionInLine + node.stop.stopIndex - node.stop.stopIndex,
                    endLineNumber: node.stop.line,
                    message: `Todo ${todo} already defined`,
                    startColumn: node.stop.charPositionInLine,
                    startLineNumber: node.stop.line,
                    input: ""
                });
            } else {
                definedTodos.push(todo);
            }
        } else if (node instanceof CompleteExpressionContext) {
            const todoToComplete = node.STRING().text;
            // console.log(todoToComplete);
            if (definedTodos.every(todo_ => todo_ !== todoToComplete)) {
                // if the the todo is not yet defined, here we are only checking the predefined todo until this expression
                // which means the order is important
                errors.push({
                    code: "2",
                    endColumn: node.stop.charPositionInLine + node.stop.stopIndex - node.stop.stopIndex,
                    endLineNumber: node.stop.line,
                    message: `Todo ${todoToComplete} is not defined`,
                    startColumn: node.stop.charPositionInLine,
                    startLineNumber: node.stop.line,
                    input: ""
                });
            }
        }

    })
    return errors;
}

```

```js
import { TodoLangGrammarParser, TodoExpressionsContext } from "../ANTLR/TodoLangGrammarParser";
import { TodoLangGrammarLexer } from "../ANTLR/TodoLangGrammarLexer";
import { ANTLRInputStream, CommonTokenStream } from "antlr4ts";
import TodoLangErrorListener, { ITodoLangError } from "./TodoLangErrorListener";

function parse(code: string): {ast:TodoExpressionsContext, errors: ITodoLangError[],get_lable:Array<string | undefined>} {
    const inputStream = new ANTLRInputStream(code);
    const lexer = new TodoLangGrammarLexer(inputStream);
    lexer.removeErrorListeners()
    const todoLangErrorsListner = new TodoLangErrorListener();
    lexer.addErrorListener(todoLangErrorsListner);
    const tokenStream = new CommonTokenStream(lexer);
    const parser = new TodoLangGrammarParser(tokenStream);
    parser.removeErrorListeners();
    parser.addErrorListener(todoLangErrorsListner);
    const ast =  parser.todoExpressions();
    const get_lable =parser.get_label;
    const errors: ITodoLangError[]  = todoLangErrorsListner.getErrors();
    return {ast, errors,get_lable};
}
export function parseAndGetASTRoot(code: string): TodoExpressionsContext {
    const {ast} = parse(code);
    return ast;
}
export function parseAndGetSyntaxErrors(code: string): ITodoLangError[] {
    const {errors} = parse(code);
    
    return errors;
}

export function parseAndGetLable(code: string):Array<string | undefined> {
    const {get_lable} = parse(code);
    return get_lable;
}

```

這邊TodoLangGrammarParser重寫一個fucntion出來，得到public get_label: Array<string | undefined>
![](https://i.imgur.com/5VhURTh.png)
整體大概是邏輯觸發錯誤時去抓define_lable出來

registerCompletionItemProvider 每次觸發會透過TodoLangAutoCompletionProvider2撈取存在worker的lable.

這邊要注意非同步async
provideCompletionItems: async function (model, position, context)
![](https://i.imgur.com/2S712qP.png)
用index 抓取關鍵字也就是get_label的Array
![](https://i.imgur.com/iKD1c1G.png)

![](https://i.imgur.com/NpXIA6T.png)

到這邊就完成作者的自動補全。
![](https://i.imgur.com/284rQo3.png)

其他功能也能正常WORK.

在稍微改裝一點我們換成vscode 風格，如果在加上前面的riscv模擬器，就可以變成線上ide
目前寫好按鈕假設，搞清楚input ouput我們就可以模擬在線上ide執行riscv指令。

https://github.com/x213212/TodoLangEditor?organization=x213212&organization=x213212
![](https://i.imgur.com/1cIhNqM.png)

