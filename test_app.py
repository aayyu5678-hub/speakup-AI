import sys
import sqlite3
import time
from app import app
from database import DB_PATH

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

client = app.test_client()

print("==================================================")
print("  SpeakUp AI — Automated Project Test Suite")
print("==================================================")

# 1. Test basic page routes (logout first to ensure fresh session)
client.get('/logout')
routes = ['/', '/practice', '/vocabulary', '/interview', '/login', '/register']
for r in routes:
    res = client.get(r)
    print(f"GET {r:15} -> Status: {res.status_code}")
    assert res.status_code == 200, f"Failed GET {r}"

# Dashboard sets default demo session if visited unauthenticated
dash_init = client.get('/dashboard')
print(f"GET /dashboard      -> Status: {dash_init.status_code}")
assert dash_init.status_code == 200

# 2. Test Settings Status endpoint
status_res = client.get('/api/settings/status')
print(f"GET /api/settings/status -> Status: {status_res.status_code}, Configured: {status_res.get_json()['configured']}")
assert status_res.status_code == 200

# 3. Test Student Registration & Authentication Flow
print("\n--- Testing Student Account Creation & Login ---")
unique_suffix = int(time.time())
test_email = f"priya_{unique_suffix}@college.edu"
test_name = "Priya Sharma"
test_password = "password123"

# Register new student
reg_res = client.post('/register', json={
    'name': test_name,
    'email': test_email,
    'password': test_password
})
reg_data = reg_res.get_json()
print(f"POST /register -> Status: {reg_res.status_code}, Success: {reg_data.get('success')}, User ID: {reg_data.get('user', {}).get('id')}")
assert reg_res.status_code == 200 and reg_data.get('success') is True
new_user_id = reg_data['user']['id']

# Duplicate registration check (should reject duplicate email)
dup_res = client.post('/register', json={
    'name': test_name,
    'email': test_email,
    'password': test_password
})
print(f"Duplicate POST /register -> Status: {dup_res.status_code}, Expected Error: {dup_res.get_json().get('error')}")
assert dup_res.status_code == 400

# Logout
logout_res = client.get('/logout')
assert logout_res.status_code == 302

# Bad password login check
bad_login = client.post('/login', json={
    'email': test_email,
    'password': 'wrongpassword'
})
print(f"Failed Login Check -> Status: {bad_login.status_code}, Error: {bad_login.get_json().get('error')}")
assert bad_login.status_code == 400

# Successful login
good_login = client.post('/login', json={
    'email': test_email,
    'password': test_password
})
login_data = good_login.get_json()
print(f"Valid Login Check -> Status: {good_login.status_code}, User: {login_data.get('user', {}).get('name')}")
assert good_login.status_code == 200 and login_data.get('success') is True

# Verify /practice renders with the registered student's actual name
practice_page = client.get('/practice').get_data(as_text=True)
assert "Hello Priya!" in practice_page, "Expected 'Hello Priya!' in practice room greeting"
assert "Alex" not in practice_page, "Found unwanted 'Alex' in practice room page"
print("Verified: Practice room rendered personalized greeting 'Hello Priya!' (Not Alex)!")

# 4. Test Chat Logging & AI Personalized Name Response in SQLite
print("\n--- Testing AI Conversation Personalization with Student Name ---")
chat_payload = {
    'message': "Hi Sophia! I am practicing for my campus placement interviews.",
    'topic': 'college-life',
    'level': 'intermediate',
    'history': []
}
chat_res = client.post('/api/chat', json=chat_payload)
chat_data = chat_res.get_json()
ai_reply = chat_data.get('ai_response', '')
print(f"POST /api/chat -> Status: {chat_res.status_code}, AI Reply: {ai_reply}")
assert chat_res.status_code == 200
assert 'Priya' in ai_reply, f"Expected student name 'Priya' in AI reply: {ai_reply}"
assert 'Alex' not in ai_reply, f"Found unwanted 'Alex' in AI reply: {ai_reply}"
print("Verified: Sophia addressed the student by their registered name 'Priya'!")

# Test follow-up turn with thank you
chat_payload2 = {
    'message': "Thank you so much for the advice!",
    'topic': 'college-life',
    'level': 'intermediate',
    'history': [
        {'role': 'user', 'content': 'Hi Sophia! I am practicing for my campus placement interviews.'},
        {'role': 'assistant', 'content': ai_reply}
    ]
}
chat_res2 = client.post('/api/chat', json=chat_payload2)
chat_data2 = chat_res2.get_json()
ai_reply2 = chat_data2.get('ai_response', '')
print(f"POST /api/chat (Turn 2) -> AI Reply: {ai_reply2}")
assert 'Priya' in ai_reply2, f"Expected student name 'Priya' in follow-up turn: {ai_reply2}"
print("Verified: Sophia continues addressing 'Priya' dynamically across multi-turn exchanges!")

# Verify record inserted into SQLite chat_logs for this user
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM chat_logs WHERE user_id = ?', (new_user_id,))
logged_chats = cursor.fetchone()[0]
conn.close()
print(f"SQLite Verification: {logged_chats} chat turn(s) recorded in 'chat_logs' for user ID {new_user_id}")
assert logged_chats >= 2

# 5. Test Interview Evaluation & SQLite Persistence
print("\n--- Testing Interview Evaluation & SQLite Logging ---")
interview_payload = {
    'question_id': 1,
    'answer': "Good morning! In my final year project, I led our team in building a full stack web application. I took responsibility for the database schema and UI components, which helped our team complete all milestones ahead of schedule."
}
int_res = client.post('/api/interview/evaluate', json=interview_payload)
int_data = int_res.get_json()
print(f"POST /api/interview/evaluate -> Status: {int_res.status_code}, Score: {int_data.get('evaluation', {}).get('score')}")
assert int_res.status_code == 200

