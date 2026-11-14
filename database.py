import sqlite3
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'speakup.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
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
    except sqlite3.IntegrityError:
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
            "email": user['email']
        }
    return False, "Invalid email or password."

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, created_at FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

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
    return [dict(r) for r in rows]

def get_student_dashboard_data(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as cnt FROM chat_logs WHERE user_id = ?', (user_id,))
    total_messages = cursor.fetchone()['cnt']

    cursor.execute('SELECT COUNT(DISTINCT topic) as cnt FROM chat_logs WHERE user_id = ?', (user_id,))
    distinct_topics = cursor.fetchone()['cnt']

    cursor.execute('SELECT COUNT(*) as cnt, AVG(score) as avg_score FROM interview_logs WHERE user_id = ?', (user_id,))
    interview_stat = cursor.fetchone()
    interview_count = interview_stat['cnt']
    avg_interview_score = round(interview_stat['avg_score'], 1) if interview_stat['avg_score'] else 8.5

    cursor.execute('SELECT COUNT(*) as cnt FROM saved_words WHERE user_id = ?', (user_id,))
    saved_vocab_count = cursor.fetchone()['cnt']

    estimated_practice_minutes = max(18, (total_messages * 3) + (interview_count * 5))
    fluency_score = min(96, 75 + int(total_messages * 1.5))

    cursor.execute('''
        SELECT 'chat' as type, topic as title, created_at, 'Chat exchange' as subtitle, '' as score
        FROM chat_logs WHERE user_id = ?
        ORDER BY created_at DESC LIMIT 3
    ''', (user_id,))
    recent_chats = [dict(r) for r in cursor.fetchall()]

    cursor.execute('''
        SELECT 'interview' as type, question_text as title, created_at, 'Mock Interview' as subtitle, score
        FROM interview_logs WHERE user_id = ?
        ORDER BY created_at DESC LIMIT 3
    ''', (user_id,))
    recent_interviews = [dict(r) for r in cursor.fetchall()]

    all_activities = sorted(
        recent_chats + recent_interviews,
        key=lambda x: x['created_at'],
        reverse=True
    )[:5]

    cursor.execute('SELECT word_id, word_text, created_at FROM saved_words WHERE user_id = ? ORDER BY created_at DESC LIMIT 6', (user_id,))
    user_words = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "practice_minutes": estimated_practice_minutes,
        "conversations_count": max(distinct_topics, 1),
        "total_messages": total_messages,
        "fluency_score": fluency_score,
        "vocab_count": saved_vocab_count,
        "interview_count": interview_count,
        "avg_interview_score": avg_interview_score,
        "recent_activities": all_activities,
        "saved_words": user_words
    }

CUSTOM_WORD_ID_OFFSET = 1000

def _row_to_vocab_dict(row):
    synonyms = []
    if row['synonyms_json']:
        try:
            synonyms = json.loads(row['synonyms_json'])
        except Exception:
            synonyms = []
    return {
        "id": CUSTOM_WORD_ID_OFFSET + row['id'],
        "word": row['word'],
        "phonetic": row['phonetic'] or "",
        "part_of_speech": row['part_of_speech'] or "Word",
        "category": row['category'] or "Dictionary",
        "difficulty": row['difficulty'] or "Intermediate",
        "definition": row['definition'],
        "example": row['example'] or "",
        "synonyms": synonyms if isinstance(synonyms, list) else [],
        "tip": row['tip'] or "Try using this word once in your next Practice Room turn.",
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
