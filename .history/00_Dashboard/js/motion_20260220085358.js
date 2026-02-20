// ==============================================
// 00_Dashboard: Motion Module (Sway, Zoom, Animation)
// ==============================================

window.updateVisuals = function () {
    // ゲージの平均値を計算（0.0 ~ 1.0）
    const avgGauge = (window.gauges.love + window.gauges.lust + window.gauges.special) / 300;

    // 速度は滑らかに一定に保ちつつ、ゲージがたまると目に見えて加速させる
    const speed = 0.015 + (avgGauge * 0.035);
    window.time += speed;

    const bg = document.getElementById('bg-container');
    if (!bg) return;

    // 1. ズーム基準点の固定 (常に中心)
    bg.style.transformOrigin = `50% 50%`;

    // 2. ズームブーストの減衰
    window.zoomBoost *= 0.95;

    // 3. ある程度ランダムな円運動 (Lissajous curve / multiple overlapping waves)
    // 🌟 基本の円運動に別の周期の波を混ぜて、予測できない「生き物のような」ランダムな揺らぎを作る
    const baseRadius = 15 + (avgGauge * 35); // 基本の振れ幅（最大50pxまで）

    // xは基本の横波 + 1.3倍速の波でランダム化
    const x = Math.sin(window.time) * baseRadius + Math.sin(window.time * 1.3) * (baseRadius * 0.4);

    // yは少し遅い波 + 1.7倍速の波でランダム化（Xと周期をズラして完全な円を崩す）
    const y = Math.cos(window.time * 0.8) * baseRadius + Math.cos(window.time * 1.7) * (baseRadius * 0.4);

    // 4. スケール計算 (Base + Gauge + Boost)
    // 🌟 ベースを1.2に引き上げ、最初からアップにしてパンニング時の黒縁を完全排除
    const scale = 1.2 + (avgGauge * 0.05) + window.zoomBoost;

    // 全てを統合して適用（鏡面反転を廃止）
    bg.style.transform = `
        translate(${x}px, ${y}px) 
        scale(${scale})
    `;

    requestAnimationFrame(window.updateVisuals);
}
