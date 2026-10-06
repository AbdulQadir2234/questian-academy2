// ============================================
//   QUESTIAN ACADEMY - script.js
// ============================================

const API_URL = '/api';
let currentUser = null;
try { const s = localStorage.getItem('currentUser'); if (s) currentUser = JSON.parse(s); } catch(e) { localStorage.removeItem('currentUser'); }

var DEVELOPER_INFO = {
    name: 'Abdul Qadir Soomro',
    role: 'Full Stack Web Developer • Penetration Tester • AI & ML Engineer',
    email: '24cse23@quest.edu.pk',
    phone: '03359996428',
    location: 'Larkana, Pakistan'
};

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
    var m = url.match(/youtube\.com\/live\/([^?&#\s]+)/);
    if (m) return m[1];
    m = url.match(/youtu\.be\/([^?&#\s]+)/);
    if (m) return m[1];
    m = url.match(/[?&]v=([^?&#\s]+)/);
    if (m) return m[1];
    if (/^[a-zA-Z0-9_-]{11}$/.test(url)) return url;
    return 'dQw4w9WgXcQ';
}

// ============================================
//   VOICE
// ============================================
let femaleVoice = null;
let voiceEnabled = true;

function loadVoices() {
    if (!('speechSynthesis' in window)) return;
    var voices = speechSynthesis.getVoices();
    if (!voices.length) return;
    femaleVoice = voices.find(v => v.lang === 'hi-IN') ||
                  voices.find(v => v.name.toLowerCase().includes('female')) ||
                  voices[0];
}
if ('speechSynthesis' in window) {
    loadVoices();
    speechSynthesis.onvoiceschanged = loadVoices;
    setTimeout(loadVoices, 500);
}

function stopVoice() { if ('speechSynthesis' in window) speechSynthesis.cancel(); }

function speakUrdu(text) {
    if (!voiceEnabled) return;
    if (!('speechSynthesis' in window)) return;
    if (!femaleVoice) loadVoices();
    speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(text);
    u.rate = 0.85; u.pitch = 1.3;
    if (femaleVoice) { u.voice = femaleVoice; u.lang = femaleVoice.lang; }
    else u.lang = 'hi-IN';
    setTimeout(function() { speechSynthesis.speak(u); }, 100);
}

function toggleVoice() {
    voiceEnabled = !voiceEnabled;
    var btn = document.getElementById('voice-toggle-btn');
    if (!voiceEnabled) {
        stopVoice();
        if (btn) { btn.innerText = 'OFF'; btn.style.background = '#FEE2E2'; btn.style.color = '#DC2626'; }
    } else {
        if (btn) { btn.innerText = 'ON'; btn.style.background = '#E0E7FF'; btn.style.color = '#4F46E5'; }
        speakUrdu("Voice on ho gayi hai");
    }
}

function admissionVoiceGuide() {
    if (!voiceEnabled) { alert('Voice OFF hai'); return; }
    speakUrdu("Assalam o alaikum. Admission form mein apna naam, email, phone aur course select karein.");
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
            '<button class="btn-primary" style="width:100%;margin-top:15px;">Start Learning</button></div>';
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
        setTimeout(function() {
            if (voiceEnabled) speakUrdu("Admission form khul gaya");
        }, 500);
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
    el = document.querySelector('.dev-role'); if (el) el.innerText = d.role;
    el = document.getElementById('dev-avatar'); if (el) el.innerText = d.name.charAt(0).toUpperCase();
}

async function submitContact(e) {
    e.preventDefault();
    var name = document.getElementById('contact-name').value.trim();
    var email = document.getElementById('contact-email').value.trim();
    var subject = document.getElementById('contact-subject').value.trim();
    var message = document.getElementById('contact-message').value.trim();
    if (!name || !email || !subject || !message) return alert('Saare fields bharein');
    try {
        var r = await fetch(API_URL + '/contact', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, email, subject, message})
        });
        var d = await r.json();
        alert(d.success ? 'Message bhej diya' : 'Error');
        if (d.success) e.target.reset();
    } catch(err) { alert('Error'); }
}

function openPolicy(policy) {
    var messages = {
        'Disclaimer': 'Yeh website educational purposes ke liye hai.',
        'Privacy Policy': 'Aapki privacy hamare liye ahem hai.',
        'Terms of Service': 'Website use karne ke liye in terms se agree karein.',
        'Sitemap': 'Home, Admission, Courses, Software, News, About, Login'
    };
    alert(policy + ':\n\n' + (messages[policy] || 'Jald available'));
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

function openDashboard() {
    document.getElementById('profile-dropdown').classList.add('hidden');
    if (currentUser) showView(currentUser.role + '-dashboard');
}

function openSettings() {
    document.getElementById('profile-dropdown').classList.add('hidden');
    alert('Settings page jald available hoga');
}

function openPayment() {
    document.getElementById('profile-dropdown').classList.add('hidden');
    alert('Payment system jald available hoga');
}

function openCertificate() {
    document.getElementById('profile-dropdown').classList.add('hidden');
    alert('Certificate system jald available hoga');
}

// ============================================
//   LOGIN WITH OTP
// ============================================
async function handleLogin(e) {
    e.preventDefault();
    stopVoice();
    const username = document.getElementById('login-user').value.trim();
    const password = document.getElementById('login-pass').value.trim();
    if (!username || !password) return alert('Username aur password daalein');
    
    try {
        const r = await fetch(API_URL + '/login/send-otp', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });
        const d = await r.json();
        
        if (!d.success) return alert('❌ ' + d.message);
        
        window.pendingLoginEmail = d.email;
        alert('✅ ' + d.message);
        showOtpScreen('login');
    } catch(err) {
        alert('Server error');
    }
}

// ============================================
//   SIGNUP WITH OTP
// ============================================
async function handleSignup(e) {
    e.preventDefault();
    const name = document.getElementById('signup-name').value.trim();
    const username = document.getElementById('signup-user').value.trim();
    const email = document.getElementById('signup-email').value.trim().toLowerCase();
    const password = document.getElementById('signup-pass').value.trim();
    const role = document.getElementById('signup-role').value;

    if (!name || !username || !email || !password) return alert('Saare fields bharein');
    if (password.length < 3) return alert('Password 3+ characters');

    try {
        const r = await fetch(API_URL + '/signup/send-otp', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, username, email, password, role})
        });
        const d = await r.json();
        
        if (!d.success) return alert('❌ ' + d.message);
        
        window.pendingSignup = {email};
        alert('✅ ' + d.message);
        showOtpScreen('signup');
    } catch(err) {
        alert('Server error');
    }
}

function onRoleChange() {
    const role = document.getElementById('signup-role').value;
    const note = document.getElementById('teacher-note');
    if (note) note.style.display = role === 'teacher' ? 'block' : 'none';
}

// ============================================
//   OTP SCREEN
// ============================================
function showOtpScreen(purpose) {
    document.querySelectorAll('.container').forEach(el => { el.classList.remove('active'); el.style.display = 'none'; });
    
    let otpView = document.getElementById('otp-view');
    if (!otpView) {
        otpView = document.createElement('div');
        otpView.id = 'otp-view';
        otpView.className = 'container';
        document.body.insertBefore(otpView, document.querySelector('.main-footer'));
    }
    
    otpView.style.display = 'block';
    otpView.classList.add('active');
    
    const title = purpose === 'signup' ? 'Verify Email' : 'Login Verification';
    const info = 'Aapke email par 6-digit code bheja gaya hai. Code daalein:';
    
    otpView.innerHTML = `
        <div style="max-width:400px; margin:40px auto; text-align:center; padding:0 20px;">
            <h2 style="margin-bottom:10px;">${title}</h2>
            <p style="color:#6b7280; font-size:0.9rem; margin-bottom:24px;">${info}</p>
            <input type="text" id="otp-input" placeholder="000000" maxlength="6" 
                   style="text-align:center; font-size:1.5rem; letter-spacing:8px; font-weight:600; padding:14px;">
            <button onclick="verifyOtp('${purpose}')" class="btn-primary full-width" style="margin-top:12px;">Verify Code</button>
            <p style="color:#6b7280; font-size:0.85rem; margin-top:15px; cursor:pointer;" onclick="cancelOtp()">← Cancel</p>
        </div>
    `;
    
    setTimeout(() => document.getElementById('otp-input').focus(), 200);
}

function cancelOtp() {
    const otpView = document.getElementById('otp-view');
    if (otpView) { otpView.style.display = 'none'; otpView.classList.remove('active'); }
    showView('login');
}

async function verifyOtp(purpose) {
    const code = document.getElementById('otp-input').value.trim();
    if (!code || code.length !== 6) return alert('6-digit code daalein');
    
    const url = purpose === 'signup' ? '/signup/verify' : '/login/verify';
    const email = purpose === 'signup' ? window.pendingSignup.email : window.pendingLoginEmail;
    
    if (!email) { alert('Session error'); cancelOtp(); return; }
    
    try {
        const r = await fetch(API_URL + url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, code})
        });
        const d = await r.json();
        
        if (!d.success) return alert('❌ ' + d.message);
        
        currentUser = d.user;
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        
        cancelOtp();
        updateNav();
        showView(currentUser.role + '-dashboard');
        alert('✅ Login successful. Welcome ' + currentUser.name);
    } catch(err) {
        alert('Verify error');
    }
}

