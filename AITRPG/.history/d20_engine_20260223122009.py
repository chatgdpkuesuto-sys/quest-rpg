import random
import math
from typing import Dict, Tuple, Optional

# --- アニメクロス・ダンジョンズ D20エンジン ---

class Character:
    def __init__(self, soul_card: str, job_card: str):
        self.soul_card = soul_card
        self.job_card = job_card
        
        # 基礎ステータス (すべて10ベース)
        self.base_stats = {
            "STR": 10,  # 筋力
            "DEX": 10,  # 敏捷
            "CON": 10,  # 耐久
            "INT": 10,  # 知力
            "WIS": 10,  # 精神
            "CHA": 10   # 魅力
        }
        
        self.stats = self.base_stats.copy()
        self.skills = []
        self.weaknesses = []
        
        self.max_hp = 10
        self.current_hp = 10
        self.ac = 10  # Armor Class (防御力)
        
        self._apply_soul_card()
        self._apply_job_card()
        
        # 最終HP計算 (Base + CONボーナス)
        self.max_hp += self.get_modifier("CON")
        self.current_hp = self.max_hp

    def _apply_soul_card(self):
        """魂カード(アニメキャラ)の補正を適用"""
        if self.soul_card == "孫悟空":
            self.stats["STR"] += 4
            self.stats["CON"] += 2
            self.stats["INT"] -= 2
            self.skills.extend(["サイヤ人の血 (HP半分以下で近接ダメ+1d6)", "筋斗雲 (落下無効)"])
            self.weaknesses.append("魔法回避判定に不利")
        elif self.soul_card == "フリーレン":
            self.stats["INT"] += 4
            self.stats["WIS"] += 2
            self.stats["STR"] -= 2
            self.skills.append("悠久の魔法使い (魔法判定に有利)")
            self.weaknesses.append("朝が苦手 (朝の戦闘開始時1ターン行動不能)")
        elif self.soul_card == "ルフィ":
            self.stats["CON"] += 4
            self.stats["CHA"] += 2
            self.stats["INT"] -= 2
            self.skills.append("ゴムゴムの体 (打撃半減、電撃無効)")
            self.weaknesses.append("斬撃に弱い")
        elif self.soul_card == "キリト":
            self.stats["DEX"] += 4
            self.stats["STR"] += 2
            self.stats["WIS"] -= 2
            self.stats["CHA"] += 2
            self.skills.append("二刀流 (近接攻撃時追加攻撃)")
            self.weaknesses.append("精神セーヴに不利")
        elif self.soul_card == "アーニャ":
            self.stats["CHA"] += 4
            self.stats["WIS"] += 4
            self.stats["DEX"] += 2
            self.stats["STR"] -= 4
            self.stats["CON"] -= 2
            self.skills.append("心を読む (NPC交渉に有利)")
            self.weaknesses.append("体力がない (長期戦ペナルティ)")

    def _apply_job_card(self):
        """ジョブカード(職業)の補正を適用"""
        if self.job_card == "戦士":
            self.stats["STR"] += 2
            self.stats["CON"] += 2
            self.max_hp = 12
            self.ac = 16
            self.skills.append("渾身の一撃 (命中-5, ダメージ+10)")
        elif self.job_card == "魔法使い":
            self.stats["INT"] += 2
            self.stats["DEX"] += 2
            self.max_hp = 6
            self.ac = 11
            self.skills.append("ファイアボール (範囲3d6炎)")
        elif self.job_card == "盗賊":
            self.stats["DEX"] += 2
            self.stats["CHA"] += 2
            self.max_hp = 8
            self.ac = 14
            self.skills.append("急所攻撃 (有利時追加1d6)")
        elif self.job_card == "僧侶":
            self.stats["WIS"] += 2
            self.stats["STR"] += 2
            self.max_hp = 8
            self.ac = 15
            self.skills.append("キュア・ウーンズ (味方回復 1d8+WIS)")

    def get_modifier(self, stat_name: str) -> int:
        """ステータス値からボーナス値を計算 (例: 14 -> +2, 8 -> -1)"""
        val = self.stats.get(stat_name, 10)
        return math.floor((val - 10) / 2)


