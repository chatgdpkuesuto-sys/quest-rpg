---
id: job_system
type: rules
tags: [core, job, skills, 50_jobs, dice, unlock]
title: Job System & Skills (Complete 50)
version: 6.0
updated: 2026-02-17
---

# ジョブシステム完全版 (50 Jobs & Strict Dice)

全50種の職業データ。
**共通ルール**:
- **判定**: `1d20 + [指定ステータス] + JLv` vs 目標値(DC)
- **クリティカル(20)**: コスト無視、効果倍増、劇的成功。
- **転職**: 街のギルドで可能。ただし**解放条件**を満たす必要がある。

---

## カテゴリA: 戦士系 (Warrior Type)

### 01. 戦士 (Fighter) [STR]
- **解放条件**: 初期開放 (Default)
- **Lv1 [強打 (Bash)]**: **[判定: STR vs AC]** 物理ダメージ+2。Crit: 武器破壊。
- **Lv5 [挑発 (Taunt)]**: **[判定: STR(威圧) vs WIS]** 敵をつ引きつける。Crit: 敵が激昂して防御力低下。
- **Lv10 [投擲 (Throw)]**: **[判定: DEX vs AC]** 何でも投げる。Crit: 必中＆スタン。

### 02. 騎士 (Knight) [CON]
- **解放条件**: Fighter Lv5 + 「騎士の勲章」所持
- **Lv1 [カバー (Cover)]**: **[判定: DEX vs DC10]** 隣接味方を守る。Crit: ダメージ0。
- **Lv5 [シールドバッシュ]**: **[判定: STR vs CON]** 盾で殴りスタン。Crit: 吹き飛ばし。
- **Lv10 [不屈 (Indomitable)]**: **[判定: CON vs DC15]** HP1で耐える。Crit: ダメージ吸収回復。

### 03. 狂戦士 (Barbarian) [STR]
- **解放条件**: Fighter Lv5 + 「怒りの仮面」所持
- **Lv1 [激怒 (Rage)]**: **[判定: CON vs DC12]** 攻撃UP/防御DOWN。Crit: デメリット無し。
- **Lv5 [威圧 (Intimidate)]**: **[判定: CHA vs WIS]** 敵を怯ませる。Crit: 敵が逃走。
- **Lv10 [粉砕 (Smash)]**: **[判定: STR vs AC]** 壁や床を壊す。Crit: 地形ごと敵を埋める。

