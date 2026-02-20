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

    // 3. 視線だけを上下に動かす3Dモーション (ユーザー要望: 目の高さを維持して視線を動かす)
    // 目線（transformOrigin 30%）を軸にして首を上下に乗るような動きになり
    const maxTilt = 10 + (avgGauge * 30); // ゲージMAX時は30度まで大きく傾く
    const rotX = Math.sin(window.time * 1.2) * maxTilt; // 仰け反りと前傾

    // 4. イラスト自体は円をえがくようにうごいて (ユーザー要望: X/Yの円運動)
    const moveRadius = 15 + (avgGauge * 20);
    const x = Math.sin(window.time * 1.5) * moveRadius;
    const y = Math.cos(window.time * 1.5) * moveRadius;

    // 5. イラストを前後に動かして (ユーザー要望: スケールを波打たせて前後感を表現)
    const zSway = Math.sin(window.time * 2.0) * (0.05 + avgGauge * 0.1);

    // 6. スケール計算 (Base + Gauge + Boost + 前後スウェイ)
    // 🌟 端が見切れないように少し大きめ
    const scale = 1.6 + (avgGauge * 0.1) + window.zoomBoost + zSway;

    // 全てを統合して適用
    bg.style.transform = `
        translate(${x}px, ${y}px)
        rotateX(${rotX}deg)
        scale(${scale})
    `;

    requestAnimationFrame(window.updateVisuals);
}
