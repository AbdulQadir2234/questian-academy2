"""
QUESTIAN ACADEMY - Backend
Developer: Abdul Qadir Soomro
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re
import os
import random
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'questian-secret-2026')
CORS(app, origins=['*'])

# Email Config
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
EMAIL_ENABLED = bool(EMAIL_USER and EMAIL_PASS)

# Gemini
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
gemini_client = None
if GEMINI_KEY:
    try:
        from google import genai
        gemini_client = genai.Client(api_key=GEMINI_KEY)
        print("Gemini ready")
    except Exception as e:
        print(f"Gemini error: {str(e)[:100]}")

DATABASE = 'academy.db'

APPROVED_TEACHER_EMAILS = ['24cse23@quest.edu.pk']


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        name TEXT NOT NULL,
        email TEXT,
        verified INTEGER DEFAULT 1,
        created_at TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS otp_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        code TEXT NOT NULL,
        purpose TEXT NOT NULL,
        user_data TEXT,
        expires_at TEXT,
        used INTEGER DEFAULT 0)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        image TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS software (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        link TEXT,
        image TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        date TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS admissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, email TEXT NOT NULL,
        phone TEXT NOT NULL, course TEXT NOT NULL,
        date TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        course_id INTEGER NOT NULL,
        course_title TEXT,
        progress_percent INTEGER DEFAULT 0,
        completed INTEGER DEFAULT 0,
        last_updated TEXT,
        UNIQUE(username, course_id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS attack_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT NOT NULL, attack_type TEXT NOT NULL,
        details TEXT, endpoint TEXT, timestamp TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, email TEXT NOT NULL,
        subject TEXT NOT NULL, message TEXT NOT NULL,
        date TEXT)''')
    
    conn.commit()
    
    # Default users
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password, role, name, email, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                  ('student', generate_password_hash('123'), 'student', 'Demo Student', 'student@demo.com', datetime.now().strftime('%Y-%m-%d %H:%M')))
        c.execute("INSERT INTO users (username, password, role, name, email, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                  ('teacher', generate_password_hash('12345678900'), 'teacher', 'Abdul Qadir Soomro', '24cse23@quest.edu.pk', datetime.now().strftime('%Y-%m-%d %H:%M')))
    
    # Default courses
    c.execute("SELECT COUNT(*) FROM courses")
    if c.fetchone()[0] == 0:
        courses = [
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
        c.executemany("INSERT INTO courses (title, description, image) VALUES (?, ?, ?)", courses)
    
    # Default software
    c.execute("SELECT COUNT(*) FROM software")
    if c.fetchone()[0] == 0:
        sw = [
            ('VS Code', 'https://code.visualstudio.com/download', 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600'),
            ('XAMPP', 'https://www.apachefriends.org/download.html', 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=600'),
            ('Adobe Photoshop', 'https://www.adobe.com/products/photoshop.html', 'https://images.unsplash.com/photo-1626785774573-4b799315345d?w=600'),
            ('Python IDLE', 'https://www.python.org/downloads/', 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=600'),
            ('Kali Linux', 'https://www.kali.org/get-kali/', 'https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=600'),
            ('Git', 'https://git-scm.com/downloads', 'https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=600'),
            ('Node.js', 'https://nodejs.org/en/download/', 'https://images.unsplash.com/photo-1627398242454-45a1465c2479?w=600'),
            ('Docker', 'https://www.docker.com/products/docker-desktop/', 'https://images.unsplash.com/photo-1605745341112-85968b19335b?w=600')
        ]
        c.executemany("INSERT INTO software (name, link, image) VALUES (?, ?, ?)", sw)
    
    # Default news
    c.execute("SELECT COUNT(*) FROM news")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO news (text, date) VALUES (?, ?)",
                  ('Welcome to Questian Academy. New semester started.', datetime.now().strftime('%Y-%m-%d %H:%M')))
    
    # Default chat
    c.execute("SELECT COUNT(*) FROM chats")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO chats (sender, message, timestamp) VALUES (?, ?, ?)",
                  ('student', 'Sir, I have a question.', datetime.now().strftime('%Y-%m-%d %H:%M')))
        c.execute("INSERT INTO chats (sender, message, timestamp) VALUES (?, ?, ?)",
                  ('teacher', 'Yes, ask.', datetime.now().strftime('%Y-%m-%d %H:%M')))
    
    conn.commit()
    conn.close()


init_db()
print("Database initialized")


# ============================================
#   EMAIL FUNCTIONS
# ============================================

def send_otp_email(to_email, otp, purpose):
    """Send OTP via Gmail SMTP"""
    if not EMAIL_ENABLED:
        print("Email not configured")
        return False
    
    subject_text = "Sign Up Verification" if purpose == 'signup' else "Login Verification"
    
    html = f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;font-family:Arial,sans-serif;background:#f4f4f7;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f7;padding:40px 20px;">
<tr><td align="center">
<table width="520" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.05);">
<tr>
<td style="background:#1e3a8a;padding:24px 30px;">
<h2 style="color:#ffffff;margin:0;font-size:20px;font-weight:600;">Questian Academy</h2>
</td>
</tr>
<tr>
<td style="padding:35px 30px;">
<p style="color:#374151;font-size:15px;margin:0 0 20px 0;">Assalam-o-Alaikum,</p>
<p style="color:#374151;font-size:15px;margin:0 0 20px 0;">Aapka <strong>{subject_text}</strong> code:</p>
<div style="background:#f0f4ff;border:2px solid #1e3a8a;border-radius:8px;padding:20px;text-align:center;margin:25px 0;">
<div style="font-size:36px;font-weight:700;letter-spacing:8px;color:#1e3a8a;">{otp}</div>
</div>
<p style="color:#6b7280;font-size:13px;margin:0;">Yeh code <strong>5 minute</strong> mein expire ho jayega.</p>
<p style="color:#6b7280;font-size:13px;margin:20px 0 0 0;">Agar aapne yeh request nahi ki, toh email ignore karein.</p>
</td>
</tr>
<tr>
<td style="background:#f9fafb;padding:20px 30px;border-top:1px solid #e5e7eb;">
<p style="color:#9ca3af;font-size:12px;margin:0;">© 2026 Questian Academy. All rights reserved.</p>
</td>
</tr>
</table>
</td></tr>
</table>
</body>
</html>"""
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"Questian Academy <{EMAIL_USER}>"
        msg['To'] = to_email
        msg['Subject'] = f"Questian Academy - {subject_text} Code"
        msg.attach(MIMEText(html, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        print(f"OTP sent to {to_email}")
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def generate_otp():
    return str(random.randint(100000, 999999))


# ============================================
#   FRONTEND
# ============================================

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


# ============================================
#   SIGNUP WITH OTP
# ============================================

@app.route('/api/signup/send-otp', methods=['POST'])
def signup_send_otp():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()[:50]
    password = data.get('password', '')
    name = (data.get('name') or '').strip()[:100]
    email = (data.get('email') or '').strip().lower()[:100]
    role = data.get('role', 'student')
    
    if not all([username, password, name, email]):
        return jsonify({'success': False, 'message': 'Saare fields bharein'}), 400
    
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return jsonify({'success': False, 'message': 'Username 3-20 letters/numbers/underscore'}), 400
    
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return jsonify({'success': False, 'message': 'Email sahi nahi'}), 400
    
    if len(password) < 3:
        return jsonify({'success': False, 'message': 'Password 3+ characters'}), 400
    
    if role not in ['student', 'teacher']:
        role = 'student'
    
    if role == 'teacher' and email not in APPROVED_TEACHER_EMAILS:
        return jsonify({'success': False, 'message': 'Yeh email teacher ke liye approved nahi'}), 403
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Username pehle se mojood'}), 400
    
    c.execute("SELECT id FROM users WHERE email=?", (email,))
    if c.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Email pehle se registered'}), 400
    
    # Delete old pending OTPs for this email
    c.execute("DELETE FROM otp_codes WHERE email=? AND purpose='signup'", (email,))
    
    otp = generate_otp()
    expires = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    user_data = json.dumps({'username': username, 'password': password, 'name': name, 'email': email, 'role': role})
    
    c.execute("INSERT INTO otp_codes (email, code, purpose, user_data, expires_at, used) VALUES (?, ?, ?, ?, ?, 0)",
              (email, otp, 'signup', user_data, expires))
    conn.commit()
    conn.close()
    
    if not send_otp_email(email, otp, 'signup'):
        return jsonify({'success': False, 'message': 'Email send nahi hui. Config check karein.'}), 500
    
    return jsonify({'success': True, 'message': f'Code bhej diya {email} par'})


@app.route('/api/signup/verify', methods=['POST'])
def signup_verify():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    code = (data.get('code') or '').strip()
    
    if not email or not code:
        return jsonify({'success': False, 'message': 'Email aur code zaroori'}), 400
    
    conn = get_db()
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    c.execute("SELECT * FROM otp_codes WHERE email=? AND code=? AND purpose='signup' AND used=0 AND expires_at > ?",
              (email, code, now))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return jsonify({'success': False, 'message': 'Code galat ya expire ho gaya'}), 400
    
    user_data = json.loads(row['user_data'])
    
    # Check again
    c.execute("SELECT id FROM users WHERE username=?", (user_data['username'],))
    if c.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Username pehle se mojood'}), 400
    
    hashed = generate_password_hash(user_data['password'])
    c.execute("INSERT INTO users (username, password, role, name, email, created_at) VALUES (?, ?, ?, ?, ?, ?)",
              (user_data['username'], hashed, user_data['role'], user_data['name'], user_data['email'],
               datetime.now().strftime('%Y-%m-%d %H:%M')))
    
    c.execute("UPDATE otp_codes SET used=1 WHERE id=?", (row['id'],))
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'Account ban gaya',
        'user': {'id': new_id, 'username': user_data['username'], 'role': user_data['role'],
                 'name': user_data['name'], 'email': user_data['email']}
    })