### 04. 侍 (Samurai) [STR]
- **解放条件**: Fighter Lv5 + 「名刀」所持
- **Lv1 [居合 (Iai)]**: **[判定: DEX vs Passive Perception]** 先制攻撃。Crit: 即死(雑魚)。
- **Lv5 [心眼 (Mind's Eye)]**: **[判定: WIS vs DC15]** 不可視看破。Crit: 次の攻撃必中。
- **Lv10 [一閃 (Slash)]**: **[判定: STR vs AC]** 直線範囲攻撃。Crit: 鎧無視。

### 05. パラディン (Paladin) [CHA]
- **解放条件**: Knight Lv5 + 教会の推薦状
- **Lv1 [聖なる一撃 (Smite)]**: **[判定: STR vs AC]** 光ダメージ追加。Crit: アンデッド消滅。
- **Lv5 [レイ・オン・ハンド]**: **[判定: CHA vs DC10]** HP回復(接触)。Crit: 状態異常解除。
- **Lv10 [絶対防御 (Aegis)]**: **[判定: CON vs 攻撃値]** 魔法を防ぐオーラ。Crit: 魔法反射。

### 06. モンク (Monk) [DEX]
- **解放条件**: 武器を装備せずに戦闘勝利 x 10回
- **Lv1 [連打 (Flurry)]**: **[判定: DEX vs AC]** 2回攻撃。Crit: 3回攻撃。
- **Lv5 [気功 (Chi)]**: **[判定: WIS vs DC12]** 自己回復or毒解除。Crit: 全回復。
- **Lv10 [金剛身 (Iron Body)]**: **[判定: CON vs DC15]** 物理耐性を得る。Crit: 完全無敵(1ターン)。

### 07. 狩人 (Ranger) [DEX]
- **解放条件**: 初期開放 (Default)
- **Lv1 [狙撃 (Snipe)]**: **[判定: DEX vs AC]** 遠距離攻撃。Crit: 部位破壊(足止め等)。
- **Lv5 [追跡 (Track)]**: **[判定: WIS vs DC10]** 痕跡を追う。Crit: 敵のステータス看破。
- **Lv10 [罠設置 (Trap)]**: **[判定: DEX vs Passive Perception]** 罠を仕掛ける。Crit: 致死毒の罠。

### 08. 竜騎士 (Dragoon) [STR]
- **解放条件**: Spear Mastery習得 + 「竜の心臓」を食べる
- **Lv1 [ジャンプ (Jump)]**: **[判定: STR(跳躍) vs DC10]** 高所移動/落下攻撃。Crit: 2倍ダメージ。
- **Lv5 [竜の知識 (Dragon Lor)]**: **[判定: INT vs DC15]** 竜種と会話/弱点看破。Crit: 竜を懐かせる。
- **Lv10 [ブレス (Breath)]**: **[判定: CON vs DEX]** 火炎/雷撃を吐く。Crit: 地形効果付与。

### 09. 剣闘士 (Gladiator) [STR]
- **解放条件**: 闘技場で10勝する
- **Lv1 [アピール (Appeal)]**: **[判定: CHA vs WIS]** 観客(敵味方)を沸かせる。Crit: 全員にバフ。
- **Lv5 [網投げ (Net)]**: **[判定: DEX vs DEX]** 敵を拘束。Crit: 完全拘束。
- **Lv10 [決闘 (Duel)]**: **[判定: CHA vs WIS]** 1対1を強制する。Crit: 相手の逃走不可。

### 10. 重装兵 (Guardian) [CON]
- **解放条件**: 「タワーシールド」を装備する
- **Lv1 [要塞化 (Fortress)]**: **[判定: CON vs DC10]** 移動不可になるがAC+5。Crit: 魔法耐性も得る。
- **Lv5 [押し出し (Push)]**: **[判定: STR vs STR]** 敵を強制移動。Crit: 将棋倒し発生。
- **Lv10 [仁王立ち (Stand)]**: **[判定: CON vs DC20]** 範囲攻撃を一人で受ける。Crit: ダメージ半減。

---

## カテゴリB: 盗賊・技術系 (Rogue Type)

### 11. 盗賊 (Rogue) [DEX]
- **解放条件**: 初期開放 (Default)
- **Lv1 [鍵開け (Pick Lock)]**: **[判定: DEX vs DC]** 解錠/罠解除。Crit: 罠を回収して再利用。
- **Lv5 [スリ (Steal)]**: **[判定: DEX vs Perception]** アイテムを盗む。Crit: 装備品を盗む。
- **Lv10 [早業 (Fast Hands)]**: **[判定: DEX vs DC15]** ボーナスアクション増加。Crit: 3回行動。

### 12. 暗殺者 (Assassin) [DEX]
- **解放条件**: Rogue Lv5 + 暗殺ギルドへの加入
- **Lv1 [毒調合 (Poison)]**: **[判定: INT vs DC12]** 武器に毒付与。Crit: 猛毒(CON save)。
- **Lv5 [変装 (Disguise)]**: **[判定: CHA vs Insight]** 別人に化ける。Crit: 魔法的看破不能。
- **Lv10 [暗殺 (Assassinate)]**: **[判定: DEX vs AC]** 不意打ち時即死判定。Crit: 痕跡なし。

### 13. 忍者 (Ninja) [DEX]
- **解放条件**: Rogue Lv5 + Monk Lv3
- **Lv1 [壁走り (Wall Run)]**: **[判定: DEX vs DC10]** 壁・天井移動。Crit: 水上歩行。
- **Lv5 [変わり身 (Log)]**: **[判定: DEX vs 攻撃値]** 被弾無効化。Crit: 反撃爆破。
- **Lv10 [分身 (Clone)]**: **[判定: INT vs DC15]** 囮を作る。Crit: 分身も攻撃可能。

### 14. 斥候 (Scout) [WIS]
- **解放条件**: Ranger Lv3 + 未踏破エリアの発見
- **Lv1 [聞き耳 (Listen)]**: **[判定: WIS vs DC10]** 敵の位置把握。Crit: 会話内容までクリア。
- **Lv5 [地図作成 (Map)]**: **[判定: INT vs DC12]** 周辺地形把握。Crit: 隠し通路発見。
- **Lv10 [先制 (Initiative)]**: **[判定: DEX vs DC15]** 味方全員のイニシアチブUP。Crit: 敵全員Surprise。

### 15. 海賊 (Pirate) [STR]
- **解放条件**: 船を入手する + 賞金首になる
- **Lv1 [水泳 (Swim)]**: **[判定: STR vs DC10]** 水中行動ペナルティなし。Crit: 魚並みの速度。
- **Lv5 [脅迫 (Threaten)]**: **[判定: STR vs WIS]** アイテムをカツアゲ。Crit: 金も出させる。
- **Lv10 [砲撃 (Cannon)]**: **[判定: DEX vs DEX]** 範囲爆発攻撃。Crit: 船ごと破壊。

### 16. スパイ (Spy) [CHA]
- **解放条件**: Rogue Lv5 + 機密情報を盗む
- **Lv1 [口八丁 (Bluff)]**: **[判定: CHA vs Insight]** 嘘を信じ込ませる。Crit: 永続的な信用。
- **Lv5 [暗号解読 (Decode)]**: **[判定: INT vs DC15]** 暗号文を読む。Crit: 著者の意図まで理解。
- **Lv10 [裏切り (Betray)]**: **[判定: CHA vs WIS]** 敵を味方に寝返らせる。Crit: ボスクラスも対象。

### 17. ギャンブラー (Gambler) [LUCK]
- **解放条件**: カジノで10000G稼ぐ
- **Lv1 [ダイス (Dice)]**: **[判定: LUCK vs AC]** サイコロを投げて攻撃。出目によりダメージ変動。Crit: ゾロ目で即死。
- **Lv5 [イカサマ (Cheat)]**: **[判定: DEX vs Perception]** 出目を操作(±2)。Crit: 好きな出目にする。
- **Lv10 [ジャックポット]**: **[判定: LUCK vs DC20]** 所持金を消費して超ダメ。Crit: 金が減らず増える。

### 18. 狙撃手 (Sniper) [DEX]
- **解放条件**: Ranger Lv5 + ライフル入手
- **Lv1 [ホークアイ (Hawk Eye)]**: **[判定: WIS vs DC12]** 超遠距離視認。Crit: 弱点部位看破。
- **Lv5 [隠密射撃 (Hide Shot)]**: **[判定: DEX vs Perception]** 位置バレせず攻撃。Crit: 混乱付与。
- **Lv10 [ヘッドショット]**: **[判定: DEX vs AC]** クリティカル率UP。Crit: 即死。

### 19. 罠師 (Trapper) [INT]
- **解放条件**: 罠で敵を倒す
- **Lv1 [落とし穴 (Pit)]**: **[判定: INT vs DEX]** 足止め罠作成。Crit: ダメージ付き。
- **Lv5 [爆弾設置 (Bomb)]**: **[判定: DEX vs DC15]** 時限爆弾セット。Crit: 範囲拡大。
- **Lv10 [誘導 (Lure)]**: **[判定: CHA vs WIS]** 敵を罠に誘い込む。Crit: 敵全員を一網打尽。

### 20. 踊り子 (Dancer) [CHA]
- **解放条件**: 酒場でのパフォーマンス成功
- **Lv1 [魅惑の舞 (Charm)]**: **[判定: CHA vs WIS]** 敵1体を魅了。Crit: 敵が味方を攻撃。
- **Lv5 [応援 (Cheer)]**: **[判定: CHA vs DC10]** 味方の判定+2。Crit: 判定+5。
- **Lv10 [死の舞踏 (Dance of Death)]**: **[判定: DEX vs AC]** 回避しながら攻撃。Crit: 全回避。

---

## カテゴリC: 魔法系 (Mage Type)

### 21. 魔術師 (Wizard) [INT]
- **解放条件**: 初期開放 (Default)
- **Lv1 [魔法弾 (Bolt)]**: **[判定: INT vs AC]** 魔法ダメージ。Crit: 必中。
- **Lv5 [範囲魔法 (Area)]**: **[判定: INT vs DC15]** 魔法を範囲化。Crit: 味方巻き込みなし。
- **Lv10 [二重詠唱 (Dual Cast)]**: **[判定: INT vs DC20]** 2回魔法を使う。Crit: MP消費半減。

### 22. ソーサラー (Sorcerer) [CHA]
- **解放条件**: 「魔力の血筋」特性を持つ
- **Lv1 [魔力撃 (Magic Strike)]**: **[判定: CHA vs AC]** 近接魔法攻撃。Crit: 吹き飛ばし。
- **Lv5 [魔力変換 (Convert)]**: **[判定: CON vs DC12]** HPをMPに変換。Crit: ノーコスト回復。
- **Lv10 [暴走 (Overload)]**: **[判定: CHA vs DC15]** 威力2倍だが自傷ダメ。Crit: 自傷なし。

### 23. ウォーロック (Warlock) [CHA]
- **解放条件**: 契約を結ぶ
- **Lv1 [異界の眼 (Eldritch Eye)]**: **[判定: CHA vs DC12]** 魔法視/暗視。Crit: 透視。
- **Lv5 [呪い (Curse)]**: **[判定: CHA vs WIS]** 能力値低下デバフ。Crit: 永続化。
- **Lv10 [契約召喚 (Summon)]**: **[判定: CHA vs DC20]** 異界の存在を呼ぶ。Crit: 制御成功。

### 24. ネクロマンサー [INT]
- **解放条件**: 「死者の書」を入手
- **Lv1 [死体操作 (Animate)]**: **[判定: INT vs DC10]** 死体を操る。Crit: 生前のスキル使用可。
- **Lv5 [生気吸収 (Drain)]**: **[判定: CON vs CON]** HPドレイン。Crit: MPも吸収。
- **Lv10 [死の言葉 (Word of Death)]**: **[判定: INT vs CON]** 即死魔法。Crit: 蘇生不可。

### 25. 召喚士 (Summoner) [INT]
- **解放条件**: Wizard Lv5 + 契約
- **Lv1 [精霊召喚 (Spirit)]**: **[判定: INT vs DC12]** 小精霊を使役。Crit: 上位精霊。
- **Lv5 [転移 (Teleport)]**: **[判定: INT vs DC15]** 短距離ワープ。Crit: 味方全員移動。
- **Lv10 [幻獣召喚 (Eidolon)]**: **[判定: INT vs DC25]** 大型モンスター召喚。Crit: 暴走なし。

### 26. 幻術師 (Illusionist) [INT]
- **解放条件**: 「幻影の指輪」装備
- **Lv1 [幻影 (Illusion)]**: **[判定: INT vs Insight]** 幻を見せる。Crit: 実体化(触れる)。
- **Lv5 [透明化 (Invis)]**: **[判定: INT vs DC15]** 姿を消す。Crit: 攻撃しても解けない。
- **Lv10 [精神牢獄 (Mind Prison)]**: **[判定: INT vs INT]** 敵を幻覚に閉じ込める。Crit: 廃人化(Sanity 0)。

### 27. 付与術師 (Enchanter) [INT]
- **解放条件**: Wizard Lv3 + Blacksmith Lv1
- **Lv1 [属性付与 (Enchant)]**: **[判定: INT vs DC10]** 武器に属性追加。Crit: ダメージ+5。
- **Lv5 [操作 (Control)]**: **[判定: INT vs STR]** 無機物を動かす。Crit: 敵の武器を操作。
- **Lv10 [ゴーレム作成 (Golem)]**: **[判定: INT vs DC20]** 素材から従者作成。Crit: 知性を持つ。

### 28. 時魔道士 (Time Mage) [INT]
- **解放条件**: 「時止めの砂時計」の欠片を入手
- **Lv1 [ヘイスト (Haste)]**: **[判定: INT vs DC12]** 速度UP。Crit: 2回行動付与。
- **Lv5 [スロウ (Slow)]**: **[判定: INT vs WIS]** 敵の速度DOWN。Crit: 停止(Stun)。
- **Lv10 [ストップ (Time Stop)]**: **[判定: INT vs DC30]** 時間を止める(1T)。Crit: 2ターン停止。

### 29. 風水師 (Geomancer) [WIS]
- **解放条件**: 自然サバイバル達成
- **Lv1 [地脈操作 (Terrain)]**: **[判定: WIS vs DC12]** 地形効果を利用。Crit: 地形ダメージ倍増。
- **Lv5 [天候操作 (Weather)]**: **[判定: WIS vs DC15]** 雨/晴れを変える。Crit: 嵐を呼ぶ。
- **Lv10 [地震 (Quake)]**: **[判定: WIS vs DEX]** 広範囲攻撃。Crit: 足場崩落。

### 30. 賢者 (Sage) [INT/WIS]
- **解放条件**: Wizard Lv10 + Cleric Lv10
- **Lv1 [鑑定 (Identify)]**: **[判定: INT vs DC12]** アイテム詳細判明。Crit: 隠し効果発見。
- **Lv5 [弱点看破 (Analyze)]**: **[判定: WIS vs DC15]** 敵ステータス看破。Crit: ドロップ品予知。
- **Lv10 [連続魔 (Multi Cast)]**: **[判定: INT vs DC25]** 異なる魔法を同時使用。Crit: MP消費減。

---

## カテゴリD: 聖職・支援系 (Healer Type)

### 31. 僧侶 (Cleric) [WIS]
- **解放条件**: 初期開放 (Default)
- **Lv1 [ヒール (Heal)]**: **[判定: WIS vs DC10]** HP回復。Crit: 追加HP付与(Temp HP)。
- **Lv5 [聖域 (Sanctuary)]**: **[判定: WIS vs WIS]** 攻撃されないバリア。Crit: 反射バリア。
- **Lv10 [蘇生 (Resurrect)]**: **[判定: WIS vs DC20]** 死者復活。Crit: デメリットなし。

### 32. 神官 (Priest) [WIS]
- **解放条件**: Cleric Lv5 + 寄付
- **Lv1 [浄化 (Purify)]**: **[判定: WIS vs DC10]** 毒/病気解除。Crit: 全状態異常解除。
- **Lv5 [結界 (Barrier)]**: **[判定: WIS vs DC15]** 防御力UPエリア作成。Crit: 完全無効化エリア。
- **Lv10 [神の怒り (Smite)]**: **[判定: WIS vs AC]** 聖なる光で攻撃。Crit: 敵のバフ全解除。

### 33. ドルイド (Druid) [WIS]
- **解放条件**: 森の精霊に認められる
- **Lv1 [植物操作 (Plant)]**: **[判定: WIS vs STR]** 拘束。Crit: 持続ダメージ。
- **Lv5 [野性変身 (Shape)]**: **[判定: WIS vs DC12]** 動物に変身。Crit: 魔獣に変身。
- **Lv10 [大自然の癒やし (Regen)]**: **[判定: WIS vs DC15]** 毎ターン回復付与。Crit: 範囲化。

### 34. 吟遊詩人 (Bard) [CHA]
- **解放条件**: 聴衆を感動させる
- **Lv1 [激励 (Inspire)]**: **[判定: CHA vs DC10]** 味方にダイスボーナス。Crit: ボーナス2倍。
- **Lv5 [子守唄 (Lullaby)]**: **[判定: CHA vs WIS]** 範囲睡眠。Crit: 永続睡眠（起きない）。
- **Lv10 [英雄の歌 (Hero)]**: **[判定: CHA vs DC20]** 全ステータスUP。Crit: 無敵付与。

### 35. 錬金術師 (Alchemist) [INT]
- **解放条件**: 「錬金釜」を入手
- **Lv1 [薬剤知識 (Potion Mastery)]**: **[判定: INT vs DC10]** 使用時の回復量2倍。Crit: 状態異常も治す。
- **Lv5 [爆弾投げ (Bomb)]**: **[判定: DEX vs DEX]** 範囲攻撃。Crit: 状態異常付与。
- **Lv10 [賢者の石 (Transmute)]**: **[判定: INT vs DC30]** 敵を金に変える。Crit: 莫大なGold入手。

### 36. 医師 (Doctor) [WIS]
- **解放条件**: INT 14以上 + 「医療キット」
- **Lv1 [応急手当 (First Aid)]**: **[判定: WIS vs DC10]** HP小回復/止血。Crit: 道具消費なし。
- **Lv5 [手術 (Surgery)]**: **[判定: DEX vs DC15]** 重傷治療。Crit: 最大HP上昇。
- **Lv10 [解剖 (Anatomy)]**: **[判定: INT vs 敵のCON]** 即死攻撃(急所突き)。Crit: 素材回収数UP。

### 37. 巫女 (Exorcist) [WIS]
- **解放条件**: 女性限定
- **Lv1 [お祓い (Exorcise)]**: **[判定: WIS vs CHA]** 霊を追い払う。Crit: 霊を成仏(消滅)させる。
- **Lv5 [予言 (Divination)]**: **[判定: WIS vs DC15]** 未来予知(GMヒント)。Crit: 確定未来を知る。
- **Lv10 [神降ろし (Channeling)]**: **[判定: WIS vs DC25]** 神の力を得る。Crit: ステータスALL+10。

### 38. 学者 (Scholar) [INT]
- **解放条件**: 読書50冊以上
- **Lv1 [知識 (Knowledge)]**: **[判定: INT vs DC10]** 魔物/歴史知識。Crit: 攻略法が分かる。
- **Lv5 [戦術指揮 (Tactics)]**: **[判定: INT vs DC15]** 味方のAC/命中UP。Crit: 敵の行動阻害。
- **Lv10 [弱点付与 (Weaken)]**: **[判定: INT vs CON]** 敵に新たな弱点を作る。Crit: 全属性弱点化。

### 39. 心理カウンセラー (Psychologist) [WIS]
- **解放条件**: Sanity 0の仲間を回復
- **Lv1 [傾聴 (Listen)]**: **[判定: WIS vs DC10]** Sanity回復。Crit: LoyaltyもUP。
- **Lv5 [心理操作 (Manipulate)]**: **[判定: WIS vs Insight]** 敵の戦意喪失。Crit: 敵が自殺。
- **Lv10 [洗脳 (Brainwash)]**: **[判定: INT vs WIS]** NPCを恒久的に従わせる。Crit: スキルも使用可能に。

### 40. メイド (Maid) [DEX/CHA]
- **解放条件**: 「メイド服」を装備
- **Lv1 [清掃 (Clean)]**: **[判定: DEX vs DC10]** デバフ解除/探索。Crit: 隠し扉発見。
- **Lv5 [給仕 (Serve)]**: **[判定: DEX vs DC12]** MP回復(お茶)。Crit: Sanity大回復。
- **Lv10 [献身 (Devotion)]**: **[判定: CON vs 攻撃値]** 主人へのダメージ完全肩代わり。Crit: ダメージ0。

---

## カテゴリE: 生活・特殊系 (Special Type)

### 41. 商人 (Merchant) [CHA]
- **解放条件**: 初期開放 (Default)
- **Lv1 [値切り (Haggle)]**: **[判定: CHA vs Insight]** 割引。Crit: おまけ入手。
- **Lv5 [買収 (Bribe)]**: **[判定: CHA vs WIS]** 敵を帰らせる。Crit: 寝返らせる。
- **Lv10 [金の力 (Golden Rule)]**: **[判定: CHA vs DC15]** 金を投げて攻撃力UP。Crit: 即死(高額)。

### 42. 鍛冶屋 (Blacksmith) [STR]
- **解放条件**: 「ハンマー」所持
- **Lv1 [修理 (Repair)]**: **[判定: STR vs DC10]** 街での修理費用無料。Crit: 装備の耐久度全快。
- **Lv5 [破壊工作 (Break)]**: **[判定: STR vs AC]** 敵の装備ACを下げる。Crit: 武器破壊。
- **Lv10 [研磨 (Sharpen)]**: **[判定: STR vs DC15]** 次の攻撃ダメージ+10。Crit: クリティカル確定付与。

### 43. 料理人 (Cook) [DEX]
- **解放条件**: 「調理器具」所持
- **Lv1 [解体 (Butcher)]**: **[判定: DEX vs DC12]** 食材入手。Crit: レア肉入手。
- **Lv5 [戦闘料理 (Battle Food)]**: **[判定: DEX vs DC15]** バフ料理を投げる。Crit: 全能力UP。
- **Lv10 [魔物食 (Eat)]**: **[判定: CON vs CON]** 敵を食べて能力コピー。Crit: 永続習得。

### 44. 農民 (Farmer) [CON]
- **解放条件**: 初期開放 (Default)
- **Lv1 [栽培 (Grow)]**: **[判定: CON vs DC10]** 薬草などを増やす。Crit: 魔法の植物。
- **Lv5 [カマ攻撃 (Scythe)]**: **[判定: STR vs AC]** 植物系に特攻。Crit: 首狩り。
- **Lv10 [開拓 (Terraform)]**: **[判定: STR vs DC20]** 地形を平地(有利)に変える。Crit: 城を建てる。

### 45. アイドル (Idol) [CHA]
- **解放条件**: 「アイドル衣装」装備
- **Lv1 [ウインク (Wink)]**: **[判定: CHA vs WIS]** 単体魅了。Crit: スタン。
- **Lv5 [ライブ (Live)]**: **[判定: CHA vs DC15]** 広範囲バフ。Crit: 敵も踊り出す。
- **Lv10 [ファン召喚 (Fan Call)]**: **[判定: CHA vs DC20]** モブを呼んで攻撃させる。Crit: 親衛隊(精鋭)召喚。

### 46. バニーガール (Dealer) [LUCK]
- **解放条件**: 「バニースーツ」装備
- **Lv1 [接客 (Service)]**: **[判定: CHA vs Insight]** 情報収集。Crit: 秘密暴露。
- **Lv5 [運命操作 (Fate)]**: **[判定: LUCK vs DC15]** 次のダイスロールを有利(Advantage)にする。Crit: 20確定。
- **Lv10 [ルーレット (Gamble)]**: **[判定: LUCK vs DC15]** 所持金を賭けて倍にする。Crit: 100倍。

### 47. 奴隷 (Slave) [CON]
- **解放条件**: 「奴隷の首輪」を装備
- **Lv1 [忍耐 (Endure)]**: **[判定: CON vs ダメージ]** 被ダメ減少。Crit: 回復。
- **Lv5 [死んだふり (Fake Death)]**: **[判定: CHA vs Insight]** タゲを切る。Crit: HP回復しながら待機。
- **Lv10 [肉壁 (Meat Shield)]**: **[判定: CON vs 攻撃値]** 主人の盾になる。Crit: 反撃ダメージ。

### 48. 調教師 (Tamer) [CHA]
- **解放条件**: 動物/魔物を説得して仲間にする
- **Lv1 [動物会話 (Speak)]**: **[判定: CHA vs DC10]** 動物と話す。Crit: 命令を聞かせる。
- **Lv5 [手懐け (Tame)]**: **[判定: CHA vs WIS]** 魔物を仲間にする。Crit: ボスも可。
- **Lv10 [ムチ攻撃 (Whip)]**: **[判定: DEX vs CON]** 仲間の潜在能力開放(バフ)。Crit: 2回行動付与。

### 49. サキュバス (Succubus) [CHA]
- **解放条件**: 種族が「魔族」
- **Lv1 [ドレイン (Drain)]**: **[判定: CHA vs CON]** キスでHP/MP吸収。Crit: Sanityも吸収。
- **Lv5 [夢操作 (Dream)]**: **[判定: INT vs WIS]** 睡眠中の相手を洗脳。Crit: 永続洗脳。
- **Lv10 [ハーレム (Harem)]**: **[判定: CHA vs 全体のWIS]** 敵味方全員を魅了。Crit: 世界征服。

### 50. 勇者 (Hero) [ALL]
- **解放条件**: 世界を救う
- **Lv1 [勇気 (Brave)]**: **[判定: WIS vs DC10]** 恐怖無効/Sanity回復。Crit: 全員回復。
- **Lv5 [全力攻撃 (Smash)]**: **[判定: STR vs AC]** 全ステータスを攻撃に乗せる。Crit: 防御無視。
- **Lv10 [奇跡 (Miracle)]**: **[判定: LUCK vs DC30]** 起死回生の一撃/蘇生。Crit: GM権限レベルの奇跡。

---
**GM Note**: 判定式が不明なスキルは「関連ステータス」で補完してください。
