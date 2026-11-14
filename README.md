# SpeakUp AI — English Speaking Practice Assistant 🎙️

**Academic Mini Project**
*Department of Computer Science & Engineering*

---

## 1. Project Overview

**SpeakUp AI** is an interactive, web-based English speaking practice platform built to help college students and beginners overcome speaking hesitation, correct common spoken grammar errors, expand their active vocabulary, and prepare for campus placement interviews.

Many students have strong reading and writing skills, but hesitate when speaking in front of peers, during classroom seminars, or in HR interview rounds. This project provides a judgment-free, self-paced environment where students can speak, receive instant feedback, and track their daily progress.

---

## 2.Key Modules

### Module 1: Landing Page
- Introduction to the platform and practice goals.
- Live interactive preview of a speaking coach dialogue, grammar correction card, and audio visualizer.
- Feature overview and process breakdown (Choose Goal &rarr; Practise &rarr; Improve).

### Module 2: Student Dashboard
- Daily speaking goal tracker (18 / 25 minutes completed).
- Practice statistics: total practice time, completed conversation sessions, fluency score, and new vocabulary learned.
- Weekly practice chart displaying day-by-day minutes practiced.
- Quick navigation to speaking, grammar, and interview modules.

### Module 3: AI Speaking Practice Room
- Topic selection: *Ordering at a Cafe*, *Campus & College Life*, *Job Interview Intro*, and *Casual Chit-chat*.
- Proficiency level selector: Beginner, Intermediate, and Advanced.
- Native voice synthesis using the Web Speech API (`speechSynthesis`) so students can listen to correct spoken pronunciation.
- Speech dictation using browser `SpeechRecognition` via the microphone button.
- Instant Grammar Coach: detects common non-native spoken mistakes (e.g., *"I am agree"*, *"She don't"*, *"Discuss about"*, *"According to me"*) and provides clear, encouraging explanations.

### Module 4: Vocabulary Studio
- Curated word bank with phonetic pronunciation, parts of speech, difficulty tags, definitions, and realistic usage examples.
- Word of the Day spotlight with practical speaking tips.
- Real-time search and category filtering (*Academic*, *Professional*, *Idioms*, *Connectors*).
- Personal bookmarking system saved locally using `localStorage`.

### Module 5: Placement Interview Simulator
- Question bank featuring common HR and campus placement questions.
- Built-in guidance on the **STAR Method** (Situation, Task, Action, Result).
- Speech-to-text dictation and real-time word counting.
- Automated evaluation report: score out of 10, filler-word detection (*"like"*, *"basically"*, *"um"*), grammar check, and high-scoring model answers with audio playback.

---

## 3. Technology Stack

- **Backend:** Python 3 with Flask web framework.
- **Database & Persistence:** SQLite3 relational database (`speakup.db`) with tables for user accounts, chat logs, interview scores, and saved vocabulary.
- **Security:** Werkzeug password hashing (`generate_password_hash`, `check_password_hash`) and secure client session cookies.
- **AI Conversation Engine:** Dual-mode architecture:
  - Connects to **Google Gemini API** (`gemini-1.5-flash`) via secure server-side environment variables (`GEMINI_API_KEY`) and in-browser key connector.
  - Multi-turn local intelligent contextual engine that tracks conversation history and rotates across 60+ dialogue branches without sentence repetition.
- **Frontend:** Semantic HTML5, CSS3 with CSS custom properties (variables), Vanilla JavaScript (ES6+).
- **Speech Technologies:** W3C Web Speech API (`SpeechRecognition` for microphone voice input, `SpeechSynthesis` for native text-to-speech audio).

---

## 4. Database Schema & Architecture

The application uses an embedded relational SQLite database (`speakup.db`) initialized via `database.py`:

