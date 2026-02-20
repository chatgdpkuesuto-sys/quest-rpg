import os
import time
import json
import random
import logging
import threading
import requests
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- 設定 ---
PROJECT_ROOT = r"c:\Users\kuesu\GEM_Project_Root"
CORE_ENGINE_DIR = os.path.join(PROJECT_ROOT, "00_Core_Engine")
ACTION_FILE = os.path.join(PROJECT_ROOT, "player_action.json")
STATUS_FILE = os.path.join(PROJECT_ROOT, "status.json")
TEMPLATE_FILE = os.path.join(PROJECT_ROOT, "base.html")
OUTPUT_HTML = os.path.join(PROJECT_ROOT, "index.html")

COMFYUI_URL = "http://127.0.0.1:8188/prompt"
VOICEVOX_URL = "http://127.0.0.1:50021"

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask App セットアップ
app = Flask(__name__)
CORS(app)

# 共有の ActionHandler
handler = None

def roll_2d6():
    """2d6ダイスを振る"""
    d1, d2 = random.randint(1, 6), random.randint(1, 6)
    return d1 + d2, (d1, d2)

def load_core_rules():
    """00_Core_Engine から主要なルール・ドキュメントを読み込む"""
    rules = {}
    important_files = [
        "00_Absolute_Ero_Rule.md",
        "01_GM_System.md",
        "01_Dice_System.md",
        "05_Combat_Flow.md"
    ]
    for filename in important_files:
        path = os.path.join(CORE_ENGINE_DIR, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                rules[filename] = f.read()
    return rules

def load_game_state():
    """99_Save_Data から現在のゲーム状態を読み込む"""
    state_files = {
        "status": os.path.join(PROJECT_ROOT, "99_Save_Data", "01_Party_Status.md"),
        "inventory": os.path.join(PROJECT_ROOT, "99_Save_Data", "02_Inventory_Storage.md"),
        "relationships": os.path.join(PROJECT_ROOT, "99_Save_Data", "04_Social_Relationships.md")
    }
    state = {}
    for key, path in state_files.items():
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                state[key] = f.read()
        else:
            state[key] = "Data not found. Initialize required."
    return state

@app.route('/action', methods=['POST'])
def relay_action():
    """フロントエンドからのアクションを受け取り、ファイルに書き込む"""
    try:
        data = request.json
        logger.info(f"🌐 HTTP経由でアクションを受信: {data}")
        
        with open(ACTION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return jsonify({"status": "received", "action": data.get("action")})
    except Exception as e:
        logger.error(f"❌ Relayエラー: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

class ActionHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.last_modified = 0.0
        self.lock = threading.Lock()

    def on_modified(self, event):
        if event.src_path == ACTION_FILE:
            # 重複発火を防止
            current_time = time.time()
            with self.lock:
                if current_time - self.last_modified < 1.0:
                    return
                self.last_modified = current_time
            
            logger.info(f"🔄 ACTION_FILE の更新を検知しました: {ACTION_FILE}")
            self.process_action()

    def process_action(self):
        try:
            with open(ACTION_FILE, "r", encoding="utf-8") as f:
                action_data = json.load(f)
            
            logger.info(f"🎮 プレイヤーアクションを実行開始: {action_data.get('action')}")
            self.invoke_llm_and_generate(action_data)
        except Exception as e:
            logger.error(f"❌ アクション処理中にエラーが発生しました: {e}")

    def invoke_llm_and_generate(self, action_data):
        logger.info("🧠 LLM に思考をリクエスト...")
        
        user_action = action_data.get('action', '')
        api_key = os.environ.get("GEMINI_API_KEY")
        
        # 動的なルールとステータスの読み込み
        rules = load_core_rules()
        # 追加: 新しいセレクションプロトコルの読み込み
        selection_path = os.path.join(CORE_ENGINE_DIR, "99_Selection_Dice_Protocol.md")
        selection_protocol = ""
        if os.path.exists(selection_path):
            with open(selection_path, "r", encoding="utf-8") as f:
                selection_protocol = f.read()

        game_state = load_game_state()
        dice_res, dice_detail = roll_2d6()

        dynamic_system_prompt = f"""
あなたは「まちゃだん」の開発兼GM「りりす」です。
提供された『コアエンジン（ルール）』と『ゲーム状態』を完全に理解し、それに基づいて描写を行ってください。

【適用ルール（核心）】
{rules.get('00_Absolute_Ero_Rule.md', 'N/A')}
{rules.get('01_GM_System.md', 'N/A')}

【セレクション・プロトコル】
※ヒロイン選択が発生する場合、以下の手順に従ってください。
{selection_protocol}

【戦闘と成否判定ガイドライン】
- 判定が必要な場合、提供されたダイス目 (2d6: {dice_res} {dice_detail}) を活用して判定結果を描写してください。
{rules.get('01_Dice_System.md', 'N/A')}
{rules.get('05_Combat_Flow.md', 'N/A')}

【現在のゲーム状態】
- ステータス: {game_state.get('status', 'Unknown')}
- 所持品: {game_state.get('inventory', 'Empty')}

【必須出力フォーマット (厳密なJSON)】
必ず以下のキーを持つJSONのみを出力してください。Markdownブロック (```json) は使用せず、純粋なJSON文字列を返してください。
{{
    "situation_text": "GMとしての情景描写。ダイス判定があった場合はその結果も含めること。EXモードの『絶望レッド』『淫靡ピンク』を積極的に使用。",
    "ui_html": "<div class='choices'><button onclick='sendAction(\"アクション\")'>選択肢</button></div>",
    "image_prompt": "英語でのComfyUI向けプロンプト。描写の核心を強調。",
    "voice_text": "VOICEVOXで読み上げるセリフ"
}}
"""

        if not api_key:
            logger.warning("⚠️ 環境変数 'GEMINI_API_KEY' が設定されていません。モックデータを使用します。")
            llm_response = {
                "ui_html": """
                <div class="choices">
                    <button onclick="sendAction('冒険に出る')">冒険に出る</button>
                    <button onclick="sendAction('ステータス確認')">ステータス確認</button>
                </div>
                """,
                "situation_text": f"（APIキー未設定）あなたは「{user_action}」と行動した。ダイス目は {dice_res} だ。コアエンジンに従い、世界の歯車が回りだす……。<br><span class='highlight-despair'>【絶望レッド（赤・太字）】</span>を確認せよ。",
                "image_prompt": "1girl, dark fantasy, core engine interface, magical grimoire",
                "voice_text": "ふふふ、私の用意した世界へようこそ……。APIキーを忘れないでね？"
            }
        else:
            try:
                genai.configure(api_key=api_key)
                generation_config = {
                    "temperature": 0.8,
                    "response_mime_type": "application/json",
                }
                model = genai.GenerativeModel(
                    model_name="gemini-2.0-flash",
                    system_instruction=dynamic_system_prompt,
                    generation_config=generation_config
                )
                
                response = model.generate_content(f"プレイヤーのアクション: {user_action}")
                llm_response = json.loads(response.text)
                
            except Exception as e:
                logger.error(f"❌ LLM API 呼び出し中にエラーが発生しました: {e}")
                return
        
        logger.info("✅ LLM の思考が完了しました")
        self.generate_assets(llm_response)
        self.generate_html(llm_response)
        self.update_status()

    def generate_assets(self, llm_response):
        # 1. VOICEVOX
        voice_text = llm_response.get("voice_text", "")
        if voice_text:
            logger.info(f"🎙️ 音声生成リクエスト (VOICEVOX): {voice_text}")
            try:
                res1 = requests.post(f"{VOICEVOX_URL}/audio_query", params={"text": voice_text, "speaker": 3})
                if res1.status_code == 200:
                    query_data = res1.json()
                    res2 = requests.post(f"{VOICEVOX_URL}/synthesis", params={"speaker": 3}, json=query_data)
                    if res2.status_code == 200:
                        audio_path = os.path.join(PROJECT_ROOT, "04_Assets", "voice_out.wav")
                        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                        with open(audio_path, "wb") as f: f.write(res2.content)
                        logger.info(f"✅ 音声保存完了: {audio_path}")
            except Exception as e: logger.error(f"❌ VOICEVOX連携エラー: {e}")

        # 2. ComfyUI (Stub)
        image_prompt = llm_response.get("image_prompt", "")
        if image_prompt:
            logger.info(f"🎨 画像生成リクエスト (ComfyUI プロンプト): {image_prompt}")

    def generate_html(self, llm_response):
        logger.info("📄 index.html を生成中...")
        try:
            if not os.path.exists(TEMPLATE_FILE):
                base_html = "<html><body><div id='situation'>{{ SITUATION }}</div><div id='ui'>{{ UI_CONTENT }}</div></body></html>"
            else:
                with open(TEMPLATE_FILE, "r", encoding="utf-8") as f: base_html = f.read()
            
            output_html = base_html.replace("{{ SITUATION }}", llm_response.get("situation_text", ""))
            output_html = base_html.replace("{{ UI_CONTENT }}", llm_response.get("ui_html", ""))
            with open(OUTPUT_HTML, "w", encoding="utf-8") as f: f.write(output_html)
            logger.info(f"✅ {OUTPUT_HTML} を生成しました。")
        except Exception as e: logger.error(f"❌ HTML 生成中にエラーが発生しました: {e}")

    def update_status(self):
        logger.info("📊 status.json を更新中...")
        status_data = {"updated_at": time.time(), "state": "ready"}
        try:
            with open(STATUS_FILE, "w", encoding="utf-8") as f: json.dump(status_data, f, ensure_ascii=False, indent=4)
            logger.info("✅ ステータス更新完了")
        except Exception as e: logger.error(f"❌ status.json 更新中にエラーが発生しました: {e}")

def run_flask():
    logger.info("🌐 Action Relay Server 起動中 (Port 5000)...")
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)

def main():
    global handler
    logger.info("🚀 AI Middle-hub (Watchdog + Flask + Logic) 起動...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    if not os.path.exists(ACTION_FILE):
        with open(ACTION_FILE, "w", encoding="utf-8") as f: json.dump({"action": "standby"}, f, ensure_ascii=False)
    handler = ActionHandler()
    observer = Observer()
    project_dir = os.path.dirname(ACTION_FILE)
    observer.schedule(handler, path=project_dir, recursive=False)
    observer.start()
    logger.info(f"👀 ファイル監視を開始しました: {ACTION_FILE}")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("🛑 監視を停止します。")
    observer.join()

if __name__ == "__main__":
    main()
