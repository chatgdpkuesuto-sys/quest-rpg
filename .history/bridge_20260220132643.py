from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os, subprocess

app = Flask(__name__)
CORS(app)

ACTION_PATH = r"c:\Users\kuesu\GEM_Project_Root\player_action.json"
PULSE = r"c:\Users\kuesu\GEM_Project_Root\00_Core_Engine\trigger_pulse.py"

@app.route('/action', methods=['POST'])
def relay():
    data = request.json
    action = data.get("action", "?")
    print(f"📥 {action}")

    # 1. ファイルに保存
    with open(ACTION_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # 2. GMに通知（trigger_pulse）
    if os.path.exists(PULSE):
        subprocess.Popen(["python", PULSE])
        print("⚡ GM通知送信")

    return jsonify({"status": "relayed"})

if __name__ == '__main__':
    print("🔌 Neural Bridge [中継専用]")
    app.run(port=5000, threaded=True)