// ============================================
//   FORGOT PASSWORD
// ============================================
function showForgotPassword() { showView('forgot'); }

async function handleForgotPassword(e) {
    e.preventDefault();
    const email = document.getElementById('forgot-email').value.trim().toLowerCase();
    if (!email) return alert('Email daalein');
    
    const btn = e.target.querySelector('button');
    btn.disabled = true; btn.innerText = 'Sending...';
    
    try {
        const r = await fetch(API_URL + '/forgot-password', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email})
        });
        const d = await r.json();
        
        alert(d.success ? '✅ ' + d.message : '❌ ' + d.message);
        if (d.success) { e.target.reset(); showView('login'); }
    } catch(err) { alert('Server error'); }
    finally { btn.disabled = false; btn.innerText = 'Send Reset Link'; }
}

async function handleResetPassword(e) {
    e.preventDefault();
    const password = document.getElementById('reset-password').value;
    const confirm = document.getElementById('reset-confirm').value;
    
    if (password.length < 3) return alert('Password kam se kam 3 characters');
    if (password !== confirm) return alert('Dono passwords match nahi');
    
    const token = new URLSearchParams(window.location.search).get('token');
    if (!token) return alert('Reset token nahi mila');
    
    const btn = e.target.querySelector('button');
    btn.disabled = true; btn.innerText = 'Resetting...';
    
    try {
        const r = await fetch(API_URL + '/reset-password', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({token, password})
        });
        const d = await r.json();
        
        alert(d.success ? '✅ ' + d.message : '❌ ' + d.message);
        if (d.success) {
            window.history.replaceState({}, document.title, '/');
            showView('login');
        }
    } catch(err) { alert('Server error'); }
    finally { btn.disabled = false; btn.innerText = 'Reset Password'; }
}

