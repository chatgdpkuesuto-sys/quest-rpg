
import random
import requests
import json

# Configuration for Local Stable Diffusion WebUI (Automatic1111)
SD_API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"

def main():
    print("=== Auto-Illustrator: NPC Generator ===")
    
    # 1. Simulate NPC Generation (simplified for demo)
    race = random.choice(["Human", "Elf", "Ogre", "Dragon", "Succubus"])
    clothes = random.choice(["Bikini Armor", "Maid", "Nun", "Bondage"])
    scale = random.choice(["Standard", "Giant", "Colossus"])
    expression = random.choice(["Arrogant", "Ahegao", "Shy"])
    
    # 2. Construct Prompt (using 15_Image_Prompt_Generator.md logic)
    prompt = f"masterpiece, best quality, 1girl, {race}, {clothes}, {scale}, {expression}, erotic, fantasy"
    neg_prompt = "low quality, worst quality, bad anatomy"
    
    print(f"\n[Generated NPC]: {race} / {clothes} / {scale} / {expression}")
    print(f"[Prompt]: {prompt}")
    
    # 3. Output to File
    with open("last_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)
    print("\n[Saved]: 'last_prompt.txt' has been updated.")
    
    # 4. Try Local API
    try:
        payload = {"prompt": prompt, "negative_prompt": neg_prompt, "steps": 20}
        response = requests.post(SD_API_URL, json=payload, timeout=2)
        if response.status_code == 200:
            print("[API]: Successfully sent to Stable Diffusion!")
        else:
            print(f"[API]: Error {response.status_code}")
    except:
        print("[API]: Local Stable Diffusion not running (http://127.0.0.1:7860). Using File Mode.")

if __name__ == "__main__":
    main()
