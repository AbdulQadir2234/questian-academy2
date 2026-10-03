// ============================================
//   QUESTIAN ACADEMY - script.js
//   Developer: Abdul Qadir Soomro
// ============================================

const API_URL = '';
let currentUser = null;
try { const s = localStorage.getItem('currentUser'); if (s) currentUser = JSON.parse(s); } catch(e) { localStorage.removeItem('currentUser'); }

// ============================================
//   DEVELOPER INFO
// ============================================
var DEVELOPER_INFO = {
    name: 'Abdul Qadir Soomro',
    role: 'Full Stack Web Developer • Penetration Tester • AI & ML Engineer',
    email: '24cse23@quest.edu.pk',
    phone: '03359996428',
    location: 'Larkana, Pakistan',
    bio: 'Full Stack Developer, Penetration Tester aur AI & Machine Learning Engineer.'
};

// ============================================
//   YOUTUBE VIDEO LINKS
// ============================================
const VIDEO_LINKS = {
    'Mobile Application Development': 'https://youtu.be/u64gyCdqawU',
    'Cyber Security': 'https://youtu.be/v3iUx2SNspY',
    'Graphics Designing': 'https://youtu.be/e_dv7GBHka8',
    'Penetration Testing': 'https://www.youtube.com/live/LiDC2hLN6jg',
    'Ethical Hacking': 'https://youtu.be/u46mjbyzhvw',
    'Python Language': 'https://youtu.be/ERCMXc8x7mc',
    'AI and Machine Learning': 'https://youtu.be/D1eL1EnxXXQ',
    'Deep Learning': 'https://youtu.be/bZxAKA69xqg',
    'C# Language': 'https://youtu.be/SuLiu5AK9Ps',
    'C Language': 'https://youtu.be/irqbmMNs2Bo',
    'C++ Language': 'https://youtu.be/mlIUKyZIUUU',
    'Object Oriented Programming in Java': 'https://youtu.be/bSrm9RXwBaI'
};

