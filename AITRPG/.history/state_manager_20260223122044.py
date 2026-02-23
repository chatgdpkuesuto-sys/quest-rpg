"""
state_manager.py — ゲーム状態管理
HP、フラグ、現在シーン、会話履歴をJSONでセーブ/ロードする。
"""

import json
from pathlib import Path
from typing import Any, Optional
from d20_engine import Character


class GameState:
    """ゲームの全状態を保持・管理するクラス。"""

    def __init__(self):
        self.scene_id: int = 0
        self.turn: int = 0
        self.hp: int = 100
        self.max_hp: int = 100
        self.character: Optional[Character] = None
        self.flags: dict[str, Any] = {}
        self.visited_scenes: list[int] = []
        self.current_branch: Optional[str] = None
        self.branch_depth: int = 0  # 分岐の深さ（合流判定用）
        self.merge_theme: str = ""  # 合流時のテーマ
        self.last_scene_text: str = ""
        self.last_image_path: str = ""
        self.last_choices: list[str] = []

    def set_flag(self, key: str, value: Any = True):
        """フラグを設定する。"""
        self.flags[key] = value

    def get_flag(self, key: str, default: Any = None) -> Any:
        """フラグを取得する。"""
        return self.flags.get(key, default)

    def has_flag(self, key: str) -> bool:
        """フラグが存在するか。"""
        return key in self.flags

    def advance_turn(self):
        """ターンを進める。"""
        self.turn += 1

    def take_damage(self, amount: int):
        """ダメージを受ける。"""
        self.hp = max(0, self.hp - amount)

    def heal(self, amount: int):
        """回復する。"""
        self.hp = min(self.max_hp, self.hp + amount)

    def is_alive(self) -> bool:
        """生存判定。"""
        return self.hp > 0

    def get_context_string(self) -> str:
        """LLMに送るためのコンテキスト文字列を生成。"""
        lines = [
            f"[システム進行データ]",
            f"ターン: {self.turn}",
            f"シーン番号: {self.scene_id}"
        ]
        
        if self.character:
            c = self.character
            lines.append("\n[プレイヤーステータス]")
            lines.append(f"クラス: {c.soul_card} × {c.job_card}")
            lines.append(f"HP: {self.hp}/{self.max_hp} | AC(防御力): {c.ac}")
            stats_str = ", ".join([f"{k}: {v}({'+' if c.get_modifier(k)>=0 else ''}{c.get_modifier(k)})" for k, v in c.stats.items()])
            lines.append(f"能力値: {stats_str}")
            if c.skills:
                lines.append(f"スキル: {', '.join(c.skills)}")
            if c.weaknesses:
                lines.append(f"弱点: {', '.join(c.weaknesses)}")
            lines.append("")

        if self.current_branch:
            lines.append(f"現在の分岐: {self.current_branch}")
            lines.append(f"分岐の深さ: {self.branch_depth}")

        if self.merge_theme:
            lines.append(f"合流テーマ: {self.merge_theme}")

        # 直近の重要フラグ
        important_flags = {
            k: v for k, v in self.flags.items() if not k.startswith("_")
        }
        if important_flags:
            flags_str = ", ".join(f"{k}={v}" for k, v in important_flags.items())
            lines.append(f"フラグ: {flags_str}")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """状態を辞書に変換。"""
        d = {
            "scene_id": self.scene_id,
            "turn": self.turn,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "flags": self.flags,
            "visited_scenes": self.visited_scenes,
            "current_branch": self.current_branch,
            "branch_depth": self.branch_depth,
            "merge_theme": self.merge_theme,
        }
        if self.character:
            d["character_soul"] = self.character.soul_card
            d["character_job"] = self.character.job_card
        return d

    def from_dict(self, data: dict):
        """辞書から状態を復元。"""
        self.scene_id = data.get("scene_id", 0)
        self.turn = data.get("turn", 0)
        self.hp = data.get("hp", 100)
        self.max_hp = data.get("max_hp", 100)
        
        soul = data.get("character_soul")
        job = data.get("character_job")
        if soul and job:
            self.character = Character(soul, job)
            
        self.flags = data.get("flags", {})
        self.visited_scenes = data.get("visited_scenes", [])
        self.current_branch = data.get("current_branch")
        self.branch_depth = data.get("branch_depth", 0)
        self.merge_theme = data.get("merge_theme", "")


class StateManager:
    """ゲーム状態のセーブ/ロードを管理。"""

    def __init__(self, save_dir: Optional[str] = None):
        self.save_dir = Path(save_dir) if save_dir else Path(__file__).parent / "saves"
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.state = GameState()

    def save(self, slot: str = "autosave"):
        """ゲーム状態をJSONファイルに保存。"""
        save_path = self.save_dir / f"{slot}.json"
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self.state.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"[StateManager] 保存完了: {save_path}")

    def load(self, slot: str = "autosave") -> bool:
        """ゲーム状態をJSONファイルから読み込み。"""
        save_path = self.save_dir / f"{slot}.json"
        if not save_path.exists():
            print(f"[StateManager] セーブデータが見つかりません: {save_path}")
            return False

        with open(save_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.state.from_dict(data)
        print(f"[StateManager] ロード完了: {save_path}")
        return True

    def new_game(self):
        """新しいゲームを開始する。"""
        self.state = GameState()
        print("[StateManager] 新規ゲーム開始")
