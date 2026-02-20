"""
dive_system.py ── まちゃだん VRMMO ダイブ端末
イラスト全画面背景 / 半透明UI / VOICEVOX / BGM
"""

import os, json, time, re, threading, subprocess, glob
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance

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

# テーマ色
GM_C  = "#ff9999"
DIM   = "#888888"
GOLD  = "#ffdd88"
GREEN = "#44ff44"
YELLOW= "#ffdd44"
RED   = "#ff3333"
BTN_BG= "#1a0008"


class DiveApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.title("\u26e7 まちゃだん  DIVE TERMINAL")
        self.geometry("1280x800")
        self.configure(fg_color="#000000")
        self.minsize(900, 650)
        self.bind("<F11>", lambda e: self.attributes("-fullscreen",
                  not self.attributes("-fullscreen")))
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        self._last_ts = 0.0
        self._waiting = False
        self._bg_photo = None
        self._comfy_image_count = 0

        self._build()
        self._show_prologue()
        self._load_bg_image()
        self._start_bgm()
        self.after(POLL_MS, self._poll)
        self.bind("<Configure>", self._on_resize)

    # ================================================================
    #  UI（Canvas ベースで画像を全画面背景に）
    # ================================================================
    def _build(self):
        # キャンバス（全画面背景用）
        self.canvas = tk.Canvas(self, bg="#000000", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self._bg_id = self.canvas.create_image(0, 0, anchor="nw")

        # --- 半透明オーバーレイフレーム群（Canvas 上に配置） ---

        # ヘッダー
        hdr = ctk.CTkFrame(self.canvas, fg_color=("gray10","gray10"),
                           corner_radius=0, border_width=0, height=40)
        self.canvas.create_window(0, 0, window=hdr, anchor="nw", width=2000, tags="hdr")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="\u26e7  まちゃだん  DIVE",
                     font=ctk.CTkFont("Yu Mincho",16),
                     text_color="#8b0000").pack(side="left", padx=16)
        self.lbl_dice = ctk.CTkLabel(hdr, text="\U0001f3b2 ──",
                        font=ctk.CTkFont("Consolas",11), text_color=GOLD)
        self.lbl_dice.pack(side="right", padx=10)
        self.lbl_st = ctk.CTkLabel(hdr, text="● 待機中",
                      font=ctk.CTkFont("Consolas",10), text_color=GREEN)
        self.lbl_st.pack(side="right", padx=12)
        self.btn_bgm = ctk.CTkButton(hdr, text="♫", width=32,
                       fg_color=BTN_BG, hover_color="#330010",
                       font=ctk.CTkFont("Consolas",12),
                       command=self._toggle_bgm)
        self.btn_bgm.pack(side="right", padx=4)

        # 左下: テキストパネル（半透明背景）
        self.txt_frame = ctk.CTkFrame(self.canvas, fg_color=("gray4","gray4"),
                                       corner_radius=8, border_width=1,
                                       border_color="#3a0015")
        self.canvas.create_window(16, 54, window=self.txt_frame, anchor="nw",
                                  width=480, height=500, tags="txt_frame")
        self.txt = ctk.CTkTextbox(self.txt_frame, fg_color="transparent",
                    text_color="#e8e0e0",
                    font=ctk.CTkFont("Yu Mincho",15), wrap="word",
                    state="disabled", border_width=0)
        self.txt.pack(fill="both", expand=True, padx=10, pady=10)

        # 右下: 選択肢パネル
        self.choice_frame = ctk.CTkFrame(self.canvas, fg_color=("gray4","gray4"),
                                          corner_radius=8, border_width=1,
                                          border_color="#3a0015")
        self.canvas.create_window(0, 54, window=self.choice_frame, anchor="ne",
                                  width=320, height=500, tags="choice_frame")
        ctk.CTkLabel(self.choice_frame, text="── 行動選択 ──",
                     text_color=DIM,
                     font=ctk.CTkFont("Yu Mincho",11)).pack(pady=(10,4))
        self.cf = ctk.CTkScrollableFrame(self.choice_frame, fg_color="transparent",
                  scrollbar_button_color="#3a0015")
        self.cf.pack(fill="both", expand=True, padx=6, pady=(0,4))

        # フリー入力
        inp = ctk.CTkFrame(self.choice_frame, fg_color="transparent")
        inp.pack(fill="x", padx=6, pady=(0,8))
        self.entry = ctk.CTkEntry(inp, placeholder_text="自由行動を入力…",
                     font=ctk.CTkFont("Yu Mincho",12))
        self.entry.pack(side="left", fill="x", expand=True, padx=(0,4))
        self.entry.bind("<Return>", lambda e: self._send(self.entry.get()))
        ctk.CTkButton(inp, text="実行", width=50, fg_color=BTN_BG,
                      hover_color="#330010",
                      font=ctk.CTkFont("Yu Mincho",11),
                      command=lambda: self._send(self.entry.get())).pack(side="right")

        # フッター: GMボイス
        self.voice_frame = ctk.CTkFrame(self.canvas, fg_color=("gray4","gray4"),
                                         corner_radius=0, height=30,
                                         border_width=0)
        self.canvas.create_window(0, 0, window=self.voice_frame, anchor="sw",
                                  width=2000, tags="voice_frame")
        self.voice_frame.pack_propagate(False)
        self.lbl_v = ctk.CTkLabel(self.voice_frame, text="",
                     text_color=GM_C,
                     font=ctk.CTkFont("Yu Mincho",12))
        self.lbl_v.pack(side="left", padx=16)

    def _on_resize(self, event=None):
        """ウィンドウリサイズ時にUI要素の位置を調整"""
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 100 or h < 100:
            return
        # ヘッダー
        self.canvas.coords("hdr", 0, 0)
        self.canvas.itemconfigure("hdr", width=w)
        # テキストパネル（左下）
        txt_w = min(int(w * 0.42), 550)
        txt_h = h - 110
        self.canvas.coords("txt_frame", 16, 50)
        self.canvas.itemconfigure("txt_frame", width=txt_w, height=txt_h)
        # 選択肢パネル（右下）
        ch_w = min(int(w * 0.3), 360)
        self.canvas.coords("choice_frame", w - 16, 50)
        self.canvas.itemconfigure("choice_frame", width=ch_w, height=txt_h)
        # フッター
        self.canvas.coords("voice_frame", 0, h)
        self.canvas.itemconfigure("voice_frame", width=w)
        # 背景画像リサイズ
        if self._bg_photo:
            self._refresh_bg()

    # ================================================================
    #  全画面背景画像
    # ================================================================
    def _load_bg_image(self, path=None):
        def _do():
            if not path:
                pngs = sorted(glob.glob(os.path.join(COMFY_OUT, "ComfyUI_*.png")))
                if not pngs:
                    return
                p = pngs[-1]
            else:
                p = path
            if not os.path.exists(p):
                return
            try:
                img = Image.open(p)
                # 少し暗くして文字の可読性を確保
                img = ImageEnhance.Brightness(img).enhance(0.55)
                self._raw_bg = img
                self.after(0, self._refresh_bg)
            except Exception:
                pass
        threading.Thread(target=_do, daemon=True).start()

    def _refresh_bg(self):
        if not hasattr(self, '_raw_bg'):
            return
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 100 or h < 100:
            return
        img = self._raw_bg.copy()
        # アスペクト比を保ちつつ画面を覆う（cover）
        iw, ih = img.size
        scale = max(w / iw, h / ih)
        nw, nh = int(iw * scale), int(ih * scale)
        img = img.resize((nw, nh), Image.Resampling.LANCZOS)
        # 中央クロップ
        left = (nw - w) // 2
        top = (nh - h) // 2
        img = img.crop((left, top, left + w, top + h))
        self._bg_photo = ImageTk.PhotoImage(img)
        self.canvas.itemconfigure(self._bg_id, image=self._bg_photo)

    # ================================================================
    #  BGM
    # ================================================================
    _bgm_playing = False

    def _start_bgm(self):
        if not HAS_PYGAME:
            return
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
        if not HAS_PYGAME: return
        if self._bgm_playing:
            pygame.mixer.music.pause()
            self._bgm_playing = False
        else:
            pygame.mixer.music.unpause()
            self._bgm_playing = True

    # ================================================================
    #  プロローグ
    # ================================================================
    def _show_prologue(self):
        self._set_text(
            "あなたは気がつくと、見知らぬ世界に立っていた。\n\n"
            "ここは【男性が絶滅した世界】。\n"
            "目の前に、3人の少女が現れる。\n"
            "彼女たちの瞳が、あなたの存在に怪しく潤む……。")
        self.lbl_v.configure(text="りりす「ふふ、いらっしゃい……。運命の相手を選んで？」")
        self._clear()
        for label, action, sub in [
            ("\U0001f6e1  アリア ── 堕ちた聖騎士",
             "ヒロイン選択: アリア", "高潔な鎧の下に隠された本能"),
            ("\U0001f43a  ゼナ ── 黒狼の番い",
             "ヒロイン選択: ゼナ", "「よこせ！ 俺の獲物だ！」"),
            ("\U0001f9d9  エララ ── 母性の魔女",
             "ヒロイン選択: エララ", "「坊や、搾ってあげる\u2665」"),
            ("\U0001f3b2  ダイスに委ねる",
             "ダイスで運命に委ねる", "運命が相手を決める"),
        ]:
            self._btn(f"{label}\n{sub}", action)

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
        ctk.CTkButton(self.cf, text=label, text_color="#ffcccc",
                      fg_color=BTN_BG, hover_color="#3a0012",
                      border_color="#660022", border_width=1,
                      corner_radius=3, font=ctk.CTkFont("Yu Mincho",13),
                      anchor="w",
                      command=lambda a=action: self._send(a)
                      ).pack(fill="x", pady=4, padx=4)

    def _parse_html(self, html):
        self._clear()
        acts = re.findall(r'sendAction\(["\'](.+?)["\']', html)
        lbls = re.findall(r'>([^<]+)</button>', html)
        if not acts:
            self._btn("次へ……", "続きを読む")
            return
        for i, a in enumerate(acts):
            self._btn(lbls[i].strip() if i < len(lbls) else a, a)

    # ================================================================
    #  アクション送信
    # ================================================================
    def _send(self, action):
        if not action or self._waiting: return
        self._waiting = True
        self.lbl_st.configure(text="⏳ りりす思考中……", text_color=YELLOW)
        self._clear()
        ctk.CTkLabel(self.cf, text="りりすが世界を\n紡いでいます……",
                     text_color=DIM,
                     font=ctk.CTkFont("Yu Mincho",13)).pack(pady=40)
        self.entry.delete(0,"end")
        # 現在のComfyUI画像数を記録
        self._comfy_image_count = len(glob.glob(
            os.path.join(COMFY_OUT, "ComfyUI_*.png")))
        def _w():
            try:
                with open(ACTION_F, "w", encoding="utf-8") as f:
                    json.dump({"action": action, "timestamp": time.time()},
                              f, ensure_ascii=False, indent=4)
            except Exception:
                self.after(0, lambda: self._error("ファイル書き込み失敗"))
        threading.Thread(target=_w, daemon=True).start()

    def _error(self, msg):
        self._waiting = False
        self.lbl_st.configure(text=f"❌ {msg}", text_color=RED)
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
            with open(STATUS_F, "r", encoding="utf-8") as f:
                d = json.load(f)
            ts = d.get("updated_at", 0)
            if ts > self._last_ts:
                self.after(0, lambda: self._load(ts))
        except Exception:
            pass

    def _load(self, ts):
        self._last_ts = ts
        try:
            with open(SCENE_F, "r", encoding="utf-8") as f:
                s = json.load(f)
        except Exception as e:
            self._error(f"シーン読込失敗: {e}"); return
        self._apply(s)

    def _apply(self, s):
        self._waiting = False
        self.lbl_st.configure(text="● 世界は安定している", text_color=GREEN)
        self._set_text(s.get("situation_text", ""))
        v = s.get("voice_text", "")
        if v: self.lbl_v.configure(text=f"りりす「{v[:60]}」")
        d = s.get("dice_result", "")
        if d: self.lbl_dice.configure(text=f"\U0001f3b2 {d}")
        html = s.get("ui_html", "")
        if html: self._parse_html(html)
        else: self._show_prologue()
        # ComfyUI の新しい画像を待って背景更新
        threading.Thread(target=self._wait_for_new_image, daemon=True).start()
        # ボイス再生
        threading.Thread(target=self._voice, daemon=True).start()

    def _wait_for_new_image(self):
        """ComfyUI が新しい画像を生成するまで最大30秒待つ"""
        for _ in range(30):
            pngs = sorted(glob.glob(os.path.join(COMFY_OUT, "ComfyUI_*.png")))
            if len(pngs) > self._comfy_image_count:
                newest = pngs[-1]
                # 書き込み完了を少し待つ
                time.sleep(1)
                self.after(0, lambda p=newest: self._load_bg_image(p))
                return
            time.sleep(1)
        # タイムアウト: 既存の最新画像を使う
        pngs = sorted(glob.glob(os.path.join(COMFY_OUT, "ComfyUI_*.png")))
        if pngs:
            self.after(0, lambda p=pngs[-1]: self._load_bg_image(p))

    # ================================================================
    #  音声
    # ================================================================
    def _voice(self):
        try:
            if os.path.exists(VOICE_F):
                if HAS_PYGAME and self._bgm_playing:
                    pygame.mixer.music.set_volume(0.1)
                subprocess.run(
                    ["powershell", "-c",
                     f"(New-Object Media.SoundPlayer '{VOICE_F}').PlaySync()"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    timeout=15)
                if HAS_PYGAME and self._bgm_playing:
                    pygame.mixer.music.set_volume(0.3)
        except Exception:
            pass


if __name__ == "__main__":
    app = DiveApp()
    app.mainloop()
