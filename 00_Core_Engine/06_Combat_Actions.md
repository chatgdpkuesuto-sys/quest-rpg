---
id: combat_actions
type: system
tags: [core, combat, actions, dictionary, strict]
title: Universal Action Dictionary (300 Actions)
version: 3.0
updated: 2026-02-17
---

# Universal Action Dictionary

**「この世界で不可能なことは、ダイスが『1』を出したときだけだ。」**

このファイルは、プレイヤーが思いつくあらゆる行動を**6つのステータス**に変換するための辞書です。
GMはプレイヤーの宣言を聞き、ここから最も近いアクションを選び、判定を求めてください。

---

## 1. STR: 筋力 (Power & Force)
**「物理法則を腕力でねじ伏せる」**

### 戦闘 (Combat)
- **[攻撃 (Attack)]**: `STR vs AC`
    - 基本攻撃。ダメージは武器依存。
- **[突き飛ばし (Shove)]**: `STR (Athletics) vs STR/DEX`
    - 成功時: 敵を5m吹き飛ばす、または転倒させる(Prone)。
- **[掴む (Grapple)]**: `STR (Athletics) vs STR/DEX`
    - 成功時: 敵を拘束(Grappled)。移動不可にする。
- **[武器破壊 (Sunder)]**: `STR vs AC`
    - 敵の武器や盾を攻撃する。成功すると攻撃力低下やAC低下。
- **[タックル (Tackle)]**: `STR (Athletics) vs STR/DEX`
    - 捨て身の突撃。自分も転倒する可能性があるが、敵を吹き飛ばす。
- **[首絞め (Choke)]**: `STR vs CON`
    - 拘束中の敵に対して有効。毎ターンダメージ＋沈黙(魔法不可)。
- **[人投げ (Throw Person)]**: `STR vs DEX`
    - 掴んでいる敵を、別の敵に投げつける。範囲ダメージ。

### 探索・環境 (Exploration)
- **[ドア破壊 (Break Door)]**: `STR vs DC`
    - DC10(木) 〜 DC25(鉄)。失敗すると騒音が響く。
- **[こじ開け (Force Open)]**: `STR vs DC`
    - 鍵のかかった箱やマンホールをバールで無理やり開ける。
- **[障害物除去 (Clear Debris)]**: `STR vs DC`
    - 崩れた瓦礫や倒木をどかす。
- **[ジャンプ (Jump)]**: `STR (Athletics) vs DC`
    - 幅跳び、高飛び。DC10で3m、DC20で6m。
- **[登攀 (Climb)]**: `STR (Athletics) vs DC`
    - 崖や壁を登る。失敗すると落下ダメージ。

### ソーシャル (Social)
- **[威圧 (Intimidate)]**: `STR vs WIS`
    - 暴力的なオーラで脅す。店主から情報を聞き出す時などに。
- **[机ドン (Slam Desk)]**: `STR vs WIS`
    - 交渉の席で机を叩いて主導権を握る。

---

## 2. DEX: 敏捷 (Finesse & Precision)
**「目にも止まらぬ早業」**

### 戦闘 (Combat)
- **[攻撃 (Attack)]**: `DEX vs AC`
    - 弓、ダガー、レイピアなどでの攻撃。
- **[隠密 (Hide)]**: `DEX (Stealth) vs Perception`
    - 物陰に隠れる。成功すると次回の攻撃が有利(Advantage)。
- **[目潰し (Blind)]**: `DEX (Sleight of Hand) vs CON`
    - 砂や液体を顔にかける。成功時: 1ターン盲目(Blind)。
- **[足払い (Trip)]**: `DEX (Acrobatics) vs DEX`
    - 敵のバランスを崩させる。ダメージなし、転倒付与。
- **[急所狙い (Aim)]**: `DEX vs AC (+5 DC)`
    - 難しいが、当たればクリティカル扱いになる。
- **[二刀流 (Dual Wield)]**: `DEX vs AC`
    - ボーナスアクションで逆手の武器を使う。
- **[受け身 (Breakfall)]**: `DEX vs DC`
    - 落下時や吹き飛ばされた時のダメージを半減する。

### 探索・環境 (Exploration)
- **[鍵開け (Lockpick)]**: `DEX (Thieves' Tools) vs DC`
    - DC10〜30。失敗するとピックが折れるか罠が発動する。
- **[スリ (Pickpocket)]**: `DEX (Sleight of Hand) vs Perception`
    - 気づかれずにアイテムや鍵を盗む。
- **[罠解除 (Disarm Trap)]**: `DEX vs DC`
    - 発見済みの罠を無効化する。失敗は爆発を意味する。
- **[ロープ切断 (Cut Rope)]**: `DEX vs AC`
    - シャンデリアや吊り橋のロープを遠隔で射抜く。
- **[綱渡り (Balance)]**: `DEX (Acrobatics) vs DC`
    - 細い足場を移動する。

