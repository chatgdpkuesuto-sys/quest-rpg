"""
d20_engine.py — 『アニメクロス・ダンジョンズ』 D20コアエンジン（完全版v2）
全50種スキル / 魂カード5種 / ジョブカード4種 / 性格＆意志判定 / パーティー管理
スキル構成: ジョブスキル1つ ＋ 汎用スキル1つ
"""

import random
import math
from typing import Dict, List, Tuple, Optional

# =====================================================================
#  スキルデータベース（全50種）
# =====================================================================

SKILL_DB: Dict[str, Dict[str, dict]] = {
    "戦士": {
        "渾身の一撃":   {"type": "パッシブ",     "desc": "命中-5、命中時+10ダメ", "limit": "なし"},
        "パリィ":       {"type": "リアクション", "desc": "AC+1d6（1攻撃）", "limit": "習熟回/大休憩"},
        "追撃":         {"type": "ボーナス",     "desc": "命中時、追加攻撃1回", "limit": "習熟回/小休憩"},
        "挑発":         {"type": "アクション",   "desc": "WISセーヴ失敗で1T自分しか攻撃不可", "limit": "習熟回/大休憩"},
        "鎧砕き":       {"type": "アクション",   "desc": "命中時AC-2（1分）", "limit": "2回/小休憩"},
        "戦闘集中":     {"type": "ボーナス",     "desc": "1ターン命中+2", "limit": "なし"},
        "強打":         {"type": "アクション",   "desc": "ダメージダイス2倍", "limit": "1回/小休憩"},
        "踏み込み":     {"type": "パッシブ",     "desc": "近接攻撃射程+1m", "limit": "なし"},
        "セカンドウィンド": {"type": "ボーナス", "desc": "1d10+Lv回復", "limit": "1回/小休憩"},
        "不屈":         {"type": "パッシブ",     "desc": "HP0→HP1で耐える", "limit": "1回/大休憩"},
    },
    "魔法使い": {
        "ファイアボール":   {"type": "アクション",   "desc": "3d6火炎（DEX半減）", "limit": "INT回/大休憩"},
        "マジックミサイル": {"type": "アクション",   "desc": "必中1d4+1×3", "limit": "なし"},
        "シールド":         {"type": "リアクション", "desc": "AC+5", "limit": "INT回/小休憩"},
        "ヘイスト":         {"type": "アクション",   "desc": "AC+2＋追加行動1回（1T）", "limit": "1回/大休憩"},
        "アイスランス":     {"type": "アクション",   "desc": "2d10冷気、移動-2m（1T）", "limit": "なし"},
        "ライトニング":     {"type": "アクション",   "desc": "2d8雷", "limit": "なし"},
        "スリープ":         {"type": "アクション",   "desc": "1体行動不能（WISセーヴ、1T）", "limit": "なし"},
        "ディスペル":       {"type": "アクション",   "desc": "効果1つ解除", "limit": "習熟回/大休憩"},
        "魔力強化":         {"type": "ボーナス",     "desc": "次の呪文ダメ+INT修正", "limit": "なし"},
        "カウンタースペル": {"type": "リアクション", "desc": "魔法無効化", "limit": "習熟回/大休憩"},
    },
    "盗賊": {
        "急所攻撃":     {"type": "パッシブ",     "desc": "1T1回+1d6（Lvで増加）", "limit": "なし"},
        "巧妙なアクション": {"type": "パッシブ", "desc": "毎Tボーナス追加1回", "limit": "なし"},
        "毒刃":         {"type": "ボーナス",     "desc": "命中時1d4毒（3T）", "limit": "習熟回/小休憩"},
        "回避":         {"type": "リアクション", "desc": "ダメ半減", "limit": "習熟回/小休憩"},
        "暗殺":         {"type": "パッシブ",     "desc": "戦闘最初の命中はクリティカル", "limit": "なし"},
        "影移動":       {"type": "パッシブ",     "desc": "追加移動+2m", "limit": "なし"},
        "煙幕":         {"type": "アクション",   "desc": "敵命中-2（1T）", "limit": "なし"},
        "足払い":       {"type": "アクション",   "desc": "STRセーヴ失敗で転倒", "limit": "なし"},
        "神速連撃":     {"type": "アクション",   "desc": "攻撃2回", "limit": "1回/小休憩"},
        "看破":         {"type": "ボーナス",     "desc": "敵AC-1（1T）", "limit": "なし"},
    },
    "僧侶": {
        "キュア":       {"type": "アクション",   "desc": "1d8+WIS回復", "limit": "WIS回/小休憩"},
        "ブレッシング": {"type": "アクション",   "desc": "攻撃・セーヴ+1d4（1分）", "limit": "なし"},
        "聖盾":         {"type": "ボーナス",     "desc": "AC+2（1分）", "limit": "なし"},
        "ホールド":     {"type": "アクション",   "desc": "1体拘束（1T）", "limit": "なし"},
        "退魔光":       {"type": "アクション",   "desc": "2d8光ダメ", "limit": "なし"},
        "祈り":         {"type": "アクション",   "desc": "範囲1d4+WIS回復", "limit": "なし"},
        "浄化":         {"type": "アクション",   "desc": "状態異常解除", "limit": "なし"},
        "神罰":         {"type": "ボーナス",     "desc": "次の攻撃+2d8光", "limit": "なし"},
        "守護結界":     {"type": "ボーナス",     "desc": "ダメージ-2（1T）", "limit": "なし"},
        "蘇生":         {"type": "アクション",   "desc": "HP1で復活", "limit": "1回/大休憩"},
    },
}

