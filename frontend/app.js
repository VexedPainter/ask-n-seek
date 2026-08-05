const BASE_URL = '';
let currentVideoId = null;

// Navigation logic
const views = {
    'dashboard': ['chat-section'],
    'upload': ['hero', 'upload-section'],
    'results': ['top-objects-section', 'search-section', 'results-section']
};

function switchView(targetView) {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        if (btn.dataset.target === targetView) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    Object.keys(views).forEach(viewName => {
        const isTarget = viewName === targetView;
        views[viewName].forEach(sectionId => {
            const el = document.getElementById(sectionId);
            if (el) {
                if (isTarget) {
                    el.classList.remove('hidden');
                    // Retrigger observer for animations if needed
                    setTimeout(() => observer.observe(el), 10);
                } else {
                    el.classList.add('hidden');
                }
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => switchView(btn.dataset.target));
    });
    // Initialize default view
    switchView('dashboard');
});

// Intersection Observer for scroll reveal
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

// Realistic Cosmos/Galaxy Particles
const canvas = document.getElementById('particle-canvas');
const ctx = canvas.getContext('2d');
let particles = [];

function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

window.addEventListener('resize', resize);
resize();

class Particle {
    constructor() {
        this.angle = Math.random() * Math.PI * 2;
        // Concentrate particles in the center using power
        const maxRadius = Math.max(canvas.width, canvas.height);
        this.radius = Math.pow(Math.random(), 2.5) * maxRadius;
        this.size = Math.random() * 1.5 + 0.2;
        
        // Inner particles rotate faster
        this.speed = (Math.random() * 0.002 + 0.0005) * (200 / Math.max(this.radius, 50)); 
        
        // Colors: mostly white/silver with cyan/blue nebulas
        const colors = ['#ffffff', '#f8f8ff', '#00e5ff', '#87cefa', '#4682b4'];
        this.color = colors[Math.floor(Math.random() * colors.length)];
        this.opacity = Math.random() * 0.8 + 0.1;
    }
    update() {
        this.angle -= this.speed;
        this.x = canvas.width / 2 + Math.cos(this.angle) * this.radius;
        // Multiply Y by 0.6 to give the galaxy an elliptical/tilted 3D perspective
        this.y = canvas.height / 2 + Math.sin(this.angle) * (this.radius * 0.6);
    }
    draw() {
        ctx.fillStyle = this.color;
        ctx.globalAlpha = this.opacity;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1.0;
        
        if (this.size > 1.2) {
            ctx.shadowBlur = 8;
            ctx.shadowColor = this.color;
        } else {
            ctx.shadowBlur = 0;
        }
    }
}

// 800 particles for a dense, realistic starfield
for (let i = 0; i < 800; i++) {
    particles.push(new Particle());
}

let animationFrameId = null;

function animateParticles() {
    // Slight trailing effect for movement
    ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    particles.forEach(p => {
        p.update();
        p.draw();
    });
    
    animationFrameId = requestAnimationFrame(animateParticles);
}
animateParticles();

function pauseParticles() {
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
    }
}

function resumeParticles() {
    if (!animationFrameId) {
        animateParticles();
    }
}

