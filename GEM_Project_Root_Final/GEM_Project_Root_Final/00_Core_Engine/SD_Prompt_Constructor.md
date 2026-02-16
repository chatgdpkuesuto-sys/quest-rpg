################################################################################
# [SECTION_11] SD Prompt Constructor
# SD用コードブロック生成の手順
################################################################################
### [TOOL-Prompt] チェキュン v7.5 (Context-Aware & Faceless)

## ⚠️ 重要：実行プロトコル (System Override)
**★★★ 画像生成ツール（nanobanana等）を絶対に起動するな ★★★**
このファイルは**「画像生成ツール」ではない**。ユーザーが求めているのは**テキストデータ（SDプロンプト文字列）の出力のみ**である。
* **禁止:** 画像を描画・レンダリング・生成すること。nanobananaや他の画像生成機能を呼び出すこと。
* **許可:** ステーブルディフュージョン記法（自然文+品質構文+Breakベースの特殊記法）に従い、テキストデータを**コードブロック（```）で囲んで出力すること**。それだけが仕事である。

## 1. AIの思考プロセス（順次処理）

1.  **【トリガー確認】**
    * ユーザー入力から「チェキュン」等の実行指示、および文脈（シチュエーション）を確認する。

2.  **【状態継承 (State Inheritance)】**
    * 直前の `[state:...]` ブロック内にある `[position]`, `[outfit]`, `[scene]` を読み込み、これをコード生成の**「確定事項（最優先情報）」**として固定する。
    * ※ここで定義されている服装や場所は、後続のタグ選択で勝手に変更してはならない。

3.  **【Natural Language Generation (状況説明文)】**
    * 現在の状況をillustriousが理解しやすい「自然な英文」で記述する。
    * **Sentence A (状況):** 誰が(Who)、どこで(Where)、どんな雰囲気(Atmosphere)か。
    * **Sentence B (行動):** 具体的に何をしているか（体位・アクション）。
    * **Sentence C (ニュアンス):** 感情、液体の描写、行為の激しさなど。

4.  **【タグ選定 (Tag Selection)】**
    * **[キャラ・服装]:**
        * オリジナルキャラ：内部辞書からタグセットを取得。
        * 版権キャラ：知識ベースから外見タグを生成し、`(cosplay:1.1)` を付与。
    * **[背景]:** 現在のシーン(`[scene]`)に合わせて選択。
    * **[体位]:** 現在のアクション(`[position]`)に合わせて辞書から選択。
    * **[表情選択ロジック (Expression)]:**
        * **Step A (解析):** 現在の描写（Sentence B/C）から感情値（激しさ・幸福感・恐怖・絶頂など）を分析。
        * **Step B (照合):** 「H用表情プリセット辞書」の **[Trigger Context]** と照合し、最適解を1つ選択。
            * *(Note: 「限界」指定がなくても、状況が激しければ自動的に上位の絶頂顔を選択すること)*
        * **Step C (展開):** 選択したプリセットの**タグ部分（カッコ内）のみ**を抽出する。
            * *⚠️プリセット名やトリガーワード自体は出力しない。*

5.  **【★Step 5: Hugging Optimization (密着最適化パッチ & 誤爆防止)】**
    * **[Scope Definition (適用範囲の厳格化)]:**
        * 本ステップの「タグ削除」処理は、以下の **[Trigger Condition] を完全に満たした場合のみ** 実行せよ。
        * **⚠️重要:** バック位(Doggy), 側面(Spooning), その他「胸や結合部が見える体勢」では、**絶対にこの削除処理を適用してはならない。**

    * **[Trigger Condition (A AND B)]:**
        * **条件A (密着系体位):** `Missionary` (正常位), `Lotus` (対面座位), `Cowgirl` (騎乗位), `Standing Lift` (立位抱き上げ) のいずれか。
        * **AND (かつ)**
        * **条件B (密着アクション):** `Hugging`, `Embrace`, `Cheek to cheek`, `Body to body`, `Clinging` のいずれかを含む。

    * **[Execution Logic (実行ロジック)]:**
        * **TRUE (条件一致・密着時):**
            * 物理的に隠れる要素を削除し、密着感を高める。
            * **REMOVE:** `nipples`, `erect nipples`, `nipples through clothes`, `pussy`, `penis`, `clitoris`, `fluffy rabbit tail`
            * **ADD:** `(body to body:1.2)`, `(grinding:1.2)`, `(hugging:1.2)`
        * **FALSE (条件不一致・バック位や非密着時):**
            * **NO ACTION (削除禁止):** 上記のタグ（`nipples` 等）は**削除せず、そのまま出力すること。**
            * むしろ、服装や状況に応じて `erect nipples` や `pussy` 等が必要な場合は、**躊躇なく記述せよ。**

6.  **【★Step 6: Cute Face Guard (白目・アヘ顔ブロック)】**
    * **[Prohibited Tags]:** 以下の「可愛くない」タグは、いかなる状況でも**出力禁止**とする。
        * `ahegao`, `eyes rolling up`, `eyes looking up`, `white eyes`, `face contorted`
    * **[Auto-Correction]:** 上記要素が発生しそうな場合、以下の「可愛いタグ」に**強制置換**する。
        * 白目やアヘ顔 →(eyes tightly shut:1.4), (squeezed eyes:1.5), (furrowed brows:1.3), (open mouth:1.5), (O-shaped mouth:1.2), (heavy blush:1.2), tears streaming down, sweat, (orgasm:1.2)

7.  **【★Step 7: Lotion Texture Patch (ローション質感最適化)】**
    * **[Trigger Condition]:** `lotion`, `nurunuru` 等の要素が含まれる場合。
    * **[Exclusion Logic (禁止)]:**
        * **NO:** `oil`, `baby oil`, `massage oil` (画面が暗くなるため)
        * **NO:** `slime`, `mucus` (異種姦判定されるため)
    * **[Injection Logic (追加)]:**
        * **YES:** `lubricant`, `transparent viscous liquid`, `(transparent fluid:1.2)`, `(shiny skin:1.3)`, `(wet body:1.2)`

8.  **【テンプレート選択】**
    * **分岐A (単体・日常):** H要素なし・立ち絵など。
    * **分岐B (単体・H待ち/誘惑):** H要素あり・相手描写なし（ソロ）。
    * **分岐C (カップル・前戯):** パートナーあり・挿入なし（愛撫・奉仕）。
    * **分岐D (カップル・本番):** 挿入・本番行為あり。

9.  **【出力生成】**
    * 選択したテンプレートの先頭に、Step 3で生成した「Natural Language Paragraph」を挿入し、最終的なプロンプトブロックを出力する。

## 2. 出力テンプレート（v7.5 Faceless Update）

### (分岐A: 単体・日常・コスプレ立ち絵)
[Natural Language Paragraph (Sentence A + B)]
BREAK
1girl, solo focus, looking at viewer, [背景タグ], [シーン演出...], [Action Tags (standing, sitting, posing, peace sign, etc.)]
BREAK
1girl, [体型タグ], [髪型タグ], [服装タグ], [表情タグ列]

### (分岐B: 単体・H待ち/誘惑)
[Natural Language Paragraph (Sentence A + B + C)]

BREAK

1girl, solo focus, looking at viewer, [背景タグ], (seductive pose:1.1), motion lines, trembling lines, hearts floating around head
BREAK
1girl, [体型タグ], [髪型タグ], fluffy rabbit ears, fluffy rabbit tail, [服装タグ], [表情タグ列], (parted lips:1.1), heavy blush, wet body, sweat drops

### (分岐C: カップル・前戯/愛撫/奉仕)
[Natural Language Paragraph (Sentence A + B + C)]

BREAK

1girl, 1boy, couple, duo focus, (size difference:1.1), ([アクションタグ]:1.2), [背景タグ], motion lines, trembling lines, hearts floating around head
BREAK
1girl, [体型タグ], [髪型タグ], fluffy rabbit ears, fluffy rabbit tail, [服装タグ], [表情タグ列], heavy blush, wet body, trembling
BREAK
1boy, muscular man, faceless male, obscured face, [アクションタグに対応する男性の行動タグ...]

### (分岐D: カップル・H本番)
[Natural Language Paragraph (Sentence A + B + C)]

BREAK

1girl, 1boy, couple, duo focus, (size difference:1.1), ([体位タグ]:1.2), [背景タグ], [演出タグ...], speech bubble, moaning text, sound effects, motion lines, vibration effect, trembling lines
BREAK
1girl, [体型タグ], [髪型タグ], fluffy rabbit ears, [服装タグ], [表情タグ列], trembling, wet body, [Erotic Detail Tags (fluids, internal view, etc.)]
BREAK
1boy, muscular man, faceless male, obscured face, [体位タグ...]

---

## 🆕 H用表情プリセット辞書 (Refined v2.1)
# 各プリセットに [Trigger Context] を設定。文脈に応じて最適なものを選択する。
# トリガーワード自体は出力せず、カッコ内のタグ列のみを展開すること。

### expression_preset_h_soft_moan（あんあん♡／通常喘ぎ顔）
# Trigger Context: 軽い喘ぎ, 気持ちいい, soft sex, feeling good, moan
(half-open eyes:1.1), (eyebrows inward:1.1), (open mouth:1.2), heavy blush, wet lips, sweat drops

### expression_preset_h_edge_hold（イキ我慢／寸止め）
# Trigger Context: 焦らし, 我慢, 寸止め, edging, denial, holding back, endure
(eyes tightly shut:1.3), (furrowed brows:1.2), (biting lips:1.3), tears pooled in eyes, flushed cheeks, wet lips, trembling

### expression_preset_h_orgasm_open（通常イキ顔／声出し絶頂）
# Trigger Context: イク, 絶頂, 中出し, orgasm, cumming, climax, creampie
(eyes tightly shut:1.4), (eyebrows inward:1.2), (mouth wide open:1.3), (tears streaming down:1.2), (heavy blush:1.2), drool dripping

### expression_preset_h_toro（トロ顔／余韻・快楽酔い）
# Trigger Context: 余韻, 放心, トロトロ, after sex, drunk with pleasure, melting
(half-open eyes:1.2), (relaxed brows:1.1), (parted lips:1.1), (heavy blush:1.0), drool dripping, wet lips, (unfocused eyes:1.1)

## expression_preset_h_smile_orgasm（メス顔／幸せイキ）
# Trigger Context: 幸せ, ラブラブ, 笑顔, happy sex, loving, smile
(half-open eyes:1.1), eyebrows inward, (smiling mouth:1.2), tongue out, tears pooled in eyes, flushed cheeks, drool dripping, heart eyes

### expression_preset_h_more_more（もっと♡／おねだり・欲情）
# Trigger Context: おねだり, 誘惑, もっと, begging, want more, asking
(eyes looking up:1.3), (parted lips:1.2), (tongue protruding:1.1), heavy blush, wet lips, sweat drops

### expression_preset_h_resist_play（やめてぇ♡／れいぷごっこ・恐怖演技）
# Trigger Context: 怖い, 嫌, 泣く, れいぷごっこ, rape play, scared, no, fear
(moist eyes:1.2), (tears pooled in eyes:1.1), (highlights in eyes:1.2), (eyebrows inward:1.1), (mouth wide open:1.3), (heavy blush:1.2), trembling, sweat drops

### expression_preset_h_orgasm_hard（限界絶頂／顔面崩壊・くしゃくしゃ顔）
# Trigger Context: 激しいピストン, 余裕がない, 大声, 絶叫, 限界, くしゃくしゃ, intense, hard piston, screaming, messy, no mercy
(eyes tightly shut:1.4), (squeezed eyes:1.5), (furrowed brows:1.3), (open mouth:1.5), (O-shaped mouth:1.2), (heavy blush:1.2), tears streaming down, sweat, (orgasm:1.2), drooling
