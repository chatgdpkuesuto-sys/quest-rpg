from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import sys
import time

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
    data["timestamp"] = int(time.time())
    with open(STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    if voice_text:
        try:
            generate_voice(voice_text)
        except Exception as e:
            print(f"⚠️ ボイス生成スキップ: {e}")

# ===== フェーズ1: ステータス確定のみ =====
@app.route('/action', methods=['POST'])
def handle_action():
    try:
        data = request.json
        action = data.get("action", "")
        print(f"\n📥 受信: {action}")

        with open(ACTION_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        state = read_status()

        if action == "CONFIRM_STATS_INTENT":
            stats = data.get("stats", {})
            desc = []
            for key, label in [("power","筋力"),("speed","敏捷"),("tough","耐久"),("mind","知性"),("charm","魅力"),("skill","技巧")]:
                if stats.get(key, 0) > 0:
                    desc.append(f'{label}{stats[key]}')
            stat_text = "・".join(desc) if desc else "均衡型"

            dialogue = f"救世主の魂を受理しました。あなたの属性は【{stat_text}】です。"
            state["status"] = "hero_confirmed"
            state["last_event"] = "HERO_CONFIRMED"
            state["current_dialogue"] = dialogue
            state["current_monologue"] = f"【{stat_text}】の力を宿した救世主が、異世界ラストリアに降り立とうとしている。"
            write_status(state, voice_text=dialogue)
            print(f"✅ ステータス確定: {stat_text}")

        elif action == "BACK_TO_STATS_INTENT":
            dialogue = "能力値の再設定を受け付けました。"
            state["status"] = "making_hero"
            state["last_event"] = "BACK_TO_STATS"
            state["current_dialogue"] = dialogue
            state["current_monologue"] = ""
            state["choices"] = []
            write_status(state, voice_text=dialogue)
            print("✅ ステータスに戻る")

        else:
            with open(ACTION_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"ℹ️ 記録のみ: {action}")

        return jsonify({"status": "success"})

    except Exception as e:
        print(f"❌ エラー: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("🧠 Neural Bridge [フェーズ1: ステータス]")
    app.run(port=5000, threaded=True, debug=False)