function extractYouTubeID(url) {
    if (!url) return 'dQw4w9WgXcQ';
    var liveMatch = url.match(/youtube\.com\/live\/([^?&#\s]+)/);
    if (liveMatch) return liveMatch[1];
    var shortMatch = url.match(/youtu\.be\/([^?&#\s]+)/);
    if (shortMatch) return shortMatch[1];
    var watchMatch = url.match(/[?&]v=([^?&#\s]+)/);
    if (watchMatch) return watchMatch[1];
    var embedMatch = url.match(/youtube\.com\/embed\/([^?&#\s]+)/);
    if (embedMatch) return embedMatch[1];
    if (/^[a-zA-Z0-9_-]{11}$/.test(url)) return url;
    return 'dQw4w9WgXcQ';
}

// ============================================
//   VOICE SYSTEM
// ============================================
let femaleVoice = null;
let voiceEnabled = true;
let voicesLoaded = false;

function loadVoices() {
    if (!('speechSynthesis' in window)) return;
    var voices = speechSynthesis.getVoices();
    if (voices.length === 0) return;
    voicesLoaded = true;
    femaleVoice = 
        voices.find(v => v.lang === 'hi-IN' && v.name.toLowerCase().includes('female')) ||
        voices.find(v => v.lang === 'hi-IN') ||
        voices.find(v => v.lang.startsWith('hi')) ||
        voices.find(v => v.name.toLowerCase().includes('female')) ||
        voices.find(v => v.lang === 'en-IN') ||
        voices[0];
}
if ('speechSynthesis' in window) {
    loadVoices();
    speechSynthesis.onvoiceschanged = loadVoices;
    setTimeout(loadVoices, 200);
    setTimeout(loadVoices, 1000);
}

function stopVoice() { if ('speechSynthesis' in window) speechSynthesis.cancel(); }

function speakUrdu(text) {
    if (!voiceEnabled) return;
    if (!('speechSynthesis' in window)) return;
    if (!femaleVoice) loadVoices();
    speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(text);
    u.rate = 0.8; u.pitch = 1.4; u.volume = 1;
    if (femaleVoice) { u.voice = femaleVoice; u.lang = femaleVoice.lang; }
    else u.lang = 'hi-IN';
    setTimeout(function() { speechSynthesis.speak(u); }, 100);
}

function toggleVoice() {
    voiceEnabled = !voiceEnabled;
    var btn = document.getElementById('voice-toggle-btn');
    if (!voiceEnabled) { stopVoice(); if (btn) { btn.innerText = '🔇 OFF'; btn.style.background = '#FEE2E2'; btn.style.color = '#DC2626'; } }
    else { if (btn) { btn.innerText = '🔊 ON'; btn.style.background = '#E0E7FF'; btn.style.color = '#4F46E5'; } speakUrdu("Voice on ho gayi hai"); }
}

function admissionVoiceGuide() {
    if (!voiceEnabled) { alert('Voice OFF hai!'); return; }
    speakUrdu("Assalam o alaikum. Main aapki admission form bharne mein madad karungi. Pehle apna poora naam likhein. Phir email. Uske baad phone number. Aakhir mein course select karein. Aur submit dabayein.");
}

function admissionFieldGuide(field) {
    if (!voiceEnabled) return;
    if (field === 'name') speakUrdu("Yahan apna poora naam likhein");
    if (field === 'email') speakUrdu("Yahan apna email address likhein");
    if (field === 'phone') speakUrdu("Yahan apna phone number likhein");
    if (field === 'course') speakUrdu("Yahan se apna course select karein");
}

// ============================================
//   STATS ANIMATION
// ============================================
function animateStats() {
    var stats = document.querySelectorAll('.stat-number');
    stats.forEach(function(stat) {
        var target = parseInt(stat.getAttribute('data-target'));
        var current = 0;
        var step = Math.ceil(target / 40);
        var timer = setInterval(function() {
            current += step;
            if (current >= target) { current = target; clearInterval(timer); }
            stat.innerText = current + (target === 24 || target === 5 ? '' : '+');
        }, 40);
    });
}

// ============================================
//   COURSE FILTERS
// ============================================
var currentFilter = 'all';
var allCourses = [];

var COURSE_CATEGORIES = {
    'Mobile Application Development': 'mobile',
    'Cyber Security': 'security',
    'Graphics Designing': 'design',
    'Penetration Testing': 'security',
    'Ethical Hacking': 'security',
    'Python Language': 'programming',
    'AI and Machine Learning': 'ai',
    'Deep Learning': 'ai',
    'C# Language': 'programming',
    'C Language': 'programming',
    'C++ Language': 'programming',
    'Object Oriented Programming in Java': 'programming'
};

function filterCourses(category, btn) {
    currentFilter = category;
    document.querySelectorAll('.filter-btn').forEach(function(b) { b.classList.remove('active'); });
    if (btn) btn.classList.add('active');
    renderFilteredCourses();
}

function renderFilteredCourses() {
    var list = document.getElementById('courses-list');
    if (!list) return;
    list.innerHTML = '';
    var filtered = allCourses.filter(function(c) {
        if (currentFilter === 'all') return true;
        return COURSE_CATEGORIES[c.title] === currentFilter;
    });
    if (filtered.length === 0) {
        list.innerHTML = '<p style="color:#6B7280;text-align:center;padding:30px;">Is category mein koi course nahi.</p>';
        return;
    }
    filtered.forEach(function(x) {
        var img = x.image || 'https://via.placeholder.com/400x200?text=Course';
        var card = document.createElement('div');
        card.className = 'card course-card';
        card.innerHTML = '<img src="' + img + '" class="course-image" onerror="this.src=\'https://via.placeholder.com/400x200\'">' +
            '<div class="course-content"><h3>' + x.title + '</h3>' +
            '<p class="course-desc">' + (x.description || '') + '</p>' +
            '<button class="btn-primary" style="width:100%;margin-top:15px;">🚀 Start Learning</button></div>';
        card.querySelector('button').onclick = function() { openCourse(x.id, x.title); };
        list.appendChild(card);
    });
}

// ============================================
//   NAVIGATION
// ============================================
function showView(id) {
    stopVoice();
    var target = document.getElementById((id.includes('dashboard') ? id : id + '-view'));
    if (!target) { console.error('View not found:', id); return; }
    document.querySelectorAll('.container').forEach(function(el) {
        el.classList.remove('active');
        el.style.display = 'none';
    });
    target.classList.add('active');
    target.style.display = 'block';
    if (id === 'courses') loadCourses();
    if (id === 'software') loadSoftware();
    if (id === 'news') loadNews();
    if (id === 'about') loadAbout();
    if (id === 'student-dashboard') loadStudentDash();
    if (id === 'teacher-dashboard') loadTeacherDash();
    if (id === 'home') setTimeout(animateStats, 300);
    if (id === 'admission') {
        setTimeout(function() { if (voiceEnabled) speakUrdu("Admission form khul gaya"); }, 500);
    }
}

// ============================================
//   ABOUT
// ============================================
function loadAbout() {
    var d = DEVELOPER_INFO;
    var el;
    el = document.getElementById('dev-name'); if (el) el.innerText = d.name;
    el = document.getElementById('dev-email'); if (el) { el.innerText = d.email; el.href = 'mailto:' + d.email; }
    el = document.getElementById('dev-phone'); if (el) { el.innerText = d.phone; el.href = 'tel:' + d.phone; }
    el = document.getElementById('dev-location'); if (el) el.innerText = d.location;
    el = document.getElementById('dev-bio'); if (el) el.innerText = d.bio;
    el = document.querySelector('.dev-role'); if (el) el.innerText = d.role;
    el = document.getElementById('dev-avatar'); if (el) el.innerText = d.name.charAt(0).toUpperCase();
}

async function submitContact(e) {
    e.preventDefault();
    var name = document.getElementById('contact-name').value.trim();
    var email = document.getElementById('contact-email').value.trim();
    var subject = document.getElementById('contact-subject').value.trim();
    var message = document.getElementById('contact-message').value.trim();
    if (!name || !email || !subject || !message) return alert('Sab fields bharein!');
    try {
        var r = await fetch(API_URL + '/contact', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name: name, email: email, subject: subject, message: message})
        });
        var d = await r.json();
        alert('✅ ' + (d.message || 'Message send ho gaya!'));
        e.target.reset();
    } catch(err) { alert('❌ Message send nahi hua.'); }
}

function openPolicy(policy) {
    var messages = {
        'Disclaimer': 'Yeh website educational purposes ke liye hai. Sab courses aur content informational hain.',
        'Privacy Policy': 'Aapki privacy hamare liye ahem hai. Hum aapka data kisi teesri party se share nahi karte.',
        'Terms of Service': 'Website use karne ke liye aap in terms se agree karte hain:\n1. Koi illegal activity nahi\n2. Content copy nahi karein',
        'Sitemap': 'Pages: Home, Admission, Courses, Software, News, About, Login'
    };
    alert('📄 ' + policy + ':\n\n' + (messages[policy] || 'Jald available!'));
}

// ============================================
//   PROFILE MENU
// ============================================
function toggleProfileMenu(e) {
    if (e) e.stopPropagation();
    var menu = document.getElementById('profile-dropdown');
    if (menu) menu.classList.toggle('hidden');
}
document.addEventListener('click', function(e) {
    var menu = document.getElementById('profile-dropdown');
    var btn = document.getElementById('profile-btn');
    if (!menu || !btn) return;
    if (!menu.contains(e.target) && !btn.contains(e.target)) menu.classList.add('hidden');
});
function openDashboard() { document.getElementById('profile-dropdown').classList.add('hidden'); if (currentUser) showView(currentUser.role + '-dashboard'); }
function openSettings() { document.getElementById('profile-dropdown').classList.add('hidden'); alert('⚙️ Settings page abhi kaam kar raha hai.'); }
function openPayment() { document.getElementById('profile-dropdown').classList.add('hidden'); alert('💳 Payment system abhi kaam kar raha hai.'); }
function openCertificate() { document.getElementById('profile-dropdown').classList.add('hidden'); alert('🎓 Certificate system abhi kaam kar raha hai.'); }

// ============================================
//   LOGIN / SIGNUP
// ============================================
async function handleLogin(e) {
    e.preventDefault();
    stopVoice();
    const u = document.getElementById('login-user').value.trim();
    const p = document.getElementById('login-pass').value.trim();
    if (!u || !p) return alert('Username aur password daalein!');
    try {
        const r = await fetch(API_URL + '/login', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: u, password: p})
        });
        const d = await r.json();
        if (d.success) {
            currentUser = d.user;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            updateNav();
            document.getElementById('login-form').reset();
            document.getElementById('signup-form').reset();
            showView(currentUser.role + '-dashboard');
        } else { alert('❌ ' + (d.message || 'Galat credentials!')); }
    } catch(err) { alert('Server error!'); }
}

async function handleSignup(e) {
    e.preventDefault();
    const name = document.getElementById('signup-name').value.trim();
    const username = document.getElementById('signup-user').value.trim();
    const password = document.getElementById('signup-pass').value.trim();
    const role = document.getElementById('signup-role').value;
    if (!name || !username || !password) return alert('Sab fields bharein!');
    try {
        const r = await fetch(API_URL + '/signup', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, username, password, role})
        });
        const d = await r.json();
        alert(d.success ? '✅ ' + d.message : '❌ ' + d.message);
        if (d.success) { document.getElementById('signup-form').reset(); toggleAuthForm(); }
    } catch(err) { alert('Server error!'); }
}

function toggleAuthForm() {
    const lf = document.getElementById('login-form');
    const sf = document.getElementById('signup-form');
    const title = document.getElementById('auth-title');
    const sw = document.getElementById('auth-switch');
    if (lf.classList.contains('hidden')) {
        lf.classList.remove('hidden'); sf.classList.add('hidden');
        if (title) title.innerText = 'Login Portal';
        if (sw) sw.innerHTML = 'Don\'t have an account? <span onclick="toggleAuthForm()" style="color:#4F46E5;font-weight:600;cursor:pointer;text-decoration:underline;">Sign Up</span>';
    } else {
        lf.classList.add('hidden'); sf.classList.remove('hidden');
        if (title) title.innerText = 'Create Account';
        if (sw) sw.innerHTML = 'Already have an account? <span onclick="toggleAuthForm()" style="color:#4F46E5;font-weight:600;cursor:pointer;text-decoration:underline;">Login</span>';
    }
}

function logout() {
    stopVoice();
    currentUser = null;
    localStorage.removeItem('currentUser');
    var menu = document.getElementById('profile-dropdown');
    if (menu) menu.classList.add('hidden');
    var pbtn = document.getElementById('profile-btn');
    if (pbtn) pbtn.classList.add('hidden');
    updateNav();
    showView('home');
}

function updateNav() {
    var l = document.getElementById('login-btn');
    var profileBtn = document.getElementById('profile-btn');
    if (currentUser) {
        if (l) l.classList.add('hidden');
        if (profileBtn) {
            profileBtn.classList.remove('hidden');
            var initial = (currentUser.name || 'U').charAt(0).toUpperCase();
            document.getElementById('profile-initial').innerText = initial;
            document.getElementById('profile-avatar').innerText = initial;
            document.getElementById('profile-name').innerText = currentUser.name;
            document.getElementById('profile-role').innerText = currentUser.role;
        }
    } else {
        if (l) l.classList.remove('hidden');
        if (profileBtn) profileBtn.classList.add('hidden');
        var menu = document.getElementById('profile-dropdown');
        if (menu) menu.classList.add('hidden');
    }
}

// ============================================
//   ADMISSION
// ============================================
async function submitAdmission(e) {
    e.preventDefault();
    const name = document.getElementById('adm-name').value.trim();
    const email = document.getElementById('adm-email').value.trim();
    const phone = document.getElementById('adm-phone').value.trim();
    const course = document.getElementById('adm-course').value;
    try {
        await fetch(API_URL + '/admission', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, email, phone, course})
        });
        alert('✅ Admission submit ho gaya!');
        if (voiceEnabled) speakUrdu("Mubarak ho! Admission submit ho gaya");
        e.target.reset();
        showView('home');
    } catch(err) { alert('Error!'); }
}

