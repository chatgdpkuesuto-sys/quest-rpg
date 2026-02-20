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

# 生成済みのバリエーションを保存する場所（ダッシュボードが直接読み込む）
# このスクリプト自体が独立して動くようにルートフォルダも指定可能にしておくが、
# メインは00_Dashboard/outputs/variants
OUTPUT_DIR = r"c:\Users\kuesu\GEM_Project_Root\00_Dashboard\outputs\variants"

# ① 【完全固定】ポジティブ・ネガティブプロンプト
# 常に「高画質」「詳細」を指定し、品質を底上げする
FIXED_POSITIVE = "(masterpiece, best quality, highres:1.3), (extremely detailed CG Unity 8k wallpaper), (intricate details:1.2), (finely detailed eyes and face:1.2), "
FIXED_NEGATIVE = "(low quality, worst quality:1.4), (bad anatomy), (extra fingers), (monochrome, grayscale), text, watermark, signature, username, error, blurry, cropped, (mutated hands and fingers:1.5)"

# ② 【ルート分岐・事前生成設定】
# ルートのプレフィックスと生成枚数。プロンプト自体はキャラクターJSONから読み込む
SCENES = [
    {"prefix": "route_love", "key": "route_love", "count": 4},
    {"prefix": "route_lust", "key": "route_lust", "count": 3},
    {"prefix": "route_special", "key": "route_special", "count": 3}
]

# 各シーンにつき何枚生成するかはSCENESのcountで指定する（ダッシュボード用）
GENERATE_COUNT_PER_SCENE = 1 # Not broadly used now

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

def generate_image(prompt_text, output_path=None, custom_filename=None, is_sync_mode=False):
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
                            elif custom_filename:
                                save_image(image_data, custom_filename)
                            else:
                                save_image(image_data, os.path.join(OUTPUT_DIR, f"LiveGen_{int(time.time())}.png"))
                                
                            if is_sync_mode:
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
                break
        except Exception as e:
            pass
        
        time.sleep(1)

if __name__ == "__main__":
    import sys
    
    char_name = "Zena" # デフォルト
    is_sync = False
    
    # 引数パース
    if len(sys.argv) > 1:
        if sys.argv[1] == "sync":
            is_sync = True
            if len(sys.argv) > 2:
                char_name = sys.argv[2]
        else:
            char_name = sys.argv[1]
            if len(sys.argv) > 2 and sys.argv[2] == "sync":
                is_sync = True

    # キャラクターJSONの読み込み
    char_file = f"c:\\Users\\kuesu\\GEM_Project_Root\\00_Core_Engine\\Character_Prompts\\{char_name}.json"
    char_data = {}
    base_prompt = "1girl, solo, "
    if os.path.exists(char_file):
        with open(char_file, "r", encoding="utf-8") as f:
            char_data = json.load(f)
            base_prompt = char_data.get("base_prompt", base_prompt) + ", "
    else:
        print(f"⚠️ キャラクターファイルが見つかりません: {char_file}。フォールバックを使用します。")

    if is_sync:
        print(f"🚀 Live Server Sync Mode 起動 (キャラ: {char_name})")
        live_output = r"c:\Users\kuesu\GEM_Project_Root\00_Dashboard\outputs\latest.png"
        
        # 1. プレイヤーアクションの読み取り
        action_path = r"c:\Users\kuesu\GEM_Project_Root\player_action.json"
        action = ""
        try:
            with open(action_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                action = data.get("action", "")
        except Exception as e:
            print(f"⚠️ アクション読み取り失敗: {e}")

        # 2. ルート分岐とプロンプトの動的生成
        if "慈愛" in action:
            route_prompt = str(char_data.get("route_love", "gentle smile, blushing"))
            print("  💕 慈愛・調教ルート を検知。")
        elif "淫靡" in action:
            route_prompt = str(char_data.get("route_lust", "ahegao, intense passion"))
            print("  😈 淫靡・嗜虐ルート を検知。")
        elif "特殊" in action:
            route_prompt = str(char_data.get("route_special", "glowing eyes, trance state"))
            print("  👁️ 特殊・覚醒ルート を検知。")
        else:
            route_prompt = "standing, looking at viewer"
            print(f"  ℹ️ 特定ルート非検知: デフォルトプロンプトを使用 ({action})")

        prompt_arg = str(base_prompt) + route_prompt

        # 3. 指定パスへ生成
        generate_image(prompt_arg, output_path=live_output, is_sync_mode=True)
        
    else:
        # 従来のバッチモード（ダッシュボード事前生成モード）
        char_output_dir = os.path.join(OUTPUT_DIR, char_name)
        os.makedirs(char_output_dir, exist_ok=True)
        
        print(f"🚀 Auto Illustrator v2.0 (Pre-Generation Mode) 起動")
        print(f"👤 対象キャラクター: {char_name}")
        print(f"📂 保存先: {char_output_dir}\n")

        for scene in SCENES:
            prefix = str(scene.get("prefix", "img"))
            count = int(scene.get("count", 1))
            scene_key = str(scene.get("key", ""))
            route_prompt = str(char_data.get(scene_key, "standing, looking at viewer"))
            full_prompt = str(base_prompt) + route_prompt
            
            for i in range(1, count + 1):
                 save_filename = os.path.join(char_output_dir, f"{prefix}_{i}.png")
                 generate_image(full_prompt, custom_filename=save_filename, is_sync_mode=False)
                 
        print(f"\n🎉 {char_name} の事前生成が完了しました！")