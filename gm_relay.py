"""
gm_relay.py ── GMターン処理リレー
index_scene.json を読み → ComfyUI + VOICEVOX に投げる → status.json を更新
"""
import os, json, time, random, sys, requests

ROOT      = os.path.dirname(os.path.abspath(__file__))
SCENE_F   = os.path.join(ROOT, "index_scene.json")
STATUS_F  = os.path.join(ROOT, "status.json")
VOICE_OUT = os.path.join(ROOT, "04_Assets", "voice_out.wav")
WF_PATH   = os.path.join(ROOT, "00_Core_Engine", "Unsaved Workflow.json")

COMFY  = "http://127.0.0.1:8188/prompt"
VVOX   = "http://127.0.0.1:50021"

def main():
    with open(SCENE_F, "r", encoding="utf-8") as f:
        scene = json.load(f)

    img_prompt = scene.get("image_prompt", "")
    voice_text = scene.get("voice_text", "")

    # ── ComfyUI ──
    if img_prompt:
        try:
            with open(WF_PATH, "r", encoding="utf-8") as f:
                wf = json.load(f)
            # ノード6（ポジティブプロンプト）に注入
            if "6" in wf:
                wf["6"]["inputs"]["text"] = img_prompt
            if "3" in wf:
                wf["3"]["inputs"]["seed"] = random.randint(0, 2**53)
            r = requests.post(COMFY, json={"prompt": wf}, timeout=10)
            print(f"🎨 ComfyUI: {r.status_code}")
        except requests.ConnectionError:
            print("⚠️ ComfyUI 未起動")
        except Exception as e:
            print(f"⚠️ ComfyUI エラー: {e}")

    # ── VOICEVOX ──
    if voice_text:
        try:
            r1 = requests.post(f"{VVOX}/audio_query",
                               params={"text": voice_text, "speaker": 3}, timeout=10)
            if r1.status_code == 200:
                r2 = requests.post(f"{VVOX}/synthesis",
                                   params={"speaker": 3}, json=r1.json(), timeout=30)
                if r2.status_code == 200:
                    os.makedirs(os.path.dirname(VOICE_OUT), exist_ok=True)
                    with open(VOICE_OUT, "wb") as f:
                        f.write(r2.content)
                    print("🎙️ VOICEVOX: 音声保存完了")
        except requests.ConnectionError:
            print("⚠️ VOICEVOX 未起動")
        except Exception as e:
            print(f"⚠️ VOICEVOX エラー: {e}")

    # ── status.json 更新 ──
    with open(STATUS_F, "w", encoding="utf-8") as f:
        json.dump({"updated_at": time.time(), "state": "ready"}, f, ensure_ascii=False)
    print("✅ status.json 更新完了 → ダイブ端末に反映される")

if __name__ == "__main__":
    main()
