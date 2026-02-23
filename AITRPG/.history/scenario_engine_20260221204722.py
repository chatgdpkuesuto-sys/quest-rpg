"""
scenario_engine.py — 分岐→合流シナリオ制御エンジン
「分岐→合流」を繰り返す一本道構造でゲームを破綻させずに無限生成する。
"""

from enum import Enum
from typing import Optional
from state_manager import GameState


class ScenarioPhase(Enum):
    """シナリオの状態遷移。"""
    MAINLINE = "mainline"       # 本筋（合流後 or 開始時）
    BRANCHING = "branching"     # 分岐ポイント（選択肢提示中）
    IN_BRANCH = "in_branch"     # 分岐ルート内（選択後の展開）
    MERGING = "merging"         # 合流中（分岐ルートが本筋に戻る）


# 合流テーマ候補（LLMに「次のシーンはこのテーマで本筋に戻せ」と指示）
MERGE_THEMES = [
    "新たな敵の出現により、道が一つに収束する",
    "古い遺跡の扉の前で全てのルートが合流する",
    "嵐が近づき、避難場所に向かうことで合流する",
    "謎の人物が現れ、全ての冒険者を一箇所に集める",
    "地震が発生し、地形が変化して道が一つになる",
    "宝の地図の手がかりが一箇所を指し示す",
    "月蝕のイベントにより、全ての道が交差する",
    "追手に追われ、逃げ道が一つしかなくなる",
    "魔力の波動が全てを中心地に引き寄せる",
    "夜明けと共に、旅人たちが宿場町に集う",
]


class ScenarioEngine:
    """分岐→合流を制御するエンジン。"""

    def __init__(self):
        self.phase = ScenarioPhase.MAINLINE
        self.branch_turns_remaining: int = 0
        self.max_branch_turns: int = 3  # 分岐は最大3ターンで合流
        self.merge_theme_index: int = 0
        self.total_branches: int = 0

    def get_phase(self) -> ScenarioPhase:
        """現在のフェーズ。"""
        return self.phase

    def process_choice(self, choice_index: int, state: GameState) -> str:
        """
        プレイヤーの選択を処理し、LLMに送る追加指示を返す。

        Args:
            choice_index: 選択肢の番号（0-based）
            state: 現在のゲーム状態

        Returns:
            LLMに追加で送る指示テキスト
        """
        state.advance_turn()

        if self.phase == ScenarioPhase.MAINLINE:
            # 本筋 → 分岐ポイントへ
            return self._enter_branching(choice_index, state)

        elif self.phase == ScenarioPhase.BRANCHING:
            # 分岐ポイント → 分岐ルートへ
            return self._enter_branch(choice_index, state)

        elif self.phase == ScenarioPhase.IN_BRANCH:
            # 分岐ルート内の進行
            return self._progress_branch(choice_index, state)

        elif self.phase == ScenarioPhase.MERGING:
            # 合流 → 本筋に戻る
            return self._complete_merge(choice_index, state)

        return ""

    def _enter_branching(self, choice_index: int, state: GameState) -> str:
        """本筋から分岐ポイントへ遷移。"""
        self.phase = ScenarioPhase.BRANCHING
        state.scene_id += 1
        state.visited_scenes.append(state.scene_id)

        return (
            "【シナリオ指示】今回のシーンの最後に、"
            "プレイヤーに3つの選択肢を提示してください。"
            "各選択肢は異なる方向に物語を分岐させるものにしてください。"
        )

    def _enter_branch(self, choice_index: int, state: GameState) -> str:
        """分岐ポイントで選択 → 分岐ルートに入る。"""
        self.phase = ScenarioPhase.IN_BRANCH
        self.branch_turns_remaining = self.max_branch_turns
        self.total_branches += 1

        branch_name = f"branch_{self.total_branches}_{choice_index + 1}"
        state.current_branch = branch_name
        state.branch_depth = 1
        state.scene_id += 1
        state.visited_scenes.append(state.scene_id)

        # 合流テーマを事前に決定
        theme = MERGE_THEMES[self.merge_theme_index % len(MERGE_THEMES)]
        state.merge_theme = theme
        self.merge_theme_index += 1

        return (
            f"【シナリオ指示】プレイヤーは選択肢{choice_index + 1}を選びました。"
            f"この選択に基づいたユニークな展開を描写してください。"
            f"ただし、あと{self.branch_turns_remaining}ターン以内に "
            f"「{theme}」という展開で本筋に合流させる準備をしてください。"
        )

    def _progress_branch(self, choice_index: int, state: GameState) -> str:
        """分岐ルート内の進行。残りターンが0になったら合流へ。"""
        self.branch_turns_remaining -= 1
        state.branch_depth += 1
        state.scene_id += 1
        state.visited_scenes.append(state.scene_id)

        if self.branch_turns_remaining <= 0:
            # 合流フェーズへ
            self.phase = ScenarioPhase.MERGING
            return (
                f"【シナリオ指示】分岐ルートの最終ターンです。"
                f"「{state.merge_theme}」という展開を使って、"
                f"物語を本筋に戻してください。"
                f"次のシーンは全ての選択肢が同じ場所・状況に収束するようにしてください。"
            )
        else:
            return (
                f"【シナリオ指示】分岐ルート内です（残り{self.branch_turns_remaining}ターン）。"
                f"この分岐独自の展開を続けてください。"
            )

    def _complete_merge(self, choice_index: int, state: GameState) -> str:
        """合流完了 → 本筋に戻る。"""
        self.phase = ScenarioPhase.MAINLINE
        state.current_branch = None
        state.branch_depth = 0
        state.merge_theme = ""
        state.scene_id += 1
        state.visited_scenes.append(state.scene_id)

        return (
            "【シナリオ指示】合流完了。物語は本筋に戻りました。"
            "新たな冒険のステージを提示し、次の分岐に向けた伏線を張ってください。"
            "壮大で没入感のある情景描写をお願いします。"
        )

    def get_phase_info(self) -> str:
        """現在のフェーズ情報を人間可読な形で返す。"""
        info = f"フェーズ: {self.phase.value}"
        if self.phase == ScenarioPhase.IN_BRANCH:
            info += f" (残り{self.branch_turns_remaining}ターン)"
        return info
