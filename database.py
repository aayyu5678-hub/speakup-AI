import os
import json
import re
import sqlite3
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash, check_password_hash

try:
    import pymysql
    import pymysql.cursors
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False

DB_PATH = os.path.join(os.path.dirname(__file__), 'speakup.db')

INTEGRITY_ERRORS = (sqlite3.IntegrityError,)
if PYMYSQL_AVAILABLE and hasattr(pymysql, 'err') and hasattr(pymysql.err, 'IntegrityError'):
    INTEGRITY_ERRORS = (sqlite3.IntegrityError, pymysql.err.IntegrityError)

def get_mysql_config():
    """Detect whether MySQL credentials are provided via environment variables."""
    db_url = os.environ.get('DATABASE_URL') or os.environ.get('MYSQL_URL')
    if db_url and ('mysql://' in db_url or 'mysql+pymysql://' in db_url):
        clean_url = db_url.replace('mysql+pymysql://', 'mysql://')
        parsed = urlparse(clean_url)
        ssl_config = None
        url_lower = db_url.lower()
        if 'ssl-mode=required' in url_lower or 'tidbcloud' in url_lower or 'aivencloud' in url_lower:
            ssl_config = {'ssl_mode': 'REQUIRED'}
        return {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 3306,
            'user': parsed.username or 'root',
            'password': parsed.password or '',
            'database': (parsed.path or '').lstrip('/').split('?')[0],
            'ssl': ssl_config
        }

    mysql_host = os.environ.get('MYSQL_HOST')
    if mysql_host:
        return {
            'host': mysql_host,
            'port': int(os.environ.get('MYSQL_PORT', 3306)),
            'user': os.environ.get('MYSQL_USER', 'root'),
            'password': os.environ.get('MYSQL_PASSWORD', ''),
            'database': os.environ.get('MYSQL_DATABASE') or os.environ.get('MYSQL_DB', 'speakup'),
            'ssl': None
        }

    return None

def is_mysql_active():
    return PYMYSQL_AVAILABLE and (get_mysql_config() is not None)

class DualModeCursor:
    """Cursor wrapper that transparently adapts parameter syntax and statement differences between SQLite and MySQL."""
    def __init__(self, raw_cursor, is_mysql=False):
        self.cursor = raw_cursor
        self.is_mysql = is_mysql

    def execute(self, sql, params=None):
        if self.is_mysql:
            # 1. Adapt parameter placeholder from ? to %s
            sql = sql.replace('?', '%s')
            # 2. Adapt INSERT OR IGNORE to INSERT IGNORE
            sql = re.sub(r'\bINSERT\s+OR\s+IGNORE\s+INTO\b', 'INSERT IGNORE INTO', sql, flags=re.IGNORECASE)
            # 3. Adapt SQLite ON CONFLICT to MySQL ON DUPLICATE KEY UPDATE
            if 'ON CONFLICT' in sql:
                sql = re.sub(
                    r'ON\s+CONFLICT\s*\([^)]+\)\s*DO\s+UPDATE\s+SET\s+word_id\s*=\s*excluded\.word_id\s*,\s*word_json\s*=\s*excluded\.word_json',
                    'ON DUPLICATE KEY UPDATE word_id = VALUES(word_id), word_json = VALUES(word_json)',
                    sql,
                    flags=re.IGNORECASE
                )
        if params is not None:
            return self.cursor.execute(sql, params)
        return self.cursor.execute(sql)

    def fetchone(self):
        row = self.cursor.fetchone()
        return dict(row) if row is not None else None

    def fetchall(self):
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    @property
    def lastrowid(self):
        return self.cursor.lastrowid

    def close(self):
        try:
            return self.cursor.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class DualModeConnection:
    """Connection wrapper ensuring identical dictionary row access and commit behavior across SQLite and MySQL."""
    def __init__(self, raw_conn, is_mysql=False):
        self.conn = raw_conn
        self.is_mysql = is_mysql

    def cursor(self):
        raw_cur = self.conn.cursor()
        return DualModeCursor(raw_cur, is_mysql=self.is_mysql)

    def commit(self):
        return self.conn.commit()

    def rollback(self):
        return self.conn.rollback()

    def close(self):
        try:
            return self.conn.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()

