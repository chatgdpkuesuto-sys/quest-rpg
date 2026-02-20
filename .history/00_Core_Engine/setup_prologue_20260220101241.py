import os
import json
import urllib.request
import urllib.parse
import time
import requests

# Params
COMFYUI_HOST = "127.0.0.1:8188"
COMFYUI_URL = f"http://{COMFYUI_HOST}/prompt"
HISTORY_URL = f"http://{COMFYUI_HOST}/history"
VIEW_URL = f"http://{COMFYUI_HOST}/view"

VOICEVOX_URL = "http://127.0.0.1:50021"
ZUNDAMON_ID = 3

PROLOGUE_DIR = r"c:\Users\kuesu\GEM_Project_Root\00_Dashboard\outputs\Mia\Prologue"
VOICE_PATH = r"c:\Users\kuesu\GEM_Project_Root\00_Dashboard\outputs\voice.wav"
STATUS_PATH = r"c:\Users\kuesu\GEM_Project_Root\00_Dashboard\status.json"

PROMPT = "masterpiece, best quality, highly detailed, 1girl, Mia, cute, white hair, red eyes, cinematic lighting, dungeon background, prologue, looking at viewer, detailed face"
NEGATIVE = "(low quality, worst quality:1.4), text, error, cropped, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck"

def queue_prompt(prompt_workflow):
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(COMFYUI_URL, data=data)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

def get_history(prompt_id):
    with urllib.request.urlopen(f"{HISTORY_URL}/{prompt_id}") as response:
        return json.loads(response.read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"{VIEW_URL}?{url_values}") as response:
        return response.read()

print("1. Generating Mia Prologue Image...")
workflow = {
    "3": {"inputs": {"seed": int(time.time()), "steps": 28, "cfg": 7.0, "sampler_name": "euler", "scheduler": "normal", "denoise": 1, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}, "class_type": "KSampler"},
    "4": {"inputs": {"ckpt_name": "waiIllustriousSDXL_v160.safetensors"}, "class_type": "CheckpointLoaderSimple"},
    "5": {"inputs": {"width": 832, "height": 1216, "batch_size": 1}, "class_type": "EmptyLatentImage"}, 
    "6": {"inputs": {"text": PROMPT, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
    "7": {"inputs": {"text": NEGATIVE, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
    "8": {"inputs": {"samples": ["3", 0], "vae": ["4", 2]}, "class_type": "VAEDecode"},
    "9": {"inputs": {"filename_prefix": "GEM_Prologue", "images": ["8", 0]}, "class_type": "SaveImage"}
}

os.makedirs(PROLOGUE_DIR, exist_ok=True)
res = queue_prompt(workflow)
prompt_id = res['prompt_id']

image_saved = False
while not image_saved:
    try:
        hist = get_history(prompt_id)
        if prompt_id in hist:
            outputs = hist[prompt_id]['outputs']
            for node_id in outputs:
                node_out = outputs[node_id]
                if 'images' in node_out:
                    img = node_out['images'][0]
                    img_data = get_image(img['filename'], img['subfolder'], img['type'])
                    img_path = os.path.join(PROLOGUE_DIR, "prologue_1.png")
                    with open(img_path, "wb") as f:
                        f.write(img_data)
                    print(f"✅ Image saved to {img_path}")
                    image_saved = True
            break
    except Exception as e:
        pass
    time.sleep(1)

print("2. Generating Zundamon Voice...")
voice_text = "ついに始まるのだ！覚悟はいいのだ？"
try:
    q_res = requests.post(f"{VOICEVOX_URL}/audio_query", params={"text": voice_text, "speaker": ZUNDAMON_ID})
    if q_res.status_code == 200:
        s_res = requests.post(f"{VOICEVOX_URL}/synthesis", params={"speaker": ZUNDAMON_ID}, json=q_res.json())
        if s_res.status_code == 200:
            with open(VOICE_PATH, "wb") as f:
                f.write(s_res.content)
            print("✅ Voice saved to outputs/voice.wav")
except Exception as e:
    print("Voice generation skipped/failed:", e)

print("3. Updating status.json...")
status_data = {
  "arousal": 0,
  "despair": 0,
  "current_image": "../outputs/Mia/Prologue/prologue_1.png",
  "last_event": "プロローグ開始",
  "is_climax": False,
  "status": "updated",
  "current_dialogue": voice_text,
  "current_monologue": "闇夜に包まれたダンジョンの入り口。<br>あなたの前には、まだ何も知らない『ミア』が立っている。<br>ここから、彼女の運命を左右する過酷なTRPGが幕を開ける。",
  "variant_mode": False,
  "attributes": {
    "name": "ミア (Mia)",
    "hair": "白髪",
    "eyes": "赤眼",
    "fetish": "",
    "personality": "健気"
  },
  "timestamp": int(time.time())
}

with open(STATUS_PATH, "w", encoding='utf-8') as f:
    json.dump(status_data, f, indent=2, ensure_ascii=False)
print("✅ status.json updated.")
print("\n🎬 PROLOGUE PRE-RENDERING COMPLETE. THE STAGE IS SET.")
