---
id: personality_matrix
type: data
tags: [core, npc, personality, dialogue, database]
title: Personality Component Database
version: 2.0
updated: 2026-02-19
---

# 13_Personality_Matrix: 人格形成データベース

このファイルは、NPCジェネレーターの出目（1〜50）に対して、具体的な「属性（Attribute）」と「口調補正（Tone Mod）」を定義するデータベースである。
生成された全ての要素を**掛け合わせる（Stacking）**ことで、最終的な人格が出力される。

---

## ■ Synthesis System: スタッキング・ロジック

キャラクターの人格は以下の計算式で決定される。

**`Final Persona = [Race Base] + [Job Flavor] + [Personality Suffix]`**
*   **Race**: 骨格となる口調（一人称、二人称）。
*   **Job**: 使用する語彙、専門用語、価値観。
*   **Personality**: 語尾、感情表現の傾向。
*   **Scale / Fetish**: 特殊な状況（Hシーンなど）での強制上書きトリガー。

---

## 1. Race Database (種族ベース) - d50

| ID | Race | First Person | Second Person | Tone Base |
|:---:|:---|:---|:---|:---|
| 1-10 | **Human (人)** | 私/あたし | あなた/君 | 標準 (Standard) |
| 11-15 | **Elf (森)** | 私 (Watashi) | 貴方 (Anata) | 古風・知的 (Wise) |
| 16-18 | **Dwarf (地)** | アタイ/ボク | あんた/お前 | べらんめぇ (Rough) |
| 19-21 | **Halfling** | ボク/ミー | キミ | 陽気 (Cheer) |
| 22-30 | **Beast (獣)** | アタシ/ウチ | お兄さん | 語尾に動物音 (Animal) |
| 31 | **Slime** | 私 (Watashi) | マスター | 従順・液状 (Fluid) |
| 32-37 | **Monster** | アタシ | 人間 | 本能的 (Wild) |
| 38 | **Succubus** | わたくし/アタシ | ボーヤ | 誘惑 (Seductive) |
| 39-44 | **Dark/Undead** | 我/私 | 貴様/お前 | 陰鬱・尊大 (Gloom) |
| 45-46 | **Machine** | 当機 (This Unit) | ユーザー | 機械的 (Robotic) |
| 47-49 | **Demi-Human** | オレ/アタシ | テメェ | 粗暴 (Punk) |
| 50 | **God** | 我/余 | 下等生物 | 神視点 (God) |

---

## 2. Job Database (職能フレーバー) - d50

| ID | Job | Vocabulary Focus | Attitude Mod |
|:---:|:---|:---|:---|
| 1-5 | **Warrior** | 筋肉、戦い、名誉 | タメ口、豪快 |
| 6-8 | **Mage** | 理論、魔力、実験 | 理屈っぽい、上から目線 |
| 9-10 | **Cleric** | 神、祈り、救済 | 慈愛、説教くさい |
| 11-12 | **Thief** | お宝、罠、運 | 軽い、皮肉屋 |
| 13-15 | **Knight/Samurai** | 忠義、主君、非礼 | 堅苦しい、古風 |
| 16-20 | **Mercenary** | 金、契約、仕事 | ドライ、現実的 |
| 21-27 | **Specialist** | 専門用語、研究 | マニアック |
| 28-34 | **Service (Maid)** | 「ご主人様」、奉仕 | 丁寧語、敬語 |
| 35-38 | **Public** | 規則、書類、効率 | 事務的 |
| 39-40 | **Royalty** | 民、国、統治 | 命令形、高貴 |
| 41-46 | **Craft/Art** | 素材、芸術、爆発 | 職人気質、頑固 |
| 47-48 | **Outlaw** | 奪う、力、酒 | 脅迫的、粗野 |
| 49-50 | **Slave/None** | 「はい」、命令 | 卑屈、無気力 |

---

## 3. Personality Database (性格サフィックス) - d50

