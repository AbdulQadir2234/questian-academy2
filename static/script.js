const API_URL = '/api';
let currentUser = null;
try { const s = localStorage.getItem('currentUser'); if (s) currentUser = JSON.parse(s); } catch(e) { localStorage.removeItem('currentUser'); }

// Fallback Data
const FALLBACK_COURSES = [
    {id:1, title:'Mobile Application Development', description:'Android aur iOS apps banana seekhein.', image:'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=600'},
    {id:2, title:'Cyber Security', description:'Systems ko secure karna seekhein.', image:'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=600'},
    {id:3, title:'Graphics Designing', description:'Photoshop aur Illustrator seekhein.', image:'https://images.unsplash.com/photo-1626785774573-4b799315345d?w=600'},
    {id:4, title:'Penetration Testing', description:'Systems ki testing karna seekhein.', image:'https://images.unsplash.com/photo-1563206767-5b18f218e8de?w=600'},
    {id:5, title:'Ethical Hacking', description:'Legal hacking techniques.', image:'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600'},
    {id:6, title:'Python Language', description:'Python programming zero se hero tak.', image:'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=600'},
    {id:7, title:'AI and Machine Learning', description:'AI aur ML models banana seekhein.', image:'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600'},
    {id:8, title:'Deep Learning', description:'Neural networks aur deep learning.', image:'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=600'},
    {id:9, title:'C# Language', description:'C# programming language.', image:'https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=600'},
    {id:10, title:'C Language', description:'C programming ki bunyad.', image:'https://images.unsplash.com/photo-1587620962725-abab7fe55159?w=600'},
    {id:11, title:'C++ Language', description:'C++ aur OOP concepts.', image:'https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=600'},
    {id:12, title:'Object Oriented Programming in Java', description:'Java aur OOPs.', image:'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600'}
];

const FALLBACK_SOFTWARE = [
    {id:1, name:'VS Code', link:'https://code.visualstudio.com/download', image:'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600'},
    {id:2, name:'XAMPP', link:'https://www.apachefriends.org/download.html', image:'https://images.unsplash.com/photo-1518770660439-4636190af475?w=600'},
    {id:3, name:'Adobe Photoshop', link:'https://www.adobe.com/products/photoshop.html', image:'https://images.unsplash.com/photo-1626785774573-4b799315345d?w=600'},
    {id:4, name:'Python IDLE', link:'https://www.python.org/downloads/', image:'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=600'},
    {id:5, name:'Kali Linux', link:'https://www.kali.org/get-kali/', image:'https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=600'}
];

const VIDEO_LINKS = {
    'Mobile Application Development': 'https://youtu.be/u64gyCdqawU', 'Cyber Security': 'https://youtu.be/v3iUx2SNspY',
    'Graphics Designing': 'https://youtu.be/e_dv7GBHka8', 'Penetration Testing': 'https://www.youtube.com/live/LiDC2hLN6jg',
    'Ethical Hacking': 'https://youtu.be/u46mjbyzhvw', 'Python Language': 'https://youtu.be/ERCMXc8x7mc',
    'AI and Machine Learning': 'https://youtu.be/D1eL1EnxXXQ', 'Deep Learning': 'https://youtu.be/bZxAKA69xqg',
    'C# Language': 'https://youtu.be/SuLiu5AK9Ps', 'C Language': 'https://youtu.be/irqbmMNs2Bo',
    'C++ Language': 'https://youtu.be/mlIUKyZIUUU', 'Object Oriented Programming in Java': 'https://youtu.be/bSrm9RXwBaI'
};

