import json
from pathlib import Path
from comfyui_client import ComfyUIClient

# テスト用にスランのデータを読み込み、画像を生成する
SURAN_FILE = Path("data/characters/suran.json")

def main():
    print("Testing new Dynamic Prompt for Suran...")
    comfyui = ComfyUIClient()
    
    with open(SURAN_FILE, "r", encoding="utf-8") as f:
        chara_data = json.load(f)
        
    prompt = chara_data["visuals"]["comfyui_prompt"]
    print(f"Prompt: {prompt}")
    
    chara_path = comfyui.generate_party_chara(prompt)
    
    if chara_path:
        print(f"Success: {chara_path}")
    else:
        print("Failed to generate image.")

if __name__ == "__main__":
    main()
