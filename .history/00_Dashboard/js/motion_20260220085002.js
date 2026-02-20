// ==============================================
// 00_Dashboard: Motion Module (Sway, Zoom, Animation)
// ==============================================

window.updateVisuals = function () {
    // ゲージの平均値を計算（0.0 ~ 1.0）
    const avgGauge = (window.gauges.love + window.gauges.lust + window.gauges.special) / 300;

    // 速度アップ（蓄積量に応じて呼吸が激しくなるイメージ）
    const speed = 0.02 + (avgGauge * 0.1);
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
    // 🌟 最初からアップにしつつ、円を描くように滑らかに動く
    const radius = 30 + (avgGauge * 50); // 半径30px〜80pxで円運動
    const x = Math.sin(window.time) * radius;
    const y = Math.cos(window.time) * radius;

    // 4. スケール計算 (Base + Gauge + Boost)
    // 🌟 ベースを1.15（最初から少しアップ）にすることで、移動時に画像のはみ出し（黒枠）を隠す
    const scale = 1.15 + (avgGauge * 0.1) + window.zoomBoost;

    // 全てを統合して適用
    bg.style.transform = `
        scaleX(${window.mirrorScale}) 
        translate(${x}px, ${y}px) 
        scale(${scale})
    `;

    requestAnimationFrame(updateVisuals);
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