class D20Engine:
    """ダイスロールと判定を管理するエンジン"""
    
    @staticmethod
    def roll_dice(faces: int, count: int = 1) -> Tuple[int, list]:
        """指定面数のダイスをcount個振る"""
        rolls = [random.randint(1, faces) for _ in range(count)]
        return sum(rolls), rolls

    @staticmethod
    def skill_check(character: Character, stat_name: str, dc: int, advantage: bool = False, disadvantage: bool = False) -> Dict:
        """能力値判定を行う"""
        mod = character.get_modifier(stat_name)
        
        # 1d20を振る (有利/不利の処理)
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        
        if advantage and not disadvantage:
            base_roll = max(roll1, roll2)
            rolls_str = f"[{roll1}, {roll2}] -> {base_roll}(有利)"
        elif disadvantage and not advantage:
            base_roll = min(roll1, roll2)
            rolls_str = f"[{roll1}, {roll2}] -> {base_roll}(不利)"
        else:
            base_roll = roll1
            rolls_str = f"[{roll1}]"

        total = base_roll + mod
        success = total >= dc
        is_critical = (base_roll == 20)
        is_fumble = (base_roll == 1)
        
        if is_critical:
            success = True
        if is_fumble:
            success = False

        result = {
            "stat": stat_name,
            "mod": mod,
            "base_roll": base_roll,
            "total": total,
            "dc": dc,
            "success": success,
            "is_critical": is_critical,
            "is_fumble": is_fumble,
            "detail": f"1d20{rolls_str} + {stat_name}({mod}) = {total} vs 難易度{dc}"
        }
        return result

    @staticmethod
    def attack_roll(attacker: Character, stat_name: str, ac: int, weapon_damage_dice: str = "1d6", advantage: bool = False) -> Dict:
        """攻撃の命中判定とダメージ計算を行う"""
        # 命中判定
        hit_check = D20Engine.skill_check(attacker, stat_name, ac, advantage=advantage)
        
        damage_total = 0
        damage_detail = ""
        
        if hit_check["success"]:
            # ダメージ計算文字列のパース (例: "1d6")
            try:
                count, faces = map(int, weapon_damage_dice.lower().split('d'))
            except:
                count, faces = 1, 6
                
            # クリティカル時はダイスの数を倍にする (D&D 5e式)
            if hit_check["is_critical"]:
                count *= 2
                
            dice_sum, rolls = D20Engine.roll_dice(faces, count)
            mod = attacker.get_modifier(stat_name)
            damage_total = max(1, dice_sum + mod) # 最低1ダメージ
            
            crit_str = "【CRITICAL HIT!】" if hit_check["is_critical"] else ""
            damage_detail = f"{crit_str}{count}d{faces}{rolls} + {stat_name}({mod}) = {damage_total}ダメージ"
            
        return {
            "hit_check": hit_check,
            "damage": damage_total,
            "damage_detail": damage_detail
        }

# --- テスト実行 ---
if __name__ == "__main__":
    print("=== キャラクターテスト ===")
    pc = Character("孫悟空", "魔法使い")
    print(f"キャラ: {pc.soul_card} × {pc.job_card}")
    print(f"HP: {pc.current_hp}/{pc.max_hp} | AC: {pc.ac}")
    print("Stats:", {k: f"{v}({'+' if pc.get_modifier(k)>=0 else ''}{pc.get_modifier(k)})" for k, v in pc.stats.items()})
    print("Skills:", pc.skills)
    
    print("\n=== システムテスト: 魔法攻撃 ===")
    eng = D20Engine()
    
    # 孫悟空(魔法使い)がINTでゴブリン(AC:15)に魔法を撃つ
    atk = eng.attack_roll(pc, "INT", ac=15, weapon_damage_dice="3d6")
    print(atk["hit_check"]["detail"])
    if atk["hit_check"]["success"]:
        print("命中！", atk["damage_detail"])
    else:
        print("失敗(ミス)！")
