---
title: "Custom Vscode Extension Analyzer Debug 2"
date: "2021-10-25T04:22:00.000+08:00"
updated: "2021-10-25T04:22:16.552+08:00"
permalink: "/2021/10/custom-vscode-extension-analyzer-debug-2.html"
original_url: "https://x8795278.blogspot.com/2021/10/custom-vscode-extension-analyzer-debug-2.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-95450302958365453"
tags: ["static analyzer", "VS Code Extension"]
layout: post
---

![](https://blogger.googleusercontent.com/img/a/AVvXsEi5UKSO5lqlGiwlA7I5Xzfa7o2d5guwBGqdRt5_OcgmnCukn-trd3BaqHm_5tny14PrFXtgaBl9xAdPsg89fac7aMyP-EZbqgzCF4KHNZLAMcIO9yVphrsDzVH7ONLOF7vUARdcOR1gMjjpILYDRCuK1CN1nPIvwX5s2-bBR94ioXHQ94nrhVUqzYyQ=s320)

# Custom Vscode Extension Analyzer Debug 2
vscode Extension  先開放也無所謂(?
![](https://i.imgur.com/P8zh3WL.png)

```typescript
// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import { DebugSession } from 'vscode';

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
var arrays = []; // empty array
 var init = 0;
export function activate(context: vscode.ExtensionContext) {
	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "helloworld-sample" is now active!');
	// let globalStoragePath = context.globalStoragePath;
	context.subscriptions.push(vscode.debug.onDidChangeBreakpoints(
		session => {
			var fs = require('fs');

			const globalStoragePath = context.globalStoragePath;
			if (session['removed'].length > 0) {
				let i = 0;
				let find = -1;
				for (let array of arrays) {
					for (let sess of session['removed']) {
						console.log(sess['location']['uri']['path']);
						// console.log("sess");

						if (array['path'] == sess['location']['uri']['path']) {
							// for (let array of arrays) {

							// }
							let linesrc = (Number(sess['location']['range']['_start']['_line']) );
							if (Number(array['line']) == linesrc) {
								console.log("find");
								find = i;
								break;
							}
						}
						// const index = array.indexOf(sess['bid']);
						// if (index > -1) {
						// 	array.splice(index, 1);
						// }
					}
					// console.log(array);
					i++;
				}
				if (find >= 0) {
					arrays.splice(find, 1);
				}
				console.log(arrays);
				fs.unlink(globalStoragePath + '/breakpoint.txt', (err: any) => {
					if (err) console.log('init error');
				})
				for (let array of arrays) {
							fs.appendFile(globalStoragePath + '/breakpoint.txt', array['path'] + " " + (Number(array['line']) + 1) + "\n", function (err: any) {
								if (err)
									console.log(err);
								else
									console.log('Write operation complete.');
							});
				}
				// console.log(session['removed'][0]['_id']);
				// console.log(session['removed']);
			}
			// vscode.debug.registerDebugAdapterDescriptorFactory

			// object literal notation to create your structures
			if (session['added'].length > 0) {
				let find =-1;
				
					for (let array of arrays) {
						for (let sess of session['added']) {
							console.log(sess['location']['uri']['path']);
							// console.log("sess");
	
							if (array['path'] == sess['location']['uri']['path']) {
								// for (let array of arrays) {
	
								// }
								let linesrc = (Number(sess['location']['range']['_start']['_line']) );
								if (Number(array['line']) == linesrc) {
									console.log("find");
									find = i;
									break;
								}
							}
							// const index = array.indexOf(sess['bid']);
							// if (index > -1) {
							// 	array.splice(index, 1);
							// }
						}
						// console.log(array);
					}
					
				
				if( find ==-1)
					for (let sess of session['added']) {

						// const obj = Object.values(sess);
						// const path = Object.values(obj[1]);
						// const line = Object.values(obj[1]);
						// let getpath = path[0];
						// let getline = path[1];
						// // var property = 'path';
						// // console.log(line);
						// console.log(getpath['path']);
						// console.log(getline['_start']['_line']);
						// // console.log(obj);
						// // Object.keys(test).forEach(key => {
						// // 	console.log(key);
						// //   });
						// // console.log(sess.location.url);
						// fs.appendFile(globalStoragePath + '/breakpoint.txt', getpath['path'] + " " + (Number(getline['_start']['_line']) + 1) + "\n", function (err: any) {
						// 	if (err)
						// 		console.log(err);
						// 	else
						// 		console.log('Write operation complete.');
						// });
						let id = sess['_id'];
						let pathstc = sess['location']['uri']['path'];
						let linesrc = (Number(sess['location']['range']['_start']['_line']) );
						arrays.push({ bid: id, path: pathstc, line: linesrc });
						// console.log(id);
						// console.log(pathstc);
						// console.log(linesrc);
						// console.log(sess);
					
				}
				console.log(arrays);
				// if(init == 0)
				// init =1;
				// console.log("globalStoragePath" + globalStoragePath);
				// console.log("Breakpoint changed" + session.added);
				fs.unlink(globalStoragePath + '/breakpoint.txt', (err: any) => {
					if (err) console.log('init error');
				})
				for (let array of arrays) {
							fs.appendFile(globalStoragePath + '/breakpoint.txt', array['path'] + " " + (Number(array['line']) + 1) + "\n", function (err: any) {
								if (err)
									console.log(err);
								else
									console.log('Write operation complete.');
							});
				}
			}
		}
	))

	// const storagePathCast = (context.storageUri as vscode.Uri).path;
	// const globalStoragePath = context.globalStorageUri.path;
	// The command has been defined in the package.json file
	// Now provide the implementation of the command with registerCommand
	// The commandId parameter must match the command field in package.json

	const disposable = vscode.commands.registerCommand('extension.helloWorld', () => {

		// The code you place here will be executed every time your command is executed
		vscode.debug.onDidReceiveDebugSessionCustomEvent(event => {
			// console.log(event.event);
			if (event.event == 'stopped') {

				console.log("Hello World!");
			}
		})
		// vscode.debug.registerDebugAdapterTrackerFactory('*', {

		// 	createDebugAdapterTracker(session: DebugSession) {

		// 		return {
		// 			onWillReceiveMessage: m => console.log(`> ${JSON.stringify(m, undefined, 2)}`),
		// 			onDidSendMessage: m => console.log(`< ${JSON.stringify(m, undefined, 2)}`)
		// 		};
		// 	}
		// });
		// Display a message box to the user
		vscode.window.showInformationMessage('welcome use Gcc plugin analyzer');
		const storagePath = context.storagePath;
		const globalStoragePath = context.globalStoragePath;
		console.log("storagePath" + storagePath);

		vscode.window.showInformationMessage(globalStoragePath + "/breakpoint.txt")
		// var fs = require('fs');
		// fs.unlink(globalStoragePath + '/breakpoint.txt', (err: any) => {
		// 	if (err) console.log('init error');
		// })
		//Write to output.
		// orange.appendLine("storagePath");
		// console.log("globalStoragePath" + globalStoragePath);
		// context.workspaceState.update('keyA', 'keyAValue');
		/*
		* 取得memento的資料，可設定初始預設值
		*/
		// context.workspaceState.get('keyB', 'defaultValue');

	});

	context.subscriptions.push(disposable);
}

```

