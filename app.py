"""
QUESTIAN ACADEMY - Backend
Developer: Abdul Qadir Soomro
Database: PostgreSQL (Railway) / SQLite (Local)
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
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

# ============================================
#   DATABASE - PostgreSQL / SQLite
# ============================================
DATABASE_URL = os.environ.get('DATABASE_URL')
USE_POSTGRES = bool(DATABASE_URL)

if USE_POSTGRES:
    import psycopg
    import psycopg.rows
    print("Using PostgreSQL (psycopg3)")
else:
    import sqlite3
    print("Using SQLite (local)")


class DB:
    def __init__(self):
        if USE_POSTGRES:
            self.conn = psycopg.connect(DATABASE_URL)
            self.cur = self.conn.cursor(row_factory=psycopg.rows.dict_row)
        else:
            self.conn = sqlite3.connect('academy.db')
            self.conn.row_factory = sqlite3.Row
            self.cur = self.conn.cursor()

        def execute(self, query, params=None):
         if USE_POSTGRES:
               query = query.replace('?', '%s')
        if params:
            self.cur.execute(query, params)
        else:
            self.cur.execute(query)
        return self.cur

    def fetchone(self):
        row = self.cur.fetchone()
        if row is None:
            return None
        return dict(row)

    def fetchall(self):
        return [dict(r) for r in self.cur.fetchall()]

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()

    def lastrowid(self):
        if USE_POSTGRES:
            self.cur.execute("SELECT lastval()")
            return self.cur.fetchone()['lastval']
        return self.cur.lastrowid


def get_db():
    return DB()


def init_db():
    db = get_db()
    
    # Users
    if USE_POSTGRES:
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            verified INTEGER DEFAULT 1,
            created_at TEXT)''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS otp_codes (
            id SERIAL PRIMARY KEY,
            email TEXT NOT NULL,
            code TEXT NOT NULL,
            purpose TEXT NOT NULL,
            user_data TEXT,
            expires_at TEXT,
            used INTEGER DEFAULT 0)''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS password_resets (
            id SERIAL PRIMARY KEY,
            email TEXT NOT NULL,
            token TEXT NOT NULL,
            expires_at TEXT,
            used INTEGER DEFAULT 0)''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS courses (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            image TEXT)''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS software (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            link TEXT,
            image TEXT)''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS news (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            date TEXT)''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS chats (
            id SERIAL PRIMARY KEY,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT)''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS admissions (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL, email TEXT NOT NULL,
            phone TEXT NOT NULL, course TEXT NOT NULL,
            date TEXT)''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS attendance (
            id SERIAL PRIMARY KEY,
            student_name TEXT NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL)''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS progress (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            course_id INTEGER NOT NULL,
            course_title TEXT,
            progress_percent INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0,
            last_updated TEXT,
            video_seconds INTEGER DEFAULT 0,
            UNIQUE(username, course_id))''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL, email TEXT NOT NULL,
            subject TEXT NOT NULL, message TEXT NOT NULL,
            date TEXT)''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS notifications (
            id SERIAL PRIMARY KEY,
            user_role TEXT,
            title TEXT NOT NULL,
            message TEXT,
            is_read INTEGER DEFAULT 0,
            timestamp TEXT)''')
    else:
        # SQLite
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            verified INTEGER DEFAULT 1,
            created_at TEXT)''')
        db.execute('''CREATE TABLE IF NOT EXISTS otp_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL, code TEXT NOT NULL,
            purpose TEXT NOT NULL, user_data TEXT,
            expires_at TEXT, used INTEGER DEFAULT 0)''')
        db.execute('''CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL, token TEXT NOT NULL,
            expires_at TEXT, used INTEGER DEFAULT 0)''')
        db.execute('''CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, description TEXT, image TEXT)''')
        db.execute('''CREATE TABLE IF NOT EXISTS software (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, link TEXT, image TEXT)''')
        db.execute('''CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL, date TEXT)''')
        db.execute('''CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL, message TEXT NOT NULL, timestamp TEXT)''')
        db.execute('''CREATE TABLE IF NOT EXISTS admissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT NOT NULL,
            phone TEXT NOT NULL, course TEXT NOT NULL, date TEXT)''')
        db.execute('''CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL, date TEXT NOT NULL, status TEXT NOT NULL)''')
        db.execute('''CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL, course_id INTEGER NOT NULL,
            course_title TEXT, progress_percent INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0, last_updated TEXT,
            video_seconds INTEGER DEFAULT 0,
            UNIQUE(username, course_id))''')
        db.execute('''CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT NOT NULL,
            subject TEXT NOT NULL, message TEXT NOT NULL, date TEXT)''')
        db.execute('''CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_role TEXT, title TEXT NOT NULL,
            message TEXT, is_read INTEGER DEFAULT 0, timestamp TEXT)''')
    
    db.commit()
    
    # Default users
    db.execute("SELECT COUNT(*) as count FROM users")
    row = db.fetchone()
    if row['count'] == 0:
        db.execute("INSERT INTO users (username, password, role, name, email, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                   ('student', generate_password_hash('123'), 'student', 'Demo Student', 'student@demo.com', datetime.now().strftime('%Y-%m-%d %H:%M')))
        db.execute("INSERT INTO users (username, password, role, name, email, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                   ('teacher', generate_password_hash('12345678900'), 'teacher', 'Abdul Qadir Soomro', '24cse23@quest.edu.pk', datetime.now().strftime('%Y-%m-%d %H:%M')))
        db.execute("INSERT INTO users (username, password, role, name, email, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                   ('admin', generate_password_hash('admin123'), 'admin', 'Administrator', 'admin@quest.edu.pk', datetime.now().strftime('%Y-%m-%d %H:%M')))
    
    # Default courses
    db.execute("SELECT COUNT(*) as count FROM courses")
    if db.fetchone()['count'] == 0:
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
        for c in courses:
            db.execute("INSERT INTO courses (title, description, image) VALUES (?, ?, ?)", c)
    
    # Default software
    db.execute("SELECT COUNT(*) as count FROM software")
    if db.fetchone()['count'] == 0:
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
        for s in sw:
            db.execute("INSERT INTO software (name, link, image) VALUES (?, ?, ?)", s)
    
    db.execute("SELECT COUNT(*) as count FROM news")
    if db.fetchone()['count'] == 0:
        db.execute("INSERT INTO news (text, date) VALUES (?, ?)",
                   ('Welcome to Questian Academy. New semester started.', datetime.now().strftime('%Y-%m-%d %H:%M')))
    
    db.execute("SELECT COUNT(*) as count FROM chats")
    if db.fetchone()['count'] == 0:
        db.execute("INSERT INTO chats (sender, message, timestamp) VALUES (?, ?, ?)",
                   ('student', 'Sir, I have a question.', datetime.now().strftime('%Y-%m-%d %H:%M')))
        db.execute("INSERT INTO chats (sender, message, timestamp) VALUES (?, ?, ?)",
                   ('teacher', 'Yes, ask.', datetime.now().strftime('%Y-%m-%d %H:%M')))
    
    db.commit()
    db.close()


init_db()
print("Database initialized")

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


# ============ EMAIL ============
def _send_brevo(to_email, subject, html):
    if not EMAIL_ENABLED:
        print("Email not configured")
        return False
    try:
        payload = json.dumps({
            "sender": {"name": SENDER_NAME, "email": EMAIL_USER},
            "to": [{"email": to_email}],
            "subject": subject,
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


def send_otp_email(to_email, otp, purpose):
    subject_text = "Sign Up Verification" if purpose == 'signup' else "Login Verification"
    html = f"""<!DOCTYPE html><html><body style="margin:0;padding:0;font-family:Arial,sans-serif;background:#f4f4f7;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f7;padding:40px 20px;"><tr><td align="center">
