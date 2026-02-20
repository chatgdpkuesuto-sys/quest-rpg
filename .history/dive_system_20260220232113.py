"""
dive_system.py ── まちゃだん VRMMO ダイブ端末（完全版）
イラスト表示 / VOICEVOX音声 / BGMループ / フルスクリーン対応
"""

import os, json, time, re, threading, subprocess, glob
import customtkinter as ctk
from PIL import Image, ImageTk

# ===== pygame BGM =====
try:
    import pygame
    pygame.mixer.init(frequency=22050)
    HAS_PYGAME = True
except Exception:
    HAS_PYGAME = False

ROOT       = os.path.dirname(os.path.abspath(__file__))
ACTION_F   = os.path.join(ROOT, "player_action.json")
SCENE_F    = os.path.join(ROOT, "index_scene.json")
STATUS_F   = os.path.join(ROOT, "status.json")
VOICE_F    = os.path.join(ROOT, "04_Assets", "voice_out.wav")
COMFY_OUT  = os.path.join(os.path.expanduser("~"), "ComfyUI", "output")
BGM_DIR    = os.path.join(ROOT, "04_Assets", "bgm")
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
        self.title("\u26e7 \u307e\u3061\u3083\u3060\u3093  DIVE TERMINAL")
        self.geometry("1200x780")
        self.configure(fg_color=BG)
        self.minsize(900, 650)
        self.bind("<F11>", lambda e: self.attributes("-fullscreen",
                  not self.attributes("-fullscreen")))
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        self._last_ts = 0.0
        self._waiting = False
        self._img_ref = None     # GC防止
        self._last_comfy_idx = 0 # 最後に読んだComfyUI画像

        self._build()
        self._show_prologue()
        self._start_bgm()
        self.after(POLL_MS, self._poll)

    # ================================================================
    #  UI構築
    # ================================================================
    def _build(self):
        # ── ヘッダー ──
        h = ctk.CTkFrame(self, fg_color=PANEL, height=46, corner_radius=0,
                         border_width=1, border_color=BORDER)
        h.pack(fill="x"); h.pack_propagate(False)
        ctk.CTkLabel(h, text="\u26e7  \u307e\u3061\u3083\u3060\u3093  DIVE TERMINAL",
                     font=ctk.CTkFont("Yu Mincho",18),
                     text_color="#8b0000").pack(side="left",padx=20)
        self.lbl_dice = ctk.CTkLabel(h, text="\U0001f3b2 \u2500\u2500",
                        font=ctk.CTkFont("Consolas",12), text_color=GOLD)
        self.lbl_dice.pack(side="right",padx=12)
        self.lbl_st = ctk.CTkLabel(h, text="\u25cf \u5f85\u6a5f\u4e2d",
                      font=ctk.CTkFont("Consolas",11), text_color=GREEN)
        self.lbl_st.pack(side="right",padx=16)
        # BGM ボタン
        self.btn_bgm = ctk.CTkButton(h, text="\u266b BGM", width=60,
                       fg_color=BFG, hover_color=BHV, border_width=1,
                       border_color=BBR, font=ctk.CTkFont("Consolas",10),
                       command=self._toggle_bgm)
        self.btn_bgm.pack(side="right",padx=4)

        # ── メインボディ（3カラム） ──
        body = ctk.CTkFrame(self, fg_color=BG)
        body.pack(fill="both", expand=True, padx=10, pady=8)
        body.columnconfigure(0, weight=3)  # 左: テキスト
        body.columnconfigure(1, weight=2)  # 中: イラスト
        body.columnconfigure(2, weight=2)  # 右: 選択肢
        body.rowconfigure(0, weight=1)

        # 左: 状況テキスト
        L = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=6,
                         border_width=1, border_color=BORDER)
        L.grid(row=0, column=0, sticky="nsew", padx=(0,6))
        self.txt = ctk.CTkTextbox(L, fg_color=PANEL, text_color=TEXT,
                    font=ctk.CTkFont("Yu Mincho",15), wrap="word",
                    state="disabled", border_width=0)
        self.txt.pack(fill="both", expand=True, padx=12, pady=12)

        # 中: イラストパネル
        M = ctk.CTkFrame(body, fg_color="#050002", corner_radius=6,
                         border_width=1, border_color=BORDER)
        M.grid(row=0, column=1, sticky="nsew", padx=(0,6))
        self.img_label = ctk.CTkLabel(M, text="\u3014 \u821e\u53f0\u88cf \u3015",
                          text_color=DIM, font=ctk.CTkFont("Yu Mincho",14),
                          fg_color="#050002")
        self.img_label.pack(fill="both", expand=True, padx=4, pady=4)

        # 右: 選択肢 + 入力
        R = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=6,
                         border_width=1, border_color=BORDER)
        R.grid(row=0, column=2, sticky="nsew")
        ctk.CTkLabel(R, text="\u2500\u2500 \u884c\u52d5\u9078\u629e \u2500\u2500",
                     text_color=DIM,
                     font=ctk.CTkFont("Yu Mincho",11)).pack(pady=(14,4))
        self.cf = ctk.CTkScrollableFrame(R, fg_color=PANEL,
                  scrollbar_button_color=BORDER)
        self.cf.pack(fill="both", expand=True, padx=8, pady=(0,4))

        # フリー入力
        inp = ctk.CTkFrame(R, fg_color=PANEL)
        inp.pack(fill="x", padx=8, pady=(0,8))
        self.entry = ctk.CTkEntry(inp, placeholder_text="\u81ea\u7531\u884c\u52d5\u3092\u5165\u529b\u2026",
                     font=ctk.CTkFont("Yu Mincho",13))
        self.entry.pack(side="left", fill="x", expand=True, padx=(0,4))
        self.entry.bind("<Return>", lambda e: self._send(self.entry.get()))
        ctk.CTkButton(inp, text="\u5b9f\u884c", width=60, fg_color=BFG,
                      hover_color=BHV, border_color=BBR, border_width=1,
                      font=ctk.CTkFont("Yu Mincho",12),
                      command=lambda: self._send(self.entry.get())).pack(side="right")

        # ── フッター ──
        f = ctk.CTkFrame(self, fg_color=PANEL, height=34, corner_radius=0,
                         border_width=1, border_color=BORDER)
        f.pack(fill="x"); f.pack_propagate(False)
        self.lbl_v = ctk.CTkLabel(f, text="", text_color=GM,
                     font=ctk.CTkFont("Yu Mincho",12))
        self.lbl_v.pack(side="left", padx=16)

    # ================================================================
    #  BGM
    # ================================================================
    _bgm_playing = False

    def _start_bgm(self):
        if not HAS_PYGAME:
            return
        # BGMフォルダがなければ作る
        os.makedirs(BGM_DIR, exist_ok=True)
        files = glob.glob(os.path.join(BGM_DIR, "*.wav")) + \
                glob.glob(os.path.join(BGM_DIR, "*.mp3")) + \
                glob.glob(os.path.join(BGM_DIR, "*.ogg"))
        if not files:
            return
        try:
            pygame.mixer.music.load(files[0])
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(loops=-1)
            self._bgm_playing = True
        except Exception:
            pass

    def _toggle_bgm(self):
        if not HAS_PYGAME:
            return
        if self._bgm_playing:
            pygame.mixer.music.pause()
            self._bgm_playing = False
            self.btn_bgm.configure(text="\u266b BGM OFF")
        else:
            pygame.mixer.music.unpause()
            self._bgm_playing = True
            self.btn_bgm.configure(text="\u266b BGM")

    # ================================================================
    #  プロローグ
    # ================================================================
    def _show_prologue(self):
        self._set_text(
            "\u3042\u306a\u305f\u306f\u6c17\u304c\u3064\u304f\u3068\u3001\u898b\u77e5\u3089\u306c\u4e16\u754c\u306b\u7acb\u3063\u3066\u3044\u305f\u3002\n\n"
            "\u3053\u3053\u306f\u3010\u7537\u6027\u304c\u7d76\u6ec5\u3057\u305f\u4e16\u754c\u3011\u3002\n"
            "\u76ee\u306e\u524d\u306b\u30013\u4eba\u306e\u5c11\u5973\u304c\u73fe\u308c\u308b\u3002\n"
            "\u5f7c\u5973\u305f\u3061\u306e\u77b3\u304c\u3001\u3042\u306a\u305f\u306e\u5b58\u5728\u306b\u602a\u3057\u304f\u6f64\u3080\u2026\u2026\u3002")
        self.lbl_v.configure(text="\u308a\u308a\u3059\u300c\u3075\u3075\u3001\u3044\u3089\u3063\u3057\u3083\u3044\u2026\u2026\u3002\u904b\u547d\u306e\u76f8\u624b\u3092\u9078\u3093\u3067\uff1f\u300d")
        self._clear()
        for label, action, sub in [
            ("\U0001f6e1\ufe0f  \u30a2\u30ea\u30a2 \u2500\u2500 \u5819\u3061\u305f\u8056\u9a0e\u58eb",
             "\u30d2\u30ed\u30a4\u30f3\u9078\u629e: \u30a2\u30ea\u30a2",
             "\u9ad8\u6f54\u306a\u93a7\u306e\u4e0b\u306b\u96a0\u3055\u308c\u305f\u672c\u80fd"),
            ("\U0001f43a  \u30bc\u30ca \u2500\u2500 \u9ed2\u72fc\u306e\u756a\u3044",
             "\u30d2\u30ed\u30a4\u30f3\u9078\u629e: \u30bc\u30ca",
             "\u300c\u3088\u3053\u305b\uff01 \u4ffa\u306e\u7372\u7269\u3060\uff01\u300d"),
            ("\U0001f9d9\u200d\u2640\ufe0f  \u30a8\u30e9\u30e9 \u2500\u2500 \u6bcd\u6027\u306e\u9b54\u5973",
             "\u30d2\u30ed\u30a4\u30f3\u9078\u629e: \u30a8\u30e9\u30e9",
             "\u300c\u574a\u3084\u3001\u643e\u3063\u3066\u3042\u3052\u308b\u2665\u300d"),
            ("\U0001f3b2  \u30c0\u30a4\u30b9\u306b\u59d4\u306d\u308b",
             "\u30c0\u30a4\u30b9\u3067\u904b\u547d\u306b\u59d4\u306d\u308b",
             "\u904b\u547d\u304c\u76f8\u624b\u3092\u6c7a\u3081\u308b"),
        ]:
            self._btn(f"{label}\n{sub}", action)
        # 最新のComfyUI画像を表示
        self._show_latest_image()

    # ================================================================
    #  画像表示
    # ================================================================
    def _show_latest_image(self, specific_path=None):
        """ComfyUI の最新出力画像を右パネルに表示"""
        def _load():
            path = specific_path
            if not path:
                pngs = sorted(glob.glob(os.path.join(COMFY_OUT, "ComfyUI_*.png")))
                if not pngs:
                    return
                path = pngs[-1]
            if not os.path.exists(path):
                return
            try:
                img = Image.open(path)
                # パネルサイズにフィット
                max_w, max_h = 340, 500
                img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.after(0, lambda: self._set_image(photo))
            except Exception:
                pass
        threading.Thread(target=_load, daemon=True).start()

    def _set_image(self, photo):
        self._img_ref = photo  # GC防止
        self.img_label.configure(image=photo, text="")

    # ================================================================
    #  テキスト / ボタン
    # ================================================================
    def _set_text(self, t):
        c = re.sub(r"<[^>]+>", "", t.replace("<br>","\n").replace("<br/>","\n"))
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
                      ).pack(fill="x", pady=5, padx=4)

    def _parse_html(self, html):
        self._clear()
        acts = re.findall(r'sendAction\(["\'](.+?)["\']', html)
        lbls = re.findall(r'>([^<]+)</button>', html)
        if not acts:
            self._btn("\u6b21\u3078\u2026\u2026", "\u7d9a\u304d\u3092\u8aad\u3080")
            return
        for i, a in enumerate(acts):
            self._btn(lbls[i].strip() if i<len(lbls) else a, a)

    # ================================================================
    #  アクション送信
    # ================================================================
    def _send(self, action):
        if not action or self._waiting: return
        self._waiting = True
        self.lbl_st.configure(text="\u23f3 \u308a\u308a\u3059\u601d\u8003\u4e2d\u2026\u2026", text_color=YELLOW)
        self._clear()
        ctk.CTkLabel(self.cf, text="\u308a\u308a\u3059\u304c\u4e16\u754c\u3092\u7d21\u3044\u3067\u3044\u307e\u3059\u2026\u2026",
                     text_color=DIM,
                     font=ctk.CTkFont("Yu Mincho",13)).pack(pady=40)
        self.entry.delete(0,"end")
        def _w():
            try:
                with open(ACTION_F, "w", encoding="utf-8") as f:
                    json.dump({"action": action, "timestamp": time.time()},
                              f, ensure_ascii=False, indent=4)
            except Exception:
                self.after(0, lambda: self._error("\u30d5\u30a1\u30a4\u30eb\u66f8\u304d\u8fbc\u307f\u5931\u6557"))
        threading.Thread(target=_w, daemon=True).start()

    def _error(self, msg):
        self._waiting = False
        self.lbl_st.configure(text=f"\u274c {msg}", text_color=RED)
        self._show_prologue()

    # ================================================================
    #  ポーリング
    # ================================================================
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
        except Exception: pass

    def _load(self, ts):
        self._last_ts = ts
        try:
            with open(SCENE_F,"r",encoding="utf-8") as f:
                s = json.load(f)
        except Exception as e:
            self._error(f"\u30b7\u30fc\u30f3\u8aad\u8fbc\u5931\u6557: {e}"); return
        self._apply(s)

    def _apply(self, s):
        self._waiting = False
        self.lbl_st.configure(text="\u25cf \u4e16\u754c\u306f\u5b89\u5b9a\u3057\u3066\u3044\u308b", text_color=GREEN)
        self._set_text(s.get("situation_text",""))
        v = s.get("voice_text","")
        if v: self.lbl_v.configure(text=f"\u308a\u308a\u3059\u300c{v[:60]}\u300d")
        d = s.get("dice_result","")
        if d: self.lbl_dice.configure(text=f"\U0001f3b2 {d}")
        html = s.get("ui_html","")
        if html: self._parse_html(html)
        else: self._show_prologue()
        # イラスト更新（ComfyUI最新画像）
        self._show_latest_image()
        # ボイス再生
        threading.Thread(target=self._voice, daemon=True).start()

    # ================================================================
    #  音声再生
    # ================================================================
    def _voice(self):
        try:
            if os.path.exists(VOICE_F):
                # BGMを一時的に小さくする
                if HAS_PYGAME and self._bgm_playing:
                    pygame.mixer.music.set_volume(0.1)
                subprocess.run(
                    ["powershell","-c",
                     f"(New-Object Media.SoundPlayer '{VOICE_F}').PlaySync()"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    timeout=15)
                # BGM音量を戻す
                if HAS_PYGAME and self._bgm_playing:
                    pygame.mixer.music.set_volume(0.3)
        except Exception: pass


if __name__ == "__main__":
    app = DiveApp()
    app.mainloop()
