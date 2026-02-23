"""
voicevox_client.py — VOICEVOX 音声合成クライアント
2段階API（audio_query → synthesis）でテキストをWAVに変換する。
"""

import json
import time
import requests
from pathlib import Path
from typing import Optional


def load_config() -> dict:
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


class VoicevoxClient:
    """VOICEVOX APIと通信して音声を合成するクライアント。"""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or load_config()
        self.vv_config = self.config["voicevox"]
        self.base_url = self.vv_config["url"]
        self.speaker_id = self.vv_config["speaker_id"]
        self.output_dir = Path(__file__).parent / self.vv_config["output_dir"]
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(
        self, text: str, speaker_id: Optional[int] = None
    ) -> Optional[Path]:
        """
        テキストを音声に変換し、WAVファイルとして保存する。

        Args:
            text: 読み上げるテキスト（日本語）
            speaker_id: VOICEVOX話者ID（Noneでデフォルト使用）

        Returns:
            生成WAVファイルのPathオブジェクト。失敗時はNone。
        """
        if not text or not text.strip():
            return None

        sid = speaker_id if speaker_id is not None else self.speaker_id

        try:
            # ステップ1: audio_query でクエリJSONを取得
            query_resp = requests.post(
                f"{self.base_url}/audio_query",
                params={"text": text, "speaker": sid},
                timeout=30,
            )
            query_resp.raise_for_status()
            query_data = query_resp.json()

            # 話速を少し速めにし、感情（抑揚）を強めにする（没入感重視）
            query_data["speedScale"] = 1.1
            query_data["intonationScale"] = 1.6

            # ステップ2: synthesis でWAVバイナリを取得
            synth_resp = requests.post(
                f"{self.base_url}/synthesis",
                params={"speaker": sid},
                json=query_data,
                timeout=60,
            )
            synth_resp.raise_for_status()

            # タイムスタンプ付きファイル名で保存
            timestamp = int(time.time() * 1000)
            save_path = self.output_dir / f"voice_{timestamp}.wav"

            with open(save_path, "wb") as f:
                f.write(synth_resp.content)

            print(f"[VOICEVOX] 音声保存: {save_path}")
            return save_path

        except requests.exceptions.ConnectionError:
            print("[VOICEVOX] 接続エラー。VOICEVOXが起動しているか確認してください。")
            return None
        except Exception as e:
            print(f"[VOICEVOX] エラー: {e}")
            return None

    def synthesize_dialogue(
        self, dialogue_text: str, speaker_id: Optional[int] = None
    ) -> Optional[Path]:
        """
        [DIALOGUE]セクションのテキストからセリフ部分だけを抽出して音声化。

        「キャラ名「セリフ」」形式から「セリフ」部分を取り出す。
        """
        import re

        # 「」内のセリフを抽出
        lines = dialogue_text.strip().split("\n")
        speech_parts = []
        for line in lines:
            match = re.search(r"「(.+?)」", line)
            if match:
                speech_parts.append(match.group(1))
            elif line.strip():
                speech_parts.append(line.strip())

        if not speech_parts:
            return None

        combined = "。".join(speech_parts)
        return self.synthesize(combined, speaker_id)


# === テスト ===
if __name__ == "__main__":
    print("=== VOICEVOX 接続テスト ===")
    client = VoicevoxClient()

    # テスト1: 基本合成
    result = client.synthesize("闇の大陸ノクターナルへようこそ。あなたの冒険が今、始まる。")
    if result:
        print(f"成功！音声パス: {result}")
    else:
        print("音声合成に失敗しました。")

    # テスト2: セリフ抽出合成
    result2 = client.synthesize_dialogue('ゼナ「目覚めたか、冒険者よ。ここは闇の大陸ノクターナルだ。」')
    if result2:
        print(f"セリフ合成成功！音声パス: {result2}")
