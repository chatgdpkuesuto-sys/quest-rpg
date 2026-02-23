import json
from pathlib import Path
from comfyui_client import ComfyUIClient

STATE_FILE = Path("data/game_state.json")

def main():
    print("Generating Everyday-Cosplay Action Cards and Background...")
    comfyui = ComfyUIClient()
    
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)

    party_info = state.get("party_info", [])
    
    for i, member in enumerate(party_info):
        name = member.get("name")
        
        # ユーザー要望：「職業のコスプレをさせている感じ」「背景はもっと日常感」
        if name == "涼宮ハルヒ":
            prompt = "suzumiya haruhi, wearing fantasy RPG hero cosplay costume, holding toy sword, dynamic action pose, upper body, high school classroom background, masterpiece, best quality"
        elif name == "セイバー":
            prompt = "saber (fate), wearing modern casual clothes with knight cosplay accents, holding Excalibur, dynamic combat pose, upper body, modern city street background, afternoon, masterpiece, best quality"
        elif name == "スラン" or name == "suran":
            prompt = "1girl, silver hair elf, wearing japanese high school uniform cosplay, casting wind magic, dynamic action pose, upper body, school club room background, masterpiece, best quality"
        else:
            prompt = f"{name}, wearing fantasy cosplay costume, dynamic action pose, upper body, everyday life background, masterpiece, best quality"
        
        print(f"Generating Card for {name} with prompt: {prompt}")
        card_path = comfyui.generate_party_chara(prompt)
        if card_path:
            party_info[i]["image_path"] = str(card_path)

    state["party_info"] = party_info
    
    # 全体の背景（ダンジョンから日常へ）
    print("Generating new everyday background...")
    bg_prompt = "masterpiece, best quality, bright modern high school club room, afternoon sunlight, everyday life, anime style background, indoors"
    bg_path = comfyui.generate(bg_prompt)
    if bg_path:
        state["bg_image_path"] = str(bg_path)
        
    state["scene_text"] = "【日常風景でのTRPGセッション開始！？】\n\n『気がつくと、仄暗いダンジョンではなく……日差しの差し込む見慣れた「部室」のような空間にいた。』\n『そして隣を見ると、ファンタジー世界の鎧やローブではなく、「それっぽいコスプレ」をしたハルヒやセイバーたちがやる気満々で立っている！』\n\nハルヒ：「ただのダンジョンじゃ面白くないでしょ！今日はこの部室で、リアルなTRPGをやるわよ！」\n\nセイバー：「マスター、この現代的でありながら騎士の意匠を取り入れた服……動きやすくて良いですね。」\n\nスラン：「ふふ……私も学生服というものを着てみました。魔法の詠唱に支障はなさそうです。」\n\n（まさかの日常×コスプレ空間から物語がスタートした。どう行動しようか？）"
    
    # 立ち絵代表（今回はハルヒにしておく）
    chara_prompt_haruhi = "suzumiya haruhi, wearing fantasy RPG hero cosplay costume, holding toy sword, dynamic action pose, full body, masterpiece, best quality"
    print("Generating standing character (Haruhi)...")
    chara_path = comfyui.generate_party_chara(chara_prompt_haruhi)
    if chara_path:
        state["chara_image_path"] = str(chara_path)

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        
    print("Cosplay & Everyday update completed! Check game_state.json.")

if __name__ == "__main__":
    main()
