import os
import json
import time
import pyautogui

def generate_engine_pulse():
    print("🔥 Neural Pulse Detected: Triggering Game Engine...")
    
    # ユーザーのアクションを読み取る
    action_path = r"c:\Users\kuesu\GEM_Project_Root\player_action.json"
    action = "不明"
    try:
        with open(action_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            action = data.get("action", "不明")
    except Exception:
        pass

    # ========================================================
    # 【禁断の黒魔術】物理的なキー操作によるVSCodeチャット自動発火
    # ========================================================
    print(f"  👉 プレイヤーアクション [{action}] を検知。VSCodeチャットに自動入力を開始します...")
    
    # 少しだけ待ってから（ブラウザからフォーカスが外れないように注意しつつ、今回は裏技で直接キーを送る）
    # ユーザーには「VSCodeのチャット入力欄にカーソルを合わせっぱなしにしておく」運用をお願いする。
    time.sleep(0.5)
    
    # チャットに「。 (Enter)」を力技で打ち込む
    pyautogui.typewrite('。')
    pyautogui.press('enter')
    
    print(f"  ✅ 自動入力を完了しました。AIが応答を開始します。")

if __name__ == "__main__":
    generate_engine_pulse()
