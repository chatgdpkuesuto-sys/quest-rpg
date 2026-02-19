import os
import shutil
import time
import json
from pathlib import Path

# --- 設定 ---
# Stability MatrixのText2Img出力先
SOURCE_DIR = r"C:\Users\kuesu\OneDrive\Desktop\StabilityMatrix-win-x64\Data\Images\Text2Img"
# プロジェクト内の出力先フォルダ
DEST_DIR = r"c:\Users\kuesu\GEM_Project_Root\outputs"
DEST_FILE = "latest.png"
STATUS_JSON_PATH = r"c:\Users\kuesu\GEM_Project_Root\00_Dashboard\status.json"
# -----------

os.makedirs(DEST_DIR, exist_ok=True)

def get_latest_file(path):
    files = list(Path(path).glob("*.png")) + list(Path(path).glob("*.jpg"))
    if not files:
        return None
    return max(files, key=os.path.getmtime)

print(f"Monitoring: {SOURCE_DIR}")
last_file = get_latest_file(SOURCE_DIR)

try:
    while True:
        current_latest = get_latest_file(SOURCE_DIR)
        
        # 新しい画像が生成された場合
        if current_latest and current_latest != last_file:
            print(f"New image found: {current_latest.name}")
            
            # プロジェクトフォルダへコピー（latest.pngとして上書き）
            shutil.copy2(current_latest, os.path.join(DEST_DIR, DEST_FILE))
            
            # 既存の status.json を読み込んで画像パスだけを更新（発情度などを消さないため）
            status_data = {}
            if os.path.exists(STATUS_JSON_PATH):
                with open(STATUS_JSON_PATH, "r", encoding="utf-8") as f:
                    try:
                        status_data = json.load(f)
                        if not isinstance(status_data, dict):
                            status_data = {}
                    except json.JSONDecodeError:
                        status_data = {}
                
            # ダッシュボードからの相対パスに合わせる
            status_data["current_image"] = "../outputs/latest.png"
            status_data["status"] = "updated"
            
            with open(STATUS_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(status_data, f, ensure_ascii=False, indent=2)
            
            last_file = current_latest
            print("Successfully synced to Live Server!")
            
        time.sleep(1) # 1秒ごとにチェック
except KeyboardInterrupt:
    print("Sync stopped.")
