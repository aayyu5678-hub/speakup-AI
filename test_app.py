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

# 1. Test unauthenticated guest flow (logout first to ensure fresh session)
client.get('/logout')
res_home = client.get('/')
print(f"GET / (unauthenticated) -> Status: {res_home.status_code}")
assert res_home.status_code == 302 and '/login' in res_home.location, "Unauthenticated / should redirect to /login"

res_dash_guest = client.get('/dashboard')
print(f"GET /dashboard (guest)  -> Status: {res_dash_guest.status_code}")
assert res_dash_guest.status_code == 302 and '/login' in res_dash_guest.location, "Unauthenticated /dashboard should redirect to /login"

res_login = client.get('/login')
print(f"GET /login              -> Status: {res_login.status_code}")
assert res_login.status_code == 200

res_reg = client.get('/register')
print(f"GET /register           -> Status: {res_reg.status_code}")
assert res_reg.status_code == 200

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

# Check initial dashboard streak for newly registered student (0 activities -> Day 1)
init_dash = client.get('/dashboard').get_data(as_text=True)
assert '<strong>1</strong>-day streak' in init_dash or '1 <span class="stat-unit">' in init_dash, "Initial registered student streak must start from Day 1!"

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

# 9. Test Current Navigation Drawer Modules & Routes
print("\n--- Testing Navigation Drawer Module Routes ---")
sidebar_routes = ['/modules', '/vocabulary', '/practice', '/listening', '/conversation', '/progress', '/achievements', '/profile']
for s_route in sidebar_routes:
    res = client.get(s_route)
    print(f"GET {s_route:16} -> Status: {res.status_code}")
    assert res.status_code == 200, f"Failed GET {s_route}"

# 10. Test Grammar Module Safe Redirect (Removed Simulator)
print("\n--- Testing Grammar Module Clean Removal & Safe Redirect ---")
gram_redir = client.get('/grammar')
print(f"GET /grammar -> Status: {gram_redir.status_code}, Redirects to: {gram_redir.location}")
assert gram_redir.status_code == 302
assert '/modules' in gram_redir.location

# 11. Test Profile Update API (Real Database Mutation)
print("\n--- Testing Profile Update API ---")
updated_name = "Priya Sharma (Tech Scholar)"
prof_res = client.post('/api/user/profile', json={
    'name': updated_name,
    'email': test_email,
    'avatar': '👩‍🎓'
})
prof_data = prof_res.get_json()
print(f"POST /api/user/profile -> Status: {prof_res.status_code}, User: {prof_data.get('user', {}).get('name')}, Avatar: {prof_data.get('user', {}).get('avatar')}")
assert prof_res.status_code == 200 and prof_data.get('success') is True
assert prof_data['user']['name'] == updated_name
assert prof_data['user']['avatar'] == '👩‍🎓'

# Verify profile reflected in database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('SELECT name, avatar FROM users WHERE id = ?', (new_user_id,))
db_user = cursor.fetchone()
conn.close()
assert db_user[0] == updated_name and db_user[1] == '👩‍🎓'
print("Verified: Profile name and avatar updated in SQLite database!")

# 12. Test Real Password Change & Re-authentication Flow
print("\n--- Testing Real Password Change API ---")
# Wrong current password test
bad_pwd_res = client.post('/api/user/password', json={
    'current_password': 'wrong_password_attempt',
    'new_password': 'newpassword456',
    'confirm_password': 'newpassword456'
})
assert bad_pwd_res.status_code == 400
print("Verified: Incorrect current password rejected properly!")

# Mismatched confirm password test
mismatch_res = client.post('/api/user/password', json={
    'current_password': test_password,
    'new_password': 'newpassword456',
    'confirm_password': 'differentpassword'
})
assert mismatch_res.status_code == 400
print("Verified: Mismatched confirm password rejected!")

# Correct password update
good_pwd_res = client.post('/api/user/password', json={
    'current_password': test_password,
    'new_password': 'newpassword456',
    'confirm_password': 'newpassword456'
})
assert good_pwd_res.status_code == 200
print("Verified: Password changed successfully in database!")

# Verify re-login with old password fails
client.get('/logout')
relogin_old = client.post('/login', json={'email': test_email, 'password': test_password})
assert relogin_old.status_code == 400
print("Verified: Old password no longer authenticates!")

# Verify re-login with NEW password succeeds
relogin_new = client.post('/login', json={'email': test_email, 'password': 'newpassword456'})
assert relogin_new.status_code == 200 and relogin_new.get_json().get('success') is True
print("Verified: New password successfully authenticated student!")

# 13. Test Hamburger Navigation Drawer, Topbar Logo & Flash Screen
print("\n--- Testing Hamburger Navigation Drawer, Topbar Logo & Flash Screen ---")
dash_html = client.get('/dashboard').get_data(as_text=True)

# Test Splash / Flash Screen
assert 'id="splashScreen"' in dash_html, "Splash screen not found in HTML!"