```
┌─────────────────────────┐       ┌─────────────────────────────────────┐
│          users          │       │              chat_logs              │
├─────────────────────────┤       ├─────────────────────────────────────┤
│ id (PK, AUTOINCREMENT)  │◄──┐   │ id (PK, AUTOINCREMENT)              │
│ name (TEXT)             │   │   │ user_id (FK -> users.id)            │
│ email (TEXT, UNIQUE)    │   ├───┤ topic (TEXT)                        │
│ password_hash (TEXT)    │   │   │ level (TEXT)                        │
│ created_at (TIMESTAMP)  │   │   │ user_message (TEXT)                 │
└─────────────────────────┘   │   │ ai_response (TEXT)                  │
                              │   │ has_grammar_error (INTEGER 0/1)     │
                              │   │ created_at (TIMESTAMP)              │
                              │   └─────────────────────────────────────┘
                              │   ┌─────────────────────────────────────┐
                              │   │           interview_logs            │
                              │   ├─────────────────────────────────────┤
                              │   │ id (PK, AUTOINCREMENT)              │
                              ├───┤ user_id (FK -> users.id)            │
                              │   │ question_text (TEXT)                │
                              │   │ student_answer (TEXT)               │
                              │   │ score (REAL)                        │
                              │   │ word_count (INTEGER)                │
                              │   │ filler_words (TEXT)                 │
                              │   │ improvement_tip (TEXT)              │
                              │   │ created_at (TIMESTAMP)              │
                              │   └─────────────────────────────────────┘
                              │   ┌─────────────────────────────────────┐
                              │   │             saved_words             │
                              │   ├─────────────────────────────────────┤
                              │   │ id (PK, AUTOINCREMENT)              │
                              └───┤ user_id (FK -> users.id)            │
                                  │ word_id (INTEGER)                   │
                                  │ word_text (TEXT)                    │
                                  │ created_at (TIMESTAMP)              │
                                  │ UNIQUE(user_id, word_id)            │
                                  └─────────────────────────────────────┘
```

---

## 5. Project Directory Structure

```text
speakup-ai/
├── app.py                     # Flask application routes, AI dialogue logic, REST endpoints
├── database.py                # SQLite database initialization, models, queries, auth
├── speakup.db                 # SQLite database file storing persistent student records
├── .env                       # Environment file storing GEMINI_API_KEY securely
├── requirements.txt           # Python dependencies: Flask, Werkzeug
├── test_app.py                # Comprehensive automated project test suite
├── README.md                  # Mini project documentation & viva guide
├── static/
│   ├── css/
│   │   ├── style.css          # Core styles, design tokens, navbar, footer, auth modal
│   │   ├── dashboard.css      # Dashboard layout, metrics, chart styling
│   │   ├── practice.css       # Conversation room, chat bubbles, microphone states
│   │   └── modules.css        # Vocabulary cards and interview layout
│   └── js/
│       ├── main.js            # Navigation, auth modal toggle & fetch, Gemini key connector
│       ├── practice.js        # Multi-turn conversation logic, speech synthesis, grammar alerts
│       ├── vocabulary.js      # Word search, category filters, audio, SQLite bookmark sync
│       └── interview.js       # Question selector, STAR framework evaluation, audio playback
└── templates/
    ├── base.html              # Base Jinja2 layout with user badge and auth modal
    ├── index.html             # Landing page with interactive demo preview
    ├── auth.html              # Dedicated student sign in and account creation page
    ├── dashboard.html         # Student dashboard rendering live SQLite stats
    ├── practice.html          # Practice room with Sophia
    ├── vocabulary.html        # Vocabulary studio
    └── interview.html         # Interview simulator
```

---

## 6. How to Run Locally

### Step 1: Open Terminal / PowerShell
```bash
cd "C:\Users\hp\.gemini\antigravity\scratch\speakup-ai"
```

### Step 2: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the automated test suite
```bash
python test_app.py
```

### Step 4: Run the server
```bash
python app.py
```

### Step 5: Open in your browser
Open your browser and navigate to:  
**`http://127.0.0.1:5000`**

- **Demo Student Account:** `alex.turner@college.edu` | Password: `student123`
- Or click **Create Account / Register** to create your own student account!

---

## 7. Viva / Project Defense Questions & Answers

**Q1:What is the main objective of this mini project?**
> *The objective is to provide college students with an interactive, private platform to practice spoken English. It addresses communication apprehension through simulated scenarios, real-time grammar feedback, and structured interview coaching.*

**Q2: Why use SQLite for data persistence in a college project?**  
> *SQLite is an ACID-compliant relational database built directly into Python (`import sqlite3`). It requires zero external database installation, runs natively on any machine, stores data in a single portable file (`speakup.db`), and fully supports standard SQL queries, primary/foreign keys, and transactions.*

**Q3: How are student passwords protected?**
> *Passwords are never stored in plain text. We use Werkzeug's `generate_password_hash()` which generates salted PBKDF2/SHA-256 hashes, and verify them via `check_password_hash()`, adhering to security best practices.*

**Q4: How does the AI conversation system ensure responses do not repeat?**
> *The engine tracks the multi-turn `conversationHistory` array sent from the frontend. It calculates the conversation turn number, filters out phrases already spoken in the current session, and dynamically branches into context-specific questions and follow-ups. If a Gemini API key is provided, it calls Google Gemini live.*

**Q5: How does the application handle speech input and output without paid APIs?**
> *The application uses the browser's native Web Speech API (`window.speechSynthesis` for text-to-speech audio and `SpeechRecognition` for microphone speech capture). This ensures zero API costs, zero external server latency, and full student privacy.*