# ============================================
#   LOGIN WITH OTP
# ============================================

@app.route('/api/login/send-otp', methods=['POST'])
def login_send_otp():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username aur password zaroori'}), 400
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    
    if not user or not check_password_hash(user['password'], password):
        conn.close()
        return jsonify({'success': False, 'message': 'Galat username ya password'}), 401
    
    email = user['email']
    if not email:
        conn.close()
        return jsonify({'success': False, 'message': 'Is account mein email nahi hai'}), 400
    
    c.execute("DELETE FROM otp_codes WHERE email=? AND purpose='login'", (email,))
    
    otp = generate_otp()
    expires = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    
    c.execute("INSERT INTO otp_codes (email, code, purpose, user_data, expires_at, used) VALUES (?, ?, ?, ?, ?, 0)",
              (email, otp, 'login', json.dumps({'user_id': user['id']}), expires))
    conn.commit()
    conn.close()
    
    if not send_otp_email(email, otp, 'login'):
        return jsonify({'success': False, 'message': 'Email send nahi hui'}), 500
    
    # Mask email for display
    masked = email[:2] + '***' + email[email.find('@'):]
    return jsonify({'success': True, 'message': f'Code bhej diya', 'email': masked})


@app.route('/api/login/verify', methods=['POST'])
def login_verify():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    code = (data.get('code') or '').strip()
    
    if not email or not code:
        return jsonify({'success': False, 'message': 'Email aur code zaroori'}), 400
    
    conn = get_db()
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    c.execute("SELECT * FROM otp_codes WHERE email=? AND code=? AND purpose='login' AND used=0 AND expires_at > ?",
              (email, code, now))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return jsonify({'success': False, 'message': 'Code galat ya expire'}), 400
    
    user_data = json.loads(row['user_data'])
    c.execute("SELECT * FROM users WHERE id=?", (user_data['user_id'],))
    user = c.fetchone()
    
    c.execute("UPDATE otp_codes SET used=1 WHERE id=?", (row['id'],))
    conn.commit()
    conn.close()
    
    if not user:
        return jsonify({'success': False, 'message': 'User nahi mila'}), 404
    
    return jsonify({
        'success': True,
        'user': {'id': user['id'], 'username': user['username'], 'role': user['role'],
                 'name': user['name'], 'email': user['email']}
    })


