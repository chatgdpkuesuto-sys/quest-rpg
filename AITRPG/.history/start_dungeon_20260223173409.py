import json
import time
from pathlib import Path
from comfyui_client import ComfyUIClient
from voicevox_client import VoicevoxClient
from gm_tools import GMTools

STATE_FILE = Path("data/game_state.json")

def main():
    print("Starting Main Dungeon Scenario...")
    comfyui = ComfyUIClient()
    voicevox = VoicevoxClient()
    gm = GMTools()
    
    # 3人のキャラクターを取得
    suran = gm.get_character_by_id("suran")
    haruhi = gm.get_character_by_id("haruhi")
    saber = gm.get_character_by_id("saber")
    
    # パーティ情報を作成
    party = [
        gm.generate_party_info_from_chara(suran),
        gm.generate_party_info_from_chara(haruhi),
        gm.generate_party_info_from_chara(saber)
    ]
    
    # ダンジョンの背景画像を生成
    bg_prompt = "masterpiece, best quality, dark fantasy dungeon, ancient stone walls, mysterious glowing blue runes, dimly lit corridor, sinister atmosphere, anime style"
    bg_path = comfyui.generate(bg_prompt)
    
    # キャラクター（代表してセイバー）の立ち絵を生成（今回は既存のものを手抜きで流用することもできますが、せっかくなので再生成するか、前回のをそのまま使うか。ダンジョン背景に合わせて生成するのがベストです。今回は時間短縮のためプロンプトから生成）
    # ※キャラ立ち絵は先ほどのテストで生成した画像が assets/characters/ 等に落ちている可能性がありますが、今回は真面目に生成します
    print("Generating Saber's standing picture for the scene...")
    chara_path = comfyui.generate_party_chara(saber["visuals"]["comfyui_prompt"])
    
    # セイバーのセリフを生成
    voice_text = "ここがダンジョンですか。マスター、背後は私にお任せを。……何か嫌な予感がします、油断なきよう。"
    voice_path = voicevox.synthesize_dialogue(voice_text, speaker_id=saber["audio"]["voice_id"])
    
    # 状態更新
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
        
    state["mode"] = "EXPLORATION"
    state["bg_image_path"] = str(bg_path) if bg_path else ""
    state["chara_image_path"] = str(chara_path) if chara_path else ""
    state["scene_text"] = "【探索開始：忘れられた地下遺跡】\n\n『あなた達3人とマスター（プレイヤー）は、仄暗い地下遺跡の入り口に足を踏み入れた。』\n『壁には不気味な青いルーン文字が浮かび上がり、冷たい風が奥から吹き抜けてくる……』\n\nセイバー：「ここがダンジョンですか。マスター、背後は私にお任せを。……何か嫌な予感がします、油断なきよう。」\n\nハルヒ：「ちょっと！あたしを差し置いて勝手に進まないでよね！さあ、宇宙人か未来人か、どーんと来なさい！」\n\nスラン：「ふふ……賑やかなパーティーになりそうですね。私の風の魔法でサポートしますよ。」\n\n（さて、一行はどう行動するだろうか？）"
    state["dialogue_text"] = voice_text
    state["voice_path"] = str(voice_path) if voice_path else ""
    state["party_info"] = party
    
    # 自由入力メインですが、目安としての選択肢
    state["choices"] = ["慎重に奥へ進む", "周囲を探索してアイテムを探す", "いきなりハルヒに踊らせてみる"]
    
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        
    print("Updated game_state.json. The adventure begins!")

if __name__ == "__main__":
    main()
