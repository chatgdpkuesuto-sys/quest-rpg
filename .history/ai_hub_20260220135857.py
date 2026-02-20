import os
import time
import json
import logging
import threading
import requests
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

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
            
            logger.info(f"🎮 プレイヤーアクション: {action_data.get('action')}")
            
            # --- ここから LLM を呼び出して次のシナリオ展開とUIを生成する ---
            self.invoke_llm_and_generate(action_data)
            
        except Exception as e:
            logger.error(f"❌ アクション処理中にエラーが発生しました: {e}")

    def invoke_llm_and_generate(self, action_data):
        logger.info("🧠 LLM に思考をリクエスト...")
        
        # TODO: 実際の LLM API (Gemini / OpenAI 等) を呼び出す処理を実装
        # ここではモックデータを返す
        
        mock_llm_response = {
            "ui_html": """
            <div class="choices">
                <button onclick="sendAction('抵抗する')">抵抗する</button>
                <button onclick="sendAction('受け入れる')">受け入れる</button>
            </div>
            """,
            "situation_text": "あなたの目の前に、不気味な影が立ち塞がっています。どうしますか？",
            "image_prompt": "1girl, dark fantasy, horror, monster shadow, glowing red eyes",
            "voice_text": "ふふふ、大人しくしなさい……"
        }
        
        logger.info("✅ LLM の思考が完了しました")
        
        # 各種 API を連携してアセットを生成
        self.generate_assets(mock_llm_response)
        
        # HTML を生成
        self.generate_html(mock_llm_response)
        
        # ステータスを更新
        self.update_status()

    def generate_assets(self, llm_response):
        logger.info("🎨 画像生成をリクエスト (ComfyUI)...")
        # TODO: 実際の ComfyUI API 呼び出し
        
        logger.info("🎙️ 音声生成をリクエスト (VOICEVOX)...")
        # TODO: 実際の VOICEVOX API 呼び出し

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

def main():
    logger.info("🚀 AI Middle-hub (Watchdog) 起動...")
    
    # ACTION_FILE が存在しない場合は空のJSONを作成
    if not os.path.exists(ACTION_FILE):
        with open(ACTION_FILE, "w", encoding="utf-8") as f:
            json.dump({"action": "standby"}, f, ensure_ascii=False)
            
    event_handler = ActionHandler()
    observer = Observer()
    
    # 監視対象はファイルを直接指定できないため、ディレクトリを監視
    project_dir = os.path.dirname(ACTION_FILE)
    observer.schedule(event_handler, path=project_dir, recursive=False)
    
    observer.start()
    logger.info(f"👀 監視を開始しました: {ACTION_FILE}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("🛑 監視を停止します。")
    observer.join()

if __name__ == "__main__":
    main()
