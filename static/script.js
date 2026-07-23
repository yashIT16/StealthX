// Matrix digital rain background
const canvas = document.getElementById('matrixCanvas');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$+-*/=%""\'#&_(),.;:?!\\|{}<>[]^~';
const fontSize = 14;
const columns = canvas.width / fontSize;
const drops = [];
for(let x = 0; x < columns; x++) drops[x] = 1;

function drawMatrix() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = '#0F0';
    ctx.font = fontSize + 'px monospace';
    
    for(let i = 0; i < drops.length; i++) {
        const text = letters.charAt(Math.floor(Math.random() * letters.length));
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);
        if(drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
    }
}
setInterval(drawMatrix, 33);

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const newColumns = Math.floor(canvas.width / fontSize);
    const currentLength = drops.length;
    
    if (newColumns > currentLength) {
        for(let x = currentLength; x < newColumns; x++) {
            drops[x] = 1;
        }
    } else {
        drops.length = newColumns;
    }
});

// UI Navigation
const navLinks = document.querySelectorAll('.nav-links a');
const sections = document.querySelectorAll('.glass-panel');

navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        navLinks.forEach(l => l.classList.remove('active'));
        e.target.classList.add('active');
        
        sections.forEach(s => s.classList.add('hidden'));
        document.getElementById(e.target.dataset.target).classList.remove('hidden');
    });
});

// Utility APIs
async function postData(url, data) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return res.json();
}

async function getData(url) {
    const res = await fetch(url);
    return res.json();
}

// Analyzer
document.getElementById('analyze-btn').addEventListener('click', async () => {
    const pwd = document.getElementById('analyze-input').value;
    if(!pwd) return;
    
    const data = await postData('/api/analyze', { password: pwd });
    
    document.getElementById('analyze-results').classList.remove('hidden');
    
    const colors = ["#ff2a2a", "#ff7b00", "#ffb800", "#a1ff00", "#00ff41"];
    const labels = ["Very Weak", "Weak", "Fair", "Strong", "Very Strong"];
    
    const fill = document.getElementById('strength-fill');
    fill.style.width = ((data.score + 1) * 20) + '%';
    fill.style.background = colors[data.score];
    
    document.getElementById('score-text').innerText = `Score: ${data.score}/4 - ${labels[data.score]}`;
    document.getElementById('score-text').style.color = colors[data.score];
    
    document.getElementById('res-entropy').innerText = data.entropy;
    document.getElementById('res-breches').innerText = data.breaches;
    if (data.breaches > 0) document.getElementById('res-breches').classList.add('warning-text');
    else document.getElementById('res-breches').classList.remove('warning-text');
    
    document.getElementById('ct-fast').innerText = data.crack_times.online_fast;
    document.getElementById('ct-slow').innerText = data.crack_times.offline_slow;
    document.getElementById('ct-vfast').innerText = data.crack_times.offline_fast;
    
    const fb = document.getElementById('res-feedback');
    fb.innerHTML = '';
    if(data.feedback.warning) fb.innerHTML += `<li><b>Warning:</b> ${data.feedback.warning}</li>`;
    data.feedback.suggestions.forEach(s => fb.innerHTML += `<li>${s}</li>`);
});

// Generator
const lenInput = document.getElementById('gen-len');
const lenDisp = document.getElementById('len-disp');
lenInput.addEventListener('input', () => lenDisp.innerText = lenInput.value);

document.getElementById('gen-btn').addEventListener('click', async () => {
    const data = await postData('/api/generate', {
        length: parseInt(lenInput.value),
        uppercase: document.getElementById('gen-up').checked,
        lowercase: document.getElementById('gen-low').checked,
        numbers: document.getElementById('gen-num').checked,
        special: document.getElementById('gen-spec').checked
    });
    document.getElementById('gen-output').value = data.password;
});

// Attack
document.getElementById('attack-btn').addEventListener('click', async () => {
    const pwd = document.getElementById('attack-target').value;
    const mode = document.getElementById('attack-mode').value;
    if(!pwd) return;
    
    const term = document.getElementById('attack-results');
    const content = document.getElementById('term-content');
    
    term.classList.remove('hidden');
    content.innerHTML = `> Initiating attack sequence...<br>> Hashing target...<br>`;
    
    // Disable button during execution
    const btn = document.getElementById('attack-btn');
    btn.disabled = true;
    btn.innerText = "ATTACKING...";
    
    const data = await postData('/api/attack', { password: pwd, mode: mode });
    
    content.innerHTML += `> Target Hash (MD5Crypt): <span class="elec-text">${data.hash}</span><br>`;
    content.innerHTML += `> Mode: ${data.result.mode}<br><br>`;
    
    if(data.result.success) {
        content.innerHTML += `> <span style="color:#00ff41">CRACKED!</span> Password found: <b>${data.result.password}</b><br>`;
        content.innerHTML += `> Time: ${data.result.time_taken}s`;
    } else {
        // Strip out the exact word "error" or "Error" if it exists in the message so it looks cleaner
        let errMsg = data.result.error || 'Complexity too high.';
        errMsg = errMsg.replace(/error:?\s*/i, "");
        content.innerHTML += `> <span style="color:#ff2a2a">NOT CRACKED.</span> ${errMsg}<br>`;
        content.innerHTML += `> Time: ${data.result.time_taken}s`;
    }
    
    btn.disabled = false;
    btn.innerText = "INITIATE";
});

// Pwned Checker
document.getElementById('pwned-btn').addEventListener('click', async () => {
    const pwd = document.getElementById('pwned-input').value;
    if(!pwd) return;
    
    // Disable button during execution
    const btn = document.getElementById('pwned-btn');
    btn.disabled = true;
    btn.innerText = "CHECKING...";
    
    const data = await postData('/api/check-pwned', { password: pwd });
    
    document.getElementById('pwned-results').classList.remove('hidden');
    const msgEl = document.getElementById('pwned-status-msg');
    const countEl = document.getElementById('pwned-count');
    
    countEl.innerText = data.breaches;
    
    if (data.breaches > 0) {
        msgEl.innerHTML = `<span style="color:#ff2a2a">DANGER: THIS PASSWORD IS PWNED!</span>`;
        countEl.style.color = '#ff2a2a';
    } else if (data.breaches === 0) {
        msgEl.innerHTML = `<span style="color:#00ff41">SAFE: NO MATCHES FOUND.</span>`;
        countEl.style.color = '#00ff41';
    } else {
        msgEl.innerHTML = `<span style="color:#ffb800">ERROR: COULD NOT REACH HIBP API.</span>`;
        countEl.style.color = '#ffb800';
    }
    
    btn.disabled = false;
    btn.innerText = "CHECK STATUS";
});

// History
async function refreshHistory() {
    const data = await getData('/api/history');
    const tbody = document.querySelector('#hist-table tbody');
    tbody.innerHTML = '';
    
    [...data].reverse().forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${r.timestamp.substring(0,19).replace('T', ' ')}</td>
            <td>${r.type}</td>
            <td>${JSON.stringify(r.details)}</td>
        `;
        tbody.appendChild(tr);
    });
}
document.getElementById('refresh-hist-btn').addEventListener('click', refreshHistory);
document.querySelector('a[data-target="history-sec"]').addEventListener('click', refreshHistory);
