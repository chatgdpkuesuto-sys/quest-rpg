---
id: image_prompt_generator
type: tool
tags: [core, utility, image, prompt]
title: Local Image Prompt Generator
version: 1.0
updated: 2026-02-19
---

# 15_Image_Prompt_Generator: 画像生成プロンプト構築システム

このファイルは、`12_NPC_Generator.md` の結果を、ローカル環境（Stable Diffusionなど）で使用可能な **「呪文（Prompt Tags）」** に変換するための辞書である。
ユーザーはこのファイルを参考に、生成されたNPCの特徴をタグとしてコピー＆ペーストして使用する。

---

## 1. Description Tags (外見タグ変換表)

### 【Race (種族)】
| ID | Race | Prompt Tags (Danbooru Style) |
|:---:|:---|:---|
| 1-10 | Human | `1girl, human` |
| 11-15 | Elf | `1girl, elf, pointed ears, nature background` |
| 16-18 | Dwarf | `1girl, dwarf, short stature, muscular` |
| 22-30 | Beast | `1girl, animal ears, tail, kemonomimi, (cat ears / dog ears / fox ears)` |
| 31 | Slime | `1girl, slime girl, transparent skin, liquid body` |
| 38 | Succubus | `1girl, succubus, wings, horns, heart-shaped tail` |
| 40 | Ogre | `1girl, oni, horns, red skin (optional), tall, muscular female` |
| 47 | Dragon | `1girl, dragon girl, dragon horns, dragon wings, tail` |
| 50 | God | `1girl, goddess, halo, divine aura, glowing eyes` |

### 【Clothing (服装)】
| ID | Clothing | Prompt Tags |
|:---:|:---|:---|
| 1-5 | Adventurer | `fantasy clothes, leather armor, cape` |
| 13-15 | Bikini Armor | `bikini armor, armored bikini, plate metal, revealing clothes` |
| 16-21 | Maid | `maid, maid headdress, frills, apron` |
| 22-26 | Religious | `nun, nun habit, veil, cross` |
| 29-30 | Swimsuit | `school swimsuit` or `bikini, cleavage` |
| 36 | Bondage | `bondage, rope, leather straps, gag` |
| 50 | Naked | `naked, nude, nipples, pussy` |

### 【Scale (体格・巨大化)】
※「Giantess」要素を強調するためのタグセット。
| Class | Scale | Prompt Tags |
|:---:|:---|:---|
| 1-2 | Micro/Mini | `minigirl, fairy size, holding giant object, giant surroundings` |
| 3 | Standard | `normal size` |
| 4-5 | Tall/Titan | `giantess, tall female, height difference, giant, low angle view, looking down` |
| 6 | Colossus | `giantess, hyper giantess, size difference, mountain background, crushing` |

### 【Expression (表情・親密度)】
| State | Prompt Tags |
|:---:|:---|
| Arrogant | `haughty, looking down, smirk, confident` |
| Shy / Gap | `blush, embarrassed, shy, covering face` |
| Pleasure | `ahegao, rolling eyes, drooling, open mouth, tongue out` |
| Broken | `empty eyes, mind break, drool, messy hair` |

---

## 2. Prompt Template (構成テンプレート)

以下のフォーマットに従ってタグを連結する。

```text
(Quality Tags),
(Race Tags), (Clothing Tags), (Scale Tags),
(Body Feature Tags), (Expression Tags),
(Background Tags)
```

---

## 3. Example Generation (生成例)

**Target**: **Ouka (Ogre / Bikini Armor / Titan / Ahegao)**

```text
masterpiece, best quality, highres, 8k,
1girl, oni, horns, muscular female, long hair,
bikini armor, armored bikini, revealing clothes, metal plate,
giantess, tall female, size difference, low angle view, looking down,
huge breasts, thick thighs, navel,
ahegao, rolling eyes, drooling, tongue out, blush, sweaty skin,
forest background, trees, sunlight
```

**[Negative Prompt Recommendation]**
`low quality, worst quality, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, cropped`