# 汎用スキル（全クラス取得可能）
UNIVERSAL_SKILLS: Dict[str, dict] = {
    "応急手当":   {"type": "アクション", "desc": "1d6回復（戦闘外）", "limit": "なし"},
    "気合い":     {"type": "ボーナス",   "desc": "次の判定+1d4", "limit": "なし"},
    "威圧":       {"type": "アクション", "desc": "CHA対抗で敵命中-2（1T）", "limit": "なし"},
    "集中":       {"type": "パッシブ",   "desc": "セーヴ+2（1回）", "limit": "なし"},
    "見切り":     {"type": "リアクション", "desc": "次の攻撃を不利にする", "limit": "なし"},
    "体術":       {"type": "パッシブ",   "desc": "素手1d6ダメ", "limit": "なし"},
    "精神抵抗":   {"type": "リアクション", "desc": "状態異常セーヴ再挑戦", "limit": "なし"},
    "戦術眼":     {"type": "ボーナス",   "desc": "味方1体命中+2（1T）", "limit": "なし"},
    "全力移動":   {"type": "ボーナス",   "desc": "追加移動+3m", "limit": "なし"},
    "覚醒":       {"type": "パッシブ",   "desc": "HP半分以下で攻撃+2（1T）", "limit": "なし"},
}

# =====================================================================
#  魂カードデータ（5種）
# =====================================================================