// ============================================
//   AUTH TOGGLE
// ============================================
function toggleAuthForm() {
    const lf = document.getElementById('login-form');
    const sf = document.getElementById('signup-form');
    const title = document.getElementById('auth-title');
    const sw = document.getElementById('auth-switch');
    if (lf.classList.contains('hidden')) {
        lf.classList.remove('hidden'); sf.classList.add('hidden');
        if (title) title.innerText = 'Login';
        if (sw) sw.innerHTML = 'Don\'t have an account? <span onclick="toggleAuthForm()" style="color:#1e3a8a;font-weight:600;cursor:pointer;">Sign Up</span>';
    } else {
        lf.classList.add('hidden'); sf.classList.remove('hidden');
        if (title) title.innerText = 'Create Account';
        if (sw) sw.innerHTML = 'Already have an account? <span onclick="toggleAuthForm()" style="color:#1e3a8a;font-weight:600;cursor:pointer;">Login</span>';
    }
}

function logout() {
    stopVoice();
    currentUser = null;
    localStorage.removeItem('currentUser');
    var menu = document.getElementById('profile-dropdown');
    if (menu) menu.classList.add('hidden');
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
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, email, phone, course})
        });
        alert('Admission submit ho gaya');
        e.target.reset();
        showView('home');
    } catch(err) { alert('Error'); }
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
    var videoUrl = VIDEO_LINKS[title] || '';
    var videoId = extractYouTubeID(videoUrl);
    var videoBox = document.querySelector('.video-placeholder');
    if (videoBox) {
        videoBox.innerHTML = '<iframe width="100%" height="100%" src="https://www.youtube.com/embed/' + videoId + '?rel=0" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="border-radius:6px;"></iframe>';
        videoBox.style.padding = '0';
        videoBox.style.background = '#000';
    }
    if (currentUser && currentUser.role === 'student') updateProgress(id, title, 25);
}

