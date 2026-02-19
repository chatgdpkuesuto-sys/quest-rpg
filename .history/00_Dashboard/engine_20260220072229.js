// ==============================================
// 00_Dashboard: OBS Overlay Engine (Real-Time JSON Polling)
// ==============================================

// --- Audio Generation via Web Audio API ---
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
let heartbeatInterval = null;
let currentArousal = 0; // 同期用キャッシュ

// Audio Initialization (Must be clicked once due to browser autoplay policies)
function initEngine() {
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
    document.getElementById('init-audio').style.display = 'none';

    // 0.5秒ごとにJSONをポーリングして画面を更新
    setInterval(pollGameState, 500);
    // 初期ポーリング
    pollGameState();
}

// ドクン、ドクンという心音を合成する関数
function playHeartbeat(intensity) {
    if (audioCtx.state === 'suspended') return;

    const baseFreq = 40 + (intensity * 0.5);

    const osc = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    osc.type = 'sine';

    osc.frequency.setValueAtTime(baseFreq, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(10, audioCtx.currentTime + 0.3);

    gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
    gainNode.gain.linearRampToValueAtTime(1.0, audioCtx.currentTime + 0.05);
    gainNode.gain.exponentialRampToValueAtTime(0.1, audioCtx.currentTime + 0.15);
    gainNode.gain.linearRampToValueAtTime(0.8, audioCtx.currentTime + 0.2);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.4);

    osc.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    osc.start();
    osc.stop(audioCtx.currentTime + 0.5);
}

// 発情度に応じた心音ループの更新
function updateHeartbeatLoop(arousalLevel) {
    if (currentArousal === arousalLevel) return; // 変更がなければ何もしない
    currentArousal = arousalLevel;

    if (heartbeatInterval) clearInterval(heartbeatInterval);

    if (arousalLevel < 30) return; // 30未満は心音なし

    const intervalMs = 1000 - ((arousalLevel - 30) * 8.5);

    heartbeatInterval = setInterval(() => {
        playHeartbeat(arousalLevel);

        // CSS Animation Sync
        const blood = document.getElementById('blood-overlay');
        blood.style.boxShadow = `inset 0 0 ${arousalLevel * 2}px rgba(255, 0, ${100 - arousalLevel}, ${arousalLevel / 100})`;
        setTimeout(() => {
            blood.style.boxShadow = `inset 0 0 0px rgba(255, 0, 128, 0)`;
        }, 300);

    }, intervalMs);
}

// === Asynchronous JSON Polling ===
async function pollGameState() {
    try {
        // キャッシュパージのためにタイムスタンプ付与
        const response = await fetch('status.json?t=' + new Date().getTime());
        if (!response.ok) return;
        const state = await response.json();

        // DOM Elements
        const arousalFill = document.getElementById('arousal-fill');
        const arousalVal = document.getElementById('arousal-value');
        const despairFill = document.getElementById('despair-fill');
        const despairVal = document.getElementById('despair-value');
        const bgImage = document.getElementById('bg-image');

        // Update Values smoothly
        arousalFill.style.width = `${state.arousal}%`;
        arousalVal.innerText = `${state.arousal}%`;

        despairFill.style.width = `${state.despair}%`;
        despairVal.innerText = `${state.despair}%`;

        // Update Dialogue Text
        const dialogueBox = document.getElementById('dialogue-text');
        if (state.current_dialogue && dialogueBox.innerHTML !== state.current_dialogue) {
            dialogueBox.innerHTML = state.current_dialogue;
        }

        // Update Background Image if provided
        // status.json からの更新シグナル（タイムスタンプ変更）で強制更新する
        if (state.current_image) {
            // 初回ロード時、またはタイムスタンプが更新された場合に画像・音声をリロード
            if (!window.lastImageTimestamp || state.timestamp !== window.lastImageTimestamp) {
                const timeStr = "?t=" + (state.timestamp || new Date().getTime());

                // 画像更新
                bgImage.src = state.current_image + timeStr;

                // 音声更新と再生
                const voicePlayer = document.getElementById('voice-player');
                if (voicePlayer) {
                    voicePlayer.src = "outputs/voice.wav" + timeStr;
                    voicePlayer.play().catch(e => console.log("Audio autoplay blocked:", e));
                }

                window.lastImageTimestamp = state.timestamp;
            }
        }

        // Arousal Effects (Visual Pulse)
        if (state.arousal >= 80) {
            arousalFill.parentElement.parentElement.classList.add('alert-glow');
            document.body.classList.add('pulse-extreme');
        } else {
            arousalFill.parentElement.parentElement.classList.remove('alert-glow');
            document.body.classList.remove('pulse-extreme');
        }

        // Despair Effects (Glitch)
        const glitchOverlay = document.getElementById('glitch-overlay');
        if (state.despair >= 50) {
            glitchOverlay.style.opacity = (state.despair / 100);
            if (state.despair >= 80) {
                document.body.style.animation = "shake 0.3s infinite";
            }
        } else {
            glitchOverlay.style.opacity = 0;
            document.body.style.animation = "none";
        }

        // オーディオループの即時更新
        updateHeartbeatLoop(state.arousal);

    } catch (error) {
        console.error("Failed to fetch status.json:", error);
    }
}