// ============================================
//   COURSES
// ============================================
async function loadCourses() {
    try {
        const r = await fetch(API_URL + '/courses');
        const c = await r.json();
        allCourses = c;
        renderFilteredCourses();
    } catch(err) { console.error(err); }
}

function openCourse(id, title) {
    document.getElementById('courses-list').classList.add('hidden');
    document.getElementById('course-detail').classList.remove('hidden');
    document.getElementById('detail-title').innerText = title;
    document.getElementById('test-area').classList.add('hidden');
    var videoUrl = VIDEO_LINKS[title] || 'https://youtu.be/dQw4w9WgXcQ';
    var videoId = extractYouTubeID(videoUrl);
    var videoBox = document.querySelector('.video-placeholder');
    if (videoBox) {
        videoBox.innerHTML = '<iframe width="100%" height="100%" src="https://www.youtube.com/embed/' + videoId + '?rel=0" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="border-radius:12px;"></iframe>';
        videoBox.style.padding = '0';
        videoBox.style.background = '#000';
        videoBox.style.overflow = 'hidden';
    }
    if (currentUser && currentUser.role === 'student') updateProgress(id, title, 25);
}

async function updateProgress(courseId, courseTitle, percent) {
    if (!currentUser) return;
    try {
        await fetch(API_URL + '/progress', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: currentUser.username, course_id: courseId, course_title: courseTitle, progress_percent: percent})
        });
    } catch(err) { console.error(err); }
}

