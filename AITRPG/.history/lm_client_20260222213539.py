"""
lm_client.py — LM Studio 通信クライアント
OpenAI互換APIでローカルLLMと通信し、<think>タグを除去して構造化出力を返す。
"""

import re
import json
import requests
from pathlib import Path
from typing import Optional


def load_config() -> dict:
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_system_prompt(config: dict) -> str:
    prompt_file = Path(__file__).parent / config["game"]["system_prompt_file"]
    with open(prompt_file, "r", encoding="utf-8") as f:
        return f.read()


def strip_think_tags(text: str) -> str:
    """<think>...</think>タグ内の思考部分を除去する。"""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def parse_gm_response(raw_text: str) -> dict:
    """
    GM応答を構造化パースする。
    Returns: {
        "scene": str,       # 情景描写
        "dialogue": str,    # セリフ
        "image_prompt": str,# ComfyUI向け英語プロンプト
        "choices": list[str]# 選択肢リスト
    }
    """
    cleaned = strip_think_tags(raw_text)

    result = {
        "scene": "",
        "dialogue": "",
        "image_prompt": "",
        "choices": [],
        "raw": cleaned,
    }

    # [SCENE] 抽出
    scene_match = re.search(
        r"\[SCENE\]\s*\n(.*?)(?=\n\[(?:DIALOGUE|IMAGE|CHOICES)\]|\Z)",
        cleaned,
        re.DOTALL,
    )
    if scene_match:
        result["scene"] = scene_match.group(1).strip()

    # [DIALOGUE] 抽出
    dialogue_match = re.search(
        r"\[DIALOGUE\]\s*\n(.*?)(?=\n\[(?:SCENE|IMAGE|CHOICES)\]|\Z)",
        cleaned,
        re.DOTALL,
    )
    if dialogue_match:
        result["dialogue"] = dialogue_match.group(1).strip()

    # [IMAGE] 抽出
    image_match = re.search(
        r"\[IMAGE\]\s*\n(.*?)(?=\n\[(?:SCENE|DIALOGUE|CHOICES)\]|\Z)",
        cleaned,
        re.DOTALL,
    )
    if image_match:
        result["image_prompt"] = image_match.group(1).strip()

    # [CHOICES] 抽出
    choices_match = re.search(
        r"\[CHOICES\]\s*\n(.*?)(?=\n\[(?:SCENE|DIALOGUE|IMAGE)\]|\Z)",
        cleaned,
        re.DOTALL,
    )
    if choices_match:
        choices_text = choices_match.group(1).strip()
        # "1. xxx" "2. xxx" "3. xxx" 形式をパース
        choices = re.findall(r"\d+\.\s*(.+)", choices_text)
        result["choices"] = [c.strip() for c in choices]

    return result


class LMClient:
    """LM Studio とのOpenAI互換API通信クライアント。"""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or load_config()
        self.lm_config = self.config["lm_studio"]
        self.url = self.lm_config["url"]
        self.model = self.lm_config["model"]
        self.system_prompt = load_system_prompt(self.config)
        self.conversation_history: list[dict] = []

    def reset_history(self):
        """会話履歴をリセット。"""
        self.conversation_history = []

    def send(self, user_message: str, context: str = "") -> dict:
        """
        ユーザーメッセージをGM(LLM)に送信し、構造化された応答を返す。

        Args:
            user_message: プレイヤーの入力テキスト
            context: 追加コンテキスト（ゲーム状態など）

        Returns:
            parse_gm_response() の結果辞書
        """
        # コンテキスト付きメッセージを構築
        full_message = user_message
        if context:
            full_message = f"【現在の状況】\n{context}\n\n【プレイヤーの行動】\n{user_message}"

        self.conversation_history.append({"role": "user", "content": full_message})

        # メッセージ配列を構築
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversation_history[-20:]  # 直近20ターンのみ送信

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.8,
            "max_tokens": 2048,
            "stream": True,
        }

        try:
            resp = requests.post(self.url, json=payload, timeout=120, stream=True)
            resp.raise_for_status()
            
            raw_content = ""
            print("[LMClient] ", end="", flush=True)
            
            for line in resp.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith('data: ') and decoded != 'data: [DONE]':
                        try:
                            chunk_data = json.loads(decoded[6:])
                            delta = chunk_data["choices"][0].get("delta", {})
                            chunk_str = delta.get("content", "")
                            if chunk_str:
                                raw_content += chunk_str
                                # コンソールに少しずつ出力して生存確認（改行はスペースにして簡略化）
                                clean_chunk = chunk_str.replace('\n', ' ')
                                print(clean_chunk, end="", flush=True)
                        except Exception:
                            pass
            
            print("\n")

            # 会話履歴にアシスタント応答を追加（思考タグ除去済み）
            cleaned_content = strip_think_tags(raw_content)
            self.conversation_history.append(
                {"role": "assistant", "content": cleaned_content}
            )

            return parse_gm_response(raw_content)

        except requests.exceptions.ConnectionError:
            return {
                "scene": "【接続エラー】LM Studioに接続できません。サーバーが起動しているか確認してください。",
                "dialogue": "",
                "image_prompt": "",
                "choices": ["再試行する", "設定を確認する", "終了する"],
                "raw": "",
            }
        except Exception as e:
            return {
                "scene": f"【エラー】GM応答の取得に失敗: {str(e)}",
                "dialogue": "",
                "image_prompt": "",
                "choices": ["再試行する", "設定を確認する", "終了する"],
                "raw": "",
            }


# === テスト ===
if __name__ == "__main__":
    print("=== LM Studio 接続テスト ===")
    client = LMClient()
    result = client.send("ゲームを開始する。冒険者として目覚めたところから始めてくれ。")
    print(f"\n[SCENE]\n{result['scene']}")
    print(f"\n[DIALOGUE]\n{result['dialogue']}")
    print(f"\n[IMAGE]\n{result['image_prompt']}")
    print(f"\n[CHOICES]\n{result['choices']}")
