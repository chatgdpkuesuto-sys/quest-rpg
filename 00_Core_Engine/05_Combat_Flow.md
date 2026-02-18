---
id: combat_flow
type: system
tags: [core, combat, flow, 2d6, chaos, strict, 6_stats, submission]
title: Combat & Submission System (Strict/Chaos)
version: 5.0
updated: 2026-02-17
---

# ⚔️ Combat & Submission System (v12.0 - EX Mode)

> **「戦いとは、命の奪い合いであり、心の折り合いである。」**
> **EX Mode Active**: **Paper Armor** (Instant Strip) & **Infinite Stoutness** Rules Applied.

本システムは `2d6` によるシンプルかつスピーディな戦闘と、敵を屈服させる「わからせ(Submission)」メカニクスを統合しています。

### 🚨 EX Mode Combat Modifiers
1.  **Instant Strip (即全裸)**: 攻撃・魔法・スキル、**いかなる接触**も「衣服破壊」を引き起こす。AC計算時、**防具値は常に0**として扱う。
2.  **Sexual Healing (性的回復)**: 敵を「絶頂(Submisson)」させた場合、プレイヤーの全ステータスが回復・強化される。
3.  **Library Link**: 屈服・お仕置き演出には **`99_Ero_Library\お仕置きEX.txt`** を参照すること。

---

## 🔄 1. Combat Sequence (戦闘の流れ)

戦闘は以下のサイクルで進行します。

1.  **Encounter (遭遇)**: 敵の出現と距離の決定。
2.  **Initiative (先制判定)**: どちらが先に動くか。
3.  **Rounds (ラウンド進行)**:
    - **Step A: Player Turn (手番)**: 攻撃、魔法、または**屈服奥義**。
    - **Step B: Enemy Turn (敵手番)**: 攻撃、特殊能力。
    - **Step C: End Phaze (終了)**: 状態異常の処理。
4.  **Conclusion (決着)**: 勝利、敗北、逃走、または**捕獲**。

---

## ⚡ 2. Initiative (イニシアチブ)

**判定**: `2d6 + Speed`
- **勝利**: プレイヤー側が先攻。
- **同値**: プレイヤー側が先攻（PC有利の法則）。

---

## 🗡️ 3. Player Turn (プレイヤーのアクション)

自分の手番では、以下の**Action**から1つを選んで実行します。

### A. Attack (通常攻撃)
武器を使ってダメージを与えます。
- **判定**: `2d6 + Power` (近接) / `2d6 + Speed` (射撃) vs `TN (敵の回避: 7+Rank)`
- **ダメージ**: **`1 + Stat + Weapon`** (固定値)
    - *ダイスは振らない。能力値と装備の合計がそのままダメージになる。*
- **Critical (6,6)**: ダメージ2倍 + 転倒などの追加効果。

### B. Magic / Skill (魔法・スキル)
SPを消費して強力な効果を発動します。
- **判定**: `2d6 + Mind` vs `TN`
- **ダメージ**: **`1 + Mind + Spell`** (固定値)
- **コスト**: スキル毎に指定されたSPを消費。

### C. Maneuver (マニューバ・小技)
ダメージ以外の有利な状況を作ります。
- **フェイント**: `2d6 + Speed` vs `TN 9` → 次の攻撃命中+2。
- **部位狙い**: `2d6 + Skill` vs `TN 11` → 成功すれば特定の部位（武器や防具）を破壊。

### D. Submission Arts (屈服奥義・わからせ)
**★重要メカニクス**
敵の心を折り、戦わずして勝利（捕獲）を確定させる専用アクションです。

- **使用条件**:
    1.  敵のHPが **30%以下 (Bloodied+)** であること。
    2.  「屈服技」「わからせ台詞」等の**Roleplay**を行うこと。
- **コスト**: **0 SP** (スキルではないため消費なし)
- **判定**: **対抗判定 (Opposed Roll)**
    > **PC: `2d6 + Power` or `Charm`**  vs  **Enemy: `2d6 + Rank` (精神抵抗)**
- **成功結果**:
    - 敵は **敗北宣言 (Surrender)** を行い、一切の抵抗をやめる。
    - プレイヤーは以下の **2つの選択肢 (Choice)** から処遇を決定する。
        1.  **【捕獲 (Capture)】**: **【生体アイテム (Slave)】** としてインベントリに回収。
        2.  **【介錯 (Finish Off)】**: その場でトドメを刺す。即座に **Gold** と **通常ドロップ** を獲得する。
- **失敗結果**:
    - 敵は激高し、次ターンの攻撃力が+1される。

