---
id: standard_quests_index
type: index
tags: [world, quest, index, tutorial]
title: Standard Quest Index & Tutorial
version: 2.0
updated: 2026-02-17
---

# 通常クエスト一覧 (Standard Quest Index)

**`18_Quest_System.md`** に準拠したランダムクエスト集。
全50本のクエストデータは `Quests/` フォルダ内の各ランク別ファイルを参照してください。

---

## クエストデータ格納場所 (File Links)

| Rank | 推奨Lv | ファイル名 | 内容 |
|:---:|:---:|:---|:---|
| **E** | 1-2 | `Quests/Standard_Rank_E.md` | 初級クエスト (10本) |
| **D** | 3-4 | `Quests/Standard_Rank_D.md` | 中級クエスト (10本) |
| **C** | 5-6 | `Quests/Standard_Rank_C.md` | 上級クエスト (10本) |
| **B** | 7-8 | `Quests/Standard_Rank_B.md` | 英雄級クエスト (10本) |
| **A** | 9-10 | `Quests/Standard_Rank_A.md` | 神話級クエスト (10本) |

---

## チュートリアルクエスト (Tutorial)

### Rank E: 行方不明の荷物 (Missing Cargo)
*「商人の大切な荷物が、ダンジョンで紛失してしまった…」*

- **Rank**: E (推奨Lv 1-2)
- **Boss**: **盗賊団のリーダー** (Rank 2)
- **報酬**: 50 G + 荷物回収
- **場所**: 街道沿いの森

### 1. 進行フロー
- **クリア条件**: **進行度 3** 達成でボス出現。ボス撃破でクリア。

### 2. 行動と結果 (Action & Result)
| 行動 | 判定 (2d6) | 成功時の結果 (`Count+1`) | 失敗時の結果 (`Count+0`) |
|:---|:---:|:---|:---|
| **探索する** | **Speed vs 7** | 👉 **宝箱発見** (Rank E)<br>荷物が紛れ込んでいるかも？ | 👉 **敵出現** (Rank 1-2)<br>物陰から襲われる！ |
| **調査する** | **Mind vs 7** | 👉 **荷物の手がかり**<br>足跡発見 (イベント発生) | 👉 **トラップ発動** (TN 7)<br>落とし穴 `1d6` dmg |
| **交渉する** | **Charm vs 9** | 👉 **協力NPC出現**<br>目撃情報を得る | 👉 **敵増援**<br>騒がしくて敵が来る |

### 3. ボス戦
- **名前**: 荷物泥棒のボス
- **ステータス**: HP 20 / AC 12 / 攻撃 +3 (2dmg)
- **ドロップ**: 盗まれた荷物 (クエストアイテム)
