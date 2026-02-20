// ==============================================
// 00_Dashboard: Main Initialization & API Module
// ==============================================

// API連携関数 (Flaskサーバーへアクション送信)
window.sendAction = async function (actionName, x = 0, y = 0) {
    console.log(`Action Sent: ${actionName} at (${x}%, ${y}%)`);

    try {
        await fetch(`http://localhost:5000/action?t=${Date.now()}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: actionName, x: x, y: y, time: Date.now() })
        });
    } catch (e) {
        console.error("Failed to send action:", e);
    }
}

// 初期化処理
document.addEventListener('DOMContentLoaded', () => {
    // 🌟 画場が映らない（真っ黒）問題の防止：
    // status.json が読み込まれる前、または存在しない場合のフェールセーフ
    const bgContainer = document.getElementById('bg-container');
    if (bgContainer && !bgContainer.style.backgroundImage) {
        bgContainer.style.backgroundImage = `url('outputs/variants/variant_1.png')`;
    }

    // 各モジュールの起動
    if (typeof window.initEngine === "function") window.initEngine();
    if (typeof window.updateVisuals === "function") window.updateVisuals();
    if (typeof window.startDecayLoop === "function") window.startDecayLoop();
    if (typeof window.setupInteraction === "function") window.setupInteraction();
});
