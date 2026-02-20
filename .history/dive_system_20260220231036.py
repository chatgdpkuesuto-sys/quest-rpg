"""
dive_system.py ── まちゃだん VRMMO ダイブ端末
"""

import os, json, time, re, threading, subprocess
import customtkinter as ctk

ROOT       = os.path.dirname(os.path.abspath(__file__))
ACTION_F   = os.path.join(ROOT, "player_action.json")
SCENE_F    = os.path.join(ROOT, "index_scene.json")
STATUS_F   = os.path.join(ROOT, "status.json")
VOICE_F    = os.path.join(ROOT, "04_Assets", "voice_out.wav")
POLL_MS    = 1200

# カラー
BG="#0a0005"; PANEL="#100208"; BORDER="#3a0015"
TEXT="#e0d0d0"; GM="#ff9999"; DIM="#555"
BFG="#1e0008"; BHV="#3a0012"; BBR="#660022"; BT="#ffcccc"
GOLD="#ffdd88"; GREEN="#44ff44"; YELLOW="#ffdd44"; RED="#ff3333"


class DiveApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.title("⛧ まちゃだん  DIVE TERMINAL")
        self.geometry("1040x740")
        self.configure(fg_color=BG)
        self.minsize(800,600)
        self.bind("<F11>", lambda e: self.attributes("-fullscreen",
                  not self.attributes("-fullscreen")))

        self._last_ts = 0.0
        self._waiting = False
        self._build()
        self._show_prologue()
        self.after(POLL_MS, self._poll)

    def _build(self):
        # ヘッダー
        h = ctk.CTkFrame(self, fg_color=PANEL, height=46, corner_radius=0,
                         border_width=1, border_color=BORDER)
        h.pack(fill="x"); h.pack_propagate(False)
        ctk.CTkLabel(h, text="⛧  まちゃだん  DIVE TERMINAL",
                     font=ctk.CTkFont("Yu Mincho",18),
                     text_color="#8b0000").pack(side="left",padx=20)
        self.lbl_dice = ctk.CTkLabel(h, text="🎲 ──",
                        font=ctk.CTkFont("Consolas",12), text_color=GOLD)
        self.lbl_dice.pack(side="right",padx=12)
        self.lbl_st = ctk.CTkLabel(h, text="● 待機中",
                      font=ctk.CTkFont("Consolas",11), text_color=GREEN)
        self.lbl_st.pack(side="right",padx=16)

        # 本体
        body = ctk.CTkFrame(self, fg_color=BG)
        body.pack(fill="both", expand=True, padx=12, pady=10)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        # 左: テキスト
        L = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=6,
                         border_width=1, border_color=BORDER)
        L.grid(row=0,column=0,sticky="nsew",padx=(0,8))
        self.txt = ctk.CTkTextbox(L, fg_color=PANEL, text_color=TEXT,
                    font=ctk.CTkFont("Yu Mincho",15), wrap="word",
                    state="disabled", border_width=0)
        self.txt.pack(fill="both",expand=True,padx=12,pady=12)

        # 右: 選択肢 + 入力
        R = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=6,
                         border_width=1, border_color=BORDER)
        R.grid(row=0,column=1,sticky="nsew")
        ctk.CTkLabel(R, text="── 行動選択 ──", text_color=DIM,
                     font=ctk.CTkFont("Yu Mincho",11)).pack(pady=(14,4))
        self.cf = ctk.CTkScrollableFrame(R, fg_color=PANEL,
                  scrollbar_button_color=BORDER)
        self.cf.pack(fill="both",expand=True,padx=8,pady=(0,4))

        # フリー入力
        inp = ctk.CTkFrame(R, fg_color=PANEL)
        inp.pack(fill="x", padx=8, pady=(0,8))
        self.entry = ctk.CTkEntry(inp, placeholder_text="自由行動を入力…",
                     font=ctk.CTkFont("Yu Mincho",13))
        self.entry.pack(side="left",fill="x",expand=True,padx=(0,4))
        self.entry.bind("<Return>", lambda e: self._send(self.entry.get()))
        ctk.CTkButton(inp, text="実行", width=60, fg_color=BFG,
                      hover_color=BHV, border_color=BBR, border_width=1,
                      font=ctk.CTkFont("Yu Mincho",12),
                      command=lambda: self._send(self.entry.get())).pack(side="right")

        # フッター
        f = ctk.CTkFrame(self, fg_color=PANEL, height=32, corner_radius=0,
                         border_width=1, border_color=BORDER)
        f.pack(fill="x"); f.pack_propagate(False)
        self.lbl_v = ctk.CTkLabel(f, text="", text_color=GM,
                     font=ctk.CTkFont("Yu Mincho",12))
        self.lbl_v.pack(side="left",padx=16)

    # === プロローグ ===
    def _show_prologue(self):
        self._set_text(
            "あなたは気がつくと、見知らぬ世界に立っていた。\n\n"
            "ここは【男性が絶滅した世界】。\n"
            "目の前に、3人の少女が現れる。\n"
            "彼女たちの瞳が、あなたの存在に怪しく潤む……。")
        self.lbl_v.configure(text="りりす「ふふ、いらっしゃい……。あなたの運命の相手を選んで？」")
        self._clear()
        for label, action, sub in [
            ("🛡️  アリア ── 堕ちた聖騎士","ヒロイン選択: アリア","高潔な鎧の下に隠された本能"),
            ("🐺  ゼナ ── 黒狼の番い","ヒロイン選択: ゼナ","「よこせ！ 俺の獲物だ！」"),
            ("🧙‍♀️  エララ ── 母性の魔女","ヒロイン選択: エララ","「坊や、搾ってあげる♥」"),
            ("🎲  ダイスに委ねる","ダイスで運命に委ねる","運命が相手を決める"),
        ]:
            self._btn(f"{label}\n{sub}",action)

    # === テキスト ===
    def _set_text(self, t):
        c = re.sub(r"<[^>]+>","", t.replace("<br>","\n").replace("<br/>","\n"))
        self.txt.configure(state="normal")
        self.txt.delete("1.0","end")
        self.txt.insert("end", c)
        self.txt.configure(state="disabled")

    def _clear(self):
        for w in self.cf.winfo_children(): w.destroy()

    def _btn(self, label, action):
        ctk.CTkButton(self.cf, text=label, text_color=BT, fg_color=BFG,
                      hover_color=BHV, border_color=BBR, border_width=1,
                      corner_radius=3, font=ctk.CTkFont("Yu Mincho",14),
                      anchor="w",
                      command=lambda a=action: self._send(a)
                      ).pack(fill="x",pady=5,padx=4)

    def _parse_html(self, html):
        self._clear()
        acts = re.findall(r'sendAction\(["\'](.+?)["\']', html)
        lbls = re.findall(r'>([^<]+)</button>', html)
        if not acts:
            self._btn("次へ……","続きを読む")
            return
        for i, a in enumerate(acts):
            self._btn(lbls[i].strip() if i<len(lbls) else a, a)

    # === アクション送信（ファイル直書き） ===
    def _send(self, action):
        if not action or self._waiting:
            return
        self._waiting = True
        self.lbl_st.configure(text="⏳ りりす思考中……", text_color=YELLOW)
        self._clear()
        ctk.CTkLabel(self.cf, text="りりすが世界を紡いでいます……",
                     text_color=DIM,
                     font=ctk.CTkFont("Yu Mincho",13)).pack(pady=40)
        self.entry.delete(0,"end")

        def _write():
            try:
                with open(ACTION_F, "w", encoding="utf-8") as f:
                    json.dump({"action": action, "timestamp": time.time()},
                              f, ensure_ascii=False, indent=4)
            except Exception:
                self.after(0, lambda: self._error("ファイル書き込み失敗"))
        threading.Thread(target=_write, daemon=True).start()

    def _error(self, msg):
        self._waiting = False
        self.lbl_st.configure(text=f"❌ {msg}", text_color=RED)
        self._show_prologue()

    # === ポーリング ===
    def _poll(self):
        if self._waiting:
            threading.Thread(target=self._check, daemon=True).start()
        self.after(POLL_MS, self._poll)

    def _check(self):
        try:
            with open(STATUS_F,"r",encoding="utf-8") as f:
                d = json.load(f)
            ts = d.get("updated_at",0)
            if ts > self._last_ts:
                self.after(0, lambda: self._load(ts))
        except Exception:
            pass

    def _load(self, ts):
        self._last_ts = ts
        try:
            with open(SCENE_F,"r",encoding="utf-8") as f:
                s = json.load(f)
        except Exception as e:
            self._error(f"シーン読込失敗: {e}"); return
        self._apply(s)

    def _apply(self, s):
        self._waiting = False
        self.lbl_st.configure(text="● 世界は安定している", text_color=GREEN)
        self._set_text(s.get("situation_text",""))
        v = s.get("voice_text","")
        if v: self.lbl_v.configure(text=f"りりす「{v[:60]}」")
        d = s.get("dice_result","")
        if d: self.lbl_dice.configure(text=f"🎲 {d}")
        html = s.get("ui_html","")
        if html: self._parse_html(html)
        else: self._show_prologue()
        threading.Thread(target=self._voice, daemon=True).start()

    def _voice(self):
        try:
            if os.path.exists(VOICE_F):
                subprocess.Popen(
                    ["powershell","-c",
                     f"(New-Object Media.SoundPlayer '{VOICE_F}').PlaySync()"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception: pass


if __name__ == "__main__":
    app = DiveApp()
    app.mainloop()
