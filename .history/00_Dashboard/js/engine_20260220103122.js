// ==============================================
// 00_Dashboard: engine.js (Core Data Polling)
// ==============================================

const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

window.initEngine = function () {
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
    const initOverlay = document.getElementById('init-overlay');
    if (initOverlay) initOverlay.style.display = 'none';

    // 0.5秒おきにステータスを監視
    setInterval(pollGameState, 500);
    pollGameState();
}

// 🌟 主人公ステータス割り振り処理
window.allocatedStats = { power: 0, speed: 0, tough: 0, mind: 0, charm: 0, skill: 0 };
let remainingPoints = 3;

// html内でのonclickに反応するためwindowオブジェクトにアタッチ
window.adjStat = function (stat, delta) {
    if (delta > 0 && remainingPoints <= 0) return; // ポイントがない
    if (delta < 0 && window.allocatedStats[stat] <= 0) return; // 0未満にはできない
    if (delta > 0 && window.allocatedStats[stat] >= 3) return; // 上限は3まで

    window.allocatedStats[stat] += delta;
    remainingPoints -= delta;

    document.getElementById('val-' + stat).innerText = window.allocatedStats[stat];
    document.getElementById('remaining-points').innerText = remainingPoints;
}

window.confirmStats = function () {
    if (remainingPoints > 0) {
        if (!confirm(`まだポイントが ${remainingPoints} 残っていますが、このまま進みますか？`)) {
            return;
        }
    }

    // ステータス割り振り画面を隠し、ターゲット選択画面を表示
    document.getElementById('stat-dialog').style.display = 'none';
    document.getElementById('target-dialog').style.display = 'block';
}

window.backToStats = function () {
    document.getElementById('stat-dialog').style.display = 'block';
    document.getElementById('target-dialog').style.display = 'none';
}

