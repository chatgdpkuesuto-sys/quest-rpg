---
id: drop_tables
type: system
tags: [core, rules, drop, loot, chest, quest, luck, d100, japanese]
title: ドロップ・宝箱・報酬テーブル (Master Loot Tables)
version: 3.1
updated: 2026-02-17
---

# ドロップ・宝箱・報酬テーブル (Master Loot Tables)

全てのアイテムは以下のファイルを参照します：
- `14_Item_Weapons.md` (武器)
- `15_Item_Armor.md` (防具)
- `16_Item_Consumables.md` (道具・換金)

---

## 1. ドロップ判定 (Drop Check) [LUCK]
敵1体を倒すごとに `d100` をロールする。
このロールには **キャラクターのLUCK修正 (幸運)** が加算される。

> **Drop Roll = `1d100 + LUCK修正 + 継続ボーナス`**

| ロール値 | 結果 (Result) | 内容 (Content) |
|:---|:---|:---|
| **01-40** | **ハズレ / ゴミ** | XPのみ、または 1d10 Gold |
| **41-70** | **通常ドロップ** | XP + `換金アイテム (Rank E)` or `消耗品` |
| **71-90** | **装備ドロップ** | XP + `通常装備 (Rank E-D)` |
| **91-110** | **レアドロップ** | XP + **`レア装備` (Affix付き)** |
| **111+** | **伝説級** | XP + **`レジェンダリー` (Rank A-S)** |

> **継続ボーナス**: Phase 4で「継続」を選択中、ロール値に **+20**。

---

## 2. 宝箱テーブル (Treasure Chests)
ダンジョン内で発見した宝箱の中身。
**[罠解除判定: DEX vs 罠DC]** または **[強運回避: LUCK vs 罠DC]** で処理する。

### Tier 1 (Rank E - 初級)
- **罠 (DC 10)**: 毒針(Poison), 警報(Encounter)
- **Gold**: `2d10 + 20` G
- **Item Roll (d100)**:
    - **01-50**: ポーション x2, 松明 x3
    - **51-80**: [武器][防具] Rank E Random
    - **81-95**: [換金] Rank E Valuable
    - **96-00**: **Rare Table** (Affix付き)

### Tier 2 (Rank D - 中級)
- **罠 (DC 13)**: 爆発(`2d6` Fire), 麻痺ガス(Paralyze)
- **Gold**: `5d10 + 100` G
- **Item Roll (d100)**:
    - **01-40**: ハイポーション, 毒消し
    - **41-75**: [武器][防具] Rank D Random
    - **76-90**: [換金] Rank D Valuable
    - **91-00**: **Rare Table**

### Tier 3 (Rank C - 上級)
- **罠 (DC 16)**: 石化ガス, ミミック(戦闘)
- **Gold**: `10d10 + 500` G
- **Item Roll (d100)**:
    - **01-30**: 万能薬, エクストラポーション, 巻物
    - **31-70**: [武器][防具] Rank C Random
    - **71-85**: [換金] Rank C Valuable
    - **86-00**: **Rare Table**

### Tier 4 (Rank B - 英雄級)
- **罠 (DC 20)**: 転送装置(分断), 死神の鎌(即死)
- **Gold**: `20d20 + 2000` G
- **Item Roll (d100)**:
    - **01-20**: 蘇生薬, エリクサー
    - **21-60**: [武器][防具] Rank B Random
    - **61-80**: [換金] Rank B Valuable
    - **81-00**: **Legendary Table**

### Tier 5 (Rank A/S - 神話級)
- **罠 (DC 25+)**: 次元断絶(キャラロスト), 全員HP1
- **Gold**: `5000+` G
- **Item Roll (d100)**:
    - **01-50**: **Legendary Table (Rank A)**
    - **51-00**: **Mythic Table (Rank S)**

---

## 3. クエスト報酬計算式 (Quest Rewards)

> **報酬額 = 基本Gold + (討伐数 x 倍率) + LUCKボーナス**

| Quest Rank | 基本Gold | 討伐倍率 (1体あたり) | アイテム報酬 |
|:---|:---|:---|:---|
| **Rank E** | 50 G | +5 G | ポーション x3 |
| **Rank D** | 200 G | +10 G | ハイポーション, 解錠ツール |
| **Rank C** | 800 G | +50 G | 魔法のスクロール, [Rank C] Item |
| **Rank B** | 3000 G | +100 G | 蘇生薬, [Rank B] Item |
| **Rank A** | 10000 G | +500 G | **Legendary Item** |

- **LUCKボーナス**: 報酬受け取り時に `LUCK判定` に成功すると、追加の報奨金(+20%)やコネクションを得られる。

---

## 4. レア・特殊効果 (Rare & Affix) [LUCK Reroll]

`Rare Drop` 確定時、**LUCK判定(DC 15)** に成功すると、Affix決定ロールを一度だけ振り直すことができる。

### 武器 Affix (d20)
1.  **鋭利な (Sharp)**: Damage +1
2.  **重厚な (Heavy)**: Dmg +2, Hit -1
3.  **軽量な (Light)**: Hit +1
4.  **残虐な (Brutal)**: クリティカル率UP
5.  **ゴブリン殺しの**: 対ゴブリン +1d6
6.  **死霊殺しの**: 対アンデッド +1d6
7.  **竜殺しの**: 対ドラゴン +2d6
8.  **燃える (Burning)**: +1d4 火ダメージ
9.  **凍てつく (Frozen)**: +1d4 氷ダメージ
10. **痺れる (Shocking)**: +1d4 雷ダメージ
11. **吸血の (Vampiric)**: ダメージの10%回復
12. **幸運の (Lucky)**: ドロップ率 +5%
13. **必中の (Accurate)**: Hit +2
14. **名匠の (Masterwork)**: 1の目を振り直し
15. **呪われた (Cursed)**: Dmg +5 / 自傷 1d4
16. **神速の (Speed)**: 追加攻撃(Bonus Action)
17. **首切りの (Vorpal)**: クリティカル時 即死
18. **聖なる (Holy)**: +1d8 光ダメージ(対アンデッド)
19. **暗黒の (Dark)**: +1d6 闇ダメージ
20. **古代の (Ancient)**: ランク+1 相当

### 防具 Affix (d20)
1.  **頑丈な (Sturdy)**: AC +1
2.  **活力の (Vitality)**: MaxHP +5
3.  **耐性の (Resistance)**: 属性耐性 (火/氷など)
4.  **回避の (Evasion)**: DEX Save +1
5.  **不屈の (Iron Will)**: WIS Save +1
6.  **隠密の (Lightweight)**: 隠密有利
7.  **棘付き (Spiked)**: 反射ダメージ 1
8.  **癒やしの (Healing)**: 毎ターン HP1 回復
9.  **四次元 (Pocket)**: アイテム枠 +2スロット
10. **魅惑の (Glamorous)**: CHA +1
11. **堅固な (Fortified)**: クリティカル無効
12. **俊足の (Swift)**: 移動速度 +5ft
13. **魔力の (Arcane)**: MP +5
14. **静寂の (Silent)**: 隠密 +2
15. **幸運の (Lucky)**: 全セーヴ +1
16. **聖なる (Holy)**: 闇属性半減
17. **暗黒の (Dark)**: 光属性半減
18. **慈愛の (Generous)**: HP回復魔法の効果UP
19. **幽体の (Ghostly)**: 物理耐性(小) / 魔法弱点
20. **アダマン (Adamant)**: AC +2 / 重さ2倍
