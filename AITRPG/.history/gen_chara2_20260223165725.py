import json
import time
from pathlib import Path
from comfyui_client import ComfyUIClient
from voicevox_client import VoicevoxClient

STATE_FILE = Path("data/game_state.json")

def main():
    print("Generating second character with new VOICE and Intonation...")
    comfyui = ComfyUIClient()
    voicevox = VoicevoxClient()
    
    # ハルヒ風のキャラを生成（生成済みならキャッシュなどがあれば早いですが、今回は同じプロンプトを使います）
    chara_path = comfyui.generate_party_chara("1girl, brown hair, yellow headband, school uniform, confident smile, hands on hips")
    
    # ハルヒに合う、元気で勝気な声（小夜: 46 などを想定）
    # ※ VOICEVOXに小夜がいない場合はデフォルトの四国めたん等の別スタイル等になりますが、ID8（春日部つむぎ）など定番のIDを使います
    voice_text = "ただの人間には興味ありません！この中に宇宙人、未来人、異世界人がいたら、あたしのところに来なさい！以上！"
    voice_path = voicevox.synthesize_dialogue(voice_text, speaker_id=8)
    
    # 状態更新
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
        
    state["chara_image_path"] = str(chara_path) if chara_path else ""
    state["voice_path"] = str(voice_path) if voice_path else ""
    state["scene_text"] = "【パーティー編成（2/3人目）】\n\n『光の中から、腕組みをした強気な少女が現れた！』\n\n少女：「ただの人間には興味ありません！この中に宇宙人、未来人、異世界人がいたら、あたしのところに来なさい！以上！」\n\n（なんという強烈な個性……！彼女を2人目の仲間に加えますか？）"
    state["dialogue_text"] = voice_text
    
    # 選択肢をテキスト入力可能な指示に変更
    state["choices"] = ["仲間に加える", "別のキャラを召喚する"]
    
    # スランのステータスをUI（party_info）に追加
    state["party_info"] = [
        {
            "name": "スラン",
            "hp": 20,
            "max_hp": 20,
            "alive": True,
            "status": "OK"
        }
    ]
    
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        
    print("Updated game_state.json with character 2 (new speaker and intonation).")

if __name__ == "__main__":
    main()
