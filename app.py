"""
QUESTIAN ACADEMY - Backend
Developer: Abdul Qadir Soomro
Database: SQLite
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import re
import random
import json
import secrets
import urllib.request
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'questian-secret-2026')
CORS(app, origins=['*'])

DATABASE = 'academy.db'
BREVO_API_KEY = os.environ.get('BREVO_API_KEY')
EMAIL_USER = os.environ.get('EMAIL_USER')
SENDER_NAME = os.environ.get('SENDER_NAME', 'Questian Academy')
EMAIL_ENABLED = bool(BREVO_API_KEY and EMAIL_USER)
APPROVED_TEACHER_EMAILS = ['24cse23@quest.edu.pk']

GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
gemini_client = None
if GEMINI_KEY:
    try:
        from google import genai
        gemini_client = genai.Client(api_key=GEMINI_KEY)
        print("Gemini ready")
    except Exception as e:
        print(f"Gemini error: {str(e)[:100]}")


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
        created_at TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS otp_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL, code TEXT NOT NULL,
        purpose TEXT NOT NULL, user_data TEXT,
        expires_at TEXT, used INTEGER DEFAULT 0)''')

    c.execute('''CREATE TABLE IF NOT EXISTS password_resets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL, token TEXT NOT NULL,
        expires_at TEXT, used INTEGER DEFAULT 0)''')

    c.execute('''CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL, description TEXT, image TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS software (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, link TEXT, image TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL, date TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL, message TEXT NOT NULL, timestamp TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS admissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, email TEXT NOT NULL,
        phone TEXT NOT NULL, course TEXT NOT NULL, date TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT NOT NULL, date TEXT NOT NULL, status TEXT NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL, course_id INTEGER NOT NULL,
        course_title TEXT, progress_percent INTEGER DEFAULT 0,
        completed INTEGER DEFAULT 0, last_updated TEXT,
        UNIQUE(username, course_id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, email TEXT NOT NULL,
        subject TEXT NOT NULL, message TEXT NOT NULL, date TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_role TEXT, title TEXT NOT NULL,
        message TEXT, is_read INTEGER DEFAULT 0, timestamp TEXT)''')

    conn.commit()

    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password, role, name, email, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                  ('student', generate_password_hash('123'), 'student', 'Demo Student', 'student@demo.com', datetime.now().strftime('%Y-%m-%d %H:%M')))
        c.execute("INSERT INTO users (username, password, role, name, email, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                  ('teacher', generate_password_hash('12345678900'), 'teacher', 'Abdul Qadir Soomro', '24cse23@quest.edu.pk', datetime.now().strftime('%Y-%m-%d %H:%M')))
        c.execute("INSERT INTO users (username, password, role, name, email, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                  ('admin', generate_password_hash('admin123'), 'admin', 'Administrator', 'admin@quest.edu.pk', datetime.now().strftime('%Y-%m-%d %H:%M')))

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

    c.execute("SELECT COUNT(*) FROM news")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO news (text, date) VALUES (?, ?)",
                  ('Welcome to Questian Academy. New semester started.', datetime.now().strftime('%Y-%m-%d %H:%M')))

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


def send_otp_email(to_email, otp, purpose):
    if not EMAIL_ENABLED:
        print("Email not configured")
        return False
    subject_text = "Sign Up Verification" if purpose == 'signup' else "Login Verification"
    html = f"""<!DOCTYPE html><html><body style="font-family:Arial;background:#f4f4f7;padding:40px;">
