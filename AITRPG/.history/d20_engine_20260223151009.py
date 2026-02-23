"""
d20_engine.py — 『アニメクロス・ダンジョンズ』 D20コアエンジン（完全版v3）
全50種スキル / 魂カード5種 / ジョブカード4種 / 性格＆意志判定 / パーティー管理
スキル構成: ジョブスキル1つ ＋ 汎用スキル1つ ＋ 固有スキル1つ（パッシブ）
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
        "chara_skill": {
            "name": "戦闘本能",
            "type": "PASSIVE",
            "desc": "戦いの気配を嗅ぎ取り、一瞬早く動く。",
            "trigger": "COMBAT_START",
            "effect": {"type": "ADVANTAGE", "target": "initiative"},
            "limit": 1, "recharge": "COMBAT_START",
        },
        "weaknesses": ["魔法回避判定に不利"],
    },
    "フリーレン": {
        "origin": "葬送のフリーレン",
        "stat_mods": {"INT": +2, "WIS": +2, "STR": -2},
        "personality": "冷静",
        "obedience": 60,
        "chara_skill": {
            "name": "古代魔術の素養",
            "type": "PASSIVE",
            "desc": "詠唱が洗練され、魔法の命中が安定する。",
            "trigger": "BEFORE_ATTACK_ROLL",
            "effect": {"type": "BONUS_TO_ROLL", "value": 2, "condition": "magic"},
            "limit": 1, "recharge": "TURN_START",
        },
        "weaknesses": ["朝が苦手（朝の戦闘開始時1ターン行動不能）"],
    },
    "ルフィ": {
        "origin": "ONE PIECE",
        "stat_mods": {"CON": +4, "WIS": +2, "INT": -2},
        "personality": "天然",
        "obedience": 20,
        "chara_skill": {
            "name": "不屈の意志",
            "type": "PASSIVE",
            "desc": "倒れても折れない。気合いで立ち上がる。",
            "trigger": "AFTER_TAKING_DAMAGE",
            "effect": {"type": "AUTO_STABILIZE", "condition": "hp_zero"},
            "limit": 1, "recharge": "LONG_REST",
        },
        "weaknesses": ["斜撃ダメージに弱い"],
    },
    "キリト": {
        "origin": "SAO",
        "stat_mods": {"DEX": +4, "STR": +2, "WIS": -2, "CHA": +2},
        "personality": "孤高",
        "obedience": 50,
        "chara_skill": {
            "name": "剣技の連結",
            "type": "PASSIVE",
            "desc": "ヒットの流れで追撃の威力が乗る。",
            "trigger": "AFTER_HIT",
            "effect": {"type": "BONUS_DAMAGE", "dice": "1d4"},
            "limit": 1, "recharge": "TURN_START",
        },
        "weaknesses": ["精神(WIS)セーヴに常に不利"],
    },
    "アーニャ": {
        "origin": "SPY×FAMILY",
        "stat_mods": {"CHA": +4, "WIS": +4, "DEX": +2, "STR": -4, "CON": -2},
        "personality": "マイペース",
        "obedience": 25,
        "chara_skill": {
            "name": "直感（？）",
            "type": "PASSIVE",
            "desc": "よく分からないが、ヤバさを察することがある。",
            "trigger": "EXPLORATION_CHECK",
            "effect": {"type": "ADVANTAGE", "category": ["調査", "看破", "危険察知"]},
            "limit": 1, "recharge": "SHORT_REST",
        },
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
                 universal_skill: Optional[str] = None,
                 personality: Optional[str] = None,
                 origin: Optional[str] = None):
        self.soul_card = soul_card
        self.job_card = job_card
        self.level = 1
        self.proficiency = 2

        self.base_stats = {"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10}
        self.stats = self.base_stats.copy()

        if soul_card in SOUL_CARDS:
            soul = SOUL_CARDS[soul_card]
        else:
            # 未知の魂カード（ランダム生成ヒロイン用）の自動ステータス構築
            mods = {"STR": 1, "DEX": 1, "CON": 1, "INT": 1, "WIS": 1, "CHA": 1}
            # 特化ステータスをランダムに2箇所上げる
            specialties = random.sample(list(mods.keys()), 2)
            for s in specialties:
                mods[s] += 1
            
            soul = {
                "origin": origin or "異世界",
                "personality": personality or "謎めいた",
                "obedience": random.randint(30, 80),
                "stat_mods": mods,
                "chara_skill": generate_random_chara_skill(soul_card),
                "weaknesses": ["予測不能な行動を取ることがある"]
            }

        self.personality: str = personality or soul.get("personality", "普通")
        self.obedience: int = soul.get("obedience", 50)
        self.origin: str = origin or soul.get("origin", "不明")

        # --- キャラスキル（魂ごとに固定1つ、構造化） ---
        chara = soul.get("chara_skill", {})
        self.chara_skill_name: str = chara.get("name", "")
        self.chara_skill_desc: str = chara.get("desc", "")
        self.chara_skill_trigger: str = chara.get("trigger", "")
        self.chara_skill_effect: dict = chara.get("effect", {})
        self.chara_skill_limit: int = chara.get("limit", 0)
        self.chara_skill_recharge: str = chara.get("recharge", "")
        self.chara_skill_uses: int = 0  # 使用済み回数

        self.innate_skills: List[dict] = []  # 構造化スキルで管理
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
        """全習得スキル名リスト（ジョブ+汎用+キャラ）"""
        names = []
        if self.job_skill:
            names.append(self.job_skill)
        if self.universal_skill:
            names.append(self.universal_skill)
        if self.chara_skill_name:
            names.append(f"★{self.chara_skill_name}")
        return names

    def take_damage(self, amount: int) -> dict:
        self.current_hp = max(0, self.current_hp - amount)
        result = {"damage": amount, "remaining_hp": self.current_hp, "chara_skill_log": ""}
        if self.current_hp <= 0:
            # ジョブスキル「不屈」
            if "不屈" == self.job_skill and "不屈済" not in self.conditions:
                self.current_hp = 1
                self.conditions.append("不屈済")
                result["stood_firm"] = True
                result["remaining_hp"] = 1
            # ★固有スキル: AFTER_TAKING_DAMAGE + AUTO_STABILIZE (hp_zero)
            elif (self.chara_skill_trigger == "AFTER_TAKING_DAMAGE"
                  and self.chara_skill_effect.get("type") == "AUTO_STABILIZE"
                  and self.chara_skill_effect.get("condition") == "hp_zero"
                  and self.try_chara_skill()):
                self.current_hp = 1
                result["stood_firm"] = True
                result["remaining_hp"] = 1
                result["chara_skill_log"] = f"★{self.chara_skill_name}発動→HP1で耐えた！"
            else:
                self.is_downed = True
                self.current_hp = 0
                result["downed"] = True
        return result

    def try_chara_skill(self) -> bool:
        """固有スキルの使用を試みる。使用可能ならTrueを返し回数を消費。"""
        if self.chara_skill_limit <= 0:
            return True  # 制限なし→常に使用可
        if self.chara_skill_uses < self.chara_skill_limit:
            self.chara_skill_uses += 1
            return True
        return False

    def recharge_chara_skill(self, recharge_type: str):
        """リチャージ条件に合致すれば使用回数をリセット。"""
        if self.chara_skill_recharge == recharge_type:
            self.chara_skill_uses = 0

    def recharge_turn_start(self):
        """ターン開始時のリチャージ。"""
        self.recharge_chara_skill("TURN_START")

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
            "chara_skill_name": self.chara_skill_name,
            "chara_skill_desc": self.chara_skill_desc,
            "chara_skill_uses": self.chara_skill_uses,
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
        c.chara_skill_uses = d.get("chara_skill_uses", 0)
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
        chara_skill_log = ""

        # 渾身の一撃
        if attacker.job_skill == "渾身の一撃":
            hit_penalty = 5
            bonus_damage = 10
        # 覚醒チェック
        if attacker.universal_skill == "覚醒" and attacker.current_hp <= attacker.max_hp // 2:
            bonus_damage += 2

        # ★固有スキル: BEFORE_ATTACK_ROLL フック
        attacker.recharge_turn_start()  # ターン開始リチャージ
        hit_bonus_from_chara = 0
        if attacker.chara_skill_trigger == "BEFORE_ATTACK_ROLL":
            eff = attacker.chara_skill_effect
            # 魔法条件チェック
            condition_ok = True
            if eff.get("condition") == "magic" and stat not in ("INT", "WIS"):
                condition_ok = False
            if condition_ok and attacker.try_chara_skill():
                if eff.get("type") == "BONUS_TO_ROLL":
                    hit_bonus_from_chara = eff.get("value", 0)
                    chara_skill_log = f"★{attacker.chara_skill_name}発動→命中+{hit_bonus_from_chara}"
                elif eff.get("type") == "ADVANTAGE":
                    advantage = True
                    chara_skill_log = f"★{attacker.chara_skill_name}発動→有利"

        base, detail = D20Engine.roll_d20(advantage, disadvantage)
        hit_total = base + mod - hit_penalty + hit_bonus_from_chara
        crit = (base == 20)
        fumble = (base == 1)
        hit = crit if crit or fumble else (hit_total >= ac)

        hit_detail_str = f"1d20{detail}+{stat}({mod:+d})"
        if hit_penalty:
            hit_detail_str += f"-{hit_penalty}"
        if hit_bonus_from_chara:
            hit_detail_str += f"+固有{hit_bonus_from_chara}"
        hit_detail_str += f"={hit_total} vs AC{ac}"

        result = {
            "character": attacker.get_display_name(), "stat": stat,
            "base_roll": base, "hit_total": hit_total, "ac": ac,
            "hit": hit, "is_critical": crit, "is_fumble": fumble,
            "hit_detail": hit_detail_str,
            "damage": 0, "damage_detail": "",
            "chara_skill_log": chara_skill_log,
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

            # ★固有スキル: AFTER_HIT フック
            chara_bonus_dmg = 0
            if attacker.chara_skill_trigger == "AFTER_HIT":
                eff = attacker.chara_skill_effect
                if eff.get("type") == "BONUS_DAMAGE" and attacker.try_chara_skill():
                    dice_str = eff.get("dice", "1d4")
                    try:
                        dn, dd = map(int, dice_str.lower().split("d"))
                        chara_bonus_dmg, _ = D20Engine.roll_dice(dd, dn)
                    except Exception:
                        chara_bonus_dmg = 2
                    chara_skill_log = f"★{attacker.chara_skill_name}発動→+{chara_bonus_dmg}ダメージ"
                    result["chara_skill_log"] = chara_skill_log

            total_dmg = max(1, dice_sum + mod + bonus_damage + sneak + chara_bonus_dmg)
            crit_tag = "【CRITICAL!】" if crit else ""
            dmg_parts = f"{crit_tag}{cnt}d{faces}{rolls}+{stat}({mod:+d})"
            if sneak:
                dmg_parts += f"+急所{sneak}"
            if hit_penalty:
                dmg_parts += f"+渾身10"
            if chara_bonus_dmg:
                dmg_parts += f"+固有{chara_bonus_dmg}"
            dmg_parts += f"={total_dmg}ダメージ"
            result["damage"] = total_dmg
            result["damage_detail"] = dmg_parts

        return result

    @staticmethod
    def roll_initiative(characters: List[Character]) -> List[Tuple]:
        """COMBAT_STARTトリガーの有利を反映したイニシアティブロール"""
        results = []
        for c in characters:
            adv = False
            skill_log = ""
            # ★固有スキル: COMBAT_START → ADVANTAGE(initiative)
            if (c.chara_skill_trigger == "COMBAT_START"
                and c.chara_skill_effect.get("type") == "ADVANTAGE"
                and c.chara_skill_effect.get("target") == "initiative"
                and c.try_chara_skill()):
                adv = True
                skill_log = f"★{c.chara_skill_name}"
            r1 = random.randint(1, 20)
            r2 = random.randint(1, 20) if adv else r1
            roll = max(r1, r2) if adv else r1
            total = roll + c.get_modifier("DEX")
            results.append((c, total, skill_log))
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    @staticmethod
    def death_saving_throw(char: Character) -> Dict:
        """死亡セーヴ (D&D準拠)"""
        roll = random.randint(1, 20)
        result = {
            "character": char.get_display_name(),
            "roll": roll,
            "success_count": char.death_save_success,
            "fail_count": char.death_save_fail,
        }

        if roll == 20:
            # ナチュラル20: HP1で復活
            char.revive(1)
            result["nat20"] = True
            result["detail"] = f"死亡セーヴ: d20[{roll}] → 【奇跡！】HP1で意識回復！"
        elif roll == 1:
            # ナチュラル1: 失敗2回分
            char.death_save_fail += 2
            result["nat1"] = True
            result["detail"] = f"死亡セーヴ: d20[{roll}] → 【絶望】失敗×2！({char.death_save_fail}/3)"
        elif roll >= 10:
            char.death_save_success += 1
            result["detail"] = f"死亡セーヴ: d20[{roll}] → 成功！({char.death_save_success}/3)"
        else:
            char.death_save_fail += 1
            result["detail"] = f"死亡セーヴ: d20[{roll}] → 失敗...({char.death_save_fail}/3)"

        # 判定
        if char.death_save_success >= 3:
            char.stabilize()
            result["stabilized"] = True
            result["detail"] = str(result.get("detail", "")) + " → 容態安定！"
        elif char.death_save_fail >= 3:
            char.die()
            result["died"] = True
            result["detail"] = str(result.get("detail", "")) + " → 死亡..."

        result["success_count"] = char.death_save_success
        result["fail_count"] = char.death_save_fail
        return result

    @staticmethod
    def enemy_attack(enemy: Enemy, target: Character) -> Dict:
        """敵の攻撃処理"""
        roll = random.randint(1, 20)
        hit_total = roll + enemy.atk_bonus
        crit = (roll == 20)
        fumble = (roll == 1)
        hit = crit if crit or fumble else (hit_total >= target.ac)

        result = {
            "attacker": enemy.name, "target": target.get_display_name(),
            "roll": roll, "hit_total": hit_total, "target_ac": target.ac,
            "hit": hit, "is_critical": crit, "is_fumble": fumble,
            "hit_detail": f"{enemy.name}の攻撃: 1d20[{roll}]+{enemy.atk_bonus}={hit_total} vs AC{target.ac}",
            "damage": 0, "damage_detail": "",
        }

        if hit:
            # ダメージ計算
            try:
                parts = enemy.damage_dice.lower().replace("+", "d").split("d")
                if len(parts) == 3:
                    cnt, faces, bonus = int(parts[0]), int(parts[1]), int(parts[2])
                else:
                    cnt, faces, bonus = int(parts[0]), int(parts[1]), 0
            except Exception:
                cnt, faces, bonus = 1, 6, 0
            if crit:
                cnt *= 2
            dice_sum, rolls = D20Engine.roll_dice(faces, cnt)
            total_dmg = max(1, dice_sum + bonus)
            crit_tag = "【CRITICAL!】" if crit else ""
            result["damage"] = total_dmg
            result["damage_detail"] = f"{crit_tag}{cnt}d{faces}{rolls}+{bonus}={total_dmg}ダメージ"

        return result

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
        """スキルを使用し、結果を返す（interpret_skill ベースの汎用処理）"""
        result: Dict = {"skill": skill_name, "user": user.get_display_name(), "success": True}

        # スキル情報を検索
        desc, type_str = "", ""
        for job, skills in SKILL_DB.items():
            if skill_name in skills:
                desc = skills[skill_name]["desc"]
                type_str = skills[skill_name].get("type", "")
                break
        if skill_name in UNIVERSAL_SKILLS:
            desc = UNIVERSAL_SKILLS[skill_name]["desc"]
            type_str = UNIVERSAL_SKILLS[skill_name].get("type", "")
        for s in user.innate_skills:
            if s["name"] == skill_name:
                desc = s["desc"]
                type_str = s.get("type", "")

        # SkillEffect解釈
        effect = interpret_skill(skill_name, desc, type_str)
        result["effect"] = effect

        detail_parts = [f"『{skill_name}』発動！"]

        # ダメージ処理
        if effect["damage"]:
            dice_n, dice_d, dice_bonus = effect["damage"]
            total, rolls = D20Engine.roll_dice(dice_d, dice_n)
            total += dice_bonus
            detail_parts.append(f"{dice_n}d{dice_d}{'+' + str(dice_bonus) if dice_bonus else ''}{rolls}={total}ダメージ")
            result["damage"] = total

            # 必中チェック（マジックミサイル等）
            if effect.get("auto_hit"):
                detail_parts.append("（必中）")

        # 回復処理
        if effect["heal"]:
            dice_n, dice_d, dice_bonus = effect["heal"]
            total, rolls = D20Engine.roll_dice(dice_d, dice_n)
            # 能力修正を加算
            if effect["target"] == "SELF":
                total += dice_bonus
                actual = user.heal(total)
                detail_parts.append(f"自己回復{actual}！({dice_n}d{dice_d}{rolls}+{dice_bonus}={total})")
                result["heal"] = actual
            elif target:
                stat_bonus = dice_bonus
                total += stat_bonus
                actual = target.heal(total)
                detail_parts.append(f"{target.soul_card}を{actual}回復！({dice_n}d{dice_d}{rolls}+{stat_bonus}={total})")
                result["heal"] = actual
            else:
                total += dice_bonus
                detail_parts.append(f"回復{total}({dice_n}d{dice_d}{rolls}+{dice_bonus})")
                result["heal"] = total

        # AC修正
        if effect["ac_mod"]:
            detail_parts.append(f"AC{effect['ac_mod']:+d}")

        # 命中修正
        if effect["to_hit_mod"]:
            detail_parts.append(f"命中{effect['to_hit_mod']:+d}")

        # セーヴ
        if effect["save"]:
            detail_parts.append(f"({effect['save']['ability']}セーヴDC{effect['save']['dc']})")

        # 状態異常
        if effect.get("condition"):
            detail_parts.append(f"→{effect['condition']}")

        # ダメージも回復もない場合
        if not effect["damage"] and not effect["heal"] and not effect["ac_mod"] and not effect["to_hit_mod"]:
            detail_parts.append(f"— {desc}")
            result["narrative_only"] = True

        result["detail"] = " ".join(detail_parts)
        return result


# =====================================================================
#  SkillEffect 解釈エンジン（仕様B）
# =====================================================================

def interpret_skill(skill_name: str, desc: str, type_str: str = "") -> Dict:
    """
    スキルのdescを解析して効果を返す。
    B-3 優先順位: ダイス明示 > キーワード > 演出のみ
    """
    import re as _re

    effect: Dict = {
        "action_type": _parse_action_type(type_str),
        "damage": None,       # (n, d, bonus) tuple or None
        "heal": None,         # (n, d, bonus) tuple or None
        "ac_mod": None,       # int or None
        "to_hit_mod": None,   # int or None
        "target": "ENEMY",    # SELF / ALLY / ENEMY / AREA
        "save": None,         # {"ability": str, "dc": int, "half_on_success": bool} or None
        "condition": None,    # str or None
        "auto_hit": False,    # 必中フラグ
        "duration": "INSTANT",
        "limit": None,
    }

    # === B-4: ダイス表記抽出 ===
    dice_matches = _re.findall(r'(\d+)d(\d+)(?:\+(\d+))?', desc)

    # === B-5: キーワード → 効果マッピング ===

    # 1) 回復系
    heal_keywords = ["回復", "癒し", "治療", "キュア", "HPを"]
    is_heal = any(kw in desc for kw in heal_keywords)

    # 2) AC系
    ac_match = _re.search(r'AC\s*([+\-]\d+)', desc)
    if not ac_match:
        ac_match = _re.search(r'AC\+(\d+)', desc)

    # 3) 命中系
    hit_match = _re.search(r'命中\s*([+\-]\d+)', desc)
    if not hit_match:
        hit_match = _re.search(r'命中([+\-]\d+)', desc)

    # 4) 必中
    if "必中" in desc:
        effect["auto_hit"] = True

    # 5) セーヴ系
    save_match = _re.search(r'(STR|DEX|CON|INT|WIS|CHA)セーヴ', desc)
    if save_match:
        effect["save"] = {
            "ability": save_match.group(1),
            "dc": 12,  # v1.0固定DC
            "half_on_success": "半減" in desc,
        }

    # 6) 状態異常
    condition_keywords = {
        "行動不能": "INCAPACITATED", "金縛り": "PARALYZED", "拘束": "RESTRAINED",
        "転倒": "PRONE", "毒": "POISONED", "眠": "SLEEP",
    }
    for kw, cond in condition_keywords.items():
        if kw in desc:
            effect["condition"] = cond
            break

    # 7) target判定
    if any(kw in desc for kw in ["自身", "自己", "自分"]):
        effect["target"] = "SELF"
    elif any(kw in desc for kw in ["味方", "全員", "範囲"]):
        effect["target"] = "ALLY"
        if "全員" in desc or "範囲" in desc:
            effect["target"] = "AREA"

    # 8) 半減
    if "半減" in desc and not is_heal:
        pass  # save.half_on_success で処理済み

    # === ダイス→効果の割り当て ===
    if dice_matches:
        n, d, bonus = int(dice_matches[0][0]), int(dice_matches[0][1]), int(dice_matches[0][2] or 0)
        if is_heal:
            effect["heal"] = (n, d, bonus)
            if effect["target"] == "ENEMY":
                effect["target"] = "ALLY"
        else:
            effect["damage"] = (n, d, bonus)
    elif is_heal:
        # ダイスなし回復 → 1d8デフォルト
        effect["heal"] = (1, 8, 0)
        if effect["target"] == "ENEMY":
            effect["target"] = "ALLY"

    # === AC修正 ===
    if ac_match:
        val_str = ac_match.group(1) if ac_match.group(1) else f"+{ac_match.group(1)}"
        try:
            effect["ac_mod"] = int(val_str)
        except ValueError:
            # AC+5 形式
            try:
                effect["ac_mod"] = int(ac_match.group(1))
            except (ValueError, IndexError):
                pass

    # === 命中修正 ===
    if hit_match:
        try:
            effect["to_hit_mod"] = int(hit_match.group(1))
        except ValueError:
            pass

    # 特殊: desc内に「+Nダメ」パターン（ダイスなしの追加ダメ）
    bonus_dmg = _re.search(r'[+＋](\d+)ダメ', desc)
    if bonus_dmg and not effect["damage"]:
        val = int(bonus_dmg.group(1))
        effect["damage"] = (0, 0, val)  # ボーナスのみダメージ

    # 特殊: 命中-N, +Nダメ パターン（渾身の一撃等）
    desc_hit_penalty = _re.search(r'命中-(\d+)', desc)
    if desc_hit_penalty:
        effect["to_hit_mod"] = -int(desc_hit_penalty.group(1))

    desc_hit_bonus_dmg = _re.search(r'命中時[+＋](\d+)ダメ', desc)
    if desc_hit_bonus_dmg and not effect["damage"]:
        val = int(desc_hit_bonus_dmg.group(1))
        effect["damage"] = (0, 0, val)

    # duration
    if "1T" in desc or "1ターン" in desc:
        effect["duration"] = "TURNS(1)"
    elif "1分" in desc:
        effect["duration"] = "COMBAT_END"

    return effect


def _parse_action_type(type_str: str) -> str:
    """type文字列からアクション種別を判定"""
    if not type_str:
        return "ACTION"
    if "リアクション" in type_str:
        return "REACTION"
    if "ボーナス" in type_str:
        return "BONUS"
    if "パッシブ" in type_str:
        return "PASSIVE"
    return "ACTION"


# =====================================================================
#  未知の魂ランダム生成（仕様F）
# =====================================================================

_RANDOM_CHARA_SKILL_TEMPLATES = [
    {"category": "先手型", "trigger": "COMBAT_START", "effect": {"type": "ADVANTAGE", "target": "initiative"}, "limit": 1, "recharge": "COMBAT_START", "quality": "資質"},
    {"category": "集中型", "trigger": "BEFORE_ATTACK_ROLL", "effect": {"type": "BONUS_TO_ROLL", "value": 2}, "limit": 1, "recharge": "COMBAT_START", "quality": "集中力"},
    {"category": "耐久型", "trigger": "AFTER_TAKING_DAMAGE", "effect": {"type": "REDUCE_DAMAGE", "value": 2}, "limit": 1, "recharge": "TURN_START", "quality": "耐久力"},
    {"category": "逆転型", "trigger": "AFTER_MISS", "effect": {"type": "REROLL_D20"}, "limit": 1, "recharge": "SHORT_REST", "quality": "根性"},
    {"category": "探索型", "trigger": "EXPLORATION_CHECK", "effect": {"type": "ADVANTAGE"}, "limit": 1, "recharge": "SHORT_REST", "quality": "直感"},
    {"category": "不屈型", "trigger": "AFTER_TAKING_DAMAGE", "effect": {"type": "AUTO_STABILIZE", "condition": "hp_zero"}, "limit": 1, "recharge": "LONG_REST", "quality": "意志"},
]

def generate_random_chara_skill(soul_name: str) -> dict:
    """仕様F: 未知の魂にランダム固有スキルを生成"""
    template = random.choice(_RANDOM_CHARA_SKILL_TEMPLATES)
    # 名前生成: "{1文字目}の{quality}"
    name = f"{soul_name[0]}の{template['quality']}"
    desc_map = {
        "先手型": "戦いの気配を感じ取り、素早く動く。",
        "集中型": "精神を集中し、攻撃の精度が上がる。",
        "耐久型": "粘り強さでダメージを軽減する。",
        "逆転型": "失敗から学び、再挑戦する。",
        "探索型": "異変を察知する勘が働く。",
        "不屈型": "決して倒れない。気合いで立ち上がる。",
    }
    return {
        "name": name,
        "type": "PASSIVE",
        "desc": desc_map.get(str(template.get("category", "")), "不思議な力。"),
        "trigger": template["trigger"],
        "effect": template["effect"],
        "limit": template["limit"],
        "recharge": template["recharge"],
    }


# =====================================================================
#  テスト
# =====================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  D20コアエンジン v3 テスト（キャラスキルパッシブ対応）")
    print("=" * 60)

    party = [
        Character("孫悟空", "戦士", job_skill="渾身の一撃", universal_skill="覚醒"),
        Character("フリーレン", "魔法使い", job_skill="ファイアボール", universal_skill="気合い"),
        Character("キリト", "盗賊", job_skill="急所攻撃", universal_skill="戦術眼"),
    ]

    print("\n--- パーティー ---")
    for m in party:
        print(f"  {m.get_status_line()}")
        print(f"    性格:{m.personality} 従順度:{m.obedience}")
        print(f"    ジョブ: {m.job_skill} / 汎用: {m.universal_skill}")
        print(f"    ★固有: {m.chara_skill_name}（{m.chara_skill_desc}）")
        print(f"      trigger={m.chara_skill_trigger} effect={m.chara_skill_effect}")

    print(f"\n--- イニシアティブ（孫悟空の戦闘本能→有利） ---")
    init = D20Engine.roll_initiative(party)
    for c, val, log in init:
        tag = f" {log}" if log else ""
        print(f"  {c.soul_card}: {val}{tag}")

    print(f"\n--- 攻撃（フリーレン INT攻撃 vs AC12、古代魔術+2反映） ---")
    atk = D20Engine.attack_roll(party[1], "INT", ac=12, damage_dice="1d6")
    print(f"  {atk['hit_detail']}")
    print(f"  {'命中！ ' + atk['damage_detail'] if atk['hit'] else 'ミス！'}")
    if atk['chara_skill_log']:
        print(f"  ★{atk['chara_skill_log']}")

    print(f"\n--- 攻撃（キリト DEX攻撃 vs AC10、剣技の連結+1d4反映） ---")
    atk2 = D20Engine.attack_roll(party[2], "DEX", ac=10, damage_dice="1d8")
    print(f"  {atk2['hit_detail']}")
    if atk2['hit']:
        print(f"  命中！ {atk2['damage_detail']}")
    if atk2['chara_skill_log']:
        print(f"  ★{atk2['chara_skill_log']}")

    print(f"\n--- 未知の魂ランダム生成 ---")
    for _ in range(3):
        rnd = generate_random_chara_skill("テスト魂")
        print(f"  {rnd['name']}: {rnd['desc']} trigger={rnd['trigger']} effect={rnd['effect']}")

    print(f"\n--- スキル数 ---")
    total = sum(len(v) for v in SKILL_DB.values()) + len(UNIVERSAL_SKILLS)
    print(f"  ジョブスキル: {sum(len(v) for v in SKILL_DB.values())}種")
    print(f"  汎用スキル: {len(UNIVERSAL_SKILLS)}種")
    print(f"  合計: {total}種")

