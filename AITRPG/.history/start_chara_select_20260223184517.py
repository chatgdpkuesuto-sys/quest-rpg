"""
start_chara_select.py — キャラクター選択画面からゲームを開始するスクリプト
1. キャラ選択画面を game_state.json に書き出す
2. game_core.py で表示し、プレイヤーの選択を待つ
3. 選択されたキャラの8ポーズ差分を CHARAPOSE.json ワークフローで自動生成
4. ダンジョン探索画面へ遷移
"""

import json
import time
import sys
from pathlib import Path
from comfyui_client import ComfyUIClient
from voicevox_client import VoicevoxClient
from gm_tools import GMTools

STATE_FILE = Path("data/game_state.json")
ACTION_FILE = Path("data/player_action.json")

def reset_action():
    with open(ACTION_FILE, "w", encoding="utf-8") as f:
        json.dump({"latest_action": "", "latest_choice_index": -1, "timestamp": 0}, f, ensure_ascii=False, indent=2)

def write_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def wait_for_player_action():
    """プレイヤーの選択を待つ"""
    print("[Script] プレイヤーの選択を待機中...")
    last_ts = 0
    while True:
        try:
            with open(ACTION_FILE, "r", encoding="utf-8") as f:
                action = json.load(f)
            ts = action.get("timestamp", 0)
            if ts > 0 and ts != last_ts:
                return action
        except:
            pass
        time.sleep(0.5)