SOUL_CARDS: Dict[str, dict] = {
    "孫悟空": {
        "origin": "ドラゴンボール",
        "stat_mods": {"STR": +2, "CON": +2, "INT": -2},
        "personality": "熱血",
        "obedience": 30,
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
        "obedience": 60,
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
        "obedience": 20,
        "innate_skills": [
            {"name": "ゴムゴムの体", "desc": "打撃ダメージ半減、電撃無効"},
        ],
        "weaknesses": ["斬撃ダメージに弱い"],
    },
    "キリト": {
        "origin": "SAO",
        "stat_mods": {"DEX": +4, "STR": +2, "WIS": -2, "CHA": +2},
        "personality": "孤高",
        "obedience": 50,
        "innate_skills": [
            {"name": "二刀流", "desc": "近接攻撃時、ボーナスアクションで追加攻撃"},
        ],
        "weaknesses": ["精神(WIS)セーヴに常に不利"],
    },
    "アーニャ": {
        "origin": "SPY×FAMILY",
        "stat_mods": {"CHA": +4, "WIS": +4, "DEX": +2, "STR": -4, "CON": -2},
        "personality": "マイペース",
        "obedience": 25,
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
    "戦士":     {"stat_mods": {"STR": +2, "CON": +2}, "base_hp": 12, "ac": 16, "emoji": "🛡️", "main_stat": "STR"},
    "魔法使い": {"stat_mods": {"INT": +2, "DEX": +2}, "base_hp": 6,  "ac": 11, "emoji": "🪄", "main_stat": "INT"},
    "盗賊":     {"stat_mods": {"DEX": +2, "CHA": +2}, "base_hp": 8,  "ac": 14, "emoji": "🗡️", "main_stat": "DEX"},
    "僧侶":     {"stat_mods": {"WIS": +2, "STR": +2}, "base_hp": 8,  "ac": 15, "emoji": "📿", "main_stat": "WIS"},
}


# =====================================================================
#  Character クラス
# =====================================================================

class Character:
    """パーティメンバー1人分のデータ"""

    def __init__(self, soul_card: str, job_card: str,
                 job_skill: Optional[str] = None,
                 universal_skill: Optional[str] = None):
        self.soul_card = soul_card
        self.job_card = job_card
        self.level = 1
        self.proficiency = 2  # 習熟ボーナス

        # --- 基礎ステータス ---
        self.base_stats = {"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10}
        self.stats = self.base_stats.copy()

        # --- 性格・意志 ---
        soul = SOUL_CARDS.get(soul_card, {})
        self.personality: str = soul.get("personality", "普通")
        self.obedience: int = soul.get("obedience", 50)
        self.origin: str = soul.get("origin", "不明")

        # --- 固有スキル & 弱点 ---
        self.innate_skills: List[dict] = soul.get("innate_skills", [])
        self.weaknesses: List[str] = list(soul.get("weaknesses", []))

        # --- 選択スキル（ジョブ1 + 汎用1） ---
        self.job_skill: str = job_skill or ""
        self.universal_skill: str = universal_skill or ""

        # --- スキル使用回数トラッカー ---
        self.skill_uses: Dict[str, int] = {}

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
        self.is_downed = False  # HP0で戦闘不能
        self.is_stable = False  # 安定済み
        self.death_save_success = 0
        self.death_save_fail = 0
        self.conditions: List[str] = []

    def get_modifier(self, stat_name: str) -> int:
        val = self.stats.get(stat_name, 10)
        return math.floor((val - 10) / 2)

    def get_all_skill_names(self) -> List[str]:
        """全習得スキル名リスト"""
        names = [s["name"] for s in self.innate_skills]
        if self.job_skill:
            names.append(self.job_skill)
        if self.universal_skill:
            names.append(self.universal_skill)
        return names

    def take_damage(self, amount: int) -> dict:
        self.current_hp = max(0, self.current_hp - amount)
        result = {"damage": amount, "remaining_hp": self.current_hp}
        if self.current_hp <= 0:
            if "不屈" == self.job_skill and "不屈済" not in self.conditions:
                self.current_hp = 1
                self.conditions.append("不屈済")
                result["stood_firm"] = True
                result["remaining_hp"] = 1
            else:
                self.is_downed = True
                self.current_hp = 0
                result["downed"] = True
        return result

    def stabilize(self):
        """死亡セーヴ3成功で安定"""
        self.is_stable = True
        self.death_save_success = 0
        self.death_save_fail = 0

    def die(self):
        """死亡セーヴ3失敗で死亡"""
        self.is_alive = False
        self.is_downed = True
        self.death_save_success = 0
        self.death_save_fail = 0

    def revive(self, hp: int = 1):
        """蘇生"""
        self.is_downed = False
        self.is_stable = False
        self.is_alive = True
        self.current_hp = min(hp, self.max_hp)
        self.death_save_success = 0
        self.death_save_fail = 0

    def heal(self, amount: int) -> int:
        old = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old

    def get_display_name(self) -> str:
        emoji = JOB_CARDS.get(self.job_card, {}).get("emoji", "")
        return f"{emoji}{self.soul_card}({self.job_card})"

    def get_status_line(self) -> str:
        return f"{self.get_display_name()} HP:{self.current_hp}/{self.max_hp} AC:{self.ac}"

    def get_stat_summary(self) -> str:
        parts = []
        for k in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
            mod = self.get_modifier(k)
            parts.append(f"{k}:{mod:+d}")
        return " ".join(parts)

    def to_dict(self) -> dict:
        return {
            "soul_card": self.soul_card, "job_card": self.job_card,
            "job_skill": self.job_skill, "universal_skill": self.universal_skill,
            "current_hp": self.current_hp, "conditions": self.conditions,
            "is_alive": self.is_alive, "is_downed": self.is_downed,
            "is_stable": self.is_stable,
            "death_save_success": self.death_save_success,
            "death_save_fail": self.death_save_fail,
            "skill_uses": self.skill_uses,
        }

    @staticmethod
    def from_dict(d: dict) -> "Character":
        c = Character(d["soul_card"], d["job_card"],
                      d.get("job_skill", ""), d.get("universal_skill", ""))
        c.current_hp = d.get("current_hp", c.max_hp)
        c.conditions = d.get("conditions", [])
        c.is_alive = d.get("is_alive", True)
        c.is_downed = d.get("is_downed", False)
        c.is_stable = d.get("is_stable", False)
        c.death_save_success = d.get("death_save_success", 0)
        c.death_save_fail = d.get("death_save_fail", 0)
        c.skill_uses = d.get("skill_uses", {})
        return c


# =====================================================================
#  Enemy クラス
# =====================================================================

ENEMY_TEMPLATES: Dict[str, dict] = {
    "ゴブリン":   {"hp": 7,  "ac": 15, "atk_bonus": 4, "damage": "1d6+2", "name": "ゴブリン"},
    "オーク":     {"hp": 15, "ac": 13, "atk_bonus": 5, "damage": "1d12+3", "name": "オーク"},
    "スライム":   {"hp": 22, "ac": 8,  "atk_bonus": 3, "damage": "1d6+1", "name": "スライム"},
    "スケルトン": {"hp": 13, "ac": 13, "atk_bonus": 4, "damage": "1d6+2", "name": "スケルトン"},
    "ダークエルフ": {"hp": 11, "ac": 15, "atk_bonus": 4, "damage": "1d8+2", "name": "ダークエルフ"},
}


class Enemy:
    """敵ユニット"""
    def __init__(self, name: str, hp: int, ac: int, atk_bonus: int, damage: str):
        self.name = name
        self.max_hp = hp
        self.current_hp = hp
        self.ac = ac
        self.atk_bonus = atk_bonus
        self.damage_dice = damage
        self.is_alive = True

    def take_damage(self, amount: int) -> dict:
        self.current_hp = max(0, self.current_hp - amount)
        result = {"damage": amount, "remaining_hp": self.current_hp}
        if self.current_hp <= 0:
            self.is_alive = False
            result["defeated"] = True
        return result

    def to_dict(self) -> dict:
        return {
            "name": self.name, "max_hp": self.max_hp,
            "current_hp": self.current_hp, "ac": self.ac,
            "atk_bonus": self.atk_bonus, "damage_dice": self.damage_dice,
            "is_alive": self.is_alive,
        }

    @staticmethod
    def from_dict(d: dict) -> "Enemy":
        e = Enemy(d["name"], d["max_hp"], d["ac"], d["atk_bonus"], d["damage_dice"])
        e.current_hp = d.get("current_hp", e.max_hp)
        e.is_alive = d.get("is_alive", True)
        return e

    @staticmethod
    def from_template(template_name: str) -> "Enemy":
        t = ENEMY_TEMPLATES.get(template_name, ENEMY_TEMPLATES["ゴブリン"])
        return Enemy(t["name"], t["hp"], t["ac"], t["atk_bonus"], t["damage"])


# =====================================================================
#  D20Engine — 判定・戦闘処理
# =====================================================================

class D20Engine:
    """ダイスロールと判定を管理するコアエンジン"""

    @staticmethod
    def roll_dice(faces: int, count: int = 1) -> Tuple[int, list]:
        rolls = [random.randint(1, faces) for _ in range(count)]
        return sum(rolls), rolls

    @staticmethod
    def roll_d20(advantage: bool = False, disadvantage: bool = False) -> Tuple[int, str]:
        r1 = random.randint(1, 20)
        r2 = random.randint(1, 20)
        if advantage and not disadvantage:
            return max(r1, r2), f"[{r1},{r2}]→{max(r1,r2)}(有利)"
        elif disadvantage and not advantage:
            return min(r1, r2), f"[{r1},{r2}]→{min(r1,r2)}(不利)"
        return r1, f"[{r1}]"

    @staticmethod
    def skill_check(char: Character, stat: str, dc: int,
                    advantage: bool = False, disadvantage: bool = False) -> Dict:
        mod = char.get_modifier(stat)
        base, detail = D20Engine.roll_d20(advantage, disadvantage)
        total = base + mod
        crit = (base == 20)
        fumble = (base == 1)
        success = crit if crit or fumble else (total >= dc)
        return {
            "character": char.get_display_name(), "stat": stat, "mod": mod,
            "base_roll": base, "total": total, "dc": dc,
            "success": success, "is_critical": crit, "is_fumble": fumble,
            "detail": f"1d20{detail}+{stat}({mod:+d})={total} vs DC{dc}",
        }

    @staticmethod
    def attack_roll(attacker: Character, stat: str, ac: int,
                    damage_dice: str = "1d6",
                    advantage: bool = False, disadvantage: bool = False) -> Dict:
        mod = attacker.get_modifier(stat)
        hit_penalty = 0
        bonus_damage = 0

        # 渾身の一撃
        if attacker.job_skill == "渾身の一撃":
            hit_penalty = 5
            bonus_damage = 10
        # 戦闘集中（アクティブ時）
        # 覚醒チェック
        if attacker.universal_skill == "覚醒" and attacker.current_hp <= attacker.max_hp // 2:
            bonus_damage += 2

        base, detail = D20Engine.roll_d20(advantage, disadvantage)
        hit_total = base + mod - hit_penalty
        crit = (base == 20)
        fumble = (base == 1)
        hit = crit if crit or fumble else (hit_total >= ac)

        result = {
            "character": attacker.get_display_name(), "stat": stat,
            "base_roll": base, "hit_total": hit_total, "ac": ac,
            "hit": hit, "is_critical": crit, "is_fumble": fumble,
            "hit_detail": f"1d20{detail}+{stat}({mod:+d}){f'-{hit_penalty}' if hit_penalty else ''}={hit_total} vs AC{ac}",
            "damage": 0, "damage_detail": "",
        }

        if hit:
            try:
                cnt, faces = map(int, damage_dice.lower().split("d"))
            except Exception:
                cnt, faces = 1, 6
            if crit:
                cnt *= 2
            # 強打
            if attacker.job_skill == "強打":
                cnt *= 2
            dice_sum, rolls = D20Engine.roll_dice(faces, cnt)

            # 急所攻撃
            sneak = 0
            if attacker.job_skill == "急所攻撃" and advantage:
                s, _ = D20Engine.roll_dice(6, 1)
                sneak = s

            total_dmg = max(1, dice_sum + mod + bonus_damage + sneak)
            crit_tag = "【CRITICAL!】" if crit else ""
            result["damage"] = total_dmg
            result["damage_detail"] = f"{crit_tag}{cnt}d{faces}{rolls}+{stat}({mod:+d}){f'+急所{sneak}' if sneak else ''}{f'+渾身10' if hit_penalty else ''}{f'+覚醒2' if bonus_damage > 10 else ''}={total_dmg}ダメージ"

        return result

    @staticmethod
    def roll_initiative(characters: List[Character]) -> List[Tuple[Character, int]]:
        results = [(c, random.randint(1, 20) + c.get_modifier("DEX")) for c in characters]
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    @staticmethod
    def will_check(char: Character, command_text: str) -> Dict:
        roll = random.randint(1, 20)
        cha_mod = char.get_modifier("CHA")
        ob_bonus = (char.obedience - 50) // 10
        total = roll + cha_mod + ob_bonus
        dc = 12
        obeys = total >= dc

        rebel_actions = {
            "熱血": "命令を無視して敵に突っ込む",
            "冷静": "独自の判断でより合理的な行動をとる",
            "天然": "まったく関係ないことを始める",
            "孤高": "単独で別行動をとる",
            "マイペース": "のんびりしていて行動が遅れる",
        }
        rebel = rebel_actions.get(char.personality, "勝手に動く")
        return {
            "character": char.get_display_name(), "personality": char.personality,
            "roll": roll, "cha_mod": cha_mod, "obedience_bonus": ob_bonus,
            "total": total, "dc": dc, "obeys": obeys,
            "rebel_action": rebel if not obeys else "",
            "detail": f"{char.soul_card}[{char.personality}] 1d20[{roll}]+CHA({cha_mod:+d})+従順({ob_bonus:+d})={total} vs DC{dc} → {'従う！' if obeys else f'反抗！→{rebel}'}",
        }

    @staticmethod
    def process_party_command(party: List[Character], command_text: str) -> Dict:
        results = []
        for m in party:
            if not m.is_alive:
                results.append({"character": m.get_display_name(), "status": "戦闘不能", "will_check": None})
                continue
            will = D20Engine.will_check(m, command_text)
            results.append({
                "character": m.get_display_name(), "status": "行動可能",
                "will_check": will, "obeys": will["obeys"],
                "personality": will["personality"], "rebel_action": will["rebel_action"],
            })
        return {"command": command_text, "party_results": results}

    @staticmethod
    def use_skill(user: Character, skill_name: str, target: Optional["Character"] = None) -> Dict:
        result: Dict = {"skill": skill_name, "user": user.get_display_name(), "success": True}

        if skill_name == "キュア" and target:
            h, _ = D20Engine.roll_dice(8, 1)
            amt = h + user.get_modifier("WIS")
            actual = target.heal(amt)
            result["detail"] = f"{target.soul_card}を{actual}回復！(1d8[{h}]+WIS={amt})"
        elif skill_name == "祈り":
            h, _ = D20Engine.roll_dice(4, 1)
            amt = h + user.get_modifier("WIS")
            result["detail"] = f"範囲回復: 全員{amt}回復(1d4[{h}]+WIS)"
        elif skill_name == "セカンドウィンド":
            h, _ = D20Engine.roll_dice(10, 1)
            amt = h + user.level
            actual = user.heal(amt)
            result["detail"] = f"自己回復{actual}！(1d10[{h}]+Lv{user.level})"
        elif skill_name == "応急手当" and target:
            h, _ = D20Engine.roll_dice(6, 1)
            actual = target.heal(h)
            result["detail"] = f"{target.soul_card}を{actual}回復！(1d6[{h}])"
        elif skill_name == "ファイアボール":
            d, r = D20Engine.roll_dice(6, 3)
            result["detail"] = f"ファイアボール！3d6{r}={d}火炎ダメ(DEX半減)"
            result["damage"] = d
        elif skill_name == "マジックミサイル":
            total = 0
            for _ in range(3):
                d, _ = D20Engine.roll_dice(4, 1)
                total += d + 1
            result["detail"] = f"マジックミサイル！必中{total}ダメ"
            result["damage"] = total
        elif skill_name == "アイスランス":
            d, r = D20Engine.roll_dice(10, 2)
            result["detail"] = f"アイスランス！2d10{r}={d}冷気+移動-2m"
            result["damage"] = d
        elif skill_name == "ライトニング":
            d, r = D20Engine.roll_dice(8, 2)
            result["detail"] = f"ライトニング！2d8{r}={d}雷ダメ"
            result["damage"] = d
        elif skill_name == "退魔光":
            d, r = D20Engine.roll_dice(8, 2)
            result["detail"] = f"退魔光！2d8{r}={d}光ダメ"
            result["damage"] = d
        elif skill_name == "ゾルトラーク":
            d, r = D20Engine.roll_dice(10, 1)
            result["detail"] = f"ゾルトラーク！1d10{r}={d}魔法ダメ"
            result["damage"] = d
        elif skill_name == "神速連撃":
            result["detail"] = "神速連撃！攻撃2回！"
        elif skill_name == "蘇生" and target:
            target.is_alive = True
            target.current_hp = 1
            result["detail"] = f"{target.soul_card}をHP1で蘇生！"
        else:
            # 汎用: データベースから説明を引く
            desc = ""
            for job, skills in SKILL_DB.items():
                if skill_name in skills:
                    desc = skills[skill_name]["desc"]
                    break
            if skill_name in UNIVERSAL_SKILLS:
                desc = UNIVERSAL_SKILLS[skill_name]["desc"]
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
    print("  D20コアエンジン v2 テスト（50スキル版）")
    print("=" * 60)

    party = [
        Character("孫悟空", "戦士", job_skill="渾身の一撃", universal_skill="覚醒"),
        Character("フリーレン", "魔法使い", job_skill="ファイアボール", universal_skill="気合い"),
        Character("アーニャ", "盗賊", job_skill="急所攻撃", universal_skill="戦術眼"),
    ]

    print("\n--- パーティー ---")
    for m in party:
        print(f"  {m.get_status_line()}")
        print(f"    {m.get_stat_summary()}")
        print(f"    性格:{m.personality} 従順度:{m.obedience}")
        print(f"    ジョブスキル: {m.job_skill} / 汎用: {m.universal_skill}")
        print(f"    固有: {[s['name'] for s in m.innate_skills]}")

    print("\n--- 意志判定（'慎重に進め'） ---")
    for pr in D20Engine.process_party_command(party, "慎重に進め")["party_results"]:
        if pr["will_check"]:
            print(f"  {pr['will_check']['detail']}")

    print(f"\n--- 攻撃（孫悟空 vs AC15） ---")
    atk = D20Engine.attack_roll(party[0], "STR", ac=15, damage_dice="1d8")
    print(f"  {atk['hit_detail']}")
    print(f"  {'命中！ ' + atk['damage_detail'] if atk['hit'] else 'ミス！'}")

    print(f"\n--- スキル: ファイアボール ---")
    print(f"  {D20Engine.use_skill(party[1], 'ファイアボール')['detail']}")

    print(f"\n--- スキル数 ---")
    total = sum(len(v) for v in SKILL_DB.values()) + len(UNIVERSAL_SKILLS)
    print(f"  ジョブスキル: {sum(len(v) for v in SKILL_DB.values())}種")
    print(f"  汎用スキル: {len(UNIVERSAL_SKILLS)}種")
    print(f"  合計: {total}種")
