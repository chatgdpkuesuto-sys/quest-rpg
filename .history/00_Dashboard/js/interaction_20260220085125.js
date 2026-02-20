// ==============================================
// 00_Dashboard: Interaction Module (Gauges & Buttons)
// ==============================================

window.triggerClimax = function () {
    if (!window.pendingClimax) return;

    console.log("🚀 TRIGGERING MANUAL CLIMAX!");

    // 1. AIへ送信
    if (window.sendAction) window.sendAction(window.pendingClimax.action, window.pendingClimax.x, window.pendingClimax.y);

    // 2. 立ち絵切り替え
    if (typeof cycleVariant === "function") cycleVariant();

    // 3. UIリセット
    const btn = document.getElementById('climax-trigger');
    btn.style.display = 'none';
    for (let k in window.gauges) window.gauges[k] = 0;
    document.querySelectorAll('.buildup-fill').forEach(el => el.style.width = '0%');

    window.pendingClimax = null;
}

// ゲージの自動減少（Decay）ロジック
window.startDecayLoop = function () {
    setInterval(() => {
        for (let key in window.gauges) {
            if (window.gauges[key] > 0) {
                window.gauges[key] -= 0.3;
                if (window.gauges[key] < 0) window.gauges[key] = 0;
                const fill = document.getElementById(`fill-${key}`);
                if (fill) fill.style.width = window.gauges[key] + '%';
            }
        }
    }, 100);
}

// クリックイベントハンドラ
window.setupInteraction = function () {
    document.addEventListener('mousedown', (event) => {
        if (event.target.id === 'init-audio' || event.target.id === 'climax-trigger') return;

        const xPercent = (event.clientX / window.innerWidth) * 100;
        const yPercent = (event.clientY / window.innerHeight) * 100;

        window.zoomBoost = 0.15; // 🌟 ズームしすぎてはみ出ないように 0.3 -> 0.15 に低減

        let clickType = 'heart';
        let gaugeKey = 'love';

        if (event.button === 2) {
            clickType = 'fire';
            gaugeKey = 'lust';
        } else if (event.button === 1) {
            clickType = 'blue-sparkle';
            gaugeKey = 'special';
        }

        window.gauges[gaugeKey] = Math.min(100, window.gauges[gaugeKey] + 15);

        const fill = document.getElementById(`fill-${gaugeKey}`);
        if (fill) fill.style.width = window.gauges[gaugeKey] + '%';

        if (window.createClickEffect) window.createClickEffect(xPercent, yPercent, clickType);

        if (window.gauges[gaugeKey] >= 100) {
            const pathNames = { love: "慈愛・調教ルート", lust: "淫靡・嗜虐ルート", special: "特殊・覚醒ルート" };
            const finalAction = `${pathNames[gaugeKey]} [深淵への発展]`;

            const btn = document.getElementById('climax-trigger');
            btn.className = gaugeKey;
            btn.innerText = "DEVOUR " + gaugeKey.toUpperCase();
            btn.style.display = 'block';

            window.pendingClimax = {
                action: finalAction,
                x: xPercent,
                y: yPercent
            };

            for (let i = 0; i < 15; i++) {
                setTimeout(() => {
                    if (window.createClickEffect) window.createClickEffect(50 + (Math.random() - 0.5) * 40, 50 + (Math.random() - 0.5) * 40, clickType);
                }, i * 40);
            }
        }
    });
}
