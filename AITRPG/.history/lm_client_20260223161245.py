"""
lm_client.py — LM Studio 通信クライアント
OpenAI互換APIでローカルLLMと通信し、<think>タグを除去して構造化出力を返す。
"""

import re
import json
import random
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
    仕様A: JSON出力を優先試行。失敗時はタグベースのフォールバック。
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

    # === 1) JSON直接パース（仕様A準拠の場合） ===
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict) and "scene" in parsed:
            result["scene"] = parsed.get("scene", "")
            result["dialogue"] = parsed.get("dialogue", "")
            result["image_prompt"] = parsed.get("image_prompt", "")
            result["choices"] = parsed.get("choices", [])
            return result
    except (json.JSONDecodeError, ValueError):
        pass

    # === 2) コードフェンス内のJSON抽出 ===
    json_match = re.search(r'```(?:json)?\s*\n?\s*(\{.*?\})\s*\n?\s*```', cleaned, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group(1))
            if isinstance(parsed, dict) and "scene" in parsed:
                result["scene"] = parsed.get("scene", "")
                result["dialogue"] = parsed.get("dialogue", "")
                result["image_prompt"] = parsed.get("image_prompt", "")
                result["choices"] = parsed.get("choices", [])
                return result
        except (json.JSONDecodeError, ValueError):
            pass

    # === 3) 埋もれたJSON抽出（テキスト中の { ... }） ===
    brace_match = re.search(r'\{[^{}]*"scene"[^{}]*\}', cleaned, re.DOTALL)
    if brace_match:
        try:
            parsed = json.loads(brace_match.group(0))
            if isinstance(parsed, dict) and "scene" in parsed:
                result["scene"] = parsed.get("scene", "")
                result["dialogue"] = parsed.get("dialogue", "")
                result["image_prompt"] = parsed.get("image_prompt", "")
                result["choices"] = parsed.get("choices", [])
                return result
        except (json.JSONDecodeError, ValueError):
            pass

    # === 4) フォールバック: [SCENE]/[DIALOGUE]/[IMAGE]/[CHOICES] タグ形式 ===
    scene_match = re.search(
        r"\[SCENE\]\s*\n(.*?)(?=\n\[(?:DIALOGUE|IMAGE|CHOICES)\]|\Z)",
        cleaned, re.DOTALL,
    )
    if scene_match:
        result["scene"] = scene_match.group(1).strip()

    dialogue_match = re.search(
        r"\[DIALOGUE\]\s*\n(.*?)(?=\n\[(?:SCENE|IMAGE|CHOICES)\]|\Z)",
        cleaned, re.DOTALL,
    )
    if dialogue_match:
        result["dialogue"] = dialogue_match.group(1).strip()

    image_match = re.search(
        r"\[IMAGE\]\s*\n(.*?)(?=\n\[(?:SCENE|DIALOGUE|CHOICES)\]|\Z)",
        cleaned, re.DOTALL,
    )
    if image_match:
        result["image_prompt"] = image_match.group(1).strip()

    choices_match = re.search(
        r"\[CHOICES\]\s*\n(.*?)(?=\n\[(?:SCENE|DIALOGUE|IMAGE)\]|\Z)",
        cleaned, re.DOTALL,
    )
    if choices_match:
        choices_text = choices_match.group(1).strip()
        choices = re.findall(r"\d+\.\s*(.+)", choices_text)
        result["choices"] = [c.strip() for c in choices]

    # === 5) 最終フォールバック: 全テキストをsceneに ===
    if not result["scene"] and cleaned:
        result["scene"] = cleaned

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

    def generate_candidates(self, exclude_names: list[str] = None) -> list[dict]:
        """ランダムなアニメ女子キャラ（ヒロイン）の候補を3人生成する（専用プロンプト使用）。"""
        exclude_str = ""
        if exclude_names:
            exclude_str = f"\n※重要※ 以下のキャラクターは既に登場したため、絶対に別のキャラクターを出力してください！\n除外リスト: {', '.join(exclude_names)}\n"

        # ランダム性を強制的に引き出すための属性キーワードガチャ
        decades = ["1980年代", "1990年代", "2000年代", "2010年代", "2020年代", "年代問わず"]
        genres = ["SF", "ファンタジー", "学園バトル", "ラブコメ", "ロボット", "魔法少女", "ホラー", "日常系", "異世界", "スポーツ"]
        hair_colors = ["赤髪", "青髪", "金髪", "銀髪/白髪", "緑髪", "ピンク髪", "黒髪", "茶髪", "紫髪"]
        
        hint_str = (
            f"【今回のランダム選出テーマ（ヒント）】\n"
            f"・年代: {random.choice(decades)}\n"
            f"・ジャンル: {random.choice(genres)} または {random.choice(genres)}\n"
            f"・特徴的要素（例）: {random.choice(hair_colors)}のキャラ、またはマイナー作品のキャラ\n"
            "※必ずしもこれに完全一致する必要はありませんが、いつも同じキャラになるのを防ぐためのインスピレーションとして使ってください。\n"
        )

        sys_prompt = (
            "あなたはパーティーメンバーを提案するガチャシステムです。\n"
            f"{exclude_str}\n"
            f"{hint_str}\n"
            "※非常に重要※ 完全なランダム性を重視してください。メジャーなキャラクターだけでなく、マニアックな作品、古い作品、最新の作品など、幅広いジャンルのアニメ・ゲームから、毎回全く異なる女子ヒロインを3人選出してください。定番キャラ（同じ作品のキャラばかり等）に偏らないようにしてください。\n"
            "ランダムな女子アニメキャラクター、または美少女ゲームヒロインを3人、"
            "名前・原作名・性格・特徴（スキル等）とともに考えてください。\n"
            "※画像生成で利用するため、必ず英語でのキャラクター名(name_en)と原作名(origin_en)のDanbooruタグ表記も含めてください。\n"
            "※ゲーム内の表示には日本語を使うため、name, origin, personality, desc は必ず【日本語】で出力してください。\n"
            "出力は必ず以下のJSON形式のみとし、他のテキストは一切出力しないでください。\n"
            "[\n"
            "  {\"name\": \"キャラ名(日本語)\", \"name_en\": \"Character English Name\", \"origin\": \"原作名(日本語)\", \"origin_en\": \"Origin English Name\", \"personality\": \"性格(日本語)\", \"desc\": \"簡単な説明(日本語)\"},\n"
            "  {\"name\": \"キャラ名2(日本語)\", \"name_en\": \"Character2 English Name\", \"origin\": \"原作名2(日本語)\", \"origin_en\": \"Origin2 English Name\", \"personality\": \"性格(日本語)\", \"desc\": \"簡単な説明(日本語)\"},\n"
            "  {\"name\": \"キャラ名3(日本語)\", \"name_en\": \"Character3 English Name\", \"origin\": \"原作名3(日本語)\", \"origin_en\": \"Origin3 English Name\", \"personality\": \"性格(日本語)\", \"desc\": \"簡単な説明(日本語)\"}\n"
            "]"
        )
        # 温度を高めてシードも疑似的に付与することでランダム性を強制
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": f"ランダムな乱数シード[{random.randint(10000, 99999)}]。定番にとらわれず、全く異なる新しい候補を3人生成してください。"}
        ]
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.9,
            "max_tokens": 1024,
            "stream": False,
        }
        print("[LMClient] ガチャ候補生成中...", flush=True)
        try:
            resp = requests.post(self.url, json=payload, timeout=60)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            
            # 思考タグがあれば除去
            content = strip_think_tags(content)
            
            # JSON部分の抽出（```json ... ``` があるかもしれないので探す）
            import re
            json_match = re.search(r"\[\s*\{.*?\}\s*\]", content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
                
            return json.loads(content)
        except Exception as e:
            print(f"[LMClient] 候補生成エラー: {e}")
            if 'content' in locals():
                print(f"[LMClient] 生レスポンス:\n{content}")
            
            # エラー時のフォールバック（いくつか適当なキャラを入れておく）
            return [
                {"name": "アスナ", "origin": "SAO", "personality": "慈愛", "desc": "剣術に長けた副団長"},
                {"name": "エミリア", "origin": "Re:ゼロ", "personality": "お人好し", "desc": "精霊術師のハーフエルフ"},
                {"name": "ホロ", "origin": "狼と香辛料", "personality": "賢い", "desc": "豊穣を司る賢狼"}
            ]


# === テスト ===
if __name__ == "__main__":
    print("=== LM Studio 接続テスト ===")
    client = LMClient()
    result = client.send("ゲームを開始する。冒険者として目覚めたところから始めてくれ。")
    print(f"\n[SCENE]\n{result['scene']}")
    print(f"\n[DIALOGUE]\n{result['dialogue']}")
    print(f"\n[IMAGE]\n{result['image_prompt']}")
    print(f"\n[CHOICES]\n{result['choices']}")
