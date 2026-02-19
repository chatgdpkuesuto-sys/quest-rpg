import json
import random
import urllib.request
import urllib.parse
import time
import uuid
import os

# ======================================================================
# 【設定エリア】
# ======================================================================

COMFYUI_HOST = "127.0.0.1:8188"
COMFYUI_URL = f"http://{COMFYUI_HOST}/prompt"
HISTORY_URL = f"http://{COMFYUI_HOST}/history"
VIEW_URL = f"http://{COMFYUI_HOST}/view"

# 保存先ディレクトリ (絶対パス推奨)
OUTPUT_DIR = r"c:\Users\kuesu\GEM_Project_Root\99_Ero_Library\Generated_Images"

# ① 【完全固定】ポジティブ・ネガティブプロンプト
# 常に「高画質」「詳細」を指定し、品質を底上げする
FIXED_POSITIVE = "(masterpiece, best quality, highres:1.3), (extremely detailed CG Unity 8k wallpaper), (intricate details:1.2), (finely detailed eyes and face:1.2), "
FIXED_NEGATIVE = "(low quality, worst quality:1.4), (bad anatomy), (extra fingers), (monochrome, grayscale), text, watermark, signature, username, error, blurry, cropped, (mutated hands and fingers:1.5)"

# ② 【シーン設定】
SCENES = [
    {
        "name": "Scene1_Portrait", 
        "width": 832,
        "height": 1216,
        "prompt": "Serena Siluria, gardevoir gijinka, 1girl, solo, standing in a mystical forest, elegant white dress, full body, cinematic lighting"
    },
    {
        "name": "Scene2_Landscape", 
        "width": 1216,
        "height": 832,
        "prompt": "Serena Siluria, gardevoir gijinka, 1girl, solo, lying on bed, spread legs, heavy blush, looking up at viewer, dimly lit bedroom"
    },
     {
        "name": "Scene3_Square", 
        "width": 1024,
        "height": 1024,
        "prompt": "Serena Siluria, gardevoir gijinka, 1girl, solo, close up, face focus, lustful expression, tongue out, heavily blushing, blurry background"
    }
]

# 各シーンにつき何枚ずつ生成するか
GENERATE_COUNT_PER_SCENE = 1

# ======================================================================

def queue_prompt(prompt_workflow):
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(COMFYUI_URL, data=data)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"❌ ComfyUIへの接続エラー: {e}")
        return None

def get_latest_file(path):
    pass # Not needed in direct mode, but keeping for compatibility if reused

def get_history(prompt_id):
    with urllib.request.urlopen(f"{HISTORY_URL}/{prompt_id}") as response:
        return json.loads(response.read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"{VIEW_URL}?{url_values}") as response:
        return response.read()

def save_image(image_data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(image_data)
    print(f"  💾 保存完了: {filepath}")

def generate_image(prompt_text, output_path=None):
    print(f"\n🎬 生成開始: {prompt_text[:30]}...")
    
    # ワークフロー定義
    final_positive = f"{FIXED_POSITIVE} {prompt_text}"
    
    workflow = {
        "3": {"inputs": {"seed": random.randint(0, 10000000000), "steps": 28, "cfg": 7.0, "sampler_name": "euler", "scheduler": "normal", "denoise": 1, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}, "class_type": "KSampler"},
        "4": {"inputs": {"ckpt_name": "waiIllustriousSDXL_v160.safetensors"}, "class_type": "CheckpointLoaderSimple"},
        "5": {"inputs": {"width": 832, "height": 1216, "batch_size": 1}, "class_type": "EmptyLatentImage"}, 
        "6": {"inputs": {"text": final_positive, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
        "7": {"inputs": {"text": FIXED_NEGATIVE, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
        "8": {"inputs": {"samples": ["3", 0], "vae": ["4", 2]}, "class_type": "VAEDecode"},
        "9": {"inputs": {"filename_prefix": "GEM_LivePlay", "images": ["8", 0]}, "class_type": "SaveImage"}
    }

    # 1. プロンプトをキューに入れる
    response = queue_prompt(workflow)
    if not response:
        return
    
    prompt_id = response['prompt_id']
    print(f"  ✅ キューに追加 (ID: {prompt_id}) - 生成待機中...")

    # 2. 生成完了を待機 (ポーリング)
    while True:
        try:
            history = get_history(prompt_id)
            if prompt_id in history:
                print("  ✅ 生成完了！画像をダウンロードします...")
                
                # 出力画像情報を取得
                outputs = history[prompt_id]['outputs']
                for node_id in outputs:
                    node_output = outputs[node_id]
                    if 'images' in node_output:
                        for image in node_output['images']:
                            image_data = get_image(image['filename'], image['subfolder'], image['type'])
                            
                            if output_path:
                                save_image(image_data, output_path)
                                # ダッシュボードへの同期 (JSON書き換え)
                                status_path = r"c:\Users\kuesu\GEM_Project_Root\00_Dashboard\status.json"
                                status_data = {}
                                if os.path.exists(status_path):
                                    try:
                                        with open(status_path, "r", encoding="utf-8") as f:
                                            status_data = json.load(f)
                                            if not isinstance(status_data, dict):
                                                status_data = {}
                                    except Exception:
                                        status_data = {}
                                
                                status_data["current_image"] = "outputs/latest.png"
                                status_data["status"] = "updated_by_16_Illustrator"
                                status_data["timestamp"] = int(time.time())
                                
                                with open(status_path, "w", encoding="utf-8") as f:
                                    json.dump(status_data, f, ensure_ascii=False, indent=2)
                                print("  📡 Live Server との同期完了！")
                            else:
                                timestamp = int(time.time())
                                save_filename = f"LiveGen_{timestamp}.png"
                                save_image(image_data, os.path.join(OUTPUT_DIR, save_filename))
                break
        except Exception as e:
            pass
        
        time.sleep(1)

if __name__ == "__main__":
    import sys
    
    # CLI引数があれば1枚だけ生成してダッシュボードに投げるモード
    if len(sys.argv) > 1:
        prompt_arg = sys.argv[1]
        print("🚀 Live Server Sync Mode 起動")
        live_output = r"c:\Users\kuesu\GEM_Project_Root\00_Dashboard\outputs\latest.png"
        generate_image(prompt_arg, output_path=live_output)
    else:
        # 従来のバッチモード
        print("🚀 Auto Illustrator v2.0 (ComfyUI連携版) 起動")
        print(f"📂 保存先: {OUTPUT_DIR}\n")

        for scene in SCENES:
            for i in range(1, GENERATE_COUNT_PER_SCENE + 1):
                 generate_image(scene["prompt"])
                
        print("\n🎉 全ての生成が完了しました！")