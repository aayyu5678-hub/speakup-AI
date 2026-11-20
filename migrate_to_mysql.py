"""
SpeakUp AI — Cloud MySQL Database Migration Tool
Migrates existing SQLite records from speakup.db into your cloud MySQL database.

Usage:
    python migrate_to_mysql.py
Or with explicit connection string:
    python migrate_to_mysql.py --url "mysql://user:password@host:port/database?ssl-mode=REQUIRED"
"""

import os
import sys
import sqlite3
import argparse
from urllib.parse import urlparse

# Reconfigure stdout for UTF-8 compatibility on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), 'speakup.db')

def parse_args():
    parser = argparse.ArgumentParser(description="Migrate SpeakUp AI SQLite database to Cloud MySQL")
    parser.add_argument("--url", help="MySQL connection URL (mysql://user:pass@host:port/db)")
    return parser.parse_args()

def load_env_if_present():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and not os.environ.get(k):
                            os.environ[k] = v
        except Exception:
            pass

def main():
    args = parse_args()
    load_env_if_present()

    target_url = args.url or os.environ.get("DATABASE_URL") or os.environ.get("MYSQL_URL")
    if not target_url and not os.environ.get("MYSQL_HOST"):
        print("==================================================")
        print("     SpeakUp AI — MySQL Migration Tool")
        print("==================================================")
        print("Error: No MySQL connection details found.")
        print("\nPlease provide your MySQL connection URL in one of two ways:")
        print("  1. Pass it as a command argument:")
        print('     python migrate_to_mysql.py --url "mysql://user:pass@host:port/dbname?ssl-mode=REQUIRED"')
        print("  2. Add DATABASE_URL to your .env file:")
        print("     DATABASE_URL=mysql://user:pass@host:port/dbname?ssl-mode=REQUIRED")
        sys.exit(1)

    try:
        import pymysql
        import pymysql.cursors
    except ImportError:
        print("Error: PyMySQL is not installed. Please run:")
        print("  pip install pymysql cryptography")
        sys.exit(1)

    if not os.path.exists(SQLITE_DB_PATH):
        print(f"Error: Local SQLite database not found at {SQLITE_DB_PATH}")
        sys.exit(1)

    # Temporary set target_url in environ if passed via cli
    if target_url:
        os.environ["DATABASE_URL"] = target_url

    from database import get_connection, init_db

    print("==================================================")
    print("     SpeakUp AI — MySQL Migration Tool")
    print("==================================================")
    print("1. Connecting to Cloud MySQL and initializing tables...")
    try:
        init_db()
        mysql_conn = get_connection()
        if not mysql_conn.is_mysql:
            print("Notice: Connected to SQLite instead of MySQL. Check your connection URL.")
            sys.exit(1)
        print("   -> Connection successful!")
    except Exception as e:
        print(f"   -> Failed to connect to MySQL: {e}")
        sys.exit(1)

    sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()
    mysql_cur = mysql_conn.cursor()

    # 1. Migrate users
    print("\n2. Migrating 'users' table...")
    sqlite_cur.execute("SELECT * FROM users")
    users = sqlite_cur.fetchall()
    users_migrated = 0
    for u in users:
        mysql_cur.execute("SELECT id FROM users WHERE email = %s", (u['email'],))
        if not mysql_cur.fetchone():
            mysql_cur.execute(
                "INSERT INTO users (id, name, email, password_hash, created_at) VALUES (%s, %s, %s, %s, %s)",
                (u['id'], u['name'], u['email'], u['password_hash'], u['created_at'])
            )
            users_migrated += 1
    mysql_conn.commit()
    print(f"   -> {users_migrated} new user(s) migrated (total in SQLite: {len(users)})")

    # 2. Migrate chat_logs
    print("\n3. Migrating 'chat_logs' table...")
    sqlite_cur.execute("SELECT * FROM chat_logs")
    chats = sqlite_cur.fetchall()
    chats_migrated = 0
    for c in chats:
        mysql_cur.execute(
            """INSERT INTO chat_logs (id, user_id, topic, level, user_message, ai_response, has_grammar_error, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE id=id""",
            (c['id'], c['user_id'], c['topic'], c['level'], c['user_message'], c['ai_response'], c['has_grammar_error'], c['created_at'])
        )
        chats_migrated += 1
    mysql_conn.commit()
    print(f"   -> {chats_migrated} chat log(s) migrated")

    # 3. Migrate interview_logs
    print("\n4. Migrating 'interview_logs' table...")
    sqlite_cur.execute("SELECT * FROM interview_logs")
    interviews = sqlite_cur.fetchall()
    interviews_migrated = 0
    for i in interviews:
        mysql_cur.execute(
            """INSERT INTO interview_logs (id, user_id, question_text, student_answer, score, word_count, filler_words, improvement_tip, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE id=id""",
            (i['id'], i['user_id'], i['question_text'], i['student_answer'], i['score'], i['word_count'], i['filler_words'], i['improvement_tip'], i['created_at'])
        )
        interviews_migrated += 1
    mysql_conn.commit()
    print(f"   -> {interviews_migrated} interview log(s) migrated")

    # 4. Migrate saved_words
    print("\n5. Migrating 'saved_words' table...")
    sqlite_cur.execute("SELECT * FROM saved_words")
    saved_words = sqlite_cur.fetchall()
    saved_migrated = 0
    for sw in saved_words:
        mysql_cur.execute(
            """INSERT IGNORE INTO saved_words (id, user_id, word_id, word_text, created_at)
               VALUES (%s, %s, %s, %s, %s)""",
            (sw['id'], sw['user_id'], sw['word_id'], sw['word_text'], sw['created_at'])
        )
        saved_migrated += 1
    mysql_conn.commit()
    print(f"   -> {saved_migrated} saved word(s) migrated")

    # 5. Migrate dictionary_words
    print("\n6. Migrating 'dictionary_words' table...")
    sqlite_cur.execute("SELECT * FROM dictionary_words")
    dict_words = sqlite_cur.fetchall()
    dict_migrated = 0
    for dw in dict_words:
        mysql_cur.execute(
            """INSERT IGNORE INTO dictionary_words (id, word_key, word, phonetic, part_of_speech, category, difficulty, definition, example, synonyms_json, tip, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (dw['id'], dw['word_key'], dw['word'], dw['phonetic'], dw['part_of_speech'], dw['category'], dw['difficulty'], dw['definition'], dw['example'], dw['synonyms_json'], dw['tip'], dw['created_at'])
        )
        dict_migrated += 1
    mysql_conn.commit()
    print(f"   -> {dict_migrated} dictionary cache record(s) migrated")

    sqlite_conn.close()
    mysql_conn.close()

    print("\n==================================================")
    print("  ALL DATA MIGRATED TO CLOUD MYSQL SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    main()