// Drag and drop spotlight effect
const dropZone = document.getElementById('drop-zone');
dropZone.addEventListener('mousemove', (e) => {
    const rect = dropZone.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    dropZone.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(255,255,255,0.08) 0%, transparent 50%)`;
});
dropZone.addEventListener('mouseleave', () => {
    dropZone.style.background = 'transparent';
});

// Upload handling
const fileInput = document.getElementById('file-input');
const browseBtn = document.querySelector('.browse-btn');

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'rgba(255,255,255,0.5)';
});
dropZone.addEventListener('dragleave', () => {
    dropZone.style.borderColor = 'rgba(255,255,255,0.05)';
});
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'rgba(255,255,255,0.05)';
    if (e.dataTransfer.files.length) {
        handleUpload(e.dataTransfer.files[0]);
    }
});
browseBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
});
dropZone.addEventListener('click', () => {
    fileInput.click();
});
fileInput.addEventListener('change', () => {
    if (fileInput.files.length) {
        handleUpload(fileInput.files[0]);
    }
});

async function handleUpload(file) {
    currentVideoId = file.name;
    document.getElementById('ingest-status').classList.remove('hidden');
    document.getElementById('progress-text').innerText = 'Uploading...';
    pauseParticles();
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const res = await fetch(`${BASE_URL}/ingest`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        pollStatus(data.job_id);
    } catch (err) {
        alert('Upload failed: ' + err.message);
    }
}

function pollStatus(jobId) {
    const pBar = document.getElementById('progress-bar');
    const pText = document.getElementById('progress-text');
    
    const interval = setInterval(async () => {
        try {
            const res = await fetch(`${BASE_URL}/ingest/status/${jobId}`);
            const data = await res.json();
            
            pBar.style.width = `${data.progress_pct}%`;
            pText.innerText = `${data.current_phase} (${data.progress_pct}%)`;
            
            if (data.status === 'COMPLETED') {
                clearInterval(interval);
                pText.innerText = 'Ingestion Complete';
                resumeParticles();
                onIngestComplete();
            } else if (data.status === 'FAILED') {
                clearInterval(interval);
                pText.innerText = `Failed: ${data.current_phase}`;
                resumeParticles();
            }
        } catch (err) {
            console.error('Polling error', err);
        }
    }, 800);
}

async function onIngestComplete() {
    // Automatically switch to Results view
    switchView('results');
    
    // Fetch Top Objects
    try {
        const res = await fetch(`${BASE_URL}/video/${currentVideoId}/top-objects`);
        const data = await res.json();
        renderTopObjects(data.objects);
    } catch (err) {
        console.error('Failed to fetch top objects', err);
    }
}

function renderTopObjects(objects) {
    const grid = document.getElementById('objects-grid');
    grid.innerHTML = '';
    
    if (!objects || objects.length === 0) {
        grid.innerHTML = '<p class="subheadline">No distinct objects identified.</p>';
        return;
    }
    
    objects.forEach(obj => {
        const card = document.createElement('div');
        card.className = 'object-card';
        card.innerHTML = `
            <h3 class="object-class">${obj.class_name}</h3>
            <div class="object-meta">
                <span>Count: ${obj.count}</span>
                <span>Avg Conf: ${(obj.avg_confidence * 100).toFixed(0)}%</span>
                ${obj.dominant_color ? `<span>Color: ${obj.dominant_color}</span>` : ''}
            </div>
        `;
        grid.appendChild(card);
    });
}

// Search
document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.getElementById('search-input').value = btn.dataset.query;
    });
});

document.getElementById('search-btn').addEventListener('click', performSearch);
document.getElementById('search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') performSearch();
});

async function performSearch() {
    const query = document.getElementById('search-input').value.trim();
    if (!query || !currentVideoId) return;
    
    const resultsSec = document.getElementById('results-section');
    resultsSec.classList.remove('hidden');
    setTimeout(() => observer.observe(resultsSec), 100);
    
    const msgEl = document.getElementById('results-message');
    const listEl = document.getElementById('jump-list');
    msgEl.innerHTML = 'Searching...';
    msgEl.className = 'results-message';
    listEl.innerHTML = '';
    
    try {
        const res = await fetch(`${BASE_URL}/query`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: query, video_id: currentVideoId})
        });
        const data = await res.json();
        
        renderResults(data);
    } catch (err) {
        msgEl.innerHTML = 'Search failed: ' + err.message;
    }
}

let pauseTimeout = null;

function renderResults(data) {
    const msgEl = document.getElementById('results-message');
    const listEl = document.getElementById('jump-list');
    const player = document.getElementById('video-player');
    
    // Ensure video is loaded
    if (!player.src || !player.src.includes(currentVideoId)) {
        player.src = `${BASE_URL}/video/${currentVideoId}`;
    }
    
    if (data.no_match_diagnosis) {
        const diag = data.no_match_diagnosis;
        msgEl.innerText = diag.message;
        if (diag.type === 'unsupported_vocabulary') {
            msgEl.className = 'results-message msg-unsupported';
        } else {
            msgEl.className = 'results-message msg-constraint';
        }
        return;
    }
    
    msgEl.innerText = `Found ${data.results.length} matches`;
    msgEl.className = 'results-message';
    
    data.results.forEach(r => {
        const card = document.createElement('div');
        card.className = 'result-card';
        
        // Extract confidence from explanation (e.g. "... max confidence 0.81")
        const confMatch = r.explanation.match(/confidence ([\d.]+)/);
        const conf = confMatch ? parseFloat(confMatch[1]) : 0;
        
        const start = r.start !== undefined ? r.start : r.window;
        const end = r.end !== undefined ? r.end : r.window;
        
        let timeText = formatTime(start);
        if (start !== end) {
            timeText += ` - ${formatTime(end)}`;
        }
        
        card.innerHTML = `
            <div class="result-header">
                <span class="timestamp">${timeText}</span>
                <div class="confidence-track">
                    <div class="confidence-fill" style="width: ${conf * 100}%"></div>
                </div>
            </div>
            <p class="explanation">${r.explanation}</p>
        `;
        
        card.addEventListener('click', () => {
            seekToTimestamp(start, end);
        });
        
        listEl.appendChild(card);
    });
}

function seekToTimestamp(start, end) {
    const player = document.getElementById('video-player');
    
    // Ensure video is loaded
    if (!player.src || !player.src.includes(currentVideoId)) {
        player.src = `${BASE_URL}/video/${currentVideoId}`;
    }
    
    // Smooth scroll up to the video player
    player.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    player.currentTime = start;
    
    // Wait 1 second for the scroll to finish before playing
    setTimeout(() => {
        const playPromise = player.play();
        
        if (playPromise !== undefined) {
            playPromise.catch(error => {
                console.warn("Playback interrupted or blocked. Trying muted...", error);
                player.muted = true;
                player.play().catch(e => console.error("Playback fully blocked:", e));
            });
        }
    }, 1000);
    
    if (window.activePauseTimeout) {
        clearTimeout(window.activePauseTimeout);
    }
    
    if (end !== undefined && end !== null) {
        const checkPause = () => {
            if (player.currentTime >= end + 1) {
                player.pause();
            } else if (!player.paused) {
                window.activePauseTimeout = setTimeout(checkPause, 100);
            }
        };
        window.activePauseTimeout = setTimeout(checkPause, 100);
    }
}

function formatTime(s) {
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
}

// ── Chat Panel ──────────────────────────────────────────────────────

const chatInput = document.getElementById('chat-input');
const chatSendBtn = document.getElementById('chat-send-btn');
const chatMessages = document.getElementById('chat-messages');
const chatTyping = document.getElementById('chat-typing');

chatSendBtn.addEventListener('click', () => {
    const text = chatInput.value.trim();
    if (text) sendChatMessage(text);
});

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const text = chatInput.value.trim();
        if (text) sendChatMessage(text);
    }
});

function appendBubble(type, content) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${type}-bubble`;
    
    const avatar = document.createElement('div');
    avatar.className = 'bubble-avatar';
    avatar.textContent = type === 'ai' ? '✧' : '◆';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'bubble-content';
    
    if (typeof content === 'string') {
        const p = document.createElement('p');
        p.textContent = content;
        contentDiv.appendChild(p);
    } else {
        contentDiv.appendChild(content);
    }
    
    bubble.appendChild(avatar);
    bubble.appendChild(contentDiv);
    chatMessages.appendChild(bubble);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return contentDiv;
}

