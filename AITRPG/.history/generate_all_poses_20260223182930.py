import json
from pathlib import Path
from comfyui_client import ComfyUIClient

STATE_FILE = Path("data/game_state.json")

def main():
    print("Generating 8 Poses for Party Members...")
    comfyui = ComfyUIClient()
    
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)

    party_info = state.get("party_info", [])
    
    for member in party_info:
        name = member.get("name")
        
        # アクション等の指定を含めない「基本の身体と服装の特徴」だけのクリーンなプロンプトを作成
        if name == "涼宮ハルヒ":
            base_prompt = "1girl, suzumiya haruhi, wearing fantasy RPG hero cosplay costume, holding toy sword, upper body, masterpiece, best quality"
        elif name == "セイバー":
            base_prompt = "1girl, saber (fate), wearing modern casual clothes with knight cosplay accents, upper body, masterpiece, best quality"
        elif name == "スラン" or name == "suran":
            base_prompt = "1girl, suran, silver hair elf, pointy ears, wearing japanese high school uniform cosplay, upper body, masterpiece, best quality"
        else:
            base_prompt = f"1girl, {name}, wearing fantasy cosplay costume, upper body, masterpiece, best quality"
        
        print(f"--- Starting 8-pose generation for {name} ---")
        poses = comfyui.generate_chara_poses(name, base_prompt)
        print(f"Finished {name}. Generated {len(poses)} images.\n")

if __name__ == "__main__":
    main()
