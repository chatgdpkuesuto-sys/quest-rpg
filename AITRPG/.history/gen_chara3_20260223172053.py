import json
import time
from pathlib import Path
from comfyui_client import ComfyUIClient
from voicevox_client import VoicevoxClient

STATE_FILE = Path("data/game_state.json")

def main():
    print("Generating third character...")
    comfyui = ComfyUIClient()
    voicevox = VoicevoxClient()
    
    # セイバー風のキャラを生成
    chara_path = comfyui.generate_party_chara("1girl, blonde hair, green eyes, bun hair, braided bun, blue dress, silver armor, knight, holding invisible sword")
    
    # 騎士王風の威厳ある声（Voicevox ID 14 や 29 などを想定、今回は14）
    voice_text = "問おう、貴方が私のマスターか。……ふむ、悪くない魔力パスだ。私の剣は、これより貴方と共にある。"
    voice_path = voicevox.synthesize_dialogue(voice_text, speaker_id=14)
    
    # 状態更新
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
        
    state["chara_image_path"] = str(chara_path) if chara_path else ""
    state["voice_path"] = str(voice_path) if voice_path else ""
    state["scene_text"] = "【パーティー編成（3/3人目）】\n\n『最後に召喚陣から現れたのは、白銀の甲冑と青いドレスに身を包んだ、凛々しい金髪の騎士だった！』\n\n騎士：「問おう、貴方が私のマスターか。……ふむ、悪くない魔力パスだ。私の剣は、これより貴方と共にある。」\n\n（圧倒的なカリスマと存在感！彼女を最後の仲間に加えますか？）"
    state["dialogue_text"] = voice_text
    
    # 選択肢
    state["choices"] = ["仲間に加える", "別のキャラを召喚する"]
    
    # 涼宮ハルヒ風のキャラをUI（party_info）に追加
    state["party_info"] = [
        {
            "name": "スラン",
            "hp": 20,
            "max_hp": 20,
            "alive": True,
            "status": "OK"
        },
        {
            "name": "ハルヒ",
            "hp": 25,
            "max_hp": 25,
            "alive": True,
            "status": "OK"
        }
    ]
    
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        
    print("Updated game_state.json with character 3.")

if __name__ == "__main__":
    main()
