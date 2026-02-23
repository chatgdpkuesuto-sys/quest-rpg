"""
game_core.py — メインゲームループ（パーティー指揮官版）
プレイヤーは指揮官。3人の仲間を選び、命令して冒険を進める。
"""

import sys
import random
import threading
import traceback
from pathlib import Path
from typing import Optional, List

from lm_client import LMClient
from comfyui_client import ComfyUIClient, SCENE_TEMPLATES
from voicevox_client import VoicevoxClient
from state_manager import StateManager
from scenario_engine import ScenarioEngine
from renderer import Renderer
from d20_engine import Character, D20Engine, SOUL_CARDS, JOB_CARDS, SKILL_DB, UNIVERSAL_SKILLS


class GameCore:
    """メインゲームエンジン（パーティー指揮官版）"""

    def __init__(self):
        print("=" * 50)
        print("  ANIME CROSS DUNGEONS")
        print("  パーティー指揮官モード")
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

        # キャラ作成フェーズ管理
        self.creation_phase = "DONE"  # MEMBER_1, MEMBER_2, MEMBER_3, JOB_1, JOB_2, JOB_3, SKILL_x, DONE
        self.remaining_souls: List[str] = []
        self.current_soul_picks: List[str] = []
        self.current_job_picks: List[str] = []
        self._building_party: List[dict] = []  # {soul, job, job_skill, universal_skill}
        self._current_member_idx: int = 0
        self._available_skills_list: List[str] = []

        print("[GameCore] 初期化完了\n")

    # =================================================================
    #  キャラクターメイキング（UIの3択で進行）
    # =================================================================

    def _start_member_selection(self, member_num: int):
        """仲間N人目の魂カード選択画面を表示"""
        self.creation_phase = f"MEMBER_{member_num}"
        self._current_member_idx = member_num

        # 残りの魂カードから3枚をランダム表示
        picks = random.sample(self.remaining_souls, min(3, len(self.remaining_souls)))
        self.current_soul_picks = picks

        msg = f"【パーティー編成（{member_num}/3）】\n\nあなたの{member_num}人目の仲間を選んでください。"
        for i, name in enumerate(picks):
            soul = SOUL_CARDS[name]
            msg += f"\n\n{i+1}. {name}（{soul['origin']}）"
            msg += f"\n   性格: {soul['personality']} / 従順度: {soul['obedience']}"

        self._show_creation_screen(msg, picks)

    def _start_job_selection(self, member_num: int):
        """仲間N人目のジョブカード選択画面"""
        self.creation_phase = f"JOB_{member_num}"
        self._current_member_idx = member_num

        soul_name = self._building_party[member_num - 1]["soul"]
        jobs = list(JOB_CARDS.keys())
        picks = random.sample(jobs, 3)
        self.current_job_picks = picks

        msg = f"【{soul_name}のジョブ選択】\n\n{soul_name}に就かせる職業を選んでください。"
        for i, jname in enumerate(picks):
            j = JOB_CARDS[jname]
            msg += f"\n\n{i+1}. {j['emoji']}{jname}（HP:{j['base_hp']}+CON / AC:{j['ac']}）"

        self._show_creation_screen(msg, [f"{JOB_CARDS[j]['emoji']}{j}" for j in picks])

    def _start_job_skill_selection(self, member_num: int):
        """仲間N人目のジョブスキル選択画面"""
        self.creation_phase = f"JSKILL_{member_num}"
        self._current_member_idx = member_num

        info = self._building_party[member_num - 1]
        job = info["job"]
        all_skills = list(SKILL_DB.get(job, {}).keys())
        picks = random.sample(all_skills, min(3, len(all_skills)))
        self._available_skills_list = picks

        msg = f"【{info['soul']}({job})のジョブスキル】\n\n習得するジョブスキルを１つ選んでください。"
        for i, sname in enumerate(picks):
            sdata = SKILL_DB[job][sname]
            msg += f"\n\n{i+1}. {sname}（{sdata['type']}）\n   {sdata['desc']}"
            if sdata.get('limit', 'なし') != 'なし':
                msg += f" [{sdata['limit']}]"

        self._show_creation_screen(msg, picks)

    def _start_universal_skill_selection(self, member_num: int):
        """仲間N人目の汎用スキル選択画面"""
        self.creation_phase = f"USKILL_{member_num}"
        self._current_member_idx = member_num

        info = self._building_party[member_num - 1]
        all_uni = list(UNIVERSAL_SKILLS.keys())
        picks = random.sample(all_uni, min(3, len(all_uni)))
        self._available_skills_list = picks

        msg = f"【{info['soul']}({info['job']})の汎用スキル】\n\n習得する汎用スキルを１つ選んでください。"
        for i, sname in enumerate(picks):
            sdata = UNIVERSAL_SKILLS[sname]
            msg += f"\n\n{i+1}. {sname}（{sdata['type']}）\n   {sdata['desc']}"

        self._show_creation_screen(msg, picks)

    def _show_creation_screen(self, msg: str, choices: List[str]):
        """キャラ作成画面を表示"""
        self.renderer.set_loading(False)
        self.renderer.set_scene(scene_text=msg, choices=choices)
        self.state_mgr.state.last_choices = choices
        self.awaiting_choice = True

    def _handle_creation_choice(self, choice_index: int) -> bool:
        """キャラ作成フェーズの選択処理。処理したらTrue."""
        if self.creation_phase == "DONE":
            return False

        phase = self.creation_phase

        if phase.startswith("MEMBER_"):
            num = int(phase.split("_")[1])
            chosen_soul = self.current_soul_picks[choice_index]
            self.remaining_souls.remove(chosen_soul)
            self._building_party.append({"soul": chosen_soul, "job": "", "job_skill": "", "universal_skill": ""})
            print(f"[GameCore] 仲間{num}: {chosen_soul} を選択")
            self._start_job_selection(num)

        elif phase.startswith("JOB_"):
            num = int(phase.split("_")[1])
            chosen_job = self.current_job_picks[choice_index]
            self._building_party[num - 1]["job"] = chosen_job
            print(f"[GameCore] {self._building_party[num - 1]['soul']}のジョブ: {chosen_job}")
            self._start_job_skill_selection(num)

        elif phase.startswith("JSKILL_"):
            num = int(phase.split("_")[1])
            chosen = self._available_skills_list[choice_index]
            self._building_party[num - 1]["job_skill"] = chosen
            print(f"[GameCore] ジョブスキル: {chosen}")
            self._start_universal_skill_selection(num)

        elif phase.startswith("USKILL_"):
            num = int(phase.split("_")[1])
            chosen = self._available_skills_list[choice_index]
            self._building_party[num - 1]["universal_skill"] = chosen
            print(f"[GameCore] 汎用スキル: {chosen}")

            if num < 3:
                self._start_member_selection(num + 1)
            else:
                self._finalize_party()

        return True

    def _finalize_party(self):
        """パーティーを確定してゲーム開始"""
        self.creation_phase = "DONE"
        state = self.state_mgr.state

        for info in self._building_party:
            pc = Character(info["soul"], info["job"],
                           job_skill=info["job_skill"],
                           universal_skill=info["universal_skill"])
            state.party.append(pc)

        party_desc = "、".join([f"『{m.soul_card}({m.job_card})』" for m in state.party])
        print(f"[GameCore] パーティー確定: {party_desc}")

        intro = (
            f"プレイヤーは自らは戦えない「指揮官」として、"
            f"3人のパーティーメンバー({party_desc})を率いて"
            f"暗黒大陸ノクターナルの迷宮に挑む。"
            f"まずはパーティーが迷宮の入口に到着した場面から始めてくれ。"
        )
        self._generate_scene(intro)

    # =================================================================
    #  パーティー情報をUI用dictリストに変換
    # =================================================================

    def _get_party_info(self) -> Optional[list]:
        """renderer に渡すパーティー情報"""
        party = self.state_mgr.state.party
        if not party:
            return None
        return [
            {
                "name": m.get_display_name(),
                "hp": m.current_hp,
                "max_hp": m.max_hp,
                "alive": m.is_alive,
            }
            for m in party
        ]

    # =================================================================
    #  メインループ
    # =================================================================

    def run(self):
        """メインゲームループ。"""
        try:
            # キャラ作成フェーズ
            self.remaining_souls = list(SOUL_CARDS.keys())
            self._start_member_selection(1)

            while self.running:
                result = self.renderer.render()

                if result is None:
                    continue
                if result == -1:
                    self.running = False
                    break
                if result == -2:
                    continue
                if result in (0, 1, 2) and self.awaiting_choice and not self.generating:
                    self._handle_choice(result)

        except Exception as e:
            print(f"\n[GameCore] エラー: {e}")
            traceback.print_exc()
        finally:
            self._cleanup()

    # =================================================================
    #  シーン生成
    # =================================================================

    def _generate_scene(self, user_message: str, scenario_instruction: str = ""):
        """シーンを生成する。テキスト先行表示。"""
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

                full_msg = user_message
                if scenario_instruction:
                    full_msg += f"\n\n{scenario_instruction}"

                print(f"[GameCore] LLMにリクエスト送信中...")
                response = self.lm.send(full_msg, context=context)
                print(f"[GameCore] LLM応答受信！")

                party_info = self._get_party_info()

                self.renderer.set_loading(False)
                self.renderer.set_scene(
                    image_path=None,
                    scene_text=response["scene"],
                    dialogue_text=response["dialogue"],
                    choices=response["choices"],
                    party_info=party_info,
                )

                state.last_scene_text = response["scene"]
                state.last_choices = response["choices"]
                self.awaiting_choice = bool(response["choices"])
                self.generating = False

                # 音声
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
                            print(f"[GameCore] 音声エラー: {e}")
                    threading.Thread(target=_gen_audio, daemon=True).start()

                # 背景画像
                best_pose = self._guess_chara_pose(response["dialogue"], response["scene"])

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
                                party_info=party_info,
                            )
                    except Exception as e:
                        print(f"[GameCore] 画像選択エラー: {e}")

                _pick_image()

                # キャラ生成
                if response["dialogue"] and best_pose:
                    def _gen_chara():
                        try:
                            new_path = self.comfyui.generate_character(best_pose)
                            if new_path:
                                self.renderer.update_chara(str(new_path))
                        except Exception as e:
                            print(f"[GameCore] キャラ生成エラー: {e}")
                    threading.Thread(target=_gen_chara, daemon=True).start()

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

        threading.Thread(target=_generate, daemon=True).start()

    # =================================================================
    #  選択肢処理
    # =================================================================

    def _handle_choice(self, choice_index: int):
        """プレイヤーの選択を処理する。"""
        state = self.state_mgr.state
        choices = state.last_choices

        if choice_index >= len(choices):
            return

        chosen_text = choices[choice_index]
        print(f"\n[GameCore] 指揮官命令: {choice_index + 1}. {chosen_text}")

        # キャラ作成中はそちらで処理
        if self._handle_creation_choice(choice_index):
            return

        # --- パーティーコマンド処理 ---
        # 1. 各メンバーの意志判定
        alive_members = state.get_alive_members()
        cmd_result = self.d20.process_party_command(alive_members, chosen_text)

        # 2. 意志判定結果をコンソールに出力
        will_report = "\n[パーティー意志判定]\n"
        for pr in cmd_result["party_results"]:
            if pr["will_check"]:
                will_report += f"  {pr['will_check']['detail']}\n"

        print(will_report)

        # 3. 従ったメンバーのダイスロール
        dice_results = will_report
        for pr in cmd_result["party_results"]:
            if pr["status"] == "戦闘不能":
                dice_results += f"\n  {pr['character']}: 戦闘不能\n"
                continue

            member_char = None
            for m in alive_members:
                if m.get_display_name() == pr["character"]:
                    member_char = m
                    break

            if member_char and pr.get("obeys"):
                # 従った → アクション判定
                roll_text = self._determine_roll_for_member(member_char, chosen_text)
                if roll_text:
                    dice_results += f"\n  {pr['character']}(従う):\n{roll_text}\n"

        # 4. シナリオ制御
        scenario_instruction = self.scenario.process_choice(choice_index, state)
        phase = self.scenario.get_phase_info()
        print(f"[GameCore] {phase}")

        # 5. 全結果をGMに送る
        scenario_instruction += f"\n\n絶対厳守: 次の判定結果に従って各メンバーの行動を描写すること。\n{dice_results}"

        user_msg = f"指揮官の命令「{chosen_text}」を受けてパーティーが行動する。"
        self._generate_scene(user_msg, scenario_instruction)

    def _determine_roll_for_member(self, member: Character, action_text: str) -> str:
        """メンバーのアクションに対するダイスロール"""
        action = action_text.lower()

        if any(kw in action for kw in ["攻撃", "剣", "斬", "殴", "突撃", "戦"]):
            stat = "STR" if member.get_modifier("STR") >= member.get_modifier("DEX") else "DEX"
            res = self.d20.attack_roll(member, stat, ac=13, damage_dice="1d8")
            if res["hit"]:
                return f"    {stat}攻撃: {res['hit_detail']}\n    → 命中！ {res['damage_detail']}"
            else:
                return f"    {stat}攻撃: {res['hit_detail']}\n    → ミス！"

        elif any(kw in action for kw in ["魔法", "詠唱", "炎", "氷", "雷"]):
            res = self.d20.attack_roll(member, "INT", ac=12, damage_dice="3d6")
            if res["hit"]:
                return f"    INT魔法: {res['hit_detail']}\n    → 命中！ {res['damage_detail']}"
            else:
                return f"    INT魔法: {res['hit_detail']}\n    → ミス！"

        elif any(kw in action for kw in ["避", "逃", "隠", "盗", "偵察"]):
            res = self.d20.skill_check(member, "DEX", dc=12)
            return f"    DEX判定: {res['detail']} → {'成功！' if res['success'] else '失敗...'}"

        elif any(kw in action for kw in ["説得", "交渉", "威圧", "話"]):
            res = self.d20.skill_check(member, "CHA", dc=14)
            return f"    CHA交渉: {res['detail']} → {'成功！' if res['success'] else '失敗...'}"

        elif any(kw in action for kw in ["探", "観察", "調べ", "慎重"]):
            res = self.d20.skill_check(member, "INT", dc=10)
            return f"    INT調査: {res['detail']} → {'成功！' if res['success'] else '失敗...'}"

        elif any(kw in action for kw in ["守", "防御", "待機"]):
            return f"    → 防御態勢（AC+2）"

        return ""

    # =================================================================
    #  画像選択（既存流用）
    # =================================================================

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
        "dungeon_entrance": ["入口", "門", "ダンジョン入"],
        "dungeon_corridor": ["通路", "廊下", "地下", "ダンジョン"],
        "crystal_cave": ["洞窟", "鍾乳洞", "水晶"],
        "ruins": ["遺跡", "廃墟", "古代"],
        "treasure_room": ["宝", "財宝", "金貨"],
        "campfire": ["焚き火", "キャンプ", "野営", "休憩"],
        "battle_field": ["戦場", "戦い", "戦闘", "敵"],
        "magic_circle": ["魔法陣", "呪文", "魔力", "召喚"],
        "sunrise": ["朝", "日の出", "夜明け", "目覚め"],
        "night_sky": ["夜空", "星", "月", "夜"],
        "rain": ["雨", "嵐", "雷"],
        "snow": ["雪", "冬", "吹雪", "寒い"],
    }

    def _pick_scene_image(self, scene_text: str) -> Optional[Path]:
        image_dir = Path(__file__).parent / "assets" / "generated"
        if not image_dir.exists():
            return None
        best_name = None
        best_score = 0
        for filename, keywords in self.SCENE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in scene_text)
            if score > best_score:
                best_score = score
                best_name = filename
        if best_name:
            path = image_dir / f"{best_name}.png"
            if path.exists():
                return path
        available = list(image_dir.glob("*.png"))
        if available:
            return random.choice(available)
        return None

    CHARA_KEYWORDS = {
        "smile": ["微笑", "ふふ", "笑", "優し"],
        "serious": ["真剣", "静か", "冷た", "見つめ"],
        "surprised": ["驚", "えっ", "なっ", "目を見開"],
        "sad": ["悲し", "俯", "うつむ", "申し訳"],
        "blush": ["赤面", "照れ", "恥ず"],
        "attack": ["詠唱", "魔法", "攻撃", "放つ"],
        "back": ["背を向", "去って", "後ろ姿"],
    }

    def _guess_chara_pose(self, dialogue_text: str, scene_text: str) -> Optional[str]:
        if not dialogue_text:
            return None
        target_text = dialogue_text + " " + scene_text
        best_name = "smile"
        best_score = 0
        for pose_name, keywords in self.CHARA_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in target_text)
            if score > best_score:
                best_score = score
                best_name = pose_name
        return best_name

    def _pick_chara_image(self, dialogue_text: str, scene_text: str) -> Optional[Path]:
        best_name = self._guess_chara_pose(dialogue_text, scene_text)
        if not best_name:
            return None
        image_dir = Path(__file__).parent / "assets" / "characters"
        if not image_dir.exists():
            return None
        path = image_dir / f"elf_{best_name}.png"
        if path.exists():
            return path
        available = list(image_dir.glob("elf_*.png"))
        if available:
            return random.choice(available)
        return None

    PROP_KEYWORDS = {
        "grass": ["草原", "野外", "草"],
        "table": ["酒場", "居酒屋", "食事", "宿"],
        "desk": ["ギルド", "受付", "執務室"],
        "signboard": ["街", "町", "市場", "広場"],
        "bushes": ["森", "茂み", "川", "山", "林"],
        "crystals": ["洞窟", "水晶", "地下"],
        "window_frame": ["城", "室内", "部屋"],
    }

    def _pick_prop_image(self, scene_text: str) -> Optional[Path]:
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

    def _cleanup(self):
        print("\n[GameCore] 終了処理中...")
        self.state_mgr.save()
        self.renderer.cleanup()
        print("[GameCore] ゲーム終了。お疲れ様でした。")


def main():
    game = GameCore()
    game.run()


if __name__ == "__main__":
    main()
