import json
from pathlib import Path
from comfyui_client import ComfyUIClient

STATE_FILE = Path("data/game_state.json")
CHARA_DIR = Path("data/characters")

def main():
    print("Generating updated dynamic characters (Anime Ver)...")
    comfyui = ComfyUIClient()
    
    with open(CHARA_DIR / "haruhi.json", "r", encoding="utf-8") as f:
        haruhi = json.load(f)
        
    haruhi_prompt = haruhi["visuals"]["comfyui_prompt"]
    print(f"Generating Haruhi: {haruhi_prompt}")
    
    # generate_party_charaの引数(soul_name)としてプロンプトテキストをそのまま流し込みます
    haruhi_img_path = comfyui.generate_party_chara(haruhi_prompt)
    
    # 状態更新
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
        
    state["chara_image_path"] = str(haruhi_img_path) if haruhi_img_path else ""
    state["scene_text"] = "【キャラクター完全準拠テスト】\n\n『キャラクターの名前や外見を、元アニメ作品そのままのタグで再生成しました！』\n\n（「涼宮ハルヒ」や「セイバー」といった固有名詞をそのまま表示し、イラストも原作に極めて近い状態になっています）"
    
    # party_infoの名前も準拠前の「ハルヒ」から「涼宮ハルヒ」などに直しておきます
    for p in state.get("party_info", []):
        if p["name"] == "ハルヒ":
            p["name"] = "涼宮ハルヒ"
    
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        
    print("Updated game_state.json with anime-accurate illustration.")

if __name__ == "__main__":
    main()
