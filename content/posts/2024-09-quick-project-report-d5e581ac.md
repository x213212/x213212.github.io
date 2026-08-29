---
title: "Quick Project Report (chatgpt)"
date: "2024-09-29T06:55:00.002+08:00"
updated: "2024-09-29T19:58:20.437+08:00"
permalink: "/2024/09/quick-project-report.html"
original_url: "https://x8795278.blogspot.com/2024/09/quick-project-report.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8471100425639409224"
tags: ["openai", "rust"]
layout: post
---

![](https://hackmd.io/_uploads/H1RNSWUCA.png)

# 最近看code很麻煩 用chatgpt 寫一個摘要系統
![image](https://hackmd.io/_uploads/H1RNSWUCA.png)
![image](https://hackmd.io/_uploads/SyPNrZLC0.png)
![image](https://hackmd.io/_uploads/HJkLH-8CC.png)
這邊採用chatgpt 問答的方式 去過濾目錄沒有比較更好的想法哈哈,
key就定義在目錄下自行替換
![image](https://hackmd.io/_uploads/HJ2nHbLRA.png)
github :https://github.com/x213212/QPRhttps://github.com/x213212/QPR
```rust
// ===========================
// 可配置的常數
// ===========================

// 伺服器埠號設定
const SERVER_PORT: u16 = 3030;

// 程式碼檔案的副檔名清單
const CODE_FILE_EXTENSIONS: &[&str] = &[
    "rs", "py", "js", "ts", "java", "cpp", "c", "go", "sh", "rb", "bat", "cs", "resx","h","md",
];

// GPT 提示語設定（包含佔位符 {}）
const FOLDER_ANALYSIS_PROMPT: &str = "請根據以下資料夾名稱進行分析，過濾出可能是使用者撰寫的源代碼目錄 ,並返回一個 JSON 結構，key強迫為 'analysis_key'，值為符合條件的資料夾名稱的陣列：\n{folders}\n{extra_folders}";

const FILE_SUMMARY_PROMPT: &str = "請為以下程式碼生成一個簡短的功能摘要，不超過100個字。請用專業的軟體工程師風格描述該源代碼具體在做什麼，程式碼變數請保留原來的變數名稱英文，好讓我可以快速分析。請用繁體中文：\n{}";

// 專案目錄路徑設定
const PROJECT_PATH: &str = "/root/Ghost";

// ===========================
// 可配置的常數
// ===========================

// 伺服器埠號設定
const SERVER_PORT: u16 = 3030;

// 程式碼檔案的副檔名清單
const CODE_FILE_EXTENSIONS: &[&str] = &[
    "rs", "py", "js", "ts", "java", "cpp", "c", "go", "sh", "rb", "bat", "cs", "resx","h","md",
];

// GPT 提示語設定（包含佔位符 {}）
const FOLDER_ANALYSIS_PROMPT: &str = "請根據以下資料夾名稱進行分析，過濾出可能是使用者撰寫的源代碼目錄 ,並返回一個 JSON 結構，key強迫為 'analysis_key'，值為符合條件的資料夾名稱的陣列：\n{folders}\n{extra_folders}";

const FILE_SUMMARY_PROMPT: &str = "請為以下程式碼生成一個簡短的功能摘要，不超過100個字。請用專業的軟體工程師風格描述該源代碼具體在做什麼，程式碼變數請保留原來的變數名稱英文，好讓我可以快速分析。請用繁體中文：\n{}";

// 專案目錄路徑設定
const PROJECT_PATH: &str = "/root/Ghost";

```
```sh
收集的資料夾：
收集的資料夾：
Ghost
  Server
    CharServer
      Accounts
      Characters
      Interoperability
      Net
      Properties
    Common
      Collections
      Constants
      Data
      IO
        Packet
      Net
      Properties
      Security
      Threading
      Utilities
    GameServer
      Ghost
        Accounts
        Characters
        Map
        Provider
      Interoperability
      Net
        Handler
        Packet
      Properties
    LoginServer
      Accounts
      Interoperability
      Net
      Properties
    MessageServer
      Characters
      Interoperability
      Net
      Properties

重新過濾後的結果：
{
   "analysis_key":[
      "CharServer",
      "GameServer"
   ]
}
請輸入要保留的資料夾名稱（以逗號分隔，或輸入 'ok' 表示完成）：
ok
最終選定的資料夾為：
[
    "CharServer",
    "GameServer",
]
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Characters/CharacterTrade.cs
已完成摘要：/root/Ghost/Server/CharServer/Storage.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Storage.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/FishHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Quest.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Pet.cs
已完成摘要：/root/Ghost/Server/CharServer/Shortcut.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Characters/CharacterItems.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Provider/CashShopFactory.cs
已完成摘要：/root/Ghost/Server/CharServer/Net/CharPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Characters/CharacterKeyMap.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Characters/CharacterUseSlot.cs
已完成摘要：/root/Ghost/Server/CharServer/Accounts/Account.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Item.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/ActionHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Interoperability/InteroperabilityClient.cs
已完成摘要：/root/Ghost/Server/CharServer/Skill.cs
已完成摘要：/root/Ghost/Server/CharServer/Characters/CharacterSkills.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Client.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/NpcShopHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Accounts/NoAccountException.cs
已完成摘要：/root/Ghost/Server/CharServer/Net/Client.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Shortcut.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/ItemData.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Map/Loot.cs
已完成摘要：/root/Ghost/Server/CharServer/Item.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Member.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/GameHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/PetHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Characters/CharacterQuests.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/PvPHandler.cs
已完成摘要：/root/Ghost/Server/CharServer/Characters/CharacterStorages.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Characters/CharacterPets.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Characters/CharacterShop.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/PetPacket.cs
已完成摘要：/root/Ghost/Server/CharServer/CharServer.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Commodity.cs
已完成摘要：/root/Ghost/Server/CharServer/Interoperability/InteroperabilityClient.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/PartyHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/SpiritHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/PartyPacket.cs
已完成摘要：/root/Ghost/Server/CharServer/Characters/CharacterKeyMap.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Characters/Character.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Accounts/Account.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Skill.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/CouponHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/StoragePacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/FishPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/QuestPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/PlayerShopPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Provider/PetFactory.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/CashShopHandler.cs
已完成摘要：/root/Ghost/Server/CharServer/Characters/Character.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Map.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/GameServerHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Provider/MobFactory.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/MonsterHandler.cs
已完成摘要：/root/Ghost/Server/CharServer/Net/CharHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Characters/CharacterStorages.cs
已完成摘要：/root/Ghost/Server/GameServer/GameServer.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/StatusPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/StatusHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Monster.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/SkillPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/PvPPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/CashShopPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/QuestHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/MonsterPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/MapPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/GamePacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/TradeHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/SkillHandler.cs
已完成摘要：/root/Ghost/Server/CharServer/Characters/CharacterUseSlot.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/PlayerShopHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/TradePacket.cs
已完成摘要：/root/Ghost/Server/CharServer/Characters/CharacterItems.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/StorageHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Properties/AssemblyInfo.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Provider/ItemFactory.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/InventoryPacket.cs
已完成摘要：/root/Ghost/Server/CharServer/Accounts/NoAccountException.cs
已完成摘要：/root/Ghost/Server/CharServer/Properties/AssemblyInfo.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Characters/CharacterParty.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Map/Drop.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/InventoryHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Provider/MapFactory.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/MapHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Characters/CharacterSkills.cs
啟動網頁伺服器，請訪問 http://127.0.0.1:3030unt.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Item.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/ActionHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Interoperability/InteroperabilityClient.cs
已完成摘要：/root/Ghost/Server/CharServer/Skill.cs
已完成摘要：/root/Ghost/Server/CharServer/Characters/CharacterSkills.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Client.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/NpcShopHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Accounts/NoAccountException.cs
已完成摘要：/root/Ghost/Server/CharServer/Net/Client.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Shortcut.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/ItemData.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Map/Loot.cs
已完成摘要：/root/Ghost/Server/CharServer/Item.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Member.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/GameHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/PetHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Characters/CharacterQuests.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/PvPHandler.cs
已完成摘要：/root/Ghost/Server/CharServer/Characters/CharacterStorages.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Characters/CharacterPets.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Characters/CharacterShop.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/PetPacket.cs
已完成摘要：/root/Ghost/Server/CharServer/CharServer.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Commodity.cs
已完成摘要：/root/Ghost/Server/CharServer/Interoperability/InteroperabilityClient.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/PartyHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/SpiritHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/PartyPacket.cs
已完成摘要：/root/Ghost/Server/CharServer/Characters/CharacterKeyMap.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Characters/Character.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Accounts/Account.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Skill.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/CouponHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/StoragePacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/FishPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/QuestPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/PlayerShopPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Provider/PetFactory.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/CashShopHandler.cs
已完成摘要：/root/Ghost/Server/CharServer/Characters/Character.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Map.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/GameServerHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Provider/MobFactory.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/MonsterHandler.cs
已完成摘要：/root/Ghost/Server/CharServer/Net/CharHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Characters/CharacterStorages.cs
已完成摘要：/root/Ghost/Server/GameServer/GameServer.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/StatusPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/StatusHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Monster.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/SkillPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/PvPPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/CashShopPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/QuestHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/MonsterPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/MapPacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/GamePacket.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/TradeHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/SkillHandler.cs
已完成摘要：/root/Ghost/Server/CharServer/Characters/CharacterUseSlot.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/PlayerShopHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/TradePacket.cs
已完成摘要：/root/Ghost/Server/CharServer/Characters/CharacterItems.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/StorageHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Properties/AssemblyInfo.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Provider/ItemFactory.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Packet/InventoryPacket.cs
已完成摘要：/root/Ghost/Server/CharServer/Accounts/NoAccountException.cs
已完成摘要：/root/Ghost/Server/CharServer/Properties/AssemblyInfo.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Characters/CharacterParty.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Map/Drop.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/InventoryHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Provider/MapFactory.cs
已完成摘要：/root/Ghost/Server/GameServer/Net/Handler/MapHandler.cs
已完成摘要：/root/Ghost/Server/GameServer/Ghost/Characters/CharacterSkills.cs
啟動網頁伺服器，請訪問 http://127.0.0.1:3030
```