<div style="max-width:520px;margin:auto;background:#fff;border-radius:8px;padding:35px;">
<h2 style="color:#0f172a;">Questian Academy</h2>
<p>Assalam-o-Alaikum,</p>
<p>Aapka <strong>{subject_text}</strong> code:</p>
<div style="background:#eff6ff;border:2px solid #3b82f6;border-radius:8px;padding:20px;text-align:center;margin:25px 0;">
<div style="font-size:36px;font-weight:700;letter-spacing:8px;color:#1e40af;">{otp}</div></div>
<p style="color:#6b7280;font-size:13px;">Yeh code 5 minute mein expire ho jayega.</p>
</div></body></html>"""
    try:
        payload = json.dumps({
            "sender": {"name": SENDER_NAME, "email": EMAIL_USER},
            "to": [{"email": to_email}],
            "subject": f"Questian Academy - {subject_text} Code",
            "htmlContent": html
        }).encode('utf-8')
        req = urllib.request.Request("https://api.brevo.com/v3/smtp/email",
            data=payload,
            headers={"accept": "application/json", "content-type": "application/json", "api-key": BREVO_API_KEY},
            method="POST")
        with urllib.request.urlopen(req, timeout=15) as response:
            print(f"Email sent to {to_email}")
            return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def send_reset_email(to_email, token):
    if not EMAIL_ENABLED:
        return False
    reset_link = f"https://questian-academy2-production.up.railway.app/?token={token}"
    html = f"""<!DOCTYPE html><html><body style="font-family:Arial;background:#f4f4f7;padding:40px;">
