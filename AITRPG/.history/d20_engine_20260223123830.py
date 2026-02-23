"""
d20_engine.py — 『アニメクロス・ダンジョンズ』 D20コアエンジン（完全版）
全40種スキル / 魂カード5種 / ジョブカード4種 / 性格＆意志判定 / パーティー管理
"""

import random
import math
from typing import Dict, List, Tuple, Optional

# =====================================================================
#  スキルデータベース（全40種）
# =====================================================================

SKILL_DB: Dict[str, Dict[str, dict]] = {
    "戦士": {
        "渾身の一撃":       {"type": "パッシブ",           "desc": "命中-5、ダメージ+10"},
        "パリィ":           {"type": "リアクション",       "desc": "AC+1d6で近接攻撃を弾く"},
        "なぎ払い":         {"type": "パッシブ",           "desc": "敵撃破時、ボーナスで隣の敵に追撃"},
        "挑発の雄叫び":     {"type": "アクション",         "desc": "敵全員WISセーヴ。失敗で攻撃を自分に固定"},
        "突撃":             {"type": "アクション",         "desc": "10m直進攻撃でダメージ+2d6、敵吹き飛ばし"},
        "鎧砕き":           {"type": "アクション",         "desc": "命中時、戦闘終了まで対象AC-2"},
        "セカンドウィンド":  {"type": "ボーナスアクション", "desc": "HP 1d10+Lv 回復（小休憩で再使用可）"},
        "踏みとどまり":     {"type": "パッシブ",           "desc": "HP0ダメージ時、1回だけHP1で耐える"},
        "怒りの反撃":       {"type": "リアクション",       "desc": "被ダメ時、隣接敵に即殴り返し"},
        "ぶん投げ":         {"type": "アクション",         "desc": "小型敵/物を掴んで別の敵に投げつける"},
    },
    "魔法使い": {
        "ファイアボール":     {"type": "アクション",         "desc": "範囲3d6炎ダメージ（DEXセーヴ半減）"},
        "マジックミサイル":   {"type": "アクション",         "desc": "必中3本、各1d4+1ダメージ"},
        "シールド":           {"type": "リアクション",       "desc": "そのターンAC+5"},
        "ショート・テレポート": {"type": "ボーナスアクション", "desc": "視界内10m以内にワープ"},
        "スリープ":           {"type": "アクション",         "desc": "エリア内の敵をHP低い順に眠らせる"},
        "アイス・ランス":     {"type": "アクション",         "desc": "2d10ダメージ+次ターン移動力半減"},
        "ヘイスト":           {"type": "アクション",         "desc": "味方1人: AC+2、1ターン2回アクション"},
        "カウンタースペル":   {"type": "リアクション",       "desc": "INT判定で敵魔法を打ち消す"},
        "チェイン・ライトニング": {"type": "アクション",     "desc": "敵1体+連鎖3体に2d8雷ダメージ"},
        "イリュージョン":     {"type": "アクション",         "desc": "幻影デコイ生成、敵の攻撃誘導"},
    },
    "盗賊": {
        "急所攻撃":         {"type": "パッシブ",           "desc": "有利or味方隣接時、ダメージ+1d6"},
        "巧妙なアクション": {"type": "パッシブ",           "desc": "隠密/離脱/早足をボーナスアクション化"},
        "スモークボム":     {"type": "アクション",         "desc": "エリア視界遮断、中の者は攻撃不利"},
        "ポイズン・ダガー": {"type": "ボーナスアクション", "desc": "次命中時、毎ターン1d4毒ダメージ"},
        "かすめ取り":       {"type": "ボーナスアクション", "desc": "敵から有利でアイテム窃盗"},
        "直感回避":         {"type": "リアクション",       "desc": "被ダメージ半減（小休憩で再使用可）"},
        "罠設置":           {"type": "アクション",         "desc": "足元に罠。踏んだ敵にダメージ+移動不能"},
        "アサシネイト":     {"type": "パッシブ",           "desc": "未行動/不意打ち敵は自動クリティカル"},
        "目潰し":           {"type": "ボーナスアクション", "desc": "次ターン終了まで敵の攻撃不利"},
        "フックショット":   {"type": "ボーナスアクション", "desc": "高所移動or軽い敵を引き寄せ"},
    },
    "僧侶": {
        "キュア・ウーンズ":       {"type": "アクション",         "desc": "味方1人 1d8+WIS 回復"},
        "聖なる盾":               {"type": "ボーナスアクション", "desc": "味方1人にAC+2（戦闘終了まで）"},
        "ブレッシング":           {"type": "アクション",         "desc": "味方3人の攻撃/セーヴに+1d4"},
        "ターン・アンデッド":     {"type": "アクション",         "desc": "アンデッドWISセーヴ。失敗で逃亡"},
        "サンクチュアリ":         {"type": "ボーナスアクション", "desc": "味方1人に聖域（攻撃にWISセーヴ必要）"},
        "ホールド・パーソン":     {"type": "アクション",         "desc": "人型1体金縛り（セーヴまで行動不能）"},
        "ディスペル":             {"type": "アクション",         "desc": "状態異常/バフを1つ解除"},
        "スピリチュアル・ウェポン": {"type": "ボーナスアクション", "desc": "光の武器召喚、毎ターンボーナスで攻撃"},
        "癒しの祈り":             {"type": "アクション",         "desc": "10m内味方全員 1d4+WIS 回復"},
        "リバイブ":               {"type": "アクション",         "desc": "死後1分以内の味方をHP1で蘇生"},
    },
}

