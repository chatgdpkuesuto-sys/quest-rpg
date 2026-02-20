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

    // 1. ズーム基準点の固定
    bg.style.transformOrigin = `50% 50%`;

    // 2. ズームブーストの減衰
    window.zoomBoost *= 0.95;

    // 3. 覗き窓（Container）を固定し、中のイラストを上下にスライド (Vertical Panning)
    // Y軸（縦）の background-position をパーセンテージでアニメーションさせる
    // 0% で「画像が下にスライド（顔が見える）」、100% で「画像が上にスライド（足元・股間が見える）」
    const swayAmplitude = 20 + (avgGauge * 30); // ゲージがあがると±幅が大きくなり、全身を舐め回すようになる
    const yPercent = 50 + (Math.sin(window.time * 0.8) * swayAmplitude);

    // 画像位置を更新（X軸は常に中央の50%で固定）
    bg.style.backgroundPosition = `50% ${yPercent}%`;

    // 4. スケールで「手前・奥（接近・後退）」を表現する
    // yPercent（上下スライド）に連動して、顔が近づく（下にスライドする）時は大きく、
    // 体を引く（上にスライドする）時は少し小さくなるように設定
    const baseScale = 1.1 + (avgGauge * 0.05) + window.zoomBoost;
    // Math.sin(time*0.8) を使って、上下スライドと同じ周期で息遣い（前後）を表現
    const zDepth = Math.sin(window.time * 0.8) * 0.08;

    const finalScale = baseScale - zDepth;

    // 物理的な移動（translateやrotate）は一切せず、純粋なズームのみ適用
    bg.style.transform = `scale(${finalScale})`;

    requestAnimationFrame(window.updateVisuals);
}
