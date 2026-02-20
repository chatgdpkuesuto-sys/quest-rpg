// ==============================================
// 00_Dashboard: Final Reactive Engine
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
        document.getElementById('remaining-points').innerText = remainingPoints;

        if (data.phase === 'target') {
            document.getElementById('stat-dialog').style.display = 'none';
            document.getElementById('target-dialog').style.display = 'block';
        }
        console.log("📂 State restored from LocalStorage");
    }
};

// 2. UI制御
window.lockUI = (locked) => {
    window.isProcessing = locked;
    const btn = document.querySelector('#stat-dialog .char-btn');
    if (btn) {
        btn.disabled = locked;
        btn.style.opacity = locked ? 0.5 : 1;
        btn.innerText = locked ? "通信中..." : "確定";
    }
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

window.confirmStats = () => {
    if (window.isProcessing) return;
    window.lockUI(true);
    window.saveState();

    const payload = {
        action: 'CONFIRM_STATS',
        stats: window.allocatedStats,
        time: Date.now()
    };

    fetch('http://127.0.0.1:5000/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
        .then(r => r.json())
        .then(data => {
            console.log("✅ Stats sent to bridge");
            // ここでリロードはせず、AIがstatus.jsonを更新するのを待つ
        })
        .catch(err => {
            console.error("❌ Bridge Error:", err);
            window.lockUI(false);
        });
};

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

        if (state.status === 'hero_confirmed') {
            statDialog.style.display = 'none';
            targetDialog.style.display = 'block';
            window.saveState();
        } else if (state.status === 'active' || state.status === 'waiting_for_input') {
            initOverlay.style.display = 'none';
        }

        // 表示反映 (ダイアログ、モノローグ等)
        if (state.current_dialogue) {
            document.getElementById('dialogue-box').style.display = 'block';
            document.getElementById('dialogue-text').innerText = state.current_dialogue;
        }

    } catch (e) { }
}

window.addEventListener('load', () => {
    window.loadState();
    setInterval(poll, 1000);
    document.addEventListener('click', () => { if (audioCtx.state === 'suspended') audioCtx.resume(); }, { once: true });
});