function hideCourseDetail() {
    document.getElementById('courses-list').classList.remove('hidden');
    document.getElementById('course-detail').classList.add('hidden');
    var videoBox = document.querySelector('.video-placeholder');
    if (videoBox) {
        videoBox.innerHTML = '<span>▶ Video Player</span>';
        videoBox.style.padding = '';
        videoBox.style.background = '#1F2937';
    }
}

function downloadNotes() { alert('📥 Notes download started!'); }
function startTest() { document.getElementById('test-area').classList.remove('hidden'); }
function submitTest() {
    const s = document.querySelector('input[name="q1"]:checked');
    alert(s && s.value === 'a' ? '✅ Correct!' : '❌ Wrong');
}

// ============================================
//   SOFTWARE
// ============================================
async function loadSoftware() {
    try {
        const r = await fetch(API_URL + '/software');
        const c = await r.json();
        const list = document.getElementById('software-list');
        if (!list) return;
        list.innerHTML = '';
        c.forEach(function(x) {
            const img = x.image || 'https://via.placeholder.com/400x200?text=Software';
            const card = document.createElement('div');
            card.className = 'card course-card';
            card.innerHTML = '<img src="' + img + '" class="course-image" onerror="this.src=\'https://via.placeholder.com/400x200\'">' +
                '<div class="course-content"><h3>' + x.name + '</h3>' +
                '<button class="btn-success" style="width:100%;margin-top:15px;">⬇️ Download</button></div>';
            card.querySelector('button').onclick = function() {
                if (x.link && x.link !== '#') window.open(x.link, '_blank');
            };
            list.appendChild(card);
        });
    } catch(err) { console.error(err); }
}

