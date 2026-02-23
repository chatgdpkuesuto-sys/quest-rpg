"""
generate_all_scenes.py — シーン画像一括生成スクリプト
全シーンタイプの画像を事前生成し、ファイル名で管理する。
"""

import time
from comfyui_client import ComfyUIClient

# シーン画像定義: { ファイル名: プロンプト }
SCENE_LIBRARY = {
    # === 街・建物 ===
    "town_square": "masterpiece, best quality, ultra-detailed, illustration, fantasy town square, cobblestone, fountain, medieval buildings, warm sunlight, anime style",
    "tavern_inside": "masterpiece, best quality, ultra-detailed, illustration, cozy tavern interior, wooden tables, candlelight, warm atmosphere, fireplace, anime style",
    "castle_hall": "masterpiece, best quality, ultra-detailed, illustration, grand castle hall, red carpet, chandeliers, marble pillars, elegant, anime style",
    "shop": "masterpiece, best quality, ultra-detailed, illustration, fantasy item shop interior, potions on shelves, magical items, cozy, anime style",
    "church": "masterpiece, best quality, ultra-detailed, illustration, beautiful fantasy cathedral interior, stained glass windows, holy light, peaceful, anime style",
    "guild_hall": "masterpiece, best quality, ultra-detailed, illustration, adventurer guild hall, quest board, busy atmosphere, fantasy, anime style",

    # === 自然 ===
    "forest": "masterpiece, best quality, ultra-detailed, illustration, enchanted forest, sunlight through trees, green foliage, magical particles, anime style",
    "forest_night": "masterpiece, best quality, ultra-detailed, illustration, mystical forest at night, moonlight, glowing mushrooms, fireflies, anime style",
    "mountain": "masterpiece, best quality, ultra-detailed, illustration, epic mountain landscape, sunset sky, clouds below, breathtaking view, anime style",
    "river": "masterpiece, best quality, ultra-detailed, illustration, beautiful river in forest, clear water, rocks, wildflowers, peaceful, anime style",
    "flower_field": "masterpiece, best quality, ultra-detailed, illustration, vast flower field, blue sky, white clouds, colorful flowers, peaceful, anime style",
    "beach": "masterpiece, best quality, ultra-detailed, illustration, fantasy beach, crystal clear water, sunset, palm trees, beautiful sky, anime style",

    # === ダンジョン・探索 ===
    "dungeon_entrance": "masterpiece, best quality, ultra-detailed, illustration, ancient dungeon entrance, stone archway, vines, mysterious atmosphere, anime style",
    "dungeon_corridor": "masterpiece, best quality, ultra-detailed, illustration, stone dungeon corridor, torchlight, ancient walls, mysterious, anime style",
    "crystal_cave": "masterpiece, best quality, ultra-detailed, illustration, crystal cave, glowing crystals, beautiful reflections, underground lake, anime style",
    "ruins": "masterpiece, best quality, ultra-detailed, illustration, ancient ruins, overgrown with plants, crumbling pillars, mystical atmosphere, anime style",
    "treasure_room": "masterpiece, best quality, ultra-detailed, illustration, treasure room, golden coins, jewels, treasure chests, magical glow, anime style",

    # === イベント・戦闘 ===
    "campfire": "masterpiece, best quality, ultra-detailed, illustration, campfire at night, starry sky, warm fire, cozy atmosphere, anime style",
    "battle_field": "masterpiece, best quality, ultra-detailed, illustration, open battlefield, dramatic sky, wind blowing, epic atmosphere, anime style",
    "magic_circle": "masterpiece, best quality, ultra-detailed, illustration, glowing magic circle on ground, mystical energy, runes, fantasy, anime style",

    # === キャラクター ===
    "girl_adventurer": "masterpiece, best quality, ultra-detailed, illustration, 1girl, adventurer outfit, leather armor, sword, confident smile, fantasy, anime style",
    "girl_mage": "masterpiece, best quality, ultra-detailed, illustration, 1girl, mage robes, staff, magical aura, long hair, fantasy, anime style",
    "girl_healer": "masterpiece, best quality, ultra-detailed, illustration, 1girl, white robes, gentle smile, healing magic, warm light, fantasy, anime style",
    "mysterious_npc": "masterpiece, best quality, ultra-detailed, illustration, 1girl, hooded cloak, mysterious smile, glowing eyes, fantasy, anime style",

    # === 特殊シーン ===
    "sunrise": "masterpiece, best quality, ultra-detailed, illustration, beautiful sunrise over fantasy landscape, golden light, clouds, epic, anime style",
    "night_sky": "masterpiece, best quality, ultra-detailed, illustration, beautiful night sky, stars, milky way, moonlight, serene, fantasy, anime style",
    "rain": "masterpiece, best quality, ultra-detailed, illustration, rainy fantasy town, wet cobblestones, lantern light, reflections, atmospheric, anime style",
    "snow": "masterpiece, best quality, ultra-detailed, illustration, snowy fantasy landscape, winter village, soft snowfall, warm windows, cozy, anime style",
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
