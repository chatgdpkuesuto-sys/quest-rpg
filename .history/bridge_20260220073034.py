from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app) # ブラウザからのアクセスを許可

@app.route('/action', methods=['POST'])
def receive_action():
    data = request.json
    print(f"\n⚡ プレイヤーからの操作を受信しました: {data['action']}")
    
    with open('player_action.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    # PythonスクリプトをキックしてAIに通知する
    import subprocess
    subprocess.Popen(["python", r"c:\Users\kuesu\GEM_Project_Root\00_Core_Engine\trigger_pulse.py"])
        
    return jsonify({"status": "received"})

if __name__ == '__main__':
    print("🚀 Neural Bridge Server (ポート: 5000) を起動しました")
    app.run(port=5000, threaded=True)
