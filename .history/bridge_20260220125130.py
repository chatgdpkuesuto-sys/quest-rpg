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
            print(f"🎙️ ボイス生成完了")
        except Exception as e:
            print(f"⚠️ ボイス生成スキップ: {e}")

# ===== ヒロインデータ =====
HEROINES = {
    "Aria": {
        "name": "アリア",
        "hair": "銀髪", "eyes": "碧眼",
        "fetish": "清楚/聖女", "personality": "慈愛",
        "intro": "教会の奥、薄暗い聖堂の回廊を歩いていると、祭壇の前で跪く一人の少女の姿が見えた。銀色の長い髪が、ステンドグラスの微かな光を受けて淡く輝いている。あなたの足音に気づいた彼女は、ゆっくりと振り返り、碧い瞳であなたを見つめる。",
        "dialogue": "あ……あなたが、異世界から召喚された救世主様……ですか？　わたくし、聖女アリアと申します。どうか……この世界を、お救いください。"
    },
    "Zena": {
        "name": "ゼナ",
        "hair": "黒髪", "eyes": "紅眼",
        "fetish": "女騎士/誇り高い", "personality": "高潔",
        "intro": "城門を抜けた先の訓練場。剣を振るう凛とした音が響いている。黒髪を短く切り揃えた女騎士が、鍛錬に没頭していた。汗に濡れた褐色の肌。紅い瞳がこちらを射抜くように見据える。",
        "dialogue": "……何者だ。この訓練場に一般人の立ち入りは許可していない。……救世主？ フン、その貧弱な体で何ができる。私はゼナ。あなたの実力、この剣で試させてもらう。"
    },
    "Elara": {
        "name": "エララ",
        "hair": "金髪", "eyes": "翠眼",
        "fetish": "エルフ/森の民", "personality": "神秘的",
        "intro": "王都から離れた大森林。幾重にも重なる木漏れ日の奥に、人ならざる美貌の影が揺れていた。尖った耳、森の色をした翠の瞳。千年を生きるエルフが、あなたの存在を静かに品定めしている。",
        "dialogue": "……人間。あなたから、この世界のものではない気配がする。興味深い。私はエララ。この森の番人よ。あなたが本当に救世主なら……少し、付き合ってもらえる？"
    },
    "Elize": {
        "name": "エリーゼ",
        "hair": "紫髪", "eyes": "金眼",
        "fetish": "魔女/小悪魔", "personality": "妖艶",
        "intro": "歓楽街の裏路地。怪しげな香りが漂う薬屋の扉を開けると、紫色の髪をした妖艶な女が、にやりと笑ってこちらを見た。金色の瞳が、暗がりの中で猫のように光る。",
        "dialogue": "あらぁ……見ない顔ね。それも、とびきり美味しそうな。ふふ、私はエリーゼ。この街の何でも屋よ。あなた、救世主なんですって？ なら、私と契約しない？ 損はさせないわ。"
    },
    "Yuni": {
        "name": "ユニ",
        "hair": "茶髪", "eyes": "琥珀眼",
        "fetish": "猫獣人/盗賊", "personality": "無邪気",
        "intro": "気がつくと、腰のポーチが軽い。振り返ると、猫耳と尻尾を持つ小柄な少女が、あなたの財布を手に持ってにんまりと笑っていた。捕まえようとすると、ひらりと身をかわす。",
        "dialogue": "にゃはは、ごめんにゃさい！ つい手が出ちゃって。ボク、ユニ！ 盗賊ギルドの見習いにゃ。……え？ 救世主様？ じゃあお金持ち？ ボクも連れてってくれるにゃ！"
    },
    "Mia": {
        "name": "ミア",
        "hair": "桃髪", "eyes": "桜眼",
        "fetish": "幼馴染/世話焼き", "personality": "健気",
        "intro": "この世界に飛ばされて最初に意識が戻った場所。小さな村の寝室で、一人の少女があなたの額を冷たい手で撫でていた。桃色の髪、桜色の瞳が潤んでいる。あなたの顔を見て、涙を流しながら微笑んだ。",
        "dialogue": "よかったぁ……目が覚めたんだ。私、ミア。あなたが倒れてるのを見つけて、ずっと看病してたの。ここは辺境の村よ。あなた、記憶がないの？ ……大丈夫、私がそばにいるから。"
    }
}

