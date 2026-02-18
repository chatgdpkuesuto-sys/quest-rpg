# 💎 GEM Fantasy RPG Project (Version 6.1)

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
*   **[ルールブック (Rule System)](00_Core_Engine/04_Rule_System.md)**: 2d6ベースの判定システム。6つの基本能力値とLUCK。
*   **[キャラクター作成 (Character Creation)](00_Core_Engine/06_Character_Creation.md)**: **6-Stat System (Power, Speed, Tough, Mind, Charm, Skill)** によるビルドガイド。
*   **[戦闘フロー (Combat Flow)](00_Core_Engine/05_Combat_Flow.md)**: 厳格なラウンド進行とアクション定義。**屈服奥義**の実装。
*   **[おしおきリスト (Punishment List)](00_Core_Engine/20_Punishment_List.md)**: 捕獲・調教・わからせのためのデータ集。
*   **[暗黒ルール (Dark Rules)](00_Core_Engine/07_Dark_Rule_System.md)**: Sanity(正気度)、Loyalty(忠誠度)、そして「堕ちる」プロセス。

### 2. 世界とデータ (World & Data)
*   **[ワールド設定 (World Overview)](01_World_Module/00_World_Overview.md)**: 世界観、歴史、地理。
*   **[メインキャスト (Main Cast)](02_Character_Data/Main_Cast/01_Main_Cast.md)**: **全5人のヒロイン**の統合データ（ステータス・イベント）。
    *   Aria, Zena, Elara, Elize, Yuni
*   **[モンスター (Enemies)](01_World_Module/Enemies/)**: Tier 1〜5 までの敵データ。
*   **[クエスト (Quests)](01_World_Module/Quests/)**: Rank E〜S の標準クエストデータ（全95本以上）。
    *   **[標準クエスト索引](01_World_Module/03_Standard_Quests.md)**
*   **[アイテム (Items)]**: 300種以上の武器・防具・道具。

---

## 🎮 遊び方 (How to Play)

1.  **セットアップ**: AIに `00_Core_Engine/00_Index.md` を読み込ませ、「Anti-Gravity Mode」を起動します。
2.  **キャラ作成**: 名称と職業を決定し、能力値を割り振ります。
    *   `00_Core_Engine/06_Character_Creation.md` を参照。
3.  **冒険の開始**: プロローグ (`04_Event_Prologue.md`) に従い、最初のパートナーを選びます。
4.  **クエスト受注**: `Standard Quests` から自分のランクに合った依頼を受けます。
5.  **探索と戦闘**: 
    - `Intent: Move` でダンジョンを進み、`Intent: Attack` で敵を倒します。
    - **HPが30%以下の敵**には `Intent: Submission` (屈服奥義) が可能です。
    - `Intent: Interact_NPC` で仲間と交流し、親密度を深めます。

---

## 🔨 更新履歴 (Update Log)
*   **v6.1** (Current):
    *   **ファイル統合**: メインヒロインデータを `01_Main_Cast.md` に集約。
    *   **クエスト統合**: クエストデータを `Standard_Rank_E〜S.md` に再編・統合。
    *   **6-Stat System**: 全キャラクターのデータ形式を新ステータス (Power/Speed/Tough/Mind/Charm/Skill) に統一。
*   **v6.0**: **屈服・おしおきシステム** の完全実装。
*   **v5.0**: パラメータの6能力値化。ジョブシステム刷新。

---
*Project GEM: Gravity-Defying Ero-RPG Module.*
