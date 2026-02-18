import random
import json
import requests
import datetime
import os

# Configuration for ComfyUI
COMFYUI_API_URL = "http://127.0.0.1:8188/prompt"
WORKFLOW_FILE = "workflow_api.json"

# --- USER CUSTOM NODE CONFIG ---
# Update these based on your `workflow_api.json`
# Node 17: Positive Prompt (CLIPTextEncode)
# Node 7:  Negative Prompt (CLIPTextEncode)
# Node 3:  KSampler (Seed)
NODE_POSITIVE = "17"
NODE_NEGATIVE = "7"
NODE_KSAMPLER = "3" 

# --- Tag Database ---
RACE_TAGS = {
    "Human": "1girl, human",
    "Elf": "1girl, elf, pointed ears, nature background",
    "Dwarf": "1girl, dwarf, short stature, muscular",
    "Beast": "1girl, animal ears, tail, kemonomimi",
    "Slime": "1girl, slime girl, transparent skin, liquid body",
    "Succubus": "1girl, succubus, wings, horns, heart-shaped tail",
    "Ogre": "1girl, oni, horns, red skin (optional), tall, muscular female",
    "Dragon": "1girl, dragon girl, dragon horns, dragon wings, tail",
    "God": "1girl, goddess, halo, divine aura, glowing eyes"
}

CLOTHES_TAGS = {
    "Adventurer": "fantasy clothes, leather armor, cape",
    "Bikini Armor": "bikini armor, armored bikini, plate metal, revealing clothes",
    "Maid": "maid, maid headdress, frills, apron",
    "Nun": "nun, nun habit, veil, cross",
    "Swimsuit": "school swimsuit",
    "Bondage": "bondage, rope, leather straps, gag",
    "Naked": "naked, nude, nipples, pussy"
}

SCALE_TAGS = {
    "Micro": "minigirl, fairy size, holding giant object, giant surroundings",
    "Standard": "normal size",
    "Giant": "giantess, tall female, height difference, giant, low angle view, looking down",
    "Colossus": "giantess, hyper giantess, size difference, mountain background, crushing"
}

EXPRESSION_TAGS = {
    "Standard": "looking at viewer, smile",
    "Arrogant": "haughty, looking down, smirk, confident",
    "Shy": "blush, embarrassed, shy, covering face",
    "Phased": "ahegao, rolling eyes, drooling, open mouth, tongue out, blush, sweaty skin"
}

def generate_npc_prompt():
    """Generates a random NPC and constructs a prompt."""
    race = random.choice(list(RACE_TAGS.keys()))
    clothes = random.choice(list(CLOTHES_TAGS.keys()))
    scale = random.choice(list(SCALE_TAGS.keys()))
    expression = random.choice(list(EXPRESSION_TAGS.keys()))
    
    # Base Quality Tags (Anime Style)
    quality_tags = "masterpiece, best quality, highly detailed, high contrast, glorious lighting"
    
    # Construct Full Prompt
    prompt = f"{quality_tags},\n{RACE_TAGS[race]}, {CLOTHES_TAGS[clothes]}, {SCALE_TAGS[scale]}, {EXPRESSION_TAGS[expression]},\nindoors, dark fantasy tavern background, cinematic lighting, depth of field"
    
    negative_prompt = "(text:1.5), (watermark:1.3), signature, username, artist name, date, timestamp, title, subtitles, credits,\ntext on sign, text on bottle, label, menu, book text, handwriting,\n(low quality, worst quality:1.4), bad anatomy, blurry, fuzzy, modern clothes, modern background, sunbeams, bright, sci-fi, 3d render, multiple girls"
    
    filename = f"{race}_{scale}_{expression}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return prompt, negative_prompt, filename

def main():
    print("=== Auto-Illustrator: ComfyUI Connector (Custom Workflow) ===")
    
    # 1. Generate Prompt
    prompt, neg, filename = generate_npc_prompt()
    
    print(f"\n[Generated NPC]: {filename}")
    print(f"\n[Prompt]:\n{prompt}")
    print("-" * 50)
    
    # 2. Output to File
    with open("last_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt + "\n\nNegative:\n" + neg)
    
    # 3. ComfyUI Integration
    if os.path.exists(WORKFLOW_FILE):
        print(f"\n[API] Loading '{WORKFLOW_FILE}'...")
        try:
            with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
                workflow = json.load(f)
            
            # --- Injecting Values ---
            
            # 1. Positive Prompt (Node 17)
            if NODE_POSITIVE in workflow:
                print(f" -> Injecting Positive Prompt into Node {NODE_POSITIVE}")
                workflow[NODE_POSITIVE]["inputs"]["text"] = prompt
            else:
                print(f"⚠️ Warning: Node {NODE_POSITIVE} (Positive) not found!")

            # 2. Negative Prompt (Node 7)
            if NODE_NEGATIVE in workflow:
                print(f" -> Injecting Negative Prompt into Node {NODE_NEGATIVE}")
                workflow[NODE_NEGATIVE]["inputs"]["text"] = neg
            else:
                print(f"⚠️ Warning: Node {NODE_NEGATIVE} (Negative) not found!")

            # 3. Random Seed (Node 3)
            if NODE_KSAMPLER in workflow:
                new_seed = random.randint(1, 99999999999999)
                print(f" -> Injecting New Seed ({new_seed}) into Node {NODE_KSAMPLER}")
                workflow[NODE_KSAMPLER]["inputs"]["seed"] = new_seed
            else:
                 print(f"⚠️ Warning: Node {NODE_KSAMPLER} (KSampler) not found!")

            # --- Sending Request ---
            print("\nSending to ComfyUI API...")
            payload = {"prompt": workflow}
            response = requests.post(COMFYUI_API_URL, json=payload, timeout=2)
            
            if response.status_code == 200:
                print("🎉 [SUCCESS] Generation Queued! Check ComfyUI.")
            else:
                print(f"⚠️ [API ERROR] Status {response.status_code}: {response.text}")

        except Exception as e:
            print(f"⚠️ Script Error: {e}")
    else:
        print(f"\n⚠️ '{WORKFLOW_FILE}' not found. Please place your API JSON in the same folder.")

if __name__ == "__main__":
    main()
