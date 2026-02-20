import json
import random
import urllib.request
import urllib.parse
import time
import os
import sys

# ======================================================================
# 【設定エリア】
# ======================================================================

COMFYUI_HOST = "127.0.0.1:8188"
COMFYUI_URL = f"http://{COMFYUI_HOST}/prompt"
HISTORY_URL = f"http://{COMFYUI_HOST}/history"
VIEW_URL = f"http://{COMFYUI_HOST}/view"

# 保存先ディレクトリ
OUTPUT_BASE_DIR = r"c:\Users\kuesu\GEM_Project_Root\00_Dashboard\outputs\variants"

# 固定ポジティブ・ネガティブ
FIXED_POSITIVE = "(masterpiece, best quality, highres:1.3), (extremely detailed CG Unity 8k wallpaper), (intricate details:1.2), (finely detailed eyes and face:1.2), "
FIXED_NEGATIVE = "(low quality, worst quality:1.4), (bad anatomy), (extra fingers), (monochrome, grayscale), text, watermark, signature, username, error, blurry, cropped, (mutated hands and fingers:1.5)"

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

def generate_variation(prompt_text, index):
    print(f"\n🎬 バリエーション生成 [{index}/10]: {prompt_text[:30]}...")
    
    # ワークフロー定義 (Seedを変えることで差分を作る)
    final_positive = f"{FIXED_POSITIVE} {prompt_text}"
    
    workflow = {
        "3": {"inputs": {"seed": random.randint(0, 10000000000), "steps": 28, "cfg": 7.0, "sampler_name": "euler", "scheduler": "normal", "denoise": 1, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}, "class_type": "KSampler"},
        "4": {"inputs": {"ckpt_name": "waiIllustriousSDXL_v160.safetensors"}, "class_type": "CheckpointLoaderSimple"},
        "5": {"inputs": {"width": 832, "height": 1216, "batch_size": 1}, "class_type": "EmptyLatentImage"}, 
        "6": {"inputs": {"text": final_positive, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
        "7": {"inputs": {"text": FIXED_NEGATIVE, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
        "8": {"inputs": {"samples": ["3", 0], "vae": ["4", 2]}, "class_type": "VAEDecode"},
        "9": {"inputs": {"filename_prefix": "GEM_Variant", "images": ["8", 0]}, "class_type": "SaveImage"}
    }

    response = queue_prompt(workflow)
    if not response: return None
    
    prompt_id = response['prompt_id']
    
    while True:
        try:
            history = get_history(prompt_id)
            if prompt_id in history:
                outputs = history[prompt_id]['outputs']
                for node_id in outputs:
                    node_output = outputs[node_id]
                    if 'images' in node_output:
                        for image in node_output['images']:
                            image_data = get_image(image['filename'], image['subfolder'], image['type'])
                            save_path = os.path.join(OUTPUT_BASE_DIR, f"variant_{index}.png")
                            save_image(image_data, save_path)
                            return save_path
                break
        except Exception: pass
        time.sleep(1)
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 17_Batch_Illustrator.py \"prompt\"")
        sys.exit(1)
        
    prompt = sys.argv[1]
    print(f"🚀 Batch Illustrator 起動 (10枚生成予定)")
    
    for i in range(1, 11):
        generate_variation(prompt, i)
        
    print("\n🎉 全てのバリエーション生成が完了しました！")
