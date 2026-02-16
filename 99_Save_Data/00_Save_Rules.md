---
id: save_rules
type: system
tags: [system, save, guidelines, persistence]
title: Save Data Management Rules
version: 1.0
updated: 2026-02-16
---

# セーブデータ運用ルール (Persistence Rules)

**「チャットログは流れるが、記録は石に刻め」**

AIとのチャットプレイにおいて、アイテムやステータスが「忘却」されるのを防ぐための鉄則です。

## 1. 基本・原則
1.  **チャット欄 = RAM (一時メモリ)**
    *   会話の流れ、一時的な感情、その場の演出。
    *   ログが長くなるとAIは忘れます。
2.  **このフォルダ = HDD (永続ストレージ)**
    *   **ここ書かれていることだけが「真実」です。**
    *   どんなに感動的なイベントで伝説の剣を手に入れても、`02_Inventory_Storage.md` に追記しなければ、それは「夢だった」ことになります。

## 2. セーブのタイミング (When to Save)
以下のタイミングで、必ずファイルを更新してください。

*   **セッション終了時 (End of Session)**:
    *   XP、Gold、アイテムの増減を確定させる。
*   **重要なイベント後 (Major Event)**:
    *   ボス撃破、ヒロインの好感度変化、ジョブチェンジ時。
*   **倉庫へ送る時 (To Storage)**:
    *   手持ちアイテムを倉庫へ移す処理は、即座にファイルへ反映させること。

## 3. ファイル構成
*   **[01_Party_Status.md](01_Party_Status.md)**: キャラクターの強さ、HP。
*   **[02_Inventory_Storage.md](02_Inventory_Storage.md)**: アイテムと倉庫。
*   **[03_Quest_Log.md](03_Quest_Log.md)**: 物語の進行状況。
*   **[04_Social_Relationships.md](04_Social_Relationships.md)**: **【重要】** 全キャラクターとの好感度・記憶・関係性。

## 4. 復帰方法 (Load Game)
久しぶりにプレイを再開する際は、**「セーブデータフォルダをすべて読み込む」**ことから始めてください。
そうすれば、AIは即座に状況を思い出し、前回の続きからスムーズに再開できます。
