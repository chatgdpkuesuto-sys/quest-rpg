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

    // 3. イラスト自体の上下運動 (Vertical Panning)
    // 🌟 「視線を上下に動かす＝イラスト自体をそのまま上下に動かす」というリクエスト
    const moveRadiusY = 40 + (avgGauge * 180); // 上下（縦）の動きを主力に
    const moveRadiusX = 10 + (avgGauge * 20);  // 左右（横）は少しだけ揺らす

    // 縦（Y軸）メインで動き、横（X軸）は少しだけ揺らす
    const x = Math.sin(window.time * 0.8) * moveRadiusX;
    const y = Math.cos(window.time * 1.2) * moveRadiusY;

    // 4. スケール計算 (Base + Gauge + Boost)
    // 🌟 大きく動しても見切れないように初期スケールを高めに設定
    const scale = 1.6 + (avgGauge * 0.1) + window.zoomBoost;

    // 全てを統合して適用（物理的な移動のみ。3Dは使わない）
    bg.style.transform = `
        translate(${x}px, ${y}px)
        scale(${scale})
    `;

    requestAnimationFrame(window.updateVisuals);
}
