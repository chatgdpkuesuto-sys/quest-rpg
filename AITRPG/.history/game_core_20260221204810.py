"""
game_core.py — メインゲームループ（心臓部）
入力→GM→描画→音声の非同期パイプラインを統合する。
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
            self._generate_opening()

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
                    if not self.awaiting_choice and not self.generating:
                        # 選択肢なしのシーンでテキスト完了後にエンターで次へ
                        pass
                    continue

                if result in (0, 1, 2) and self.awaiting_choice and not self.generating:
                    # 選択肢が選ばれた
                    self._handle_choice(result)

        except Exception as e:
            print(f"\n[GameCore] エラー: {e}")
            traceback.print_exc()
        finally:
            self._cleanup()

    def _generate_opening(self):
        """オープニングシーンを生成する。"""
        self.renderer.set_loading(True)
        self.generating = True

        def _generate():
            try:
                state = self.state_mgr.state
                context = state.get_context_string()

                # GMにオープニングを要求
                response = self.lm.send(
                    "ゲームを開始する。冒険者が暗黒大陸ノクターナルで目覚めるところから始めてくれ。",
                    context=context,
                )

                # 画像生成と音声生成を並列で開始
                image_path = None
                audio_path = None

                if response["image_prompt"]:
                    image_path = self.comfyui.generate(response["image_prompt"])

                # セリフがあれば音声合成
                voice_text = response["dialogue"] or response["scene"]
                if voice_text:
                    # 長すぎるテキストは冒頭だけ
                    truncated = voice_text[:200]
                    if response["dialogue"]:
                        audio_path = self.voicevox.synthesize_dialogue(truncated)
                    else:
                        audio_path = self.voicevox.synthesize(truncated)

                # レンダラー更新
                self.renderer.set_loading(False)
                self.renderer.set_scene(
                    image_path=str(image_path) if image_path else None,
                    scene_text=response["scene"],
                    dialogue_text=response["dialogue"],
                    choices=response["choices"],
                )

                # 音声再生
                if audio_path:
                    self.renderer.play_audio(str(audio_path))

                # 状態更新
                state.last_scene_text = response["scene"]
                state.last_choices = response["choices"]
                if image_path:
                    state.last_image_path = str(image_path)

                self.awaiting_choice = bool(response["choices"])
                self.generating = False

                # オートセーブ
                self.state_mgr.save()

            except Exception as e:
                print(f"[GameCore] オープニング生成エラー: {e}")
                traceback.print_exc()
                self.renderer.set_loading(False)
                self.renderer.set_scene(
                    scene_text=f"【エラー】シーン生成に失敗しました: {str(e)}",
                    choices=["再試行する", "終了する"],
                )
                self.awaiting_choice = True
                self.generating = False

        # バックグラウンドスレッドで生成
        thread = threading.Thread(target=_generate, daemon=True)
        thread.start()

    def _handle_choice(self, choice_index: int):
        """プレイヤーの選択を処理する。"""
        if self.generating:
            return

        state = self.state_mgr.state
        choices = state.last_choices

        if choice_index >= len(choices):
            return

        chosen_text = choices[choice_index]
        print(f"\n[GameCore] プレイヤー選択: {choice_index + 1}. {chosen_text}")

        # ローディング開始
        self.renderer.set_loading(True)
        self.awaiting_choice = False
        self.generating = True

        def _generate():
            try:
                # シナリオエンジンで分岐/合流制御
                scenario_instruction = self.scenario.process_choice(
                    choice_index, state
                )
                context = state.get_context_string()
                context += f"\n{self.scenario.get_phase_info()}"

                # LLMに選択結果を送信
                user_msg = f"選択肢{choice_index + 1}「{chosen_text}」を選んだ。"
                if scenario_instruction:
                    user_msg += f"\n\n{scenario_instruction}"

                response = self.lm.send(user_msg, context=context)

                # 画像と音声を並列生成
                image_path = None
                audio_path = None

                # 画像生成（別スレッド）
                image_thread = None
                if response["image_prompt"]:
                    def _gen_image():
                        nonlocal image_path
                        image_path = self.comfyui.generate(
                            response["image_prompt"]
                        )
                    image_thread = threading.Thread(target=_gen_image, daemon=True)
                    image_thread.start()

                # 音声生成
                voice_text = response["dialogue"] or response["scene"]
                if voice_text:
                    truncated = voice_text[:200]
                    if response["dialogue"]:
                        audio_path = self.voicevox.synthesize_dialogue(truncated)
                    else:
                        audio_path = self.voicevox.synthesize(truncated)

                # 画像生成の完了を待つ
                if image_thread:
                    image_thread.join(timeout=120)

                # レンダラー更新
                self.renderer.set_loading(False)
                self.renderer.set_scene(
                    image_path=str(image_path) if image_path else None,
                    scene_text=response["scene"],
                    dialogue_text=response["dialogue"],
                    choices=response["choices"],
                )

                # 音声再生
                if audio_path:
                    self.renderer.play_audio(str(audio_path))

                # 状態更新
                state.last_scene_text = response["scene"]
                state.last_choices = response["choices"]
                if image_path:
                    state.last_image_path = str(image_path)

                self.awaiting_choice = bool(response["choices"])
                self.generating = False

                # オートセーブ
                self.state_mgr.save()

                phase = self.scenario.get_phase_info()
                print(f"[GameCore] シーン更新完了 — {phase}")

            except Exception as e:
                print(f"[GameCore] シーン生成エラー: {e}")
                traceback.print_exc()
                self.renderer.set_loading(False)
                self.renderer.set_scene(
                    scene_text=f"【エラー】シーン生成に失敗しました: {str(e)}",
                    choices=["再試行する", "終了する"],
                )
                self.awaiting_choice = True
                self.generating = False

        # バックグラウンドスレッドで生成
        thread = threading.Thread(target=_generate, daemon=True)
        thread.start()

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
