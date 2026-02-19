// ==============================================
// MACHADUN ENGINE: CHAOS LOGIC
// ==============================================

const logWindow = document.getElementById('log-window');
const actionInput = document.getElementById('action-input');
const bloodOverlay = document.getElementById('blood-overlay');

// --- Audio Generation via Web Audio API ---
// Generate synthetic beeps/noises (No external files needed)
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function playGlitchSound() {
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const osc = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(150, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(40, audioCtx.currentTime + 0.1);

    gainNode.gain.setValueAtTime(0.3, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);

    osc.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    osc.start();
    osc.stop(audioCtx.currentTime + 0.1);
}

function playClimaxSound() {
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const osc = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(800, audioCtx.currentTime);
    osc.frequency.linearRampToValueAtTime(1200, audioCtx.currentTime + 0.5);
    osc.frequency.linearRampToValueAtTime(0, audioCtx.currentTime + 1.5);

    gainNode.gain.setValueAtTime(0.5, audioCtx.currentTime);
    gainNode.gain.linearRampToValueAtTime(1, audioCtx.currentTime + 0.5);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 1.5);

    osc.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    osc.start();
    osc.stop(audioCtx.currentTime + 1.5);
}

// --- Text Parser for Chaos Effects ---
// Replace raw keywords with HTML span tags for CSS animations
function parseChaosText(text) {
    let parsed = text;

    // Heartbeat Keywords
    parsed = parsed.replace(/快感|絶頂|子宮|媚薬/g, '<span class="heartbeat">$&</span>');
    parsed = parsed.replace(/あぁっ|ドクン/g, '<span class="neon-pink">$&</span>');

    // Shake / Despair Keywords
    parsed = parsed.replace(/致命傷|死亡|ゲームオーバー|LP: 0/g, '<span class="extreme-red">$&</span>');

    // Manual Glitch Target
    parsed = parsed.replace(/\*\*\*(.*?)\*\*\*/g, '<span class="glitch-text" data-text="$1">$1</span>');

    return parsed;
}

// --- Appending Logs ---
function appendMessage(sender, rawText) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}-message`;

    // Parse the text for chaos keywords
    msgDiv.innerHTML = parseChaosText(rawText);
    logWindow.appendChild(msgDiv);

    // Auto Scroll
    logWindow.scrollTop = logWindow.scrollHeight;

    // Trigger Screen Effects depending on content
    if (rawText.includes("絶頂") || rawText.includes("死") || rawText.includes("***")) {
        bloodOverlay.classList.add('active');
        playClimaxSound();
        document.body.style.animation = "shake 0.5s";

        setTimeout(() => {
            bloodOverlay.classList.remove('active');
            document.body.style.animation = "none";
        }, 1500);
    } else {
        playGlitchSound();
    }
}

// --- Event Listeners ---
actionInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        const text = actionInput.value.trim();
        if (text) {
            // 1. Show user message
            appendMessage('user', "> " + text);
            actionInput.value = '';

            // 2. Play typing/submitting sound
            playGlitchSound();

            // 3. Simulate AI GM Response after delay
            setTimeout(() => {
                simulateGMResponse(text);
            }, 1000);
        }
    }
});

function simulateGMResponse(userText) {
    // A rudimentary logic to demonstrate the chaos. 
    // In reality, this would fetch from the python backend or LLM.
    let response = "";
    if (userText.includes("アリア")) {
        response = "「まさか…『男』……！？ いえ、あり得ない…でも、この匂い、この匂いはぁっ…！！」<br>騎士の誇りをかなぐり捨て、強烈な快感の予感に太ももをガクガクと震わせている。";
    } else if (userText.includes("絶頂")) {
        response = "***限界を超えた刺激***が脳を焼き切る！<br>「あぁっ！　もう、無理ぃっ、いくぅぅううっ！！」<br>彼女は致命傷に等しい快感に身をよじらせた。";
    } else {
        response = "少女たちはその行動に目を丸くし、次なる本能の赴くままにあなたへ距離を詰める。<br>逃げるか、それともこのまま***捕食***されるか？";
    }

    appendMessage('gm', response);
}
