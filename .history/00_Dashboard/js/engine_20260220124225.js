// ==============================================
// 00_Dashboard: Final Reactive Engine (FIXED)
// ==============================================

const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
window.isProcessing = false;
window.engineRunning = false;
window.allocatedStats = { power: 0, speed: 0, tough: 0, mind: 0, charm: 0, skill: 0 };
let remainingPoints = 3;

// 1. 永続化 (Save/Load)
window.saveState = function () {
    const state = {
        stats: window.allocatedStats,
        remaining: remainingPoints,
        phase: document.getElementById('target-dialog').style.display === 'block' ? 'target' : 'stat'
    };
    localStorage.setItem('machadun_local_save', JSON.stringify(state));
    console.log("💾 State saved to LocalStorage");
};

window.loadState = function () {
    const saved = localStorage.getItem('machadun_local_save');
    if (saved) {
        const data = JSON.parse(saved);
        window.allocatedStats = data.stats;
        remainingPoints = data.remaining;

        // UI復元
        Object.keys(window.allocatedStats).forEach(s => {
            const el = document.getElementById(`val-${s}`);
            if (el) el.innerText = window.allocatedStats[s];
        });
        const remPointsEl = document.getElementById('remaining-points');
        if (remPointsEl) remPointsEl.innerText = remainingPoints;

        console.log("📂 State restored from LocalStorage");
    }
};

// 2. UI制御
window.lockUI = (locked) => {
    window.isProcessing = locked;
    // 全てのボタンを無効化
    const buttons = document.querySelectorAll('button');
    buttons.forEach(b => {
        b.disabled = locked;
        b.style.opacity = locked ? 0.5 : 1;
    });
    document.body.style.cursor = locked ? 'wait' : 'default';
};

// 3. アクション
window.adjStat = (stat, delta) => {
    if (delta > 0 && remainingPoints <= 0) return;
    if (delta < 0 && window.allocatedStats[stat] <= 0) return;
    window.allocatedStats[stat] += delta;
    remainingPoints -= delta;
    document.getElementById(`val-${stat}`).innerText = window.allocatedStats[stat];
    document.getElementById('remaining-points').innerText = remainingPoints;
    window.saveState();
};

// 【重要】ステータス確定 (意志表示)
window.confirmStats = () => {
    if (window.isProcessing) return;
    window.lockUI(true);
    window.saveState();

    const payload = {
        action: 'CONFIRM_STATS_INTENT',
        stats: window.allocatedStats,
        time: Date.now()
    };

    fetch('http://127.0.0.1:5000/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    }).catch(err => {
        console.error("Bridge Error:", err);
        window.lockUI(false);
    });
};

// 【重要】戻る (意志表示)
window.backToStats = () => {
    if (window.isProcessing) return;
    window.lockUI(true);

    const payload = {
        action: 'BACK_TO_STATS_INTENT',
        time: Date.now()
    };

    fetch('http://127.0.0.1:5000/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    }).catch(err => {
        console.error("Bridge Error:", err);
        window.lockUI(false);
    });
};

// 【重要】ゲーム開始 (キャラ選択意志表示)
window.startGame = (charKey, charName) => {
    if (window.isProcessing) return;
    window.lockUI(true);

    const payload = {
        action: 'CHARACTER_SELECT_INTENT',
        target: charKey,
        target_name: charName,
        time: Date.now()
    };

    fetch('http://127.0.0.1:5000/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    }).catch(() => window.lockUI(false));
};

// 4. ポーリング (反応型)
let lastTimestamp = 0;
async function poll() {
    try {
        const res = await fetch('../status.json?t=' + Date.now());
        if (!res.ok) return;
        const state = await res.json();

        if (state.timestamp === lastTimestamp) return;
        lastTimestamp = state.timestamp;

        window.lockUI(false);

        // ステートに応じたフェーズ切り替え
        const initOverlay = document.getElementById('init-overlay');
        const statDialog = document.getElementById('stat-dialog');
        const targetDialog = document.getElementById('target-dialog');

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

        // 表示反映
        if (state.current_dialogue) {
            const dBox = document.getElementById('dialogue-box');
            const dText = document.getElementById('dialogue-text');
            if (dBox && dText) {
                dBox.style.display = 'block';
                dText.innerHTML = state.current_dialogue;
            }
        }

    } catch (e) { }
}

window.addEventListener('load', () => {
    window.loadState();
    window.engineRunning = true;
    setInterval(poll, 1000);
    poll();
    document.addEventListener('click', () => { if (audioCtx.state === 'suspended') audioCtx.resume(); }, { once: true });
});
