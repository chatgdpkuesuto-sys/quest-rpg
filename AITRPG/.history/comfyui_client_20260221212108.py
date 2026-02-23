"""
comfyui_client.py — ComfyUI 画像生成クライアント
workflow_api.json をテンプレートとして読み込み、プロンプトを差し替えて画像を生成する。
"""

import io
import json
import uuid
import time
import struct
import requests
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode


def load_config() -> dict:
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


# テンプレートプロンプト集（きれいなアニメイラスト系）
SCENE_TEMPLATES = [
    "masterpiece, best quality, ultra-detailed, illustration, 1girl, fantasy world, beautiful scenery, vibrant colors, anime style",
    "masterpiece, best quality, ultra-detailed, illustration, 1girl, medieval town, cobblestone street, warm lighting, anime style",
    "masterpiece, best quality, ultra-detailed, illustration, 1girl, enchanted forest, sunlight through trees, magical atmosphere, anime style",
    "masterpiece, best quality, ultra-detailed, illustration, 1girl, ancient ruins, mystical glow, adventure, anime style",
    "masterpiece, best quality, ultra-detailed, illustration, 1girl, castle interior, grand hall, candlelight, anime style",
    "masterpiece, best quality, ultra-detailed, illustration, 1girl, mountain landscape, sunset sky, epic view, anime style",
    "masterpiece, best quality, ultra-detailed, illustration, 1girl, tavern interior, cozy atmosphere, warm colors, anime style",
    "masterpiece, best quality, ultra-detailed, illustration, 1girl, crystal cave, glowing crystals, beautiful reflections, anime style",
    "masterpiece, best quality, ultra-detailed, illustration, 1girl, flower field, blue sky, peaceful, anime style",
    "masterpiece, best quality, ultra-detailed, illustration, 1girl, night sky, stars, moonlight, serene atmosphere, anime style",
]


