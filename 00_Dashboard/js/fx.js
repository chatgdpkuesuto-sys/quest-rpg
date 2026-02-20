// ==============================================
// 00_Dashboard: FX Module (Particles & Ripples)
// ==============================================

// 🌟 定期的にかわいいエフェクト（ハートやキラキラ）を降らせる
window.spawnKawaiiParticle = function () {
    const particles = ['💖', '✨', '⭐', '🐾', '🎀'];
    const p = document.createElement('div');
    p.className = 'click-effect'; // CSSを流用
    p.innerHTML = particles[Math.floor(Math.random() * particles.length)];
    p.style.left = Math.random() * 100 + '%';
    p.style.top = '110%'; // 画面下から
    p.style.fontSize = (1 + Math.random() * 2) + 'rem';
    p.style.opacity = '0.7';
    document.body.appendChild(p);

    // 下から上へゆっくり浮かぶアニメーション
    p.animate([
        { transform: 'translateY(0) scale(1)', opacity: 0.7 },
        { transform: 'translateY(-100vh) scale(1.5)', opacity: 0 }
    ], { duration: 5000 + Math.random() * 3000, easing: 'ease-out' });

    setTimeout(() => p.remove(), 8000);
}

// 🌟 クリックエフェクト（視覚的ギミック）
window.createClickEffect = function (x, y, type = 'heart') {
    const effect = document.createElement('div');
    effect.className = 'click-effect';
    effect.style.left = x + '%';
    effect.style.top = y + '%';

    // タイプによってアイコンを変える
    if (type === 'heart') effect.innerHTML = '❤️';
    else if (type === 'blue-sparkle') effect.innerHTML = '✨';
    else effect.innerHTML = '🔥';

    document.body.appendChild(effect);

    // 効果音の再生（ある場合）
    const se = document.getElementById('se-player');
    if (se) {
        se.src = 'sounds/hit.mp3';
        se.play().catch(e => console.log("SE Play blocked"));
    }

    setTimeout(() => effect.remove(), 800);
}