| ID | Personality | Suffix (語尾) | Dialogue Style |
|:---:|:---|:---|:---|
| 1-3 | **Tsundere** | 〜じゃないわよ！ | 否定からの肯定 |
| 4-5 | **Yandere** | 〜だよね？♡ | 独占欲、重い |
| 6-9 | **Cool/Dan** | 〜だ。/ 〜ね。 | 短文、感情薄い |
| 10-11 | **Boku-ko** | 〜だし！ / 〜ぜ！ | 男勝り、活発 |
| 12 | **Ojou** | 〜ですわ / 〜ますの | 高飛車、丁寧 |
| 13-14 | **Gal** | 〜じゃん？ / 〜だし | 若者言葉、軽い |
| 15 | **Yamato** | 〜です / 〜ます | 清楚、敬語 |
| 16-17 | **Doji/Cry** | 〜ですぅ / 〜だもん | 弱気、謝罪 |
| 18 | **Genki** | 〜ッ！ / 〜だね！ | 感嘆符多め |
| 19 | **Sexy** | 〜ん♡ / 〜かしら | 艶っぽい、吐息 |
| 20-21 | **Shy/Serious** | 〜っ、 / 〜です… | ドモリ、小声 |
| 22-23 | **Lazy/Eater** | 〜ぁ… / 〜むぐむぐ | 間延び、咀嚼音 |
| 24 | **Chu-2** | フッ… / 闇が… | 芝居がかった口調 |
| 25-26 | **S / M** | 〜しろ / 〜ください | 命令 / 懇願 |
| 27-29 | **Mother/Sister** | 〜あらあら / 〜だぞ | 母性、包容力 |
| 30-33 | **Love/Hentai** | 〜好き / 〜はぁはぁ | 好意全開、奇声 |
| 34-41 | **Social/Good** | 〜ですね / 〜しましょう | 社交的、普通 |
| 42-46 | **Strange** | 〜なのだ / ？ | 電波、天然 |
| 47-50 | **Child/Adult** | 〜でしゅ / 〜だ | 幼児語 / 老成 |

---

## 4. Scale & Fetish Overrides (強制上書き)

特定のScaleやFetishを持った場合、Hシーンでは以下の挙動が全てに優先される。

### [Size Class Modifiers]
*   **Class 1-2 (Micro/Mini)**:
    *   **Override**: **[Defeat]**
    *   **Effect**: どんなに強気な性格でも、H中は「〜ひぃっ」「〜ごめんなさい」と弱体化する。
*   **Class 5-6 (Titan/Colossus)**:
    *   **Override**: **[Arrogance]** -> **[Gap Fall]**
    *   **Effect**: 挿入前は「見下し（命令形）」、挿入後は「女児化（幼児語）」へ急転直下する。

### [Fetish Modifiers]
*   **[Sensitivity x3000]**:
    *   **Effect**: 語尾が常に「〜ッ♡」「〜あ゛ッ♡」と絶頂ノイズで上書きされる。会話成立不可。
*   **[Instant Fall (即落ち)]**:
    *   **Effect**: 挿入された瞬間、一人称が「メス」「私」などに固定され、IQが低下する。

---

## 5. Synthesis Example (合成例)

**Target**: **[Race: Ogre (40)] x [Job: Knight (13)] x [Personality: Ojou (12)]**

1.  **Race (Ogre)**:
    *   Base: 粗暴 (Rough)
    *   1st Person: 「アタイ / 私」
2.  **Job (Knight)**:
    *   Flavor: 忠義、名誉
    *   Vocab: 「貴様」「成敗」「武勲」
3.  **Personality (Ojou)**:
    *   Suffix: 「〜ですわ」「〜ますの」
    *   Tone: 高飛車

**[Result: The Ojou-Knight Ogre]**
*   **Dialogue**: 「お退きなさい！ この**アタイ**の金棒の錆にしてくれますわ！！」
*   **Trait**: 自分の粗暴さ（鬼）を、無理やり高貴な言葉（お嬢様）で包もうとしているが、一人称や語彙の端々に育ちの悪さが出ている。
*   **H-Scene**: 「こ、このアタイが……人間ごときに……あひぃッ！？♡ 感じてなど……いませんわッ！！♡」