async function updateProgress(courseId, courseTitle, percent) {
    if (!currentUser) return;
    try {
        await fetch(API_URL + '/progress', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: currentUser.username, course_id: courseId, course_title: courseTitle, progress_percent: percent})
        });
    } catch(err) { console.error(err); }
}

function hideCourseDetail() {
    document.getElementById('courses-list').classList.remove('hidden');
    document.getElementById('course-detail').classList.add('hidden');
}

function downloadNotes() { alert('Notes download started'); }
function startTest() { document.getElementById('test-area').classList.remove('hidden'); }
function submitTest() {
    const s = document.querySelector('input[name="q1"]:checked');
    alert(s && s.value === 'a' ? 'Correct!' : 'Wrong');
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
                '<button class="btn-success" style="width:100%;margin-top:15px;">Download</button></div>';
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
        c.forEach(function(x) { list.innerHTML += '<div class="news-item">' + x.text + '</div>'; });
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
            box.innerHTML = '<p style="color:#6B7280;">Abhi koi course shuru nahi kiya.</p>';
            return;
        }
        progress.forEach(function(p) {
            box.innerHTML += '<div style="margin-bottom:10px; padding:10px; background:#F9FAFB; border-radius:4px;">' +
                '<div style="font-weight:600;">' + p.course_title + '</div>' +
                '<div style="background:#E5E7EB; height:8px; border-radius:4px; margin-top:5px;">' +
                '<div style="background:#1e3a8a; width:' + p.progress_percent + '%; height:100%; border-radius:4px;"></div></div>' +
                '<div style="font-size:0.8rem; color:#6B7280; margin-top:3px;">' + p.progress_percent + '% complete</div></div>';
        });
    } catch(err) { console.error(err); }
}

