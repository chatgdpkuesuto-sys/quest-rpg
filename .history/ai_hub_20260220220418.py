import os
import time
import json
import random
import logging
import threading
import requests
from dotenv import load_dotenv
from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- .env 読み込み ---
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# --- 設定 ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CORE_ENGINE_DIR = os.path.join(PROJECT_ROOT, "00_Core_Engine")
ACTION_FILE = os.path.join(PROJECT_ROOT, "player_action.json")
STATUS_FILE = os.path.join(PROJECT_ROOT, "status.json")
OUTPUT_SCENE = os.path.join(PROJECT_ROOT, "index_scene.json")

COMFYUI_URL = "http://127.0.0.1:8188/prompt"
VOICEVOX_URL = "http://127.0.0.1:50021"
COMFYUI_PROMPT_NODE_ID = "16"   # ★ プロンプト注入先ノードID

# --- ロギング ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ai_hub")

# --- Flask ---
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
CORS(app)

handler = None  # ActionHandler の参照

# ============================================================
#  ユーティリティ
# ============================================================

def roll_2d6():
    d1, d2 = random.randint(1, 6), random.randint(1, 6)
    return d1 + d2, (d1, d2)


def load_core_rules():
    rules = {}
    for fname in [
        "00_Absolute_Ero_Rule.md",
        "01_GM_System.md",
        "01_Dice_System.md",
        "05_Combat_Flow.md",
    ]:
        path = os.path.join(CORE_ENGINE_DIR, fname)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                rules[fname] = f.read()
    return rules


def load_game_state():
    state = {}
    mapping = {
        "status":        os.path.join(PROJECT_ROOT, "99_Save_Data", "01_Party_Status.md"),
        "inventory":     os.path.join(PROJECT_ROOT, "99_Save_Data", "02_Inventory_Storage.md"),
        "relationships": os.path.join(PROJECT_ROOT, "99_Save_Data", "04_Social_Relationships.md"),
    }
    for key, path in mapping.items():
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                state[key] = f.read()
        else:
            state[key] = "(データなし)"
    return state


def load_selection_protocol():
    path = os.path.join(CORE_ENGINE_DIR, "99_Selection_Dice_Protocol.md")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# ============================================================
#  Flask ルート
# ============================================================

