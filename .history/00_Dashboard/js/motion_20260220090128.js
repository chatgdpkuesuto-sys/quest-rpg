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

    // 3. 大きく・速くなる円運動（少しだけランダムな揺らぎを入れる）
    // 🌟 ゲージによって半径（移動範囲）をかなり大きく広げる
    const baseRadius = 10 + (avgGauge * 60); // 10px 〜 70px

    // 基本の円運動をメインにしつつ、微妙に異なる周期の波を混ぜて少しランダムに見せる
    const x = Math.sin(window.time) * baseRadius + Math.sin(window.time * 2.1) * (baseRadius * 0.2);
    const y = Math.cos(window.time) * baseRadius + Math.cos(window.time * 1.6) * (baseRadius * 0.2);

    // 4. 新たな3D傾き効果 (Pseudo-3D Parallax Tilt: 視点円運動)
    // 🌟 視点（カメラ）が円を描くように動く立体演出
    const maxTilt = 10 + (avgGauge * 20); // 最大傾斜角 (10度〜30度)

    // X軸（上下）とY軸（左右）の傾きに、それぞれsinとcosを使うことで、
    // まるでカメラがイラストの周りをぐるぐると円を描きながら回っているような3D感になります。
    const rotX = Math.sin(window.time * 1.5) * maxTilt;
    const rotY = Math.cos(window.time * 1.5) * maxTilt;

    // 5. スケール計算 (Base + Gauge + Boost)
    // 🌟 3D傾きで奥の端が見切れないようにベーススケールをさらに少しアップ
    const scale = 1.35 + (avgGauge * 0.05) + window.zoomBoost;

    // 全てを統合して適用（3D回転を追加）
    bg.style.transform = `
        translate(${x}px, ${y}px)
        rotateX(${rotX}deg)
        rotateY(${rotY}deg)
        scale(${scale})
    `;

    requestAnimationFrame(window.updateVisuals);
}
