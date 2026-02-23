import json
import time
from pathlib import Path
from voicevox_client import VoicevoxClient

STATE_FILE = Path("data/game_state.json")

def main():
    print("Generating response audio...")
    voicevox = VoicevoxClient()
    
    # ユーザーが「ほほ」と言った（あるいはクリックした）体でのGMからの返答
    voice_text = "ほほ！笑っている場合ではありませんよ！さあ、早く次の仲間を探しましょう！"
    voice_path = voicevox.synthesize_dialogue(voice_text)
    
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
        
    state["voice_path"] = str(voice_path) if voice_path else ""
    state["scene_text"] = "【GMからのメッセージ】\n\n『ほほ……？ 余裕そうですね。ですがまだまだ準備は始まったばかりですよ！』\n『さあ、引き続きパーティ編成を進めましょう。』"
    state["dialogue_text"] = voice_text
    state["choices"] = ["次のガチャを引く"]
    
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        
    print("Updated game_state.json with custom response.")

if __name__ == "__main__":
    main()
