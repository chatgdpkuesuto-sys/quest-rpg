"""
ai_hub.py ── まちゃだん VRMMO 物理エンジン
-------------------------------------------
player_action.json を監視 → Gemini API → ComfyUI → VOICEVOX → index_scene.json
"""

import os
import time
import json
import random
import logging
import threading
import requests
from dotenv import load_dotenv
from google import genai
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- .env ---
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# --- パス ---
ROOT = os.path.dirname(os.path.abspath(__file__))
ACTION_FILE = os.path.join(ROOT, "player_action.json")
SCENE_FILE  = os.path.join(ROOT, "index_scene.json")
STATUS_FILE = os.path.join(ROOT, "status.json")
VOICE_OUT   = os.path.join(ROOT, "04_Assets", "voice_out.wav")

COMFYUI_URL  = "http://127.0.0.1:8188/prompt"
VOICEVOX_URL = "http://127.0.0.1:50021"
COMFYUI_NODE = "16"

# --- ロギング ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("ai_hub")

# --- 処理中フラグ（ループ防止の最重要ガード） ---
_processing = False
_processing_lock = threading.Lock()


def roll_2d6():
    d1, d2 = random.randint(1, 6), random.randint(1, 6)
    return d1 + d2, f"({d1},{d2})"


def read_file(path):
    """UTF-8でファイル読み込み。なければ空文字を返す。"""
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_system_prompt(dice_total, dice_detail):
    """コンパクトなシステムプロンプトを構築（トークン節約）"""
    # ステータスだけ読む（軽量）
    status_text = read_file(os.path.join(ROOT, "99_Save_Data", "01_Party_Status.md"))[:800]
    inventory_text = read_file(os.path.join(ROOT, "99_Save_Data", "02_Inventory_Storage.md"))[:400]

    return f"""あなたは「まちゃだん」のGM「りりす」。ダークファンタジーTRPGの世界を描写する。

【世界観】男性が絶滅した世界。プレイヤーは唯一の男性。ヒロインたちは本能的にプレイヤーに惹かれる。
【トーン】絶望レッド（赤太字）で危機を、淫靡ピンクで快感を表現。EXモード全開。
【ダイス判定】今回のダイス: 2d6={dice_total} {dice_detail}
  - 10以上: 大成功  - 7-9: 成功  - 4-6: 失敗  - 3以下: ファンブル

【ステータス】{status_text[:400] if status_text else '初期状態'}
【所持品】{inventory_text[:200] if inventory_text else 'なし'}

【出力ルール】純粋なJSON文字列のみ返せ。```jsonブロック禁止。
{{
    "situation_text": "情景描写（HTMLタグ使用可）",
    "ui_html": "<button class='choice-btn' onclick='sendAction(\\\"行動\\\")'>選択肢</button> を複数生成",
    "image_prompt": "英語のComfyUI画像プロンプト。1girl, dark fantasy等",
    "voice_text": "りりすのセリフ（日本語30文字以内）"
}}"""


class ActionWatcher(FileSystemEventHandler):
    """player_action.json だけを監視。他のファイル変更は完全無視。"""
    def __init__(self):
        super().__init__()
        self._last = 0.0

    def on_modified(self, event):
        global _processing

        # ★ player_action.json 以外は完全無視
        if not event.src_path.replace("\\", "/").endswith("player_action.json"):
            return

        # ★ 処理中なら無視（ループ防止の最重要ガード）
        with _processing_lock:
            if _processing:
                log.debug("⏭️ 処理中のため無視")
                return

        # デバウンス（2秒以内の重複イベントを無視）
        now = time.time()
        if now - self._last < 2.0:
            return
        self._last = now

        log.info("🔄 player_action.json 更新検知")
        threading.Thread(target=process_turn, daemon=True).start()


