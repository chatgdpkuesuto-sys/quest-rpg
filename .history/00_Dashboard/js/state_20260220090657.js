// ==============================================
// 00_Dashboard: Global State Module
// ==============================================

window.gauges = { love: 0, lust: 0, special: 0 };
window.time = Math.random() * 1000; // 🌟 ページ更新ごとに開始位置（視点）をランダムにずらす
window.mirrorScale = 1;
window.pendingClimax = null;
window.currentOriginX = 50;
window.currentOriginY = 50;
window.targetOriginX = 50;
window.targetOriginY = 50;
window.zoomBoost = 0;
