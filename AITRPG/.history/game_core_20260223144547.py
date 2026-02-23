"""
game_core.py — メインゲームループ（指揮官モード＋ターン制戦闘）
プレイヤーは司令塔。魂カードだけ選び、3人の仲間を率いて冒険する。
戦闘はイニシアチブ順ターン制。
"""

import re
import sys
import random
import threading
import traceback
from pathlib import Path
from typing import Optional, List, Dict

from lm_client import LMClient
from comfyui_client import ComfyUIClient, SCENE_TEMPLATES
from voicevox_client import VoicevoxClient
from state_manager import StateManager
from scenario_engine import ScenarioEngine
from renderer import Renderer
from d20_engine import (
    Character, D20Engine, Enemy, ENEMY_TEMPLATES,
    SOUL_CARDS, JOB_CARDS, SKILL_DB, UNIVERSAL_SKILLS,
)


class GameCore:
    """メインゲームエンジン（指揮官モード＋ターン制戦闘）"""

    def __init__(self):
        print("=" * 50)
        print("  ANIME CROSS DUNGEONS")
        print("  指揮官モード + ターン制戦闘")
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

        # キャラ作成
        self.creation_phase = "DONE"
        self.remaining_souls: List[str] = []
        self.current_soul_picks: List[str] = []
        self._building_party: List[str] = []  # 魂名のリスト

        print("[GameCore] 初期化完了\n")

    # =================================================================
    #  キャラクターメイキング（魂カードのみ選択、ジョブ/スキルはランダム）
    # =================================================================

    def _start_member_selection(self, member_num: int):
        """仲間N人目の魂カード選択"""
        self.creation_phase = f"MEMBER_{member_num}"
        picks = random.sample(self.remaining_souls, min(3, len(self.remaining_souls)))
        self.current_soul_picks = picks

        msg = f"【パーティー編成（{member_num}/3）】\n\nあなたの{member_num}人目の仲間を選んでください。"
        for i, name in enumerate(picks):
            soul = SOUL_CARDS[name]
            msg += f"\n\n{i+1}. {name}（{soul['origin']}）"
            msg += f"\n   性格: {soul['personality']}"

        self.renderer.set_loading(False)
        self.renderer.set_scene(scene_text=msg, choices=picks)
        self.state_mgr.state.last_choices = picks
        self.awaiting_choice = True

    def _handle_creation_choice(self, choice_index: int) -> bool:
        """キャラ作成フェーズ処理"""
        if self.creation_phase == "DONE":
            return False

        phase = self.creation_phase
        if phase.startswith("MEMBER_"):
            num = int(phase.split("_")[1])
            chosen = self.current_soul_picks[choice_index]
            self.remaining_souls.remove(chosen)
            self._building_party.append(chosen)
            print(f"[GameCore] 仲間{num}: {chosen} を選択")

            if num < 3:
                self._start_member_selection(num + 1)
            else:
                self._finalize_party()
        return True

    def _finalize_party(self):
        """パーティー確定（ジョブ/スキルはランダム）"""
        self.creation_phase = "DONE"
        state = self.state_mgr.state
        jobs = list(JOB_CARDS.keys())

        party_lines = []
        for soul_name in self._building_party:
            job = random.choice(jobs)
            job_skill = random.choice(list(SKILL_DB.get(job, {}).keys()))
            uni_skill = random.choice(list(UNIVERSAL_SKILLS.keys()))
            pc = Character(soul_name, job, job_skill=job_skill, universal_skill=uni_skill)
            state.party.append(pc)
            party_lines.append(
                f"  {pc.get_display_name()}\n"
                f"    ジョブスキル: {job_skill} / 汎用: {uni_skill} / ★キャラ: {pc.chara_skill_name}（{pc.chara_skill_desc}）"
            )

        party_desc = "\n".join(party_lines)
        print(f"[GameCore] パーティー確定:\n{party_desc}")

        # TALOTTOワークフローでキャラカード画像を非同期生成
        def _gen_chara_cards():
            for m in state.party:
                try:
                    path = self.comfyui.generate_party_chara(m.soul_card, m.job_card)
                    if path:
                        print(f"[GameCore] キャラカード完成: {m.soul_card} → {path.name}")
                except Exception as e:
                    print(f"[GameCore] キャラカード生成エラー({m.soul_card}): {e}")
        threading.Thread(target=_gen_chara_cards, daemon=True).start()

        intro = (
            f"プレイヤーは自らは戦えない「指揮官」として、"
            f"3人のパーティーメンバーを率いて暗黒大陸ノクターナルの迷宮に挑む。"
            f"まずはパーティーが迷宮の入口に到着した場面から始めてくれ。"
        )
        self._generate_scene(intro)

    # =================================================================
    #  パーティー情報
    # =================================================================

    def _get_party_info(self) -> Optional[list]:
        party = self.state_mgr.state.party
        if not party:
            return None
        info = []
        for m in party:
            status = "DEAD" if not m.is_alive else "DOWN" if m.is_downed else "OK"
            info.append({
                "name": m.get_display_name(),
                "hp": m.current_hp, "max_hp": m.max_hp, "ac": m.ac,
                "alive": m.is_alive, "status": status,
                "chara_skill": m.chara_skill_name,
            })
        return info

    # =================================================================
    #  戦闘モード
    # =================================================================

    def _check_combat_markers(self, scene_text: str):
        """シーンテキストから戦闘マーカーを検知"""
        state = self.state_mgr.state

        if "【COMBAT_START】" in scene_text:
            # 敵情報パース
            enemies = []
            for match in re.finditer(r"【ENEMY:(.+?)/HP:(\d+)/AC:(\d+)】", scene_text):
                name, hp, ac = match.group(1), int(match.group(2)), int(match.group(3))
                # テンプレートがあればそこからatk_bonusとdamageを取得
                template = ENEMY_TEMPLATES.get(name)
                if template:
                    enemies.append(Enemy(name, hp, ac, template["atk_bonus"], template["damage"]))
                else:
                    enemies.append(Enemy(name, hp, ac, 3, "1d6+1"))

            if not enemies:
                enemies = [Enemy.from_template("ゴブリン")]

            self._enter_combat(enemies)

        elif "【COMBAT_END】" in scene_text:
            self._exit_combat()

    def _enter_combat(self, enemies: List[Enemy]):
        """戦闘モード開始"""
        state = self.state_mgr.state
        state.in_combat = True
        state.enemies = enemies
        state.combat_round = 1

        # イニシアチブロール（★固有スキル COMBAT_START フック）
        initiative_results = []
        for i, m in enumerate(state.party):
            m.recharge_chara_skill("COMBAT_START")  # 戦闘開始リチャージ
            if m.is_alive and not m.is_downed:
                adv = False
                skill_tag = ""
                # ★固有スキル: COMBAT_START → ADVANTAGE(initiative)
                if (m.chara_skill_trigger == "COMBAT_START"
                    and m.chara_skill_effect.get("type") == "ADVANTAGE"
                    and m.chara_skill_effect.get("target") == "initiative"
                    and m.try_chara_skill()):
                    adv = True
                    skill_tag = f" ★{m.chara_skill_name}"
                r1 = random.randint(1, 20) + m.get_modifier("DEX")
                r2 = random.randint(1, 20) + m.get_modifier("DEX") if adv else r1
                roll = max(r1, r2) if adv else r1
                initiative_results.append(("pc", i, roll, m.get_display_name() + skill_tag))
        for i, e in enumerate(state.enemies):
            roll = random.randint(1, 20) + 1  # 敵DEXは+1固定（簡易）
            initiative_results.append(("enemy", i, roll, e.name))

        initiative_results.sort(key=lambda x: x[2], reverse=True)
        state.turn_order = [(r[0], r[1]) for r in initiative_results]
        state.turn_ptr = 0

        init_log = "[イニシアチブ] "
        init_log += " → ".join([f"{r[3]}({r[2]})" for r in initiative_results])
        print(f"[GameCore] 戦闘開始！ {init_log}")
        print(f"[GameCore] 敵: {', '.join(e.name for e in enemies)}")

        self._process_combat_turn()

    def _exit_combat(self):
        """戦闘終了 → 探索モードへ"""
        state = self.state_mgr.state
        state.in_combat = False
        state.enemies = []
        state.turn_order = []
        state.turn_ptr = 0
        state.combat_round = 0
        print("[GameCore] 戦闘終了 → 探索モードへ")

    def _process_combat_turn(self):
        """現在のターンアクターに応じた処理"""
        state = self.state_mgr.state

        if not state.in_combat or not state.turn_order:
            return

        # 勝利チェック
        if not state.get_alive_enemies():
            self._end_combat_victory()
            return

        # 敗北チェック
        if not state.is_party_alive():
            self._end_combat_defeat()
            return

        # ポインタ巻き戻し
        if state.turn_ptr >= len(state.turn_order):
            state.turn_ptr = 0
            state.combat_round += 1
            print(f"[GameCore] ラウンド{state.combat_round}")

        actor_type, actor_idx = state.turn_order[state.turn_ptr]

        if actor_type == "pc":
            member = state.party[actor_idx]
            if not member.is_alive:
                # 死亡→スキップ
                state.turn_ptr += 1
                self._process_combat_turn()
            elif member.is_downed:
                # 戦闘不能→死亡セーヴ
                self._process_death_save(member)
            else:
                # 行動可能→3択表示
                self._show_combat_choices(member)
        elif actor_type == "enemy":
            enemy = state.enemies[actor_idx]
            if enemy.is_alive:
                self._process_enemy_turn(enemy)
            else:
                state.turn_ptr += 1
                self._process_combat_turn()

    def _show_combat_choices(self, member: Character):
        """PCターン: 通常攻撃/ジョブスキル/汎用スキルの3択"""
        job_label = f"{member.job_skill}" if member.job_skill else "（なし）"
        uni_label = f"{member.universal_skill}" if member.universal_skill else "（なし）"

        choices = [
            f"通常攻撃",
            f"{job_label}",
            f"{uni_label}",
        ]

        msg = f"【{member.get_display_name()}のターン】\nラウンド{self.state_mgr.state.combat_round}\n\n行動を選んでください。"

        party_info = self._get_party_info()
        self.renderer.set_loading(False)
        self.renderer.set_scene(scene_text=msg, choices=choices, party_info=party_info)
        self.state_mgr.state.last_choices = choices
        self.awaiting_choice = True

    def _process_pc_combat_action(self, member: Character, choice_index: int):
        """PCの戦闘行動を処理"""
        state = self.state_mgr.state
        alive_enemies = state.get_alive_enemies()
        if not alive_enemies:
            self._end_combat_victory()
            return

        target_enemy = random.choice(alive_enemies)
        dice_report = ""

        if choice_index == 0:
            # 通常攻撃
            main_stat = JOB_CARDS.get(member.job_card, {}).get("main_stat", "STR")
            atk = self.d20.attack_roll(member, main_stat, target_enemy.ac, "1d8")
            dice_report = f"{member.get_display_name()}の通常攻撃 vs {target_enemy.name}:\n"
            if atk.get("chara_skill_log"):
                dice_report += f"  {atk['chara_skill_log']}\n"
            dice_report += f"  {atk['hit_detail']}\n"
            if atk["hit"]:
                dmg_result = target_enemy.take_damage(atk["damage"])
                dice_report += f"  → 命中！ {atk['damage_detail']}\n"
                dice_report += f"  {target_enemy.name} HP: {dmg_result['remaining_hp']}/{target_enemy.max_hp}\n"
                if dmg_result.get("defeated"):
                    dice_report += f"  → {target_enemy.name}を撃破！\n"
            else:
                dice_report += f"  → ミス！\n"

        elif choice_index == 1:
            # ジョブスキル
            skill_result = self.d20.use_skill(member, member.job_skill, target=None)
            dice_report = f"{member.get_display_name()}のジョブスキル『{member.job_skill}』:\n"
            dice_report += f"  {skill_result['detail']}\n"
            # ダメージスキルなら敵に適用
            if skill_result.get("damage") and alive_enemies:
                dmg_result = target_enemy.take_damage(skill_result["damage"])
                dice_report += f"  {target_enemy.name} HP: {dmg_result['remaining_hp']}/{target_enemy.max_hp}\n"
                if dmg_result.get("defeated"):
                    dice_report += f"  → {target_enemy.name}を撃破！\n"
            elif skill_result.get("heal"):
                dice_report += f"  回復量: {skill_result['heal']}\n"

        elif choice_index == 2:
            # 汎用スキル
            skill_result = self.d20.use_skill(member, member.universal_skill, target=None)
            dice_report = f"{member.get_display_name()}の汎用スキル『{member.universal_skill}』:\n"
            dice_report += f"  {skill_result['detail']}\n"
            if skill_result.get("damage") and alive_enemies:
                dmg_result = target_enemy.take_damage(skill_result["damage"])
                dice_report += f"  {target_enemy.name} HP: {dmg_result['remaining_hp']}/{target_enemy.max_hp}\n"
                if dmg_result.get("defeated"):
                    dice_report += f"  → {target_enemy.name}を撃破！\n"

        # GMに描写依頼（確定結果パケットを使用）
        state.turn_ptr += 1

        packet = self._build_resolved_packet(
            actor_name=member.get_display_name(),
            chosen_action=["通常攻撃", member.job_skill, member.universal_skill][choice_index],
            dice_report=dice_report,
        )
        user_msg = f"{member.soul_card}が行動した。"
        self._generate_scene(user_msg, packet, combat_mode=True)

    def _process_enemy_turn(self, enemy: Enemy):
        """敵ターンの自動処理"""
        state = self.state_mgr.state
        targets = state.get_combat_ready_members()
        if not targets:
            state.turn_ptr += 1
            self._process_combat_turn()
            return

        target = random.choice(targets)
        atk = self.d20.enemy_attack(enemy, target)

        dice_report = f"{enemy.name}の攻撃 vs {target.get_display_name()}:\n"
        dice_report += f"  {atk['hit_detail']}\n"
        if atk["hit"]:
            dmg_result = target.take_damage(atk["damage"])
            dice_report += f"  → 命中！ {atk['damage_detail']}\n"
            dice_report += f"  {target.get_display_name()} HP: {dmg_result['remaining_hp']}/{target.max_hp}\n"
            if dmg_result.get("chara_skill_log"):
                dice_report += f"  {dmg_result['chara_skill_log']}\n"
            if dmg_result.get("downed"):
                dice_report += f"  → {target.soul_card}が戦闘不能！\n"
        else:
            dice_report += f"  → ミス！\n"

        print(f"[GameCore]\n{dice_report}")
        state.turn_ptr += 1

        packet = self._build_resolved_packet(
            actor_name=enemy.name,
            chosen_action=f"{enemy.name}の攻撃",
            dice_report=dice_report,
        )
        user_msg = f"{enemy.name}が{target.soul_card}を攻撃した。"
        self._generate_scene(user_msg, packet, combat_mode=True)

    def _process_death_save(self, member: Character):
        """死亡セーヴ処理"""
        state = self.state_mgr.state
        result = self.d20.death_saving_throw(member)
        dice_report = f"{result['detail']}\n"
        print(f"[GameCore] {dice_report}")

        state.turn_ptr += 1

        if result.get("nat20"):
            extra = f"{member.soul_card}が奇跡的にHP1で意識を取り戻した！"
        elif result.get("died"):
            extra = f"{member.soul_card}が息を引き取った..."
        elif result.get("stabilized"):
            extra = f"{member.soul_card}の容態が安定した。"
        else:
            extra = f"{member.soul_card}の死亡セーヴ結果。"

        packet = self._build_resolved_packet(
            actor_name=member.get_display_name(),
            chosen_action="死亡セーヴ",
            dice_report=f"{dice_report}{extra}",
        )
        user_msg = f"{member.soul_card}が死亡セーヴを行った。"
        self._generate_scene(user_msg, packet, combat_mode=True)

    def _end_combat_victory(self):
        """戦闘勝利"""
        state = self.state_mgr.state
        self._exit_combat()
        msg = "司令塔の指揮のもと、パーティーは敵を全滅させた！【COMBAT_END】マーカーをつけてシーンを描写し、次の探索の選択肢を3つ出してくれ。"
        self._generate_scene(msg)

    def _end_combat_defeat(self):
        """戦闘敗北"""
        state = self.state_mgr.state
        self._exit_combat()
        msg = "パーティーは全滅した...。【COMBAT_END】マーカーをつけて敗北を描写してくれ。"
        self._generate_scene(msg)

    # =================================================================
    #  メインループ
    # =================================================================

    def run(self):
        try:
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
    #  確定結果パケットビルダー（仕様C）
    # =================================================================

    def _build_resolved_packet(self, actor_name: str, chosen_action: str,
                                dice_report: str) -> str:
        """毎ターンGMに渡す確定結果パケットを生成"""
        state = self.state_mgr.state

        enemy_lines = "\n".join(
            f"  {e.name} HP:{e.current_hp}/{e.max_hp} AC:{e.ac} ({'ALIVE' if e.is_alive else 'DEAD'})"
            for e in state.enemies
        ) if state.enemies else "  なし"

        ally_lines = "\n".join(
            f"  {m.get_display_name()} HP:{m.current_hp}/{m.max_hp} {'DOWN' if m.is_downed else 'DEAD' if not m.is_alive else 'OK'}"
            for m in state.party
        )

        packet = f"""[戦況]
Round: {state.combat_round}
Turn: {actor_name}
Enemies:
{enemy_lines}
Allies:
{ally_lines}

[行動]
Actor: {actor_name}
Chosen: {chosen_action}
Resolved:
{dice_report}

[GM描写要件]
- actorは必ず1行以上しゃべる（性格に沿う）
- 上の数値を改変しない
- 次の状況を一歩進める"""
        return packet

    def _build_user_prompt(self, user_message: str, resolved_results: str = "",
                           combat_mode: bool = False) -> str:
        """仕様A-3: User Promptテンプレート構築"""
        state = self.state_mgr.state
        mode = "COMBAT" if state.in_combat else "EXPLORATION"

        # パーティー情報
        party_lines = []
        for i, m in enumerate(state.party):
            label = chr(65 + i)  # A, B, C
            skills = f"ジョブ:{m.job_skill} / 汎用:{m.universal_skill} / 固有:★{m.chara_skill_name}"
            party_lines.append(
                f"  {label}: {m.soul_card} / {m.job_card} / {skills} / 性格:{m.personality}"
            )
        party_text = "\n".join(party_lines)

        prompt = f"""[現在のモード]
{mode}

[状況]
{state.last_scene_text[:300] if state.last_scene_text else 'ゲーム開始'}

[パーティー（3人）]
{party_text}"""

        # 戦闘情報
        if state.in_combat:
            enemy_status = " / ".join(
                f"{e.name} HP:{e.current_hp}/{e.max_hp}" for e in state.enemies
            )
            ally_hp = " / ".join(
                f"{m.soul_card} HP:{m.current_hp}/{m.max_hp}" for m in state.party
            )
            init_order = " → ".join(
                f"{'PC' if t == 'pc' else '敵'}{i}" for t, i in state.turn_order
            )
            prompt += f"""\n
[戦闘情報]
ラウンド: {state.combat_round}
イニシアティブ順: {init_order}
敵: {enemy_status}
味方HP: {ally_hp}"""

        # 確定結果
        if resolved_results:
            prompt += f"""\n
[確定結果]
{resolved_results}"""

        # GMへの指示
        if combat_mode:
            prompt += """\n
[GMへの指示]
- [確定結果]を改変せずに、1ターン分の描写を行う
- 行動したPCは必ず1行以上喋る（魂の性格に沿う）
- choicesは[]にする（戦闘中はシステムがchoicesを提示）"""
        else:
            prompt += """\n
[GMへの指示]
- 次の状況を1段階進める
- choicesに必ず3つの選択肢を入れる（短く、行動の種類が分かれるもの）"""

        prompt += f"\n\n[プレイヤーの行動]\n{user_message}"
        return prompt

    # =================================================================
    #  シーン生成
    # =================================================================

    def _generate_scene(self, user_message: str, scenario_instruction: str = "",
                        combat_mode: bool = False):
        """シーン生成。テキスト先行表示。"""
        if self.generating:
            return

        self.renderer.set_loading(True)
        self.awaiting_choice = False
        self.generating = True

        def _generate():
            try:
                state = self.state_mgr.state

                # 仕様A-3: テンプレートベースのUser Prompt構築
                full_msg = self._build_user_prompt(
                    user_message, resolved_results=scenario_instruction,
                    combat_mode=combat_mode,
                )

                print(f"[GameCore] LLMにリクエスト送信中...")
                response = self.lm.send(full_msg)
                print(f"[GameCore] LLM応答受信！")

                # 戦闘マーカーチェック
                self._check_combat_markers(response["scene"])

                party_info = self._get_party_info()

                # 戦闘中はGMのchoicesを無視（次のターン処理で上書き）
                display_choices = response["choices"] if not state.in_combat else []

                self.renderer.set_loading(False)
                self.renderer.set_scene(
                    image_path=None,
                    scene_text=response["scene"],
                    dialogue_text=response["dialogue"],
                    choices=display_choices,
                    party_info=party_info,
                )

                state.last_scene_text = response["scene"]
                state.last_choices = display_choices
                self.generating = False

                if state.in_combat:
                    # 戦闘中: 次のターンを処理
                    self._process_combat_turn()
                else:
                    self.awaiting_choice = bool(display_choices)

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

                # 画像選択
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
                                choices=state.last_choices,
                                party_info=party_info,
                            )
                    except Exception as e:
                        print(f"[GameCore] 画像選択エラー: {e}")
                _pick_image()

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

            except Exception as e:
                print(f"[GameCore] シーン生成エラー: {e}")
                traceback.print_exc()
                self.renderer.set_loading(False)
                self.renderer.set_scene(
                    scene_text=f"【エラー】シーン生成に失敗: {str(e)}",
                    choices=["再試行する", "設定を確認する", "終了する"],
                )
                self.awaiting_choice = True
                self.generating = False

        threading.Thread(target=_generate, daemon=True).start()

    # =================================================================
    #  選択肢処理
    # =================================================================

    def _handle_choice(self, choice_index: int):
        state = self.state_mgr.state
        choices = state.last_choices
        if choice_index >= len(choices):
            return

        chosen_text = choices[choice_index]
        print(f"\n[GameCore] 選択: {choice_index + 1}. {chosen_text}")

        # キャラ作成中
        if self._handle_creation_choice(choice_index):
            return

        # 戦闘中 → PCの戦闘行動
        if state.in_combat:
            if state.turn_order and state.turn_ptr < len(state.turn_order):
                actor_type, actor_idx = state.turn_order[state.turn_ptr]
                if actor_type == "pc":
                    member = state.party[actor_idx]
                    self._process_pc_combat_action(member, choice_index)
            return

        # 探索モード → 意志判定＋GMへ送る
        alive_members = state.get_alive_members()
        cmd_result = self.d20.process_party_command(alive_members, chosen_text)

        will_report = "\n[パーティー意志判定]\n"
        for pr in cmd_result["party_results"]:
            if pr["will_check"]:
                will_report += f"  {pr['will_check']['detail']}\n"
        print(will_report)

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
                roll_text = self._determine_roll_for_member(member_char, chosen_text)
                if roll_text:
                    dice_results += f"\n  {pr['character']}(従う):\n{roll_text}\n"

        scenario_instruction = self.scenario.process_choice(choice_index, state)
        scenario_instruction += f"\n\n絶対厳守: 次の判定結果に従って描写すること。\n{dice_results}"

        user_msg = f"指揮官の命令「{chosen_text}」"
        self._generate_scene(user_msg, scenario_instruction)

    def _determine_roll_for_member(self, member: Character, action_text: str) -> str:
        action = action_text.lower()
        if any(kw in action for kw in ["攻撃", "剣", "斬", "殴", "突撃", "戦"]):
            stat = "STR" if member.get_modifier("STR") >= member.get_modifier("DEX") else "DEX"
            res = self.d20.attack_roll(member, stat, ac=13, damage_dice="1d8")
            return f"    {stat}攻撃: {res['hit_detail']}\n    → {'命中！ ' + res['damage_detail'] if res['hit'] else 'ミス！'}"
        elif any(kw in action for kw in ["魔法", "詠唱", "炎", "氷", "雷"]):
            res = self.d20.attack_roll(member, "INT", ac=12, damage_dice="3d6")
            return f"    INT魔法: {res['hit_detail']}\n    → {'命中！ ' + res['damage_detail'] if res['hit'] else 'ミス！'}"
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
        "town_square": ["街", "町", "広場", "市場"], "tavern_inside": ["酒場", "宿", "居酒屋"],
        "castle_hall": ["城", "宮殿", "玉座"], "forest": ["森", "林", "木々", "草原"],
        "dungeon_entrance": ["入口", "門", "ダンジョン入"],
        "dungeon_corridor": ["通路", "廊下", "地下", "ダンジョン"],
        "crystal_cave": ["洞窟", "鍾乳洞", "水晶"], "ruins": ["遺跡", "廃墟", "古代"],
        "campfire": ["焚き火", "キャンプ", "野営", "休憩"],
        "battle_field": ["戦場", "戦い", "戦闘", "敵"], "night_sky": ["夜空", "星", "月"],
    }

    def _pick_scene_image(self, scene_text: str) -> Optional[Path]:
        image_dir = Path(__file__).parent / "assets" / "generated"
        if not image_dir.exists():
            return None
        best_name, best_score = None, 0
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
        return random.choice(available) if available else None

    CHARA_KEYWORDS = {
        "smile": ["微笑", "笑", "優し"], "serious": ["真剣", "冷た"],
        "surprised": ["驚", "えっ"], "attack": ["詠唱", "魔法", "攻撃"],
    }

    def _guess_chara_pose(self, dialogue: str, scene: str) -> Optional[str]:
        if not dialogue:
            return None
        text = dialogue + " " + scene
        best, best_s = "smile", 0
        for name, kws in self.CHARA_KEYWORDS.items():
            s = sum(1 for kw in kws if kw in text)
            if s > best_s:
                best_s = s
                best = name
        return best

    def _pick_chara_image(self, dialogue: str, scene: str) -> Optional[Path]:
        name = self._guess_chara_pose(dialogue, scene)
        if not name:
            return None
        d = Path(__file__).parent / "assets" / "characters"
        if not d.exists():
            return None
        p = d / f"elf_{name}.png"
        if p.exists():
            return p
        avail = list(d.glob("elf_*.png"))
        return random.choice(avail) if avail else None

    PROP_KEYWORDS = {
        "grass": ["草原", "野外"], "table": ["酒場", "食事", "宿"],
        "bushes": ["森", "茂み", "川"], "crystals": ["洞窟", "水晶"],
    }

    def _pick_prop_image(self, scene_text: str) -> Optional[Path]:
        d = Path(__file__).parent / "assets" / "props"
        if not d.exists():
            return None
        best, best_s = None, 0
        for name, kws in self.PROP_KEYWORDS.items():
            s = sum(1 for kw in kws if kw in scene_text)
            if s > best_s:
                best_s = s
                best = name
        if best:
            p = d / f"prop_{best}.png"
            if p.exists():
                return p
        return None

    def _cleanup(self):
        print("\n[GameCore] 終了処理中...")
        self.state_mgr.save()
        self.renderer.cleanup()
        print("[GameCore] ゲーム終了。")


def main():
    game = GameCore()
    game.run()


if __name__ == "__main__":
    main()
