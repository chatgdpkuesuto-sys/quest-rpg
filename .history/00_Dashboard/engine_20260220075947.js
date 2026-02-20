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

// 全局状態管理
let lastTimestamp = 0;
let variantInterval = null; // 自動アニメーション用（現在はクリック連動を優先）
let currentVariantIndex = 1;

// 🌟 NEW: 画像を次のバリエーションに切り替える関数
function cycleVariant() {
    const bgContainer = document.getElementById('bg-container');
    currentVariantIndex = (currentVariantIndex % 10) + 1;
    // キャッシュ回避のためにタイムスタンプ付与
    bgContainer.style.backgroundImage = `url('outputs/variants/variant_${currentVariantIndex}.png?t=${Date.now()}')`;
    console.log(`Manual Cycle: Variant ${currentVariantIndex}`);
}

// ダッシュボード更新関数
async function pollGameState() {
    try {
        // キャッシュパージのためにタイムスタンプ付与
        const response = await fetch('status.json?t=' + new Date().getTime());
        if (!response.ok) return;
        const state = await response.json();

        // DOM Elements
        const bgImage = document.getElementById('bg-image');

        // Update Dialogue Text (Manga Bubble Style)
        const bubbleContainer = document.getElementById('bubble-container');
        if (state.current_dialogue && window.lastDialogue !== state.current_dialogue) {
            window.lastDialogue = state.current_dialogue;

            // 既存の吹き出しをクリア
            bubbleContainer.innerHTML = '';

            // セリフを句読点や改行で分割（短く切る）
            const dialogueClean = state.current_dialogue.replace(/<br>/g, '。');
            const chunks = dialogueClean.split(/[。！？]/).filter(s => s.trim().length > 0);

            // 分割されたセリフを吹き出しとして順次・またはランダムに配置
            chunks.forEach((text, index) => {
                const bubble = document.createElement('div');
                bubble.className = 'manga-bubble';
                bubble.innerHTML = text;

                // 位置のランダム性（重なりすぎないように）
                const randomX = 20 + Math.random() * 50; // 20% - 70%
                const randomY = 10 + Math.random() * 60; // 10% - 70%

                bubble.style.left = randomX + '%';
                bubble.style.top = randomY + '%';

                // 少しずつ遅れて出現させる
                bubble.style.animationDelay = (index * 0.5) + 's';

                bubbleContainer.appendChild(bubble);
            });
        }

        // Update Background Image if provided
        // status.json からの更新シグナル（タイムスタンプ変更）で強制更新する
        if (state.current_image) {
            // 初回ロード時、またはタイムスタンプが更新された場合に画像・音声をリロード
            if (!window.lastImageTimestamp || state.timestamp !== window.lastImageTimestamp) {
                const timeStr = "?t=" + (state.timestamp || new Date().getTime());

                // 画像更新
                // bgImage.src = state.current_image + timeStr; // Original line, replaced by new logic below

                // 音声更新と再生
                // 🌟 画像の更新処理
                const bgContainer = document.getElementById('bg-container');
                if (state.variant_mode) {
                    // バリエーションモード：初期表示を設定（以後はクリックで切り替わる）
                    if (!window.lastImageTimestamp) {
                        bgContainer.style.backgroundImage = `url('outputs/variants/variant_1.png?t=${Date.now()}')`;
                    }
                } else {
                    // 通常モード：最新の1枚を表示
                    if (state.current_image) {
                        bgContainer.style.backgroundImage = `url('${state.current_image}?t=${state.timestamp}')`;
                    }
                }
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
            document.body.classList.add('pulse-extreme');
        } else {
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
