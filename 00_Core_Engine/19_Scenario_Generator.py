
import json
import random
import urllib.request
import time

# ======================================================================
# 【Stage 1: Encounter Mode - Lapis Lazura】
# ======================================================================

COMFYUI_URL = "http://127.0.0.1:8188/prompt"

# ① 【完全固定】ポジティブ・ネガティブプロンプト
FIXED_POSITIVE = "(masterpiece, best quality, highres:1.3), (extremely detailed CG Unity 8k wallpaper), (intricate details:1.2), (finely detailed eyes and face:1.2), (cinematic lighting:1.2), (ray tracing:1.1), (depth of field:1.1),"
FIXED_NEGATIVE = "(low quality, worst quality:1.4), (bad anatomy), (extra fingers), (monochrome, grayscale), text, watermark, signature, username, error, blurry, cropped, (mutated hands and fingers:1.5), extra limbs, too many legs"

# ② 【シーン設定: 出会い】
SCENES = [
    {
        "name": "Encounter_Lapis_Wide", 
        "width": 832,
        "height": 1216,
        "prompt": "1girl, solo, Lapis Lazura, blue slime gijinka, (translucent blue hair:1.2), golden eyes, pale skin, (slime textured skin:1.1), blue translucent dress, forming from a shimmering blue pond, (wide shot:1.2), full body, mystical glowing cavern background, stalactites, bioluminescent plants, water ripples"
    },
    {
        "name": "Encounter_Lapis_Up", 
        "width": 1024,
        "height": 1024,
        "prompt": "1girl, solo, Lapis Lazura, blue slime gijinka, (translucent blue hair:1.2), golden eyes, (slime textured skin:1.1), (centered:1.3), upper body, face focus, curious expression, tilting head, eyes looking at viewer, soft bioluminescent lighting, glowing slime particles"
    }
]

GENERATE_COUNT_PER_SCENE = 1  

# ======================================================================

def send_to_comfyui(prompt_text, width, height, file_prefix):
    final_positive = f"{FIXED_POSITIVE} {prompt_text}"
    
    workflow = {
        "3": {"inputs": {"seed": random.randint(0, 1125899906842624), "steps": 28, "cfg": 7.0, "sampler_name": "euler", "scheduler": "normal", "denoise": 1, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}, "class_type": "KSampler"},
        "4": {"inputs": {"ckpt_name": "waiIllustriousSDXL_v160.safetensors"}, "class_type": "CheckpointLoaderSimple"},
        "5": {"inputs": {"width": width, "height": height, "batch_size": 1}, "class_type": "EmptyLatentImage"}, 
        "6": {"inputs": {"text": final_positive, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
        "7": {"inputs": {"text": FIXED_NEGATIVE, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
        "8": {"inputs": {"samples": ["3", 0], "vae": ["4", 2]}, "class_type": "VAEDecode"},
        "9": {"inputs": {"filename_prefix": file_prefix, "images": ["8", 0]}, "class_type": "SaveImage"}
    }

    p = {"prompt": workflow}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(COMFYUI_URL, data=data)
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.read()
    except Exception as e:
        print(f"❌ 送信エラー: {e}")
        return None

if __name__ == "__main__":
    print("\n" + "="*50)
    print("📜 遭遇ログ: Lapis Lazura (スライムの娘)")
    print("="*50)
    print("洞窟の奥、静かに揺れる青い泉があった。")
    print("あなたが近づくと、水面が盛り上がり、一人の少女の像を結ぶ。")
    print("半透明の身体は光を弾き、彼女は無垢な瞳であなたを見つめていた。")
    print("="*50 + "\n")

    print("🚀 画像生成リクエストを開始します...")
    for scene in SCENES:
        print(f"\n🎬 【シーン設定】: {scene['name']}")
        for i in range(1, GENERATE_COUNT_PER_SCENE + 1):
            file_prefix = f"Stage1_Lapis_{scene['name']}_{i}"
            print(f"  ⏳ 生成リクエスト送信中 ({i}/{GENERATE_COUNT_PER_SCENE})...")
            result = send_to_comfyui(scene["prompt"], scene["width"], scene["height"], file_prefix)
            if result:
                print(f"  ✅ 送信完了。")
            else:
                print(f"  ❌ 失敗。")
            time.sleep(1)
            
    print("\n🎉 全ての生成依頼が完了しました。")
