import sys
import requests
import json
import os
import time

VOICEVOX_URL = "http://127.0.0.1:50021"
# Zundamon Normal by default, user requested speaker 3
SPEAKER_ID = 3
OUTPUT_PATH = r"c:\Users\kuesu\GEM_Project_Root\00_Dashboard\outputs\voice.wav"

def generate_voice(text):
    print(f"🎙️ 音声生成リクエスト: {text}")
    
    # 1. 音声合成用のクエリを作成
    query_payload = {"text": text, "speaker": SPEAKER_ID}
    try:
        query_response = requests.post(f"{VOICEVOX_URL}/audio_query", params=query_payload)
        query_response.raise_for_status()
        query_data = query_response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ VOICEVOXとの通信エラー (Query): {e}")
        return False

    # 2. クエリをもとに音声を合成
    synth_payload = {"speaker": SPEAKER_ID}
    try:
        synth_response = requests.post(f"{VOICEVOX_URL}/synthesis", params=synth_payload, json=query_data)
        synth_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ VOICEVOXとの通信エラー (Synthesis): {e}")
        return False

    # 3. ファイルに保存
    with open(OUTPUT_PATH, "wb") as f:
        f.write(synth_response.content)
    
    print(f"✅ 音声保存完了: {OUTPUT_PATH}")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text_to_speak = sys.argv[1]
        generate_voice(text_to_speak)
    else:
        print("使い方: python voice_engine.py '喋らせたいテキスト'")
