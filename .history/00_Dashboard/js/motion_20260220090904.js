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

    // 3. イラスト自体の上下運動 (Vertical Panning)
    // 🌟 ユーザー要望により「上と下を見るような感じ」に特化させる
    // ゲージMAX時は大きく上下にパンニングする
    const moveRadiusY = 40 + (avgGauge * 180); // 上下（縦）の動きを非常に大きく
    const moveRadiusX = 10 + (avgGauge * 20);  // 左右（横）の揺れは少しだけ（自然さを残す）

    // 縦（Y軸）メインで動き、横（X軸）は少しだけ揺らす
    const x = Math.sin(window.time * 0.8) * moveRadiusX;
    const y = Math.cos(window.time * 1.2) * moveRadiusY;

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
