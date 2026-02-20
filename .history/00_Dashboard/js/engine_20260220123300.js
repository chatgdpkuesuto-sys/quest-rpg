// ==============================================
// 00_Dashboard: refined-engine.js (Stat Focus)
// ==============================================

const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
window.isProcessing = false;
window.engineRunning = false;
window.allocatedStats = { power: 0, speed: 0, tough: 0, mind: 0, charm: 0, skill: 0 };
let remainingPoints = 3;

// 1. UI状態管理
window.lockUI = function (locked) {
    window.isProcessing = locked;
    const layers = ['stat-dialog', 'target-dialog', 'interaction-layer'];
    layers.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.pointerEvents = locked ? 'none' : 'auto';
    });
    document.body.style.cursor = locked ? 'wait' : 'default';
};

// 2. 主人公メイキング
window.adjStat = (stat, delta) => {
    if (delta > 0 && remainingPoints <= 0) return;
    if (delta < 0 && window.allocatedStats[stat] <= 0) return;
    window.allocatedStats[stat] += delta;
    remainingPoints -= delta;
    document.getElementById(`val-${stat}`).innerText = window.allocatedStats[stat];
    document.getElementById('remaining-points').innerText = remainingPoints;
};

// 【重要】ステータス確定をバックエンドへ飛ばす
window.confirmStats = () => {
    if (window.isProcessing) return;
    window.lockUI(true);

    const payload = {
        action: 'CONFIRM_STATS',
        stats: window.allocatedStats,
        time: Date.now()
    };

    fetch('http://127.0.0.1:5000/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    }).then(res => res.json()).then(data => {
        console.log("Stats confirmed by bridge:", data);
        // AI側のstatus.json更新を待つ
    }).catch(err => {
        console.error("Bridge Connection Failed:", err);
        window.lockUI(false);
    });
};

window.backToStats = () => {
    // クライアント側で戻る
    document.getElementById('stat-dialog').style.display = 'block';
    document.getElementById('target-dialog').style.display = 'none';
};

// 3. ゲーム開始 (キャラ選択)
window.startGame = (charKey, charName) => {
    if (window.isProcessing) return;
    window.lockUI(true);

    const payload = {
        action: 'START_GAME',
        target: charKey,
        time: Date.now()
    };

    fetch('http://127.0.0.1:5000/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    }).catch(err => {
        console.error("Bridge Connection Failed:", err);
        window.lockUI(false);
    });
};

// 4. ステータス監視 (Polling)
let lastTimestamp = 0;

async function pollGameState() {
    try {
        const res = await fetch('../status.json?t=' + Date.now());
        if (!res.ok) return;
        const state = await res.json();

        if (state.timestamp === lastTimestamp) return;
        lastTimestamp = state.timestamp;

        window.lockUI(false);

        // --- ステート制御 ---
        const statDialog = document.getElementById('stat-dialog');
        const targetDialog = document.getElementById('target-dialog');
        const initOverlay = document.getElementById('init-overlay');

        if (state.status === 'making_hero') {
            initOverlay.style.display = 'flex';
            statDialog.style.display = 'block';
            targetDialog.style.display = 'none';
        }
        else if (state.status === 'hero_confirmed') {
            initOverlay.style.display = 'flex';
            statDialog.style.display = 'none';
            targetDialog.style.display = 'block';
        }
        else if (state.status === 'active' || state.status === 'waiting_for_input') {
            initOverlay.style.display = 'none';
        }

        // --- UI更新 (共通) ---
        if (state.attributes && state.attributes.name !== "なし") {
            document.getElementById('char-name').innerText = state.attributes.name;
        }

        // セリフやモノローグの更新 (詳細省略、前回のロジックを維持)
        if (state.current_dialogue) {
            document.getElementById('dialogue-box').style.display = 'block';
            document.getElementById('dialogue-text').innerHTML = state.current_dialogue;
        }

    } catch (e) {
        console.error("Polling Error:", e);
    }
}

window.initEngine = () => {
    if (window.engineRunning) return;
    setInterval(pollGameState, 1000);
    pollGameState();
    window.engineRunning = true;
};

// ロード時
window.addEventListener('load', () => {
    window.initEngine();
    document.addEventListener('click', () => { if (audioCtx.state === 'suspended') audioCtx.resume(); }, { once: true });
});
