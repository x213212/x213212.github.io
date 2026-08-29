---
title: "git command"
date: "2024-05-02T01:31:00.001+08:00"
updated: "2024-05-02T01:31:00.445+08:00"
permalink: "/2024/05/git-command.html"
original_url: "https://x8795278.blogspot.com/2024/05/git-command.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6486697550662622305"
tags: ["git"]
layout: post
---

![](https://hackmd.io/_uploads/ryCS2leGA.png)

![image](https://hackmd.io/_uploads/ryCS2leGA.png)

# git merge
ex 假設兩個分支master 和 a
有個文件為test.log
```
a
```
```
git add ./test.log
git commit -m 'add test.log'
```
切到 branch a
```
git checkout a
```
```
a
b
```

```
git add ./test.log
git commit -m 'add b'
git push -f
```
切回master
```
git checkout master
git merge a
```
接下來就可以vscode 解決衝突完再push

# git rebase
假設一個文件有5個commit
```
commit a
commit b
commit c
commit d
commit e
```
分別對應文字檔案
```
a commit a
b commit b
c commit c
d commit d
e commit e
```
假設要commit 要最近五筆commit
git rebase -i HEAD~5 ,那麼起始點就是從a開始
之後會進入一個ui 介面你可以選擇那些要pick 和 drop
比如說 a ~ e我只想留 a 和 e 那我b~d 都drop
```
git add ./test.log
git rebase --continue
```
大概就是從a開始為基底，假設操作都是drop 則會直接顯示到e commit 的內容
```
current<<
a 
current<<
b 
c 
d 
e 
incomming<<
```
預設 git rebase的交互環境為 nano 要透過crtl + x 來儲存操作就可以了按下y 存檔就可以看到git 已經套用剛剛的操作
```
git log push -f 
```
由於已經影響分支所以記得加上-f
```
commit a
commit e
```
所以最終commit 剩這樣就可以好好整理

然後每次的
```
git add ./test.log
git rebase --continue
```
其實還會問你要不要重新命名當下commit,所以可以順便重構一下當時的commit

```
pick: 保留該 commit（這是預設行為）。
reword: 保留 commit，但修改提交信息。
edit: 在應用該 commit 之後暫停，以便你可以修改文件並做出更多的 commit，或對現有的 commit 做更動。
squash: 將該 commit 與前一個 commit 合併，並合併它們的提交信息。
fixup: 將該 commit 與前一個 commit 合併，但只保留前一個 commit 的提交信息。
drop: 從歷史中完全刪除該 commit。
```
# git stash
假設線上有更新的版本那麼我開發速度比線上的版本還要舊其實可以透過
```
git stash 
```
push 歷史記錄到stack 裡面
然後下
```
git pull 
```
抓取最新的code下來
在下
```
git stash pop
```
將本地修改pop出來

再透過
```
git diff 
```
看那些東西有被改到再去vscode 看是否要用上最新的版本code解決衝突後就可以push了
```
git push
```
# git submodule
假設有兩個專案a,b
在a大專案下面嵌套b就可以下
```
git submodule add https://github.com/x213212/test_sub.git b
git add ./
git commit -m 'add b submodule'
```
這樣的話假設下面模組有更新則可以下
```
git submodule update --remote
```
更換 submodule
```
cd test_git  # 進入 A 專案目錄
git submodule deinit test_sub  # 移除原有的子模組配置
git rm test_sub  # 從 Git 中移除子模組的追蹤
git commit -m "Removed submodule test_sub"  # 提交變更

git submodule add https://github.com/x213212/test_sub.git test_sub
git submodule update --init --recursive 
```
自動a 專案順便將目錄下的 submodule 都clone
```
git clone --recurse-submodules https://github.com/x213212/test_git
```

