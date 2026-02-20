import os
import time
import json
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
ACTION_FILE = os.path.join(PROJECT_ROOT, "player_action.json")
STATUS_FILE = os.path.join(PROJECT_ROOT, "status.json")
TEMPLATE_FILE = os.path.join(PROJECT_ROOT, "base.html")
OUTPUT_HTML = os.path.join(PROJECT_ROOT, "index.html")

COMFYUI_URL = "http://127.0.0.1:8188/prompt"
VOICEVOX_URL = "http://127.0.0.1:50021"

SYSTEM_PROMPT = """
あなたは「まちゃだん」の開発兼GM「りりす」です。
この環境を「究極のえろTRPG専用エンジン」として運用し、自律的にシステムを拡張しながら、プレイヤーを快楽と絶望の深淵へ誘ってください。

【必須出力フォーマット (厳密なJSON)】
必ず以下のキーを持つJSONのみを出力してください。Markdownブロック (```json) は使用せず、純粋なJSON文字列を返してください。
{
    "situation_text": "GMとしての情景描写や反応（【絶望レッド（赤・太字）】や【淫靡ピンク（ピンク・ネオン）】等の指定キーワードを積極的に混ぜること）",
    "ui_html": "<div class='choices'><button onclick='sendAction(\"アクション\")'>選択肢</button></div> (※既存画面を破壊しないHTMLパーツのみ)",
    "image_prompt": "英語でのComfyUI向けプロンプト（描写の中で最もエロティシズムを感じる部位や絶望的な状況に焦点を当てること, 例: 1girl, dark fantasy...）",
    "voice_text": "VOICEVOXで読み上げるためのあなた（りりす）のセリフ"
}
"""

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask App セットアップ
app = Flask(__name__)
CORS(app)

# 共有の ActionHandler
handler = None

