import sys
import requests
import json
import os
import time
import random
import re

VOICEVOX_URL = "http://127.0.0.1:50021"

# 女性キャラクターを中心としたVOICEVOXのよく使うSpeaker IDのリスト
# 2: 四国めたん, 3: ずんだもん, 8: 春日部つむぎ, 11: 白上虎太郎(少年), 14: 冥鳴ひまり, 16: 九州そら, 20: もち子さん, 29: No.7 等
SPEAKER_LIST = [2, 3, 8, 14, 16, 20, 23, 29] 
OUTPUT_PATH = r"c:\Users\kuesu\GEM_Project_Root\00_Dashboard\outputs\voice.wav"

def strip_html(text):
    return re.sub(r'<[^>]*>', '', text)

def generate_voice(text):
    # HTMLタグを除去
    clean_text = strip_html(text)
    print(f"🎙️ 音声生成リクエスト: {clean_text}")
    
    # 🌟 NEW: キャラクターをランダムに決定
    speaker_id = random.choice(SPEAKER_LIST)
    print(f"🗣️ 選択されたスピーカーID: {speaker_id}")
    
    # 1. 音声合成用のクエリを作成
    query_payload = {"text": clean_text, "speaker": speaker_id}
    try:
        query_response = requests.post(f"{VOICEVOX_URL}/audio_query", params=query_payload)
        query_response.raise_for_status()
        query_data = query_response.json()
        
        # 🌟 NEW: ランダムに抑揚・早さ・ピッチをいじる
        query_data["speedScale"] = round(random.uniform(0.85, 1.25), 2)       # 少し遅め〜少し早め
        query_data["pitchScale"] = round(random.uniform(-0.15, 0.15), 2)      # ピッチの高低
        query_data["intonationScale"] = round(random.uniform(1.0, 1.6), 2)    # 抑揚を強めにして感情豊かに
        
        print(f"🎛️ パラメータ調整 - 速さ: {query_data['speedScale']}, ピッチ: {query_data['pitchScale']}, 抑揚: {query_data['intonationScale']}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ VOICEVOXとの通信エラー (Query): {e}")
        return False

    # 2. クエリをもとに音声を合成
    synth_payload = {"speaker": speaker_id}
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