### ソーシャル (Social)
- **[イカサマ (Cheating)]**: `DEX (Sleight of Hand) vs Perception`
    - 賭け事でカードをすり替える。
- **[早着替え (Disguise)]**: `DEX vs Perception`
    - 一瞬で変装して群衆に紛れる。
- **[ダンス (Dance)]**: `DEX (Performance) vs DC`
    - 華麗な身のこなしで注目を集める。

---

## 3. CON: 耐久 (Endurance & Guts)
**「死ぬこと以外はかすり傷」**

### 戦闘 (Combat)
- **[防御専念 (Dodge)]**: -
    - アクションとして宣言。次のターンまでAC+5、DEXセーブ有利。
- **[かばう (Cover)]**: `CON vs Attack`
    - 隣接する味方への攻撃を代わりに受ける。ダメージ軽減可。
- **[強行突破 (Overrun)]**: `CON (Athletics) vs STR`
    - 敵の包囲網を体当たりで無理やり突破する。
- **[毒霧 (Poison Breath)]**: `CON vs CON`
    - (種族特性などがあれば) 体内で生成した毒を吐く。

### 探索・環境 (Exploration)
- **[毒見 (Taste Test)]**: `CON vs DC`
    - 怪しい食べ物や液体を舐めて成分を特定する。失敗すると中毒。
- **[息止め (Hold Breath)]**: `CON vs DC`
    - 水中や毒ガスエリアでの活動時間延長。
- **[長距離走 (Marathon)]**: `CON vs DC`
    - 疲労せずに長時間移動し続ける。
- **[大食い (Eating)]**: `CON vs DC`
    - 大量の料理を食べて回復する、または大食い大会で勝つ。
- **[徹夜 (Stay Awake)]**: `CON vs DC`
    - 見張りなどで眠らずに行動する。

### ソーシャル (Social)
- **[飲み比べ (Drinking Contest)]**: `CON vs CON`
    - 酒場で情報を聞き出すための勝負。負けた方は情報を吐く。
- **[我慢比べ (Endurance Test)]**: `CON vs CON`
    - サウナ対決や、拷問に耐える。

---

## 4. INT: 知性 (Knowledge & Tactics)
**「勝負は戦う前に決まっている」**

### 戦闘 (Combat)
- **[弱点分析 (Analyze)]**: `INT (Investigation) vs Deception`
    - 敵のHP、AC、耐性、弱点を見抜く。成功時: 味方全員が情報共有。
- **[戦術指揮 (Tactics)]**: `INT vs DC`
    - 味方に指示を出し、次のターンの攻撃を有利にする。
- **[環境利用 (Use Object)]**: `INT vs DC`
    - 「あそこの樽を崩せば敵に当たる」などを計算して実行する。
- **[魔法行使 (Cast Spell)]**: `INT vs DC/Save`
    - Wizard系の魔法判定。

### 探索・環境 (Exploration)
- **[捜査 (Search)]**: `INT (Investigation) vs DC`
    - 部屋を調べて隠しアイテムや手がかりを見つける。
    - **Perception(WIS)** との違い: 「五感で気づく」のがWIS、「論理的に探す」のがINT。
- **[鑑定 (Appraise)]**: `INT vs DC`
    - アイテムの真贋、価値、魔法効果を判定する。
- **[知識回想 (Recall Lore)]**: `INT (History/Arcana) vs DC`
    - モンスターの生態や土地の歴史を思い出す。
- **[暗号解読 (Decipher)]**: `INT vs DC`
    - 未知の言語や暗号文を読む。
- **[地図作成 (Mapping)]**: `INT vs DC`
    - 正確な地図を描き、迷う確率を下げる。

### ソーシャル (Social)
- **[論破 (Debate)]**: `INT vs INT`
    - 論理的に相手を言い負かす。正論で攻める。
- **[偽造 (Forgery)]**: `INT vs Investigation`
    - 身分証や手紙の偽物を作る。
- **[値踏み (Estimate)]**: `INT vs Deception`
    - 商人の提示価格が適正か見抜く。

---

## 5. WIS: 判断 (Intuition & Will)
**「空気を読み、真実を感じ取る」**

### 戦闘 (Combat)
- **[予測 (Predict)]**: `WIS (Insight) vs Deception`
    - 敵の次の行動（誰を狙うか、大技が来るか）を読む。
- **[手当 (First Aid)]**: `WIS (Medicine) vs DC10`
    - 瀕死の味方を安定化させる、またはHPを小回復。
- **[精神統一 (Focus)]**: `WIS vs DC`
    - 恐怖(Frightened)や混乱(Stunned)を自力で解除する。
- **[祈り (Pray)]**: `WIS vs DC`
    - 神に祈り、加護(Guidance: +1d4)を得る。

