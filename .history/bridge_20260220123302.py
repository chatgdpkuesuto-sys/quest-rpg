from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import subprocess

# ==========================================
# Neural Bridge Server (bridge.py) - REFINED
# ==========================================

app = Flask(__name__)
CORS(app)

BASE_DIR = r"c:\Users\kuesu\GEM_Project_Root"
ACTION_PATH = os.path.join(BASE_DIR, "player_action.json")
PULSE_SCRIPT = os.path.join(BASE_DIR, r"00_Core_Engine\trigger_pulse.py")

@app.route('/action', methods=['POST'])
def handle_action():
    try:
        data = request.json
        print(f"\n📥 操作受信: {data.get('action')}")

        # player_action.json に書き出し
        with open(ACTION_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        # AIをキック
        if os.path.exists(PULSE_SCRIPT):
            subprocess.Popen(["python", PULSE_SCRIPT])
            print("⚡ Neural Pulse 送信完了")

        return jsonify({"status": "success", "received": data})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Neural Bridge Server (Stat Focused) 起動完了")
    app.run(port=5000, threaded=True)
