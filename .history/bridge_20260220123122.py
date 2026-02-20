from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import subprocess

# ==========================================
# Neural Bridge Server (bridge.py)
# ==========================================
# 役割: ブラウザUIからの入力を受け取り、ファイルに書き込み、
# 物理キーボード入力をシミュレートしてAIを「起こす」。

app = Flask(__name__)
CORS(app)

# 物理パスの定義
BASE_DIR = r"c:\Users\kuesu\GEM_Project_Root"
HISTORY_PATH = os.path.join(BASE_DIR, "history.json")
ACTION_PATH = os.path.join(BASE_DIR, "player_action.json")
PULSE_SCRIPT = os.path.join(BASE_DIR, r"00_Core_Engine\trigger_pulse.py")

@app.route('/action', methods=['POST'])
def handle_action():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        print(f"\n[BRIDGE] 📥 受信アクション: {data.get('action')} - {data.get('choice_label', '')}")

        # 1. 履歴の保存
        history = []
        if os.path.exists(HISTORY_PATH):
            try:
                with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except:
                history = []
        
        history.append(data)
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)

        # 2. 現在のアクションの保存
        with open(ACTION_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        # 3. ニューラル・パルスの送信 (AIを起動)
        if os.path.exists(PULSE_SCRIPT):
            subprocess.Popen(["python", PULSE_SCRIPT])
            print("[BRIDGE] ⚡ Neural Pulse 送信完了")

        return jsonify({"status": "success", "received": data})

    except Exception as e:
        print(f"[BRIDGE] ❌ エラー発生: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*40)
    print("🚀 MACHADUN Neural Bridge Server")
    print(f"📍 PORT: 5000")
    print(f"📁 Root: {BASE_DIR}")
    print("="*40)
    app.run(port=5000, threaded=True, debug=False)
