from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import sys
import time

# voice_engine をインポート
sys.path.insert(0, os.path.join(r"c:\Users\kuesu\GEM_Project_Root", "00_Core_Engine"))
from voice_engine import generate_voice

app = Flask(__name__)
CORS(app)

BASE_DIR = r"c:\Users\kuesu\GEM_Project_Root"
STATUS_PATH = os.path.join(BASE_DIR, "status.json")
ACTION_PATH = os.path.join(BASE_DIR, "player_action.json")

def read_status():
    with open(STATUS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def write_status(data, voice_text=None):
    """status.json を書き出し、セリフがあればVOICEVOXで読み上げる"""
    data["timestamp"] = int(time.time())
    with open(STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # セリフがあればボイス生成
    if voice_text:
        try:
            generate_voice(voice_text)
            print(f"🎙️ ボイス生成完了: {voice_text[:30]}...")
        except Exception as e:
            print(f"⚠️ ボイス生成スキップ: {e}")

@app.route('/action', methods=['POST'])
def handle_action():
    try:
        data = request.json
        action = data.get("action", "")
        print(f"\n📥 受信: {action}")

        # アクションをファイルに記録
        with open(ACTION_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        # 現在の状態を読む
        state = read_status()

        # ===== 意志の処理 =====
        if action == "CONFIRM_STATS_INTENT":
            state["status"] = "hero_confirmed"
            state["last_event"] = "HERO_CONFIRMED"
            stats = data.get("stats", {})
            desc = []
            if stats.get("power", 0) > 0: desc.append(f'筋力{stats["power"]}')
            if stats.get("speed", 0) > 0: desc.append(f'敏捷{stats["speed"]}')
            if stats.get("tough", 0) > 0: desc.append(f'耐久{stats["tough"]}')
            if stats.get("mind", 0) > 0: desc.append(f'知性{stats["mind"]}')
            if stats.get("charm", 0) > 0: desc.append(f'魅力{stats["charm"]}')
            if stats.get("skill", 0) > 0: desc.append(f'技巧{stats["skill"]}')
            stat_text = "・".join(desc) if desc else "均衡型"
            dialogue = f"救世主の魂を受理しました。{stat_text}の器を持つあなたに、契約するヒロインを選んでいただきます。"
            state["current_dialogue"] = dialogue
            state["current_monologue"] = "魂の器が形作られた。次なる選択は、あなたが絆を結ぶヒロイン。"
            write_status(state, voice_text=dialogue)
            print(f"✅ → hero_confirmed ({stat_text})")

        elif action == "BACK_TO_STATS_INTENT":
            state["status"] = "making_hero"
            state["last_event"] = "BACK_TO_STATS"
            dialogue = "能力値の再設定を受け付けました。改めて定義してください。"
            state["current_dialogue"] = dialogue
            state["current_monologue"] = "時は巻き戻された。汝の魂、その真なる形を問い直す。"
            write_status(state, voice_text=dialogue)
            print("✅ → making_hero (戻る)")

        elif action == "CHARACTER_SELECT_INTENT":
            target = data.get("target", "Unknown")
            target_name = data.get("target_name", target)
            state["status"] = "active"
            state["last_event"] = f"CHARACTER_SELECTED_{target}"
            state["attributes"]["name"] = target_name
            dialogue = f"{target_name}との契約が成立しました。物語が始まります。"
            state["current_dialogue"] = dialogue
            state["current_monologue"] = f"運命の歯車が動き出した。{target_name}、その魂に刻まれた宿命が、今あなたの手に委ねられる。"
            state["choices"] = []
            write_status(state, voice_text=dialogue)
            print(f"✅ → active ({target_name})")

        else:
            # ゲーム中のアクション（LOVE, LUST等）はファイルに記録するのみ
            # GM（AI）が手動でstatus.jsonを更新する
            write_status(state)
            print(f"ℹ️ GM待ちアクション: {action}")

        return jsonify({"status": "success", "new_state": state["status"]})

    except Exception as e:
        print(f"❌ エラー: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("=" * 40)
    print("🧠 MACHADUN Neural Bridge (自律型 + VOICEVOX)")
    print(f"📁 STATUS: {STATUS_PATH}")
    print("=" * 40)
    app.run(port=5000, threaded=True, debug=False)
