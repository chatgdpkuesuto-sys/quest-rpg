# 01_World_Module

世界観の“辞書”となるモジュールです。
場所・勢力・アイテム・クエストなどの**確定情報**を格納しています。

## 📂 ディレクトリ構成

### **[`Quests/`](Quests/)**
標準クエストデータ (Rank E〜S) が格納されています。
*   索引: **[`03_Standard_Quests.md`](03_Standard_Quests.md)**

### **[`Locations/`](Locations/)**
街、ダンジョン、各階層の詳細データ。

### **[`Factions/`](Factions/)**
ギルド、騎士団、宗教団体などの勢力データ。

### **[`Items/`](Items/)**
特殊アイテムやアーティファクトのデータ（標準装備は Core Engine で定義）。

### **[`Allies/`](Allies/)** & **[`Enemies/`](Enemies/)**
（※ 現在はキャラクターデータは `02_Character_Data` に移行中ですが、世界のNPCやモンスターデータはここに残ります）

---

## 📜 主要ファイル
*   **[`00_World_Overview.md`](00_World_Overview.md)**: 世界観、歴史、地理の概要。
*   **[`02_Dungeon_Rules.md`](02_Dungeon_Rules.md)**: ダンジョンの生成ルールとギミック。
*   **[`04_Event_Prologue.md`](04_Event_Prologue.md)**: ゲーム開始時のプロローグイベント（パートナー選択）。
