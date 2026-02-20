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

    // 1. ズーム基準点の固定 (目の高さをロック：上から30%の位置に固定)
    // これにより顔の位置が画面内でブレず、視点だけが動くような3D演出の軸ができる
    bg.style.transformOrigin = `50% 30%`;

    // 2. ズームブーストの減衰
    window.zoomBoost *= 0.95;

    // 3. イラスト自体の円満な円運動 (Restrained Circular Translation)
    // 🌟 これが「同じ形（円を描くように）」の元の動きです
    const moveRadius = 15 + (avgGauge * 30); // ゲージMAX時でも45px程度に抑える

    // X軸とY軸で同じ周期のsin/cosを使うことで、きれいな「円」を描かせます
    const x = Math.sin(window.time * 1.5) * moveRadius;
    const y = Math.cos(window.time * 1.5) * moveRadius;

    // 4. スケール計算 (Base + Gauge + Boost)
    // 🌟 動きが減った分、ズームも自然なレベルに抑える
    const scale = 1.3 + (avgGauge * 0.05) + window.zoomBoost;

    // 全てを統合して適用（物理的な移動のみ）
    bg.style.transform = `
        translate(${x}px, ${y}px)
        scale(${scale})
    `;

    requestAnimationFrame(window.updateVisuals);
}
