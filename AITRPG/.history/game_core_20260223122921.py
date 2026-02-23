"""
game_core.py — メインゲームループ（心臓部）
入力→GM→描画→音声の非同期パイプラインを統合する。
テキスト先行表示：LLM応答が来たらすぐテキスト表示、画像は後から差し替え。
"""

import sys
import random
import threading
import traceback
from pathlib import Path
from typing import Optional

from lm_client import LMClient
from comfyui_client import ComfyUIClient, SCENE_TEMPLATES
from voicevox_client import VoicevoxClient
from state_manager import StateManager
from scenario_engine import ScenarioEngine
from renderer import Renderer
from d20_engine import Character, D20Engine


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
        self.d20 = D20Engine()

        self.running = True
        self.awaiting_choice = False
        self.generating = False
        
        self.creation_phase = "DONE"
        self.available_souls = []
        self.available_jobs = []
        self._temp_soul = ""
        self._temp_job = ""

        print("[GameCore] 初期化完了\n")

    def _show_soul_selection(self):
        """UI上で魂カードを選択させる"""
        self.creation_phase = "SOUL"
        self.available_souls = random.sample(["孫悟空", "フリーレン", "ルフィ", "キリト", "アーニャ"], 3)
        msg = "【キャラクターメイキング（1/2）】\n\nあなたの『魂』となるキャラクターを３つのカードから選んでください。"
        
        def _gen_audio():
            try:
                text = "あなたの魂となるキャラクターを選んでください。"
                audio_path = self.voicevox.synthesize(text)
                if audio_path: self.renderer.play_audio(str(audio_path))
            except: pass
        threading.Thread(target=_gen_audio, daemon=True).start()

        self.renderer.set_loading(False)
        self.renderer.set_scene(scene_text=msg, choices=self.available_souls)
        self.state_mgr.state.last_choices = self.available_souls
        self.awaiting_choice = True

    def _show_job_selection(self):
        """UI上でジョブカードを選択させる"""
        self.creation_phase = "JOB"
        self.available_jobs = random.sample(["戦士", "魔法使い", "盗賊", "僧侶"], 3)
        msg = f"【キャラクターメイキング（2/2）】\n\nあなたは『{self._temp_soul}』の魂に適合しました。\n次に、この世界で就く『職業』を３つのジョブカードから選んでください。"
        
        def _gen_audio():
            try:
                text = "あなたは適合しました。次に、この世界で就く職業を選んでください。"
                audio_path = self.voicevox.synthesize(text)
                if audio_path: self.renderer.play_audio(str(audio_path))
            except: pass
        threading.Thread(target=_gen_audio, daemon=True).start()

        self.renderer.set_loading(False)
        self.renderer.set_scene(scene_text=msg, choices=self.available_jobs)
        self.state_mgr.state.last_choices = self.available_jobs
        self.awaiting_choice = True

    def run(self):
        """メインゲームループ。"""
        try:
            # キャラ作成フェーズ開始
            self._show_soul_selection()

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
                char_data = None
                if state.character:
                    c = state.character
                    char_data = {
                        "soul": c.soul_card,
                        "job": c.job_card,
                        "hp": state.hp,
                        "max_hp": state.max_hp,
                        "ac": c.ac,
                        "STR": c.get_modifier("STR"),
                        "DEX": c.get_modifier("DEX"),
                        "CON": c.get_modifier("CON"),
                        "INT": c.get_modifier("INT"),
                        "WIS": c.get_modifier("WIS"),
                        "CHA": c.get_modifier("CHA"),
                        "skills": ", ".join(c.skills)
                    }

                self.renderer.set_loading(False)
                self.renderer.set_scene(
                    image_path=None,
                    scene_text=response["scene"],
                    dialogue_text=response["dialogue"],
                    choices=response["choices"],
                    character_info=char_data
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

                # 会話からキャラのポーズを推測
                best_pose = self._guess_chara_pose(response["dialogue"], response["scene"])

                # ステップ4: シーンに合わせて背景と小物を即座に表示、キャラはライブラリから仮表示
                def _pick_image():
                    try:
                        bg_path = self._pick_scene_image(response["scene"])
                        chara_path = self._pick_chara_image(response["dialogue"], response["scene"])
                        prop_path = self._pick_prop_image(response["scene"])

                        if bg_path:
                            state.last_image_path = str(bg_path)
                            self.renderer.set_scene(
                                image_path=str(bg_path),
                                chara_path=str(chara_path) if chara_path else None,
                                prop_path=str(prop_path) if prop_path else None,
                                scene_text=response["scene"],
                                dialogue_text=response["dialogue"],
                                choices=response["choices"],
                                character_info=char_data
                            )
                    except Exception as e:
                        print(f"[GameCore] 画像選択エラー: {e}")

                _pick_image()  # 即座に選択（ファイルから読むだけなので高速）

                # ステップ5: キャラクターの立ち絵のみコンテキストに沿って裏でリアルタイム生成
                if response["dialogue"] and best_pose:
                    def _gen_chara():
                        try:
                            new_path = self.comfyui.generate_character(best_pose)
                            if new_path:
                                self.renderer.update_chara(str(new_path))
                        except Exception as e:
                            print(f"[GameCore] キャラ生成スレッドエラー: {e}")

                    # 音声生成とは別のスレッドで立ち上げる
                    threading.Thread(target=_gen_chara, daemon=True).start()

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

    # シーンテキストのキーワード → 画像ファイル名のマッピング
    SCENE_KEYWORDS = {
        "town_square": ["街", "町", "広場", "市場"],
        "tavern_inside": ["酒場", "宿", "居酒屋", "バー", "食事"],
        "castle_hall": ["城", "宮殿", "玉座", "王"],
        "shop": ["店", "商人", "買い物", "道具"],
        "church": ["教会", "神殿", "祈り", "聖"],
        "guild_hall": ["ギルド", "冒険者", "依頼", "受付"],
        "forest": ["森", "林", "木々", "草原"],
        "forest_night": ["夜の森", "暗い森"],
        "mountain": ["山", "峠", "崖", "高台"],
        "river": ["川", "河", "橋", "水辺"],
        "flower_field": ["花", "花畑", "草花"],
        "beach": ["海", "浜", "砂浜", "波"],
        "dungeon_entrance": ["入口", "門", "ダンジョン入"],
        "dungeon_corridor": ["通路", "廊下", "地下", "ダンジョン"],
        "crystal_cave": ["洞窟", "鍾乳洞", "水晶", "クリスタル"],
        "ruins": ["遺跡", "廃墟", "古代"],
        "treasure_room": ["宝", "財宝", "金貨"],
        "campfire": ["焚き火", "キャンプ", "野営", "休憩"],
        "battle_field": ["戦場", "戦い", "戦闘", "敵"],
        "magic_circle": ["魔法陣", "呪文", "魔力", "召喚"],
        "girl_adventurer": ["冒険者の少女", "剣士", "戦士"],
        "girl_mage": ["魔法使い", "魔女", "杖"],
        "girl_healer": ["治療", "回復", "癒し", "僧侶"],
        "mysterious_npc": ["謎の人物", "フード", "占い"],
        "sunrise": ["朝", "日の出", "夜明け", "目覚め"],
        "night_sky": ["夜空", "星", "月", "夜"],
        "rain": ["雨", "嵐", "雷"],
        "snow": ["雪", "冬", "吹雪", "寒い"],
    }

    def _pick_scene_image(self, scene_text: str) -> Optional[Path]:
        """シーンテキストからキーワードマッチで最適な画像を選ぶ。"""
        image_dir = Path(__file__).parent / "assets" / "generated"

        if not image_dir.exists():
            return None

        # キーワードマッチでスコアリング
        best_name = None
        best_score = 0

        for filename, keywords in self.SCENE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in scene_text)
            if score > best_score:
                best_score = score
                best_name = filename

        # マッチしたファイルが存在するか確認
        if best_name:
            path = image_dir / f"{best_name}.png"
            if path.exists():
                return path

        # マッチしなかった場合、ランダムに1枚選ぶ
        available = list(image_dir.glob("*.png"))
        if available:
            return random.choice(available)

        return None

    # キャラ立ち絵のキーワードマッピング
    CHARA_KEYWORDS = {
        "smile":     ["微笑", "ふふ", "笑", "優し"],
        "serious":   ["真剣", "静か", "冷た", "見つめ"],
        "surprised": ["驚", "えっ", "なっ", "目を見開"],
        "sad":       ["悲し", "俯", "うつむ", "申し訳"],
        "blush":     ["赤面", "照れ", "恥ず", "目を逸ら"],
        "attack":    ["詠唱", "魔法", "攻撃", "放つ", "杖を構え"],
        "back":      ["背を向", "去って", "後ろ姿"],
        "look_back": ["振り返", "肩越"],
    }

    def _guess_chara_pose(self, dialogue_text: str, scene_text: str) -> Optional[str]:
        """テキストから立ち絵のポーズ（キーワード）を推測する。"""
        if not dialogue_text:
            return None

        target_text = dialogue_text + " " + scene_text
        best_name = "smile"  # デフォルト
        best_score = 0

        for pose_name, keywords in self.CHARA_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in target_text)
            if score > best_score:
                best_score = score
                best_name = pose_name
                
        return best_name

    def _pick_chara_image(self, dialogue_text: str, scene_text: str) -> Optional[Path]:
        """テキストから立ち絵画像を推測して選出する。"""
        best_name = self._guess_chara_pose(dialogue_text, scene_text)
        if not best_name:
            return None

        image_dir = Path(__file__).parent / "assets" / "characters"
        if not image_dir.exists():
            return None

        path = image_dir / f"elf_{best_name}.png"
        if path.exists():
            return path
        
        # なければランダムに
        available = list(image_dir.glob("elf_*.png"))
        if available:
            return random.choice(available)
            
        return None

    # 小物のキーワードマッピング
    PROP_KEYWORDS = {
        "grass": ["草原", "野外", "草", "原野"],
        "table": ["酒場", "居酒屋", "食事", "宿"],
        "desk": ["ギルド", "受付", "執務室", "書斎"],
        "signboard": ["街", "町", "市場", "広場", "店"],
        "bushes": ["森", "茂み", "川", "山", "林", "木々"],
        "magic_circle_ground": ["魔法陣", "召喚", "遺跡"],
        "crystals": ["洞窟", "水晶", "クリスタル", "地下"],
        "window_frame": ["城", "室内", "部屋", "宮殿"],
    }

    def _pick_prop_image(self, scene_text: str) -> Optional[Path]:
        """テキストから状況に合う手前小物（プロップ）を選出する。"""
        image_dir = Path(__file__).parent / "assets" / "props"
        if not image_dir.exists():
            return None

        best_name = None
        best_score = 0

        for prop_name, keywords in self.PROP_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in scene_text)
            if score > best_score:
                best_score = score
                best_name = prop_name

        if best_name:
            path = image_dir / f"prop_{best_name}.png"
            if path.exists():
                return path

        return None

    def _determine_roll(self, action_text: str) -> str:
        """選択肢のテキストから、振るべきダイス判定を推測し実行する"""
        state = self.state_mgr.state
        if not state.character:
            return ""
            
        pc = state.character
        action = action_text.lower()
        
        # 簡易キーワードマッチで判定ステータスとDC/ACを決定
        if any(kw in action for kw in ["攻撃", "剣", "斬", "殴", "叩"]):
            # STR近接攻撃とみなす
            res = self.d20.attack_roll(pc, "STR", ac=13, weapon_damage_dice="1d8")
            if res["hit_check"]["success"]:
                return f"\n[システムダイス結果]\nSTR攻撃判定: {res['hit_check']['detail']}\n-> 命中！\nダメージ: {res['damage_detail']}"
            else:
                return f"\n[システムダイス結果]\nSTR攻撃判定: {res['hit_check']['detail']}\n-> ミス！"
                
        elif any(kw in action for kw in ["魔法", "詠唱", "炎", "氷"]):
            # INT魔法攻撃とみなす
            res = self.d20.attack_roll(pc, "INT", ac=12, weapon_damage_dice="3d6")
            if res["hit_check"]["success"]:
                return f"\n[システムダイス結果]\nINT魔法判定: {res['hit_check']['detail']}\n-> 命中！\nダメージ: {res['damage_detail']}"
            else:
                return f"\n[システムダイス結果]\nINT魔法判定: {res['hit_check']['detail']}\n-> ミス！"
                
        elif any(kw in action for kw in ["避ける", "逃げる", "隠れる", "弓", "盗"]):
            # DEX判定
            res = self.d20.skill_check(pc, "DEX", dc=12)
            return f"\n[システムダイス結果]\nDEX判定: {res['detail']} -> {'成功！' if res['success'] else '失敗...'}"
            
        elif any(kw in action for kw in ["説得", "交渉", "威圧", "嘘"]):
            # CHA判定
            res = self.d20.skill_check(pc, "CHA", dc=14)
            return f"\n[システムダイス結果]\nCHA交渉判定: {res['detail']} -> {'成功！' if res['success'] else '失敗...'}"
            
        elif any(kw in action for kw in ["探す", "観察", "調べる"]):
            # WIS/INT判定
            res = self.d20.skill_check(pc, "INT", dc=10)
            return f"\n[システムダイス結果]\nINT調査判定: {res['detail']} -> {'成功！' if res['success'] else '失敗...'}"
            
        # 該当しない場合はダイスなし
        return ""

    def _handle_choice(self, choice_index: int):
        """プレイヤーの選択を処理する。"""
        state = self.state_mgr.state
        choices = state.last_choices

        if choice_index >= len(choices):
            return

        chosen_text = choices[choice_index]
        print(f"\n[GameCore] プレイヤー選択: {choice_index + 1}. {chosen_text}")

        # キャラ作成フェーズの判定
        if self.creation_phase != "DONE":
            if self.creation_phase == "SOUL":
                self._temp_soul = self.available_souls[choice_index]
                self._show_job_selection()
            elif self.creation_phase == "JOB":
                self._temp_job = self.available_jobs[choice_index]
                self.creation_phase = "DONE"
                
                # キャラ確定
                pc = Character(self._temp_soul, self._temp_job)
                state.character = pc
                print(f"[GameCore] キャラクター確定: {self._temp_soul} × {self._temp_job}")
                
                intro_msg = f"プレイヤーは『{self._temp_soul}の魂』を持ち『{self._temp_job}の職業』に就いた冒険者として、暗黒大陸ノクターナルで目覚めるところから始めてくれ。"
                self._generate_scene(intro_msg)
            return

        # 裏でダイスを振る
        dice_result_text = self._determine_roll(chosen_text)
        if dice_result_text:
            print(dice_result_text)

        # シナリオエンジンで分岐/合流制御
        scenario_instruction = self.scenario.process_choice(choice_index, state)
        phase = self.scenario.get_phase_info()
        print(f"[GameCore] {phase}")
        
        # ダイス結果があれば、GMへの指示に追加する
        if dice_result_text:
            scenario_instruction += f"\n\n絶対厳守: 次のダイス判定結果に従って情景を描写すること。結果を無視・改変してはならない。\n{dice_result_text}"

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
