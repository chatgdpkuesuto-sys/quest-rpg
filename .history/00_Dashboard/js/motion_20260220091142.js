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

    // 3. 視線だけを動かす3Dモーション (Eye-Level Locked Parallax)
    // 🌟 物理的に画像を上下に動かさず、3Dの「X軸回転（pitch）」を使う
    // 目線（transformOrigin 30%）を軸にして首を上下に乗るような動きになり
    // 「目は合ったまま視線で身体を舐め回す」ような奥行きのある動きになります
    const maxTilt = 10 + (avgGauge * 30); // ゲージMAX時は30度まで大きく傾く
    const rotX = Math.sin(window.time * 1.2) * maxTilt; // 仰け反りと前傾

    // ほんの少しだけ左右に揺れる（自然な手ブレや息遣いのため）
    const swayX = Math.cos(window.time * 0.9) * (5 + avgGauge * 15);

    // 4. スケール計算 (Base + Gauge + Boost)
    // 🌟 端が見切れないように少し大きめ
    const scale = 1.6 + (avgGauge * 0.1) + window.zoomBoost;

    // 全てを統合して適用（Y軸への激しい移動は避け、回転で視点移動を表現）
    bg.style.transform = `
        translateX(${swayX}px)
        rotateX(${rotX}deg)
        scale(${scale})
    `;

    requestAnimationFrame(window.updateVisuals);
}
