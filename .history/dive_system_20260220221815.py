"""
dive_system.py ── まちゃだん VRMMO ダイブ端末
----------------------------------------------
起動方法:
  .venv/Scripts/python.exe dive_system.py
"""

import os
import json
import time
import threading
import re
import subprocess
import requests
import customtkinter as ctk

PROJECT_ROOT  = os.path.dirname(os.path.abspath(__file__))
SCENE_JSON    = os.path.join(PROJECT_ROOT, "index_scene.json")
STATUS_JSON   = os.path.join(PROJECT_ROOT, "status.json")
VOICE_FILE    = os.path.join(PROJECT_ROOT, "04_Assets", "voice_out.wav")
API_URL       = "http://127.0.0.1:5000/action"
POLL_MS       = 1500

# ── カラー ─────────────────────────────────
BG         = "#0a0005"
PANEL      = "#100208"
BORDER     = "#3a0015"
TEXT       = "#e0d0d0"
TEXT_GM    = "#ff9999"
TEXT_DIM   = "#555555"
BTN_FG     = "#1e0008"
BTN_HOVER  = "#3a0012"
BTN_BORDER = "#660022"
BTN_TEXT   = "#ffcccc"
GOLD       = "#ffdd88"
GREEN      = "#44ff44"
YELLOW     = "#ffdd44"
RED        = "#ff3333"


class DiveApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("⛧ まちゃだん  DIVE TERMINAL")
        self.geometry("1040x740")
        self.configure(fg_color=BG)
        self.minsize(800, 600)

        self._last_ts: float = 0.0
        self._waiting: bool = False

        self._build_ui()
        self._show_prologue()
        self.after(POLL_MS, self._poll)

    # ─────────────────────────────────────────
    #  UI 構築
    # ─────────────────────────────────────────
    def _build_ui(self):
        # ヘッダー
        hdr = ctk.CTkFrame(self, fg_color=PANEL, height=46, corner_radius=0,
                           border_width=1, border_color=BORDER)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        ctk.CTkLabel(hdr, text="⛧  まちゃだん  DIVE TERMINAL",
                     font=ctk.CTkFont("Yu Mincho", 18),
                     text_color="#8b0000").pack(side="left", padx=20)

        self.lbl_dice = ctk.CTkLabel(hdr, text="🎲 ──",
                                     font=ctk.CTkFont("Consolas", 12),
                                     text_color=GOLD)
        self.lbl_dice.pack(side="right", padx=12)

        self.lbl_status = ctk.CTkLabel(hdr, text="● 待機中",
                                       font=ctk.CTkFont("Consolas", 11),
                                       text_color=GREEN)
        self.lbl_status.pack(side="right", padx=16)

        # 本体 2カラム
        body = ctk.CTkFrame(self, fg_color=BG)
        body.pack(fill="both", expand=True, padx=12, pady=10)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        # 左: 状況テキスト
        left = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=6,
                             border_width=1, border_color=BORDER)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.txt = ctk.CTkTextbox(left, fg_color=PANEL, text_color=TEXT,
                                   font=ctk.CTkFont("Yu Mincho", 15),
                                   wrap="word", state="disabled", border_width=0)
        self.txt.pack(fill="both", expand=True, padx=12, pady=12)

        # 右: ボタンエリア
        right = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=6,
                              border_width=1, border_color=BORDER)
        right.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(right, text="── 選択 ──", text_color=TEXT_DIM,
                     font=ctk.CTkFont("Yu Mincho", 11)).pack(pady=(14, 4))

        self.choices_frame = ctk.CTkScrollableFrame(
            right, fg_color=PANEL,
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color="#5a0025"
        )
        self.choices_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # フッター (GMセリフ)
        ftr = ctk.CTkFrame(self, fg_color=PANEL, height=32, corner_radius=0,
                           border_width=1, border_color=BORDER)
        ftr.pack(fill="x")
        ftr.pack_propagate(False)

        self.lbl_voice = ctk.CTkLabel(ftr, text="",
                                      text_color=TEXT_GM,
                                      font=ctk.CTkFont("Yu Mincho", 12))
        self.lbl_voice.pack(side="left", padx=16)

    # ─────────────────────────────────────────
    #  プロローグ（初期選択画面）
    # ─────────────────────────────────────────
    def _show_prologue(self):
        self._set_text(
            "あなたは気がつくと、見知らぬ世界に立っていた。\n\n"
            "ここは【男性が絶滅した世界】。\n"
            "目の前に、3人の少女が現れる。\n"
            "彼女たちの瞳が、あなたの存在に怪しく潤む……。"
        )
        self.lbl_voice.configure(text="りりす  「ふふ、いらっしゃい……。あなたの運命の相手を選んで？」")
        self._clear_choices()
        choices = [
            ("🛡️  アリア ── 堕ちた聖騎士",  "ヒロイン選択: アリア（聖堂騎士）",  "高潔な鎧の下に隠された、種の保存本能。"),
            ("🐺  ゼナ ── 黒狼の番い",       "ヒロイン選択: ゼナ（黒狼の獣人）",   "「よこせ！ それは俺の獲物だ！」"),
            ("🧙‍♀️  エララ ── 母性の魔女",    "ヒロイン選択: エララ（蒼の魔女）",   "「坊や、お姉さんが搾ってあげる♥」"),
            ("─" * 22, None, ""),
            ("🎲  ダイスに委ねる",            "ダイスで運命に委ねる",               "運命があなたの相手を決める。"),
        ]
        for label, action, sub in choices:
            if action is None:
                ctk.CTkLabel(self.choices_frame, text=label,
                             text_color=BORDER,
                             font=ctk.CTkFont("Consolas", 10)).pack(pady=2)
            else:
                self._add_btn(f"{label}\n{sub}" if sub else label, action)

    # ─────────────────────────────────────────
    #  テキスト・ボタン操作
    # ─────────────────────────────────────────
    def _set_text(self, text: str):
        clean = re.sub(r"<[^>]+>", "", text.replace("<br>", "\n").replace("<br/>", "\n"))
        self.txt.configure(state="normal")
        self.txt.delete("1.0", "end")
        self.txt.insert("end", clean)
        self.txt.configure(state="disabled")

    def _clear_choices(self):
        for w in self.choices_frame.winfo_children():
            w.destroy()

    def _add_btn(self, label: str, action: str):
        ctk.CTkButton(
            self.choices_frame,
            text=label,
            text_color=BTN_TEXT,
            fg_color=BTN_FG,
            hover_color=BTN_HOVER,
            border_color=BTN_BORDER,
            border_width=1,
            corner_radius=3,
            font=ctk.CTkFont("Yu Mincho", 14),
            anchor="w",
            command=lambda a=action: self._send_action(a),
        ).pack(fill="x", pady=5, padx=4)

    def _render_ui_html(self, html: str):
        """LLMが返した ui_html からボタンを抽出"""
        self._clear_choices()
        actions = re.findall(r'sendAction\(["\'](.+?)["\']', html)
        labels  = re.findall(r'>([^<]+)</button>', html)
        if not actions:
            self._add_btn("次へ……", "続きを読む")
            return
        for i, act in enumerate(actions):
            lbl = labels[i].strip() if i < len(labels) else act
            self._add_btn(lbl, act)

    # ─────────────────────────────────────────
    #  アクション送信
    # ─────────────────────────────────────────
    def _send_action(self, action: str):
        if self._waiting:
            return
        self._waiting = True
        self._set_status("⏳ 思考中……", YELLOW)
        self._clear_choices()
        ctk.CTkLabel(self.choices_frame,
                     text="りりすが思考しています……",
                     text_color=TEXT_DIM,
                     font=ctk.CTkFont("Yu Mincho", 13)).pack(pady=40)

        def _post():
            try:
                r = requests.post(API_URL,
                                  json={"action": action, "timestamp": time.time()},
                                  timeout=5)
                if r.status_code == 200:
                    self.after(0, lambda: self._set_status("● AIが動いています……", YELLOW))
                else:
                    self.after(0, lambda: self._on_error(f"HTTP {r.status_code}"))
            except Exception as e:
                self.after(0, lambda: self._on_error(f"接続失敗: {e}"))
        threading.Thread(target=_post, daemon=True).start()

    def _on_error(self, msg: str):
        self._waiting = False
        self._set_status(f"❌ {msg}", RED)
        self._show_prologue()

    # ─────────────────────────────────────────
    #  ポーリング
    # ─────────────────────────────────────────
    def _poll(self):
        if self._waiting:
            threading.Thread(target=self._check_update, daemon=True).start()
        self.after(POLL_MS, self._poll)

    def _check_update(self):
        try:
            with open(STATUS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            ts = data.get("updated_at", 0)
            if ts > self._last_ts:
                self.after(0, lambda: self._load_scene(ts))
        except Exception:
            pass

    def _load_scene(self, ts: float):
        self._last_ts = ts
        try:
            with open(SCENE_JSON, "r", encoding="utf-8") as f:
                scene = json.load(f)
        except Exception as e:
            self._on_error(f"シーン読込失敗: {e}")
            return
        self._apply_scene(scene)

    def _apply_scene(self, scene: dict):
        self._waiting = False
        self._set_status("● 準備完了", GREEN)

        self._set_text(scene.get("situation_text", ""))

        voice_text = scene.get("voice_text", "")
        if voice_text:
            self.lbl_voice.configure(text=f"りりす  「{voice_text[:60]}」")

        dice = scene.get("dice_result", "")
        if dice:
            self.lbl_dice.configure(text=f"🎲 {dice}")

        ui_html = scene.get("ui_html", "")
        if ui_html:
            self._render_ui_html(ui_html)
        else:
            self._show_prologue()

        threading.Thread(target=self._play_voice, daemon=True).start()

    # ─────────────────────────────────────────
    #  音声
    # ─────────────────────────────────────────
    def _play_voice(self):
        try:
            if os.path.exists(VOICE_FILE):
                subprocess.Popen(
                    ["powershell", "-c",
                     f"(New-Object Media.SoundPlayer '{VOICE_FILE}').PlaySync()"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
        except Exception:
            pass

    # ─────────────────────────────────────────
    #  ステータス
    # ─────────────────────────────────────────
    def _set_status(self, text: str, color: str):
        self.lbl_status.configure(text=text, text_color=color)


if __name__ == "__main__":
    app = DiveApp()
    app.mainloop()