async function markAttendance() {
    if (!currentUser) return alert('Login karein');
    try {
        const r = await fetch(API_URL + '/attendance', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({student_name: currentUser.name})
        });
        const d = await r.json();
        var statusEl = document.getElementById('attendance-status');
        if (statusEl) {
            statusEl.innerText = d.message;
            statusEl.style.color = d.success ? '#047857' : '#b91c1c';
            statusEl.style.fontWeight = 'bold';
            statusEl.style.marginTop = '10px';
        }
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
        m.innerHTML = '<h4 style="color:#1e3a8a;">Courses</h4>';
        c.forEach(function(x) { m.innerHTML += '<div style="padding:6px;background:#f9fafb;border-radius:4px;margin-bottom:6px;font-size:0.85rem;">' + x.title + '<br><button class="btn-primary" style="padding:3px 8px;font-size:0.7rem;margin:4px 4px 0 0;" onclick="editCourse(' + x.id + ')">Edit</button><button class="btn-danger" style="padding:3px 8px;font-size:0.7rem;margin-top:4px;" onclick="del(\'courses\',' + x.id + ')">Delete</button></div>'; });
        m.innerHTML += '<h4 style="color:#047857;">Software</h4>';
        s.forEach(function(x) { m.innerHTML += '<div style="padding:6px;background:#f9fafb;border-radius:4px;margin-bottom:6px;font-size:0.85rem;">' + x.name + '<br><button class="btn-danger" style="padding:3px 8px;font-size:0.7rem;margin-top:4px;" onclick="del(\'software\',' + x.id + ')">Delete</button></div>'; });
        m.innerHTML += '<h4 style="color:#b91c1c;">News</h4>';
        n.forEach(function(x) { m.innerHTML += '<div style="padding:6px;background:#f9fafb;border-radius:4px;margin-bottom:6px;font-size:0.85rem;">' + x.text.substring(0, 30) + '...<br><button class="btn-danger" style="padding:3px 8px;font-size:0.7rem;" onclick="del(\'news\',' + x.id + ')">Delete</button></div>'; });
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

async function del(type, id) {
    if (!confirm('Delete?')) return;
    await fetch(API_URL + '/' + type + '/' + id, {method: 'DELETE'});
    loadManage();
}

// ============================================
//   SECURITY
// ============================================
async function loadSecurityPanel() {
    try {
        const stats = await fetch(API_URL + '/security/stats').then(r => r.json());
        var el;
        el = document.getElementById('stat-attacks'); if (el) el.innerText = stats.total_attacks || 0;
        el = document.getElementById('stat-blocked'); if (el) el.innerText = stats.blocked_ips || 0;
        el = document.getElementById('stat-today'); if (el) el.innerText = stats.attacks_today || 0;
        el = document.getElementById('stat-logins'); if (el) el.innerText = stats.failed_logins_today || 0;
    } catch(err) { console.error(err); }
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
//   AI CHAT - POWERFUL
// ============================================
function toggleAI() {
    document.getElementById('ai-chat-container').classList.toggle('hidden');
}

function handleAIKeyPress(e) { if (e.key === 'Enter') sendAIMessage(); }

async function sendAIMessage() {
    const input = document.getElementById('ai-input');
    const msg = input.value.trim();
    if (!msg) return;
    
    addAI('user', msg);
    input.value = '';
    
    // Typing indicator
    addAI('bot', '<i style="color:#9ca3af;">Soch raha hoon...</i>', 'thinking');
    
    try {
        // Try Gemini first
        let r = await fetch(API_URL + '/ai/smart', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: msg})
        });
        let d = await r.json();
        
        removeThinking();
        
        // If empty, try keyword AI
        if (!d || !d.response || d.response === 'undefined' || d.response.trim() === '') {
            r = await fetch(API_URL + '/ai', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            });
            d = await r.json();
        }
        
        const finalResp = (d && d.response) ? d.response : 'Maazrat! Dobara try karein.';
        addAI('bot', finalResp);
        
        if (d && d.source) console.log('AI source:', d.source);
    } catch(err) {
        removeThinking();
        console.error('AI error:', err);
        addAI('bot', 'Server se connect nahi ho raha.');
    }
}

function removeThinking() {
    const box = document.getElementById('ai-messages');
    const t = box.querySelector('[data-thinking="true"]');
    if (t) t.remove();
}

function addAI(sender, text, id) {
    const box = document.getElementById('ai-messages');
    const div = document.createElement('div');
    div.className = 'ai-msg ' + sender;
    if (id === 'thinking') div.setAttribute('data-thinking', 'true');
    div.innerHTML = text;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

// ============================================
//   AUTO REFRESH CHAT
// ============================================
setInterval(function() {
    if (!currentUser) return;
    if (currentUser.role === 'student') {
        const d = document.getElementById('student-dashboard');
        if (d && d.classList.contains('active')) loadChats('student-chat-box');
    }
    if (currentUser.role === 'teacher') {
        const d = document.getElementById('teacher-dashboard');
        if (d && d.classList.contains('active')) loadChats('teacher-chat-box');
    }
}, 3000);

// ============================================
//   INITIALIZE
// ============================================
window.addEventListener('load', function() {
    console.log('Script loaded');
    loadVoices();
    updateNav();
    
    // Check reset token
    const token = new URLSearchParams(window.location.search).get('token');
    if (token) {
        fetch(API_URL + '/verify-reset-token', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({token})
        })
        .then(r => r.json())
        .then(d => {
            if (d.success) showView('reset');
            else { alert('Link galat ya expire'); showView('login'); }
        })
        .catch(() => showView('login'));
        return;
    }
    
    if (currentUser) showView(currentUser.role + '-dashboard');
    else showView('home');
});