// ==============================================
// 00_Dashboard: Interaction Module
// ==============================================

document.addEventListener('DOMContentLoaded', () => {
    const interactionLayer = document.getElementById('interaction-layer');
    if (!interactionLayer) return;

    // 右クリックメニューを無効化
    document.addEventListener('contextmenu', event => event.preventDefault());

    interactionLayer.addEventListener('mousedown', (e) => {
        // クリック座標の計算 (0.0 ~ 100.0)
        const rect = interactionLayer.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;

        let actionType = 'LOVE'; // Left click
        let className = 'left-click';
        if (e.button === 1) { actionType = 'SPECIAL'; className = 'middle-click'; } // Middle click
        else if (e.button === 2) { actionType = 'LUST'; className = 'right-click'; } // Right click

        // クリックエフェクトの表示
        createRipple(e.clientX, e.clientY, className);

        // バックエンド（bridge.py）に送信
        sendAction(actionType, x, y);
    });
});

function createRipple(x, y, className) {
    const ripple = document.createElement('div');
    ripple.className = `click-ripple ${className}`;
    ripple.style.left = `${x}px`;
    ripple.style.top = `${y}px`;

    // rippleサイズ
    ripple.style.width = '100px';
    ripple.style.height = '100px';

    document.body.appendChild(ripple);

    setTimeout(() => {
        ripple.remove();
    }, 600);
}

function sendAction(type, x, y) {
    const payload = {
        action: type,
        x: x.toFixed(2),
        y: y.toFixed(2),
        time: Date.now()
    };

    console.log("Sending action:", payload);

    fetch('http://127.0.0.1:5000/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    }).catch(err => console.error("Communication error with bridge:", err));
}