# =====================================================================
#  魂カードデータ（5種）
# =====================================================================

SOUL_CARDS: Dict[str, dict] = {
    "孫悟空": {
        "origin": "ドラゴンボール",
        "stat_mods": {"STR": +2, "CON": +2, "INT": -2},
        "personality": "熱血",
        "obedience": 30,  # 低い = 命令無視しやすい
        "innate_skills": [
            {"name": "激怒", "desc": "HP半分以下で近接ダメ+2、STR判定有利"},
            {"name": "筋斗雲", "desc": "落下ダメージ無効"},
        ],
        "weaknesses": ["魔法回避判定に不利"],
    },
    "フリーレン": {
        "origin": "葬送のフリーレン",
        "stat_mods": {"INT": +2, "WIS": +2, "STR": -2},
        "personality": "冷静",
        "obedience": 60,  # 合理的なら従う
        "innate_skills": [
            {"name": "フェイの血筋", "desc": "眠らされず、魅了セーヴに有利"},
            {"name": "ゾルトラーク", "desc": "武器なしで1d10の魔法遠隔攻撃"},
        ],
        "weaknesses": ["朝が苦手（朝の戦闘開始時1ターン行動不能）"],
    },
    "ルフィ": {
        "origin": "ONE PIECE",
        "stat_mods": {"CON": +4, "WIS": +2, "INT": -2},
        "personality": "天然",
        "obedience": 20,  # かなり低い
        "innate_skills": [
            {"name": "ゴムゴムの体", "desc": "打撃ダメージ半減、電撃無効"},
        ],
        "weaknesses": ["斬撃ダメージに弱い"],
    },
    "キリト": {
        "origin": "SAO",
        "stat_mods": {"DEX": +4, "STR": +2, "WIS": -2, "CHA": +2},
        "personality": "孤高",
        "obedience": 50,  # 中間
        "innate_skills": [
            {"name": "二刀流", "desc": "近接攻撃時、ボーナスアクションで追加攻撃"},
        ],
        "weaknesses": ["精神(WIS)セーヴに常に不利"],
    },
    "アーニャ": {
        "origin": "SPY×FAMILY",
        "stat_mods": {"CHA": +4, "WIS": +4, "DEX": +2, "STR": -4, "CON": -2},
        "personality": "マイペース",
        "obedience": 25,  # 低い
        "innate_skills": [
            {"name": "心を読む", "desc": "NPC交渉・嘘看破に常に有利"},
        ],
        "weaknesses": ["体力がない（長期戦でSTR/DEXペナルティ）"],
    },
}

# =====================================================================
#  ジョブカードデータ（4種）
# =====================================================================

JOB_CARDS: Dict[str, dict] = {
    "戦士": {
        "stat_mods": {"STR": +2, "CON": +2},
        "base_hp": 12,
        "ac": 16,
        "emoji": "🛡️",
    },
    "魔法使い": {
        "stat_mods": {"INT": +2, "DEX": +2},
        "base_hp": 6,
        "ac": 11,
        "emoji": "🪄",
    },
    "盗賊": {
        "stat_mods": {"DEX": +2, "CHA": +2},
        "base_hp": 8,
        "ac": 14,
        "emoji": "🗡️",
    },
    "僧侶": {
        "stat_mods": {"WIS": +2, "STR": +2},
        "base_hp": 8,
        "ac": 15,
        "emoji": "📿",
    },
}


