"""
renderer.py — Pygame フルスクリーンレンダラー
UIボタン一切なし。画面全体が一枚絵、テキストはタイプライター表示。
"""

import os
import sys
import json
import pygame
from pathlib import Path
from typing import Optional


def load_config() -> dict:
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


class Renderer:
    """Pygame フルスクリーン描画エンジン。"""

    # カラーパレット（ダークファンタジー）
    COLOR_BG = (10, 10, 15)
    COLOR_OVERLAY = (0, 0, 0, 180)
    COLOR_TEXT = (220, 215, 200)
    COLOR_HIGHLIGHT = (200, 160, 80)
    COLOR_CHOICE = (180, 140, 60)
    COLOR_CHOICE_HOVER = (255, 200, 100)
    COLOR_DIM = (120, 110, 100)
    COLOR_SCENE_BORDER = (60, 50, 40)

    def __init__(self, config: Optional[dict] = None):
        self.config = config or load_config()
        self.render_config = self.config["renderer"]
        self.fullscreen = self.render_config["fullscreen"]
        self.text_speed = self.render_config["text_speed"]  # ms per character
        self.font_size = self.render_config["font_size"]

        pygame.init()
        pygame.mixer.init()

        # ディスプレイ設定
        display_info = pygame.display.Info()
        self.screen_w = display_info.current_w
        self.screen_h = display_info.current_h

        if self.fullscreen:
            self.screen = pygame.display.set_mode(
                (self.screen_w, self.screen_h), pygame.FULLSCREEN
            )
        else:
            self.screen_w = 1280
            self.screen_h = 720
            self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))

        pygame.display.set_caption("NOCTURNAL — 暗黒幻想VRMMO")

        # フォント設定（日本語対応）
        self.font = self._load_japanese_font(self.font_size)
        self.font_small = self._load_japanese_font(int(self.font_size * 0.75))
        self.font_large = self._load_japanese_font(int(self.font_size * 1.3))

        # クロック
        self.clock = pygame.time.Clock()

        # 表示状態
        self.current_image: Optional[pygame.Surface] = None
        self.current_chara: Optional[pygame.Surface] = None
        self.current_prop: Optional[pygame.Surface] = None
        self.scene_text: str = ""
        self.dialogue_text: str = ""
        self.choices: list[str] = []
        self.displayed_chars: int = 0
        self.text_complete: bool = False
        self.last_char_time: int = 0
        self.selected_choice: int = -1  # ホバー中の選択肢

        # フェード
        self.fade_alpha: int = 0
        self.fading_in: bool = False
        
        self.chara_fade_alpha: int = 0
        self.chara_fading_in: bool = False

        # 音声再生
        self.current_sound: Optional[pygame.mixer.Sound] = None

        # ローディング表示
        self.is_loading: bool = False
        self.loading_dots: int = 0
        self.loading_timer: int = 0

    def _load_japanese_font(self, size: int) -> pygame.font.Font:
        """日本語対応フォントをロードする。"""
        # Windows日本語フォント候補
        font_candidates = [
            "C:/Windows/Fonts/meiryo.ttc",
            "C:/Windows/Fonts/msgothic.ttc",
            "C:/Windows/Fonts/msmincho.ttc",
            "C:/Windows/Fonts/YuGothM.ttc",
            "C:/Windows/Fonts/YuGothR.ttc",
        ]

        for font_path in font_candidates:
            if os.path.exists(font_path):
                try:
                    return pygame.font.Font(font_path, size)
                except Exception:
                    continue

        # フォールバック
        return pygame.font.SysFont("msgothic", size)

    def set_scene(
        self,
        image_path: Optional[str] = None,
        chara_path: Optional[str] = None,
        prop_path: Optional[str] = None,
        scene_text: str = "",
        dialogue_text: str = "",
        choices: Optional[list[str]] = None,
    ):
        """新しいシーンを設定する。"""
        # 背景画像読み込み
        if image_path and Path(image_path).exists():
            try:
                raw = pygame.image.load(str(image_path))
                self.current_image = self._fit_image(raw)
                self.fading_in = True
                self.fade_alpha = 0
            except Exception as e:
                print(f"[Renderer] 背景画像読み込みエラー: {e}")

        # キャラ立ち絵読み込み
        if chara_path and Path(chara_path).exists():
            try:
                raw_chara = pygame.image.load(str(chara_path)).convert_alpha()
                self.current_chara = self._fit_chara_image(raw_chara)
                self.chara_fading_in = False
            except Exception as e:
                print(f"[Renderer] キャラ画像読み込みエラー: {e}")
        else:
            self.current_chara = None

        # 小物画像読み込み
        if prop_path and Path(prop_path).exists():
            try:
                raw_prop = pygame.image.load(str(prop_path)).convert_alpha()
                self.current_prop = self._fit_prop_image(raw_prop)
            except Exception as e:
                print(f"[Renderer] 小物画像読み込みエラー: {e}")
        else:
            self.current_prop = None

        # テキスト設定
        full_text = ""
        if scene_text:
            full_text = scene_text
        if dialogue_text:
            if full_text:
                full_text += "\n\n"
            full_text += dialogue_text

        self.scene_text = full_text
        self.dialogue_text = dialogue_text
        self.choices = choices or []
        self.displayed_chars = 0
        self.text_complete = False
        self.last_char_time = pygame.time.get_ticks()
        self.selected_choice = -1

    def _fit_image(self, surface: pygame.Surface) -> pygame.Surface:
        """画像を画面にフィットさせる（アスペクト比維持）。"""
        img_w, img_h = surface.get_size()
        scale_w = self.screen_w / img_w
        scale_h = self.screen_h / img_h
        scale = max(scale_w, scale_h)  # 画面を覆うように（Cover）

        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        scaled = pygame.transform.smoothscale(surface, (new_w, new_h))

        # 中央クロップ
        x = (new_w - self.screen_w) // 2
        y = (new_h - self.screen_h) // 2
        cropped = scaled.subsurface(
            pygame.Rect(x, y, self.screen_w, self.screen_h)
        )
        return cropped.copy()

    def _fit_chara_image(self, surface: pygame.Surface) -> pygame.Surface:
        """キャラ画像を高さに合わせてスケールする。"""
        img_w, img_h = surface.get_size()
        
        # キャラクターは画面高さの95%に収まるようにスケール（少し下端を開ける）
        target_h = int(self.screen_h * 0.95)
        scale = target_h / img_h
        target_w = int(img_w * scale)
        
        scaled = pygame.transform.smoothscale(surface, (target_w, target_h))
        return scaled

    def _fit_prop_image(self, surface: pygame.Surface) -> pygame.Surface:
        """小物画像を高さに合わせてスケールする。"""
        img_w, img_h = surface.get_size()
        
        # 小物は手前に大きく表示（画面高さの約60%）
        target_h = int(self.screen_h * 0.7)
        scale = target_h / img_h
        target_w = int(img_w * scale)
        
        scaled = pygame.transform.smoothscale(surface, (target_w, target_h))
        return scaled

    def update_chara(self, chara_path: str):
        """キャラ立ち絵のみを後から更新・フェードインさせる。"""
        if chara_path and Path(chara_path).exists():
            try:
                raw_chara = pygame.image.load(str(chara_path)).convert_alpha()
                self.current_chara = self._fit_chara_image(raw_chara)
                self.chara_fading_in = True
                self.chara_fade_alpha = 0
            except Exception as e:
                print(f"[Renderer] キャラ更新読み込みエラー: {e}")

    def play_audio(self, audio_path: str):
        """音声ファイルを再生する。"""
        if audio_path and Path(audio_path).exists():
            try:
                if self.current_sound:
                    self.current_sound.stop()
                self.current_sound = pygame.mixer.Sound(str(audio_path))
                self.current_sound.play()
            except Exception as e:
                print(f"[Renderer] 音声再生エラー: {e}")

    def set_loading(self, loading: bool):
        """ローディング状態を設定。"""
        self.is_loading = loading
        self.loading_dots = 0

    def skip_text(self):
        """テキスト送りを完了させる。"""
        self.displayed_chars = len(self.scene_text)
        self.text_complete = True

    def render(self) -> Optional[int]:
        """
        1フレーム描画し、プレイヤーの選択を返す。

        Returns:
            None: まだ未選択
            0-2: 選択肢番号
            -1: 終了要求
            -2: テキスト送り要求
        """
        now = pygame.time.get_ticks()

        # イベント処理
        result = self._handle_events()
        if result is not None:
            return result

        # 画面クリア
        self.screen.fill(self.COLOR_BG)

        # 背景とキャラ描画
        if self.current_image:
            if self.fading_in:
                self.fade_alpha = min(255, self.fade_alpha + 8)
                if self.fade_alpha >= 255:
                    self.fading_in = False
                
                # 背景フェードイン
                temp_bg = self.current_image.copy()
                temp_bg.set_alpha(self.fade_alpha)
                self.screen.blit(temp_bg, (0, 0))
                
                # キャラも一緒にフェードイン
                if self.current_chara:
                    temp_chara = self.current_chara.copy()
                    temp_chara.set_alpha(self.fade_alpha)
                    chara_x = self.screen_w // 2 - temp_chara.get_width() // 2 + 150 # 少し右寄り
                    chara_y = self.screen_h - temp_chara.get_height()
                    self.screen.blit(temp_chara, (chara_x, chara_y))
                
                # 小物も一緒にフェードイン
                if self.current_prop:
                    temp_prop = self.current_prop.copy()
                    temp_prop.set_alpha(self.fade_alpha)
                    prop_x = self.screen_w // 2 - temp_prop.get_width() // 2 # 中央
                    prop_y = self.screen_h - temp_prop.get_height() # 下端
                    self.screen.blit(temp_prop, (prop_x, prop_y))
            else:
                # フェード完了後
                self.screen.blit(self.current_image, (0, 0))
                
                # キャラの単独フェードインまたは通常描画
                if self.current_chara:
                    temp_chara = self.current_chara.copy()
                    if self.chara_fading_in:
                        self.chara_fade_alpha = min(255, self.chara_fade_alpha + 12)
                        temp_chara.set_alpha(self.chara_fade_alpha)
                        if self.chara_fade_alpha >= 255:
                            self.chara_fading_in = False
                    
                    chara_x = self.screen_w // 2 - temp_chara.get_width() // 2 + 150
                    chara_y = self.screen_h - temp_chara.get_height()
                    self.screen.blit(temp_chara, (chara_x, chara_y))
                
                if self.current_prop:
                    prop_x = self.screen_w // 2 - self.current_prop.get_width() // 2
                    prop_y = self.screen_h - self.current_prop.get_height()
                    self.screen.blit(self.current_prop, (prop_x, prop_y))

        # タイプライターテキスト更新
        if not self.text_complete and self.scene_text:
            if now - self.last_char_time > self.text_speed:
                self.displayed_chars += 1
                self.last_char_time = now
                if self.displayed_chars >= len(self.scene_text):
                    self.text_complete = True

        # テキストオーバーレイ
        if self.scene_text:
            self._draw_text_overlay()

        # 選択肢（テキスト完了後のみ表示）
        if self.text_complete and self.choices:
            self._draw_choices()

        # ローディング表示
        if self.is_loading:
            self._draw_loading(now)

        pygame.display.flip()
        self.clock.tick(60)

        return None

    def _handle_events(self) -> Optional[int]:
        """イベントハンドリング。"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return -1

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return -1

                elif event.key == pygame.K_F11:
                    self._toggle_fullscreen()

                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if not self.text_complete:
                        self.skip_text()
                        return -2
                    elif not self.choices:
                        return -2

                elif event.key == pygame.K_1 and self.text_complete and len(self.choices) >= 1:
                    return 0
                elif event.key == pygame.K_2 and self.text_complete and len(self.choices) >= 2:
                    return 1
                elif event.key == pygame.K_3 and self.text_complete and len(self.choices) >= 3:
                    return 2

            elif event.type == pygame.MOUSEMOTION and self.text_complete and self.choices:
                self._update_choice_hover(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN and self.text_complete and self.choices:
                if event.button == 1:
                    clicked = self._get_clicked_choice(event.pos)
                    if clicked is not None:
                        return clicked

        return None

    def _toggle_fullscreen(self):
        """フルスクリーン切替。"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            display_info = pygame.display.Info()
            self.screen_w = display_info.current_w
            self.screen_h = display_info.current_h
            self.screen = pygame.display.set_mode(
                (self.screen_w, self.screen_h), pygame.FULLSCREEN
            )
        else:
            self.screen_w = 1280
            self.screen_h = 720
            self.screen = pygame.display.set_mode(
                (self.screen_w, self.screen_h)
            )

        # 画像を再フィット
        if self.current_image:
            # 元画像を再読み込みが必要だが、今は省略
            pass

    def _draw_text_overlay(self):
        """テキストオーバーレイ描画（画面下部の半透明領域）。"""
        # 表示テキスト
        visible_text = self.scene_text[: self.displayed_chars]
        if not visible_text:
            return

        # オーバーレイ領域計算
        overlay_h = int(self.screen_h * 0.35)
        overlay_y = self.screen_h - overlay_h

        # 半透明背景
        overlay = pygame.Surface((self.screen_w, overlay_h), pygame.SRCALPHA)
        overlay.fill(self.COLOR_OVERLAY)

        # 上端にグラデーションライン
        pygame.draw.line(
            overlay,
            self.COLOR_SCENE_BORDER,
            (40, 0),
            (self.screen_w - 40, 0),
            2,
        )

        self.screen.blit(overlay, (0, overlay_y))

        # テキスト描画
        margin_x = 60
        margin_y = 25
        max_width = self.screen_w - margin_x * 2

        self._draw_wrapped_text(
            visible_text,
            margin_x,
            overlay_y + margin_y,
            max_width,
            self.font,
            self.COLOR_TEXT,
        )

    def _draw_choices(self):
        """選択肢を画面右下に描画する。"""
        if not self.choices:
            return

        margin = 60
        choice_h = 50
        spacing = 10
        total_h = len(self.choices) * (choice_h + spacing)
        start_y = self.screen_h - total_h - margin
        choice_w = 450

        self._choice_rects = []

        for i, choice in enumerate(self.choices):
            x = self.screen_w - choice_w - margin
            y = start_y + i * (choice_h + spacing)
            rect = pygame.Rect(x, y, choice_w, choice_h)
            self._choice_rects.append(rect)

            # 背景
            bg_color = (
                (50, 40, 30, 220)
                if i != self.selected_choice
                else (80, 65, 40, 240)
            )
            bg_surface = pygame.Surface((choice_w, choice_h), pygame.SRCALPHA)
            bg_surface.fill(bg_color)
            self.screen.blit(bg_surface, (x, y))

            # 枠線
            border_color = (
                self.COLOR_CHOICE
                if i != self.selected_choice
                else self.COLOR_CHOICE_HOVER
            )
            pygame.draw.rect(self.screen, border_color, rect, 2)

            # テキスト
            text_color = (
                self.COLOR_TEXT
                if i != self.selected_choice
                else self.COLOR_CHOICE_HOVER
            )
            label = f"{i + 1}. {choice}"
            text_surf = self.font_small.render(label, True, text_color)
            text_rect = text_surf.get_rect(
                midleft=(x + 20, y + choice_h // 2)
            )
            self.screen.blit(text_surf, text_rect)

    def _draw_loading(self, now: int):
        """ローディングインジケーター。"""
        if now - self.loading_timer > 400:
            self.loading_dots = (self.loading_dots + 1) % 4
            self.loading_timer = now

        dots = "." * self.loading_dots
        text = f"思考中{dots}"
        surf = self.font.render(text, True, self.COLOR_HIGHLIGHT)
        x = self.screen_w // 2 - surf.get_width() // 2
        y = self.screen_h // 2 - surf.get_height() // 2
        self.screen.blit(surf, (x, y))

    def _draw_wrapped_text(
        self,
        text: str,
        x: int,
        y: int,
        max_width: int,
        font: pygame.font.Font,
        color: tuple,
    ):
        """テキスト折り返し描画。"""
        lines = text.split("\n")
        current_y = y
        line_height = font.get_linesize() + 4

        for line in lines:
            if not line.strip():
                current_y += line_height // 2
                continue

            # 一行が長すぎたら折り返し
            words_line = ""
            for char in line:
                test = words_line + char
                if font.size(test)[0] > max_width:
                    if words_line:
                        surf = font.render(words_line, True, color)
                        self.screen.blit(surf, (x, current_y))
                        current_y += line_height
                    words_line = char
                else:
                    words_line = test

            if words_line:
                surf = font.render(words_line, True, color)
                self.screen.blit(surf, (x, current_y))
                current_y += line_height

    def _update_choice_hover(self, mouse_pos: tuple):
        """マウスホバー中の選択肢を更新。"""
        if not hasattr(self, "_choice_rects"):
            return
        self.selected_choice = -1
        for i, rect in enumerate(self._choice_rects):
            if rect.collidepoint(mouse_pos):
                self.selected_choice = i
                break

    def _get_clicked_choice(self, mouse_pos: tuple) -> Optional[int]:
        """クリックされた選択肢を返す。"""
        if not hasattr(self, "_choice_rects"):
            return None
        for i, rect in enumerate(self._choice_rects):
            if rect.collidepoint(mouse_pos):
                return i
        return None

    def cleanup(self):
        """リソース解放。"""
        if self.current_sound:
            self.current_sound.stop()
        pygame.quit()
