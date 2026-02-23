import json
import random
from pathlib import Path
from typing import List, Dict

CHARA_DIR = Path("data/characters")
STATE_FILE = Path("data/game_state.json")

class GMTools:
    """ゲームマスター（Antigravity）用の管理ツール"""
    
    def __init__(self):
        self.characters = self.load_all_characters()
        
    def load_all_characters(self) -> List[Dict]:
        """data/characters/ 以下のすべてのJSONファイルを読み込む"""
        loaded_charas = []
        if not CHARA_DIR.exists():
            return loaded_charas
            
        for file_path in CHARA_DIR.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    chara_data = json.load(f)
                    loaded_charas.append(chara_data)
            except Exception as e:
                print(f"エラー: {file_path.name} の読み込みに失敗しました - {e}")
                
        return loaded_charas

    def get_character_by_id(self, chara_id: str) -> Dict:
        """指定したIDのキャラクターデータを取得する"""
        for char in self.characters:
            if char.get("id") == chara_id:
                return char
        return {}

    def get_random_character(self) -> Dict:
        """読み込んだリストからランダムに1体を返す"""
        if not self.characters:
            return {}
        return random.choice(self.characters)

    def draw_gacha(self, exclude_ids: List[str] = None) -> Dict:
        """引かれていないキャラの中からランダムにガチャとして1体を引く"""
        if exclude_ids is None:
            exclude_ids = []
            
        available = [c for c in self.characters if c.get("id") not in exclude_ids]
        
        if not available:
            print("もうガチャ候補がいません！")
            return {}
            
        return random.choice(available)

    def generate_party_info_from_chara(self, chara_data: Dict) -> Dict:
        """キャラクター設定JSONから、UI表示用（party_info）の形式に変換する"""
        if not chara_data:
            return {}
            
        return {
            "name": chara_data.get("name", "Unknown"),
            "hp": chara_data.get("hp", 10),
            "max_hp": chara_data.get("max_hp", 10),
            "alive": True,
            "status": "OK"
        }

if __name__ == "__main__":
    tools = GMTools()
    print(f"ロード済みキャラクター: {len(tools.characters)} 人")
    for c in tools.characters:
        print(f"- {c['name']} ({c['job_name']})")
    
    print("\n[テストガチャを1回引いてみます]")
    gacha_result = tools.draw_gacha()
    print(gacha_result)