# ============================================
#   COURSES
# ============================================

@app.route('/api/courses', methods=['GET'])
def get_courses():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM courses")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route('/api/courses', methods=['POST'])
def add_course():
    data = request.get_json() or {}
    title = (data.get('title') or '').strip()[:200]
    if not title:
        return jsonify({'success': False, 'message': 'Title zaroori'}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO courses (title, description, image) VALUES (?, ?, ?)",
              (title, (data.get('description') or '')[:500], (data.get('image') or '')[:500]))
    conn.commit()
    nid = c.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': nid, 'title': title})


@app.route('/api/courses/<int:cid>', methods=['PUT'])
def update_course(cid):
    data = request.get_json() or {}
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE courses SET title=?, description=?, image=? WHERE id=?",
              ((data.get('title') or '')[:200], (data.get('description') or '')[:500],
               (data.get('image') or '')[:500], cid))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/courses/<int:cid>', methods=['DELETE'])
def delete_course(cid):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM courses WHERE id=?", (cid,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ============================================
#   SOFTWARE
# ============================================

@app.route('/api/software', methods=['GET'])
def get_software():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM software")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route('/api/software', methods=['POST'])
def add_software():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()[:100]
    if not name:
        return jsonify({'success': False, 'message': 'Name zaroori'}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO software (name, link, image) VALUES (?, ?, ?)",
              (name, (data.get('link') or '#')[:500], (data.get('image') or '')[:500]))
    conn.commit()
    nid = c.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': nid})


