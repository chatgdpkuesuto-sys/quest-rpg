"""
generate_all_scenes.py — シーン画像一括生成スクリプト
全シーンタイプの画像を事前生成し、ファイル名で管理する。
"""

import time
from comfyui_client import ComfyUIClient

# 共通プレフィックス（柔らかい水彩風）
_BASE = "masterpiece, best quality, ultra-detailed, illustration, watercolor style, dreamy, muted colors, low contrast, soft focus, pastel tones, gentle lighting"

# シーン画像定義: { ファイル名: プロンプト }
SCENE_LIBRARY = {
    # === 街・建物 ===
    "town_square": f"{_BASE}, fantasy town square, cobblestone, fountain, medieval buildings, anime style",
    "tavern_inside": f"{_BASE}, cozy tavern interior, wooden tables, warm candlelight, anime style",
    "castle_hall": f"{_BASE}, grand castle hall, red carpet, chandeliers, marble pillars, anime style",
    "shop": f"{_BASE}, fantasy item shop interior, potions on shelves, magical items, anime style",
    "church": f"{_BASE}, beautiful fantasy cathedral interior, stained glass windows, holy light, anime style",
    "guild_hall": f"{_BASE}, adventurer guild hall, quest board, warm atmosphere, anime style",

    # === 自然 ===
    "forest": f"{_BASE}, enchanted forest, sunlight filtering through trees, green foliage, anime style",
    "forest_night": f"{_BASE}, mystical forest at night, soft moonlight, glowing mushrooms, anime style",
    "mountain": f"{_BASE}, mountain landscape, soft sunset sky, gentle clouds, serene view, anime style",
    "river": f"{_BASE}, beautiful river in forest, clear water, rocks, wildflowers, anime style",
    "flower_field": f"{_BASE}, vast flower field, soft blue sky, white clouds, gentle breeze, anime style",
    "beach": f"{_BASE}, fantasy beach, crystal clear water, soft sunset, gentle waves, anime style",

    # === ダンジョン・探索 ===
    "dungeon_entrance": f"{_BASE}, ancient dungeon entrance, stone archway, ivy vines, anime style",
    "dungeon_corridor": f"{_BASE}, stone dungeon corridor, soft torchlight, ancient walls, anime style",
    "crystal_cave": f"{_BASE}, crystal cave, softly glowing crystals, reflections, anime style",
    "ruins": f"{_BASE}, ancient ruins, overgrown with plants, soft sunlight, anime style",
    "treasure_room": f"{_BASE}, treasure room, golden coins, jewels, soft magical glow, anime style",

    # === イベント・戦闘 ===
    "campfire": f"{_BASE}, campfire at night, soft starry sky, gentle warm fire, cozy, anime style",
    "battle_field": f"{_BASE}, open field, dramatic soft sky, gentle wind, anime style",
    "magic_circle": f"{_BASE}, glowing magic circle on ground, soft mystical energy, anime style",

    # === キャラクター ===
    "girl_adventurer": f"{_BASE}, 1girl, adventurer outfit, leather armor, sword, confident smile, anime style",
    "girl_mage": f"{_BASE}, 1girl, mage robes, staff, soft magical aura, long hair, anime style",
    "girl_healer": f"{_BASE}, 1girl, white robes, gentle smile, soft healing magic, anime style",
    "mysterious_npc": f"{_BASE}, 1girl, hooded cloak, mysterious smile, anime style",

    # === 特殊シーン ===
    "sunrise": f"{_BASE}, beautiful sunrise over fantasy landscape, soft golden light, anime style",
    "night_sky": f"{_BASE}, beautiful night sky, soft starlight, gentle moonlight, serene, anime style",
    "rain": f"{_BASE}, rainy fantasy town, soft lantern light, gentle reflections, anime style",
    "snow": f"{_BASE}, snowy fantasy landscape, soft snowfall, gentle warm windows, anime style",
}


def main():
    print("=" * 50)
    print("  シーン画像一括生成")
    print(f"  全{len(SCENE_LIBRARY)}枚を生成します")
    print("=" * 50)

    client = ComfyUIClient()
    if not client.workflow_template:
        print("ERROR: workflow_api.json が見つかりません！")
        return

    success = 0
    fail = 0

    for name, prompt in SCENE_LIBRARY.items():
        # 既存チェック
        existing = client.output_dir / f"{name}.png"
        if existing.exists():
            print(f"[SKIP] {name}.png — 既に存在")
            success += 1
            continue

        print(f"\n[{success + fail + 1}/{len(SCENE_LIBRARY)}] {name} を生成中...")
        result = client.generate(prompt)

        if result:
            # ファイル名をリネーム
            target = client.output_dir / f"{name}.png"
            result.rename(target)
            print(f"  ✅ {target}")
            success += 1
        else:
            print(f"  ❌ 生成失敗: {name}")
            fail += 1

        # 連続生成の負荷軽減
        time.sleep(1)

    print(f"\n{'=' * 50}")
    print(f"  完了！ 成功: {success} / 失敗: {fail}")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