<table width="520" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;border:1px solid #e5e7eb;">
<tr><td style="background:#0f172a;padding:24px 30px;"><h2 style="color:#ffffff;margin:0;font-size:20px;">Questian Academy</h2></td></tr>
<tr><td style="padding:35px 30px;"><p style="color:#374151;font-size:15px;margin:0 0 20px 0;">Assalam-o-Alaikum,</p>
<p style="color:#374151;font-size:15px;margin:0 0 20px 0;">Aapka <strong>{subject_text}</strong> code:</p>
<div style="background:#eff6ff;border:2px solid #3b82f6;border-radius:8px;padding:20px;text-align:center;margin:25px 0;">
<div style="font-size:36px;font-weight:700;letter-spacing:8px;color:#1e40af;">{otp}</div></div>
<p style="color:#6b7280;font-size:13px;margin:0;">Yeh code <strong>5 minute</strong> mein expire ho jayega.</p>
</td></tr>
<tr><td style="background:#f9fafb;padding:20px 30px;border-top:1px solid #e5e7eb;"><p style="color:#9ca3af;font-size:12px;margin:0;">2026 Questian Academy. All rights reserved.</p></td></tr>
</table></td></tr></table></body></html>"""
    return _send_brevo(to_email, f"Questian Academy - {subject_text} Code", html)


def send_reset_email(to_email, token):
    reset_link = f"https://questian-academy2-production.up.railway.app/?token={token}"
    html = f"""<!DOCTYPE html><html><body style="margin:0;padding:0;font-family:Arial,sans-serif;background:#f4f4f7;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f7;padding:40px 20px;"><tr><td align="center">