# =====================================================================
#  Character クラス
# =====================================================================

class Character:
    """パーティメンバー1人分のデータ"""

    def __init__(self, soul_card: str, job_card: str, chosen_skills: Optional[List[str]] = None):
        self.soul_card = soul_card
        self.job_card = job_card
        self.level = 1

        # --- 基礎ステータス (すべて10ベース) ---
        self.base_stats = {
            "STR": 10, "DEX": 10, "CON": 10,
            "INT": 10, "WIS": 10, "CHA": 10,
        }
        self.stats = self.base_stats.copy()

        # --- 性格・意志 ---
        soul = SOUL_CARDS.get(soul_card, {})
        self.personality: str = soul.get("personality", "普通")
        self.obedience: int = soul.get("obedience", 50)
        self.origin: str = soul.get("origin", "不明")

        # --- 固有スキル & 弱点 ---
        self.innate_skills: List[dict] = soul.get("innate_skills", [])
        self.weaknesses: List[str] = list(soul.get("weaknesses", []))

        # --- ジョブスキル（プレイヤーが2つ選択） ---
        self.job_skills: List[str] = list(chosen_skills or [])

        # --- ステータス補正適用 ---
        for stat, mod in soul.get("stat_mods", {}).items():
            self.stats[stat] = self.stats.get(stat, 10) + mod

        job = JOB_CARDS.get(job_card, {})
        for stat, mod in job.get("stat_mods", {}).items():
            self.stats[stat] = self.stats.get(stat, 10) + mod

        # --- HP / AC ---
        self.max_hp = job.get("base_hp", 10) + self.get_modifier("CON")
        self.current_hp = self.max_hp
        self.ac = job.get("ac", 10)

        # --- 状態管理 ---
        self.is_alive = True
        self.conditions: List[str] = []  # 状態異常 (毒、眠り等)

    def get_modifier(self, stat_name: str) -> int:
        """ステータス値 → ボーナス値 (例: 14 → +2)"""
        val = self.stats.get(stat_name, 10)
        return math.floor((val - 10) / 2)

    def take_damage(self, amount: int) -> dict:
        """ダメージを受ける。結果を返す"""
        self.current_hp = max(0, self.current_hp - amount)
        result = {"damage": amount, "remaining_hp": self.current_hp}
        if self.current_hp <= 0:
            # 踏みとどまり判定
            if "踏みとどまり" in self.job_skills and "踏みとどまり済" not in self.conditions:
                self.current_hp = 1
                self.conditions.append("踏みとどまり済")
                result["stood_firm"] = True
                result["remaining_hp"] = 1
            else:
                self.is_alive = False
                result["downed"] = True
        return result

    def heal(self, amount: int) -> int:
        """回復する。実際の回復量を返す"""
        old = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old

    def get_display_name(self) -> str:
        """表示名"""
        job_data = JOB_CARDS.get(self.job_card, {})
        emoji = job_data.get("emoji", "")
        return f"{emoji}{self.soul_card}({self.job_card})"

    def get_status_line(self) -> str:
        """1行ステータス"""
        hp_bar = f"HP:{self.current_hp}/{self.max_hp}"
        return f"{self.get_display_name()} {hp_bar} AC:{self.ac}"

    def get_stat_summary(self) -> str:
        """能力値一覧"""
        parts = []
        for k in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
            mod = self.get_modifier(k)
            sign = "+" if mod >= 0 else ""
            parts.append(f"{k}:{sign}{mod}")
        return " ".join(parts)

    def to_dict(self) -> dict:
        """セーブ用シリアライズ"""
        return {
            "soul_card": self.soul_card,
            "job_card": self.job_card,
            "job_skills": self.job_skills,
            "current_hp": self.current_hp,
            "conditions": self.conditions,
            "is_alive": self.is_alive,
        }

    @staticmethod
    def from_dict(d: dict) -> "Character":
        """ロード用デシリアライズ"""
        c = Character(d["soul_card"], d["job_card"], d.get("job_skills", []))
        c.current_hp = d.get("current_hp", c.max_hp)
        c.conditions = d.get("conditions", [])
        c.is_alive = d.get("is_alive", True)
        return c


# =====================================================================
#  D20Engine — 判定・戦闘処理
# =====================================================================