@app.route('/api/software/<int:sid>', methods=['PUT'])
def update_software(sid):
    data = request.get_json() or {}
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE software SET name=?, link=?, image=? WHERE id=?",
              ((data.get('name') or '')[:100], (data.get('link') or '')[:500],
               (data.get('image') or '')[:500], sid))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/software/<int:sid>', methods=['DELETE'])
def delete_software(sid):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM software WHERE id=?", (sid,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ============================================
#   NEWS
# ============================================

@app.route('/api/news', methods=['GET'])
def get_news():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM news ORDER BY id DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route('/api/news', methods=['POST'])
def add_news():
    data = request.get_json() or {}
    text = (data.get('text') or '').strip()[:1000]
    if not text:
        return jsonify({'success': False, 'message': 'Text zaroori'}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO news (text, date) VALUES (?, ?)",
              (text, datetime.now().strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    nid = c.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': nid})


@app.route('/api/news/<int:nid>', methods=['DELETE'])
def delete_news(nid):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM news WHERE id=?", (nid,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ============================================
#   CHAT
# ============================================

@app.route('/api/chats', methods=['GET'])
def get_chats():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM chats ORDER BY id ASC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route('/api/chats', methods=['POST'])
def send_chat():
    data = request.get_json() or {}
    sender = (data.get('sender') or '')[:20]
    message = (data.get('message') or '')[:1000]
    if not sender or not message:
        return jsonify({'success': False}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO chats (sender, message, timestamp) VALUES (?, ?, ?)",
              (sender, message, datetime.now().strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    nid = c.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': nid})


# ============================================
#   ADMISSION
# ============================================

@app.route('/api/admission', methods=['POST'])
def submit_admission():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()[:100]
    email = (data.get('email') or '').strip()[:100]
    phone = (data.get('phone') or '').strip()[:20]
    course = (data.get('course') or '').strip()[:100]
    
    if not all([name, email, phone, course]):
        return jsonify({'success': False, 'message': 'Saare fields zaroori'}), 400
    
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO admissions (name, email, phone, course, date) VALUES (?, ?, ?, ?, ?)",
              (name, email, phone, course, datetime.now().strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Admission submit ho gaya'})


# ============================================
#   ATTENDANCE
# ============================================

@app.route('/api/attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json() or {}
    student = (data.get('student_name') or '').strip()[:100]
    if not student:
        return jsonify({'success': False}), 400
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM attendance WHERE student_name=? AND date=?", (student, today))
    if c.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Aaj ki attendance lagi hui hai'})
    c.execute("INSERT INTO attendance (student_name, date, status) VALUES (?, ?, ?)",
              (student, today, 'Present'))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Attendance mark ho gayi'})


# ============================================
#   PROGRESS
# ============================================

@app.route('/api/progress/<username>', methods=['GET'])
def get_progress(username):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM progress WHERE username=?", (username,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route('/api/progress', methods=['POST'])
def update_progress():
    data = request.get_json() or {}
    username = (data.get('username') or '')[:50]
    course_id = data.get('course_id')
    course_title = (data.get('course_title') or '')[:200]
    percent = data.get('progress_percent', 0)
    if not username or not course_id:
        return jsonify({'success': False}), 400
    completed = 1 if percent >= 100 else 0
    conn = get_db()
    c = conn.cursor()
    c.execute("""INSERT INTO progress (username, course_id, course_title, progress_percent, completed, last_updated)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(username, course_id) DO UPDATE SET
        progress_percent=excluded.progress_percent,
        completed=excluded.completed,
        last_updated=excluded.last_updated""",
              (username, course_id, course_title, percent, completed, datetime.now().strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ============================================
#   CONTACT
# ============================================

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()[:100]
    email = (data.get('email') or '').strip()[:100]
    subject = (data.get('subject') or '').strip()[:200]
    message = (data.get('message') or '').strip()[:2000]
    if not all([name, email, subject, message]):
        return jsonify({'success': False, 'message': 'Saare fields bharein'}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO contacts (name, email, subject, message, date) VALUES (?, ?, ?, ?, ?)",
              (name, email, subject, message, datetime.now().strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Message bhej diya'})
    

# ============================================
#   SECURITY APIs
# ============================================

@app.route('/api/security/blocked', methods=['GET'])
def get_blocked():
    return jsonify([])

@app.route('/api/security/blocked/<int:bid>', methods=['DELETE'])
def unblock(bid):
    return jsonify({'success': True})

@app.route('/api/security/notifications', methods=['GET'])
def get_notifs():
    return jsonify([])

@app.route('/api/security/notifications/read', methods=['POST'])
def mark_read():
    return jsonify({'success': True})

@app.route('/api/security/stats', methods=['GET'])
def sec_stats():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM courses")
    courses = c.fetchone()[0]
    conn.close()
    return jsonify({'total_attacks': 0, 'attacks_today': 0, 'blocked_ips': 0,
                    'failed_logins_today': 0, 'unread_notifications': 0, 'total_users': users})


# ============================================
#   AI CHAT
# ============================================

AI_KB = [
    (['hello', 'hi', 'salam', 'assalam'], 'Assalam-o-Alaikum. Main Questian AI hoon. Kya madad chahiye?'),
    (['course', 'courses'], '12 courses: Mobile App Dev, Cyber Security, Graphics, Pen Testing, Ethical Hacking, Python, AI/ML, Deep Learning, C#, C, C++, Java OOP'),
    (['python'], 'Python ek aasan language hai. AI, Data Science, Web Development mein use hoti hai.'),
    (['ai', 'machine learning'], 'AI aur ML course computers ko smart banane ke baare mein hai.'),
    (['cyber', 'security', 'hacking'], 'Cyber Security aur Ethical Hacking course systems ko secure karna sikhata hai.'),
    (['fee', 'fees', 'paisa'], 'Fees affordable hai. Admission form bharein ya teacher se poochein.'),
    (['admission', 'apply'], 'Admission ke liye navbar mein "Admission" tab hai. Form bharein.'),
    (['login', 'signup'], 'Login ke liye username/password, phir email code. Naya account ke liye Sign Up.'),
    (['software', 'download'], 'Software tab mein VS Code, XAMPP, Photoshop, Python IDLE, Kali Linux, Git, Node.js, Docker sab hain.'),
    (['attendance', 'hazri'], 'Student Dashboard mein Attendance card hai. Mark Present dabayein.'),
    (['developer', 'abdul'], 'Developer: Abdul Qadir Soomro. Email: 24cse23@quest.edu.pk, Phone: 03359996428'),
    (['help', 'madad'], 'Pooch sakte hain: courses, fees, admission, login, software, attendance.'),
    (['thanks', 'shukriya'], 'Shukriya!'),
    (['bye'], 'Allah Hafiz!'),
]


@app.route('/api/ai', methods=['POST'])
def ai_chat():
    data = request.get_json() or {}
    msg = (data.get('message') or '').lower().strip()
    if not msg:
        return jsonify({'response': 'Kuch likhein'})
    
    best = None
    score = 0
    for kws, resp in AI_KB:
        s = sum(len(k) * 2 for k in kws if k in msg)
        if s > score:
            score = s
            best = resp
    
    if best:
        return jsonify({'response': best, 'source': 'keyword'})
    return jsonify({'response': 'Mujhe exact jawab nahi pata. Courses, fees, admission ke baare mein pooch sakte hain.', 'source': 'keyword'})


@app.route('/api/ai/smart', methods=['POST'])
def ai_smart():
    return ai_chat()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting on port {port}")
    print(f"Email: {'Enabled' if EMAIL_ENABLED else 'Disabled'}")
    app.run(debug=False, host='0.0.0.0', port=port)