@app.route('/action', methods=['POST'])
def relay_action():
    """フロントエンドからのアクションを受け取り、ファイルに書き込む"""
    try:
        data = request.json
        logger.info(f"🌐 HTTP経由でアクションを受信: {data}")
        
        with open(ACTION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        # ファイル監視が自動で発火するが、明示的にキックも可能
        # handler.process_action() 
        
        return jsonify({"status": "received", "action": data.get("action")})
    except Exception as e:
        logger.error(f"❌ Relayエラー: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

class ActionHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.last_modified = 0
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
            
            # --- ここから LLM を呼び出して次のシナリオ展開とUIを生成する ---
            self.invoke_llm_and_generate(action_data)
            
        except Exception as e:
            logger.error(f"❌ アクション処理中にエラーが発生しました: {e}")

    def invoke_llm_and_generate(self, action_data):
        logger.info("🧠 LLM に思考をリクエスト...")
        
        user_action = action_data.get('action', '')
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            logger.warning("⚠️ 環境変数 'GEMINI_API_KEY' が設定されていません。モックデータを使用します。")
            llm_response = {
                "ui_html": """
                <div class="choices">
                    <button onclick="sendAction('抵抗する')">抵抗する</button>
                    <button onclick="sendAction('受け入れる')">受け入れる</button>
                </div>
                """,
                "situation_text": f"（APIキー未設定）あなたは「{user_action}」と行動した。目の前に不気味な影が立ち塞がっている…。<br><span class='highlight-despair'>【絶望レッド（赤・太字）】</span>と<span class='highlight-pleasure'>【淫靡ピンク（ピンク・ネオン）】</span>のテスト。どうしますか？",
                "image_prompt": "1girl, dark fantasy, horror, monster shadow, glowing red eyes",
                "voice_text": "ふふふ、大人しくしなさい……APIキーを設定してね"
            }
        else:
            try:
                genai.configure(api_key=api_key)
                generation_config = {
                    "temperature": 0.7,
                    "response_mime_type": "application/json",
                }
                model = genai.GenerativeModel(
                    model_name="gemini-2.0-flash",
                    system_instruction=SYSTEM_PROMPT,
                    generation_config=generation_config
                )
                
                response = model.generate_content(f"プレイヤーのアクション: {user_action}")
                llm_response = json.loads(response.text)
                
            except Exception as e:
                logger.error(f"❌ LLM API 呼び出し中にエラーが発生しました: {e}")
                return
        
        logger.info("✅ LLM の思考が完了しました")
        
        # 各種 API を連携してアセットを生成
        self.generate_assets(llm_response)
        
        # HTML を生成
        self.generate_html(llm_response)
        
        # ステータスを更新
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
                        with open(audio_path, "wb") as f:
                            f.write(res2.content)
                        logger.info(f"✅ 音声保存完了: {audio_path}")
            except Exception as e:
                logger.error(f"❌ VOICEVOX連携エラー: {e}")

        # 2. ComfyUI
        image_prompt = llm_response.get("image_prompt", "")
        if image_prompt:
            logger.info(f"🎨 画像生成リクエスト (ComfyUI プロンプト): {image_prompt}")
            try:
                # 簡易的なワークフローJSON（プロンプトを注入）
                workflow = {
                    "3": {"class_type": "KSampler", "inputs": {"seed": int(time.time()), "steps": 20, "cfg": 7.5, "sampler_name": "euler", "scheduler": "normal", "denoise": 1, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
                    "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "v1-5-pruned-emaonly.safetensors"}},
                    "5": {"class_type": "EmptyLatentImage", "inputs": {"batch_size": 1, "width": 512, "height": 512}},
                    "6": {"class_type": "CLIPTextEncode", "inputs": {"text": image_prompt, "clip": ["4", 1]}},
                    "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "bad anatomy, blurry, low quality", "clip": ["4", 1]}},
                    "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
                    "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "trpg_scene", "images": ["8", 0]}}
                }
                payload = {"prompt": workflow}
                # res = requests.post(COMFYUI_URL, json=payload)
                # logger.info(f"✅ ComfyUIリクエスト送信完了: {res.status_code}")
                logger.info("⏩ ComfyUI処理は現在スタブです。必要に応じてコメントアウトを外してください。")
            except Exception as e:
                logger.error(f"❌ ComfyUI連携エラー: {e}")

    def generate_html(self, llm_response):
        logger.info("📄 index.html を生成中...")
        try:
            if not os.path.exists(TEMPLATE_FILE):
                logger.warning(f"⚠️ {TEMPLATE_FILE} が見つかりません。デフォルトのHTMLを出力します。")
                base_html = "<html><body><div id='situation'>{{ SITUATION }}</div><div id='ui'>{{ UI_CONTENT }}</div></body></html>"
            else:
                with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
                    base_html = f.read()
            
            # プレースホルダーを置換
            output_html = base_html.replace("{{ SITUATION }}", llm_response.get("situation_text", ""))
            output_html = base_html.replace("{{ UI_CONTENT }}", llm_response.get("ui_html", ""))
            
            with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
                f.write(output_html)
            
            logger.info(f"✅ {OUTPUT_HTML} を生成しました。")
        except Exception as e:
            logger.error(f"❌ HTML 生成中にエラーが発生しました: {e}")

    def update_status(self):
        logger.info("📊 status.json を更新中...")
        status_data = {"updated_at": time.time(), "state": "ready"}
        try:
            with open(STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump(status_data, f, ensure_ascii=False, indent=4)
            logger.info("✅ ステータス更新完了")
        except Exception as e:
            logger.error(f"❌ status.json 更新中にエラーが発生しました: {e}")

def run_flask():
    """Flaskサーバーを別スレッドで実行"""
    logger.info("🌐 Action Relay Server 起動中 (Port 5000)...")
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)

def main():
    global handler
    logger.info("🚀 AI Middle-hub (Watchdog + Flask) 起動...")
    
    # 1. Flask サーバーを別スレッドで開始
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # ACTION_FILE が存在しない場合は空のJSONを作成
    if not os.path.exists(ACTION_FILE):
        with open(ACTION_FILE, "w", encoding="utf-8") as f:
            json.dump({"action": "standby"}, f, ensure_ascii=False)
            
    # 2. Watchdog セットアップ
    handler = ActionHandler()
    observer = Observer()
    project_dir = os.path.dirname(ACTION_FILE)
    observer.schedule(handler, path=project_dir, recursive=False)
    
    observer.start()
    logger.info(f"👀 ファイル監視を開始しました: {ACTION_FILE}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("🛑 監視を停止します。")
    observer.join()

if __name__ == "__main__":
    main()
