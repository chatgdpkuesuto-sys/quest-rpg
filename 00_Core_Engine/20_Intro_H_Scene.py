
import json
import random
import urllib.request
import time

# ======================================================================
# 【Stage 2: Intro H-Scene Mode - Lapis Lazura】
# ======================================================================

COMFYUI_URL = "http://127.0.0.1:8188/prompt"

# ① 【完全固定】ポジティブ・ネガティブプロンプト
FIXED_POSITIVE = "(masterpiece, best quality, highres:1.3), (extremely detailed CG Unity 8k wallpaper), (intricate details:1.2), (finely detailed eyes and face:1.2), (cinematic lighting:1.2), (ray tracing:1.1), (depth of field:1.1),"
FIXED_NEGATIVE = "(low quality, worst quality:1.4), (bad anatomy), (extra fingers), (monochrome, grayscale), text, watermark, signature, username, error, blurry, cropped, (mutated hands and fingers:1.5), extra limbs, too many legs"

# ② 【シーン設定: 導入H】
SCENES = [
    {
        "name": "IntroH_Lapis_Melting", 
        "width": 832,
        "height": 1216,
        "prompt": "1girl, solo, Lapis Lazura, blue slime gijinka, (melting body:1.3), (semi-liquid:1.1), (translucent blue hair:1.2), golden eyes, (heavy blush:1.4), (lustful expression:1.3), parted lips, saliva dripping, translucent blue dress merging with skin, kneeling on damp ground, (bare shoulders:1.1), (cleavage:0.8), glowing slime core in chest, bioluminescent cave background"
    },
    {
        "name": "IntroH_Lapis_FaceUp", 
        "width": 1216,
        "height": 832,
        "prompt": "1girl, solo, Lapis Lazura, blue slime gijinka, (submissive:1.2), lying on back, spread legs, (body becoming fluid:1.2), (pale translucent skin:1.1), looking up at viewer, (tears in eyes:1.1), tongue out, (heavy blush:1.4), disheveled blue hair, (clinging clothes:1.2), wet environment, mossy floor, glowing plants"
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
    print("📜 遭遇ログ: Lapis Lazura (熱を帯びる水体)")
    print("="*50)
    print("あなたの熱に当てられたのか、彼女の身体が柔らかく、輪郭を失い始める。")
    print("「あ……あつい……なにか、が……溶けて……っ」")
    print("透き通った肌は赤らみ、滴り落ちる雫は彼女自身の身体の一部だった。")
    print("="*50 + "\n")

    print("🚀 画像生成リクエストを開始します...")
    for scene in SCENES:
        print(f"\n🎬 【シーン設定】: {scene['name']}")
        for i in range(1, GENERATE_COUNT_PER_SCENE + 1):
            file_prefix = f"Stage2_Lapis_{scene['name']}_{i}"
            print(f"  ⏳ 生成リクエスト送信中 ({i}/{GENERATE_COUNT_PER_SCENE})...")
            result = send_to_comfyui(scene["prompt"], scene["width"], scene["height"], file_prefix)
            if result:
                print(f"  ✅ 送信完了。")
            else:
                print(f"  ❌ 失敗。")
            time.sleep(1)
            
    print("\n🎉 全ての生成依頼が完了しました。")
