import json
from pathlib import Path
from comfyui_client import ComfyUIClient
from gm_tools import GMTools

STATE_FILE = Path("data/game_state.json")

def main():
    print("Generating Action Cards for Party Members...")
    comfyui = ComfyUIClient()
    gm = GMTools()
    
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)

    party_info = state.get("party_info", [])
    
    for i, member in enumerate(party_info):
        name = member.get("name")
        chara_data = None
        for char in gm.characters:
            if char["name"] == name:
                chara_data = char
                break
        
        if chara_data:
            # すでに「キャラ名・職業・アクションポーズ・詳細指定」が組み込まれたプロンプトを取得
            prompt = chara_data["visuals"]["comfyui_prompt"]
            
            # 手札カード（TALOTTO枠）を生成
            print(f"Generating Card for {name}...")
            card_path = comfyui.generate_party_chara(prompt)
            if card_path:
                party_info[i]["image_path"] = str(card_path)

    state["party_info"] = party_info
    
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        
    print("Action Cards generated and game_state.json updated! Check the Game Window.")

if __name__ == "__main__":
    main()
