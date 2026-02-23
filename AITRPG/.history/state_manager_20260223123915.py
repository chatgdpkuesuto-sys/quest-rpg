"""
state_manager.py — ゲーム状態管理（パーティー対応版）
パーティー全員のHP・状態をJSONでセーブ/ロードする。
"""

import json
from pathlib import Path
from typing import Any, Optional, List
from d20_engine import Character


class GameState:
    """ゲームの全状態を保持・管理するクラス。"""

    def __init__(self):
        self.scene_id: int = 0
        self.turn: int = 0
        self.party: List[Character] = []  # パーティー（3人）
        self.flags: dict[str, Any] = {}
        self.visited_scenes: list[int] = []
        self.current_branch: Optional[str] = None
        self.branch_depth: int = 0
        self.merge_theme: str = ""
        self.last_scene_text: str = ""
        self.last_image_path: str = ""
        self.last_choices: list[str] = []

    def set_flag(self, key: str, value: Any = True):
        self.flags[key] = value

    def get_flag(self, key: str, default: Any = None) -> Any:
        return self.flags.get(key, default)

    def has_flag(self, key: str) -> bool:
        return key in self.flags

    def advance_turn(self):
        self.turn += 1

    def is_party_alive(self) -> bool:
        """パーティーに生存者がいるか。"""
        return any(m.is_alive for m in self.party)

    def get_alive_members(self) -> List[Character]:
        """生存中のメンバーリスト。"""
        return [m for m in self.party if m.is_alive]

    def get_context_string(self) -> str:
        """LLMに送るためのコンテキスト文字列を生成。"""
        lines = [
            f"[システム進行データ]",
            f"ターン: {self.turn}",
            f"シーン番号: {self.scene_id}"
        ]

        if self.party:
            lines.append("\n[パーティーメンバー]")
            for i, m in enumerate(self.party, 1):
                alive_mark = "✓" if m.is_alive else "✗"
                lines.append(f"  {alive_mark} {m.get_display_name()}")
                lines.append(f"    HP: {m.current_hp}/{m.max_hp} | AC: {m.ac}")
                lines.append(f"    {m.get_stat_summary()}")
                lines.append(f"    性格: {m.personality} | 従順度: {m.obedience}")
                innate_names = [s["name"] for s in m.innate_skills]
                all_skills = innate_names + m.job_skills
                if all_skills:
                    lines.append(f"    スキル: {', '.join(all_skills)}")
                if m.weaknesses:
                    lines.append(f"    弱点: {', '.join(m.weaknesses)}")
            lines.append("")

        if self.current_branch:
            lines.append(f"現在の分岐: {self.current_branch}")
            lines.append(f"分岐の深さ: {self.branch_depth}")

        if self.merge_theme:
            lines.append(f"合流テーマ: {self.merge_theme}")

        important_flags = {
            k: v for k, v in self.flags.items() if not k.startswith("_")
        }
        if important_flags:
            flags_str = ", ".join(f"{k}={v}" for k, v in important_flags.items())
            lines.append(f"フラグ: {flags_str}")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """状態を辞書に変換。"""
        return {
            "scene_id": self.scene_id,
            "turn": self.turn,
            "party": [m.to_dict() for m in self.party],
            "flags": self.flags,
            "visited_scenes": self.visited_scenes,
            "current_branch": self.current_branch,
            "branch_depth": self.branch_depth,
            "merge_theme": self.merge_theme,
        }

    def from_dict(self, data: dict):
        """辞書から状態を復元。"""
        self.scene_id = data.get("scene_id", 0)
        self.turn = data.get("turn", 0)

        party_data = data.get("party", [])
        self.party = [Character.from_dict(d) for d in party_data]

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
        save_path = self.save_dir / f"{slot}.json"
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self.state.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"[StateManager] 保存完了: {save_path}")

    def load(self, slot: str = "autosave") -> bool:
        save_path = self.save_dir / f"{slot}.json"
        if not save_path.exists():
            print(f"[StateManager] セーブデータなし: {save_path}")
            return False
        with open(save_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.state.from_dict(data)
        print(f"[StateManager] ロード完了: {save_path}")
        return True

    def new_game(self):
        self.state = GameState()
        print("[StateManager] 新規ゲーム開始")
