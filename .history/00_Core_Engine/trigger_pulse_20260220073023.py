import os
import json
import time

def generate_engine_pulse():
    print("🔥 Neural Pulse Detected: Triggering Game Engine...")
    
    # ここに本来はローカルLLMAPIや、外部APIを叩く処理を入れる。
    # 現在のアーキテクチャではAI（りりす）はVSCode拡張として動いているため、
    # 外部(LiveServer)からAIへ「文章を生成しろ」と強制的にトリガーを引くためのダミーファイルを更新し、
    # VSCodeのファイル監視機能(Run on Save等)に検知させるアプローチを取る。
    
    trigger_path = r"c:\Users\kuesu\GEM_Project_Root\AI_TRIGGER.md"
    action_path = r"c:\Users\kuesu\GEM_Project_Root\player_action.json"
    
    action = "不明"
    try:
        with open(action_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            action = data.get("action", "不明")
    except Exception:
        pass

    with open(trigger_path, "w", encoding="utf-8") as f:
        f.write(f"【システム命令】\nプレイヤーから以下の操作を受信しました。\n即座にこの行動の結果を計算し、テキスト・音声・ComfyUI画像を生成してダッシュボードを更新しなさい。\n\nアクション: {action}\nタイムスタンプ: {time.time()}")
    print(f"  ✅ AI_TRIGGER.md を更新しました。")

if __name__ == "__main__":
    generate_engine_pulse()
