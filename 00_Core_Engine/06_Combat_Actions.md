---
id: combat_actions
type: system
tags: [core, combat, actions, dictionary, strict, 6_stats]
title: Universal Action Dictionary (6-Stat Edition)
version: 4.0
updated: 2026-02-18
---

# Universal Action Dictionary (6-Stat Edition)

**「この世界で不可能なことは、ダイスが『1』を出したときだけだ。」**

このファイルは、プレイヤーが思いつくあらゆる行動を**6つのステータス (Power, Speed, Tough, Mind, Charm, Skill)** に変換するための辞書です。
GMはプレイヤーの宣言を聞き、ここから最も近いアクションを選び、判定を求めてください。

---

## 1. Power: 筋力 (Strength & Force)
**「物理法則を腕力でねじ伏せる」**

### 戦闘 (Combat)
- **[攻撃 (Attack)]**: `Power vs AC`
    - 近接武器（剣、斧、槍など）での基本攻撃。
- **[突き飛ばし (Shove)]**: `Power vs Power/Speed`
    - 成功時: 敵を5m吹き飛ばす、または転倒させる(Prone)。
- **[掴む (Grapple)]**: `Power vs Power/Speed`
    - 成功時: 敵を拘束(Grappled)。移動不可にする。
- **[武器破壊 (Sunder)]**: `Power vs AC`
    - 敵の武器や盾を攻撃する。成功すると攻撃力低下やAC低下。
- **[タックル (Tackle)]**: `Power vs Power/Speed`
    - 捨て身の突撃。自分も転倒する可能性があるが、敵を吹き飛ばす。
- **[人投げ (Throw)]**: `Power vs Speed`
    - 掴んでいる敵を、別の敵に投げつける。範囲ダメージ。

### 探索・環境 (Exploration)
- **[ドア破壊 (Break Door)]**: `Power vs DC`
    - DC10(木) 〜 DC25(鉄)。失敗すると騒音が響く。
- **[障害物除去 (Clear Debris)]**: `Power vs DC`
    - 崩れた瓦礫や倒木をどかす。
- **[ジャンプ (Jump)]**: `Power vs DC`
    - 幅跳び、高飛び。DC10で3m、DC20で6m。
- **[登攀 (Climb)]**: `Power vs DC`
    - 崖や壁を登る。失敗すると落下ダメージ。

---

## 2. Speed: 敏捷 (Speed & Reflex)
**「目にも止まらぬ早業」**

### 戦闘 (Combat)
- **[攻撃 (Attack)]**: `Speed vs AC`
    - 軽量武器（短剣、レイピア）や射撃武器（弓）での攻撃。
- **[隠密 (Hide)]**: `Speed vs Mind (Perception)`
    - 物陰に隠れる。成功すると次回の攻撃が有利(Advantage)。
- **[回避 (Dodge)]**: `Speed vs Attack Roll`
    - パッシブ防御ではなく、アクティブな回避行動。
- **[イニシアチブ (Initiative)]**: `Speed Check`
    - 戦闘開始時の行動順決定。
- **[足払い (Trip)]**: `Speed vs Speed`
    - 敵のバランスを崩させる。ダメージなし、転倒付与。
- **[二刀流 (Dual Wield)]**: `Speed vs AC`
    - ボーナスアクションで逆手の武器を使う。

### 探索・環境 (Exploration)
- **[綱渡り (Balance)]**: `Speed vs DC`
    - 細い足場を移動する。
- **[受身 (Breakfall)]**: `Speed vs DC`
    - 落下ダメージを軽減する。
- **[スリ (Pickpocket)]**: `Speed vs Mind`
    - 気づかれずにアイテムや鍵を盗む。
- **[脱出 (Escape)]**: `Speed vs Power`
    - 拘束や掴みから抜け出す。

---

## 3. Tough: 耐久 (Endurance & Guts)
**「死ぬこと以外はかすり傷」**

### 戦闘 (Combat)
- **[防御 (Guard)]**: `Tough vs Attack Roll`
    - 肉体や鎧で攻撃を受け止める。ダメージ軽減判定。
- **[かばう (Cover)]**: `Tough vs Attack`
    - 隣接する味方への攻撃を代わりに受ける。
- **[強行突破 (Overrun)]**: `Tough vs Power`
    - 敵の包囲網を体当たりで無理やり突破する。
- **[毒ブレス (Poison Breath)]**: `Tough vs Tough`
    - (種族特性など) 体内で生成した毒を吐く。

### 探索・環境 (Exploration)
- **[毒見 (Taste Test)]**: `Tough vs DC`
    - 怪しい食べ物や液体を舐めて成分を特定する。失敗すると中毒。
- **[息止め (Hold Breath)]**: `Tough vs DC`
    - 水中や毒ガスエリアでの活動時間延長。
