from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app) # ブラウザからのアクセスを許可

@app.route('/action', methods=['POST'])
def receive_action():
    data = request.json
    print(f"\n⚡ プレイヤーからの操作を受信しました: {data['action']}")
    
    # 履歴を蓄積 (Data Accumulation) - 絶対パスを使用
    history_path = r"c:\Users\kuesu\GEM_Project_Root\history.json"
    action_path = r"c:\Users\kuesu\GEM_Project_Root\player_action.json"
    pulse_script = r"c:\Users\kuesu\GEM_Project_Root\00_Core_Engine\trigger_pulse.py"

    try:
        with open(history_path, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []
    
    history.append(data)
    
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

    with open(action_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    # PythonスクリプトをキックしてAIに通知する (物理的なPulseを発生させる)
    import subprocess
    subprocess.Popen(["python", pulse_script])
        
    return jsonify({"status": "received"})

if __name__ == '__main__':
    print("🚀 Neural Bridge Server (ポート: 5000) を起動しました")
    app.run(port=5000, threaded=True)
