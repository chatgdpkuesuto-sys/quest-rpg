"""
generate_all_scenes.py — シーン画像一括生成スクリプト
全シーンタイプの画像を事前生成し、ファイル名で管理する。
"""

import time
from comfyui_client import ComfyUIClient

# シーン画像定義: { ファイル名: プロンプト }
SCENE_LIBRARY = {
    # === 街・建物 ===
    "town_square": "masterpiece, best quality, ultra-detailed, illustration, fantasy town square, cobblestone, fountain, medieval buildings, soft colors, pastel tones, gentle lighting, anime style",
    "tavern_inside": "masterpiece, best quality, ultra-detailed, illustration, cozy tavern interior, wooden tables, candlelight, soft colors, pastel tones, gentle warm atmosphere, anime style",
    "castle_hall": "masterpiece, best quality, ultra-detailed, illustration, grand castle hall, red carpet, chandeliers, marble pillars, soft colors, pastel tones, gentle lighting, anime style",
    "shop": "masterpiece, best quality, ultra-detailed, illustration, fantasy item shop interior, potions on shelves, magical items, soft colors, pastel tones, gentle lighting, anime style",
    "church": "masterpiece, best quality, ultra-detailed, illustration, beautiful fantasy cathedral interior, stained glass windows, soft holy light, pastel tones, gentle atmosphere, anime style",
    "guild_hall": "masterpiece, best quality, ultra-detailed, illustration, adventurer guild hall, quest board, soft colors, pastel tones, gentle warm lighting, anime style",

    # === 自然 ===
    "forest": "masterpiece, best quality, ultra-detailed, illustration, enchanted forest, soft sunlight through trees, green foliage, pastel tones, gentle colors, anime style",
    "forest_night": "masterpiece, best quality, ultra-detailed, illustration, mystical forest at night, soft moonlight, glowing mushrooms, pastel tones, gentle atmosphere, anime style",
    "mountain": "masterpiece, best quality, ultra-detailed, illustration, mountain landscape, soft sunset sky, gentle clouds, pastel tones, serene view, anime style",
    "river": "masterpiece, best quality, ultra-detailed, illustration, beautiful river in forest, clear water, rocks, wildflowers, soft colors, pastel tones, gentle lighting, anime style",
    "flower_field": "masterpiece, best quality, ultra-detailed, illustration, vast flower field, soft blue sky, white clouds, pastel flowers, gentle breeze, anime style",
    "beach": "masterpiece, best quality, ultra-detailed, illustration, fantasy beach, crystal clear water, soft sunset, pastel sky, gentle waves, anime style",

    # === ダンジョン・探索 ===
    "dungeon_entrance": "masterpiece, best quality, ultra-detailed, illustration, ancient dungeon entrance, stone archway, vines, soft colors, pastel tones, gentle atmosphere, anime style",
    "dungeon_corridor": "masterpiece, best quality, ultra-detailed, illustration, stone dungeon corridor, soft torchlight, ancient walls, pastel tones, gentle mysterious atmosphere, anime style",
    "crystal_cave": "masterpiece, best quality, ultra-detailed, illustration, crystal cave, softly glowing crystals, pastel reflections, gentle underground light, anime style",
    "ruins": "masterpiece, best quality, ultra-detailed, illustration, ancient ruins, overgrown with plants, soft sunlight, pastel tones, gentle peaceful atmosphere, anime style",
    "treasure_room": "masterpiece, best quality, ultra-detailed, illustration, treasure room, golden coins, jewels, soft magical glow, pastel tones, gentle lighting, anime style",

    # === イベント・戦闘 ===
    "campfire": "masterpiece, best quality, ultra-detailed, illustration, campfire at night, soft starry sky, gentle warm fire, pastel tones, cozy atmosphere, anime style",
    "battle_field": "masterpiece, best quality, ultra-detailed, illustration, open field, dramatic soft sky, gentle wind, pastel tones, epic atmosphere, anime style",
    "magic_circle": "masterpiece, best quality, ultra-detailed, illustration, glowing magic circle on ground, soft mystical energy, pastel runes, gentle glow, anime style",

    # === キャラクター ===
    "girl_adventurer": "masterpiece, best quality, ultra-detailed, illustration, 1girl, adventurer outfit, leather armor, sword, confident smile, soft colors, pastel tones, gentle lighting, anime style",
    "girl_mage": "masterpiece, best quality, ultra-detailed, illustration, 1girl, mage robes, staff, soft magical aura, long hair, pastel tones, gentle lighting, anime style",
    "girl_healer": "masterpiece, best quality, ultra-detailed, illustration, 1girl, white robes, gentle smile, soft healing magic, warm pastel light, anime style",
    "mysterious_npc": "masterpiece, best quality, ultra-detailed, illustration, 1girl, hooded cloak, mysterious smile, soft colors, pastel tones, gentle atmosphere, anime style",

    # === 特殊シーン ===
    "sunrise": "masterpiece, best quality, ultra-detailed, illustration, beautiful sunrise over fantasy landscape, soft golden light, pastel clouds, gentle morning, anime style",
    "night_sky": "masterpiece, best quality, ultra-detailed, illustration, beautiful night sky, soft starlight, gentle moonlight, pastel tones, serene, anime style",
    "rain": "masterpiece, best quality, ultra-detailed, illustration, rainy fantasy town, soft lantern light, gentle reflections, pastel tones, atmospheric, anime style",
    "snow": "masterpiece, best quality, ultra-detailed, illustration, snowy fantasy landscape, soft snowfall, gentle warm windows, pastel winter colors, cozy, anime style",
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