# Verify interview logged in SQLite
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM interview_logs WHERE user_id = ?', (new_user_id,))
logged_interviews = cursor.fetchone()[0]
conn.close()
print(f"SQLite Verification: {logged_interviews} interview session(s) recorded in 'interview_logs' for user ID {new_user_id}")
assert logged_interviews >= 1

# 6. Test Vocabulary Bookmark Toggling & SQLite Persistence
print("\n--- Testing Vocabulary Studio Bookmark Persistence ---")
vocab_toggle_res = client.post('/api/vocabulary/toggle', json={
    'word_id': 2,
    'word_text': 'Elaborate'
})
toggle_data = vocab_toggle_res.get_json()
print(f"POST /api/vocabulary/toggle -> Status: {vocab_toggle_res.status_code}, Action: {toggle_data.get('action')}")
assert vocab_toggle_res.status_code == 200 and toggle_data.get('action') == 'saved'

# Verify word logged in SQLite
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('SELECT word_text FROM saved_words WHERE user_id = ? AND word_id = ?', (new_user_id, 2))
saved_word_record = cursor.fetchone()
conn.close()
print(f"SQLite Verification: Word '{saved_word_record[0]}' found in 'saved_words' for user ID {new_user_id}")
assert saved_word_record is not None

# 6b. Test Changing Daily Word of the Day & Unlimited Word Lookup
print("\n--- Testing Dynamic Word of the Day & Unlimited Dictionary Lookup ---")
daily1_res = client.get('/api/vocabulary/daily')
daily1 = daily1_res.get_json().get('word', {})
print(f"Initial Daily Word: {daily1.get('word')} ({daily1.get('date')})")
assert daily1_res.status_code == 200 and daily1.get('word')

daily2_res = client.get(f"/api/vocabulary/daily?refresh=1&exclude={daily1.get('word')}")
daily2 = daily2_res.get_json().get('word', {})
print(f"Refreshed Daily Word: {daily2.get('word')}")
assert daily2_res.status_code == 200 and daily2.get('word')
assert daily2.get('word').lower() != daily1.get('word').lower(), "Expected refreshed Daily Word to change!"

lookup_res = client.get('/api/vocabulary/lookup?word=ephemeral')
lookup_data = lookup_res.get_json()
print(f"GET /api/vocabulary/lookup?word=ephemeral -> Status: {lookup_res.status_code}, Word: {lookup_data.get('entry', {}).get('word')}, ID: {lookup_data.get('entry', {}).get('id')}")
assert lookup_res.status_code == 200 and lookup_data.get('success') is True
entry = lookup_data['entry']
assert entry.get('definition') and entry.get('id', 0) >= 1000

# Verify custom searched word can be bookmarked and appears on /vocabulary
custom_save_res = client.post('/api/vocabulary/toggle', json={
    'word_id': entry['id'],
    'word_text': entry['word']
})
assert custom_save_res.status_code == 200 and custom_save_res.get_json().get('action') == 'saved'
vocab_page_html = client.get('/vocabulary').get_data(as_text=True)
assert entry['word'] in vocab_page_html, f"Expected custom saved word '{entry['word']}' in /vocabulary HTML"

gibberish_res = client.get('/api/vocabulary/lookup?word=xqzwptv123')
print(f"Gibberish check -> Status: {gibberish_res.status_code}, Error: {gibberish_res.get_json().get('error')}")
assert gibberish_res.status_code == 404

# 7. Test Dynamic Dashboard Data Rendering
print("\n--- Testing Dynamic Student Dashboard ---")
dash_res = client.get('/dashboard')
dash_html = dash_res.get_data(as_text=True)
print(f"GET /dashboard -> Status: {dash_res.status_code}")
assert dash_res.status_code == 200
assert test_name in dash_html, f"Expected student name '{test_name}' in dashboard HTML"
assert "Elaborate" in dash_html, "Expected saved word 'Elaborate' in dashboard HTML"
print(f"Verified: Dashboard dynamically displayed student name '{test_name}' and saved vocabulary 'Elaborate'!")

# 8. Test a 4-turn consecutive conversation to verify NO REPEATED SENTENCES!
history = []
user_messages = [
    "Hi Sophia! I would like to order a warm cappuccino.",
    "Regular size with oat milk, please.",
    "Yes, please warm up a fresh croissant for me too.",
    "I will pay with my card, thank you!"
]

assistant_responses = []
print("\n--- Testing 4-turn Cafe Conversation for Non-Repetition ---")
for i, u_msg in enumerate(user_messages):
    payload = {
        'message': u_msg,
        'topic': 'ordering-cafe',
        'level': 'intermediate',
        'history': history
    }
    resp = client.post('/api/chat', json=payload)
    data = resp.get_json()
    ai_text = data['ai_response']
    
    print(f"[Turn {i+1}] Student: {u_msg}")
    print(f"[Turn {i+1}] Sophia:  {ai_text}")
    
    assert ai_text not in assistant_responses, f"Duplicate response detected on turn {i+1}: '{ai_text}'"
    assistant_responses.append(ai_text)
    
    history.append({'role': 'user', 'content': u_msg})
    history.append({'role': 'assistant', 'content': ai_text})

print("\n==================================================")
print("  ALL TESTS PASSED! SpeakUp AI is 100% verified.")
print("==================================================")