<div style="max-width:520px;margin:auto;background:#fff;border-radius:8px;padding:35px;">
<h2 style="color:#0f172a;">Questian Academy</h2>
<p>Password reset karne ke liye neeche button dabayein:</p>
<div style="text-align:center;margin:30px 0;">
<a href="{reset_link}" style="background:#3b82f6;color:#fff;padding:14px 32px;text-decoration:none;border-radius:8px;font-weight:600;">Reset Password</a></div>
<p style="color:#6b7280;font-size:13px;">Link 15 minute mein expire hoga.</p>
</div></body></html>"""
    try:
        payload = json.dumps({
            "sender": {"name": SENDER_NAME, "email": EMAIL_USER},
            "to": [{"email": to_email}],
            "subject": "Questian Academy - Password Reset",
            "htmlContent": html
        }).encode('utf-8')
        req = urllib.request.Request("https://api.brevo.com/v3/smtp/email",
            data=payload,
            headers={"accept": "application/json", "content-type": "application/json", "api-key": BREVO_API_KEY},
            method="POST")
        with urllib.request.urlopen(req, timeout=15) as response:
            return True
    except Exception as e:
        print(f"Reset email error: {e}")
        return False


def generate_otp():
    return str(random.randint(100000, 999999))


# ============ ROUTES ============
@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


# ============ SIGNUP ============
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
        return jsonify({'success': False, 'message': 'Username 3-20 chars'}), 400
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return jsonify({'success': False, 'message': 'Email sahi nahi'}), 400
    if len(password) < 3:
        return jsonify({'success': False, 'message': 'Password 3+ chars'}), 400
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

    c.execute("DELETE FROM otp_codes WHERE email=? AND purpose='signup'", (email,))
    otp = generate_otp()
    expires = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    user_data = json.dumps({'username': username, 'password': password, 'name': name, 'email': email, 'role': role})
    c.execute("INSERT INTO otp_codes (email, code, purpose, user_data, expires_at, used) VALUES (?, ?, ?, ?, ?, 0)",
              (email, otp, 'signup', user_data, expires))
    conn.commit()
    conn.close()

    if not send_otp_email(email, otp, 'signup'):
        return jsonify({'success': False, 'message': 'Email send nahi hui'}), 500
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
        return jsonify({'success': False, 'message': 'Code galat ya expire'}), 400

    user_data = json.loads(row['user_data'])
    hashed = generate_password_hash(user_data['password'])
    c.execute("INSERT INTO users (username, password, role, name, email, created_at) VALUES (?, ?, ?, ?, ?, ?)",
              (user_data['username'], hashed, user_data['role'], user_data['name'], user_data['email'],
               datetime.now().strftime('%Y-%m-%d %H:%M')))
    new_id = c.lastrowid
    c.execute("UPDATE otp_codes SET used=1 WHERE id=?", (row['id'],))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Account ban gaya',
                    'user': {'id': new_id, 'username': user_data['username'], 'role': user_data['role'],
                             'name': user_data['name'], 'email': user_data['email']}})


# ============ LOGIN ============
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
        return jsonify({'success': False, 'message': 'Account mein email nahi'}), 400

    c.execute("DELETE FROM otp_codes WHERE email=? AND purpose='login'", (email,))
    otp = generate_otp()
    expires = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO otp_codes (email, code, purpose, user_data, expires_at, used) VALUES (?, ?, ?, ?, ?, 0)",
              (email, otp, 'login', json.dumps({'user_id': user['id'], 'email': email}), expires))
    conn.commit()
    conn.close()

    if not send_otp_email(email, otp, 'login'):
        return jsonify({'success': False, 'message': 'Email send nahi hui'}), 500
    masked = email[:2] + '***' + email[email.find('@'):]
    return jsonify({'success': True, 'message': f'Code bhej diya {masked} par', 'email': email})


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
    return jsonify({'success': True,
                    'user': {'id': user['id'], 'username': user['username'], 'role': user['role'],
                             'name': user['name'], 'email': user['email']}})


# ============ FORGOT PASSWORD ============
@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    if not email:
        return jsonify({'success': False, 'message': 'Email zaroori'}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()
    if not user:
        conn.close()
        return jsonify({'success': True, 'message': 'Agar email registered hai, to link bhej diya.'})

    token = secrets.token_urlsafe(32)
    expires = (datetime.now() + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
    c.execute("DELETE FROM password_resets WHERE email=?", (email,))
    c.execute("INSERT INTO password_resets (email, token, expires_at, used) VALUES (?, ?, ?, 0)",
              (email, token, expires))
    conn.commit()
    conn.close()

    if not send_reset_email(email, token):
        return jsonify({'success': False, 'message': 'Email send nahi hui'}), 500
    return jsonify({'success': True, 'message': f'Reset link bhej diya {email} par'})


@app.route('/api/verify-reset-token', methods=['POST'])
def verify_reset_token():
    data = request.get_json() or {}
    token = (data.get('token') or '').strip()
    if not token:
        return jsonify({'success': False, 'message': 'Token zaroori'}), 400
    conn = get_db()
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("SELECT * FROM password_resets WHERE token=? AND used=0 AND expires_at > ?", (token, now))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({'success': False, 'message': 'Link galat ya expire'}), 400
    return jsonify({'success': True, 'email': row['email']})


@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    token = (data.get('token') or '').strip()
    new_password = data.get('password', '')
    if not token or not new_password:
        return jsonify({'success': False, 'message': 'Token aur password zaroori'}), 400
    if len(new_password) < 3:
        return jsonify({'success': False, 'message': 'Password 3+ chars'}), 400

    conn = get_db()
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("SELECT * FROM password_resets WHERE token=? AND used=0 AND expires_at > ?", (token, now))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({'success': False, 'message': 'Link galat ya expire'}), 400

    hashed = generate_password_hash(new_password)
    c.execute("UPDATE users SET password=? WHERE email=?", (hashed, row['email']))
    c.execute("UPDATE password_resets SET used=1 WHERE id=?", (row['id'],))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Password reset ho gaya! Ab login karein.'})


# ============ COURSES ============
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


# ============ SOFTWARE ============
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


@app.route('/api/software/<int:sid>', methods=['DELETE'])
def delete_software(sid):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM software WHERE id=?", (sid,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ============ NEWS ============
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


# ============ CHAT ============
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


# ============ ADMISSION ============
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


# ============ ATTENDANCE ============
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


# ============ PROGRESS ============
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


# ============ CONTACT ============
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


# ============ SECURITY ============
@app.route('/api/security/blocked', methods=['GET'])
def get_blocked(): return jsonify([])

@app.route('/api/security/blocked/<int:bid>', methods=['DELETE'])
def unblock(bid): return jsonify({'success': True})

@app.route('/api/security/notifications', methods=['GET'])
def get_notifs(): return jsonify([])

@app.route('/api/security/notifications/read', methods=['POST'])
def mark_read(): return jsonify({'success': True})

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
                    'failed_logins_today': 0, 'unread_notifications': 0,
                    'total_users': users, 'total_courses': courses})


# ============ AI CHAT ============
AI_KB = [
    (['hello', 'hi', 'hey', 'salam', 'assalam', 'aoa'], 'Assalam-o-Alaikum! Main Questian AI hoon. Kya madad chahiye?'),
    (['courses list', 'saare courses', 'all courses', 'kya courses', '12 courses'], 'Hamare paas 12 courses hain: Mobile App Dev, Cyber Security, Graphics, Pen Testing, Ethical Hacking, Python, AI/ML, Deep Learning, C#, C, C++, Java OOP'),
    (['python'], 'Python Language Course: Python basics, OOP, libraries, real projects. Best for beginners.'),
    (['ai', 'machine learning'], 'AI/ML Course: Supervised/Unsupervised learning, model training, real projects.'),
    (['cyber', 'security'], 'Cyber Security Course: Network security, cryptography, threats, firewalls.'),
    (['admission', 'apply'], 'Admission ke liye Navbar mein "Admission" tab hai. Form bharein.'),
    (['fee', 'fees', 'paisa'], 'Fees bohat affordable hai. Admission form bharein exact details ke liye.'),
    (['login', 'sign in'], 'Login: Username/password, phir email code.'),
    (['signup', 'register'], 'Sign Up: Login page par "Sign Up" link. Email verification zaroori hai.'),
    (['forgot password', 'password bhool'], 'Forgot Password link dabayein, email par reset link aayega.'),
    (['software', 'download'], 'Software tab: VS Code, XAMPP, Photoshop, Kali Linux, Git, Node.js, Docker.'),
    (['attendance', 'hazri'], 'Student Dashboard mein "Mark Present" button hai.'),
    (['developer', 'abdul qadir'], 'Developer: Abdul Qadir Soomro. Email: 24cse23@quest.edu.pk'),
    (['admin'], 'Admin: username "admin", password "admin123"'),
    (['help'], 'Pooch sakte hain: courses, fees, admission, login, forgot password, software.'),
    (['thanks', 'shukriya'], 'Shukriya!'),
    (['bye'], 'Allah Hafiz!'),
]


def keyword_ai(msg):
    msg = msg.lower().strip()
    if not msg: return 'Kuch likhein'
    best = None; score = 0
    for kws, resp in AI_KB:
        s = sum(len(k) * 3 for k in kws if k in msg)
        if s > score:
            score = s; best = resp
    if best: return best
    return "Mujhe exact jawab nahi mila. Poochiye: courses, fees, admission, login, forgot password, software."


@app.route('/api/ai', methods=['POST'])
def ai_chat():
    data = request.get_json() or {}
    msg = (data.get('message') or '').strip()[:500]
    if not msg: return jsonify({'response': 'Kuch likhein'})
    return jsonify({'response': keyword_ai(msg), 'source': 'keyword'})


@app.route('/api/ai/smart', methods=['POST'])
def ai_smart():
    data = request.get_json() or {}
    msg = (data.get('message') or '').strip()[:500]
    if not msg: return jsonify({'response': 'Kuch likhein'})
    if gemini_client:
        try:
            prompt = f"Answer in Roman Urdu (2-3 sentences): {msg}"
            for m in ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']:
                try:
                    r = gemini_client.models.generate_content(model=m, contents=prompt)
                    if r and r.text:
                        return jsonify({'response': r.text.strip(), 'source': 'gemini'})
                except: continue
        except: pass
    return jsonify({'response': keyword_ai(msg), 'source': 'keyword'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Email: {'Enabled' if EMAIL_ENABLED else 'Disabled'}")
    print(f"Gemini: {'Active' if gemini_client else 'Keyword only'}")
    app.run(debug=False, host='0.0.0.0', port=port)
