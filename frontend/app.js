const BASE_URL = '';
let currentVideoId = null;

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
    // Show Top Objects and Search sections
    const topSec = document.getElementById('top-objects-section');
    const searchSec = document.getElementById('search-section');
    
    topSec.classList.remove('hidden');
    searchSec.classList.remove('hidden');
    
    // Slight delay to allow CSS reveal to trigger if they intersect
    setTimeout(() => {
        observer.observe(topSec);
        observer.observe(searchSec);
    }, 100);
    
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
            // Smooth scroll up to the video player
            player.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            player.currentTime = start;
            
            // Wait 1 second for the scroll to finish before playing
            setTimeout(() => {
                const playPromise = player.play();
                
                if (playPromise !== undefined) {
                    playPromise.catch(error => {
                        console.warn("Playback interrupted or blocked. Trying muted...", error);
                        // Browsers sometimes block unmuted playback even on click. 
                        player.muted = true;
                        player.play().catch(e => console.error("Playback fully blocked:", e));
                    });
                }
            }, 1000);
            
            if (window.activePauseTimeout) {
                clearTimeout(window.activePauseTimeout);
            }
            
            const checkPause = () => {
                if (player.currentTime >= end + 1) {
                    player.pause();
                } else if (!player.paused) {
                    window.activePauseTimeout = setTimeout(checkPause, 100);
                }
            };
            window.activePauseTimeout = setTimeout(checkPause, 100);
        });
        
        listEl.appendChild(card);
    });
}

function formatTime(s) {
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
}
