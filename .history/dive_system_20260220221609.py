"""
dive_system.py ── まちゃだん VRMMO ダイブ端末
----------------------------------------------
ai_hub.py (Flask port 5000) と連携する
CustomTkinter 製ネイティブクライアント。

起動方法:
  .venv\Scripts\python.exe dive_system.py
"""

import os
import json
import time
import threading
import requests
import customtkinter as ctk
from tkinter import PhotoImage
from PIL import Image, ImageTk, ImageFilter
import textwrap

# =========================================================
#  定数
# =========================================================
PROJECT_ROOT   = os.path.dirname(os.path.abspath(__file__))
SCENE_JSON     = os.path.join(PROJECT_ROOT, "index_scene.json")
STATUS_JSON    = os.path.join(PROJECT_ROOT, "status.json")
VOICE_FILE     = os.path.join(PROJECT_ROOT, "04_Assets", "voice_out.wav")
API_URL        = "http://127.0.0.1:5000/action"

POLL_INTERVAL  = 1500  # ms（status.json の監視間隔）

# =========================================================
#  カラーパレット
# =========================================================
BG          = "#0a0005"
PANEL_BG    = "#100208"
BORDER      = "#3a0015"
TEXT_MAIN   = "#e0d0d0"
TEXT_GM     = "#ff9999"
TEXT_DESPAIR= "#ff2222"
TEXT_PLEASURE="#ff66b2"
TEXT_DIM    = "#666666"
BTN_BG      = "#1e0008"
BTN_HOVER   = "#3a0012"
BTN_BORDER  = "#660022"
BTN_TEXT    = "#ffcccc"
GOLD        = "#ffdd88"

