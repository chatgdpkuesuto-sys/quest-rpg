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

# --- キャラクター生成用定数 ---
# ポーズ定義: { キーワード: ポーズ記述 }
CHARA_POSES = {
    "smile":     "standing, looking at viewer, gentle smile, calm expression",
    "serious":   "standing, looking at viewer, serious, focused expression",
    "surprised": "standing, looking at viewer, surprised, wide eyes",
    "sad":       "standing, looking at viewer, sad, looking down, melancholic",
    "blush":     "standing, looking at viewer, blush, shy timid expression",
    "attack":    "action pose, dynamic pose, casting offensive magic attack, fierce expression",
    "back":      "from behind, back, looking away",
    "look_back": "from behind, looking back at viewer, over shoulder",
}
CHARA_BASE = "masterpiece, best quality, newest, 1girl, solo, elf, pointy ears, silver hair, long flowing hair, beautiful detailed blue eyes, delicate facial features, consistent face, fantasy white and gold robes, holding wooden staff, witch hat, full body, boots"
CHARA_BG = "simple background, green background, chroma key"
CHARA_NEGATIVE = "cropped, out of frame, worst quality, low quality, oldest, early, displeasing, complex background, scenery, depth of field, drop shadow, 3d, realistic, blurry, bad anatomy, text, watermark, mutated face, distorted face, changing face, inconsistent face"