@app.route('/action', methods=['POST'])
def handle_action():
    try:
        data = request.json
        action = data.get("action", "")
        print(f"\n📥 受信: {action}")

        with open(ACTION_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        state = read_status()

        # ===== ステータス確定 → プロローグ（没入型ヒロイン選択）=====
        if action == "CONFIRM_STATS_INTENT":
            stats = data.get("stats", {})
            desc = []
            if stats.get("power", 0) > 0: desc.append(f'筋力{stats["power"]}')
            if stats.get("speed", 0) > 0: desc.append(f'敏捷{stats["speed"]}')
            if stats.get("tough", 0) > 0: desc.append(f'耐久{stats["tough"]}')
            if stats.get("mind", 0) > 0: desc.append(f'知性{stats["mind"]}')
            if stats.get("charm", 0) > 0: desc.append(f'魅力{stats["charm"]}')
            if stats.get("skill", 0) > 0: desc.append(f'技巧{stats["skill"]}')
            stat_text = "・".join(desc) if desc else "均衡型"

            state["status"] = "active"
            state["last_event"] = "PROLOGUE_START"
            state["current_monologue"] = (
                f"あなたは目を覚ます。<br>"
                f"見知らぬ天井。見知らぬ空気。身体に宿るのは、【{stat_text}】の力。<br>"
                f"ここは異世界ラストリア。魔王の軍勢が人類を脅かす、剣と魔法の世界だ。<br>"
                f"召喚された救世主として、あなたは最初の『運命の出会い』を迎える――"
            )
            state["current_dialogue"] = "運命の相手を見つけなさい。あなたの魂が惹かれる場所へ、足を向けてください。"
            state["choices"] = [
                {"id": "Aria",   "label": "教会の聖堂へ向かう ── 祈りの声が聞こえる"},
                {"id": "Zena",   "label": "城門の訓練場へ向かう ── 剣戟の音が響く"},
                {"id": "Elara",  "label": "大森林の奥へ進む ── 不思議な気配を感じる"},
                {"id": "Elize",  "label": "歓楽街の裏路地へ入る ── 妖しい香りが漂う"},
                {"id": "Yuni",   "label": "雑踏の中を歩く ── 何かに見られている気がする"},
                {"id": "Mia",    "label": "意識が霞む ── 誰かの温もりを感じる"}
            ]
            write_status(state, voice_text=state["current_dialogue"])
            print(f"✅ → プロローグ開始 ({stat_text})")

        # ===== 戻る =====
        elif action == "BACK_TO_STATS_INTENT":
            state["status"] = "making_hero"
            state["last_event"] = "BACK_TO_STATS"
            state["choices"] = []
            dialogue = "能力値の再設定を受け付けました。"
            state["current_dialogue"] = dialogue
            state["current_monologue"] = ""
            write_status(state, voice_text=dialogue)
            print("✅ → making_hero (戻る)")

        # ===== ヒロイン選択（没入型） =====
        elif action == "CHOICE_MADE":
            choice_id = data.get("choice_id", "")
            heroine = HEROINES.get(choice_id)
            if heroine:
                state["status"] = "active"
                state["last_event"] = f"ENCOUNTER_{choice_id}"
                state["attributes"] = {
                    "name": heroine["name"],
                    "hair": heroine["hair"],
                    "eyes": heroine["eyes"],
                    "fetish": heroine["fetish"],
                    "personality": heroine["personality"]
                }
                state["current_monologue"] = heroine["intro"]
                state["current_dialogue"] = heroine["dialogue"]
                state["choices"] = []
                write_status(state, voice_text=heroine["dialogue"])
                print(f"✅ → {heroine['name']}との邂逅")
            else:
                write_status(state)

        # ===== ゲーム中アクション（GM待ち）=====
        else:
            write_status(state)
            print(f"ℹ️ GM待ちアクション: {action}")

        return jsonify({"status": "success", "new_state": state["status"]})

    except Exception as e:
        print(f"❌ エラー: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("=" * 40)
    print("🧠 MACHADUN Neural Bridge (没入型TRPG + VOICEVOX)")
    print(f"📁 STATUS: {STATUS_PATH}")
    print("=" * 40)
    app.run(port=5000, threaded=True, debug=False)