<table width="520" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;border:1px solid #e5e7eb;">
<tr><td style="background:#0f172a;padding:24px 30px;"><h2 style="color:#ffffff;margin:0;font-size:20px;">Questian Academy</h2></td></tr>
<tr><td style="padding:35px 30px;"><p style="color:#374151;font-size:15px;">Assalam-o-Alaikum,</p>
<p style="color:#374151;font-size:15px;">Password reset karne ke liye neeche button dabayein:</p>
<div style="text-align:center;margin:30px 0;">
<a href="{reset_link}" style="background:#3b82f6;color:#ffffff;padding:14px 32px;text-decoration:none;border-radius:8px;font-weight:600;display:inline-block;">Reset Password</a></div>
<p style="color:#6b7280;font-size:13px;">Yeh link <strong>15 minute</strong> mein expire ho jayega.</p>
</td></tr>
<tr><td style="background:#f9fafb;padding:20px 30px;border-top:1px solid #e5e7eb;"><p style="color:#9ca3af;font-size:12px;margin:0;">2026 Questian Academy. All rights reserved.</p></td></tr>
</table></td></tr></table></body></html>"""
    return _send_brevo(to_email, "Questian Academy - Password Reset", html)


def generate_otp():
    return str(random.randint(100000, 999999))


def push_notification(user_role, title, message):
    """Add notification for a role (student/teacher/admin/all)"""
    try:
        db = get_db()
        db.execute("INSERT INTO notifications (user_role, title, message, is_read, timestamp) VALUES (?, ?, ?, 0, ?)",
                   (user_role, title, message, datetime.now().strftime('%Y-%m-%d %H:%M')))
        db.commit()
        db.close()
    except Exception as e:
        print(f"Notification error: {e}")


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
    
    db = get_db()
    db.execute("SELECT id FROM users WHERE username=?", (username,))
    if db.fetchone():
        db.close()
        return jsonify({'success': False, 'message': 'Username pehle se mojood'}), 400
    db.execute("SELECT id FROM users WHERE email=?", (email,))
    if db.fetchone():
        db.close()
        return jsonify({'success': False, 'message': 'Email pehle se registered'}), 400
    
    db.execute("DELETE FROM otp_codes WHERE email=? AND purpose='signup'", (email,))
    otp = generate_otp()
    expires = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    user_data = json.dumps({'username': username, 'password': password, 'name': name, 'email': email, 'role': role})
    db.execute("INSERT INTO otp_codes (email, code, purpose, user_data, expires_at, used) VALUES (?, ?, ?, ?, ?, 0)",
               (email, otp, 'signup', user_data, expires))
    db.commit()
    db.close()
    
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
    
    db = get_db()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.execute("SELECT * FROM otp_codes WHERE email=? AND code=? AND purpose='signup' AND used=0 AND expires_at > ?",
               (email, code, now))
    row = db.fetchone()
    if not row:
        db.close()
        return jsonify({'success': False, 'message': 'Code galat ya expire'}), 400
    
    user_data = json.loads(row['user_data'])
    hashed = generate_password_hash(user_data['password'])
    db.execute("INSERT INTO users (username, password, role, name, email, created_at) VALUES (?, ?, ?, ?, ?, ?)",
               (user_data['username'], hashed, user_data['role'], user_data['name'], user_data['email'],
                datetime.now().strftime('%Y-%m-%d %H:%M')))
    new_id = db.lastrowid()
    db.execute("UPDATE otp_codes SET used=1 WHERE id=?", (row['id'],))
    db.commit()
    db.close()
    
    # Notification for admin/teacher
    push_notification('admin', 'New User Registered', f'{user_data["name"]} ({user_data["role"]}) ne signup kiya')
    
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
    
    db = get_db()
    db.execute("SELECT * FROM users WHERE username=?", (username,))
    user = db.fetchone()
    if not user or not check_password_hash(user['password'], password):
        db.close()
        return jsonify({'success': False, 'message': 'Galat username ya password'}), 401
    
    email = user['email']
    if not email:
        db.close()
        return jsonify({'success': False, 'message': 'Account mein email nahi'}), 400
    
    db.execute("DELETE FROM otp_codes WHERE email=? AND purpose='login'", (email,))
    otp = generate_otp()
    expires = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    db.execute("INSERT INTO otp_codes (email, code, purpose, user_data, expires_at, used) VALUES (?, ?, ?, ?, ?, 0)",
               (email, otp, 'login', json.dumps({'user_id': user['id'], 'email': email}), expires))
    db.commit()
    db.close()
    
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
    
    db = get_db()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.execute("SELECT * FROM otp_codes WHERE email=? AND code=? AND purpose='login' AND used=0 AND expires_at > ?",
               (email, code, now))
    row = db.fetchone()
    if not row:
        db.close()
        return jsonify({'success': False, 'message': 'Code galat ya expire'}), 400
    
    user_data = json.loads(row['user_data'])
    db.execute("SELECT * FROM users WHERE id=?", (user_data['user_id'],))
    user = db.fetchone()
    db.execute("UPDATE otp_codes SET used=1 WHERE id=?", (row['id'],))
    db.commit()
    db.close()
    
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
    
    db = get_db()
    db.execute("SELECT * FROM users WHERE email=?", (email,))
    user = db.fetchone()
    if not user:
        db.close()
        return jsonify({'success': True, 'message': 'Agar email registered hai, to link bhej diya.'})
    
    token = secrets.token_urlsafe(32)
    expires = (datetime.now() + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
    db.execute("DELETE FROM password_resets WHERE email=?", (email,))
    db.execute("INSERT INTO password_resets (email, token, expires_at, used) VALUES (?, ?, ?, 0)",
               (email, token, expires))
    db.commit()
    db.close()
    
    if not send_reset_email(email, token):
        return jsonify({'success': False, 'message': 'Email send nahi hui'}), 500
    masked = email[:2] + '***' + email[email.find('@'):]
    return jsonify({'success': True, 'message': f'Reset link bhej diya {masked} par'})


@app.route('/api/verify-reset-token', methods=['POST'])
def verify_reset_token():
    data = request.get_json() or {}
    token = (data.get('token') or '').strip()
    if not token:
        return jsonify({'success': False, 'message': 'Token zaroori'}), 400
    db = get_db()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.execute("SELECT * FROM password_resets WHERE token=? AND used=0 AND expires_at > ?", (token, now))
    row = db.fetchone()
    db.close()
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
    
    db = get_db()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.execute("SELECT * FROM password_resets WHERE token=? AND used=0 AND expires_at > ?", (token, now))
    row = db.fetchone()
    if not row:
        db.close()
        return jsonify({'success': False, 'message': 'Link galat ya expire'}), 400
    
    hashed = generate_password_hash(new_password)
    db.execute("UPDATE users SET password=? WHERE email=?", (hashed, row['email']))
    db.execute("UPDATE password_resets SET used=1 WHERE id=?", (row['id'],))
    db.commit()
    db.close()
    return jsonify({'success': True, 'message': 'Password reset ho gaya! Ab login karein.'})


# ============ COURSES ============
@app.route('/api/courses', methods=['GET'])
def get_courses():
    db = get_db()
    db.execute("SELECT * FROM courses")
    rows = db.fetchall()
    db.close()
    return jsonify(rows)


@app.route('/api/courses', methods=['POST'])
def add_course():
    data = request.get_json() or {}
    title = (data.get('title') or '').strip()[:200]
    if not title:
        return jsonify({'success': False, 'message': 'Title zaroori'}), 400
    db = get_db()
    db.execute("INSERT INTO courses (title, description, image) VALUES (?, ?, ?)",
               (title, (data.get('description') or '')[:500], (data.get('image') or '')[:500]))
    db.commit()
    nid = db.lastrowid()
    db.close()
    push_notification('all', 'New Course Added', f'{title} add kiya gaya')
    return jsonify({'success': True, 'id': nid, 'title': title})


@app.route('/api/courses/<int:cid>', methods=['PUT'])
def update_course(cid):
    data = request.get_json() or {}
    db = get_db()
    db.execute("UPDATE courses SET title=?, description=?, image=? WHERE id=?",
               ((data.get('title') or '')[:200], (data.get('description') or '')[:500],
                (data.get('image') or '')[:500], cid))
    db.commit()
    db.close()
    return jsonify({'success': True})


@app.route('/api/courses/<int:cid>', methods=['DELETE'])
def delete_course(cid):
    db = get_db()
    db.execute("DELETE FROM courses WHERE id=?", (cid,))
    db.commit()
    db.close()
    return jsonify({'success': True})


# ============ SOFTWARE ============
@app.route('/api/software', methods=['GET'])
def get_software():
    db = get_db()
    db.execute("SELECT * FROM software")
    rows = db.fetchall()
    db.close()
    return jsonify(rows)


@app.route('/api/software', methods=['POST'])
def add_software():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()[:100]
    if not name:
        return jsonify({'success': False, 'message': 'Name zaroori'}), 400
    db = get_db()
    db.execute("INSERT INTO software (name, link, image) VALUES (?, ?, ?)",
               (name, (data.get('link') or '#')[:500], (data.get('image') or '')[:500]))
    db.commit()
    nid = db.lastrowid()
    db.close()
    return jsonify({'success': True, 'id': nid})


@app.route('/api/software/<int:sid>', methods=['DELETE'])
def delete_software(sid):
    db = get_db()
    db.execute("DELETE FROM software WHERE id=?", (sid,))
    db.commit()
    db.close()
    return jsonify({'success': True})


# ============ NEWS ============
@app.route('/api/news', methods=['GET'])
def get_news():
    db = get_db()
    db.execute("SELECT * FROM news ORDER BY id DESC")
    rows = db.fetchall()
    db.close()
    return jsonify(rows)


@app.route('/api/news', methods=['POST'])
def add_news():
    data = request.get_json() or {}
    text = (data.get('text') or '').strip()[:1000]
    if not text:
        return jsonify({'success': False, 'message': 'Text zaroori'}), 400
    db = get_db()
    db.execute("INSERT INTO news (text, date) VALUES (?, ?)",
               (text, datetime.now().strftime('%Y-%m-%d %H:%M')))
    db.commit()
    nid = db.lastrowid()
    db.close()
    push_notification('all', 'New Announcement', text[:100])
    return jsonify({'success': True, 'id': nid})


@app.route('/api/news/<int:nid>', methods=['DELETE'])
def delete_news(nid):
    db = get_db()
    db.execute("DELETE FROM news WHERE id=?", (nid,))
    db.commit()
    db.close()
    return jsonify({'success': True})


# ============ CHAT ============
@app.route('/api/chats', methods=['GET'])
def get_chats():
    db = get_db()
    db.execute("SELECT * FROM chats ORDER BY id ASC")
    rows = db.fetchall()
    db.close()
    return jsonify(rows)


@app.route('/api/chats', methods=['POST'])
def send_chat():
    data = request.get_json() or {}
    sender = (data.get('sender') or '')[:20]
    message = (data.get('message') or '')[:1000]
    if not sender or not message:
        return jsonify({'success': False}), 400
    db = get_db()
    db.execute("INSERT INTO chats (sender, message, timestamp) VALUES (?, ?, ?)",
               (sender, message, datetime.now().strftime('%Y-%m-%d %H:%M')))
    db.commit()
    nid = db.lastrowid()
    db.close()
    # Notify opposite role
    if sender == 'student':
        push_notification('teacher', 'New Student Message', message[:80])
    else:
        push_notification('student', 'Teacher Replied', message[:80])
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
    db = get_db()
    db.execute("INSERT INTO admissions (name, email, phone, course, date) VALUES (?, ?, ?, ?, ?)",
               (name, email, phone, course, datetime.now().strftime('%Y-%m-%d %H:%M')))
    db.commit()
    db.close()
    push_notification('teacher', 'New Admission Form', f'{name} ne {course} ke liye apply kiya')
    return jsonify({'success': True, 'message': 'Admission submit ho gaya'})


# ============ ATTENDANCE ============
@app.route('/api/attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json() or {}
    student = (data.get('student_name') or '').strip()[:100]
    if not student:
        return jsonify({'success': False}), 400
    today = datetime.now().strftime('%Y-%m-%d')
    db = get_db()
    db.execute("SELECT id FROM attendance WHERE student_name=? AND date=?", (student, today))
    if db.fetchone():
        db.close()
        return jsonify({'success': False, 'message': 'Aaj ki attendance lagi hui hai'})
    db.execute("INSERT INTO attendance (student_name, date, status) VALUES (?, ?, ?)",
               (student, today, 'Present'))
    db.commit()
    db.close()
    return jsonify({'success': True, 'message': 'Attendance mark ho gayi'})


# ============ PROGRESS (with video seconds) ============
@app.route('/api/progress/<username>', methods=['GET'])
def get_progress(username):
    db = get_db()
    db.execute("SELECT * FROM progress WHERE username=?", (username,))
    rows = db.fetchall()
    db.close()
    return jsonify(rows)


@app.route('/api/progress', methods=['POST'])
def update_progress():
    data = request.get_json() or {}
    username = (data.get('username') or '')[:50]
    course_id = data.get('course_id')
    course_title = (data.get('course_title') or '')[:200]
    percent = data.get('progress_percent', 0)
    video_seconds = data.get('video_seconds', 0)
    if not username or not course_id:
        return jsonify({'success': False}), 400
    completed = 1 if percent >= 100 else 0
    
    db = get_db()
    if USE_POSTGRES:
        db.execute("""INSERT INTO progress (username, course_id, course_title, progress_percent, completed, last_updated, video_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(username, course_id) DO UPDATE SET
            progress_percent=EXCLUDED.progress_percent,
            completed=EXCLUDED.completed,
            last_updated=EXCLUDED.last_updated,
            video_seconds=GREATEST(progress.video_seconds, EXCLUDED.video_seconds)""",
            (username, course_id, course_title, percent, completed,
             datetime.now().strftime('%Y-%m-%d %H:%M'), video_seconds))
    else:
        db.execute("""INSERT INTO progress (username, course_id, course_title, progress_percent, completed, last_updated, video_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(username, course_id) DO UPDATE SET
            progress_percent=excluded.progress_percent,
            completed=excluded.completed,
            last_updated=excluded.last_updated,
            video_seconds=MAX(progress.video_seconds, excluded.video_seconds)""",
            (username, course_id, course_title, percent, completed,
             datetime.now().strftime('%Y-%m-%d %H:%M'), video_seconds))
    db.commit()
    db.close()
    return jsonify({'success': True})


# ============ NOTIFICATIONS ============
@app.route('/api/notifications/<role>', methods=['GET'])
def get_notifications(role):
    db = get_db()
    db.execute("SELECT * FROM notifications WHERE user_role=? OR user_role='all' ORDER BY id DESC LIMIT 30", (role,))
    rows = db.fetchall()
    db.close()
    return jsonify(rows)


@app.route('/api/notifications/<int:nid>/read', methods=['POST'])
def mark_notification_read(nid):
    db = get_db()
    db.execute("UPDATE notifications SET is_read=1 WHERE id=?", (nid,))
    db.commit()
    db.close()
    return jsonify({'success': True})


@app.route('/api/notifications/<role>/read-all', methods=['POST'])
def mark_all_read(role):
    db = get_db()
    db.execute("UPDATE notifications SET is_read=1 WHERE user_role=? OR user_role='all'", (role,))
    db.commit()
    db.close()
    return jsonify({'success': True})


@app.route('/api/notifications/<role>/unread-count', methods=['GET'])
def unread_count(role):
    db = get_db()
    db.execute("SELECT COUNT(*) as c FROM notifications WHERE (user_role=? OR user_role='all') AND is_read=0", (role,))
    count = db.fetchone()['c']
    db.close()
    return jsonify({'count': count})


# ============ ADMIN DASHBOARD ============
@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    db = get_db()
    db.execute("SELECT COUNT(*) as c FROM users")
    total_users = db.fetchone()['c']
    db.execute("SELECT COUNT(*) as c FROM users WHERE role='student'")
    students = db.fetchone()['c']
    db.execute("SELECT COUNT(*) as c FROM users WHERE role='teacher'")
    teachers = db.fetchone()['c']
    db.execute("SELECT COUNT(*) as c FROM courses")
    courses = db.fetchone()['c']
    db.execute("SELECT COUNT(*) as c FROM admissions")
    admissions = db.fetchone()['c']
    db.execute("SELECT COUNT(*) as c FROM contacts")
    contacts = db.fetchone()['c']
    db.close()
    return jsonify({'total_users': total_users, 'students': students, 'teachers': teachers,
                    'courses': courses, 'admissions': admissions, 'contacts': contacts})


@app.route('/api/admin/users', methods=['GET'])
def admin_users():
    db = get_db()
    db.execute("SELECT id, username, name, email, role, created_at FROM users ORDER BY id DESC")
    rows = db.fetchall()
    db.close()
    return jsonify(rows)


@app.route('/api/admin/users/<int:uid>', methods=['DELETE'])
def admin_delete_user(uid):
    db = get_db()
    db.execute("SELECT username FROM users WHERE id=?", (uid,))
    row = db.fetchone()
    if row and row['username'] == 'admin':
        db.close()
        return jsonify({'success': False, 'message': 'Admin delete nahi ho sakta'}), 400
    db.execute("DELETE FROM users WHERE id=?", (uid,))
    db.commit()
    db.close()
    return jsonify({'success': True})


@app.route('/api/admin/admissions', methods=['GET'])
def admin_admissions():
    db = get_db()
    db.execute("SELECT * FROM admissions ORDER BY id DESC")
    rows = db.fetchall()
    db.close()
    return jsonify(rows)


@app.route('/api/admin/contacts', methods=['GET'])
def admin_contacts():
    db = get_db()
    db.execute("SELECT * FROM contacts ORDER BY id DESC")
    rows = db.fetchall()
    db.close()
    return jsonify(rows)


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
    db = get_db()
    db.execute("INSERT INTO contacts (name, email, subject, message, date) VALUES (?, ?, ?, ?, ?)",
               (name, email, subject, message, datetime.now().strftime('%Y-%m-%d %H:%M')))
    db.commit()
    db.close()
    push_notification('admin', 'New Contact Message', f'{name}: {subject}')
    return jsonify({'success': True, 'message': 'Message bhej diya'})


# ============ AI CHAT ============
AI_KB = [
    (['hello', 'hi', 'hey', 'salam', 'assalam', 'aoa'], 'Assalam-o-Alaikum! Main Questian AI hoon. Kya madad chahiye?'),
    (['courses list', 'saare courses', 'all courses', 'kya courses', '12 courses'], 'Hamare paas 12 courses hain: Mobile App Dev, Cyber Security, Graphics, Pen Testing, Ethical Hacking, Python, AI/ML, Deep Learning, C#, C, C++, Java OOP'),
    (['python course', 'learn python', 'python language'], 'Python Language Course: Python basics, OOP, libraries, real projects. Best for beginners.'),
    (['ai course', 'machine learning'], 'AI/ML Course: Supervised/Unsupervised learning, model training, real projects.'),
    (['cyber security', 'cybersecurity'], 'Cyber Security Course: Network security, cryptography, threats, firewalls.'),
    (['admission', 'apply', 'enroll'], 'Admission ke liye Navbar mein "Admission" tab hai. Form bharein aur submit karein.'),
    (['fee', 'fees', 'paisa', 'price'], 'Fees bohat affordable hai. Exact details ke liye admission form bharein.'),
    (['login', 'sign in'], 'Login: Username/password daalein, phir email par 6-digit code aayega.'),
    (['signup', 'sign up', 'register', 'account banana'], 'Sign Up: Login page par "Sign Up" link dabayein. Email verification zaroori hai.'),
    (['forgot password', 'password bhool'], 'Forgot Password: Login page par "Forgot Password?" dabayein, email par reset link aayega.'),
    (['software', 'download'], 'Software tab mein VS Code, XAMPP, Photoshop, Kali Linux, Git, Node.js, Docker sab hain.'),
    (['attendance', 'hazri'], 'Attendance: Student Dashboard mein "Mark Present" button hai.'),
    (['teacher se chat', 'chat with teacher'], 'Student Dashboard mein "Chat with Teacher" section hai.'),
    (['developer', 'abdul qadir'], 'Developer: Abdul Qadir Soomro. Email: 24cse23@quest.edu.pk, Phone: 03359996428'),
    (['admin', 'administrator'], 'Admin dashboard ke liye "admin" username aur "admin123" password use karein.'),
    (['help', 'madad'], 'Pooch sakte hain: courses, fees, admission, login, forgot password, software, attendance.'),
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
            prompt = f"You are Questian Academy's AI. Answer in Roman Urdu (2-3 sentences). Question: {msg}"
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
    print(f"DB: {'PostgreSQL' if USE_POSTGRES else 'SQLite'}")
    print(f"Email: {'Enabled' if EMAIL_ENABLED else 'Disabled'}")
    print(f"Gemini: {'Active' if gemini_client else 'Keyword only'}")
    app.run(debug=False, host='0.0.0.0', port=port)