def process_turn():
    """1ターン分の処理を実行"""
    global _processing
    with _processing_lock:
        if _processing:
            return
        _processing = True

    try:
        # 1. アクション読み込み
        with open(ACTION_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        action = data.get("action", "")
        log.info("🎮 アクション: %s", action)

        if action in ("standby", ""):
            return

        # 2. ダイス
        dice_total, dice_detail = roll_2d6()
        log.info("🎲 ダイス: %s %s", dice_total, dice_detail)

        # 3. Gemini API
        llm = call_gemini(action, dice_total, dice_detail)
        if llm is None:
            return

        log.info("✅ LLM応答取得完了")

        # 4. ComfyUI（非同期、失敗しても続行）
        img_prompt = llm.get("image_prompt", "")
        if img_prompt:
            threading.Thread(target=send_comfyui, args=(img_prompt,), daemon=True).start()

        # 5. VOICEVOX（非同期、失敗しても続行）
        voice = llm.get("voice_text", "")
        if voice:
            threading.Thread(target=send_voicevox, args=(voice,), daemon=True).start()

        # 6. シーン書き出し
        scene = {
            "situation_text": llm.get("situation_text", ""),
            "ui_html": llm.get("ui_html", ""),
            "image_prompt": img_prompt,
            "voice_text": voice,
            "dice_result": f"{dice_total} {dice_detail}",
            "generated_at": time.time(),
        }
        with open(SCENE_FILE, "w", encoding="utf-8") as f:
            json.dump(scene, f, ensure_ascii=False, indent=4)
        log.info("📄 index_scene.json 書き出し完了")

        # 7. ステータス更新
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump({"updated_at": time.time(), "state": "ready"}, f, ensure_ascii=False)
        log.info("✅ status.json 更新完了")

    except Exception as e:
        log.error("❌ process_turn エラー: %s", e)
        # エラーでもシーンにフィードバック
        try:
            with open(SCENE_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "situation_text": f"<span style='color:red'>【エラー】{e}</span>",
                    "ui_html": "<button class='choice-btn' onclick='sendAction(\"再試行\")'>再試行</button>",
                    "image_prompt": "", "voice_text": "",
                    "dice_result": "", "generated_at": time.time(),
                }, f, ensure_ascii=False, indent=4)
            with open(STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump({"updated_at": time.time(), "state": "error"}, f, ensure_ascii=False)
        except Exception:
            pass
    finally:
        with _processing_lock:
            _processing = False


def call_gemini(action, dice_total, dice_detail):
    api_key = os.environ.get("GGEMINI_API_KEY", "")
    if not api_key:
        log.error("❌ GGEMINI_API_KEY 未設定")
        return None
    try:
        client = genai.Client(api_key=api_key)
        prompt = build_system_prompt(dice_total, dice_detail)
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"プレイヤーのアクション: {action}",
            config=genai.types.GenerateContentConfig(
                system_instruction=prompt,
                temperature=0.85,
                response_mime_type="application/json",
            ),
        )
        return json.loads(resp.text)
    except Exception as e:
        log.error("❌ Gemini API エラー: %s", e)
        return None


def send_comfyui(prompt):
    log.info("🎨 ComfyUI: %s", prompt[:50])
    try:
        wf_path = os.path.join(ROOT, "00_Core_Engine", "Unsaved Workflow.json")
        if not os.path.exists(wf_path):
            log.warning("⚠️ ワークフロー未発見")
            return
        with open(wf_path, "r", encoding="utf-8") as f:
            wf = json.load(f)
        # ノード16にプロンプト注入（フォールバック: ノード6）
        target = COMFYUI_NODE if COMFYUI_NODE in wf else "6"
        if target in wf:
            wf[target]["inputs"]["text"] = prompt
        if "3" in wf:
            wf["3"]["inputs"]["seed"] = random.randint(0, 2**53)
        r = requests.post(COMFYUI_URL, json={"prompt": wf}, timeout=10)
        log.info("✅ ComfyUI 送信完了: %s", r.status_code)
    except requests.ConnectionError:
        log.warning("⚠️ ComfyUI 未起動（スキップ）")
    except Exception as e:
        log.warning("⚠️ ComfyUI エラー: %s", e)


def send_voicevox(text):
    log.info("🎙️ VOICEVOX: %s", text[:30])
    try:
        r1 = requests.post(f"{VOICEVOX_URL}/audio_query",
                           params={"text": text, "speaker": 3}, timeout=10)
        if r1.status_code != 200:
            log.warning("⚠️ VOICEVOX query失敗: %s", r1.status_code)
            return
        r2 = requests.post(f"{VOICEVOX_URL}/synthesis",
                           params={"speaker": 3}, json=r1.json(), timeout=30)
        if r2.status_code == 200:
            os.makedirs(os.path.dirname(VOICE_OUT), exist_ok=True)
            with open(VOICE_OUT, "wb") as f:
                f.write(r2.content)
            log.info("✅ 音声保存完了")
    except requests.ConnectionError:
        log.warning("⚠️ VOICEVOX 未起動（スキップ）")
    except Exception as e:
        log.warning("⚠️ VOICEVOX エラー: %s", e)


def main():
    log.info("🚀 ai_hub.py 起動（Watchdog のみ / Flask なし）")

    if not os.path.exists(ACTION_FILE):
        with open(ACTION_FILE, "w", encoding="utf-8") as f:
            json.dump({"action": "standby"}, f, ensure_ascii=False)

    watcher = ActionWatcher()
    observer = Observer()
    observer.schedule(watcher, path=ROOT, recursive=False)
    observer.start()
    log.info("👀 監視開始: %s", ACTION_FILE)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        log.info("🛑 停止")
    observer.join()


if __name__ == "__main__":
    main()
