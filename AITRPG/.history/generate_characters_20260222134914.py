"""
generate_characters.py — キャラ立ち絵一括生成スクリプト
ポーズ別に個別リクエストを送って確実に8枚生成する。
グリーンバック出力 → Pythonで緑色背景を透過に変換。
"""

import json
import time
import requests
import uuid
from pathlib import Path
from urllib.parse import urlencode


def load_config():
    with open(Path(__file__).parent / "config.json", "r", encoding="utf-8") as f:
        return json.load(f)


# ポーズ定義: { ファイル名: ポーズ記述 }
POSES = {
    "smile":     "standing, looking at viewer, gentle smile, calm expression",
    "serious":   "standing, looking at viewer, serious, focused expression",
    "surprised": "standing, looking at viewer, surprised, wide eyes",
    "sad":       "standing, looking at viewer, sad, looking down, melancholic",
    "blush":     "standing, looking at viewer, blush, shy timid expression",
    "attack":    "action pose, dynamic pose, casting offensive magic attack, fierce expression",
    "back":      "from behind, back, looking away",
    "look_back": "from behind, looking back at viewer, over shoulder",
}

# キャラ共通部分 (顔の安定化のため詳細を追加)
CHARA_BASE = "masterpiece, best quality, newest, 1girl, solo, elf, pointy ears, silver hair, long flowing hair, beautiful detailed blue eyes, delicate facial features, consistent face, fantasy white and gold robes, holding wooden staff, witch hat, full body, boots"
CHARA_BG = "simple background, green background, chroma key"
NEGATIVE = "cropped, out of frame, worst quality, low quality, oldest, early, displeasing, complex background, scenery, depth of field, drop shadow, 3d, realistic, blurry, bad anatomy, text, watermark, mutated face, distorted face, changing face, inconsistent face"


def build_workflow(pose_text: str) -> dict:
    """ポーズに合わせたワークフローを構築"""
    prompt = f"{CHARA_BASE}, {pose_text}, {CHARA_BG}"
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "waiIllustriousSDXL_v160.safetensors"}
        },
        "19": {
            "class_type": "LoraLoader",
            "inputs": {
                "model": ["1", 0], "clip": ["1", 1],
                "lora_name": "sdxl_lightning_4step_lora.safetensors",
                "strength_model": 1, "strength_clip": 1
            }
        },
        "23": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["19", 1], "text": prompt}
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["19", 1], "text": NEGATIVE}
        },
        "6": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": 768, "height": 1024, "batch_size": 1}
        },
        "2": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["19", 0], "positive": ["23", 0],
                "negative": ["4", 0], "latent_image": ["6", 0],
                "seed": 42, "control_after_generate": "randomize",
                "steps": 8, "cfg": 2, "sampler_name": "lcm",
                "scheduler": "normal", "denoise": 1
            }
        },
        "7": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["2", 0], "vae": ["1", 2]}
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "chara_elf", "images": ["7", 0]}
        }
    }


def wait_for_image(base_url, prompt_id, timeout=120):
    """生成完了を待って画像情報を返す"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{base_url}/history/{prompt_id}", timeout=5)
            if r.status_code == 200:
                h = r.json()
                if prompt_id in h:
                    status = h[prompt_id].get("status", {}).get("status_str", "")
                    if status == "error":
                        return None
                    outputs = h[prompt_id].get("outputs", {})
                    for nid, nout in outputs.items():
                        if "images" in nout and nout["images"]:
                            return nout["images"][0]
        except Exception:
            pass
        time.sleep(2)
    return None


def download_image(base_url, img_info, save_path):
    """画像をダウンロードして保存"""
    params = urlencode({
        "filename": img_info["filename"],
        "subfolder": img_info.get("subfolder", ""),
        "type": img_info.get("type", "output")
    })
    r = requests.get(f"{base_url}/view?{params}", timeout=10)
    r.raise_for_status()
    with open(save_path, "wb") as f:
        f.write(r.content)


def remove_green_bg(image_path):
    """グリーンバックを透過に変換（PIL使用）"""
    try:
        from PIL import Image
        img = Image.open(image_path).convert("RGBA")
        data = img.getdata()
        new_data = []
        for r, g, b, a in data:
            # 緑色の背景を検出して透過にする
            if g > 150 and r < 130 and b < 130:
                new_data.append((r, g, b, 0))
            elif g > 120 and g > r * 1.3 and g > b * 1.3:
                new_data.append((r, g, b, 0))
            else:
                new_data.append((r, g, b, a))
        img.putdata(new_data)
        img.save(image_path)
        return True
    except ImportError:
        print("  ⚠ Pillow未インストール - 透過処理スキップ")
        return False


def main():
    print("=" * 50)
    print("  キャラ立ち絵一括生成")
    print(f"  全{len(POSES)}ポーズ")
    print("=" * 50)

    config = load_config()
    base_url = config["comfyui"]["url"]
    client_id = str(uuid.uuid4())

    output_dir = Path(__file__).parent / "assets" / "characters"
    output_dir.mkdir(parents=True, exist_ok=True)

    success = 0
    for i, (name, pose) in enumerate(POSES.items()):
        save_path = output_dir / f"elf_{name}.png"

        # 既存チェック
        if save_path.exists():
            print(f"[SKIP] elf_{name}.png — 既に存在")
            success += 1
            continue

        print(f"\n[{i+1}/{len(POSES)}] {name} を生成中...")

        wf = build_workflow(pose)
        payload = {"prompt": wf, "client_id": client_id}

        try:
            r = requests.post(f"{base_url}/prompt", json=payload, timeout=10)
            r.raise_for_status()
            prompt_id = r.json().get("prompt_id")

            img_info = wait_for_image(base_url, prompt_id)
            if img_info:
                download_image(base_url, img_info, save_path)
                # グリーンバック除去
                remove_green_bg(save_path)
                print(f"  ✅ elf_{name}.png")
                success += 1
            else:
                print(f"  ❌ 生成失敗: {name}")
        except Exception as e:
            print(f"  ❌ エラー: {e}")

        time.sleep(1)

    print(f"\n{'=' * 50}")
    print(f"  完了！ 成功: {success}/{len(POSES)}")
    print(f"  保存先: assets/characters/")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