@app.route("/action", methods=["POST"])
def relay_action():
    try:
        data = request.json
        logger.info("🌐 HTTP 受信: %s", json.dumps(data, ensure_ascii=False))
        with open(ACTION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return jsonify({"status": "received", "action": data.get("action", "")}), 200
    except Exception as e:
        logger.error("❌ Relay エラー: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================
#  ファイル監視
# ============================================================

class ActionHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.last_modified = 0.0
        self.lock = threading.Lock()

    def on_modified(self, event):
        if not event.src_path.endswith("player_action.json"):
            return
        now = time.time()
        with self.lock:
            if now - self.last_modified < 1.5:
                return
            self.last_modified = now
        logger.info("🔄 player_action.json 更新検知")
        self.process_action()

    # ------ メインパイプライン ------
    def process_action(self):
        try:
            with open(ACTION_FILE, "r", encoding="utf-8") as f:
                action_data = json.load(f)
            user_action = action_data.get("action", "")
            logger.info("🎮 アクション: %s", user_action)
            self.run_pipeline(user_action)
        except Exception as e:
            logger.error("❌ process_action 失敗: %s", e)

    def run_pipeline(self, user_action):
        # --- 1. ルール & ステート読み込み ---
        rules = load_core_rules()
        state = load_game_state()
        selection = load_selection_protocol()
        dice_total, dice_detail = roll_2d6()

        # --- 2. システムプロンプト構築 ---
        system_prompt = self._build_system_prompt(rules, state, selection, dice_total, dice_detail)

        # --- 3. LLM 呼び出し ---
        llm_response = self._call_llm(system_prompt, user_action)
        if llm_response is None:
            return

        logger.info("✅ LLM 応答取得完了")

        # --- 4. アセット生成 ---
        self._generate_voice(llm_response.get("voice_text", ""))
        self._generate_image(llm_response.get("image_prompt", ""))

        # --- 5. シーン JSON 書き出し ---
        self._write_scene(llm_response, dice_total, dice_detail)

        # --- 6. ステータス更新 ---
        self._update_status()

    # ------ システムプロンプト ------
    def _build_system_prompt(self, rules, state, selection, dice_total, dice_detail):
        return f"""あなたは「まちゃだん」の開発兼GM「りりす」です。
提供された『コアエンジン（ルール）』と『ゲーム状態』を完全に理解し、それに基づいて描写を行ってください。

【適用ルール（核心）】
{rules.get('00_Absolute_Ero_Rule.md', '')}
{rules.get('01_GM_System.md', '')}

【セレクション・プロトコル】
{selection}

【戦闘と成否判定】
- 今回のダイス目: 2d6 = {dice_total} {dice_detail}
{rules.get('01_Dice_System.md', '')}
{rules.get('05_Combat_Flow.md', '')}

【現在のゲーム状態】
- ステータス: {state.get('status', '不明')}
- 所持品: {state.get('inventory', '不明')}

【必須出力フォーマット (厳密なJSON)】
必ず以下のキーを持つJSONのみを出力してください。
Markdownブロック (```json) は使用せず、純粋なJSON文字列を返してください。
{{
    "situation_text": "GMとしての情景描写。ダイス判定結果も含める。",
    "ui_html": "<button class='choice-btn' onclick='sendAction(\\\"次の行動\\\")'>選択肢</button>",
    "image_prompt": "英語のComfyUI向けプロンプト。",
    "voice_text": "VOICEVOXで読み上げるセリフ"
}}"""

    # ------ LLM 呼び出し（google.genai） ------
    def _call_llm(self, system_prompt, user_action):
        api_key = os.environ.get("GGEMINI_API_KEY", "")
        if not api_key:
            logger.error("❌ GGEMINI_API_KEY が .env に設定されていません。モックモード禁止のため中断します。")
            # エラー時は最低限のフィードバックをシーンに書き出す
            self._write_scene({
                "situation_text": "<span class='highlight-despair'>【システムエラー】</span> APIキーが設定されていません。<code>.env</code> ファイルに <code>GGEMINI_API_KEY</code> を設定してください。",
                "ui_html": "<button class='choice-btn' onclick='location.reload()'>再読み込み</button>",
                "image_prompt": "",
                "voice_text": "",
            }, 0, (0, 0))
            self._update_status()
            return None

        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"プレイヤーのアクション: {user_action}",
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.8,
                    response_mime_type="application/json",
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error("❌ LLM API エラー: %s", e)
            self._write_scene({
                "situation_text": f"<span class='highlight-despair'>【LLMエラー】</span> {e}",
                "ui_html": "<button class='choice-btn' onclick='location.reload()'>再試行</button>",
                "image_prompt": "",
                "voice_text": "",
            }, 0, (0, 0))
            self._update_status()
            return None

    # ------ VOICEVOX ------
    def _generate_voice(self, text):
        if not text:
            return
        logger.info("🎙️ VOICEVOX: %s", text[:40])
        try:
            r1 = requests.post(f"{VOICEVOX_URL}/audio_query", params={"text": text, "speaker": 3}, timeout=10)
            if r1.status_code != 200:
                logger.warning("⚠️ VOICEVOX audio_query 失敗: %s", r1.status_code)
                return
            r2 = requests.post(f"{VOICEVOX_URL}/synthesis", params={"speaker": 3}, json=r1.json(), timeout=30)
            if r2.status_code == 200:
                out = os.path.join(PROJECT_ROOT, "04_Assets", "voice_out.wav")
                os.makedirs(os.path.dirname(out), exist_ok=True)
                with open(out, "wb") as f:
                    f.write(r2.content)
                logger.info("✅ 音声保存: %s", out)
        except Exception as e:
            logger.warning("⚠️ VOICEVOX 接続失敗（無視して続行）: %s", e)

    # ------ ComfyUI（ノード16にプロンプト注入） ------
    def _generate_image(self, prompt):
        if not prompt:
            return
        logger.info("🎨 ComfyUI: %s", prompt[:60])
        try:
            # ベースワークフローを読み込む
            wf_path = os.path.join(CORE_ENGINE_DIR, "Unsaved Workflow.json")
            if os.path.exists(wf_path):
                with open(wf_path, "r", encoding="utf-8") as f:
                    workflow = json.load(f)
            else:
                logger.warning("⚠️ ワークフローファイルが見つかりません: %s", wf_path)
                return

            # ★ ノード16にプロンプトを注入（存在しない場合はノード6にフォールバック）
            if COMFYUI_PROMPT_NODE_ID in workflow:
                workflow[COMFYUI_PROMPT_NODE_ID]["inputs"]["text"] = prompt
            elif "6" in workflow:
                workflow["6"]["inputs"]["text"] = prompt
                logger.info("ℹ️ ノード16が見つからないためノード6にフォールバック")
            else:
                logger.error("❌ プロンプト注入先ノードが見つかりません")
                return

            # シードをランダム化
            if "3" in workflow:
                workflow["3"]["inputs"]["seed"] = random.randint(0, 2**53)

            res = requests.post(COMFYUI_URL, json={"prompt": workflow}, timeout=10)
            logger.info("✅ ComfyUI リクエスト送信: status=%s", res.status_code)
        except requests.ConnectionError:
            logger.warning("⚠️ ComfyUI に接続できません（無視して続行）")
        except Exception as e:
            logger.warning("⚠️ ComfyUI エラー: %s", e)

    # ------ シーン書き出し ------
    def _write_scene(self, llm_response, dice_total, dice_detail):
        logger.info("📄 index_scene.json 書き出し")
        scene = {
            "situation_text": llm_response.get("situation_text", ""),
            "ui_html": llm_response.get("ui_html", ""),
            "image_prompt": llm_response.get("image_prompt", ""),
            "voice_text": llm_response.get("voice_text", ""),
            "dice_result": f"{dice_total} {dice_detail}",
            "generated_at": time.time(),
        }
        with open(OUTPUT_SCENE, "w", encoding="utf-8") as f:
            json.dump(scene, f, ensure_ascii=False, indent=4)
        logger.info("✅ index_scene.json 完了")

    # ------ ステータス更新 ------
    def _update_status(self):
        data = {"updated_at": time.time(), "state": "ready"}
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info("✅ status.json 更新完了")

# ============================================================
#  起動
# ============================================================

def run_flask():
    logger.info("🌐 Flask (Port 5000) 起動")
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=False)


def main():
    global handler
    logger.info("🚀 ai_hub.py 起動 (Flask + Watchdog)")

    # Flask
    threading.Thread(target=run_flask, daemon=True).start()

    # player_action.json 初期化
    if not os.path.exists(ACTION_FILE):
        with open(ACTION_FILE, "w", encoding="utf-8") as f:
            json.dump({"action": "standby"}, f, ensure_ascii=False)

    # Watchdog
    handler = ActionHandler()
    observer = Observer()
    observer.schedule(handler, path=PROJECT_ROOT, recursive=False)
    observer.start()
    logger.info("👀 監視開始: %s", ACTION_FILE)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("🛑 停止")
    observer.join()


if __name__ == "__main__":
    main()
