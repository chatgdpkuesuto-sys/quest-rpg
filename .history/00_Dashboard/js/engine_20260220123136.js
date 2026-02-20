// ==============================================
// 00_Dashboard: Total Redesigned engine.js
// ==============================================

const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
window.isProcessing = false;
window.engineRunning = false;
window.allocatedStats = { power: 0, speed: 0, tough: 0, mind: 0, charm: 0, skill: 0 };
let remainingPoints = 3;

// 1. UI状態管理
window.lockUI = function (locked) {
    window.isProcessing = locked;
    const layers = ['choice-container', 'interaction-layer'];
    layers.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.style.pointerEvents = locked ? 'none' : 'auto';
            if (id === 'interaction-layer') el.style.display = locked ? 'none' : 'block';
        }
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

window.confirmStats = () => {
    document.getElementById('stat-dialog').style.display = 'none';
    document.getElementById('target-dialog').style.display = 'block';
};

window.backToStats = () => {
    document.getElementById('stat-dialog').style.display = 'block';
    document.getElementById('target-dialog').style.display = 'none';
};

// 3. ゲーム開始
window.startGame = (charKey, charName) => {
    if (audioCtx.state === 'suspended') audioCtx.resume();

    document.getElementById('init-overlay').style.display = 'none';
    window.initEngine();

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
    }).catch(err => console.error("Bridge Connection Failed:", err));
};

// 4. 選択肢処理
window.selectChoice = (choiceId, label) => {
    if (window.isProcessing) return;
    window.lockUI(true);

    const container = document.getElementById('choice-container');
    container.style.display = 'none';
    container.innerHTML = '';

    const payload = {
        action: 'CHOICE_MADE',
        choice_id: choiceId,
        choice_label: label,
        time: Date.now()
    };

    fetch('http://127.0.0.1:5000/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    }).catch(err => {
        console.error("Bridge Action Failed:", err);
        window.lockUI(false);
    });
};

// 5. ステータス監視 (Polling)
let lastTimestamp = 0;
let lastImage = "";
let lastDialogue = "";
let lastMonologue = "";

async function pollGameState() {
    try {
        // ルートの status.json を監視
        const res = await fetch('../status.json?t=' + Date.now());
        if (!res.ok) return;
        const state = await res.json();

        // 初期化が必要な場合
        if (state.status === 'ready' && document.getElementById('init-overlay').style.display === 'none') {
            // もしリセットされていたらリフレッシュ
            // location.reload(); 
        }

        if (state.timestamp === lastTimestamp) return;
        lastTimestamp = state.timestamp;
        window.lockUI(false);

        // UI更新: 画像
        const bg = document.getElementById('bg-container');
        const imgPath = state.current_image || "outputs/latest.png";
        if (lastImage !== imgPath || state.timestamp > lastTimestamp - 5) {
            bg.style.backgroundImage = `url('../${imgPath}?t=${state.timestamp}')`;
            lastImage = imgPath;
        }

        // UI更新: 名前と属性
        document.getElementById('char-name').innerText = state.attributes.name || "None";
        document.getElementById('char-attributes').innerHTML = `Fetish: ${state.attributes.fetish}<br>Personality: ${state.attributes.personality}`;

        // UI更新: モノローグ
        const mono = document.getElementById('monologue-container');
        if (state.current_monologue !== lastMonologue) {
            lastMonologue = state.current_monologue;
            mono.innerHTML = '';
            const chunks = state.current_monologue.split('<br>').filter(t => t.trim());
            chunks.forEach((t, i) => {
                setTimeout(() => {
                    const d = document.createElement('div');
                    d.className = 'monologue-text';
                    d.innerHTML = t;
                    mono.appendChild(d);
                    setTimeout(() => { d.classList.add('fade-out'); setTimeout(() => d.remove(), 2000); }, 10000);
                }, i * 2000);
            });
        }

        // UI更新: セリフ
        const dBox = document.getElementById('dialogue-box');
        if (state.current_dialogue !== lastDialogue) {
            lastDialogue = state.current_dialogue;
            document.getElementById('dialogue-name').innerText = state.attributes.name.split(' ')[0];
            document.getElementById('dialogue-text').innerHTML = state.current_dialogue;
            dBox.style.display = state.current_dialogue ? 'block' : 'none';

            if (state.current_dialogue) {
                const player = document.getElementById('voice-player');
                player.src = `../outputs/voice.wav?t=${state.timestamp}`;
                player.play().catch(() => { });
            }
        }

        // UI更新: ゲージ
        document.getElementById('arousal-fill').style.width = (state.arousal || 0) + '%';
        document.getElementById('despair-fill').style.width = (state.despair || 0) + '%';

        // UI更新: 選択肢
        const choiceBox = document.getElementById('choice-container');
        if (state.choices && state.choices.length > 0) {
            choiceBox.innerHTML = '';
            state.choices.forEach(c => {
                const b = document.createElement('button');
                b.className = 'choice-btn';
                b.innerText = c.label;
                b.onclick = () => window.selectChoice(c.id, c.label);
                choiceBox.appendChild(b);
            });
            choiceBox.style.display = 'flex';
        } else {
            choiceBox.style.display = 'none';
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
    // 既にゲーム中なら自動復帰
    fetch('../status.json').then(r => r.json()).then(s => {
        if (s.status !== 'ready' && s.attributes.name !== 'なし') {
            document.getElementById('init-overlay').style.display = 'none';
            window.initEngine();
        }
    }).catch(() => { });

    document.addEventListener('click', () => { if (audioCtx.state === 'suspended') audioCtx.resume(); }, { once: true });
});
