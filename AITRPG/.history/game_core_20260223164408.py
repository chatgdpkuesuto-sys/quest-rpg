import json
import time
import threading
import sys
import traceback
from pathlib import Path
from typing import Optional, Union

from renderer import Renderer
from voicevox_client import VoicevoxClient
from comfyui_client import ComfyUIClient

DATA_DIR = Path(__file__).parent / "data"
STATE_FILE = DATA_DIR / "game_state.json"
ACTION_FILE = DATA_DIR / "player_action.json"

class GameFrontEnd:
    """JSONファイル(game_state.json)を非同期監視し、Pygame画面と音声を更新するフロントエンド"""

    def __init__(self):
        print("=" * 50)
        print("  ANIME CROSS DUNGEONS - FRONTEND (Antigravity GM)")
        print("=" * 50)
        print("[FrontEnd] 初期化中...")

        DATA_DIR.mkdir(exist_ok=True)
        self.renderer = Renderer()
        self.voicevox = VoicevoxClient()
        self.comfyui = ComfyUIClient()

        self.running = True
        self.last_state_text = ""
        self.current_state = {}
        self.awaiting_choice = False

        self._init_files()
        print("[FrontEnd] 初期化完了. GM(Antigravity)からの応答を待機します...\n")

    def _init_files(self):
        """起動時のファイル初期化"""
        if not STATE_FILE.exists():
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "mode": "START",
                    "scene_text": "【読み込み中...】\n\n管理者（Antigravity）からの初期データ到着を待機しています...",
                    "choices": [],
                    "bg_image_path": "",
                    "chara_image_path": "",
                    "prop_image_path": "",
                    "bgm_path": "",
                    "voice_path": "",
                    "party_info": []
                }, f, ensure_ascii=False, indent=2)
                
        # 起動直後はアクションをリセット
        with open(ACTION_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "latest_action": "",
                "latest_choice_index": -1,
                "timestamp": 0
            }, f, ensure_ascii=False, indent=2)

    def _state_watcher_loop(self):
        """別スレッドで game_state.json の更新を監視する"""
        while self.running:
            try:
                if STATE_FILE.exists():
                    with open(STATE_FILE, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    # ファイルの中身が変わった時だけUI更新要求を出す
                    if content != self.last_state_text and content.strip():
                        try:
                            state = json.loads(content)
                            self.current_state = state
                            self.last_state_text = content
                            self._apply_state(state)
                        except json.JSONDecodeError:
                            # GM（私）が手作業で書き換え中の場合はスキップ
                            pass
                            
            except Exception as e:
                print(f"[Watcher] エラー: {e}")
                
            time.sleep(0.5)  # 0.5秒おきにチェック

    def _apply_state(self, state: dict):
        """読み込んだ state の内容を Renderer や Audio 等に反映する"""
        scene_text = state.get("scene_text", "")
        choices = state.get("choices", [])
        bg_path = state.get("bg_image_path")
        chara_path = state.get("chara_image_path")
        prop_path = state.get("prop_image_path")
        party_info = state.get("party_info", [])
        
        # 音声の自動生成（テキストベースでの簡易再生、パス直指定も可能にする）
        voice_path = state.get("voice_path")
        voice_text = state.get("dialogue_text", "") # 新たにセリフだけ喋らせる枠

        print("\n=== [FrontEnd] UI更新を受信 ===")

        # 1. 描画の更新
        # ローディングを解除
        self.renderer.set_loading(False)
        self.renderer.set_scene(
            image_path=bg_path if bg_path else None,
            chara_path=chara_path if chara_path else None,
            prop_path=prop_path if prop_path else None,
            scene_text=scene_text,
            dialogue_text=voice_text,
            choices=choices,
            party_info=party_info
        )
        
        self.awaiting_choice = bool(choices)
        
        # 2. 音声再生の非同期処理
        if voice_path and Path(voice_path).exists():
            self.renderer.play_audio(voice_path)
        elif voice_text:
            def _gen_audio():
                try:
                    path = self.voicevox.synthesize_dialogue(voice_text[:200])
                    if path:
                        self.renderer.play_audio(str(path))
                except Exception as e:
                    print(f"[Audio] 音声生成エラー: {e}")
            threading.Thread(target=_gen_audio, daemon=True).start()

    def _write_action(self, action_val: Union[int, str]):
        """選ばれた選択肢または入力テキストを player_action.json に書き出し、GMの応答を待つ"""
        choices = self.current_state.get("choices", [])
        
        if isinstance(action_val, int):
            if action_val < 0 or action_val >= len(choices):
                return
            action_text = choices[action_val]
            choice_index = action_val
        else:
            action_text = str(action_val).strip()
            choice_index = -1
            
        print(f"\n[FrontEnd] プレイヤー行動送信: {action_text}")
        
        action_data = {
            "latest_action": action_text,
            "latest_choice_index": choice_index,
            "timestamp": time.time()
        }
        
        try:
            with open(ACTION_FILE, "w", encoding="utf-8") as f:
                json.dump(action_data, f, ensure_ascii=False, indent=2)
                
            # 即座に待機状態を表示する
            self.renderer.set_loading(True)
            self.awaiting_choice = False
        except Exception as e:
            print(f"[FrontEnd] アクション送信失敗: {e}")

    def run(self):
        # 監視スレッドの開始
        watcher_thread = threading.Thread(target=self._state_watcher_loop, daemon=True)
        watcher_thread.start()

        # メインフレームループ（Pygameのイベント処理と描画）
        try:
            while self.running:
                result = self.renderer.render()
                
                if result is None:
                    continue
                if result == -1: # ウィンドウの×ボタン
                    self.running = False
                    break
                if result == -2: # ただのテキストスキップなど
                    continue
                    
                # 選択肢ボタンが押された、またはテキスト入力が確定された場合
                if result is not None and result != -1 and result != -2 and self.awaiting_choice:
                    self._write_action(result)
                    
        except Exception as e:
            print(f"\n[FrontEnd] エラー: {e}")
            traceback.print_exc()
        finally:
            print("\n[FrontEnd] 終了処理中...")
            self.running = False
            self.renderer.cleanup()
            print("[FrontEnd] ゲーム終了。")

def main():
    app = GameFrontEnd()
    app.run()

if __name__ == "__main__":
    main()
