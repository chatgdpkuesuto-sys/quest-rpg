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

    // 4. スケール計算 (Base + Gauge + Boost)
    // 🌟 円周が広がる分、ベースを1.25に引き上げてパンニング時の黒縁を完全排除
    const scale = 1.25 + (avgGauge * 0.05) + window.zoomBoost;

    // 全てを統合して適用（鏡面反転を廃止）
    bg.style.transform = `
        translate(${x}px, ${y}px) 
        scale(${scale})
    `;

    requestAnimationFrame(window.updateVisuals);
}
