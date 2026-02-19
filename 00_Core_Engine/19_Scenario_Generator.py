
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

# ② 【シーン設定: Phase 1 朝】
SCENES = [
    {
        "name": "Phase1_Inn_Morning_Wide", 
        "width": 832,
        "height": 1216,
        "prompt": "1girl, solo, Yuni, (catgirl:1.2), (cat ears:1.2), (cat tail), (thief outfit:1.1), (short pink hair:1.1), green eyes, (waking up:1.1), (stretching arms:1.2), (sitting on bed:1.1), (morning light:1.2), (sun rays), wooden fictional inn room, clutter, cozy"
    },
    {
        "name": "Phase1_Inn_Morning_Up", 
        "width": 1024,
        "height": 1024,
        "prompt": "1girl, solo, Yuni, (catgirl:1.2), (cat ears:1.2), (thief outfit:1.1), (short pink hair:1.1), green eyes, (looking at viewer:1.3), (cheerful smile:1.2), (upper body), (face focus), (morning light), (dust motes), wooden wall background"
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
    print("📜 Phase 1: Preparation (朝の目覚め)")
    print("="*50)
    print("朝日が窓から差し込み、安宿の埃っぽい空気を照らしている。")
    print("隣のベッドでは、ユニが大きなあくびをしながら伸びをしていた。")
    print("「んん〜っ…おはよ、あなた。今日も稼ぎに行こっか！」")
    print("="*50 + "\n")

    print("🚀 画像生成リクエストを開始します...")
    for scene in SCENES:
        print(f"\n🎬 【シーン設定】: {scene['name']}")
        for i in range(1, GENERATE_COUNT_PER_SCENE + 1):
            file_prefix = f"Phase1_Yuni_{scene['name']}_{i}"
            print(f"  ⏳ 生成リクエスト送信中 ({i}/{GENERATE_COUNT_PER_SCENE})...")
            result = send_to_comfyui(scene["prompt"], scene["width"], scene["height"], file_prefix)
            if result:
                print(f"  ✅ 送信完了。")
            else:
                print(f"  ❌ 失敗。")
            time.sleep(1)
            
    print("\n🎉 全ての生成依頼が完了しました。")
