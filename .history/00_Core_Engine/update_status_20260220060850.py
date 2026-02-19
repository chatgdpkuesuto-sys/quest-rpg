import os
import sys
import json
import re
import subprocess
import time

# Define paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_DATA_DIR = os.path.join(ROOT_DIR, '99_Save_Data')
SETTINGS_FILE = os.path.join(ROOT_DIR, '.vscode', 'settings.json')

# Sound triggers
S_AHHH = "あぁっ……！"
S_KAIKAN = "快感"
S_ZETCHOU = "絶頂"

def play_sound_max_volume(text_to_speak):
    # This PowerShell script sets volume to ~100% and uses TTS to speak the text
    ps_script = f"""
    $obj = new-object -com wscript.shell 
    $obj.SendKeys([char]175)
    $obj.SendKeys([char]175)
    $obj.SendKeys([char]175)
    $obj.SendKeys([char]175)
    $obj.SendKeys([char]175)
    $obj.SendKeys([char]175)
    $obj.SendKeys([char]175)
    $obj.SendKeys([char]175)
    
    Add-Type -AssemblyName System.speech
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synth.Speak('{text_to_speak}')
    """
    subprocess.Popen(["powershell", "-NoProfile", "-Command", ps_script], 
                     creationflags=subprocess.CREATE_NO_WINDOW)

def check_for_triggers(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Simple keyword matching for extreme effects
            if S_ZETCHOU in content or S_AHHH in content:
                play_sound_max_volume("あぁっ！　いっちゃう……！")
                trigger_background_change(severe=True)
            elif S_KAIKAN in content:
                play_sound_max_volume("んんっ……")
                trigger_background_change(severe=False)
                
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

def trigger_background_change(severe=False):
    # This is a conceptual implementation of changing the background image
    # depending on the game state. In a real scenario, we'd swap the image file
    # or update settings.json
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            
        # Example logic: increase opacity to make the background more visible (more despair/lust)
        current_opacity = settings.get("backgroundCover.opacity", 0.2)
        new_opacity = min(current_opacity + (0.1 if severe else 0.05), 0.8)
        
        settings["backgroundCover.opacity"] = new_opacity
        
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error updating settings: {e}")

def main():
    if len(sys.argv) > 1:
        # Expected to receive the file path that was saved
        saved_file = sys.argv[1]
        print(f"[GM_BRAIN] Detected save event on {saved_file}")
        check_for_triggers(saved_file)
    else:
        # Fallback to checking recent files in 99_Save_Data
        # For simplicity, we just check the Social_Relationships mod
        social_file = os.path.join(SAVE_DATA_DIR, '04_Social_Relationships.md')
        if os.path.exists(social_file):
            check_for_triggers(social_file)

if __name__ == "__main__":
    main()