function extractYouTubeID(url) {
    if (!url) return 'dQw4w9WgXcQ';
    var m = url.match(/youtube\.com\/live\/([^?&#\s]+)/); if (m) return m[1];
    m = url.match(/youtu\.be\/([^?&#\s]+)/); if (m) return m[1];
    m = url.match(/[?&]v=([^?&#\s]+)/); if (m) return m[1];
    if (/^[a-zA-Z0-9_-]{11}$/.test(url)) return url;
    return 'dQw4w9WgXcQ';
}

// VOICE
let femaleVoice = null, voiceEnabled = true;
function loadVoices() { if (!('speechSynthesis' in window)) return; var v = speechSynthesis.getVoices(); if (!v.length) return; femaleVoice = v.find(x => x.lang === 'hi-IN') || v.find(x => x.name.toLowerCase().includes('female')) || v[0]; }
if ('speechSynthesis' in window) { loadVoices(); speechSynthesis.onvoiceschanged = loadVoices; setTimeout(loadVoices, 500); }
function stopVoice() { if ('speechSynthesis' in window) speechSynthesis.cancel(); }
function speakUrdu(t) { if (!voiceEnabled || !('speechSynthesis' in window)) return; if (!femaleVoice) loadVoices(); speechSynthesis.cancel(); var u = new SpeechSynthesisUtterance(t); u.rate = 0.85; u.pitch = 1.3; if (femaleVoice) { u.voice = femaleVoice; u.lang = femaleVoice.lang; } else u.lang = 'hi-IN'; setTimeout(() => speechSynthesis.speak(u), 100); }
function toggleVoice() { voiceEnabled = !voiceEnabled; var b = document.getElementById('voice-toggle-btn'); if (!voiceEnabled) { stopVoice(); b.innerText = '🔇 OFF'; b.style.background = '#FEE2E2'; b.style.color = '#DC2626'; } else { b.innerText = '🔊 ON'; b.style.background = '#E0E7FF'; b.style.color = '#4F46E5'; speakUrdu("Voice on"); } }
function admissionVoiceGuide() { if (voiceEnabled) speakUrdu("Assalam o alaikum. Admission form bharein."); }
function admissionFieldGuide(f) { if (!voiceEnabled) return; if (f === 'name') speakUrdu("Apna naam likhein"); if (f === 'email') speakUrdu("Email likhein"); if (f === 'phone') speakUrdu("Phone number likhein"); if (f === 'course') speakUrdu("Course select karein"); }

// NAVIGATION
function showView(id) {
    stopVoice(); 
    var t = document.getElementById((id.includes('dashboard') ? id : id + '-view')); 
    if (!t) return;
    document.querySelectorAll('.container').forEach(el => { el.classList.remove('active'); });
    t.classList.add('active');
    if (id === 'courses') loadCourses(); 
    if (id === 'software') loadSoftware(); 
    if (id === 'news') loadNews();
    if (id === 'student-dashboard') loadStudentDash(); 
    if (id === 'teacher-dashboard') loadTeacherDash();
    if (id === 'home') setTimeout(animateStats, 300);
    window.scrollTo(0, 0);
}

function animateStats() { document.querySelectorAll('.stat-number').forEach(s => { var t = parseInt(s.getAttribute('data-target')), c = 0, st = Math.ceil(t/40); var tm = setInterval(() => { c += st; if (c >= t) { c = t; clearInterval(tm); } s.innerText = c + (t === 24 || t === 5 ? '' : '+'); }, 40); }); }

// FILTERS
var currentFilter = 'all', allCourses = [];
var CATEGORIES = { 'Mobile Application Development':'mobile','Cyber Security':'security','Graphics Designing':'design','Penetration Testing':'security','Ethical Hacking':'security','Python Language':'programming','AI and Machine Learning':'ai','Deep Learning':'ai','C# Language':'programming','C Language':'programming','C++ Language':'programming','Object Oriented Programming in Java':'programming' };
function filterCourses(c, btn) { currentFilter = c; document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active')); if (btn) btn.classList.add('active'); renderFilteredCourses(); }

async function loadCourses() {
    var list = document.getElementById('courses-list'); list.innerHTML = '';
    try {
        const r = await fetch(API_URL + '/courses'); const c = await r.json();
        if (!c || c.length === 0) throw new Error('Empty');
        allCourses = c; renderFilteredCourses();
    } catch(e) { allCourses = FALLBACK_COURSES; renderFilteredCourses(); }
}

function renderFilteredCourses() {
    var list = document.getElementById('courses-list'); list.innerHTML = '';
    var filtered = allCourses.filter(x => currentFilter === 'all' || CATEGORIES[x.title] === currentFilter);
    if (filtered.length === 0) { list.innerHTML = '<p style="color:#6B7280;text-align:center;padding:30px;">Is category mein koi course nahi.</p>'; return; }
    filtered.forEach(x => {
        var img = x.image || 'https://via.placeholder.com/400x200?text=Course';
        var card = document.createElement('div'); card.className = 'card course-card';
        card.innerHTML = `<img src="${img}" class="course-image" onerror="this.src='https://via.placeholder.com/400x200'"><div class="course-content"><h3>${x.title}</h3><p class="course-desc">${x.description}</p><button class="btn-primary" style="width:100%;margin-top:15px;" onclick="openCourse('${x.id}', '${x.title}')">🚀 Start Learning</button></div>`;
        list.appendChild(card);
    });
}

async function loadSoftware() {
    var list = document.getElementById('software-list'); list.innerHTML = '';
    try {
        const r = await fetch(API_URL + '/software'); const c = await r.json();
        if (!c || c.length === 0) throw new Error('Empty');
        renderSoftware(c);
    } catch(e) { renderSoftware(FALLBACK_SOFTWARE); }
}

function renderSoftware(c) {
    var list = document.getElementById('software-list'); list.innerHTML = '';
    c.forEach(x => {
        var img = x.image || 'https://via.placeholder.com/400x200?text=Software';
        var card = document.createElement('div'); card.className = 'card course-card';
        card.innerHTML = `<img src="${img}" class="course-image" onerror="this.src='https://via.placeholder.com/400x200'"><div class="course-content"><h3>${x.name}</h3><button class="btn-success" style="width:100%;margin-top:15px;" onclick="window.open('${x.link}', '_blank')">⬇️ Download Now</button></div>`;
        list.appendChild(card);
    });
}

async function loadNews() {
    var list = document.getElementById('news-list'); list.innerHTML = '';
    try {
        const r = await fetch(API_URL + '/news'); const c = await r.json();
        if (!c || c.length === 0) throw new Error('Empty');
        c.forEach(x => list.innerHTML += `<div class="news-item" style="background:#F9FAFB;padding:15px;border-left:4px solid #4F46E5;border-radius:0 8px 8px 0;margin-bottom:10px;">📢 ${x.text}</div>`);
    } catch(e) { list.innerHTML = `<div class="news-item" style="background:#F9FAFB;padding:15px;border-left:4px solid #4F46E5;border-radius:0 8px 8px 0;">📢 Welcome to Questian Academy!</div>`; }
}

function openCourse(id, title) {
    document.getElementById('courses-list').classList.add('hidden'); document.getElementById('course-detail').classList.remove('hidden'); document.getElementById('detail-title').innerText = title;
    var vId = extractYouTubeID(VIDEO_LINKS[title] || ''), vBox = document.querySelector('.video-placeholder');
    vBox.innerHTML = `<iframe width="100%" height="100%" src="https://www.youtube.com/embed/${vId}?rel=0" frameborder="0" allowfullscreen style="border-radius:12px;"></iframe>`;
}
function hideCourseDetail() { document.getElementById('courses-list').classList.remove('hidden'); document.getElementById('course-detail').classList.add('hidden'); }
function downloadNotes() { alert('Notes download started'); } 
function startTest() { document.getElementById('test-area').classList.remove('hidden'); } 
function submitTest() { const s = document.querySelector('input[name="q1"]:checked'); alert(s && s.value === 'a' ? 'Correct!' : 'Wrong'); }

// AUTH
async function handleLogin(e) {
    e.preventDefault(); const u = document.getElementById('login-user').value.trim(), p = document.getElementById('login-pass').value.trim();
    try {
        const r = await fetch(API_URL + '/login/send-otp', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({username: u, password: p}) });
        const d = await r.json(); if (!d.success) return alert('❌ ' + d.message);
        window.pendingLoginEmail = d.email; alert('✅ ' + d.message); showOtpScreen('login');
    } catch(err) { alert('Server error!'); }
}
async function handleSignup(e) {
    e.preventDefault(); const n = document.getElementById('signup-name').value.trim(), u = document.getElementById('signup-user').value.trim(), em = document.getElementById('signup-email').value.trim().toLowerCase(), p = document.getElementById('signup-pass').value.trim(), ro = document.getElementById('signup-role').value;
    try {
        const r = await fetch(API_URL + '/signup/send-otp', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name: n, username: u, email: em, password: p, role: ro}) });
        const d = await r.json(); if (!d.success) return alert('❌ ' + d.message);
        window.pendingSignup = {email: em}; alert('✅ ' + d.message); showOtpScreen('signup');
    } catch(err) { alert('Server error!'); }
}

function showOtpScreen(type) {
    document.querySelectorAll('.container').forEach(el => el.classList.remove('active'));
    let o = document.getElementById('otp-view'); if (!o) { o = document.createElement('div'); o.id = 'otp-view'; o.className = 'container active'; document.body.insertBefore(o, document.querySelector('.main-footer')); }
    o.innerHTML = `<div style="max-width:400px;margin:40px auto;text-align:center;"><h2>Verify Email</h2><p style="color:#6B7280;margin-bottom:20px;">6-digit code daalein</p><input type="text" id="otp-input" maxlength="6" style="text-align:center;font-size:1.5rem;letter-spacing:8px;"><button onclick="verifyOtp('${type}')" class="btn-primary full-width">Verify Code</button><p style="margin-top:15px;color:#6B7280;cursor:pointer;" onclick="showView('login')">Cancel</p></div>`;
}
async function verifyOtp(type) {
    const code = document.getElementById('otp-input').value.trim(), url = type === 'signup' ? '/signup/verify' : '/login/verify', email = type === 'signup' ? window.pendingSignup.email : window.pendingLoginEmail;
    try {
        const r = await fetch(API_URL + url, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({email, code}) }); const d = await r.json();
        if (!d.success) return alert('❌ ' + d.message);
        currentUser = d.user; localStorage.setItem('currentUser', JSON.stringify(currentUser)); updateNav(); showView(currentUser.role + '-dashboard'); alert('✅ Welcome ' + currentUser.name);
    } catch(err) { alert('Error'); }
}

function toggleAuthForm() { const lf = document.getElementById('login-form'), sf = document.getElementById('signup-form'), t = document.getElementById('auth-title'), sw = document.getElementById('auth-switch'); if (lf.classList.contains('hidden')) { lf.classList.remove('hidden'); sf.classList.add('hidden'); t.innerText = 'Login Portal'; sw.innerHTML = 'Don\'t have an account? <span onclick="toggleAuthForm()" style="color:#4F46E5;font-weight:600;cursor:pointer;text-decoration:underline;">Sign Up</span>'; } else { lf.classList.add('hidden'); sf.classList.remove('hidden'); t.innerText = 'Create Account'; sw.innerHTML = 'Already have an account? <span onclick="toggleAuthForm()" style="color:#4F46E5;font-weight:600;cursor:pointer;text-decoration:underline;">Login</span>'; } }
function showForgotPassword() { showView('forgot'); }
async function handleForgotPassword(e) { e.preventDefault(); const em = document.getElementById('forgot-email').value.trim(); try { const r = await fetch(API_URL + '/forgot-password', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({email: em}) }); const d = await r.json(); alert(d.success ? '✅ ' + d.message : '❌ ' + d.message); if(d.success) showView('login'); } catch(e){ alert('Error'); } }
async function handleResetPassword(e) { e.preventDefault(); const p = document.getElementById('reset-password').value, c = document.getElementById('reset-confirm').value; if(p !== c) return alert('Passwords match nahi kar rahe!'); const token = new URLSearchParams(window.location.search).get('token'); try { const r = await fetch(API_URL + '/reset-password', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({token, password: p}) }); const d = await r.json(); alert(d.success ? '✅ ' + d.message : '❌ ' + d.message); if(d.success) showView('login'); } catch(e){ alert('Error'); } }
function logout() { currentUser = null; localStorage.removeItem('currentUser'); updateNav(); showView('home'); }

function updateNav() { var l = document.getElementById('login-btn'), p = document.getElementById('profile-btn'); if (currentUser) { l.classList.add('hidden'); p.classList.remove('hidden'); document.getElementById('profile-initial').innerText = currentUser.name.charAt(0).toUpperCase(); document.getElementById('profile-avatar').innerText = currentUser.name.charAt(0).toUpperCase(); document.getElementById('profile-name').innerText = currentUser.name; document.getElementById('profile-role').innerText = currentUser.role; } else { l.classList.remove('hidden'); p.classList.add('hidden'); } }
function toggleProfileMenu(e) { if (e) e.stopPropagation(); document.getElementById('profile-dropdown').classList.toggle('hidden'); }
document.addEventListener('click', function(e) { var m = document.getElementById('profile-dropdown'), b = document.getElementById('profile-btn'); if (!m || !b) return; if (!m.contains(e.target) && !b.contains(e.target)) m.classList.add('hidden'); });
function openDashboard() { document.getElementById('profile-dropdown').classList.add('hidden'); if (currentUser) showView(currentUser.role + '-dashboard'); }
function openSettings() { document.getElementById('profile-dropdown').classList.add('hidden'); alert('Settings coming soon!'); }
function openCertificate() { document.getElementById('profile-dropdown').classList.add('hidden'); alert('Certificate coming soon!'); }

// DASHBOARD
function loadStudentDash() { if (!currentUser) return; document.getElementById('stu-name').innerText = currentUser.name; loadChats('student-chat-box'); loadProgress(); }
function loadTeacherDash() { if (!currentUser) return; document.getElementById('teacher-name').innerText = currentUser.name; loadChats('teacher-chat-box'); loadManage(); setTimeout(loadSecurityPanel, 500); }
async function loadProgress() { try { const r = await fetch(API_URL + '/progress/' + currentUser.username); const p = await r.json(); const b = document.getElementById('progress-list'); b.innerHTML = p.length === 0 ? '<p>Koi progress nahi.</p>' : ''; p.forEach(x => b.innerHTML += `<div style="margin-bottom:10px;"><div style="font-weight:600;">${x.course_title}</div><div style="background:#E5E7EB;height:8px;border-radius:4px;margin-top:5px;"><div style="background:linear-gradient(90deg,#4F46E5,#7C3AED);width:${x.progress_percent}%;height:100%;border-radius:4px;"></div></div><div style="font-size:0.8rem;color:#6B7280;margin-top:3px;">${x.progress_percent}% complete</div></div>`); } catch(e){} }
async function markAttendance() { try { const r = await fetch(API_URL + '/attendance', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({student_name: currentUser.name}) }); const d = await r.json(); document.getElementById('attendance-status').innerText = d.message; document.getElementById('attendance-status').style.color = d.success ? '#10B981' : '#EF4444'; } catch(e){} }
async function loadChats(box) { try { const r = await fetch(API_URL + '/chats'); const c = await r.json(); const b = document.getElementById(box); b.innerHTML = ''; c.forEach(x => { const cls = x.sender === 'teacher' ? 'teacher' : ''; b.innerHTML += `<div class="chat-msg ${cls}"><b>${x.sender === 'teacher' ? 'Teacher' : 'Student'}:</b> ${x.message}</div>`; }); b.scrollTop = b.scrollHeight; } catch(e){} }
async function sendChat(role) { const i = role === 'student' ? 'student-msg' : 'teacher-msg', m = document.getElementById(i).value.trim(); if(!m) return; await fetch(API_URL + '/chats', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({sender: role, message: m}) }); document.getElementById(i).value = ''; loadChats(role === 'student' ? 'student-chat-box' : 'teacher-chat-box'); }
async function loadManage() { try { const c = await fetch(API_URL + '/courses').then(r=>r.json()); const m = document.getElementById('manage-content'); m.innerHTML = '<h4 style="color:#4F46E5;">📚 Courses</h4>'; c.forEach(x => m.innerHTML += `<div style="padding:6px;background:#f9fafb;border-radius:6px;margin-bottom:6px;font-size:0.85rem;">${x.title} <button class="btn-danger" style="padding:3px 8px;font-size:0.7rem;margin-top:4px;" onclick="del('courses',${x.id})">🗑️ Delete</button></div>`); } catch(e){} }
async function del(t, i) { if(!confirm('Delete?')) return; await fetch(API_URL + '/' + t + '/' + i, { method: 'DELETE' }); loadManage(); }
async function addNews() { const text = document.getElementById('new-news').value.trim(); if (!text) return alert('Text daalein'); await fetch(API_URL + '/news', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({text})}); document.getElementById('new-news').value = ''; loadManage(); }
async function addSoftware() { const name = document.getElementById('new-soft-name').value.trim(), link = document.getElementById('new-soft-link').value.trim(), image = document.getElementById('new-soft-image').value.trim(); if (!name) return alert('Name daalein'); await fetch(API_URL + '/software', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name, link, image})}); document.getElementById('new-soft-name').value = ''; document.getElementById('new-soft-link').value = ''; document.getElementById('new-soft-image').value = ''; loadManage(); }
async function addCourse() { const title = document.getElementById('new-course-title').value.trim(), image = document.getElementById('new-course-image').value.trim(); if (!title) return alert('Title daalein'); await fetch(API_URL + '/courses', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({title, image})}); document.getElementById('new-course-title').value = ''; document.getElementById('new-course-image').value = ''; loadManage(); }
async function loadSecurityPanel() { try { const stats = await fetch(API_URL + '/security/stats').then(r => r.json()); var el; el = document.getElementById('stat-attacks'); if (el) el.innerText = stats.total_attacks || 0; el = document.getElementById('stat-blocked'); if (el) el.innerText = stats.blocked_ips || 0; el = document.getElementById('stat-today'); if (el) el.innerText = stats.attacks_today || 0; el = document.getElementById('stat-logins'); if (el) el.innerText = stats.failed_logins_today || 0; } catch(err) { console.error(err); } }

