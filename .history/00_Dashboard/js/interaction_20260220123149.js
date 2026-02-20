// ==============================================
// 00_Dashboard: interaction.js
// ==============================================

document.addEventListener('DOMContentLoaded', () => {
    const layer = document.getElementById('interaction-layer');
    if (!layer) return;

    layer.addEventListener('mousedown', (e) => {
        if (window.isProcessing) return;

        const rect = layer.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;

        let type = 'LOVE'; // Left
        if (e.button === 1) type = 'SPECIAL'; // Middle
        else if (e.button === 2) type = 'LUST'; // Right

        createRipple(e.clientX, e.clientY, type.toLowerCase());

        const payload = {
            action: type,
            x: x.toFixed(2),
            y: y.toFixed(2),
            time: Date.now()
        };

        fetch('http://127.0.0.1:5000/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }).catch(err => console.error("Bridge interaction failed:", err));
    });

    // 右クリック防止
    document.addEventListener('contextmenu', e => e.preventDefault());
});

function createRipple(x, y, type) {
    const r = document.createElement('div');
    r.className = `click-ripple ripple-${type}`;
    r.style.left = `${x}px`;
    r.style.top = `${y}px`;
    document.body.appendChild(r);
    setTimeout(() => r.remove(), 600);
}