class D20Engine:
    """ダイスロールと判定を管理するコアエンジン"""

    # ----- ダイス基盤 -----

    @staticmethod
    def roll_dice(faces: int, count: int = 1) -> Tuple[int, list]:
        """count個のdice(faces面)を振る"""
        rolls = [random.randint(1, faces) for _ in range(count)]
        return sum(rolls), rolls

    @staticmethod
    def roll_d20(advantage: bool = False, disadvantage: bool = False) -> Tuple[int, str]:
        """1d20を振る（有利/不利対応）"""
        r1 = random.randint(1, 20)
        r2 = random.randint(1, 20)

        if advantage and not disadvantage:
            result = max(r1, r2)
            detail = f"[{r1},{r2}]→{result}(有利)"
        elif disadvantage and not advantage:
            result = min(r1, r2)
            detail = f"[{r1},{r2}]→{result}(不利)"
        else:
            result = r1
            detail = f"[{r1}]"
        return result, detail

    # ----- 能力値判定 -----

    @staticmethod
    def skill_check(char: Character, stat: str, dc: int,
                    advantage: bool = False, disadvantage: bool = False) -> Dict:
        """能力値判定 (1d20 + mod vs DC)"""
        mod = char.get_modifier(stat)
        base, roll_detail = D20Engine.roll_d20(advantage, disadvantage)
        total = base + mod
        is_crit = (base == 20)
        is_fumble = (base == 1)
        success = (total >= dc) if not is_crit and not is_fumble else is_crit

        return {
            "character": char.get_display_name(),
            "stat": stat, "mod": mod,
            "base_roll": base, "total": total, "dc": dc,
            "success": success,
            "is_critical": is_crit, "is_fumble": is_fumble,
            "detail": f"1d20{roll_detail}+{stat}({mod:+d})={total} vs DC{dc}",
        }

    # ----- 攻撃判定 -----

    @staticmethod
    def attack_roll(attacker: Character, stat: str, ac: int,
                    damage_dice: str = "1d6",
                    advantage: bool = False, disadvantage: bool = False,
                    bonus_damage: int = 0, hit_penalty: int = 0) -> Dict:
        """攻撃ロール + ダメージ計算"""
        # 渾身の一撃処理
        if "渾身の一撃" in attacker.job_skills:
            hit_penalty += 5
            bonus_damage += 10

        mod = attacker.get_modifier(stat)
        base, roll_detail = D20Engine.roll_d20(advantage, disadvantage)
        hit_total = base + mod - hit_penalty
        is_crit = (base == 20)
        is_fumble = (base == 1)
        hit = (hit_total >= ac) if not is_crit and not is_fumble else is_crit

        result = {
            "character": attacker.get_display_name(),
            "stat": stat, "base_roll": base,
            "hit_total": hit_total, "ac": ac,
            "hit": hit, "is_critical": is_crit, "is_fumble": is_fumble,
            "hit_detail": f"1d20{roll_detail}+{stat}({mod:+d}){f'-{hit_penalty}' if hit_penalty else ''}={hit_total} vs AC{ac}",
            "damage": 0, "damage_detail": "",
        }

        if hit:
            try:
                cnt, faces = map(int, damage_dice.lower().split("d"))
            except Exception:
                cnt, faces = 1, 6
            if is_crit:
                cnt *= 2
            dice_sum, rolls = D20Engine.roll_dice(faces, cnt)

            # 急所攻撃
            sneak_extra = 0
            if "急所攻撃" in attacker.job_skills and advantage:
                sneak_sum, sneak_rolls = D20Engine.roll_dice(6, 1)
                sneak_extra = sneak_sum

            total_dmg = max(1, dice_sum + mod + bonus_damage + sneak_extra)
            crit_tag = "【CRITICAL!】" if is_crit else ""
            sneak_tag = f"+急所{sneak_extra}" if sneak_extra else ""
            result["damage"] = total_dmg
            result["damage_detail"] = (
                f"{crit_tag}{cnt}d{faces}{rolls}+{stat}({mod:+d})"
                f"{f'+渾身{bonus_damage}' if '渾身の一撃' in attacker.job_skills else ''}"
                f"{sneak_tag}={total_dmg}ダメージ"
            )

        return result

    # ----- イニシアチブ -----

    @staticmethod
    def roll_initiative(characters: List[Character]) -> List[Tuple[Character, int]]:
        """全員のイニシアチブを振り、行動順にソートして返す"""
        results = []
        for c in characters:
            roll = random.randint(1, 20) + c.get_modifier("DEX")
            results.append((c, roll))
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    # ----- 意志判定（パーティー指揮官システム） -----

    @staticmethod
    def will_check(char: Character, command_text: str) -> Dict:
        """
        キャラが指揮官の命令に従うかどうかの判定。
        従順度 + CHA修正 + 1d20 >= 難易度 で判定。
        性格によって「反抗時の独自行動」が変わる。
        """
        base_dc = 12  # 基本難易度
        cha_mod = char.get_modifier("CHA")
        roll = random.randint(1, 20)

        # 従順度を0〜100から-5〜+10のボーナスに変換
        obedience_bonus = (char.obedience - 50) // 10

        total = roll + cha_mod + obedience_bonus
        obeys = total >= base_dc

        # 性格に応じた反抗行動パターン
        rebel_actions = {
            "熱血":     "命令を無視して敵に突っ込む",
            "冷静":     "独自の判断でより合理的な行動をとる",
            "天然":     "まったく関係ないことを始める",
            "孤高":     "単独で別行動をとる",
            "マイペース": "のんびりしていて行動が遅れる",
        }
        rebel_action = rebel_actions.get(char.personality, "勝手に動く")

        return {
            "character": char.get_display_name(),
            "personality": char.personality,
            "roll": roll,
            "cha_mod": cha_mod,
            "obedience_bonus": obedience_bonus,
            "total": total,
            "dc": base_dc,
            "obeys": obeys,
            "rebel_action": rebel_action if not obeys else "",
            "detail": (
                f"{char.soul_card}[{char.personality}] "
                f"1d20[{roll}]+CHA({cha_mod:+d})+従順({obedience_bonus:+d})={total} vs DC{base_dc} "
                f"→ {'従う！' if obeys else f'反抗！→{rebel_action}'}"
            ),
        }

    # ----- パーティー全体のコマンド処理 -----

    @staticmethod
    def process_party_command(party: List[Character], command_text: str) -> Dict:
        """
        指揮官の命令を受けて、パーティー全員の意志判定→行動を処理する。
        返り値にはGMに渡す全情報が入る。
        """
        results = []
        for member in party:
            if not member.is_alive:
                results.append({
                    "character": member.get_display_name(),
                    "status": "戦闘不能",
                    "will_check": None,
                    "action_result": None,
                })
                continue

            will = D20Engine.will_check(member, command_text)
            results.append({
                "character": member.get_display_name(),
                "status": "行動可能",
                "will_check": will,
                "obeys": will["obeys"],
                "personality": will["personality"],
                "rebel_action": will["rebel_action"],
            })

        return {
            "command": command_text,
            "party_results": results,
        }

    # ----- スキル発動 -----

    @staticmethod
    def use_skill(user: Character, skill_name: str, 
                  target: Optional["Character"] = None) -> Dict:
        """スキルを発動する。効果はスキルごとに異なる。"""
        # ジョブスキル or 固有スキルの確認
        all_skills = list(user.job_skills)
        all_skills += [s["name"] for s in user.innate_skills]

        if skill_name not in all_skills:
            return {"success": False, "detail": f"{user.soul_card}は『{skill_name}』を習得していない！"}

        result: Dict = {"skill": skill_name, "user": user.get_display_name(), "success": True}

        # --- 回復系 ---
        if skill_name == "キュア・ウーンズ" and target:
            heal_roll, _ = D20Engine.roll_dice(8, 1)
            heal_amount = heal_roll + user.get_modifier("WIS")
            actual = target.heal(heal_amount)
            result["detail"] = f"{target.soul_card}のHPを{actual}回復！ (1d8[{heal_roll}]+WIS={heal_amount})"
            result["heal"] = actual

        elif skill_name == "癒しの祈り":
            heal_roll, _ = D20Engine.roll_dice(4, 1)
            heal_amount = heal_roll + user.get_modifier("WIS")
            result["detail"] = f"範囲回復: 全員{heal_amount}回復 (1d4[{heal_roll}]+WIS)"
            result["heal"] = heal_amount

        elif skill_name == "セカンドウィンド":
            heal_roll, _ = D20Engine.roll_dice(10, 1)
            heal_amount = heal_roll + user.level
            actual = user.heal(heal_amount)
            result["detail"] = f"自己回復: HP{actual}回復！ (1d10[{heal_roll}]+Lv{user.level}={heal_amount})"
            result["heal"] = actual

        # --- 攻撃系 ---
        elif skill_name == "ファイアボール":
            dmg, rolls = D20Engine.roll_dice(6, 3)
            result["detail"] = f"ファイアボール！ 3d6{rolls}={dmg}炎ダメージ（DEXセーヴ半減）"
            result["damage"] = dmg

        elif skill_name == "マジックミサイル":
            total = 0
            details = []
            for i in range(3):
                d, _ = D20Engine.roll_dice(4, 1)
                d += 1
                total += d
                details.append(str(d))
            result["detail"] = f"マジックミサイル！ 必中3本({'+'.join(details)})={total}ダメージ"
            result["damage"] = total

        elif skill_name == "アイス・ランス":
            dmg, rolls = D20Engine.roll_dice(10, 2)
            result["detail"] = f"アイス・ランス！ 2d10{rolls}={dmg}ダメージ+移動力半減"
            result["damage"] = dmg

        elif skill_name == "チェイン・ライトニング":
            dmg, rolls = D20Engine.roll_dice(8, 2)
            result["detail"] = f"チェイン・ライトニング！ 2d8{rolls}={dmg}雷ダメージ（+連鎖3体）"
            result["damage"] = dmg

        elif skill_name == "ゾルトラーク":
            dmg, rolls = D20Engine.roll_dice(10, 1)
            result["detail"] = f"ゾルトラーク！ 1d10{rolls}={dmg}魔法ダメージ"
            result["damage"] = dmg

        # --- バフ/デバフ系 ---
        elif skill_name == "ヘイスト" and target:
            result["detail"] = f"{target.soul_card}を加速！ AC+2、1ターン2回行動"

        elif skill_name == "ブレッシング":
            result["detail"] = "味方全員の攻撃/セーヴに+1d4のボーナス！"

        elif skill_name == "聖なる盾" and target:
            result["detail"] = f"{target.soul_card}にAC+2の光の盾を付与！"

        # --- その他 ---
        else:
            # 汎用: スキル説明をそのまま返す
            desc = ""
            for job, skills in SKILL_DB.items():
                if skill_name in skills:
                    desc = skills[skill_name]["desc"]
                    break
            for s in user.innate_skills:
                if s["name"] == skill_name:
                    desc = s["desc"]
            result["detail"] = f"『{skill_name}』発動！ — {desc}"

        return result