def get_connection():
    """Return an active connection: Cloud MySQL when configured, otherwise local SQLite."""
    if is_mysql_active():
        cfg = get_mysql_config()
        conn_kwargs = {
            'host': cfg['host'],
            'port': cfg['port'],
            'user': cfg['user'],
            'password': cfg['password'],
            'database': cfg['database'],
            'charset': 'utf8mb4',
            'autocommit': False,
            'cursorclass': pymysql.cursors.DictCursor
        }
        if cfg['ssl']:
            conn_kwargs['ssl'] = cfg['ssl']
        raw_conn = pymysql.connect(**conn_kwargs)
        return DualModeConnection(raw_conn, is_mysql=True)

    # Default: Local SQLite database
    raw_conn = sqlite3.connect(DB_PATH)
    raw_conn.row_factory = sqlite3.Row
    return DualModeConnection(raw_conn, is_mysql=False)

def init_db():
    """Initialize database tables. Automatically adapts schema for MySQL or SQLite."""
    conn = get_connection()
    cursor = conn.cursor()

    if conn.is_mysql:
        # MySQL 5.7+ / 8.0+ / TiDB Schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                avatar VARCHAR(255) DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                topic VARCHAR(100) NOT NULL,
                level VARCHAR(50) NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                has_grammar_error INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                question_text TEXT NOT NULL,
                student_answer TEXT NOT NULL,
                score FLOAT NOT NULL,
                word_count INT NOT NULL,
                filler_words TEXT,
                improvement_tip TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_words (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                word_id INT NOT NULL,
                word_text VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uq_user_word (user_id, word_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dictionary_words (
                id INT AUTO_INCREMENT PRIMARY KEY,
                word_key VARCHAR(255) UNIQUE NOT NULL,
                word VARCHAR(255) NOT NULL,
                phonetic VARCHAR(255),
                part_of_speech VARCHAR(100),
                category VARCHAR(100),
                difficulty VARCHAR(50),
                definition TEXT NOT NULL,
                example TEXT,
                synonyms_json TEXT,
                tip TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_words (
                date_key VARCHAR(50) PRIMARY KEY,
                word_id INT NOT NULL,
                word_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')
    else:
        # SQLite Schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                avatar TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                topic TEXT NOT NULL,
                level TEXT NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                has_grammar_error INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question_text TEXT NOT NULL,
                student_answer TEXT NOT NULL,
                score REAL NOT NULL,
                word_count INTEGER NOT NULL,
                filler_words TEXT,
                improvement_tip TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                word_id INTEGER NOT NULL,
                word_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, word_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dictionary_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_key TEXT UNIQUE NOT NULL,
                word TEXT NOT NULL,
                phonetic TEXT,
                part_of_speech TEXT,
                category TEXT,
                difficulty TEXT,
                definition TEXT NOT NULL,
                example TEXT,
                synonyms_json TEXT,
                tip TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_words (
                date_key TEXT PRIMARY KEY,
                word_id INTEGER NOT NULL,
                word_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    # Ensure avatar column exists for backward compatibility with existing databases
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN avatar TEXT DEFAULT NULL')
    except Exception:
        pass

    cursor.execute('SELECT id FROM users WHERE email = ?', ('alex.turner@college.edu',))
    existing_demo = cursor.fetchone()
    if not existing_demo:
        demo_pwd_hash = generate_password_hash('student123')
        cursor.execute(
            'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
            ('Alex Turner', 'alex.turner@college.edu', demo_pwd_hash)
        )
        demo_user_id = cursor.lastrowid

        initial_chats = [
            ("ordering-cafe", "intermediate", "Hi Sophia, could I please get a cappuccino?", "Great choice! Would you like that hot or iced? Also, whole milk or oat milk?", 0),
            ("ordering-cafe", "intermediate", "Regular size with oat milk, please.", "Regular it is! Can I tempt you with any fresh pastries today, like a butter croissant?", 0),
            ("college-life", "intermediate", "I am currently preparing for semester project presentations.", "Working on projects is where real learning happens! What is the central feature you are presenting?", 0)
        ]
        for topic, level, u_msg, a_msg, err in initial_chats:
            cursor.execute(
                'INSERT INTO chat_logs (user_id, topic, level, user_message, ai_response, has_grammar_error) VALUES (?, ?, ?, ?, ?, ?)',
                (demo_user_id, topic, level, u_msg, a_msg, err)
            )

        cursor.execute(
            'INSERT INTO interview_logs (user_id, question_text, student_answer, score, word_count, filler_words, improvement_tip) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (
                demo_user_id,
                "Tell me about yourself and your background.",
                "Good morning! I am a computer science student specializing in web engineering. Over the past two semesters, I led our group project developing full-stack web applications. I enjoy solving user interface problems and ensuring accessibility.",
                8.5,
                38,
                "None",
                "Try incorporating STAR framing (Situation, Task, Action, Result) to make your accomplishments stand out even more."
            )
        )

        initial_words = [(1, "Articulate"), (3, "Perseverance"), (4, "Nuance"), (5, "Pragmatic")]
        for w_id, w_text in initial_words:
            cursor.execute(
                'INSERT OR IGNORE INTO saved_words (user_id, word_id, word_text) VALUES (?, ?, ?)',
                (demo_user_id, w_id, w_text)
            )

    conn.commit()
    conn.close()

def register_user(name, email, password):
    email = email.strip().lower()
    name = name.strip()
    if not name or not email or not password:
        return False, "All fields are required."
    if len(password) < 4:
        return False, "Password must be at least 4 characters long."

    pwd_hash = generate_password_hash(password)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
            (name, email, pwd_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return True, {"id": user_id, "name": name, "email": email}
    except INTEGRITY_ERRORS:
        return False, "An account with this email already exists. Please sign in."
    finally:
        conn.close()

def authenticate_user(email, password):
    email = email.strip().lower()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        return True, {
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "avatar": user.get('avatar') or ''
        }
    return False, "Invalid email or password."

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, avatar, created_at FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user if user else None

def update_user_profile(user_id, name, email, avatar=None):
    """Update student profile details with uniqueness verification."""
    name = (name or "").strip()
    email = (email or "").strip().lower()
    if not name:
        return False, "Full name cannot be empty."
    if not email or "@" not in email:
        return False, "Please provide a valid email address."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id))
        if cursor.fetchone():
            return False, "This email address is already in use by another account."

        if avatar is not None:
            cursor.execute("UPDATE users SET name = ?, email = ?, avatar = ? WHERE id = ?", (name, email, avatar, user_id))
        else:
            cursor.execute("UPDATE users SET name = ?, email = ? WHERE id = ?", (name, email, user_id))
        conn.commit()

        cursor.execute("SELECT id, name, email, avatar, created_at FROM users WHERE id = ?", (user_id,))
        updated = cursor.fetchone()
        return True, updated
    except Exception as e:
        return False, f"Failed to update profile: {str(e)}"
    finally:
        conn.close()

def change_user_password(user_id, old_password, new_password):
    """Change student password after validating old password hash."""
    if not old_password:
        return False, "Current password is required."
    if not new_password or len(new_password) < 4:
        return False, "New password must be at least 4 characters long."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return False, "User account not found."

        if not check_password_hash(user['password_hash'], old_password):
            return False, "Current password is incorrect. Please verify and try again."

        new_hash = generate_password_hash(new_password)
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
        conn.commit()
        return True, "Password changed successfully."
    except Exception as e:
        return False, f"Failed to change password: {str(e)}"
    finally:
        conn.close()

def save_chat_turn(user_id, topic, level, user_message, ai_response, has_grammar_error=False):
    if not user_id:
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO chat_logs (user_id, topic, level, user_message, ai_response, has_grammar_error)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (user_id, topic, level, user_message, ai_response, 1 if has_grammar_error else 0)
    )
    conn.commit()
    conn.close()

def save_interview_result(user_id, question_text, answer, score, word_count, filler_words, tip):
    if not user_id:
        return
    conn = get_connection()
    cursor = conn.cursor()
    fillers_str = ", ".join(filler_words) if isinstance(filler_words, list) else str(filler_words)
    cursor.execute(
        '''INSERT INTO interview_logs (user_id, question_text, student_answer, score, word_count, filler_words, improvement_tip)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (user_id, question_text, answer, score, word_count, fillers_str, tip)
    )
    conn.commit()
    conn.close()

def toggle_save_word(user_id, word_id, word_text):
    if not user_id:
        return False, "Must be logged in"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM saved_words WHERE user_id = ? AND word_id = ?', (user_id, word_id))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute('DELETE FROM saved_words WHERE id = ?', (existing['id'],))
        action = "removed"
    else:
        cursor.execute('INSERT INTO saved_words (user_id, word_id, word_text) VALUES (?, ?, ?)', (user_id, word_id, word_text))
        action = "saved"
        
    conn.commit()
    conn.close()
    return True, action

def get_user_saved_words(user_id):
    if not user_id:
        return []
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT word_id, word_text FROM saved_words WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_user_achievements(user_id):
    """Calculate unlocked and upcoming milestone achievements for the student."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM chat_logs WHERE user_id = ?", (user_id,))
    chat_cnt = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM saved_words WHERE user_id = ?", (user_id,))
    vocab_cnt = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt, MAX(score) as max_s FROM interview_logs WHERE user_id = ?", (user_id,))
    int_row = cursor.fetchone()
    int_cnt = int_row['cnt']
    max_score = int_row['max_s'] or 0.0
    conn.close()

    achievements = [
        {
            "id": "first_chat",
            "title": "First Voice",
            "icon": "🎙️",
            "category": "Speaking",
            "description": "Completed your first live conversation turn with Sophia AI tutor.",
            "unlocked": chat_cnt >= 1,
            "progress": f"{min(chat_cnt, 1)}/1 Turn",
            "xp": 100
        },
        {
            "id": "vocab_builder",
            "title": "Lexicon Collector",
            "icon": "📖",
            "category": "Vocabulary",
            "description": "Saved 3 or more high-impact words to your revision study deck.",
            "unlocked": vocab_cnt >= 3,
            "progress": f"{min(vocab_cnt, 3)}/3 Words",
            "xp": 150
        },
        {
            "id": "interview_ready",
            "title": "Placement Ready",
            "icon": "💼",
            "category": "Career",
            "description": "Completed a mock placement interview evaluated with the STAR method.",
            "unlocked": int_cnt >= 1,
            "progress": f"{min(int_cnt, 1)}/1 Interview",
            "xp": 200
        },
        {
            "id": "streak_champ",
            "title": "5-Day Streak",
            "icon": "🔥",
            "category": "Habits",
            "description": "Practiced spoken English across 5 consecutive active learning sessions.",
            "unlocked": (chat_cnt + int_cnt) >= 5,
            "progress": f"{min(chat_cnt + int_cnt, 5)}/5 Sessions",
            "xp": 250
        },
        {
            "id": "active_listener",
            "title": "Active Listener",
            "icon": "🎧",
            "category": "Listening",
            "description": "Explored multi-turn listening comprehension dialogues and audio scenarios.",
            "unlocked": chat_cnt >= 2,
            "progress": f"{min(chat_cnt, 2)}/2 Dialogues",
            "xp": 120
        },
        {
            "id": "placement_ace",
            "title": "Master Orator",
            "icon": "🏆",
            "category": "Fluency",
            "description": "Scored 8.0 or higher in a simulated placement interview response.",
            "unlocked": max_score >= 8.0,
            "progress": f"{max_score:.1f}/8.0 Score" if max_score else "0.0/8.0 Score",
            "xp": 300
        }
    ]
    return achievements

def get_student_dashboard_data(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as cnt FROM chat_logs WHERE user_id = ?', (user_id,))
    total_messages = cursor.fetchone()['cnt']

    cursor.execute('SELECT COUNT(DISTINCT topic) as cnt FROM chat_logs WHERE user_id = ?', (user_id,))
    distinct_topics = cursor.fetchone()['cnt']

    cursor.execute('SELECT COUNT(*) as cnt, AVG(score) as avg_score, MAX(score) as max_score FROM interview_logs WHERE user_id = ?', (user_id,))
    interview_stat = cursor.fetchone()
    interview_count = interview_stat['cnt']
    avg_interview_score = round(interview_stat['avg_score'], 1) if interview_stat['avg_score'] else 8.5

    cursor.execute('SELECT COUNT(*) as cnt FROM saved_words WHERE user_id = ?', (user_id,))
    saved_vocab_count = cursor.fetchone()['cnt']

    estimated_practice_minutes = max(24, (total_messages * 3) + (interview_count * 5))
    fluency_score = min(96, 75 + int(total_messages * 1.5))
    completion_percent = min(94, max(45, int(40 + (total_messages * 3.5) + (saved_vocab_count * 4) + (interview_count * 5))))

    cursor.execute('''
        SELECT 'chat' as type, topic as title, created_at, 'Chat exchange' as subtitle, '' as score
        FROM chat_logs WHERE user_id = ?
        ORDER BY created_at DESC LIMIT 3
    ''', (user_id,))
    recent_chats = cursor.fetchall()

    cursor.execute('''
        SELECT 'interview' as type, question_text as title, created_at, 'Mock Interview' as subtitle, score
        FROM interview_logs WHERE user_id = ?
        ORDER BY created_at DESC LIMIT 3
    ''', (user_id,))
    recent_interviews = cursor.fetchall()

    all_activities = sorted(
        recent_chats + recent_interviews,
        key=lambda x: x['created_at'],
        reverse=True
    )[:5]

    cursor.execute('SELECT word_id, word_text, created_at FROM saved_words WHERE user_id = ? ORDER BY created_at DESC LIMIT 6', (user_id,))
    user_words = cursor.fetchall()

    conn.close()

    # For every student account, streak starts from Day 1 and increments as they practice
    if user_id == 1 and total_messages == 0:
        streak_days = 5  # demo template preview
    else:
        # Every student starts from Day 1 and continues with their actual learning
        streak_days = max(1, min(100, 1 + (total_messages // 4)))

    days_order = [
        ("Mon", "M"), ("Tue", "T"), ("Wed", "W"), ("Thu", "T"),
        ("Fri", "F"), ("Sat", "S"), ("Sun", "S")
    ]
    streak_history = []
    for idx, (d_name, d_short) in enumerate(days_order):
        is_today = (idx == 6)  # Sunday / current active day
        # For Day 1 student: only today is active. Previous days light up matching streak count:
        is_active = is_today or (idx >= (7 - streak_days))
        streak_history.append({
            "day": d_name,
            "short": d_short,
            "active": is_active,
            "today": is_today
        })

    recent_modules = [
        {
            "name": "Speaking Practice",
            "tag": "Live Voice",
            "icon": "🎙️",
            "time_ago": "2 hours ago",
            "stat": f"{total_messages} turns logged",
            "badge_color": "purple",
            "url": "/practice"
        },
        {
            "name": "Vocabulary Studio",
            "tag": "Flashcards",
            "icon": "📖",
            "time_ago": "Today",
            "stat": f"{saved_vocab_count} saved words",
            "badge_color": "green",
            "url": "/vocabulary"
        },
        {
            "name": "Interview Simulator",
            "tag": "STAR Feedback",
            "icon": "💼",
            "time_ago": "Yesterday",
            "stat": f"{avg_interview_score}/10 score",
            "badge_color": "blue",
            "url": "/interview"
        },
        {
            "name": "Listening Comprehension",
            "tag": "Audio Scenarios",
            "icon": "🎧",
            "time_ago": "2 days ago",
            "stat": "21 dialogues",
            "badge_color": "green",
            "url": "/listening"
        }
    ]

    continue_learning = {
        "title": "Mastering Placement Discussions",
        "category": "Conversational Fluency • Pathway 2",
        "description": "Continue your dialogue with Sophia on Campus & Placement interviews. Refine your STAR examples.",
        "progress_percent": completion_percent,
        "step_label": f"Module {min(5, max(1, distinct_topics + 1))} of 6",
        "url": "/practice?topic=college-life"
    }

    vocab_pct = min(96, 60 + saved_vocab_count * 6)
    interview_pct = min(98, max(50, int(avg_interview_score * 10)))

    return {
        "practice_minutes": estimated_practice_minutes,
        "conversations_count": max(distinct_topics, 1),
        "total_messages": total_messages,
        "fluency_score": fluency_score,
        "completion_percent": completion_percent,
        "streak_days": streak_days,
        "streak_history": streak_history,
        "recent_modules": recent_modules,
        "continue_learning": continue_learning,
        "vocab_count": saved_vocab_count,
        "vocab_pct": vocab_pct,
        "interview_count": interview_count,
        "avg_interview_score": avg_interview_score,
        "interview_pct": interview_pct,
        "recent_activities": all_activities,
        "saved_words": user_words
    }

CUSTOM_WORD_ID_OFFSET = 1000

def _row_to_vocab_dict(row):
    synonyms = []
    if row.get('synonyms_json'):
        try:
            synonyms = json.loads(row['synonyms_json'])
        except Exception:
            synonyms = []
    return {
        "id": CUSTOM_WORD_ID_OFFSET + row['id'],
        "word": row['word'],
        "phonetic": row.get('phonetic') or "",
        "part_of_speech": row.get('part_of_speech') or "Word",
        "category": row.get('category') or "Dictionary",
        "difficulty": row.get('difficulty') or "Intermediate",
        "definition": row['definition'],
        "example": row.get('example') or "",
        "synonyms": synonyms if isinstance(synonyms, list) else [],
        "tip": row.get('tip') or "Try using this word once in your next Practice Room turn.",
        "is_custom": True
    }

def get_cached_dictionary_word(word_text):
    word_key = (word_text or "").strip().lower()
    if not word_key:
        return None
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dictionary_words WHERE word_key = ?', (word_key,))
    row = cursor.fetchone()
    conn.close()
    return _row_to_vocab_dict(row) if row else None

def save_dictionary_word(entry):
    word = (entry.get("word") or "").strip()
    word_key = word.lower()
    if not word_key or not entry.get("definition"):
        return None

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dictionary_words WHERE word_key = ?', (word_key,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return _row_to_vocab_dict(existing)

    synonyms_json = json.dumps(entry.get("synonyms") or [])
    cursor.execute(
        '''INSERT INTO dictionary_words
           (word_key, word, phonetic, part_of_speech, category, difficulty, definition, example, synonyms_json, tip)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            word_key,
            word,
            entry.get("phonetic", ""),
            entry.get("part_of_speech", "Word"),
            entry.get("category", "Dictionary"),
            entry.get("difficulty", "Intermediate"),
            entry.get("definition", ""),
            entry.get("example", ""),
            synonyms_json,
            entry.get("tip", "")
        )
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.execute('SELECT * FROM dictionary_words WHERE id = ?', (new_id,))
    row = cursor.fetchone()
    conn.close()
    return _row_to_vocab_dict(row) if row else None

def get_saved_custom_words(user_id):
    if not user_id:
        return []
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT d.* FROM dictionary_words d
           INNER JOIN saved_words s ON (d.id + ?) = s.word_id
           WHERE s.user_id = ?
           ORDER BY s.created_at DESC''',
        (CUSTOM_WORD_ID_OFFSET, user_id)
    )
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_vocab_dict(r) for r in rows]

def get_daily_word_cache(date_key):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT word_json FROM daily_words WHERE date_key = ?', (date_key,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    try:
        return json.loads(row['word_json'])
    except Exception:
        return None

def set_daily_word_cache(date_key, word_data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO daily_words (date_key, word_id, word_json)
           VALUES (?, ?, ?)
           ON CONFLICT(date_key) DO UPDATE SET word_id = excluded.word_id, word_json = excluded.word_json''',
        (date_key, int(word_data.get("id", 1)), json.dumps(word_data))
    )
    conn.commit()
    conn.close()