// ============================================
//   NEWS
// ============================================
async function loadNews() {
    try {
        const r = await fetch(API_URL + '/news');
        const c = await r.json();
        const list = document.getElementById('news-list');
        if (!list) return;
        list.innerHTML = '';
        c.forEach(function(x) { list.innerHTML += '<div class="news-item">📢 ' + x.text + '</div>'; });
    } catch(err) { console.error(err); }
}

// ============================================
//   STUDENT DASHBOARD
// ============================================
function loadStudentDash() {
    if (!currentUser) return;
    var nameEl = document.getElementById('stu-name');
    if (nameEl) nameEl.innerText = currentUser.name;
    loadChats('student-chat-box');
    loadProgress();
}

async function loadProgress() {
    if (!currentUser) return;
    try {
        const r = await fetch(API_URL + '/progress/' + currentUser.username);
        const progress = await r.json();
        const box = document.getElementById('progress-list');
        if (!box) return;
        box.innerHTML = '';
        if (progress.length === 0) {
            box.innerHTML = '<p style="color:#6B7280;">Abhi tak koi course shuru nahi kiya. Courses tab kholein!</p>';
            return;
        }
        progress.forEach(function(p) {
            box.innerHTML += '<div style="margin-bottom:10px; padding:10px; background:#F9FAFB; border-radius:6px;">' +
                '<div style="font-weight:600;">' + p.course_title + '</div>' +
                '<div style="background:#E5E7EB; height:8px; border-radius:4px; margin-top:5px;">' +
                '<div style="background:linear-gradient(90deg,#4F46E5,#7C3AED); width:' + p.progress_percent + '%; height:100%; border-radius:4px;"></div></div>' +
                '<div style="font-size:0.8rem; color:#6B7280; margin-top:3px;">' + p.progress_percent + '% complete</div></div>';
        });
    } catch(err) { console.error(err); }
}

async function markAttendance() {
    if (!currentUser) return alert('Login karein!');
    try {
        const r = await fetch(API_URL + '/attendance', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({student_name: currentUser.name})
        });
        const d = await r.json();
        var statusEl = document.getElementById('attendance-status');
        if (statusEl) {
            statusEl.innerText = d.message;
            statusEl.style.color = d.success ? '#10B981' : '#EF4444';
            statusEl.style.fontWeight = 'bold';
            statusEl.style.marginTop = '10px';
        }
        alert(d.message);
    } catch(err) { alert('Error'); }
}

// ============================================
//   TEACHER DASHBOARD
// ============================================
function loadTeacherDash() {
    if (!currentUser) return;
    var nameEl = document.getElementById('teacher-name');
    if (nameEl) nameEl.innerText = currentUser.name;
    loadChats('teacher-chat-box');
    loadManage();
    setTimeout(loadSecurityPanel, 500);
}

async function addNews() {
    const text = document.getElementById('new-news').value.trim();
    if (!text) return alert('Text daalein');
    await fetch(API_URL + '/news', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({text})});
    document.getElementById('new-news').value = '';
    loadManage();
}

async function addSoftware() {
    const name = document.getElementById('new-soft-name').value.trim();
    const link = document.getElementById('new-soft-link').value.trim();
    const image = document.getElementById('new-soft-image').value.trim();
    if (!name) return alert('Name daalein');
    await fetch(API_URL + '/software', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name, link, image})});
    document.getElementById('new-soft-name').value = '';
    document.getElementById('new-soft-link').value = '';
    document.getElementById('new-soft-image').value = '';
    loadManage();
}