# =====================================================================
#  テスト
# =====================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  『アニメクロス・ダンジョンズ』 D20コアエンジン テスト")
    print("=" * 60)

    # パーティー作成
    party = [
        Character("孫悟空", "戦士", ["渾身の一撃", "突撃"]),
        Character("フリーレン", "魔法使い", ["ファイアボール", "シールド"]),
        Character("アーニャ", "盗賊", ["急所攻撃", "かすめ取り"]),
    ]

    print("\n--- パーティー ---")
    for m in party:
        print(f"  {m.get_status_line()}")
        print(f"    {m.get_stat_summary()}")
        print(f"    性格: {m.personality} / 従順度: {m.obedience}")
        print(f"    固有: {[s['name'] for s in m.innate_skills]}")
        print(f"    ジョブ: {m.job_skills}")

    # 意志判定テスト
    print("\n--- 意志判定テスト（命令: '慎重に進め'） ---")
    cmd_result = D20Engine.process_party_command(party, "慎重に進め")
    for pr in cmd_result["party_results"]:
        if pr["will_check"]:
            print(f"  {pr['will_check']['detail']}")

    # 攻撃テスト
    print("\n--- 攻撃テスト（孫悟空 vs ゴブリンAC15） ---")
    atk = D20Engine.attack_roll(party[0], "STR", ac=15, damage_dice="1d8", advantage=False)
    print(f"  命中: {atk['hit_detail']}")
    if atk["hit"]:
        print(f"  ダメージ: {atk['damage_detail']}")
    else:
        print("  ミス！")

    # スキルテスト
    print("\n--- スキルテスト（フリーレン → ファイアボール） ---")
    fb = D20Engine.use_skill(party[1], "ファイアボール")
    print(f"  {fb['detail']}")

    print("\n--- スキルテスト（フリーレン → ゾルトラーク） ---")
    zl = D20Engine.use_skill(party[1], "ゾルトラーク")
    print(f"  {zl['detail']}")