# Test Topbar Logo appears BEFORE Hamburger menu
logo_pos = dash_html.find('class="topbar-brand-link"')
burger_pos = dash_html.find('id="hamburgerMenuBtn"')
assert logo_pos != -1, "Topbar logo link not found!"
assert burger_pos != -1, "Hamburger menu button not found!"
assert logo_pos < burger_pos, f"Logo position ({logo_pos}) must appear BEFORE hamburger menu ({burger_pos})!"

# Test student streak rendered dynamically
assert any(f'<strong>{n}</strong>-day streak' in dash_html for n in [1, 2, 3]), "Student streak was not properly rendered!"

assert 'id="appSidebar"' in dash_html, "Navigation drawer (#appSidebar) not found!"
assert 'id="sidebarCloseBtn"' in dash_html, "Drawer close button not found!"
assert 'id="sidebarProfileSection"' in dash_html, "Drawer profile section not found!"
assert 'id="sidebarUserName"' in dash_html, "User name in drawer not found!"
assert 'id="sidebarUserEmail"' in dash_html, "User email in drawer not found!"
assert 'Edit Profile' in dash_html, "Edit Profile action not found in drawer!"
assert 'Account Settings' in dash_html or 'Settings' in dash_html, "Settings action not found in drawer!"
assert '/logout' in dash_html, "Logout action not found in drawer!"
print("Verified: Splash screen, logo before hamburger icon, 1-day streak, drawer modules, and bottom profile section present in base layout!")

# 14. Test Expanded Listening Comprehension Scenarios & Dialogue Data
print("\n--- Testing Expanded Listening Comprehension Module ---")
from listening_data import LISTENING_DIALOGUES
assert len(LISTENING_DIALOGUES) == 21, f"Expected 21 dialogues, got {len(LISTENING_DIALOGUES)}"

categories = [d['category'] for d in LISTENING_DIALOGUES]
assert categories.count('Formal') == 4, f"Expected 4 Formal dialogues, got {categories.count('Formal')}"
assert categories.count('Informal') == 4, f"Expected 4 Informal dialogues, got {categories.count('Informal')}"
assert categories.count('Professional') == 7, f"Expected 7 Professional dialogues, got {categories.count('Professional')}"
assert categories.count('Friendly') == 6, f"Expected 6 Friendly dialogues, got {categories.count('Friendly')}"

difficulties = set(d['difficulty'] for d in LISTENING_DIALOGUES)
assert {'Beginner', 'Intermediate', 'Advanced'}.issubset(difficulties), f"Missing difficulties: {difficulties}"

# Verify every dialogue has complete metadata, audio, and questions
for d in LISTENING_DIALOGUES:
    assert d['id'] > 0
    assert len(d['title']) > 5
    assert len(d['situation']) > 10
    assert len(d['audio_text']) > 50
    assert len(d['dialogue']) >= 4, f"Dialogue {d['id']} has fewer than 4 turns"
    assert len(d['questions']) >= 2, f"Dialogue {d['id']} has fewer than 2 questions"
    for q in d['questions']:
        assert len(q['options']) in [3, 4], f"Question {q['q_id']} in dialogue {d['id']} does not have 3 or 4 options"
        assert q['correct'].upper() in ['A', 'B', 'C', 'D'], f"Invalid answer {q['correct']}"
        assert len(q['explanation']) > 15, f"Missing or brief explanation in dialogue {d['id']}"

print(f"Verified: All 21 dialogues validated with multi-turn conversations, audio text, MCQs, and explanations!")

# Test category filters on /listening
listen_all = client.get('/listening?category=all')
assert listen_all.status_code == 200
assert 'Active Listening & Comprehension' in listen_all.get_data(as_text=True)

listen_formal = client.get('/listening?category=formal')
assert listen_formal.status_code == 200
formal_html = listen_formal.get_data(as_text=True)
assert 'Speaking with a Professor: Requesting an Extension' in formal_html
assert 'Talking with Friends: Planning a Weekend Hike' not in formal_html

listen_informal = client.get('/listening?category=informal')
assert listen_informal.status_code == 200
informal_html = listen_informal.get_data(as_text=True)
assert 'Talking with Friends: Planning a Weekend Hike' in informal_html
assert 'Speaking with a Professor: Requesting an Extension' not in informal_html

listen_prof = client.get('/listening?category=professional')
assert listen_prof.status_code == 200
prof_html = listen_prof.get_data(as_text=True)
assert 'Job Interviews: STAR Method on Technical Deadlines' in prof_html

listen_friendly = client.get('/listening?category=friendly')
assert listen_friendly.status_code == 200
friendly_html = listen_friendly.get_data(as_text=True)
assert 'Introducing Yourself: Campus Student Tech Society Mixer' in friendly_html

print("Verified: Listening category filters (All, Formal, Informal, Professional, Friendly) work accurately!")

print("\n==================================================")
print("  ALL TESTS PASSED! SpeakUp AI is 100% verified.")
print("==================================================")
