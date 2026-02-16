---
id: town_facilities
type: data
tags: [world, town, npc, shop, social]
title: Town Facilities \u0026 NPCs
version: 2.0
updated: 2026-02-16
---

# 街の施設とNPC (Town Facilities)

街は単なる補給地点ではない。
店主たちにも「生活」があり、「感情」があり、そして「秘密」がある。
**心音チェック**で彼女たちの本音を探り、関係を深めることができる。

## 1. 冒険者ギルド (Adventurer's Guild)
**NPC: 受付嬢 エミリ (Human)**
- **Visual**: 眼鏡、制服、常に書類仕事に追われている。
- **Service**: クエスト受注、報酬受取。
- **Deep Social**:
    - **Default**: 事務的 (Business)
    - **Loyalty**: 50 (仕事) | **Sanity**: 30 (過労)
    - **Hidden Trait**: [ストレス爆発] 繁忙期に話しかけるとキレてクエストを適当に発注する。
    - **Recovery**: 高級スイーツの差し入れ。「肩、揉みましょうか？」
    - **Fallen Bonus**: **裏クエスト** (報酬が良い特別な依頼) を回してくれる。

## 2. 鍛冶屋「鉄の薔薇」 (Blacksmith)
**NPC: 親方 ドルガー (Dwarf Girl)**
- **Visual**: 煤けた肌、タンクトップ、筋肉質。
- **Service**: 武器の購入、強化、修理。
- **Deep Social**:
    - **Default**: 職人 (Artisan)
    - **Loyalty**: 70 (腕前への信頼) | **Sanity**: 80
    - **Hidden Trait**: [武器愛] 伝説の武器を見せると興奮して鼻血を出す。
    - **Heartbeat Check**: 武器を研いでいる時の鼓動が早い＝良い仕事をしている。
    - **Fallen Bonus**: **無料修理** / **専用装備作成**。

## 3. 魔女の薬屋 (Alchemy Shop)
**NPC: 魔女 ルル (Witch)**
- **Visual**: 眠そうな目のダウナー系少女。常に大釜を混ぜている。
- **Service**: ポーション、爆弾、怪しい薬の購入。
- **Deep Social**:
    - **Default**: 実験台 (Test Subject)
    - **Loyalty**: 40 | **Sanity**: 20 (薬の影響)
    - **Hidden Trait**: [マッド] 「新作の試供品」と称して毒薬を渡してくる(50%の確率でバフ)。
    - **Recovery**: 一緒に怪しい鍋をつつく。
    - **Fallen Bonus**: **惚れ薬**、**性転換薬**などの違法アイテム販売。

## 4. 教会 (Church)
**NPC: シスター マリア (Nun)**
- **Visual**: おっとりした巨乳シスター。
- **Service**: 蘇生、解毒、呪い解除、Sanity回復の祈り。
- **Deep Social**:
    - **Default**: 迷える子羊 (Believer)
    - **Loyalty**: 90 | **Sanity**: 90 〜 0 (二重人格?)
    - **Hidden Trait**: [堕落願望] 実は神への信仰が揺らいでおり、背徳的な行為に興味がある。
    - **Heartbeat Check**: 告解室で二人きりになると脈が異常に早い。
    - **Fallen Bonus**: **無料蘇生** / **闇の祝福**(Sanity減少無効)。

## 5. 酒場「踊る猫亭」 (Tavern / Inn)
**NPC: 看板娘 ミーヤ (Catfolk)**
- **Visual**: 猫耳メイド。元気いっぱい。
- **Service**: 食事(Sanity回復)、宿泊(HP/MP回復)、噂話。
- **Deep Social**:
    - **Default**: 客 (Customer)
    - **Loyalty**: 60 (チップ次第) | **Sanity**: 70
    - **Hidden Trait**: [情報通] 街の裏情報（誰が裏切り者か）を知っている。
    - **Recovery**: マタタビをあげる。撫でる。
    - **Fallen Bonus**: **「特別サービス」** (宿泊時にSanity特大回復)。

## 6. アラクネの仕立て屋 (Tailor)
**NPC: アラクネ夫人 (Arachne)**
- **Visual**: 上品な貴婦人。下半身は蜘蛛。
- **Service**: 防具の購入、衣装チェンジ(Cosplay)。
- **Deep Social**:
    - **Default**: モデル (Model)
    - **Loyalty**: 50 | **Sanity**: 50
    - **Hidden Trait**: [拘束癖] 採寸と称して糸でグルグル巻きにしてくる。
    - **Fallen Bonus**: **オーダーメイド** (好きな耐性をつけた服を作れる)。

## 7. 奴隷市場 (Slave Market) - ※夜のみ営業
**NPC: 商人 ゲイツ (Fat Merchant)**
- **Visual**: 脂ぎった小太りの男…ではなく、その背後に控える**闇エルフの護衛(Dark Elf)**。
- **Service**: 仲間(Slave)の購入、売却。
- **Deep Social**:
    - **Target**: 護衛のシルヴィ
    - **Default**: 敵意 (Hostile)
    - **Loyalty**: 0 | **Sanity**: 10 (絶望)
    - **Hidden Trait**: [救済待ち] 商人を殺して解放してくれるのを待っている。
    - **Action**: 商人を殺害すると、市場を乗っ取ることができる。

## 8. 謎の骨董品店 (Mysterious Shop)
**NPC: 骨董屋 (Lich)**
- **Visual**: フードを被った骸骨。
- **Service**: レアアイテム、鑑定、呪いのアイテム。
- **Deep Social**:
    - **Default**: 観察者 (Observer)
    - **Loyalty**: -- | **Sanity**: --
    - **Hidden Trait**: [ダンジョンマスター] 実はこの世界の管理者の一人。
    - **Heartbeat Check**: 鼓動がない。
    - **Fallen Bonus**: **神の遺産** (バランスブレイカー・アイテム) の販売。
