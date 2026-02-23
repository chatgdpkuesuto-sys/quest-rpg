import json
import time
from pathlib import Path
from comfyui_client import ComfyUIClient
from voicevox_client import VoicevoxClient

STATE_FILE = Path("data/game_state.json")

def main():
    print("Generating image and audio...")
    comfyui = ComfyUIClient()
    voicevox = VoicevoxClient()
    
    # スランのイメージ生成
    chara_path = comfyui.generate_party_chara("1girl, green hair, elf, fantasy robes")
    
    # セリフ生成
    voice_text = "私を選んでくれたのね！よろしく頼むわ、指揮官！"
    voice_path = voicevox.synthesize_dialogue(voice_text)
    
    # 状態更新
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
        
    state["chara_image_path"] = str(chara_path) if chara_path else ""
    state["voice_path"] = str(voice_path) if voice_path else ""
    state["scene_text"] = "【パーティー編成（1/3）】\n\n『スランが仲間に加わりました！』\n\nスラン: 「私を選んでくれたのね！よろしく頼むわ、指揮官！」"
    state["dialogue_text"] = voice_text
    state["choices"] = ["次の仲間を探す"]
    
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        
    print("Updated game_state.json")

if __name__ == "__main__":
    main()
