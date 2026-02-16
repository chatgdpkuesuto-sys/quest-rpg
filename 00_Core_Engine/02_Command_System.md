---
id: command_system
type: system
tags: [core, system, commands, cheat_sheet]
title: Command System & Syntax
version: 2.0
updated: 2026-02-16
---

# コマンドシステム (Command System)

プレイヤーはチャット欄で以下の「スラッシュコマンド」を使用することで、ゲーム的なアクションを実行できます。
GM（AI）はこれらのコマンドに反応して判定や処理を行います。

## 1. ダイスロール (Dice Roll)
- `/roll [式]` または `/r [式]`
    - 例: `/r 1d20` (20面ダイスを1回振る)
    - 例: `/r 1d20+5` (命中判定など)
    - 例: `/r 2d6+3` (ダメージ判定)
    - 例: `/r 1d100` (イベント表の判定)

## 2. アクション・判定 (Action Check)
- `/check [能力値/スキル]` : 能力判定を行う
    - 例: `/check STR` (筋力判定)
    - 例: `/check Insight` (洞察判定)
    - 例: `/check Stealth` (隠密判定)
- `/save [能力値]` : セーヴィングスロー（抵抗）を行う
    - 例: `/save DEX` (罠回避)

## 3. ゲーム進行 (Game Flow)
- `/rest` : 小休憩 (HP小回復 / Spec回復)
- `/sleep` : 大休憩 (HP/MP全回復 / Sanity回復 / オートセーブ)
- `/move [場所/階層]` : 移動する
    - 例: `/move 10F` (10階へ移動)
    - 例: `/move Guild` (ギルドへ移動)
- `/shop` : 現在地のショップリストを表示
- `/status` : 現在のステータス・所持品を表示

## 4. ソーシャル (Social)
- `/talk [NPC名]` : 会話する
- `/gift [アイテム名] to [NPC名]` : プレゼントを渡す (Loyalty UP)
- `/heartbeat [NPC名]` : **心音チェック**を行う (要スキル/アイテム)
- `/party` : パーティメンバーの状態を確認する

## 5. システム・デバッグ (System)
- `/save` : 現在の状態をセーブデータ(`90_Save_System`)に記録
- `/load` : 最新のセーブデータを読み込む
- `/help` : コマンド一覧を表示
- `/img [プロンプト]` : 場面やキャラの画像を生成する (Image Gen)
- `/debug [on/off]` : GMの思考プロセス(DCなどの裏数値)を表示する

---
**GM Note**: プレイヤーがコマンドを忘れた場合も、自然言語（「剣で攻撃！」「逃げる！」）で入力すれば、GMが適切な判定(`/check STR`など)に脳内変換して処理します。
