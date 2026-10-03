"""
==============================================
    QUESTIAN ACADEMY - Backend
    Developer: Abdul Qadir Soomro
==============================================
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'questian-academy-secret-2026')
CORS(app, origins=['http://127.0.0.1:5000', 'http://localhost:5000'])

# Gemini Multi-Model
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
gemini_client = None
GEMINI_MODELS = ['gemini-2.5-flash-lite', 'gemini-2.0-flash-lite', 'gemini-2.0-flash', 'gemini-flash-latest']

if GEMINI_KEY:
    try:
        from google import genai
        gemini_client = genai.Client(api_key=GEMINI_KEY)
        print(f"✅ Gemini client ready")
    except Exception as e:
        print(f"⚠️ Gemini error: {str(e)[:150]}")
        gemini_client = None
else:
    print("⚠️ GEMINI_API_KEY not found")

DATABASE = 'academy.db'
MAX_LOGIN_ATTEMPTS = 10
BLOCK_DURATION_MINUTES = 5
SUSPICIOUS_PATTERNS = [
    r"('|--|;|/\*|\*/|xp_|exec|union|select|insert|delete|drop|update)",
    r"(<script|javascript:|onerror=|onload=|alert\()",
    r"(\.\./|\.\.\\|/etc/passwd|cmd\.exe)",
    r"(eval\(|exec\(|system\(|passthru\()",
]


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        name TEXT NOT NULL,
        created_at TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        image TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS software (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        link TEXT,
        image TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        date TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS admissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        course TEXT NOT NULL,
        date TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        course_id INTEGER NOT NULL,
        course_title TEXT,
        progress_percent INTEGER DEFAULT 0,
        completed INTEGER DEFAULT 0,
        last_updated TEXT,
        UNIQUE(username, course_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS attack_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT NOT NULL,
        attack_type TEXT NOT NULL,
        details TEXT,
        endpoint TEXT,
        user_agent TEXT,
        timestamp TEXT,
        severity TEXT DEFAULT 'LOW')''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS blocked_ips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT UNIQUE NOT NULL,
        reason TEXT,
        blocked_at TEXT,
        blocked_until TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS login_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT NOT NULL,
        username TEXT,
        success INTEGER,
        timestamp TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        message TEXT,
        type TEXT DEFAULT 'info',
        is_read INTEGER DEFAULT 0,
        timestamp TEXT)''')

    # Contact Messages
    cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        date TEXT,
        is_read INTEGER DEFAULT 0)''')

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, role, name, created_at) VALUES (?, ?, ?, ?, ?)",
                       ('student', generate_password_hash('123'), 'student', 'Ali', datetime.now().strftime('%Y-%m-%d %H:%M')))
        cursor.execute("INSERT INTO users (username, password, role, name, created_at) VALUES (?, ?, ?, ?, ?)",
                       ('teacher', generate_password_hash('123'), 'teacher', 'Sir Ahmed', datetime.now().strftime('%Y-%m-%d %H:%M')))

    cursor.execute("SELECT COUNT(*) FROM courses")
    if cursor.fetchone()[0] == 0:
        default_courses = [
            ('Mobile Application Development', 'Android aur iOS apps banana seekhein.', 'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=600'),
            ('Cyber Security', 'Systems ko secure karna seekhein.', 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=600'),
            ('Graphics Designing', 'Photoshop aur Illustrator seekhein.', 'https://images.unsplash.com/photo-1626785774573-4b799315345d?w=600'),
            ('Penetration Testing', 'Systems ki testing karna seekhein.', 'https://images.unsplash.com/photo-1563206767-5b18f218e8de?w=600'),
            ('Ethical Hacking', 'Legal hacking techniques.', 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600'),
            ('Python Language', 'Python programming zero se hero tak.', 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=600'),
            ('AI and Machine Learning', 'AI aur ML models banana seekhein.', 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600'),
            ('Deep Learning', 'Neural networks aur deep learning.', 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=600'),
            ('C# Language', 'C# programming language.', 'https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=600'),
            ('C Language', 'C programming ki bunyad.', 'https://images.unsplash.com/photo-1587620962725-abab7fe55159?w=600'),
            ('C++ Language', 'C++ aur OOP concepts.', 'https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=600'),
            ('Object Oriented Programming in Java', 'Java aur OOPs.', 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600')
        ]
        cursor.executemany("INSERT INTO courses (title, description, image) VALUES (?, ?, ?)", default_courses)

    cursor.execute("SELECT COUNT(*) FROM software")
    if cursor.fetchone()[0] == 0:
        default_software = [
            ('VS Code', 'https://code.visualstudio.com/download', 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600'),
            ('XAMPP', 'https://www.apachefriends.org/download.html', 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=600'),
            ('Adobe Photoshop', 'https://www.adobe.com/products/photoshop.html', 'https://images.unsplash.com/photo-1626785774573-4b799315345d?w=600'),
            ('Python IDLE', 'https://www.python.org/downloads/', 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=600'),
            ('Kali Linux', 'https://www.kali.org/get-kali/', 'https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=600'),
            ('Git', 'https://git-scm.com/downloads', 'https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=600'),
            ('Node.js', 'https://nodejs.org/en/download/', 'https://images.unsplash.com/photo-1627398242454-45a1465c2479?w=600'),
            ('Docker', 'https://www.docker.com/products/docker-desktop/', 'https://images.unsplash.com/photo-1605745341112-85968b19335b?w=600')
        ]
        cursor.executemany("INSERT INTO software (name, link, image) VALUES (?, ?, ?)", default_software)

    cursor.execute("SELECT COUNT(*) FROM news")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO news (text, date) VALUES (?, ?)",
                       ('Welcome to Questian Academy! New AI-powered semester started.', datetime.now().strftime('%Y-%m-%d %H:%M')))

    cursor.execute("SELECT COUNT(*) FROM chats")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO chats (sender, message, timestamp) VALUES (?, ?, ?)",
                       ('student', 'Sir, I have a question.', datetime.now().strftime('%Y-%m-%d %H:%M')))
        cursor.execute("INSERT INTO chats (sender, message, timestamp) VALUES (?, ?, ?)",
                       ('teacher', 'Yes, ask.', datetime.now().strftime('%Y-%m-%d %H:%M')))

    conn.commit()
    conn.close()


def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or 'unknown'


def is_ip_blocked(ip):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("SELECT * FROM blocked_ips WHERE ip=? AND blocked_until > ?", (ip, now))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def block_ip(ip, reason, minutes=BLOCK_DURATION_MINUTES):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now()
    blocked_until = (now + timedelta(minutes=minutes)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("SELECT * FROM blocked_ips WHERE ip=?", (ip,))
    if cursor.fetchone():
        cursor.execute("UPDATE blocked_ips SET reason=?, blocked_at=?, blocked_until=? WHERE ip=?",
                       (reason, now.strftime('%Y-%m-%d %H:%M:%S'), blocked_until, ip))
    else:
        cursor.execute("INSERT INTO blocked_ips (ip, reason, blocked_at, blocked_until) VALUES (?, ?, ?, ?)",
                       (ip, reason, now.strftime('%Y-%m-%d %H:%M:%S'), blocked_until))
    conn.commit()
    conn.close()


def log_attack(ip, attack_type, details, endpoint, severity='MEDIUM'):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ua = request.headers.get('User-Agent', 'Unknown')[:200]
    cursor.execute("INSERT INTO attack_logs (ip, attack_type, details, endpoint, user_agent, timestamp, severity) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (ip, attack_type, details[:500], endpoint, ua, now, severity))
    cursor.execute("INSERT INTO notifications (title, message, type, is_read, timestamp) VALUES (?, ?, ?, 0, ?)",
                   (f"⚠️ {attack_type} Detected!",
                    f"IP: {ip}\nEndpoint: {endpoint}\nDetails: {details[:200]}", 'attack', now))
    conn.commit()
    conn.close()


def sanitize_input(text, max_length=500):
    if not text:
        return ''
    text = str(text).strip()[:max_length]
    text = re.sub(r'<[^>]*>', '', text)
    return text


def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username):
    return re.match(r'^[a-zA-Z0-9_]{3,20}$', username) is not None


@app.before_request
def security_check():
    ip = get_client_ip()
    if ip in ['127.0.0.1', 'localhost', '::1', 'unknown', None]:
        return None
    if is_ip_blocked(ip):
        return jsonify({'success': False, 'message': 'IP blocked.'}), 403
    if request.method in ['POST', 'PUT']:
        try:
            data = request.get_json(silent=True)
            if data:
                detected = None
                for pattern in SUSPICIOUS_PATTERNS:
                    if re.search(pattern, str(data), re.IGNORECASE):
                        detected = pattern
                        break
                if detected:
                    log_attack(ip, "MALICIOUS_INPUT", f"Pattern: {detected}", request.path, 'HIGH')
                    block_ip(ip, f"Malicious input")
                    return jsonify({'success': False, 'message': '⚠️ Suspicious activity!'}), 403
        except:
            pass


@app.after_request
def add_security_headers(response):
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    if request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    else:
        response.headers['Cache-Control'] = 'no-cache'
    return response


@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


# ============================================
#   CONTACT API
# ============================================
@app.route('/api/contact', methods=['POST'])
def submit_contact():
    data = request.get_json() or {}
    name = sanitize_input(data.get('name', ''), 100)
    email = sanitize_input(data.get('email', ''), 100)
    subject = sanitize_input(data.get('subject', ''), 200)
    message = sanitize_input(data.get('message', ''), 2000)

    if not name or not email or not subject or not message:
        return jsonify({'success': False, 'message': 'Sab fields zaroori!'}), 400
    if not validate_email(email):
        return jsonify({'success': False, 'message': 'Email sahi nahi!'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO contacts (name, email, subject, message, date) VALUES (?, ?, ?, ?, ?)",
                   (name, email, subject, message, datetime.now().strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Message bhej diya gaya! Hum aap se rabta karenge.'})


@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts ORDER BY id DESC")
    contacts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(contacts)


# ============================================
#   AUTHENTICATION
# ============================================
@app.route('/api/login', methods=['POST'])
def login():
    ip = get_client_ip()
    data = request.get_json() or {}
    username = sanitize_input(data.get('username', ''), 50)
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username aur password zaroori!'}), 400

    conn = get_db()
    cursor = conn.cursor()
    if ip not in ['127.0.0.1', 'localhost', '::1', 'unknown']:
        cutoff = (datetime.now() - timedelta(minutes=BLOCK_DURATION_MINUTES)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("SELECT COUNT(*) FROM login_attempts WHERE ip=? AND success=0 AND timestamp > ?", (ip, cutoff))
        failed_count = cursor.fetchone()[0]
        if failed_count >= MAX_LOGIN_ATTEMPTS:
            block_ip(ip, "Too many failed logins")
            conn.close()
            return jsonify({'success': False, 'message': f'⚠️ IP blocked {BLOCK_DURATION_MINUTES} min.'}), 429

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    success = False
    if user and check_password_hash(user['password'], password):
        success = True

    cursor.execute("INSERT INTO login_attempts (ip, username, success, timestamp) VALUES (?, ?, ?, ?)",
                   (ip, username, 1 if success else 0, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    if success:
        cursor.execute("DELETE FROM login_attempts WHERE ip=?", (ip,))
    conn.commit()
    conn.close()

    if success:
        return jsonify({'success': True, 'user': {'id': user['id'], 'username': user['username'], 'role': user['role'], 'name': user['name']}})
    else:
        return jsonify({'success': False, 'message': 'Galat credentials!'}), 401


@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    username = sanitize_input(data.get('username', ''), 50)
    password = data.get('password', '')
    name = sanitize_input(data.get('name', ''), 100)
    role = data.get('role', 'student')

    if not username or not password or not name:
        return jsonify({'success': False, 'message': 'Sab fields zaroori!'}), 400
    if not validate_username(username):
        return jsonify({'success': False, 'message': 'Username: letters, numbers, _ (3-20)'}), 400
    if len(password) < 3:
        return jsonify({'success': False, 'message': 'Password kam se kam 3 chars!'}), 400
    if role not in ['student', 'teacher']:
        role = 'student'

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Username pehle se mojood!'}), 400

    hashed_pw = generate_password_hash(password)
    cursor.execute("INSERT INTO users (username, password, role, name, created_at) VALUES (?, ?, ?, ?, ?)",
                   (username, hashed_pw, role, name, datetime.now().strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'success': True, 'message': 'Account ban gaya! Ab login karein.', 'user': {'id': new_id, 'username': username, 'role': role, 'name': name}})


# ============================================
#   COURSES
# ============================================
@app.route('/api/courses', methods=['GET'])
def get_courses():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses")
    courses = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(courses)


@app.route('/api/courses', methods=['POST'])
def add_course():
    data = request.get_json() or {}
    title = sanitize_input(data.get('title', ''), 200)
    if not title:
        return jsonify({'success': False, 'message': 'Title zaroori'}), 400
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO courses (title, description, image) VALUES (?, ?, ?)",
                   (title, sanitize_input(data.get('description', ''), 500), sanitize_input(data.get('image', ''), 500)))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': new_id, 'title': title})


@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    data = request.get_json() or {}
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE courses SET title=?, description=?, image=? WHERE id=?",
                   (sanitize_input(data.get('title'), 200), sanitize_input(data.get('description'), 500), sanitize_input(data.get('image'), 500), course_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM courses WHERE id=?", (course_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ============================================
#   SOFTWARE
# ============================================
@app.route('/api/software', methods=['GET'])
def get_software():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM software")
    software = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(software)


@app.route('/api/software', methods=['POST'])
def add_software():
    data = request.get_json() or {}
    name = sanitize_input(data.get('name', ''), 100)
    if not name:
        return jsonify({'success': False, 'message': 'Name zaroori'}), 400
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO software (name, link, image) VALUES (?, ?, ?)",
                   (name, sanitize_input(data.get('link', '#'), 500), sanitize_input(data.get('image', ''), 500)))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': new_id})


@app.route('/api/software/<int:soft_id>', methods=['PUT'])
def update_software(soft_id):
    data = request.get_json() or {}
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE software SET name=?, link=?, image=? WHERE id=?",
                   (sanitize_input(data.get('name'), 100), sanitize_input(data.get('link'), 500), sanitize_input(data.get('image'), 500), soft_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/software/<int:soft_id>', methods=['DELETE'])
def delete_software(soft_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM software WHERE id=?", (soft_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ============================================
#   NEWS
# ============================================
@app.route('/api/news', methods=['GET'])
def get_news():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news ORDER BY id DESC")
    news = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(news)


@app.route('/api/news', methods=['POST'])
def add_news():
    data = request.get_json() or {}
    text = sanitize_input(data.get('text', ''), 1000)
    if not text:
        return jsonify({'success': False, 'message': 'Text zaroori'}), 400
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO news (text, date) VALUES (?, ?)",
                   (text, datetime.now().strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': new_id})


@app.route('/api/news/<int:news_id>', methods=['DELETE'])
def delete_news(news_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM news WHERE id=?", (news_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ============================================
#   CHAT
# ============================================
@app.route('/api/chats', methods=['GET'])
def get_chats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chats ORDER BY id ASC")
    chats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(chats)


@app.route('/api/chats', methods=['POST'])
def send_chat():
    data = request.get_json() or {}
    sender = sanitize_input(data.get('sender', ''), 20)
    message = sanitize_input(data.get('message', ''), 1000)
    if not sender or not message:
        return jsonify({'success': False}), 400
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chats (sender, message, timestamp) VALUES (?, ?, ?)",
                   (sender, message, datetime.now().strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': new_id})


# ============================================
#   ADMISSION
# ============================================
@app.route('/api/admission', methods=['POST'])
def submit_admission():
    data = request.get_json() or {}
    name = sanitize_input(data.get('name', ''), 100)
    email = sanitize_input(data.get('email', ''), 100)
    phone = sanitize_input(data.get('phone', ''), 20)
    course = sanitize_input(data.get('course', ''), 100)

    if not name or not email or not phone or not course:
        return jsonify({'success': False, 'message': 'Sab fields zaroori!'}), 400
    if not validate_email(email):
        return jsonify({'success': False, 'message': 'Email sahi nahi!'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO admissions (name, email, phone, course, date) VALUES (?, ?, ?, ?, ?)",
                   (name, email, phone, course, datetime.now().strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Admission submitted successfully!'})


# ============================================
#   ATTENDANCE
# ============================================
@app.route('/api/attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json() or {}
    student = sanitize_input(data.get('student_name', ''), 100)
    if not student:
        return jsonify({'success': False}), 400
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance WHERE student_name=? AND date=?", (student, today))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Aaj ki attendance pehle se lagi hai!'})
    cursor.execute("INSERT INTO attendance (student_name, date, status) VALUES (?, ?, ?)",
                   (student, today, 'Present'))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': '✅ Attendance mark ho gayi!'})


# ============================================
#   PROGRESS
# ============================================
@app.route('/api/progress/<username>', methods=['GET'])
def get_progress(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM progress WHERE username=?", (username,))
    progress = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(progress)


@app.route('/api/progress', methods=['POST'])
def update_progress():
    data = request.get_json() or {}
    username = sanitize_input(data.get('username', ''), 50)
    course_id = data.get('course_id')
    course_title = sanitize_input(data.get('course_title', ''), 200)
    percent = data.get('progress_percent', 0)
    if not username or not course_id:
        return jsonify({'success': False}), 400
    completed = 1 if percent >= 100 else 0
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO progress (username, course_id, course_title, progress_percent, completed, last_updated)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(username, course_id) DO UPDATE SET
            progress_percent=excluded.progress_percent,
            completed=excluded.completed,
            last_updated=excluded.last_updated
    """, (username, course_id, course_title, percent, completed, datetime.now().strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ============================================
#   SECURITY APIs
# ============================================
@app.route('/api/security/blocked', methods=['GET'])
def get_blocked_ips():
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("SELECT * FROM blocked_ips WHERE blocked_until > ? ORDER BY id DESC", (now,))
    blocked = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(blocked)


@app.route('/api/security/blocked/<int:block_id>', methods=['DELETE'])
def unblock_ip(block_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM blocked_ips WHERE id=?", (block_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/security/notifications', methods=['GET'])
def get_notifications():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT 30")
    notifs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(notifs)


@app.route('/api/security/notifications/read', methods=['POST'])
def mark_notifications_read():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET is_read=1")
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/security/stats', methods=['GET'])
def get_security_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM attack_logs")
    total_attacks = cursor.fetchone()[0]
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("SELECT COUNT(*) FROM attack_logs WHERE timestamp LIKE ?", (today + '%',))
    attacks_today = cursor.fetchone()[0]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("SELECT COUNT(*) FROM blocked_ips WHERE blocked_until > ?", (now,))
    blocked_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM login_attempts WHERE success=0 AND timestamp LIKE ?", (today + '%',))
    failed_logins = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM notifications WHERE is_read=0")
    unread = cursor.fetchone()[0]
    conn.close()
    return jsonify({'total_attacks': total_attacks, 'attacks_today': attacks_today, 'blocked_ips': blocked_count, 'failed_logins_today': failed_logins, 'unread_notifications': unread})


# ============================================
#   AI CHAT
# ============================================
AI_KNOWLEDGE = [
    {'keywords': ['hello', 'hi', 'hey', 'salam', 'assalam', 'aoa'],
     'response': "Assalam-o-Alaikum! 👋 Main Questian AI hoon. Poochiye:<br>• Courses<br>• Fees<br>• Admission<br>• Software<br>• Login"},
    {'keywords': ['course', 'courses', 'classes'],
     'response': "Hamare paas 12 courses hain:<br>1. Mobile App Development<br>2. Cyber Security<br>3. Graphics Designing<br>4. Penetration Testing<br>5. Ethical Hacking<br>6. Python<br>7. AI & ML<br>8. Deep Learning<br>9. C#<br>10. C<br>11. C++<br>12. Java OOP"},
    {'keywords': ['python'],
     'response': "🐍 Python ek aasan aur powerful language hai. AI, Data Science, Web Development mein use hoti hai."},
    {'keywords': ['ai', 'machine learning', 'ml'],
     'response': "🤖 AI aur ML course computers ko smart banane ke baare mein hai."},
    {'keywords': ['cyber', 'security', 'hacking', 'ethical'],
     'response': "🔒 Cyber Security aur Ethical Hacking course systems ko secure karna sikhata hai."},
    {'keywords': ['fee', 'fees', 'paisa', 'price'],
     'response': "💰 Fees bohat affordable hai. Exact details ke liye Admission form bharein."},
    {'keywords': ['admission', 'apply', 'enroll'],
     'response': "🎓 Admission ke liye Navbar mein 'Admission' tab hai. Form bharein."},
    {'keywords': ['login', 'signup', 'account'],
     'response': "🔐 Login: student/123 ya teacher/123"},
    {'keywords': ['software', 'download'],
     'response': "💻 'Software' tab mein VS Code, XAMPP, Photoshop, Python IDLE, Kali Linux sab hain."},
    {'keywords': ['test', 'mcq', 'exam'],
     'response': "📝 Course ke andar 'Take MCQ Test' button hai."},
    {'keywords': ['chat', 'teacher', 'contact'],
     'response': "💬 Login ke baad Student Dashboard mein 'Chat with Teacher' section hai."},
    {'keywords': ['attendance', 'hazri'],
     'response': "📅 Student Dashboard mein 'Attendance' card hai. Mark Present dabayein."},
    {'keywords': ['about', 'developer', 'abdul', 'qadir'],
     'response': "👨‍💻 Developer: Abdul Qadir Soomro<br>📧 24cse23@quest.edu.pk<br>📱 03359996428<br>📍 Larkana, Pakistan"},
    {'keywords': ['help', 'madad'],
     'response': "🎯 Poochiye: courses, fees, admission, login, software, developer info"},
    {'keywords': ['thanks', 'shukriya'],
     'response': "Aapka khair maqdam! 😊"},
    {'keywords': ['bye', 'goodbye'],
     'response': "Allah Hafiz! 👋"},
]


def keyword_ai(msg):
    msg = msg.lower().strip()
    if not msg:
        return "Kuch likhein!"
    best_match = None
    best_score = 0
    for item in AI_KNOWLEDGE:
        score = 0
        for keyword in item['keywords']:
            if keyword in msg:
                score += len(keyword) * 2
                if keyword == msg:
                    score += 100
        if score > best_score:
            best_score = score
            best_match = item
    if best_match and best_score > 0:
        return best_match['response']
    return "🤔 Mujhe exact jawab nahi pata. Poochiye: courses, fees, admission, login, software — ya teacher se chat karein."


def try_gemini(prompt):
    if not gemini_client:
        return None
    for model_name in GEMINI_MODELS:
        try:
            response = gemini_client.models.generate_content(model=model_name, contents=prompt)
            if response and response.text:
                print(f"✅ Gemini response from: {model_name}")
                return response.text.strip()
        except Exception as e:
            err_str = str(e)
            if 'quota' in err_str.lower() or 'not found' in err_str.lower() or 'no longer' in err_str.lower():
                print(f"⚠️ {model_name} unavailable, trying next...")
                continue
            else:
                print(f"⚠️ {model_name} error: {err_str[:100]}")
                continue
    return None


@app.route('/api/ai', methods=['POST'])
def ai_chat():
    data = request.get_json() or {}
    msg = sanitize_input(data.get('message', ''), 500)
    if not msg:
        return jsonify({'response': 'Kuch likhein!'})
    return jsonify({'response': keyword_ai(msg)})


@app.route('/api/ai/smart', methods=['POST'])
def ai_smart():
    data = request.get_json() or {}
    msg = sanitize_input(data.get('message', ''), 500)
    if not msg:
        return jsonify({'response': 'Kuch likhein!'})

    prompt = f"""You are Questian Academy's helpful assistant.
Answer in Roman Urdu (English letters, Urdu words) - short and friendly (2-3 sentences max).

Academy info:
- 12 Courses: Mobile App Dev, Cyber Security, Graphics, Pen Testing, Ethical Hacking, Python, AI/ML, Deep Learning, C#, C, C++, Java OOP
- Features: Admission, Courses, Software, News, Login, Chat, Tests
- Demo login: student/123 or teacher/123
- Developer: Abdul Qadir Soomro (24cse23@quest.edu.pk, 03359996428, Larkana Pakistan)

Question: {msg}

Answer in Roman Urdu:"""

    gemini_response = try_gemini(prompt)
    if gemini_response:
        return jsonify({'response': gemini_response, 'source': 'gemini'})
    return jsonify({'response': keyword_ai(msg), 'source': 'keyword'})


if __name__ == '__main__':
    print("=" * 60)
    print("   🛡️  QUESTIAN ACADEMY - Backend")
    print("   Developer: Abdul Qadir Soomro")
    print("=" * 60)
    init_db()
    print("✅ Database ready!")
    print(f"🤖 Gemini: {'✅ Active' if gemini_client else '⚠️ Keyword AI only'}")
    print("🚀 Server: http://127.0.0.1:5000")
    print("=" * 60)
    if __name__ == '__main__':
         init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)