---
id: character_creation
type: rules
tags: [core, character, creation, 6_stats]
title: Character Creation (6 Stats Edition)
version: 1.0
updated: 2026-02-17
---

# キャラクター作成 (Character Creation)

**6能力値 (Power, Speed, Tough, Mind, Charm, Skill)** を使用した作成ルール。

## 1. 能力値の決定 (Stats)
以下のいずれかの方法で決定する。

### A. ポイント割り振り (Point Buy)
- **初期値**: 全て `0`
- **ポイント**: `3点` を自由に割り振る。
- **上限**: 初期作成時の上限は **`+3`** まで可能。
    - 例: Power+3, Others 0 (一点特化型)
    - 例: Power+1, Speed+1, Tough+1 (バランス型)

### B. ダイスロール (Random Roll)
- `1d6` を3回振る。出た目に対応する能力値を `+1` する。
    - 1: Power
    - 2: Speed
    - 3: Tough
    - 4: Mind
    - 5: Charm
    - 6: Skill
    - ※重複した場合、その能力値は累積する（最大+3まで）。

## 2. 算出値 (Vitals)

能力値決定後、以下を算出する。

- **最大HP**: `5 + Tough`
- **最大SP**: `3 + Mind`

## 3. ジョブ選択 (Job Selection)
**能力値が「1以上」のステータスに対応するジョブのみ選択可能。**
参照: `[JobSystem]` (`13_Job_System.md`)

- **戦士**: 要 Power 1+
- **盗賊**: 要 Speed 1+
- **魔術師**: 要 Mind 1+
- **吟遊詩人**: 要 Charm 1+
- **重装兵**: 要 Tough 1+
- **技師**: 要 Skill 1+

**Rule**: 条件を満たしていないジョブには就けない。ポイント割り振り時は計画的に行うこと。

## 4. 装備選択 (Equipment)
ジョブに応じた初期装備セットを受け取る。

- **戦士セット**: 剣(dmg2), 革鎧(AC1)
- **盗賊セット**: 短剣(dmg1), 投げナイフ, 革鎧(AC1)
- **魔術師セット**: 杖(dmg1), ローブ(AC0), ポーション
- **共通**: 冒険者セット (松明、保存食、ロープ)

## 5. パーソナリティ (Personality)
- **名前**: 自由に決定。
- **動機**: なぜ冒険に出たか (金、名声、復讐、好奇心...)。

---

## 🏁 6. ゲーム開始 (Game Start)
キャラクター作成が完了したら、直ちに以下のファイルを読み込み、物語を開始せよ。

👉 **[プロローグイベントを開始する] (01_World_Module/04_Event_Prologue.md)**

*「運命の歯車が回り出す……」*