# =========================================================
#  メインアプリ
# =========================================================
class DiveApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        self.title("⛧ まちゃだん ── DIVE TERMINAL")
        self.geometry("1000x720")
        self.configure(fg_color=BG)
        self.minsize(800, 580)

        # 状態
        self._last_updated_at = 0.0
        self._waiting_for_response = False
        self._fade_alpha = 1.0
        self._scene_image: ImageTk.PhotoImage | None = None

        self._build_ui()
        self._show_prologue()
        self._start_polling()

    # =========================================================
    #  UIレイアウト
    # =========================================================
    def _build_ui(self):
        # ── ヘッダー ──────────────────────────
        self.header = ctk.CTkFrame(self, fg_color=PANEL_BG, height=44, corner_radius=0,
                                   border_width=1, border_color=BORDER)
        self.header.pack(fill="x", pady=(0, 0))
        self.header.pack_propagate(False)

        self.lbl_logo = ctk.CTkLabel(self.header, text="⛧  まちゃだん  DIVE TERMINAL",
                                     font=ctk.CTkFont("Yu Mincho", 18, "bold"),
                                     text_color="#8b0000")
        self.lbl_logo.pack(side="left", padx=20)

        self.lbl_status = ctk.CTkLabel(self.header, text="● 待機中",
                                       font=ctk.CTkFont("Consolas", 11),
                                       text_color="#44ff44")
        self.lbl_status.pack(side="right", padx=20)

        self.lbl_dice = ctk.CTkLabel(self.header, text="🎲 ──",
                                     font=ctk.CTkFont("Consolas", 12),
                                     text_color=GOLD)
        self.lbl_dice.pack(side="right", padx=10)

        # ── メイン 2カラム ────────────────────
        self.main_frame = ctk.CTkFrame(self, fg_color=BG)
        self.main_frame.pack(fill="both", expand=True, padx=14, pady=10)
        self.main_frame.columnconfigure(0, weight=3)
        self.main_frame.columnconfigure(1, weight=2)
        self.main_frame.rowconfigure(0, weight=1)

        # 左: テキストパネル
        self.text_panel = ctk.CTkFrame(self.main_frame, fg_color=PANEL_BG,
                                       corner_radius=6, border_width=1, border_color=BORDER)
        self.text_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.situation_box = ctk.CTkTextbox(self.text_panel,
                                            fg_color=PANEL_BG, text_color=TEXT_MAIN,
                                            font=ctk.CTkFont("Yu Mincho", 15),
                                            wrap="word", state="disabled",
                                            border_width=0)
        self.situation_box.pack(fill="both", expand=True, padx=12, pady=12)

        # 右: 画像 + ボタン
        self.right_panel = ctk.CTkFrame(self.main_frame, fg_color=PANEL_BG,
                                        corner_radius=6, border_width=1, border_color=BORDER)
        self.right_panel.grid(row=0, column=1, sticky="nsew")

        # 画像エリア
        self.img_label = ctk.CTkLabel(self.right_panel, text="〔 舞台裏 〕",
                                      text_color=TEXT_DIM,
                                      font=ctk.CTkFont("Yu Mincho", 13),
                                      fg_color=BG, corner_radius=4)
        self.img_label.pack(fill="x", padx=10, pady=(10, 5))

        # 選択肢エリア
        self.choices_label = ctk.CTkLabel(self.right_panel, text="── 選択 ──",
                                          text_color=TEXT_DIM,
                                          font=ctk.CTkFont("Yu Mincho", 11))
        self.choices_label.pack(pady=(8, 4))

        self.choices_frame = ctk.CTkScrollableFrame(self.right_panel,
                                                    fg_color=PANEL_BG,
                                                    scrollbar_button_color=BORDER)
        self.choices_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # ── フッター (GMロール) ──────────────
        self.footer = ctk.CTkFrame(self, fg_color=PANEL_BG, height=30, corner_radius=0,
                                   border_width=1, border_color=BORDER)
        self.footer.pack(fill="x")
        self.footer.pack_propagate(False)

        self.lbl_gm_voice = ctk.CTkLabel(self.footer, text="",
                                          text_color=TEXT_GM,
                                          font=ctk.CTkFont("Yu Mincho", 12, "italic"))
        self.lbl_gm_voice.pack(side="left", padx=16)

    # =========================================================
    #  プロローグ表示（初期画面）
    # =========================================================
    def _show_prologue(self):
        heroines = [
            ("🛡️ アリア ── 堕ちた聖騎士",   "ヒロイン選択: アリア（聖堂騎士）",  "高潔な鎧の下に隠された、種の保存本能。"),
            ("🐺 ゼナ ── 黒狼の番い",         "ヒロイン選択: ゼナ（黒狼の獣人）",   "「よこせ！ それは俺の獲物だ！」"),
            ("🧙‍♀️ エララ ── 母性の魔女",      "ヒロイン選択: エララ（蒼の魔女）",   "「坊や、お姉さんが搾ってあげる♥」"),
            ("🎲 ダイスに委ねる",             "ダイスで運命に委ねる",              "運命があなたの相手を決める。"),
        ]

        self._set_situation(
            "あなたは気がつくと、見知らぬ世界に立っていた。\n\n"
            "ここは【男性が絶滅した世界】。\n"
            "目の前に、3人の少女が現れる。\n"
            "彼女たちの瞳が、あなたの存在に怪しく潤む……。",
            gm_voice="「ふふ、いらっしゃい……。ボタンを押して、あなたの運命を選んで？」"
        )
        self._render_choices_from_list(heroines)

    # =========================================================
    #  テキスト更新
    # =========================================================
    def _set_situation(self, text: str, gm_voice: str = ""):
        self.situation_box.configure(state="normal")
        self.situation_box.delete("1.0", "end")
        # 改行やHTMLタグを簡易処理
        clean = text.replace("<br>", "\n").replace("<br/>", "\n")
        # HTMLタグ除去（簡易）
        import re
        clean = re.sub(r"<[^>]+>", "", clean)
        self.situation_box.insert("end", clean)
        self.situation_box.configure(state="disabled")
        if gm_voice:
            self.lbl_gm_voice.configure(text=f"りりす  「{gm_voice}」")

    # =========================================================
    #  ボタンレンダリング
    # =========================================================
    def _clear_choices(self):
        for w in self.choices_frame.winfo_children():
            w.destroy()

    def _render_choices_from_list(self, choices: list[tuple]):
        """choices: [(表示テキスト, アクション文字列, サブテキスト), ...]"""
        self._clear_choices()
        for display, action, sub in choices:
            self._add_choice_button(display, action, sub)

    def _render_choices_from_html(self, ui_html: str):
        """LLMが返した ui_html からボタンを抽出してレンダリング"""
        self._clear_choices()
        import re
        # onclick="sendAction('xxx')" を抽出
        pattern = r"onclick=['\"]sendAction\(['\"](.+?)['\"]"
        labels_p = r">([^<]+)</button>"
        actions = re.findall(pattern, ui_html)
        labels_ = re.findall(labels_p, ui_html)

        if not actions:
            # フォールバック: 全部通しで1ボタン
            self._add_choice_button("続きへ……", ui_html[:40], "")
            return

        for i, action in enumerate(actions):
            label = labels_[i] if i < len(labels_) else action
            self._add_choice_button(label.strip(), action, "")

    def _add_choice_button(self, text: str, action: str, sub: str = ""):
        btn_text = text if not sub else f"{text}\n{sub}"
        btn = ctk.CTkButton(
            self.choices_frame,
            text=btn_text,
            text_color=BTN_TEXT,
            fg_color=BTN_BG,
            hover_color=BTN_HOVER,
            border_color=BTN_BORDER,
            border_width=1,
            corner_radius=3,
            font=ctk.CTkFont("Yu Mincho", 14),
            anchor="w",
            command=lambda a=action: self._send_action(a),
        )
        btn.pack(fill="x", pady=5, padx=4)

    # =========================================================
    #  アクション送信
    # =========================================================
    def _send_action(self, action_text: str):
        if self._waiting_for_response:
            return
        self._waiting_for_response = True
        self._set_status("⏳ 思考中……", "#ffdd44")
        self._clear_choices()
        ctk.CTkLabel(self.choices_frame, text="りりすが思考しています……",
                     text_color=TEXT_DIM,
                     font=ctk.CTkFont("Yu Mincho", 13, "italic")).pack(pady=30)

        def _post():
            try:
                r = requests.post(API_URL, json={"action": action_text, "timestamp": time.time()}, timeout=5)
                if r.status_code == 200:
                    self.after(0, lambda: self._set_status("● 処理中……", "#ffaa44"))
                else:
                    self.after(0, lambda: self._on_error(f"HTTP {r.status_code}"))
            except Exception as e:
                self.after(0, lambda: self._on_error(str(e)))

        threading.Thread(target=_post, daemon=True).start()

    def _on_error(self, msg: str):
        self._waiting_for_response = False
        self._set_status(f"❌ エラー: {msg}", TEXT_DESPAIR)
        self._show_prologue()

    # =========================================================
    #  ステータスポーリング（バックグラウンドスレッド）
    # =========================================================
    def _start_polling(self):
        self._poll()

    def _poll(self):
        if not self._waiting_for_response:
            # 初回はstatus.jsonの現在値を記録するだけ
            pass
        else:
            self._check_status_json()
        # 再スケジュール
        self.after(POLL_INTERVAL, self._poll)

    def _check_status_json(self):
        def _read():
            try:
                with open(STATUS_JSON, "r", encoding="utf-8") as f:
                    data = json.load(f)
                new_ts = data.get("updated_at", 0)
                if new_ts > self._last_updated_at:
                    self.after(0, lambda: self._load_scene(new_ts))
            except Exception:
                pass
        threading.Thread(target=_read, daemon=True).start()

    def _load_scene(self, new_ts: float):
        self._last_updated_at = new_ts
        try:
            with open(SCENE_JSON, "r", encoding="utf-8") as f:
                scene = json.load(f)
            self._apply_scene(scene)
        except Exception as e:
            self._on_error(f"シーン読込失敗: {e}")

    def _apply_scene(self, scene: dict):
        self._waiting_for_response = False
        self._set_status("● 準備完了", "#44ff44")

        # テキスト更新
        self._set_situation(scene.get("situation_text", ""))

        # ダイス表示
        dice = scene.get("dice_result", "")
        if dice:
            self.lbl_dice.configure(text=f"🎲 {dice}")

        # ボタン更新
        ui_html = scene.get("ui_html", "")
        if ui_html:
            self._render_choices_from_html(ui_html)
        else:
            self._show_prologue()

        # 音声再生（非同期）
        threading.Thread(target=self._play_voice, daemon=True).start()

    # =========================================================
    #  音声再生
    # =========================================================
    def _play_voice(self):
        try:
            import subprocess
            if os.path.exists(VOICE_FILE):
                # PowerShell で wav 再生
                subprocess.Popen(
                    ["powershell", "-c", f"(New-Object Media.SoundPlayer '{VOICE_FILE}').PlaySync()"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
        except Exception:
            pass

    # =========================================================
    #  ステータスバッジ更新
    # =========================================================
    def _set_status(self, text: str, color: str):
        self.lbl_status.configure(text=text, text_color=color)


# =========================================================
#  エントリーポイント
# =========================================================
if __name__ == "__main__":
    app = DiveApp()
    app.mainloop()
