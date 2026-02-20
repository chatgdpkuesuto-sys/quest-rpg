// ステータス割り振りだけのエンジン

const stats = { power: 0, speed: 0, tough: 0, mind: 0, charm: 0, skill: 0 };
let remaining = 3;

function adj(stat, delta) {
    if (delta > 0 && remaining <= 0) return;
    if (delta < 0 && stats[stat] <= 0) return;
    stats[stat] += delta;
    remaining -= delta;
    document.getElementById(`val-${stat}`).innerText = stats[stat];
    document.getElementById('remaining').innerText = remaining;
}

function confirmStats() {
    const btn = document.getElementById('confirm-btn');
    btn.disabled = true;
    btn.innerText = '通信中...';

    const payload = {
        action: 'CONFIRM_STATS',
        stats: stats,
        time: Date.now()
    };

    fetch('http://127.0.0.1:5000/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
        .then(r => r.json())
        .then(data => {
            // 結果画面に切り替え
            document.getElementById('stat-screen').style.display = 'none';
            document.getElementById('result-screen').style.display = 'block';
            document.getElementById('result-text').innerHTML = data.message || '確定完了';

            // ボイス再生
            const player = document.getElementById('voice-player');
            player.src = '../outputs/voice.wav?t=' + Date.now();
            player.play().catch(() => { });
            document.getElementById('result-voice-status').innerText = '🎙️ ボイス再生中...';
        })
        .catch(err => {
            btn.disabled = false;
            btn.innerText = '確定';
            alert('通信エラー: ' + err);
        });
}
