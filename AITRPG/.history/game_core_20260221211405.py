"""
game_core.py — メインゲームループ（心臓部）
入力→GM→描画→音声の非同期パイプラインを統合する。
テキスト先行表示：LLM応答が来たらすぐテキスト表示、画像は後から差し替え。
"""

import sys
import threading
import traceback
from pathlib import Path
from typing import Optional

from lm_client import LMClient
from comfyui_client import ComfyUIClient
from voicevox_client import VoicevoxClient
from state_manager import StateManager
from scenario_engine import ScenarioEngine
from renderer import Renderer


class GameCore:
    """メインゲームエンジン。全モジュールを統合して駆動する。"""

    def __init__(self):
        print("=" * 50)
        print("  NOCTURNAL — 暗黒幻想VRMMO")
        print("  分岐合流型リアルタイムTRPGエンジン")
        print("=" * 50)
        print("\n[GameCore] 初期化中...")

        self.lm = LMClient()
        self.comfyui = ComfyUIClient()
        self.voicevox = VoicevoxClient()
        self.state_mgr = StateManager()
        self.scenario = ScenarioEngine()
        self.renderer = Renderer()

        self.running = True
        self.awaiting_choice = False
        self.generating = False

        print("[GameCore] 初期化完了\n")

    def run(self):
        """メインゲームループ。"""
        try:
            # オープニングシーンを生成
            self._generate_scene(
                "ゲームを開始する。冒険者が暗黒大陸ノクターナルで目覚めるところから始めてくれ。"
            )

            # メインループ
            while self.running:
                result = self.renderer.render()

                if result is None:
                    continue

                if result == -1:
                    # ESC/終了要求
                    self.running = False
                    break

                if result == -2:
                    # テキスト送り（スペース/エンター）
                    continue

                if result in (0, 1, 2) and self.awaiting_choice and not self.generating:
                    # 選択肢が選ばれた
                    self._handle_choice(result)

        except Exception as e:
            print(f"\n[GameCore] エラー: {e}")
            traceback.print_exc()
        finally:
            self._cleanup()

    def _generate_scene(self, user_message: str, scenario_instruction: str = ""):
        """
        シーンを生成する。テキストを先に表示し、画像と音声は後から更新。
        """
        if self.generating:
            return

        self.renderer.set_loading(True)
        self.awaiting_choice = False
        self.generating = True

        def _generate():
            try:
                state = self.state_mgr.state
                context = state.get_context_string()

                if scenario_instruction:
                    context += f"\n{self.scenario.get_phase_info()}"

                # 送信メッセージ構築
                full_msg = user_message
                if scenario_instruction:
                    full_msg += f"\n\n{scenario_instruction}"

                print(f"[GameCore] LLMにリクエスト送信中...")

                # ステップ1: LLM応答を取得
                response = self.lm.send(full_msg, context=context)

                print(f"[GameCore] LLM応答受信！テキスト先行表示")

                # ステップ2: テキストを即座に表示（画像なしで先行表示）
                self.renderer.set_loading(False)
                self.renderer.set_scene(
                    image_path=None,
                    scene_text=response["scene"],
                    dialogue_text=response["dialogue"],
                    choices=response["choices"],
                )

                # 状態更新
                state.last_scene_text = response["scene"]
                state.last_choices = response["choices"]
                self.awaiting_choice = bool(response["choices"])
                self.generating = False

                # ステップ3: 音声を非同期で生成・再生
                voice_text = response["dialogue"] or response["scene"]
                if voice_text:
                    def _gen_audio():
                        try:
                            truncated = voice_text[:200]
                            if response["dialogue"]:
                                audio_path = self.voicevox.synthesize_dialogue(truncated)
                            else:
                                audio_path = self.voicevox.synthesize(truncated)
                            if audio_path:
                                self.renderer.play_audio(str(audio_path))
                        except Exception as e:
                            print(f"[GameCore] 音声生成エラー: {e}")

                    threading.Thread(target=_gen_audio, daemon=True).start()

                # ステップ4: 画像を非同期で生成・差し替え
                if response["image_prompt"]:
                    def _gen_image():
                        try:
                            image_path = self.comfyui.generate(response["image_prompt"])
                            if image_path:
                                state.last_image_path = str(image_path)
                                # 画像を後から差し替え（テキストや選択肢はそのまま）
                                self.renderer.set_scene(
                                    image_path=str(image_path),
                                    scene_text=response["scene"],
                                    dialogue_text=response["dialogue"],
                                    choices=response["choices"],
                                )
                                print(f"[GameCore] 画像差し替え完了！")
                        except Exception as e:
                            print(f"[GameCore] 画像生成エラー: {e}")

                    threading.Thread(target=_gen_image, daemon=True).start()

                # オートセーブ
                self.state_mgr.save()
                print(f"[GameCore] シーン表示完了")

            except Exception as e:
                print(f"[GameCore] シーン生成エラー: {e}")
                traceback.print_exc()
                self.renderer.set_loading(False)
                self.renderer.set_scene(
                    scene_text=f"【エラー】シーン生成に失敗しました: {str(e)}",
                    choices=["再試行する", "設定を確認する", "終了する"],
                )
                self.awaiting_choice = True
                self.generating = False

        # バックグラウンドスレッドで生成
        thread = threading.Thread(target=_generate, daemon=True)
        thread.start()

    def _handle_choice(self, choice_index: int):
        """プレイヤーの選択を処理する。"""
        state = self.state_mgr.state
        choices = state.last_choices

        if choice_index >= len(choices):
            return

        chosen_text = choices[choice_index]
        print(f"\n[GameCore] プレイヤー選択: {choice_index + 1}. {chosen_text}")

        # シナリオエンジンで分岐/合流制御
        scenario_instruction = self.scenario.process_choice(choice_index, state)
        phase = self.scenario.get_phase_info()
        print(f"[GameCore] {phase}")

        # LLMに選択結果を送信
        user_msg = f"選択肢{choice_index + 1}「{chosen_text}」を選んだ。"

        self._generate_scene(user_msg, scenario_instruction)

    def _cleanup(self):
        """終了処理。"""
        print("\n[GameCore] 終了処理中...")
        self.state_mgr.save()
        self.renderer.cleanup()
        print("[GameCore] ゲーム終了。お疲れ様でした。")


def main():
    """エントリーポイント。"""
    game = GameCore()
    game.run()


if __name__ == "__main__":
    main()