async function addCourse() {
    const title = document.getElementById('new-course-title').value.trim();
    const image = document.getElementById('new-course-image').value.trim();
    if (!title) return alert('Title daalein');
    await fetch(API_URL + '/courses', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({title, image})});
    document.getElementById('new-course-title').value = '';
    document.getElementById('new-course-image').value = '';
    loadManage();
}

async function loadManage() {
    try {
        const c = await fetch(API_URL + '/courses').then(r => r.json());
        const s = await fetch(API_URL + '/software').then(r => r.json());
        const n = await fetch(API_URL + '/news').then(r => r.json());
        const m = document.getElementById('manage-content');
        if (!m) return;
        m.innerHTML = '<h4 style="color:#4F46E5;">📚 Courses</h4>';
        c.forEach(function(x) { m.innerHTML += '<div style="padding:6px;background:#f9fafb;border-radius:6px;margin-bottom:6px;font-size:0.85rem;">' + x.title + '<br><button class="btn-primary" style="padding:3px 8px;font-size:0.7rem;margin:4px 4px 0 0;" onclick="editCourse(' + x.id + ')">✏️ Edit</button><button class="btn-danger" style="padding:3px 8px;font-size:0.7rem;margin-top:4px;" onclick="del(\'courses\',' + x.id + ')">🗑️ Delete</button></div>'; });
        m.innerHTML += '<h4 style="color:#10B981;">💻 Software</h4>';
        s.forEach(function(x) { m.innerHTML += '<div style="padding:6px;background:#f9fafb;border-radius:6px;margin-bottom:6px;font-size:0.85rem;">' + x.name + '<br><button class="btn-primary" style="padding:3px 8px;font-size:0.7rem;margin:4px 4px 0 0;" onclick="editSoftware(' + x.id + ')">✏️ Edit</button><button class="btn-danger" style="padding:3px 8px;font-size:0.7rem;margin-top:4px;" onclick="del(\'software\',' + x.id + ')">🗑️ Delete</button></div>'; });
        m.innerHTML += '<h4 style="color:#EF4444;">📢 News</h4>';
        n.forEach(function(x) { m.innerHTML += '<div style="padding:6px;background:#f9fafb;border-radius:6px;margin-bottom:6px;font-size:0.85rem;">' + x.text.substring(0, 30) + '...<br><button class="btn-danger" style="padding:3px 8px;font-size:0.7rem;" onclick="del(\'news\',' + x.id + ')">🗑️ Delete</button></div>'; });
    } catch(err) { console.error(err); }
}

async function editCourse(id) {
    const c = await fetch(API_URL + '/courses').then(r => r.json());
    const x = c.find(i => i.id === id);
    if (!x) return;
    const t = prompt('Name:', x.title); if (t === null) return;
    const d = prompt('Description:', x.description || ''); if (d === null) return;
    const img = prompt('Image:', x.image || ''); if (img === null) return;
    await fetch(API_URL + '/courses/' + id, {method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({title: t, description: d, image: img})});
    loadManage();
}

async function editSoftware(id) {
    const s = await fetch(API_URL + '/software').then(r => r.json());
    const x = s.find(i => i.id === id);
    if (!x) return;
    const n = prompt('Name:', x.name); if (n === null) return;
    const l = prompt('Link:', x.link || ''); if (l === null) return;
    const img = prompt('Image:', x.image || ''); if (img === null) return;
    await fetch(API_URL + '/software/' + id, {method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name: n, link: l, image: img})});
    loadManage();
}

async function del(type, id) {
    if (!confirm('Delete?')) return;
    await fetch(API_URL + '/' + type + '/' + id, {method: 'DELETE'});
    loadManage();
}

