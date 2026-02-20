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
SAVE_PATH = os.path.join(BASE_DIR, "99_Save_Data", "hero_stats.json")

@app.route('/action', methods=['POST'])
def handle_action():
    data = request.json
    stats = data.get("stats", {})

    # ステータスの整形
    labels = {"power":"筋力","speed":"敏捷","tough":"耐久","mind":"知性","charm":"魅力","skill":"技巧"}
    desc = [f'{labels[k]}{v}' for k, v in stats.items() if v > 0]
    stat_text = "・".join(desc) if desc else "均衡型"

    # セーブ
    save_data = {"stats": stats, "stat_text": stat_text, "confirmed_at": time.time()}
    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    # ボイス生成
    dialogue = f"救世主の魂を受理しました。あなたの属性は、{stat_text}です。"
    try:
        generate_voice(dialogue)
    except:
        pass

    print(f"✅ ステータス確定: {stat_text}")
    print(f"💾 保存先: {SAVE_PATH}")

    return jsonify({"status": "success", "message": dialogue, "stat_text": stat_text})

if __name__ == '__main__':
    print("🧠 Neural Bridge [ステータス確定のみ]")
    app.run(port=5000, threaded=True, debug=False)
