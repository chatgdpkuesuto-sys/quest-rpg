---
id: drop_tables
type: system
tags: [core, rules, drop, loot, chest, quest, luck, d100]
title: Drop, Chest & Reward Tables (Grand Review)
version: 3.0
updated: 2026-02-17
---

# ドロップ・宝箱・報酬テーブル (Master Loot Tables)

全てのアイテムは以下のファイルを参照します：
- `14_Item_Weapons.md` (武器)
- `15_Item_Armor.md` (防具)
- `16_Item_Consumables.md` (道具・換金)

---

## 1. ドロップ判定 (Drop Check) [LUCK]
敵1体を倒すごとに `d100` をロールします。
このロールには **Character's LUCK Modifier (幸運修正)** が加算されます。

> **Drop Roll = `1d100 + LUCK Mod + Survival Bonus`**

| Net Roll | 結果 (Result) | 内容 (Content) |
|:---|:---|:---|
| **01-40** | **Nothing / Junk** | XPのみ、または 1d10 Gold |
| **41-70** | **Base Drop** | XP + `Valuables (Rank E)` or `Consumables` |
| **71-90** | **Item Drop** | XP + `Common Equipment (Rank E-D)` |
| **91-110** | **Rare Drop** | XP + **`Rare Equipment` (With Affix)** |
| **111+** | **Legendary** | XP + **`Legendary Item` (Rank A-S)** |

> **Survival Bonus**: Phase 4で「継続」を選択中、ロール値に **+20**。

---

## 2. 宝箱テーブル (Treasure Chests)
ダンジョン内で発見した宝箱の中身です。
**[罠解除判定: DEX vs Trap DC]** または **[強運回避: LUCK vs Trap DC]** で処理します。

### Tier 1 (Rank E - 初級)
- **Trap (DC 10)**: 毒針(Poison), 警報(Encounter)
- **Gold**: `2d10 + 20` G
- **Item Roll (d100)**:
    - **01-50**: ポーション x2, 松明 x3
    - **51-80**: [武器][防具] Rank E Random
    - **81-95**: [換金] Rank E Valuable
    - **96-00**: **Rare Table** (Affix付き)

### Tier 2 (Rank D - 中級)
- **Trap (DC 13)**: 爆発(`2d6` Fire), 麻痺ガス(Paralyze)
- **Gold**: `5d10 + 100` G
- **Item Roll (d100)**:
    - **01-40**: ハイポーション, 毒消し
    - **41-75**: [武器][防具] Rank D Random
    - **76-90**: [換金] Rank D Valuable
    - **91-00**: **Rare Table**

### Tier 3 (Rank C - 上級)
- **Trap (DC 16)**: 石化ガス, ミミック(`Combat`)
- **Gold**: `10d10 + 500` G
- **Item Roll (d100)**:
    - **01-30**: 万能薬, エクストラポーション, 巻物
    - **31-70**: [武器][防具] Rank C Random
    - **71-85**: [換金] Rank C Valuable
    - **86-00**: **Rare Table**

### Tier 4 (Rank B - 英雄級)
- **Trap (DC 20)**: テレポーター(分断), 即死(Death Scythe)
- **Gold**: `20d20 + 2000` G
- **Item Roll (d100)**:
    - **01-20**: 蘇生薬, エリクサー
    - **21-60**: [武器][防具] Rank B Random
    - **61-80**: [換金] Rank B Valuable
    - **81-00**: **Legendary Table**

### Tier 5 (Rank A/S - 神話級)
- **Trap (DC 25+)**: 次元断絶(Character Lost), 全員HP1
- **Gold**: `5000+` G
- **Item Roll (d100)**:
    - **01-50**: **Legendary Table (Rank A)**
    - **51-00**: **Mythic Table (Rank S)**

---

## 3. クエスト報酬計算式 (Quest Rewards)

> **Reward = Base Gold + (Kill Count x Multiplier) + LUCK Bonus**

| Quest Rank | Base Gold | Multiplier (per kill) | Item Reward |
|:---|:---|:---|:---|
| **Rank E** | 50 G | +5 G | ポーション x3 |
| **Rank D** | 200 G | +10 G | ハイポーション, 解錠ツール |
| **Rank C** | 800 G | +50 G | 魔法のスクロール, [Rank C] Item |
| **Rank B** | 3000 G | +100 G | 蘇生薬, [Rank B] Item |
| **Rank A** | 10000 G | +500 G | **Legendary Item** |

- **LUCK Bonus**: 報酬受け取り時に `LUCK Check` に成功すると、追加の報奨金(+20%)やコネクションを得られる。

---

## 4. レア・特殊効果 (Rare & Affix) [LUCK Reroll]

`Rare Drop` 確定時、**LUCK判定(DC 15)** に成功すると、Affix ROLLを一度だけ振り直すことができます。

### 武器 Affix (d20)
1.  **Sharp**: Damage +1
2.  **Heavy**: Dmg +2, Hit -1
3.  **Light**: Hit +1
4.  **Brutal**: Crit Range +1
5.  **Goblin Slayer's**: vs Goblin +1d6
6.  **Undead Killer's**: vs Undead +1d6
7.  **Dragon Slayer's**: vs Dragon +2d6
8.  **Burning**: +1d4 Fire
9.  **Frozen**: +1d4 Cold
10. **Shocking**: +1d4 Lightning
11. **Vampiric**: 10% HP Absorb
12. **Lucky**: Drop Rate +5%
13. **Accurate**: Hit +2
14. **Masterwork**: Reroll 1s
15. **Cursed**: Dmg +5 / Self Dmg 1d4
16. **Speed**: Bonus Action Attack
17. **Vorpal**: Crit時 即死(首切り)
18. **Holy**: +1d8 Radiant vs Undead
19. **Dark**: +1d6 Necrotic
20. **Ancient**: Rank +1 treatment

### 防具 Affix (d20)
1.  **Sturdy**: AC +1
2.  **Vitality**: MaxHP +5
3.  **Resistance**: 属性耐性 (Fire/Cold/etc)
4.  **Evasion**: DEX Save +1
5.  **Iron Will**: WIS Save +1
6.  **Lightweight**: Stealth有利
7.  **Spiked**: 反射ダメージ 1
8.  **Healing**: Regen HP1/turn
9.  **Pocket**: Item Slot +2
10. **Glamorous**: CHA +1
11. **Fortified**: Crit無効化
12. **Swift**: Speed +5ft
13. **Arcane**: MP +5
14. **Silent**: Stealth +2
15. **Lucky**: Save +1
16. **Holy**: Necrotic Resist
17. **Dark**: Radiant Resist
18. **Generous**: HP回復魔法の効果UP
19. **Ghostly**: 物理耐性(小) / 魔法弱点
20. **Adamant**: AC +2 / 重さ2倍
