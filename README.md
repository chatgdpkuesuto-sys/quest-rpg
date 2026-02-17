# 💎 GEM Fantasy RPG Project (Version 6.0)

**"剣と魔法、そして運命に抗う重力(Anti-Gravity)の冒険へ"**

このプロジェクトは、**決定論的AIエンジン (Anti-Gravity Mode)** を搭載した、テキストベースのTRPGシステム兼データ集です。
LLMの「ゆらぎ」を排除し、厳格なルールと数値に基づいたゲームプレイを提供します。

---

## 🧠 Core Engine: Anti-Gravity Mode

本システムは、以下の厳格な運用ディレクティブに基づいて動作します。
詳細は **[`00_Core_Engine/00_Index.md`](00_Core_Engine/00_Index.md)** を参照してください。

1.  **Intent Resolution**: プレイヤーの入力は、定義された `Intent Enum` (Move, Attack, Persuadeなど) に厳密に分類されます。
2.  **Rule Priority**: ナラティブよりもルール、ルールよりもシステム指令が優先されます。
3.  **State Management**: HP、SP、Sanity、Loyaltyなどの数値は、物語の都合で変動することはなく、ダイスとルールによってのみ変化します。

---

## 📂 コンテンツ・インデックス (Table of Contents)

### 1. システム (System)
- **[ルールブック (Rule System)](00_Core_Engine/04_Rule_System.md)**: 2d6ベースの判定システム。6つの基本能力値とLUCK。
- **[ジョブ＆スキル (Job System)](00_Core_Engine/13_Job_System.md)**: SP消費型のスキルシステム。
- **[戦闘フロー (Combat Flow)](00_Core_Engine/05_Combat_Flow.md)**: 厳格なラウンド進行とアクション定義。
- **[暗黒ルール (Dark Rules)](00_Core_Engine/07_Dark_Rule_System.md)**: Sanity(正気度)、Loyalty(忠誠度)、そして「堕ちる」プロセス。
- **[絶対エロルール (Absolute Ero Rule)](00_Core_Engine/00_Absolute_Ero_Rule.md)**: R-18コンテンツの安全かつ過激な描写ガイドライン。

### 2. 世界とデータ (World & Data)
- **[ワールド設定 (World Overview)](01_World_Module/00_World_Overview.md)**: 世界観、歴史、地理。
- **[仲間キャラクター (Allies)](01_World_Module/Allies/)**: **全100名**のヒロイン・仲間たち。
    - 全員に「出会い(Encounter)」と「特殊イベント(Special Episode)」を実装済み。
- **[モンスター (Enemies)](01_World_Module/Enemies/)**: Tier 1〜5 までの敵データ。ドロップアイテム完備。
- **[クエスト (Quests)](01_World_Module/Quests/)**: Rank E〜A (各10本) の標準クエストと、ストーリークエスト。
    - **[標準クエスト索引](01_World_Module/03_Standard_Quests.md)**
    - **[シナリオクエスト](01_World_Module/02_Scenario_Quests.md)**
- **[アイテム (Items)]**: 300種以上の武器・防具・道具。
    - [武器](00_Core_Engine/14_Item_Weapons.md) / [防具](00_Core_Engine/15_Item_Armor.md) / [消耗品](00_Core_Engine/16_Item_Consumables.md)

---

## 🎮 遊び方 (How to Play)

1.  **セットアップ**: AIに `00_Core_Engine/00_Index.md` を読み込ませ、「Anti-Gravity Mode」を起動します。
2.  **キャラ作成**: 名前、ジョブ、ステータスを決定します。
3.  **冒険の開始**: 「ポート・ブリーズ」の街からスタートし、クエストボード(`Standard Quests`)を確認します。
4.  **探索と戦闘**: 
    - `Intent: Move` でダンジョンを進み、`Intent: Attack` で敵を倒します。
    - `Intent: Interact_NPC` で仲間と交流し、親密度を深めます。
5.  **成長と堕落**:
    - 経験値を得てレベルアップするか、Sanityを失い「堕ちたスキル」に目覚めるか。
    - すべてはダイス（乱数）の結果次第です。

---

## 🔨 更新履歴 (Update Log)
- **v6.0**: 仲間イベント100人分実装。Anti-Gravity Mode (System Directives) の確立。
- **v5.0**: パラメータ(STR/DEX等)の6能力値化。ジョブシステム刷新。
- **v4.0**: アイテム・ドロップシステムの完全データ化。

---
*Project GEM: Gravity-Defying Ero-RPG Module.*