// ============================================
//   SECURITY PANEL
// ============================================
async function loadSecurityPanel() {
    try {
        const stats = await fetch(API_URL + '/security/stats').then(r => r.json());
        var el;
        el = document.getElementById('stat-attacks'); if (el) el.innerText = stats.total_attacks || 0;
        el = document.getElementById('stat-blocked'); if (el) el.innerText = stats.blocked_ips || 0;
        el = document.getElementById('stat-today'); if (el) el.innerText = stats.attacks_today || 0;
        el = document.getElementById('stat-logins'); if (el) el.innerText = stats.failed_logins_today || 0;
        el = document.getElementById('notif-badge'); if (el) el.innerText = stats.unread_notifications || 0;
        const notifs = await fetch(API_URL + '/security/notifications').then(r => r.json());
        const list = document.getElementById('notifications-list');
        if (!list) return;
        list.innerHTML = '';
        if (notifs.length === 0) {
            list.innerHTML = '<p style="color:#6B7280;text-align:center;padding:20px;">✅ Koi attack nahi. Website secure hai!</p>';
        } else {
            notifs.forEach(function(n) {
                list.innerHTML += '<div style="padding:10px;background:#FEE2E2;border-left:4px solid #DC2626;border-radius:0 6px 6px 0;margin-bottom:8px;">' +
                    '<div style="font-weight:600;font-size:0.9rem;">' + n.title + '</div>' +
                    '<div style="font-size:0.8rem;color:#6B7280;margin-top:4px;">' + n.message + '</div>' +
                    '<div style="font-size:0.7rem;color:#9CA3AF;margin-top:4px;">' + n.timestamp + '</div></div>';
            });
        }
    } catch(err) { console.error(err); }
}

async function markAllRead() {
    await fetch(API_URL + '/security/notifications/read', {method: 'POST'});
    loadSecurityPanel();
    alert('✅ Sab read!');
}

async function loadBlockedIPs() {
    const blocked = await fetch(API_URL + '/security/blocked').then(r => r.json());
    if (blocked.length === 0) { alert('✅ Koi IP blocked nahi.'); return; }
    let msg = '🚫 Blocked IPs:\n\n';
    blocked.forEach(function(ip, i) { msg += (i+1) + '. ' + ip.ip + '\n'; });
    if (confirm(msg + '\nSab unblock karein?')) {
        for (const ip of blocked) await fetch(API_URL + '/security/blocked/' + ip.id, {method: 'DELETE'});
        loadSecurityPanel();
    }
}

// ============================================
//   CHAT
// ============================================
async function loadChats(boxId) {
    try {
        const c = await fetch(API_URL + '/chats').then(r => r.json());
        const box = document.getElementById(boxId);
        if (!box) return;
        box.innerHTML = '';
        c.forEach(function(x) {
            const cls = x.sender === 'teacher' ? 'teacher' : '';
            box.innerHTML += '<div class="chat-msg ' + cls + '"><b>' + (x.sender === 'teacher' ? 'Teacher' : 'Student') + ':</b> ' + x.message + '</div>';
        });
        box.scrollTop = box.scrollHeight;
    } catch(err) { console.error(err); }
}

async function sendChat(role) {
    const id = role === 'student' ? 'student-msg' : 'teacher-msg';
    const msg = document.getElementById(id).value.trim();
    if (!msg) return;
    await fetch(API_URL + '/chats', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({sender: role, message: msg})});
    document.getElementById(id).value = '';
    loadChats(role === 'student' ? 'student-chat-box' : 'teacher-chat-box');
}

// ============================================
//   AI CHAT
// ============================================
function toggleAI() { document.getElementById('ai-chat-container').classList.toggle('hidden'); }
function handleAIKeyPress(e) { if (e.key === 'Enter') sendAIMessage(); }

async function sendAIMessage() {
    const input = document.getElementById('ai-input');
    const msg = input.value.trim();
    if (!msg) return;
    addAI('user', msg);
    input.value = '';
    try {
        let r = await fetch(API_URL + '/ai/smart', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: msg})
        });
        let d = await r.json();
        let response = d.response;
        if (!response || response === 'undefined') {
            r = await fetch(API_URL + '/ai', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            });
            d = await r.json();
            response = d.response || 'Maazrat!';
        }
        addAI('bot', response);
    } catch(err) { addAI('bot', 'Server se connect nahi ho raha.'); }
}

function addAI(sender, text) {
    const box = document.getElementById('ai-messages');
    const div = document.createElement('div');
    div.className = 'ai-msg ' + sender;
    div.innerHTML = text;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

// ============================================
//   AUTO REFRESH
// ============================================
setInterval(function() {
    if (!currentUser) return;
    if (currentUser.role === 'student') {
        const d = document.getElementById('student-dashboard');
        if (d && d.style.display === 'block') loadChats('student-chat-box');
    }
    if (currentUser.role === 'teacher') {
        const d = document.getElementById('teacher-dashboard');
        if (d && d.style.display === 'block') loadChats('teacher-chat-box');
    }
}, 3000);

// ============================================
//   INITIALIZE
// ============================================
window.addEventListener('load', function() {
    console.log('✅ Script loaded!');
    loadVoices();
    updateNav();
    if (currentUser) {
        showView(currentUser.role + '-dashboard');
    } else {
        showView('home');
    }
});

document.addEventListener('click', function() {
    if (!voicesLoaded) loadVoices();
}, { once: true });
// 🎯 SIMPLE AI FIX
window.sendAIMessage = async function() {
    const input = document.getElementById('ai-input');
    const msg = input.value.trim();
    if (!msg) return;
    addAI('user', msg);
    input.value = '';
    try {
        const r = await fetch('/api/ai', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: msg})
        });
        const d = await r.json();
        addAI('bot', d.response || 'Reply nahi mila');
    } catch(err) {
        addAI('bot', 'Server error');
    }
};

