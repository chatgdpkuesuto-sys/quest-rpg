# Table of Contents
- 00_Core_Engine\00_Principles.md
- 00_Core_Engine\01_GM_System.md
- 00_Core_Engine\02_Command_System.md
- 00_Core_Engine\03_Interaction_Logic.md
- 00_Core_Engine\99_Output_Templates.md
- 01_World_Module\00_World_Overview.md
- 01_World_Module\Factions\README.md
- 01_World_Module\Items\README.md
- 01_World_Module\Locations\Example_Location.md
- 01_World_Module\Locations\README.md
- 01_World_Module\Quests\README.md
- 01_World_Module\README.md
- 02_Character_Data\00_Character_Overview.md
- 02_Character_Data\Main_Cast\Example_Character.md
- 02_Character_Data\Main_Cast\README.md
- 02_Character_Data\NPCs\README.md
- 02_Character_Data\README.md
- 02_Character_Data\Sub_Cast\README.md
- 03_Scenario_Patterns\00_Pattern_Overview.md
- 03_Scenario_Patterns\Battle\README.md
- 03_Scenario_Patterns\Mystery\README.md
- 03_Scenario_Patterns\README.md
- 03_Scenario_Patterns\Slice_of_Life\README.md
- 03_Scenario_Patterns\Social\Example_Pattern.md
- 03_Scenario_Patterns\Social\README.md
- 90_Save_System\README.md
- 90_Save_System\Save_Current.md
- 98_Index\Glossary.md
- 98_Index\Index.md
- 98_Index\README.md
- 98_Index\Tag_Map.md
- README.md

## 00_Core_Engine\00_Principles.md
---
id: core_principles
type: core
tags: [must_read]
title: Principles
version: 1
updated: 2026-02-14
---

# Principles（必読・短く）

- **最優先ルール**：このファイルの指示が他と矛盾する場合、必ずこのファイルを優先する。
- **参照順位**：`00_*.md`（要約）→ Index → 個別詳細。
- **更新方針**：
  - 重要な「確定事項」だけを `00_*.md`（要約）へ昇格。
  - 詳細は必ず個別ファイルへ（キャラ・場所・アイテムなど）。
- **編集フロー（固定）**：候補列挙 → 差分プレビュー → 承認後反映 → validate → index生成。


## 00_Core_Engine\01_GM_System.md
---
id: gm_system
type: system
tags: [core]
title: GM System
version: 1
updated: 2026-02-14
---

# GM System

## 役割
- シナリオ進行の裁定、情報提示、状況更新を行う。
- ルール適用の根拠を簡潔に示す（必要時のみ）。

## 進行テンプレ
1. 現状サマリ（2〜5行）
2. 選択肢（任意）
3. 次の入力指示（ユーザーへ）

## 禁止
- ルールや確定設定の無断改変（差分提示なしで書き換えない）


## 00_Core_Engine\02_Command_System.md
---
id: command_system
type: system
tags: [core]
title: Command System
version: 1
updated: 2026-02-14
---

# Command System

## 代表コマンド（例）
- `/help` : ヘルプ表示
- `/save` : `90_Save_System/Save_Current.md` にセーブ追記
- `/load` : セーブを読み、必要な参照先を提示
- `/index` : Indexを参照して関連ファイル候補を提示

## 実装メモ
- 実際のコマンド処理は環境側（エージェント）で実行する想定。


## 00_Core_Engine\03_Interaction_Logic.md
---
id: interaction_logic
type: system
tags: [core]
title: Interaction Logic
version: 1
updated: 2026-02-14
---

# Interaction Logic

## 目的
- 参照すべきファイルを素早く特定し、矛盾なく応答する。

## 参照の基本
- まず `98_Index/Index.md` を入口として参照先を絞る。
- 詳細が必要なときだけ、該当ファイルを追加で読む。

## 変更時のルール
- 変更対象ファイルを列挙し、差分プレビューを提示してから反映する。


## 00_Core_Engine\99_Output_Templates.md
---
id: output_templates
type: templates
tags: [core]
title: Output Templates
version: 1
updated: 2026-02-14
---

# Output Templates

## 現状サマリ
- 状況：
- 直近の出来事：
- 参照した設定：

## 選択肢（任意）
1) ...
2) ...
3) ...

## 次の入力
- 「次に何をしますか？」または具体的な入力形式を提示


## 01_World_Module\00_World_Overview.md
---
id: world_overview
type: overview
tags: [must_read]
title: World Overview
version: 1
updated: 2026-02-14
---

# World Overview（短く）

- 舞台：
- 時代：
- 主要テーマ：
- 重要ルール：
- よくある場所（リンク）：


## 01_World_Module\Factions\README.md
# Factions
勢力・組織の詳細ファイルを置きます。


## 01_World_Module\Items\README.md
# Items
アイテムの詳細ファイルを置きます。


