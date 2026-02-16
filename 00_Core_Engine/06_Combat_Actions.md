---
id: combat_actions
type: system
tags: [core, combat, actions, social]
title: Combat Actions & Social Maneuvers
version: 2.0
updated: 2026-02-16
---

# 戦闘アクション (Combat Actions)

手番に取れるアクションの一覧です。
物理的な攻撃だけでなく、**言葉や態度による精神攻撃（ソーシャルアクション）**も有効です。

## 1. 物理・魔法アクション (Standard)
- **攻撃 (Attack)**: 武器で攻撃する。
- **呪文 (Cast Spell)**: 魔法を使う。
- **早足 (Dash)**: 移動速度を2倍にする。
- **離脱 (Disengage)**: 機会攻撃を受けずに移動する。
- **回避 (Dodge)**: 全力で避ける（敵の攻撃はDisadvantage）。
- **隠れる (Hide)**: DEX(Stealth)判定で姿を消す。
- **助ける (Help)**: 味方の次の判定を有利(Advantage)にする。

## 2. ソーシャル予備動作 (Social Maneuvers)
戦闘中に敵の**Sanity**や**Loyalty**を削る、あるいは**状態異常**を与えるアクションです。
これらは標準アクションとして扱われます。

### 説得 (Persuade)
- **判定**: `CHA (Persuasion)` vs 敵の `WIS (Insight)`
- **効果**:
    - 敵の**敵意を下げる** (戦闘の終了)。
    - 敵を**寝返らせる** (Loyaltyへの攻撃)。
    - **成功**: 敵が「躊躇」状態になる(攻撃不可)。大成功なら戦闘放棄。

### 威圧 (Intimidate)
- **判定**: `STR/CHA (Intimidation)` vs 敵の `WIS (Will)`
- **効果**:
    - 敵に**恐怖(Frightened)**を与える。
    - **Sanityダメージ**: 成功時、敵に `1d6` の精神ダメージ。
    - **成功**: 敵はあなたに近づけない＆判定不利。

### 挑発 (Taunt)
- **判定**: `CHA (Deception/Performance)` vs 敵の `WIS (Insight)`
- **効果**:
    - 敵のターゲットを**自分に固定**する。
    - **成功**: 敵はあなた以外を攻撃する際、Disadvantageを受ける。

### 誘惑 (Seduce)
- **判定**: `CHA (Persuasion)` vs 敵の `WIS (Will)`
- **条件**: 異性、またはその気がある相手に有効。言葉が通じること。
- **効果**:
    - 敵を**魅了(Charmed)**する。
    - **成功**: 敵はあなたを攻撃できない。大成功なら味方を攻撃し始める。

### 分析 (Analyze)
- **判定**: `INT (Investigation)` vs 敵の `CHA (Deception)`
- **効果**:
    - 敵の**ステータス、弱点、Sanity値**を見抜く。
    - **成功**: 弱点が判明。次の味方の攻撃はAdvantage。

## 3. リアクション (Reactions)
ターン外に行える行動。1ラウンドに1回のみ。
- **機会攻撃**: 敵が自分の間合いから離れた時、1回殴れる。
- **反論 (Counter Argument)**: 敵が「説得」などをしてきた時、対抗ロールを行う。
- **身代わり (Cover)**: 隣接する味方が攻撃された時、代わりにダメージを受ける。

## 4. ボーナスアクション (Bonus Actions)
特定のスキルや状況でのみ使用可能。
- **二刀流攻撃**: 逆手武器で攻撃。
- **指揮 (Command)**: (指揮官系ジョブのみ) 味方に命令を出す。
