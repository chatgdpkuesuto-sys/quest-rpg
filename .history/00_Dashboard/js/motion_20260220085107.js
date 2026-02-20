// ==============================================
// 00_Dashboard: Motion Module (Sway, Zoom, Animation)
// ==============================================

window.updateVisuals = function () {
    // ゲージの平均値を計算（0.0 ~ 1.0）
    const avgGauge = (window.gauges.love + window.gauges.lust + window.gauges.special) / 300;

    // 速度は滑らかに一定に保ちつつ、少しだけ加速
    const speed = 0.015 + (avgGauge * 0.015);
    window.time += speed;

    const bg = document.getElementById('bg-container');
    if (!bg) return;

    // 1. 滑らかなズーム基準点の移動 (Lerp)
    window.currentOriginX += (window.targetOriginX - window.currentOriginX) * 0.1;
    window.currentOriginY += (window.targetOriginY - window.currentOriginY) * 0.1;
    bg.style.transformOrigin = `${window.currentOriginX}% ${window.currentOriginY}%`;

    // 2. ズームブーストの減衰
    window.zoomBoost *= 0.95;

    // 3. 円運動 (Circular panning)
    // 🌟 はみ出ないように半径を最大50pxに制限
    const radius = 20 + (avgGauge * 30);
    const x = Math.sin(window.time) * radius;
    const y = Math.cos(window.time) * radius;

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

// 🌟 キネティック・フレームアニメーション（差分をコマ送りして命を吹き込む）
window.kineticAnimationLoop = function () {
    // 🌟 ユーザー要望：イラストの切り替わりはゲージマックス（pendingClimax）になってから！
    if (window.pendingClimax && typeof cycleVariant === "function") {
        cycleVariant();
    }

    // MAX時は高速（100msごと）、それ以外はゆったり待機
    const nextInterval = window.pendingClimax ? 150 : 1000;
    setTimeout(kineticAnimationLoop, nextInterval);
}
