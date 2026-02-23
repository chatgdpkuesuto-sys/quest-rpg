"""
state_manager.py — ゲーム状態管理（戦闘モード対応版）
パーティー・戦闘状態・敵ユニットをJSONでセーブ/ロードする。
"""

import json
from pathlib import Path
from typing import Any, Optional, List
from d20_engine import Character, Enemy


class GameState:
    """ゲームの全状態を保持・管理するクラス。"""

    def __init__(self):
        self.scene_id: int = 0
        self.turn: int = 0
        self.party: List[Character] = []

        # 戦闘状態
        self.in_combat: bool = False
        self.combat_round: int = 0
        self.turn_order: list = []       # [(type, index), ...] type="pc"|"enemy"
        self.turn_ptr: int = 0
        self.enemies: List[Enemy] = []

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
        return any(m.is_alive for m in self.party)

    def get_alive_members(self) -> List[Character]:
        return [m for m in self.party if m.is_alive]

    def get_combat_ready_members(self) -> List[Character]:
        """戦闘行動可能な(alive & not downed)メンバー"""
        return [m for m in self.party if m.is_alive and not m.is_downed]

    def get_alive_enemies(self) -> List[Enemy]:
        return [e for e in self.enemies if e.is_alive]

    def get_context_string(self) -> str:
        """LLMに送るためのコンテキスト文字列を生成。"""
        lines = [
            f"[システム進行データ]",
            f"ターン: {self.turn}",
            f"シーン番号: {self.scene_id}",
            f"モード: {'戦闘中(ラウンド{})'.format(self.combat_round) if self.in_combat else '探索'}",
        ]

        if self.party:
            lines.append("\n[パーティーメンバー]")
            for m in self.party:
                status = "✓行動可" if m.is_alive and not m.is_downed else "⚠戦闘不能" if m.is_downed and m.is_alive else "✗死亡"
                lines.append(f"  {status} {m.get_display_name()}")
                lines.append(f"    HP: {m.current_hp}/{m.max_hp} | AC: {m.ac}")
                lines.append(f"    {m.get_stat_summary()}")
                lines.append(f"    性格: {m.personality}")
                skills = m.get_all_skill_names()
                if skills:
                    lines.append(f"    スキル: {', '.join(skills)}")

        if self.in_combat and self.enemies:
            lines.append("\n[敵ユニット]")
            for e in self.enemies:
                alive = "○" if e.is_alive else "×"
                lines.append(f"  {alive} {e.name} HP:{e.current_hp}/{e.max_hp} AC:{e.ac}")

        if self.current_branch:
            lines.append(f"分岐: {self.current_branch} (深さ{self.branch_depth})")

        important_flags = {k: v for k, v in self.flags.items() if not k.startswith("_")}
        if important_flags:
            lines.append(f"フラグ: {', '.join(f'{k}={v}' for k, v in important_flags.items())}")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "scene_id": self.scene_id, "turn": self.turn,
            "party": [m.to_dict() for m in self.party],
            "in_combat": self.in_combat,
            "combat_round": self.combat_round,
            "turn_order": self.turn_order,
            "turn_ptr": self.turn_ptr,
            "enemies": [e.to_dict() for e in self.enemies],
            "flags": self.flags,
            "visited_scenes": self.visited_scenes,
            "current_branch": self.current_branch,
            "branch_depth": self.branch_depth,
            "merge_theme": self.merge_theme,
        }

    def from_dict(self, data: dict):
        self.scene_id = data.get("scene_id", 0)
        self.turn = data.get("turn", 0)
        self.party = [Character.from_dict(d) for d in data.get("party", [])]
        self.in_combat = data.get("in_combat", False)
        self.combat_round = data.get("combat_round", 0)
        self.turn_order = data.get("turn_order", [])
        self.turn_ptr = data.get("turn_ptr", 0)
        self.enemies = [Enemy.from_dict(d) for d in data.get("enemies", [])]
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
