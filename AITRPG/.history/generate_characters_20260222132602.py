"""
generate_characters.py — キャラ立ち絵一括生成スクリプト
chara_workflow_api.json を使って、DPCombinatorialGenerator で
8ポーズの透過背景キャラ立ち絵を一発生成する。
"""

import json
import time
import requests
import uuid
from pathlib import Path


def load_config():
    with open(Path(__file__).parent / "config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("=" * 50)
    print("  キャラ立ち絵一括生成")
    print("  8ポーズ × 背景除去(RMBG)")
    print("=" * 50)

    config = load_config()
    base_url = config["comfyui"]["url"]
    client_id = str(uuid.uuid4())

    # ワークフロー読み込み
    wf_path = Path(__file__).parent / "chara_workflow_api.json"
    with open(wf_path, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    # 出力先
    output_dir = Path(__file__).parent / "assets" / "characters"
    output_dir.mkdir(parents=True, exist_ok=True)

    # DPCombinatorialGenerator が8つのバリエーションを生成
    # ComfyUIが自動で8回実行する
    payload = {
        "prompt": workflow,
        "client_id": client_id,
    }

    print("\n[ComfyUI] キャラ立ち絵生成リクエスト送信中...")
    try:
        resp = requests.post(f"{base_url}/prompt", json=payload, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        prompt_id = result.get("prompt_id")
        print(f"[ComfyUI] Prompt ID: {prompt_id}")
    except Exception as e:
        print(f"[ERROR] 送信失敗: {e}")
        return

    # ポーリングで完了を待つ
    print("[ComfyUI] 生成待機中... (8ポーズ分)")
    start_time = time.time()
    timeout = 600  # 8枚分なので余裕を持って10分

    collected = []

    while time.time() - start_time < timeout:
        try:
            hist_resp = requests.get(f"{base_url}/history/{prompt_id}", timeout=5)
            if hist_resp.status_code == 200:
                history = hist_resp.json()
                if prompt_id in history:
                    entry = history[prompt_id]
                    status = entry.get("status", {})
                    status_str = status.get("status_str", "")

                    if status_str == "error":
                        print(f"[ERROR] 生成エラー: {status.get('messages', [])}")
                        return

                    outputs = entry.get("outputs", {})
                    for node_id, node_out in outputs.items():
                        if "images" in node_out:
                            for img in node_out["images"]:
                                collected.append(img)

                    if collected:
                        elapsed = time.time() - start_time
                        print(f"[ComfyUI] 生成完了！({elapsed:.1f}秒) - {len(collected)}枚")
                        break
        except Exception:
            pass
        time.sleep(2)
    else:
        print("[TIMEOUT] 生成がタイムアウトしました")
        return

    # ポーズ名リスト
    pose_names = [
        "smile",        # gentle smile
        "serious",      # serious
        "surprised",    # surprised
        "sad",          # sad, looking down
        "blush",        # blush
        "casting",      # action pose, casting magic
        "back",         # from behind, back
        "look_back",    # from behind, looking back
    ]

    # 画像ダウンロード＆ポーズ別に保存
    print(f"\n[DL] {len(collected)}枚をダウンロード中...")
    from urllib.parse import urlencode

    for i, img_info in enumerate(collected):
        filename = img_info.get("filename", f"output_{i}.png")
        subfolder = img_info.get("subfolder", "")
        img_type = img_info.get("type", "output")

        params = urlencode({"filename": filename, "subfolder": subfolder, "type": img_type})

        try:
            dl_resp = requests.get(f"{base_url}/view?{params}", timeout=10)
            dl_resp.raise_for_status()

            # ポーズ名でファイルを保存
            pose_name = pose_names[i] if i < len(pose_names) else f"pose_{i}"
            save_path = output_dir / f"elf_{pose_name}.png"

            with open(save_path, "wb") as f:
                f.write(dl_resp.content)

            print(f"  ✅ {save_path.name}")

        except Exception as e:
            print(f"  ❌ ダウンロード失敗: {e}")

    print(f"\n{'=' * 50}")
    print(f"  完了！ assets/characters/ に保存済み")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