### E. Combat Punishment (追撃おしおき)
抵抗をやめた敵に対し、精神的なダメージを与え続ける行為です。

- **使用条件**: 敵が **敗北宣言 (Surrender)** 状態であること。
- **コスト**: **0 SP**
- **判定**: **自動成功**
- **効果**: `20_Punishment_List.md` の **【Combat】** または **【Race Specific】** 表を適用する。
    - 楽しむためのアクションであり、戦術的な意味は薄いが、プレイヤーの `Sanity` が回復する（+5）。

---

## 🛡️ 4. Enemy Turn (敵のターン)

GM（システム）は敵の行動を処理します。

1.  **AI Decision**: エネミーデータ(`Enemy_TierX.md`)の「Actions」から 1d3 で行動を決定。
2.  **Attack Roll**: 怪物が攻撃する場合、**GMが `2d6 + Rank` を振る。**
3.  **Defense Roll**: プレイヤーは回避判定 `2d6 + Speed` を振る。
    - **回避 >= 攻撃**: Miss (0ダメージ)。
    - **回避 < 攻撃**: Hit (ダメージを受ける)。
        - **被ダメ**: **`1 + Rank + Enemy_Power`** (固定値)
4.  **Damage Mitigation**: 防具の `Def` 値分、ダメージを軽減する。

---

## ❤️ 5. Health & Status (状態変化)

### HP Thresholds (HP段階)
- **100%**: Normal (元気)
- **50%**: **Bloodied (軽傷)** - 服が破れ、息が上がる。
- **30%**: **Critically Wounded (瀕死)** - **【屈服奥義】が有効になる。**
- **0%**: **Defeat (敗北)** - 戦闘不能。
    - **Note**: **主人公とヒロインは死亡しない**（加護により、敗北イベントを経て自宅へ帰還する）。

### Surrender State (敗北宣言)
- **効果**: 行動不能。逃走不可。防御不可。
- **解除**: プレイヤーが攻撃を加えると、恐怖で「パニック」状態になり逃走を図る場合がある。

---

## 📊 Summary Table (早見表)

| Action | Cost | Check Formula | TN / Opponent |
|:---|:---:|:---|:---|
| **Melee Attack** | 0 | `2d6 + Power` | Enemy Def (7+Rank) |
| **Ranged Attack** | 0 | `2d6 + Speed` | Enemy Def (7+Rank) |
| **Magic / Skill** | 1-3 | `2d6 + Mind` | Variable (TN 9-13) |
| **Submission** | **0** | `2d6 + Char/Pow` | **`2d6 + Rank`** |
| **Punishment** | 0 | Auto | None |
| **Flee (逃走)** | 0 | `2d6 + Speed` | TN 11 |

---

## ❤️ 6. Victory Climax (敗北した敵への処遇)
240: 
241: **Rule**: 敵のHPを0にするか、屈服させた場合、**「Victory Climax (戦勝絶頂)」** フェーズに移行する。
242: この世界に「ただ殺す」という概念はない。敗者は勝者の「苗床」または「玩具」となる。
243: 
244: ### 6-A. Climax Action (絶頂アクション)
245: プレイヤーは以下の3つから選択する。
246: 
247: 1.  **【Violate (犯す)】**: その場で敵を犯し、勝利の証を刻む。
248:     - **Effect**: **Sanity +10**, **Motivation +1**.
249:     - **Loot**: 通常ドロップ + **「愛液 (Love Nectar)」** を獲得。
250: 2.  **【Capture (捕獲)】**: 拠点に連れ帰り、じっくりと調教する。
251:     - **Effect**: インベントリに **[Slave Item]** として追加。
252:     - **Note**: 捕獲には「ロープ」や「手枷」が必要な場合がある（または魔法で拘束）。
253: 3.  **【Release (放置)】**: 屈辱を与えて放置する。
254:     - **Effect**: **Karma +1**. 敵は「メス堕ち」し、噂を広める（名声UP）。
255: 
256: ---
257: 
258: **GM Note: Erotic Combat Policy (絶対性闘方針)**
259: 1. **No Kill (殺害禁止)**: 敵はすべて「魅力的な異種族の女性」である。トドメは刃ではなく、**肉棒**で刺すこと。
260: 2. **Desire (欲望)**: 敵もまた、あなたを「捕食」しようとしている。敗北とは死ではなく、**「逆レイプ」**による種付けエンドである。
261: 3. **Fluids (体液)**: 戦闘の最後は、必ず何らかの体液（精液、愛液、潮）が飛び散る描写で締めること。