### 探索・環境 (Exploration)
- **[知覚 (Perception)]**: `WIS vs Stealth`
    - 基本中の基本。敵の接近、物音、匂いに気づく。
- **[追跡 (Track)]**: `WIS (Survival) vs DC`
    - 足跡や折れた枝から獲物を追う。
- **[動物会話 (Handle Animal)]**: `WIS vs DC`
    - 動物をなだめる、または情報を聞く。
- **[直感 (Intuition)]**: `WIS vs DC`
    - GMから「悪い予感」やヒントをもらう。

### ソーシャル (Social)
- **[嘘発見 (Insight)]**: `WIS vs Deception`
    - 相手の表情や声色から嘘を見抜く。
- **[空気を読む (Read Atmosphere)]**: `WIS vs DC`
    - 今の発言が適切だったか、相手が何を求めているか察する。
- **[カウンセリング (Therapy)]**: `WIS vs DC`
    - 仲間のSanityを回復させる対話。

---

## 6. CHA: 魅力 (Personality & Presence)
**「世界を動かすのは、剣ではなく言葉だ」**

### 戦闘 (Combat)
- **[挑発 (Taunt)]**: `CHA vs WIS`
    - 敵を激怒させ、自分を攻撃させる(Tank行動)。
- **[鼓舞 (Inspire)]**: `CHA vs DC`
    - 味方を励まし、一時HPやダイスボーナスを与える。
- **[フェイント (Feint)]**: `CHA (Deception) vs WIS`
    - 視線を外させて、攻撃を有利にする。
- **[降伏勧告 (Surrender)]**: `CHA (Persuasion) vs WIS`
    - 明らかに勝っている時、敵に武器を捨てさせる。

### 探索・環境 (Exploration)
- **[情報収集 (Gather Info)]**: `CHA vs DC`
    - 酒場で噂話を集める。
- **[変装 (Impersonate)]**: `CHA (Performance) vs Insight`
    - 他人の振る舞いを真似て、別人になりすます。
- **[霊交信 (Channeling)]**: `CHA vs DC`
    - 霊や超常的な存在と対話する（Warlock/Miko）。

### ソーシャル (Social)
- **[説得 (Persuasion)]**: `CHA vs WIS`
    - 友好的に頼み事をする。値切り交渉、協力要請。
- **[欺瞞 (Deception)]**: `CHA vs Insight`
    - 嘘をつく、はったりをかます、無実を主張する。
- **[誘惑 (Seduce)]**: `CHA vs WIS`
    - 異性（または同性）をその気にさせる。好感度アップの基本。
- **[演説 (Speech)]**: `CHA vs Group WIS`
    - 群衆を扇動する、あるいは鎮める。
- **[尋問 (Interrogate)]**: `CHA (Intimidation) vs WIS`
    - 捕虜から情報を吐かせる。

---

## 7. Active Defense (Reaction)
敵のターンに使用する「防御的アクション」です。1ラウンドに1回のみ使用可能。

### 物理防御
- **[回避 (Dodge)]**: `DEX (Acrobatics) vs Attack Roll`
    - 全身を使って攻撃をかわす。ダメージを0にする。
- **[パリィ (Parry)]**: `STR (Athletics) vs Attack Roll`
    - 武器や盾で攻撃を弾く。ダメージを0にする。
    - **Constraint**: 武器または盾を装備していること。
- **[ブロック (Block)]**: `CON vs Attack Roll`
    - 鎧や肉体で衝撃を受け止める。
    - **Effect**: 成功時ダメージ半減。失敗時もAC+2扱いで計算。

### 魔法防御
- **[対抗呪文 (Counterspell)]**: `INT (Arcana) vs Spell DC`
    - 敵の魔法を打ち消す。Mage系クラス限定。
- **[不屈 (Endure)]**: `CON/WIS vs Save DC`
    - 状態異常(毒、麻痺、精神支配)の判定を再ロールする。

---

## 8. 特殊アクション (Special Actions)
ステータス複合や、特殊な状況での行動。

- **[協力 (Help)]**:
    - 他のプレイヤーの判定を助ける。相手は**有利(Advantage)**を得る。
- **[準備 (Ready)]**:
    - 「敵がドアを通ったら撃つ」のようにトリガーを設定して待機する。
- **[制作 (Craft)]**: `INT/DEX vs DC`
    - 休憩中にアイテムや料理を作る。
- **[求愛 (Propose)]**: `CHA vs DC (高難易度)`
    - NPCに結婚を申し込む。LoyaltyとSanityがMAXでないと失敗する。

---

> [!NOTE] **GM Note**
> これらは例に過ぎません。プレイヤーがリストにないことを提案したら、**最も近いステータス**を適用してください。
> - 「シャンデリアに乗って揺れながら攻撃」→ `DEX (Acrobatics)`
> - 「敵の兜を脱がせて視界を奪う」→ `Sleight of Hand (DEX)` or `Athletics (STR)`