def main():
    print("=" * 50)
    print("  ANIME CROSS DUNGEONS — キャラクター選択")
    print("=" * 50)
    
    gm = GMTools()
    comfyui = ComfyUIClient()
    voicevox = VoicevoxClient()
    
    # 利用可能なキャラクター一覧
    charas = gm.characters
    if not charas:
        print("エラー: data/characters/ にキャラクターデータがありません。")
        sys.exit(1)
    
    chara_names = [c["name"] for c in charas]
    chara_jobs = [c.get("job_name", "???") for c in charas]
    chara_skills = [c.get("skill", {}).get("name", "???") for c in charas]
    
    # ========== PHASE 1: メインキャラクター選択 ==========
    reset_action()
    
    intro_text = (
        "【キャラクター選択】\n\n"
        "『あなたはこれから、仲間と共にダンジョンの深奥を目指す冒険者です。』\n"
        "『まずは、先頭に立つ「メインキャラクター」を選んでください。』\n\n"
    )
    for i, c in enumerate(charas):
        stats = c.get("stats", {})
        intro_text += f"▶ {c['name']}（{c.get('job_name', '???')}）\n"
        intro_text += f"   HP:{c.get('max_hp', '?')} | STR:{stats.get('STR','?')} DEX:{stats.get('DEX','?')} INT:{stats.get('INT','?')} LUC:{stats.get('LUC','?')}\n"
        intro_text += f"   スキル: {c.get('skill',{}).get('name','???')} / パッシブ: {c.get('passive',{}).get('name','???')}\n\n"
    
    intro_text += "選択肢からメインキャラクターを選んでください！"
    
    choices = [f"{c['name']}（{c.get('job_name','???')}）" for c in charas]
    
    state = {
        "mode": "CHARA_SELECT",
        "scene_text": intro_text,
        "choices": choices,
        "bg_image_path": "",
        "chara_image_path": "",
        "prop_image_path": "",
        "bgm_path": "",
        "voice_path": "",
        "dialogue_text": "仲間を選んでください。あなたの選択が冒険の運命を決めます。",
        "party_info": []
    }
    write_state(state)
    print(f"[Script] キャラ選択画面をセット完了。選択肢: {choices}")
    
    # プレイヤーの選択を待つ
    action = wait_for_player_action()
    choice_idx = action.get("latest_choice_index", -1)
    
    if choice_idx < 0 or choice_idx >= len(charas):
        print(f"[Script] 無効な選択: {choice_idx}。デフォルト(0)を使用。")
        choice_idx = 0
    
    selected_chara = charas[choice_idx]
    remaining_charas = [c for i, c in enumerate(charas) if i != choice_idx]
    
    print(f"[Script] メインキャラ決定: {selected_chara['name']}")
    
    # ========== PHASE 2: 選択されたキャラの8ポーズ差分を生成 ==========
    reset_action()
    
    generating_text = (
        f"【{selected_chara['name']}を選択しました！】\n\n"
        f"'{selected_chara['name']}' のポーズ差分（8種類）を生成しています...\n"
        f"（笑顔・真剣・驚き・悲しみ・照れ・戦闘・背面・見返り）\n\n"
        f"しばらくお待ちください。ComfyUIが8枚の差分画像を順次生成中です。\n"
        f"完了次第、自動的に冒険が始まります！"
    )
    
    state["scene_text"] = generating_text
    state["choices"] = []
    state["dialogue_text"] = f"{selected_chara['name']}、参上です！"
    write_state(state)
    
    # ComfyUIで8ポーズ差分を生成
    base_prompt = selected_chara.get("visuals", {}).get("comfyui_prompt", f"1girl, {selected_chara['name']}")
    # ポーズ指定なしの「基本の外見」プロンプトにする（ポーズはgenerate_chara_posesが付ける）
    # comfyui_promptはアクションポーズや背景を含むので、外見の核だけ抽出
    clean_prompt = base_prompt.split(",")
    # dynamic/action/pose/background 系のワードを除外してクリーンなプロンプトに
    exclude_words = ["dynamic", "action", "pose", "background", "battlefield", "epic", "cinematic", "looking at viewer", "full body", "casting", "holding", "pointing", "summoning", "combat", "slash", "particles", "lighting", "wind energy", "power"]
    clean_parts = []
    for part in clean_prompt:
        stripped = part.strip().lower()
        if not any(ex in stripped for ex in exclude_words):
            clean_parts.append(part.strip())
    
    clean_base = ", ".join(clean_parts) if clean_parts else base_prompt
    print(f"[Script] クリーンプロンプト: {clean_base}")
    
    poses = comfyui.generate_chara_poses(selected_chara["name"], clean_base)
    print(f"[Script] {len(poses)}枚のポーズ差分を生成しました。")
    
    # ========== PHASE 3: 全員揃えてダンジョン探索開始 ==========
    # パーティ情報を構築
    party = []
    all_charas_ordered = [selected_chara] + remaining_charas
    for c in all_charas_ordered:
        info = gm.generate_party_info_from_chara(c)
        party.append(info)
    
    # 背景画像を生成
    print("[Script] ダンジョン背景を生成中...")
    bg_prompt = "masterpiece, best quality, dark fantasy dungeon entrance, ancient stone walls, mysterious glowing blue runes, dimly lit corridor, sinister atmosphere, anime style"
    bg_path = comfyui.generate(bg_prompt)
    
    # 選んだキャラの立ち絵（smileポーズがあればそれを使う）
    chara_image = ""
    if "smile" in poses:
        chara_image = str(poses["smile"])
    else:
        # 既存のカード画像を生成
        chara_path = comfyui.generate_party_chara(selected_chara["visuals"]["comfyui_prompt"])
        chara_image = str(chara_path) if chara_path else ""
    
    # セリフ生成
    voice_text = f"マスター、{selected_chara['name']}がメインに立ちます。よろしくお願いしますね。"
    voice_path = voicevox.synthesize_dialogue(voice_text, speaker_id=selected_chara["audio"]["voice_id"])
    
    # 最終ステート
    scene_text = (
        f"【冒険開始！ — {selected_chara['name']}をメインに出発！】\n\n"
        f"『{selected_chara['name']}を先頭に、3人のパーティーがダンジョンの入り口に足を踏み入れた。』\n"
        f"『壁には不気味な青いルーン文字が浮かび上がり、冷たい風が奥から吹き抜けてくる……』\n\n"
    )
    for c in all_charas_ordered:
        name = c["name"]
        if name == "涼宮ハルヒ":
            scene_text += f"ハルヒ：「さあ、行くわよ！宇宙人も未来人も、ダンジョンの奥に隠れてるに決まってるじゃない！」\n\n"
        elif name == "セイバー":
            scene_text += f"セイバー：「マスター、背後は私にお任せを。……何か嫌な予感がします、油断なきよう。」\n\n"
        elif name == "スラン":
            scene_text += f"スラン：「ふふ……賑やかなパーティーになりそうですね。私の風の魔法でサポートしますよ。」\n\n"
    
    scene_text += "（さて、一行はどう行動するだろうか？）"
    
    final_state = {
        "mode": "EXPLORATION",
        "scene_text": scene_text,
        "choices": ["慎重に奥へ進む", "周囲を探索してアイテムを探す", "まずは自己紹介をしよう"],
        "bg_image_path": str(bg_path) if bg_path else "",
        "chara_image_path": chara_image,
        "prop_image_path": "",
        "bgm_path": "",
        "voice_path": str(voice_path) if voice_path else "",
        "dialogue_text": voice_text,
        "party_info": party
    }
    write_state(final_state)
    reset_action()
    
    print("=" * 50)
    print(f"  冒険開始！ メインキャラ: {selected_chara['name']}")
    print(f"  ポーズ差分: {len(poses)}枚生成済み")
    print("=" * 50)

if __name__ == "__main__":
    main()