function showTyping() {
    chatTyping.classList.remove('hidden');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTyping() {
    chatTyping.classList.add('hidden');
}

async function sendChatMessage(text) {
    if (!currentVideoId) {
        appendBubble('ai', 'Please upload a video first before asking questions.');
        return;
    }
    
    // Append user bubble
    appendBubble('user', text);
    chatInput.value = '';
    
    // Show typing indicator
    showTyping();
    
    try {
        const res = await fetch(`${BASE_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text, video_id: currentVideoId })
        });
        const data = await res.json();
        
        hideTyping();
        
        // Build AI response content
        const fragment = document.createDocumentFragment();
        
        // Reply text
        const replyP = document.createElement('p');
        replyP.textContent = data.reply || 'No response received.';
        fragment.appendChild(replyP);
        
        // Language tag if non-English
        if (data.language_detected && data.language_detected !== 'en') {
            const langNames = { hi: 'Hindi', kn: 'Kannada', ta: 'Tamil', te: 'Telugu', ml: 'Malayalam' };
            const langTag = document.createElement('div');
            langTag.className = 'bubble-lang-tag';
            langTag.textContent = `Detected: ${langNames[data.language_detected] || data.language_detected}`;
            fragment.appendChild(langTag);
        }
        
        // Inline result chips if results exist
        if (data.results && data.results.length > 0) {
            const strip = document.createElement('div');
            strip.className = 'chat-result-strip';
            
            // Show up to 8 chips, then a "+N more" label
            const maxChips = 8;
            const showResults = data.results.slice(0, maxChips);
            
            showResults.forEach(r => {
                const start = r.start !== undefined ? r.start : r.window;
                const end = r.end !== undefined ? r.end : start;
                
                const chip = document.createElement('span');
                chip.className = 'chat-result-chip';
                chip.innerHTML = `<span class="chip-icon">▶</span> ${formatTime(start)}`;
                chip.title = r.explanation || `Jump to ${formatTime(start)}`;
                
                chip.addEventListener('click', (e) => {
                    e.stopPropagation();
                    // Switch view to Results where the video player is
                    switchView('results');
                    const player = document.getElementById('video-player');
                    if (!player.src || !player.src.includes(currentVideoId)) {
                        player.src = `${BASE_URL}/video/${currentVideoId}`;
                    }
                    seekToTimestamp(start, end);
                });
                
                strip.appendChild(chip);
            });
            
            if (data.results.length > maxChips) {
                const more = document.createElement('span');
                more.className = 'chat-result-chip';
                more.textContent = `+${data.results.length - maxChips} more`;
                more.style.cursor = 'default';
                more.style.opacity = '0.6';
                strip.appendChild(more);
            }
            
            fragment.appendChild(strip);
        }
        
        appendBubble('ai', fragment);
        
    } catch (err) {
        hideTyping();
        appendBubble('ai', `Something went wrong: ${err.message}`);
    }
}