class ComfyUIClient:
    """ComfyUI APIと通信して画像を生成するクライアント。"""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or load_config()
        self.comfy_config = self.config["comfyui"]
        self.base_url = self.comfy_config["url"]
        self.scene_workflow_file = self.comfy_config.get("scene_workflow", "HAYAME_api.json")
        self.chara_workflow_file = self.comfy_config.get("chara_workflow", "chara_api.json")
        self.talotto_workflow_file = r"c:\Users\kuesu\OneDrive\Desktop\AITRPG\ワークフロウ\TALOTTO_api.json"
        
        self.scene_prompt_node_id = str(self.comfy_config.get("scene_prompt_node_id", "6"))
        self.scene_negative_node_id = str(self.comfy_config.get("scene_negative_node_id", "7"))
        self.chara_prompt_node_id = str(self.comfy_config.get("chara_prompt_node_id", "23"))
        
        self.output_dir = Path(__file__).parent / self.comfy_config["output_dir"]
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.client_id = str(uuid.uuid4())

        # ワークフローテンプレート読み込み
        self.scene_workflow_template = self._load_workflow(self.scene_workflow_file)
        self.chara_workflow_template = self._load_workflow(self.chara_workflow_file)
        self.talotto_workflow_template = self._load_workflow(self.talotto_workflow_file)

    def _load_workflow(self, filename: str) -> Optional[dict]:
        """指定されたワークフローJSONを読み込む。なければNone。"""
        workflow_path = Path(filename)
        if not workflow_path.is_absolute():
            workflow_path = Path(__file__).parent / filename
            
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
        if not self.scene_workflow_template:
            print(f"[ComfyUI] {self.scene_workflow_file} が見つかりません。スキップします。")
            return None

        # ワークフローをコピーしてプロンプトを差し替え
        workflow = json.loads(json.dumps(self.scene_workflow_template))

        # プロンプトノードのテキストを差し替え
        if self.scene_prompt_node_id in workflow:
            node = workflow[self.scene_prompt_node_id]
            if "inputs" in node and "text" in node["inputs"]:
                node["inputs"]["text"] = positive_prompt

        # ネガティブプロンプトノードの差し替え
        if self.scene_negative_node_id in workflow:
            node = workflow[self.scene_negative_node_id]
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

    # --- TALOTTOワークフローでキャラクターカード生成 ---

    SOUL_PROMPTS = {
        "孫悟空": "1boy, spiky black hair, orange gi, martial arts, muscular, confident grin, golden aura, fighting stance, anime style, dragon ball inspired",
        "フリーレン": "1girl, long white hair, green eyes, elf ears, purple staff, black and white robe, calm expression, magical aura, flowers, anime style",
        "ルフィ": "1boy, straw hat, red vest, scar under left eye, black shorts, big smile, rubber body, stretching arms, pirate, anime style, one piece inspired",
        "キリト": "1boy, black hair, black coat, dual wielding swords, glowing blue sword, determined eyes, dark fantasy, anime style, sword art online inspired",
        "アーニャ": "1girl, pink hair, green eyes, small child, cute expression, school uniform, mind reading, excited face, spy x family inspired, anime style",
    }

    def generate_party_chara(self, soul_name: str, job_name: str = "") -> Optional[Path]:
        """
        TALOTTOワークフローでキャラカードイラストを生成。
        soul_name: 魂カード名（孫悟空、フリーレン等）
        """
        if not self.talotto_workflow_template:
            print(f"[ComfyUI] TALOTTO_api.json がないためキャラ生成スキップ。")
            return None

        # 固定のSOUL_PROMPTSになければ、渡されたプロンプト指定（英語名等）をそのまま使う
        base_prompt = self.SOUL_PROMPTS.get(soul_name, f"1girl, solo, anime style, {soul_name}")
        if job_name:
            job_tags = {
                "戦士": "heavy armor, sword and shield, knight",
                "魔法使い": "wizard robe, magic staff, arcane symbols",
                "盗賊": "hooded cloak, daggers, stealthy",
                "僧侶": "holy robes, prayer beads, divine light",
            }
            base_prompt += f", {job_tags.get(job_name, '')}"

        positive = f"masterpiece, best quality, tarot card style, ornate border, fantasy illustration, {base_prompt}"
        negative = "worst quality, low quality, blurry, deformed, ugly, extra limbs, bad anatomy, text, watermark"

        workflow = json.loads(json.dumps(self.talotto_workflow_template))

        # プロンプト差し替え（ノード23=positive, ノード4=negative）
        if "23" in workflow and "inputs" in workflow["23"]:
            workflow["23"]["inputs"]["text"] = positive
        if "4" in workflow and "inputs" in workflow["4"]:
            workflow["4"]["inputs"]["text"] = negative

        # シードランダム化
        seed = int(time.time() * 1000) % 10000000000
        if "2" in workflow and "inputs" in workflow["2"]:
            workflow["2"]["inputs"]["seed"] = seed

        prompt_payload = {"prompt": workflow, "client_id": self.client_id}

        print(f"[ComfyUI] TALOTTOキャラ生成開始: {soul_name}({job_name})...")
        try:
            resp = requests.post(f"{self.base_url}/prompt", json=prompt_payload, timeout=10)
            resp.raise_for_status()
            prompt_id = resp.json().get("prompt_id")
            if not prompt_id:
                return None

            # ポーリング
            start_time = time.time()
            img_info = None
            while time.time() - start_time < 120:
                r = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=5)
                if r.status_code == 200:
                    h = r.json()
                    if prompt_id in h:
                        status = h[prompt_id].get("status", {}).get("status_str", "")
                        if status == "error":
                            print(f"[ComfyUI] TALOTTO生成エラー")
                            break
                        outputs = h[prompt_id].get("outputs", {})
                        for nid, nout in outputs.items():
                            if "images" in nout and nout["images"]:
                                img_info = nout["images"][0]
                                break
                        if img_info:
                            break
                time.sleep(2)

            if img_info is not None:
                filename = img_info.get("filename", "output.png")
                subfolder = img_info.get("subfolder", "")
                img_type = img_info.get("type", "output")
                params = urlencode({"filename": filename, "subfolder": subfolder, "type": img_type})
                dl_resp = requests.get(f"{self.base_url}/view?{params}", timeout=10)
                dl_resp.raise_for_status()

                # 魂名で保存
                save_dir = Path(__file__).parent / "assets" / "characters"
                save_dir.mkdir(parents=True, exist_ok=True)
                safe_name = soul_name.replace(" ", "_")
                save_path = save_dir / f"card_{safe_name}.png"
                with open(save_path, "wb") as f:
                    f.write(dl_resp.content)
                print(f"[ComfyUI] TALOTTOキャラ生成完了: {save_path.name}")
                return save_path

            print(f"[ComfyUI] TALOTTOキャラ生成タイムアウト")
            return None
        except requests.exceptions.ConnectionError:
            print("[ComfyUI] 接続エラー。ComfyUIが起動しているか確認してください。")
            return None
        except Exception as e:
            print(f"[ComfyUI] TALOTTOキャラ生成失敗: {e}")
            return None

    # --- キャラクター生成メソッド ---

    def generate_character(self, pose_key: str) -> Optional[Path]:
        """
        指定されたポーズキーワードでキャラ立ち絵を都度生成＆保存する。
        （透過処理はchara.json内のRMBGノードが行うためPython側のPillow処理は不要）
        """
        pose_text = CHARA_POSES.get(pose_key, CHARA_POSES["smile"])
        prompt = f"{CHARA_BASE}, {pose_text}, {CHARA_BG}"

        if not self.chara_workflow_template:
            print(f"[ComfyUI] {self.chara_workflow_file} がないためキャラ生成スキップ。")
            return None

        workflow = json.loads(json.dumps(self.chara_workflow_template))

        # DPCombinatorialGeneratorなどのリンクを外し、直接テキストを流し込む
        if self.chara_prompt_node_id in workflow:
            node = workflow[self.chara_prompt_node_id]
            if "inputs" in node:
                node["inputs"]["text"] = prompt

        # シード値をランダムにする
        seed = int(time.time() * 1000) % 10000000000
        for node_id, node in workflow.items():
            if node.get("class_type") in ("KSampler", "KSamplerAdvanced"):
                if "inputs" in node and "seed" in node["inputs"]:
                    node["inputs"]["seed"] = seed

        prompt_payload = {
            "prompt": workflow,
            "client_id": self.client_id,
        }

        print(f"[ComfyUI] キャラクター生成開始 ('pose': {pose_key})...")
        try:
            resp = requests.post(f"{self.base_url}/prompt", json=prompt_payload, timeout=10)
            resp.raise_for_status()
            prompt_id = resp.json().get("prompt_id")

            if not prompt_id:
                return None

            start_time = time.time()
            img_info = None
            # ポーリング
            while time.time() - start_time < 120:
                r = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=5)
                if r.status_code == 200:
                    h = r.json()
                    if prompt_id in h:
                        status = h[prompt_id].get("status", {}).get("status_str", "")
                        if status == "error":
                            break
                        outputs = h[prompt_id].get("outputs", {})
                        for nid, nout in outputs.items():
                            if "images" in nout and nout["images"]:
                                img_info = nout["images"][0]
                                break
                        if img_info:
                            break
                time.sleep(2)

            if img_info is not None:
                filename = img_info.get("filename", "output.png")
                subfolder = img_info.get("subfolder", "")
                img_type = img_info.get("type", "output")
                params = urlencode({"filename": filename, "subfolder": subfolder, "type": img_type})

                dl_resp = requests.get(f"{self.base_url}/view?{params}", timeout=10)
                dl_resp.raise_for_status()

                # 最新のキャラクター画像を一時ファイルとして保存
                save_path = Path(__file__).parent / "assets" / "characters" / "chara_current.png"
                save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(save_path, "wb") as f:
                    f.write(dl_resp.content)

                # 透過処理はRMBGノードが行うため、ここでは何もしない
                print(f"[ComfyUI] キャラクター生成完了: {save_path.name}")
                return save_path

            return None
        except Exception as e:
            print(f"[ComfyUI] キャラクター生成失敗: {e}")
            return None


# === テスト ===
if __name__ == "__main__":
    print("=== ComfyUI 接続テスト ===")
    client = ComfyUIClient()

    if client.scene_workflow_template:
        print("HAYAME_api.json 読み込み成功")
        result = client.generate(
            "masterpiece, best quality, dark fantasy, ancient stone dungeon, "
            "mysterious glowing runes on walls, 1girl, silver hair, red eyes, "
            "dark armor, dramatic lighting"
        )
        if result:
            print(f"背景成功！画像パス: {result}")
    else:
        print("背景生成ワークフローが見つかりません。")

    if client.chara_workflow_template:
        print("chara_api.json 読み込み成功")
        res2 = client.generate_character("attack")
        if res2:
            print(f"キャラ生成成功！画像パス: {res2}")
