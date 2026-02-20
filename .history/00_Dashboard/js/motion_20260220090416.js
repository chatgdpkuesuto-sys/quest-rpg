// ==============================================
// 00_Dashboard: Motion Module (Sway, Zoom, Animation)
// ==============================================

window.updateVisuals = function () {
    // ゲージの平均値を計算（0.0 ~ 1.0）
    const avgGauge = (window.gauges.love + window.gauges.lust + window.gauges.special) / 300;

    // 速度は滑らかに一定に保ちつつ、ゲージがたまると目に見えて加速させる
    // 🌟 加速の度合いをさらに強く！
    const speed = 0.02 + (avgGauge * 0.06);
    window.time += speed;

    const bg = document.getElementById('bg-container');
    if (!bg) return;

    // 1. ズーム基準点の固定 (常に中心)
    bg.style.transformOrigin = `50% 50%`;

    // 2. ズームブーストの減衰
    window.zoomBoost *= 0.95;

    // 3. イラスト自体の巨大な円運動 (Physical Translation)
    // 🌟 3Dの傾きではなく、画像そのものが画面内をぐるぐると大きく動き回る
    const moveRadius = 20 + (avgGauge * 120); // ゲージMAX時は140pxもの大円を描く

    // X軸とY軸で円を描くように物理的に移動（translate）させる
    const x = Math.sin(window.time * 1.5) * moveRadius;
    const y = Math.cos(window.time * 1.5) * moveRadius;

    // 4. スケール計算 (Base + Gauge + Boost)
    // 🌟 大きく動く分、黒枠が見えないように初期ズームをかなり大きくしておく
    const scale = 1.6 + (avgGauge * 0.1) + window.zoomBoost;

    // 全てを統合して適用（物理的な移動のみ）
    bg.style.transform = `
        translate(${x}px, ${y}px)
        scale(${scale})
    `;

    requestAnimationFrame(window.updateVisuals);
}
