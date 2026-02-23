"""
generate_props.py — 手前小物（プロップ）画像一括生成スクリプト
グリーンバック付きで生成し、Pillowで透過PNGに変換する。
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


# 小物プロンプト定義: { ファイル名: プロンプト記述 }
# ※ 下寄りや手前に配置される構図を狙う
PROPS = {
    "grass": "tall grass, foreground, bottom of the frame",
    "table": "wooden tavern table, food, drinks, bottom of the frame, foreground",
    "desk": "old wooden desk, scattered papers, books, inkwell, bottom of the frame",
    "signboard": "wooden signboard, bottom right corner",
    "bushes": "dense green bushes, leaves, bottom of the frame",
    "magic_circle_ground": "glowing magic circle on the floor, flat perspective, bottom of the frame",
    "crystals": "glowing blue crystals, stalagmites, bottom corners",
    "window_frame": "stone window frame, looking out, border frame",
}

# 共通プロンプト
PROP_BASE = "masterpiece, best quality, newest, object only, no humans, simple background, green background, chroma key"
NEGATIVE = "1girl, 1boy, character, human, person, text, watermark, bad quality, blurry"


def build_workflow(prop_text: str) -> dict:
    """プロンプトに合わせたワークフローを構築"""
    prompt = f"{PROP_BASE}, {prop_text}"
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
            "inputs": {"width": 1280, "height": 720, "batch_size": 1}  # 背景と同じアスペクト比
        },
        "2": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["19", 0], "positive": ["23", 0],
                "negative": ["4", 0], "latent_image": ["6", 0],
                "seed": 42, "control_after_generate": "randomize",
                "steps": 6, "cfg": 1.5, "sampler_name": "lcm",
                "scheduler": "normal", "denoise": 1
            }
        },
        "7": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["2", 0], "vae": ["1", 2]}
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "prop", "images": ["7", 0]}
        }
    }


def wait_for_image(base_url, prompt_id, timeout=120):
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
    """グリーンバックを透過に変換"""
    try:
        from PIL import Image
        img = Image.open(image_path).convert("RGBA")
        data = img.getdata()
        new_data = []
        for r, g, b, a in data:
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
        print("  ⚠ Pillow未インストール")
        return False
    except Exception as e:
        print(f"  ⚠ 透過処理エラー: {e}")
        return False


def main():
    print("=" * 50)
    print("  手前小物画像 (Props) 一括生成")
    print(f"  全{len(PROPS)}種類")
    print("=" * 50)

    config = load_config()
    base_url = config["comfyui"]["url"]
    client_id = str(uuid.uuid4())

    output_dir = Path(__file__).parent / "assets" / "props"
    output_dir.mkdir(parents=True, exist_ok=True)

    success = 0
    for i, (name, prop_prompt) in enumerate(PROPS.items()):
        save_path = output_dir / f"prop_{name}.png"
        
        if save_path.exists():
            print(f"[SKIP] prop_{name}.png — 既に存在")
            success += 1
            continue

        print(f"\n[{i+1}/{len(PROPS)}] {name} を生成中...")
        wf = build_workflow(prop_prompt)

        try:
            r = requests.post(f"{base_url}/prompt", json={"prompt": wf, "client_id": client_id}, timeout=10)
            r.raise_for_status()
            prompt_id = r.json().get("prompt_id")

            img_info = wait_for_image(base_url, prompt_id)
            if img_info:
                download_image(base_url, img_info, save_path)
                remove_green_bg(save_path)
                print(f"  ✅ prop_{name}.png")
                success += 1
            else:
                print(f"  ❌ 生成失敗: {name}")
        except Exception as e:
            print(f"  ❌ エラー: {e}")

        time.sleep(1)

    print(f"\n{'=' * 50}")
    print(f"  完了！ 成功: {success}/{len(PROPS)}")
    print(f"  保存先: assets/props/")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