class ComfyUIClient:
    """ComfyUI APIと通信して画像を生成するクライアント。"""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or load_config()
        self.comfy_config = self.config["comfyui"]
        self.base_url = self.comfy_config["url"]
        self.prompt_node_id = self.comfy_config["prompt_node_id"]
        self.negative_node_id = self.comfy_config["negative_node_id"]
        self.output_dir = Path(__file__).parent / self.comfy_config["output_dir"]
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.client_id = str(uuid.uuid4())

        # ワークフローテンプレート読み込み
        self.workflow_template = self._load_workflow()

    def _load_workflow(self) -> Optional[dict]:
        """workflow_api.json を読み込む。なければNone。"""
        workflow_path = Path(__file__).parent / "workflow_api.json"
        if workflow_path.exists():
            with open(workflow_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def generate(
        self,
        positive_prompt: str,
        negative_prompt: str = "worst quality, low quality, blurry, deformed, ugly",
        seed: Optional[int] = None,
    ) -> Optional[Path]:
        """
        画像を生成し、保存先パスを返す。

        Args:
            positive_prompt: 画像生成プロンプト（英語）
            negative_prompt: ネガティブプロンプト
            seed: シード値（Noneでランダム）

        Returns:
            生成画像のPathオブジェクト。失敗時はNone。
        """
        if not self.workflow_template:
            print("[ComfyUI] workflow_api.json が見つかりません。スキップします。")
            return None

        # ワークフローをコピーしてプロンプトを差し替え
        workflow = json.loads(json.dumps(self.workflow_template))

        # プロンプトノードのテキストを差し替え
        if self.prompt_node_id in workflow:
            node = workflow[self.prompt_node_id]
            if "inputs" in node and "text" in node["inputs"]:
                node["inputs"]["text"] = positive_prompt

        # ネガティブプロンプトノードの差し替え
        if self.negative_node_id in workflow:
            node = workflow[self.negative_node_id]
            if "inputs" in node and "text" in node["inputs"]:
                node["inputs"]["text"] = negative_prompt

        # シード値を設定（KSamplerノードを探す）
        if seed is not None:
            for node_id, node in workflow.items():
                if node.get("class_type") in ("KSampler", "KSamplerAdvanced"):
                    if "inputs" in node and "seed" in node["inputs"]:
                        node["inputs"]["seed"] = seed

        # APIにプロンプトを送信
        prompt_payload = {
            "prompt": workflow,
            "client_id": self.client_id,
        }

        try:
            resp = requests.post(
                f"{self.base_url}/prompt",
                json=prompt_payload,
                timeout=10,
            )
            resp.raise_for_status()
            result = resp.json()
            prompt_id = result.get("prompt_id")

            if not prompt_id:
                print("[ComfyUI] prompt_id が返されませんでした。")
                return None

            # ポーリングで完了を待つ
            return self._wait_and_download(prompt_id)

        except requests.exceptions.ConnectionError:
            print("[ComfyUI] 接続エラー。ComfyUIが起動しているか確認してください。")
            return None
        except Exception as e:
            print(f"[ComfyUI] エラー: {e}")
            return None

    def _wait_and_download(
        self, prompt_id: str, timeout: int = 300
    ) -> Optional[Path]:
        """生成完了をポーリングで待ち、画像をダウンロードする。"""
        start_time = time.time()
        print(f"[ComfyUI] 生成待機中... (最大{timeout}秒)")

        while time.time() - start_time < timeout:
            try:
                resp = requests.get(
                    f"{self.base_url}/history/{prompt_id}", timeout=5
                )
                if resp.status_code == 200:
                    history = resp.json()
                    if prompt_id in history:
                        entry = history[prompt_id]
                        # エラーチェック
                        status = entry.get("status", {})
                        status_str = status.get("status_str", "")
                        if status_str == "error":
                            msgs = status.get("messages", [])
                            print(f"[ComfyUI] 生成エラー: {msgs}")
                            return None

                        outputs = entry.get("outputs", {})
                        # 出力ノードから画像を取得
                        for node_id, node_output in outputs.items():
                            if "images" in node_output:
                                for img_info in node_output["images"]:
                                    elapsed = time.time() - start_time
                                    print(f"[ComfyUI] 生成完了 ({elapsed:.1f}秒)")
                                    return self._download_image(img_info)
            except Exception:
                pass

            time.sleep(2.0)

        print("[ComfyUI] タイムアウト: 画像生成が完了しませんでした。")
        return None

    def _download_image(self, img_info: dict) -> Optional[Path]:
        """ComfyUIから画像をダウンロードして保存する。"""
        filename = img_info.get("filename", "output.png")
        subfolder = img_info.get("subfolder", "")
        img_type = img_info.get("type", "output")

        params = urlencode(
            {"filename": filename, "subfolder": subfolder, "type": img_type}
        )

        try:
            resp = requests.get(f"{self.base_url}/view?{params}", timeout=10)
            resp.raise_for_status()

            # タイムスタンプ付きファイル名で保存
            timestamp = int(time.time() * 1000)
            save_path = self.output_dir / f"scene_{timestamp}.png"

            with open(save_path, "wb") as f:
                f.write(resp.content)

            print(f"[ComfyUI] 画像保存: {save_path}")
            return save_path

        except Exception as e:
            print(f"[ComfyUI] 画像ダウンロードエラー: {e}")
            return None


# === テスト ===
if __name__ == "__main__":
    print("=== ComfyUI 接続テスト ===")
    client = ComfyUIClient()

    if client.workflow_template:
        print("workflow_api.json 読み込み成功")
        result = client.generate(
            "masterpiece, best quality, dark fantasy, ancient stone dungeon, "
            "mysterious glowing runes on walls, 1girl, silver hair, red eyes, "
            "dark armor, dramatic lighting"
        )
        if result:
            print(f"成功！画像パス: {result}")
        else:
            print("画像生成に失敗しました。")
    else:
        print("workflow_api.json が見つかりません。ComfyUIからAPI形式で保存してください。")
