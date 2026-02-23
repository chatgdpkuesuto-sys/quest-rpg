import json
from pathlib import Path
from comfyui_client import ComfyUIClient

STATE_FILE = Path("data/game_state.json")
CHARA_DIR = Path("data/characters")

def main():
    print("Generating updated dynamic characters...")
    comfyui = ComfyUIClient()
    
    # 3人のキャラデータを読み込む
    saber, haruhi, suran = None, None, None
    with open(CHARA_DIR / "saber.json", "r", encoding="utf-8") as f:
        saber = json.load(f)
    # 仮で現在画面に映っているハルヒをテストの主役にする（立ち絵として大きく表示させるため）
    
    # 実際には3人とも生成して、代表してセイバー（または任意のキャラ）を中央に表示します
    # ここでは一番派手なエフェクトを入れたセイバーを生成して画面に表示させます。
    
    saber_prompt = saber["visuals"]["comfyui_prompt"]
    print(f"Generating Saber: {saber_prompt}")
    saber_img_path = comfyui.generate_party_chara(saber_prompt)
    
    # 状態更新
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
        
    state["chara_image_path"] = str(saber_img_path) if saber_img_path else ""
    state["scene_text"] = "【イラストのアップデートテスト】\n\n『キャラクターのイラストプロンプトを強化しました！』\n\n（より職業が分かりやすく、派手なエフェクトやポーズを取ったイラストになっています）"
    
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        
    print("Updated game_state.json with new dramatic illustration.")

if __name__ == "__main__":
    main()
