import json
from pathlib import Path
from comfyui_client import ComfyUIClient
from gm_tools import GMTools

STATE_FILE = Path("data/game_state.json")

def main():
    print("Generating Simple Action Cards for Party Members...")
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
            # ユーザーの要望通り「キャラ名 ＋ 職業 ＋ アクションポーズ」をベースにシンプル化
            # 余計な装飾を削って、AIにキャラの正確な出力と構図を任せる（ついでにupper bodyなどで顔が潰れないよう工夫）
            if name == "涼宮ハルヒ":
                prompt = "suzumiya haruhi, SOS brigade chief, dynamic action pose, upper body, masterpiece, best quality"
            elif name == "セイバー":
                prompt = "saber (fate), knight, dynamic combat pose, upper body, masterpiece, best quality"
            elif name == "スラン":
                prompt = "1girl, elf wind mage, silver hair, casting wind magic, dynamic action pose, upper body, masterpiece, best quality"
            else:
                prompt = f"{name}, {chara_data.get('job_name', '')}, dynamic action pose, upper body, masterpiece, best quality"
            
            print(f"Generating Card for {name} with prompt: {prompt}")
            card_path = comfyui.generate_party_chara(prompt)
            if card_path:
                party_info[i]["image_path"] = str(card_path)

    state["party_info"] = party_info
    
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        
    print("Simple Action Cards generated and game_state.json updated!")

if __name__ == "__main__":
    main()