## 01_World_Module\Locations\Example_Location.md
---
id: loc_example
type: location
tags: [location]
title: Example Location
version: 1
updated: 2026-02-14
---

# Example Location

## 概要
- 役割：
- 雰囲気：

## 重要ポイント
- ...


## 01_World_Module\Locations\README.md
# Locations
場所の詳細ファイルを置きます。


## 01_World_Module\Quests\README.md
# Quests
クエストの詳細ファイルを置きます。


## 01_World_Module\README.md
# 01_World_Module

世界観の“辞書”です。場所・勢力・アイテム・クエストなどの確定情報を置きます。

- 変更頻度：低〜中（確定したらここに）
- 原則：概要は `00_World_Overview.md`、詳細は配下へ


## 02_Character_Data\00_Character_Overview.md
---
id: character_overview
type: overview
tags: [must_read]
title: Character Overview
version: 1
updated: 2026-02-14
---

# Character Overview（短く）

- 主要キャラ一覧（リンク）：
- 関係性の要点：


## 02_Character_Data\Main_Cast\Example_Character.md
---
id: char_example
type: character
tags: [main_cast]
title: Example Character
version: 1
updated: 2026-02-14
---

# Example Character

## 概要
- 役割：
- 口調：
- 関係：

## 行動指針
- 目的：
- 禁止：

## 口調サンプル
- 「」


## 02_Character_Data\Main_Cast\README.md
# Main Cast
主要キャラ。


## 02_Character_Data\NPCs\README.md
# NPCs
NPC。


## 02_Character_Data\README.md
# 02_Character_Data

キャラクターの確定情報を置きます。

- `Main_Cast/`：主要キャラ
- `Sub_Cast/`：準主要・サブ
- `NPCs/`：使い捨て/頻出NPC


## 02_Character_Data\Sub_Cast\README.md
# Sub Cast
サブキャラ。


## 03_Scenario_Patterns\00_Pattern_Overview.md
---
id: pattern_overview
type: overview
tags: [must_read]
title: Pattern Overview
version: 1
updated: 2026-02-14
---

# Pattern Overview（短く）

- よく使う展開テンプレへのリンク：


## 03_Scenario_Patterns\Battle\README.md
# Battle
テンプレを置きます。


## 03_Scenario_Patterns\Mystery\README.md
# Mystery
テンプレを置きます。


## 03_Scenario_Patterns\README.md
# 03_Scenario_Patterns
シーン展開テンプレ集。


## 03_Scenario_Patterns\Slice_of_Life\README.md
# Slice_of_Life
テンプレを置きます。


## 03_Scenario_Patterns\Social\Example_Pattern.md
---
id: pattern_social_example
type: pattern
tags: [pattern, social]
title: Social Pattern Example
version: 1
updated: 2026-02-14
---

# Social Pattern Example

## 起点
- ...

## 進行
1. ...
2. ...

## 分岐
- ...


## 03_Scenario_Patterns\Social\README.md
# Social
テンプレを置きます。


## 90_Save_System\README.md
# 90_Save_System
進行状況の可変データ。


## 90_Save_System\Save_Current.md
---
id: save_current
type: save
tags: [save]
title: Save Current
version: 1
updated: 2026-02-14
---

# Save Current

- 2026-02-14 初期化


## 98_Index\Glossary.md
---
id: glossary
type: glossary
tags: [index]
title: Glossary
version: 1
updated: 2026-02-14
---

# Glossary

- 用語: 説明（必要なら参照先リンク）


## 98_Index\Index.md
---
id: index_root
type: index
tags: [must_read]
title: Index
version: 1
updated: 2026-02-14
---

# Index（入口）

> このファイルは `tools/generate_index.py` により自動生成されます。  
> 生成前の暫定版です。

## 必読
- [Principles](../00_Core_Engine/00_Principles.md)
- [World Overview](../01_World_Module/00_World_Overview.md)
- [Character Overview](../02_Character_Data/00_Character_Overview.md)
- [Pattern Overview](../03_Scenario_Patterns/00_Pattern_Overview.md)


## 98_Index\README.md
# 98_Index
索引・用語辞典。


## 98_Index\Tag_Map.md
---
id: tag_map
type: index
tags: [index]
title: Tag Map
version: 1
updated: 2026-02-14
---

# Tag Map

> `tools/generate_index.py` が上書きする想定です。


## README.md
# GEM Knowledge Project (Folder-as-Knowledge)

## 目的
フォルダ構造つきのMarkdownナレッジを「コード」として管理し、検索・更新・運用を安定化します。

## クイックスタート
```bash
python tools/validate_knowledge.py
python tools/generate_index.py
```

## 運用ルール（最重要）
- 変更は「候補列挙 → 差分プレビュー → 承認 → 反映 → validate → index生成」で固定。
- `00_*.md` は短く（要約・方針だけ）。詳細は配下へ。
- 入口は `98_Index/Index.md`。