- **[長距離走 (Marathon)]**: `Tough vs DC`
    - 疲労せずに長時間移動し続ける。
- **[我慢比べ (Endurance)]**: `Tough vs DC`
    - 拷問や過酷な環境（極寒・灼熱）に耐える。

---

## 4. Mind: 知性 (Intellect & Magic)
**「勝負は戦う前に決まっている」**

### 戦闘 (Combat)
- **[魔法攻撃 (Magic Attack)]**: `Mind vs Tough/Mind`
    - 攻撃魔法の行使。
- **[弱点分析 (Analyze)]**: `Mind vs Charm (Deception)`
    - 敵のHP、AC、耐性、弱点を見抜く。
- **[戦術指揮 (Tactics)]**: `Mind vs DC`
    - 味方に指示を出し、次のターンの攻撃を有利にする。
- **[対抗呪文 (Counterspell)]**: `Mind vs Mind`
    - 敵の魔法を打ち消す。

### 探索・環境 (Exploration)
- **[捜査 (Search)]**: `Mind vs DC`
    - 部屋を調べて隠しアイテムや手がかりを見つける。
- **[知識回想 (Lore)]**: `Mind vs DC`
    - モンスターの生態や土地の歴史、魔法の知識を思い出す。
- **[暗号解読 (Decipher)]**: `Mind vs DC`
    - 未知の言語や暗号文を読む。
- **[地図作成 (Mapping)]**: `Mind vs DC`
    - 正確な地図を描き、迷う確率を下げる。

---

## 5. Charm: 魅力 (Social & Spirit)
**「世界を動かすのは、剣ではなく言葉だ」**

### 戦闘 (Combat)
- **[挑発 (Taunt)]**: `Charm vs Mind`
    - 敵を激怒させ、自分を攻撃させる(Tank行動)。
- **[鼓舞 (Inspire)]**: `Charm vs DC`
    - 味方を励まし、一時HPやダイスボーナスを与える。
- **[フェイント (Feint)]**: `Charm vs Mind`
    - 視線を外させて、攻撃を有利にする。
- **[降伏勧告 (Surrender)]**: `Charm vs Mind`
    - 明らかに勝っている時、敵に武器を捨てさせる。

### ソーシャル (Social)
- **[説得 (Persuasion)]**: `Charm vs Mind`
    - 友好的に頼み事をする。値切り交渉、協力要請。
- **[欺瞞 (Deception)]**: `Charm vs Mind`
    - 嘘をつく、はったりをかます、無実を主張する。
- **[誘惑 (Seduce)]**: `Charm vs Mind`
    - 異性（または同性）をその気にさせる。好感度アップの基本。
- **[威圧 (Intimidate)]**: `Charm vs Mind`
    - 恐怖で相手を従わせる。
- **[情報収集 (Gather Info)]**: `Charm vs DC`
    - 酒場で噂話を集める。

---

## 6. Skill: 技術 (Technique & Dexterity)
**「神は細部に宿る」**

### 戦闘 (Combat)
- **[急所攻撃 (Precision)]**: `Skill vs AC`
    - 敵の隙間を縫うような精密射撃や刺突。
- **[応急手当 (First Aid)]**: `Skill vs DC`
    - 傷ついた味方を治療する。HP小回復。
- **[罠設置 (Set Trap)]**: `Skill vs Mind`
    - 戦闘中に簡易的な罠を仕掛ける。

### 探索・環境 (Exploration)
- **[鍵開け (Lockpick)]**: `Skill vs DC`
    - 鍵のかかった扉や宝箱を開ける。
- **[罠解除 (Disarm Trap)]**: `Skill vs DC`
    - 発見済みの罠を無効化する。
- **[工作 (Craft)]**: `Skill vs DC`
    - アイテムの修理、道具の作成、料理。
- **[鑑定 (Appraise)]**: `Skill vs DC`
    - アイテムの価値や仕組みを詳しく調べる（Mindは知識、Skillは観察眼）。
- **[演奏 (Perform)]**: `Skill vs DC`
    - 楽器の演奏や曲芸を行う。

---

## 7. 特殊アクション (Special Actions)

- **[協力 (Help)]**:
    - 他のプレイヤーの判定を助ける。相手は**有利(Advantage)**を得る。
- **[準備 (Ready)]**:
    - 「敵がドアを通ったら撃つ」のようにトリガーを設定して待機する。
- **[屈服奥義 (Submission)]**:
    - **条件**: 敵HPが30%以下、かつ敵が「ひるみ」「転倒」「魅了」などの状態異常であること。
    - **判定**: `Power/Skill/Charm vs Tough/Mind`
    - **効果**: 敵を戦闘不能にし、捕獲・服従させる（R-18演出あり）。