// 🌟 キャラクター選択時の処理
window.startGame = function (charKey, charName) {
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
    const initOverlay = document.getElementById('init-overlay');
    if (initOverlay) initOverlay.style.display = 'none';

    // 音声を強制再生
    const voicePlayer = document.getElementById('voice-player');
    if (voicePlayer && voicePlayer.src) {
        voicePlayer.play().catch(e => console.log("Audio play error:", e));
    }

    console.log(`🚀 Game Started with character: ${charName} (${charKey}), Stats:`, window.allocatedStats);

    // バックエンドにキャラクタ情報とステータスを送信
    if (typeof sendAction === 'function') {
        // payloadとして送るために、interaction.jsのsendActionの使われ方を少し拡張して呼び出すか、
        // 独自のfetchを行う
        const payload = {
            action: 'START_GAME',
            target: charKey,
            protagonist_stats: window.allocatedStats,
            time: Date.now()
        };
        fetch('http://127.0.0.1:5000/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }).catch(err => console.error("Communication error with bridge:", err));
    }
}

let lastTimestamp = 0;
let lastMonologue = "";
let lastDialogue = "";
let lastImage = "";

async function pollGameState() {
    try {
        const response = await fetch('../status.json?t=' + Date.now());
        if (!response.ok) return;
        const state = await response.json();

        // タイムスタンプが更新されていなければスキップ
        if (state.timestamp === lastTimestamp) return;
        lastTimestamp = state.timestamp;

        // ----------------------------------------------------
        // 1. キャラクター情報と画像パスの管理
        // ----------------------------------------------------
        // 日本語名から英名（フォルダ名）へのマッピング
        const NAME_MAP = {
            "アリア": "Aria",
            "ゼナ": "Zena",
            "エララ": "Elara",
            "エリーゼ": "Elize",
            "ユニ": "Yuni",
            "ミア": "Mia"
        };

        const charNameRaw = state.attributes && state.attributes.name ? state.attributes.name : "なし";
        let charFolder = "Default";

        // カッコ内の英名抽出を廃止し、マッピングを使用
        if (charNameRaw !== "なし") {
            const cleanName = charNameRaw.split(' ')[0].split('(')[0];
            charFolder = NAME_MAP[cleanName] || cleanName;
        }

        document.getElementById('char-name').innerText = charNameRaw.split('(')[0];

        if (state.attributes) {
            document.getElementById('char-attributes').innerHTML =
                `特徴: ${state.attributes.fetish || "-"}<br>性格: ${state.attributes.personality || "-"}`;
        }

        // 画像の設定 (キャラ名と状態フォルダで管理)
        // state.current_image に直接パス（BG等）が入っている場合はそれを優先、
        // そうでなければ outputs/キャラ名/状態/ を構築
        const bgContainer = document.getElementById('bg-container');

        let targetImagePath = state.current_image; // デフォルトはJSONのパス

        if (state.variant_mode && charNameRaw !== "なし") {
            // 例: outputs/Zena/Normal/variant_1.png
            const stateFolder = state.arousal >= 70 ? "Ero" : "Normal";
            targetImagePath = `outputs/${charFolder}/${stateFolder}/variant_1.png`;
        } else if (state.current_image && state.current_image.includes("BG_")) {
            // 背景の場合はそのまま
            targetImagePath = state.current_image;
            window.isDefaultBG = true;
        } else {
            window.isDefaultBG = false;
        }

        window.currentCharacterName = charNameRaw;

        if (lastImage !== targetImagePath) {
            bgContainer.style.backgroundImage = `url('${targetImagePath}?t=${state.timestamp}')`;
            lastImage = targetImagePath;
        }

        // ----------------------------------------------------
        // 2. モノローグ / GMテキスト（シネマティック表示）
        // ----------------------------------------------------
        const monoContainer = document.getElementById('monologue-container');
        if (state.current_monologue && state.current_monologue !== lastMonologue) {
            lastMonologue = state.current_monologue;
            monoContainer.innerHTML = ''; // クリア

            // パラグラフ単位で分割して表示
            const chunks = state.current_monologue.split(/<br>/i).filter(s => s.trim().length > 0);

            chunks.forEach((text, i) => {
                setTimeout(() => {
                    const el = document.createElement('div');
                    el.className = 'monologue-text';
                    el.innerHTML = text;
                    monoContainer.appendChild(el);

                    // 12秒で消える
                    setTimeout(() => {
                        el.classList.add('fade-out');
                        setTimeout(() => el.remove(), 2000);
                    }, 10000);

                }, i * 2500); // 2.5秒おきに出現
            });
        }

        // ----------------------------------------------------
        // 3. キャラクターセリフ（ノベルゲーム風）
        // ----------------------------------------------------
        const dialogBox = document.getElementById('dialogue-box');
        const dialogName = document.getElementById('dialogue-name');
        const dialogText = document.getElementById('dialogue-text');

        if (state.current_dialogue && state.current_dialogue !== lastDialogue) {
            lastDialogue = state.current_dialogue;

            if (charNameRaw === "なし") {
                dialogName.innerText = "System";
            } else {
                // 日本語部分だけ表示する (ゼナ)
                dialogName.innerText = charNameRaw.split(' ')[0];
            }

            dialogText.innerHTML = state.current_dialogue;
            dialogBox.style.display = 'block';

            // 音声再生
            const voicePlayer = document.getElementById('voice-player');
            if (voicePlayer) {
                voicePlayer.src = `outputs/voice.wav?t=${state.timestamp}`;
                voicePlayer.play().catch(e => console.log("Audio play error:", e));
            }

        } else if (!state.current_dialogue) {
            dialogBox.style.display = 'none';
        }

        // ----------------------------------------------------
        // 4. ステータスとエフェクト
        // ----------------------------------------------------
        const arousalFill = document.getElementById('arousal-fill');
        const despairFill = document.getElementById('despair-fill');

        if (arousalFill) arousalFill.style.width = Math.min(100, state.arousal || 0) + '%';
        if (despairFill) despairFill.style.width = Math.min(100, state.despair || 0) + '%';

        if (state.arousal >= 80) {
            document.body.classList.add('pulse-extreme');
        } else {
            document.body.classList.remove('pulse-extreme');
        }

    } catch (err) {
        console.error("Dashboard fetch error:", err);
    }
}