// 🎯 CLIENT-SIDE AI (Instant, no backend needed)
window.sendAIMessage = function() {
    const input = document.getElementById('ai-input');
    const msg = input.value.trim();
    if (!msg) return;
    addAI('user', msg);
    input.value = '';
    
    const m = msg.toLowerCase();
    let reply = '';
    
    if (m.includes('hello') || m.includes('hi') || m.includes('salam') || m.includes('assalam') || m.includes('aoa')) {
        reply = 'Assalam-o-Alaikum! 👋 Main Questian AI hoon. Poochiye:<br>• Courses<br>• Fees<br>• Admission<br>• Software<br>• Login';
    } else if (m.includes('python')) {
        reply = '🐍 Python ek aasan aur powerful language hai. AI, Data Science, Web Development mein use hoti hai. "Python Language" course zero se shuru karta hai.';
    } else if (m.includes('course') || m.includes('courses')) {
        reply = '📚 Hamare paas 12 courses hain:<br>1. Mobile App Development<br>2. Cyber Security<br>3. Graphics Designing<br>4. Penetration Testing<br>5. Ethical Hacking<br>6. Python<br>7. AI & ML<br>8. Deep Learning<br>9. C#<br>10. C<br>11. C++<br>12. Java OOP';
    } else if (m.includes('ai') || m.includes('machine learning') || m.includes('ml')) {
        reply = '🤖 AI aur ML course computers ko smart banane ke baare mein hai. Isme models train karna sikhaya jata hai.';
    } else if (m.includes('cyber') || m.includes('security') || m.includes('hacking')) {
        reply = '🔒 Cyber Security aur Ethical Hacking course systems ko secure karna sikhata hai. Penetration Testing bhi shamil hai.';
    } else if (m.includes('fee') || m.includes('fees') || m.includes('paisa') || m.includes('price')) {
        reply = '💰 Fees bohat affordable hai. Exact details ke liye Admission form bharein ya teacher se chat karein.';
    } else if (m.includes('admission') || m.includes('apply')) {
        reply = '🎓 Admission ke liye Navbar mein "Admission" tab hai. Form bharein aur submit karein!';
    } else if (m.includes('login') || m.includes('signup')) {
        reply = '🔐 Login: student/123 ya teacher/123<br><br>Naya account ke liye "Sign Up" link use karein.';
    } else if (m.includes('software') || m.includes('download')) {
        reply = '💻 "Software" tab mein VS Code, XAMPP, Photoshop, Python IDLE, Kali Linux, Git, Node.js, Docker sab hain.';
    } else if (m.includes('test') || m.includes('mcq')) {
        reply = '📝 Course ke andar "Take MCQ Test" button hai. Test ke baad foran result aata hai.';
    } else if (m.includes('attendance') || m.includes('hazri')) {
        reply = '📅 Student Dashboard mein "Attendance" card hai. "Mark Present" button dabayein.';
    } else if (m.includes('developer') || m.includes('abdul') || m.includes('qadir')) {
        reply = '👨‍💻 Developer: Abdul Qadir Soomro<br>📧 24cse23@quest.edu.pk<br>📱 03359996428<br>📍 Larkana, Pakistan';
    } else if (m.includes('teacher') || m.includes('contact')) {
        reply = '💬 Login karne ke baad Student Dashboard mein "Chat with Teacher" section hai.';
    } else if (m.includes('help') || m.includes('madad')) {
        reply = '🎯 Poochiye: courses, fees, admission, login, software, attendance, developer info';
    } else if (m.includes('thanks') || m.includes('shukriya')) {
        reply = 'Aapka khair maqdam! 😊';
    } else if (m.includes('bye')) {
        reply = 'Allah Hafiz! 👋 Apna khayal rakhein!';
    } else {
        reply = '🤔 Mujhe exact jawab nahi pata. Poochiye:<br>• Courses<br>• Fees<br>• Admission<br>• Login<br>• Software<br>• Developer';
    }
    
    setTimeout(() => addAI('bot', reply), 400);
};
