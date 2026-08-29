---
title: "Pyhton 股票回測繪製BBand與爬蟲"
date: "2018-07-14T12:38:00.001+08:00"
updated: "2019-09-13T08:53:13.270+08:00"
permalink: "/2018/07/pyhton-bband.html"
original_url: "https://x8795278.blogspot.com/2018/07/pyhton-bband.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3295785621346414291"
tags: ["Python", "Stock", "Tutorial"]
layout: post
---

## 繪製BBand與爬蟲

## --- 技術指標用的好，也要批量選股，我們先來看初步繪圖成果吧新增了選擇檔案，稍微改了一下介面，等等批量股票篩選（暫不小心用太多執行續被官網鎖IPQQ

[![](https://i.imgur.com/VUJAjZa.png)](https://i.imgur.com/VUJAjZa.png)
[![](https://i.imgur.com/IgvRJZR.png)](https://i.imgur.com/IgvRJZR.png)

  

  

  

## BBAND.py

## --- ```html <script src="https://gist.github.com/x213212/b318d59c5981761ebda669a3bf0b1f09.js"></script> ```

## 爬蟲與篩選

## --- ```html <script src="https://gist.github.com/x213212/3e27f0ad95d4aa6be0a763aca9af71fa.js"></script> ```

像我想爬近三個月的成交量異常！？的股票，爬下來在分析再串自動下單！？，當然也要夠本，交易策略濾網要非常嚴謹，就可以放在家自動交易！？（後果不負責xd
[![](https://i.imgur.com/lqQXU4P.png)](https://i.imgur.com/lqQXU4P.png)
## 多執行緒下次調１０個好了，這次不知道要被鎖幾天，被當成ddos囉

換連手機一下
[![](https://i.imgur.com/TPZfBXR.png)](https://i.imgur.com/TPZfBXR.png)
[![](https://i.imgur.com/THEAihX.png)](https://i.imgur.com/THEAihX.png)
快像了快像了
## 下次目標

## ---

假設經過一票海選後，像是成交量阿還是要搜尋什麼類型的技術指標阿等等等等，我們可以把爬蟲後的資料，下再下來或倒入資料庫，下次爬蟲的時候我們只要爬，最近一筆再把他家進資料庫，這樣就可以下次不必再依賴yahoo資料庫，直接對自己資料庫要資料，我們不只可以用tick來做高頻交易（還要串ａｐｉ交易，你相信中華電信的網路嗎xdd，等等打造一個看盤軟體，或向xq操盤大師那樣什麼策略警示，等等，至於資料量的多寡，恩恩自己去爬吧xd，接下來我們初步就完成一個最最最最基本的自動交易軟體的雛型囉，那麼ai真的真的真的要要來看一下囉，ㄎㄎ我會不會被一堆賣課程的針對‵，應該不會它們應該更有技術含量！