// AI CHAT
function toggleAI() { document.getElementById('ai-chat-container').classList.toggle('hidden'); }
function handleAIKeyPress(e) { if (e.key === 'Enter') sendAIMessage(); }
async function sendAIMessage() {
    const input = document.getElementById('ai-input'), msg = input.value.trim(); if (!msg) return;
    const box = document.getElementById('ai-messages');
    box.innerHTML += `<div class="ai-msg user">${msg}</div>`; input.value = ''; box.scrollTop = box.scrollHeight;
    try {
        const r = await fetch(API_URL + '/ai/smart', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({message: msg}) });
        const d = await r.json();
        box.innerHTML += `<div class="ai-msg bot">${d.response || 'Maazrat!'}</div>`;
    } catch(e) { box.innerHTML += `<div class="ai-msg bot">Error connecting.</div>`; }
    box.scrollTop = box.scrollHeight;
}

async function submitContact(e) { e.preventDefault(); var name = document.getElementById('contact-name').value.trim(), email = document.getElementById('contact-email').value.trim(), subject = document.getElementById('contact-subject').value.trim(), message = document.getElementById('contact-message').value.trim(); if (!name || !email || !subject || !message) return alert('Saare fields bharein'); try { var r = await fetch(API_URL + '/contact', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name, email, subject, message}) }); var d = await r.json(); alert(d.success ? 'Message bhej diya' : 'Error'); if (d.success) e.target.reset(); } catch(err) { alert('Error'); } }
async function submitAdmission(e) { e.preventDefault(); const name = document.getElementById('adm-name').value.trim(), email = document.getElementById('adm-email').value.trim(), phone = document.getElementById('adm-phone').value.trim(), course = document.getElementById('adm-course').value; try { await fetch(API_URL + '/admission', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name, email, phone, course}) }); alert('✅ Admission submit ho gaya!'); e.target.reset(); showView('home'); } catch(err) { alert('Error!'); } }
function openPolicy(p) { alert(p + ':\n\nJald available'); }

window.addEventListener('load', () => { loadVoices(); updateNav(); const token = new URLSearchParams(window.location.search).get('token'); if (token) { fetch(API_URL + '/verify-reset-token', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({token}) }).then(r => r.json()).then(d => { if (d.success) showView('reset'); else { alert('Link galat ya expire'); showView('login'); } }).catch(() => showView('login')); return; } if (currentUser) showView(currentUser.role + '-dashboard'); else showView('home'); });