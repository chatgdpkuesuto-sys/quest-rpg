
import json
import random
import urllib.request
import time

# ======================================================================
# 【Stage 3: Finish Scene Mode - Lapis Lazura】
# ======================================================================

COMFYUI_URL = "http://127.0.0.1:8188/prompt"

# ① 【完全固定】ポジティブ・ネガティブプロンプト
FIXED_POSITIVE = "(masterpiece, best quality, highres:1.3), (extremely detailed CG Unity 8k wallpaper), (cinematic lighting), (depth of field:1.2),"
FIXED_NEGATIVE = "(low quality, worst quality:1.4), (bad anatomy), (extra fingers), (monochrome, grayscale), text, watermark, signature, username, error, blurry, cropped, (mutated hands and fingers:1.5), (fused fingers), (too many fingers), censor, mosaic, bar censor"

# ② 【シーン設定: フィニッシュ】
SCENES = [
    {
        "name": "Finish_POV_Lapis_Press", 
        "width": 1024,
        "height": 1024,
        "prompt": "1girl, (POV:1.4), (first person perspective:1.3), (looking down:1.4), (from above:1.2), (own hands holding girl:1.2), (own hands merging with fluid skin:1.2), Lapis Lazura, blue slime gijinka, (melting:1.4), (semi-liquid:1.2), (translucent blue hair spreading:1.2), golden eyes looking up, (ahegao:1.2), (heavy blush, crying, drooling, tongue out, trembling:1.3), (mating press:1.3), (torn translucent blue dress:1.2), (exposed cleavage), (spread legs:1.2), (large size difference:1.2), (penis inserted into pussy:1.3), (overflowing cum:1.2), (cum visible through translucent body:1.4), (in a glowing bioluminescent cave, wet mossy ground)"
    },
    {
        "name": "Finish_Lapis_AfterSex", 
        "width": 1216,
        "height": 832,
        "prompt": "1girl, solo, Lapis Lazura, blue slime gijinka, (lying on back:1.1), (exhausted:1.2), (body in a semi-liquid state:1.3), (translucent blue skin:1.1), (long messy blue hair), (heavy blush:1.4), (blissful ahegao:1.3), tongue out, saliva, dilated pupils, (creampie:1.3), (large amount of cum inside visible through translucent belly:1.4), (cum dripping:1.2), (messy:1.1), (glowing bioluminescent cave, stalactites, shafts of light, wet environment)"
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
    print("📜 遭遇ログ: Lapis Lazura (完全なる融解)")
    print("="*50)
    print("彼女の境界線はもはや曖昧になり、あなたの熱にすべてを委ねている。")
    print("注ぎ込まれた種火は、彼女の透き通った身体の中で白く輝いていた。")
    print("「あ……ぁ……っ！　とけて、まざって……ひとつに、なるのぉ……！」")
    print("="*50 + "\n")

    print("🚀 画像生成リクエストを開始します...")
    for scene in SCENES:
        print(f"\n🎬 【シーン設定】: {scene['name']}")
        for i in range(1, GENERATE_COUNT_PER_SCENE + 1):
            file_prefix = f"Stage3_Lapis_{scene['name']}_{i}"
            print(f"  ⏳ 生成リクエスト送信中 ({i}/{GENERATE_COUNT_PER_SCENE})...")
            result = send_to_comfyui(scene["prompt"], scene["width"], scene["height"], file_prefix)
            if result:
                print(f"  ✅ 送信完了。")
            else:
                print(f"  ❌ 失敗。")
            time.sleep(1)
            
    print("\n🎉 全ての生成依頼が完了しました。")
