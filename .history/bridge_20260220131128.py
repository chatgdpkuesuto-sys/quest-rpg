from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os, sys, time, subprocess

sys.path.insert(0, r"c:\Users\kuesu\GEM_Project_Root\00_Core_Engine")
from voice_engine import generate_voice

app = Flask(__name__)
CORS(app)

SAVE = r"c:\Users\kuesu\GEM_Project_Root\99_Save_Data\hero_stats.json"
PULSE = r"c:\Users\kuesu\GEM_Project_Root\00_Core_Engine\trigger_pulse.py"

@app.route('/action', methods=['POST'])
def action():
    data = request.json
    stats = data.get("stats", {})
    labels = {"power":"筋力","speed":"敏捷","tough":"耐久","mind":"知性","charm":"魅力","skill":"技巧"}
    desc = [f'{labels[k]}{v}' for k,v in stats.items() if v > 0]
    txt = "・".join(desc) if desc else "均衡型"

    os.makedirs(os.path.dirname(SAVE), exist_ok=True)
    with open(SAVE,"w",encoding="utf-8") as f:
        json.dump({"stats":stats,"text":txt,"time":time.time()}, f, ensure_ascii=False, indent=2)

    msg = f"救世主の魂を受理しました。あなたの属性は【{txt}】です。"
    try: generate_voice(msg)
    except: pass

    # アンチグラビティを起動
    if os.path.exists(PULSE):
        subprocess.Popen(["python", PULSE])
        print("⚡ Antigravity に通知送信")

    print(f"✅ 確定: {txt}")
    return jsonify({"status":"success","message":msg})

if __name__=='__main__':
    print("🧠 Neural Bridge [ステータス]")
    app.run(port=5000, threaded=True)
