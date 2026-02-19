---
id: environment_setup
type: docs
tags: [system, environment, rtx5060ti, comfyui, troubleshooting]
title: RTX 5060 Ti × ComfyUI 環境構築・運用引き継ぎ
version: 1.0
updated: 2026-02-19
---

# 17_Environment_Setup: RTX 5060 Ti × ComfyUI 環境構築・運用引き継ぎ

## 1. 環境の概要
*   **ハードウェア**: NVIDIA GeForce RTX 5060 Ti (最新の Blackwell アーキテクチャ)
*   **管理ツール**: Stability Matrix (ポータブル版)
*   **メインエンジン**: ComfyUI (API モード活用)
*   **使用モデル**: `waiIllustriousSDXL_v160.safetensors` (SDXL Based Model)

## 2. トラブルシューティングの記録
### 現象
インストール直後の Forge で `TypeError: 'NoneType' object is not iterable` が発生し、生成不可。

### 原因
RTX 50 シリーズ（Blackwell）が最新世代すぎるため、従来のパッケージ（Forge等）に含まれる **CUDA 12.1** ではグラボを正しく認識・制御できなかった。

### 解決策
1.  当初は手動での Python パッケージ更新を試みたが断念。
2.  最終的に **Stability Matrix** を導入。
3.  最新の **CUDA 12.8 / PyTorch** 環境を自動構築できる ComfyUI へ移行することで、ハードウェアの性能をフルに発揮可能になった。

## 3. 自動生成システム (16_Auto_Illustrator.py)
作成したスクリプトは、ComfyUI を「描画エンジン」として外部から操作する仕組みである。

*   **接続先**: `http://127.0.0.1:8188/prompt`
*   **主要なノード ID**:
    *   **プロンプト入力**: ID 6 (CLIP Text Encode)
    *   **シード値制御**: ID 3 (KSampler)
*   **自動化の流れ**:
    1.  スクリプトが種族・服装・体格・表情をランダムに決定。
    2.  SDXL 向け品質タグ (`score_9` 等) を付与し、1024x1024 サイズで JSON を構築。
    3.  `workflow_api.json` のテンプレートに注入（現在はコード内ハードコード）。
    4.  WebSocket/POST 経由で ComfyUI に送信し、生成プロセスを開始させる。

## 4. 今後の運用アドバイス
*   **モデルの共有**: Stability Matrix の「Checkpoints」フォルダにモデルを置けば、Forge と ComfyUI の両方で容量を食わずに共有可能（シンボリックリンク機能）。
*   **出力先**: 自動生成された画像は、`StabilityMatrix\Data\Packages\ComfyUI\output` に保存される。
*   **拡張性**: ComfyUI 側で「Save (API Format)」を書き出し直せば、ControlNet や LoRA を使ったより複雑な自動生成にも対応可能。
