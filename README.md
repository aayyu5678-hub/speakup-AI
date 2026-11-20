# SpeakUp AI — AI English Speaking & Placement Coach Platform 🎙️

**Academic Mini Project**  
*Department of Computer Science & Engineering*

---

## 1. Project Overview

**SpeakUp AI** is an interactive, web-based English speaking and placement readiness platform designed to help college students and early-career professionals overcome speaking hesitation, build natural conversational fluency, expand active vocabulary, and master campus placement interviews.

Many students possess strong reading and technical writing skills, but encounter communication barriers or stage-fright when articulating their ideas spontaneously in group discussions, presentations, or HR interview rounds. **SpeakUp AI** provides a private, judgment-free, self-paced learning environment with instant AI feedback, multi-turn conversational roleplays, listening comprehension drills, and gamified progress tracking.

---

## 2. Key Modules & Features

### 🌟 1. Intro Flash / Splash Screen
- **App-Like First Impression:** Displays on initial application launch with a glowing purple logo, pulsing radar ring, and a 5.5-second gradient loading progress bar.
- **Session-Aware Guarantee:** Uses browser `sessionStorage` so the intro plays once per session on startup and does **not** interrupt the user when switching between modules or features.

### ☰ 2. Responsive Hamburger Navigation Drawer
- **Clean SaaS Navigation:** A smooth slide-in navigation drawer toggled by a three-line hamburger icon (`☰`) on both desktop and mobile.
- **Active State Highlighting:** Visually highlights the active page or module.
- **Integrated Bottom Profile Section:** Displays current student avatar, full name, email, quick access to **Edit Profile**, **Account Settings**, and **Logout**.

### 📊 3. Student Dashboard
- **Personalized Welcome:** Greets the authenticated student dynamically with their registered name.
- **Dynamic Streak Counter:** Starts from **Day 1** for newly registered students and advances dynamically as they complete speaking sessions (with daily calendar pips).
- **Fluency Progress Ring:** Real-time completion percentage based on chat turns, vocabulary bookmarks, and mock interviews.
- **Quick-Access Hub:** Continue Learning card and quick launch buttons for recent modules.

### 🎧 4. Listening Comprehension Studio (Expanded)
- **21 Realistic Multi-Turn Dialogues:** Curated conversations across 4 distinct categories:
  - **Formal Conversations (4):** Academic advising, professor discussions, office inquiries, scheduling appointments.
  - **Informal Conversations (4):** Weekend plans, family talks, hobbies, meeting new peers.
  - **Professional Conversations (6):** Job interviews, sprint workplace meetings, team presentations, project deadlines, customer service.
  - **Friendly Conversations (7):** Polite opinions, offering help, introductions, dinner plans.
- **Audio Playback:** Native speech synthesis with individual turn timestamps and character role labels.
- **Interactive Quizzes:** Multiple-choice comprehension questions with immediate scoring, correct answer highlights, and detailed explanations.
- **Difficulty Tiers:** Categorized into Beginner, Intermediate, and Advanced levels.

### 💬 5. AI Conversation Room (Sophia)
- **AI Persona Sophia:** Interactive dialogue partner specializing in daily campus and professional scenarios.
- **Dual-Engine Architecture:** High-speed cloud LLMs via **Groq AI** (`llama-3.3-70b-versatile` / `gpt-oss-120b`) with resilient multi-turn offline rule-engine fallback.
- **Microphone Dictation:** Live speech-to-text dictation using the browser's `webkitSpeechRecognition`.
- **Spoken Text-to-Speech:** Real-time audio playback using the Web Speech Synthesis API.
- **Scenario Topics:** *Ordering at a Cafe*, *Campus & College Life*, *Job Interview Intro*, and *Casual Chit-chat*.

### 💼 6. Placement Interview Simulator
- **STAR Framework Evaluation:** Guidance for Situation, Task, Action, and Result structured responses.
- **Automated Feedback & Scoring:** Instant scoring out of 10 with word count calculation, STAR rubric breakdown, filler-word detection (*"basically"*, *"like"*, *"um"*), and high-scoring model answers.

### 📖 7. Vocabulary Studio & Dictionary
- **Spotlight Word of the Day:** Rotates daily with phonetics, definition, CEFR difficulty level, and spoken usage tips.
- **Unlimited Dictionary Lookup:** Integrated with the Free Dictionary API for instant definitions and audio pronunciations.
- **Persistent Bookmarks:** Save words directly to the relational database (`saved_words`) with instant bookmark toggling.

### 📈 8. Fluency Analytics & Progress Tracking
- **Competency Radar:** In-depth breakdown across Pronunciation, Spoken Fluency, Grammatical Nuance, and Active Lexicon.
- **Speaking Speed Meter:** Measures Words Per Minute (WPM) during practice sessions.

### 🏆 9. Gamified Achievements
- **Milestone Badges:** Unlockable badges (*First Spoken Words*, *Vocabulary Explorer*, *Active Listener*, *Master Orator*, *Streak Champ*) with XP rewards.

### 👤 10. Student Profile & Account Security
- **Profile Customization:** Choose from expressive student avatars and update display names.
- **Secure Password Updates:** In-database password changes verified against existing salted hashes.

---

## 3. Technology Stack

- **Backend:** Python 3 (3.10 – 3.13) with the **Flask 3.x** web framework.
- **Production Server:** **Gunicorn** WSGI HTTP server (configured for Render and cloud containers).
- **Database Architecture:**
  - **Local Development:** ACID-compliant embedded **SQLite3** (`speakup.db`).
  - **Cloud Production:** Compatible with **MySQL 8.0+** / TiDB Cloud / Aiven MySQL via `PyMySQL` and `cryptography` through connection string detection (`DATABASE_URL` or `MYSQL_*`).
- **AI Inference Engine:**
  - Primary: **Groq API** (`llama-3.3-70b-versatile`, `gpt-oss-120b`) for ultra-low latency conversational generation.
  - Secondary: **Google Gemini API** (`gemini-1.5-flash`).
  - Fallback: Offline intelligent 60+ dialogue branch engine ensuring 100% uptime even without internet access.
- **Frontend Architecture:**
  - Semantic HTML5, CSS3 with modern CSS custom variables (design tokens), Vanilla JavaScript (ES6+).
  - Fully responsive layout supporting mobile drawers, tablet grids, and desktop viewports.
- **Speech Technologies:**
  - W3C **Web Speech API** (`SpeechRecognition` for microphone voice capture and `SpeechSynthesis` for native text-to-speech).
- **Authentication & Security:**
  - Salted PBKDF2 / SHA-256 password hashing with **Werkzeug Security**.
  - Secure session cookies and route-level authentication gates.
  - Zero hardcoded secrets; strict `.gitignore` policy protecting `.env` and `.db` files.

---

## 4. Database Schema

The relational database supports both SQLite and MySQL seamlessly:

```
┌─────────────────────────┐       ┌─────────────────────────────────────┐
│          users          │       │              chat_logs              │
├─────────────────────────┤       ├─────────────────────────────────────┤
│ id (PK, AUTO_INCREMENT) │◄──┐   │ id (PK, AUTO_INCREMENT)             │
│ name (VARCHAR 100)      │   │   │ user_id (FK -> users.id)            │
│ email (VARCHAR 120, UQ) │   ├───┤ topic (VARCHAR 64)                  │
│ password_hash (VARCHAR) │   │   │ level (VARCHAR 32)                  │
│ avatar (VARCHAR 16)     │   │   │ user_message (TEXT)                 │
│ created_at (TIMESTAMP)  │   │   │ ai_response (TEXT)                  │
└─────────────────────────┘   │   │ has_grammar_error (TINYINT)         │
                              │   │ created_at (TIMESTAMP)              │
                              │   └─────────────────────────────────────┘
                              │   ┌─────────────────────────────────────┐
                              │   │           interview_logs            │
                              │   ├─────────────────────────────────────┤
                              │   │ id (PK, AUTO_INCREMENT)             │
                              ├───┤ user_id (FK -> users.id)            │
                              │   │ question_text (TEXT)                │
                              │   │ student_answer (TEXT)               │
                              │   │ score (DECIMAL 3,1)                 │
                              │   │ word_count (INT)                    │
                              │   │ filler_words (VARCHAR 255)          │
                              │   │ improvement_tip (TEXT)              │
                              │   │ created_at (TIMESTAMP)              │
                              │   └─────────────────────────────────────┘
                              │   ┌─────────────────────────────────────┐
                              │   │             saved_words             │
                              │   ├─────────────────────────────────────┤
                              │   │ id (PK, AUTO_INCREMENT)             │
                              └───┤ user_id (FK -> users.id)            │
                                  │ word_id (INT)                       │
                                  │ word_text (VARCHAR 64)              │
                                  │ created_at (TIMESTAMP)              │
                                  │ UNIQUE(user_id, word_id)            │
                                  └─────────────────────────────────────┘
```

---

## 5. Project Directory Structure

```text
speakup-ai/
├── app.py                     # Flask application routes, Groq AI engine, REST endpoints
├── database.py                # Hybrid SQLite/MySQL database layer, models, queries, auth
├── listening_data.py          # 21 comprehensive multi-turn listening comprehension scenarios
├── migrate_to_mysql.py        # Cloud database migration tool (SQLite -> Cloud MySQL)
├── requirements.txt           # Python dependencies (Flask, Gunicorn, PyMySQL, Groq, etc.)
├── Procfile                   # Cloud process execution command for Render / Heroku
├── .env.example               # Safe deployment template for environment variables
├── .gitignore                 # Strict security rules protecting .env, .db, and cache files
├── test_app.py                # 15-suite comprehensive automated test suite
├── README.md                  # Project documentation & viva defense guide
├── static/
│   ├── css/
│   │   ├── style.css          # Design tokens, splash screen, topbar, drawer navigation
│   │   ├── dashboard.css      # Dashboard layout, KPI cards, streak pips, progress rings
│   │   ├── modules.css        # Pathways grid, listening studio cards, vocabulary layout
│   │   └── practice.css       # Conversation room, speech bubbles, mic recording pulse
│   └── js/
│       ├── main.js            # Drawer controls, session-aware 5.5s splash screen, modal logic
│       ├── practice.js        # Multi-turn speech recognition, speech synthesis, AI chat
│       ├── vocabulary.js      # Dictionary API integration, audio pronunciation, bookmarking
│       └── interview.js       # STAR rubric evaluation, filler word detection, scoring
└── templates/
    ├── base.html              # Core layout with topbar logo, hamburger menu, and drawer
    ├── index.html             # Landing page with interactive preview & feature highlights
    ├── auth.html              # Dedicated student sign-in / registration with demo login
    ├── dashboard.html         # Live student dashboard with Day 1 dynamic streak
    ├── modules.html           # Structured curriculum pathways and learning modules
    ├── listening.html         # Listening Comprehension studio with audio & MCQs
    ├── practice.html          # Sophia AI conversation practice room
    ├── interview.html         # Campus placement interview simulator
    ├── vocabulary.html        # Vocabulary studio with spotlight word of the day
    ├── progress.html          # Student fluency analytics & speaking speed metrics
    ├── achievements.html      # Gamified milestone badges and XP level progress
    └── profile.html           # Student profile management, avatar picker & password change
```

---

## 6. How to Run Locally

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed.
- Modern browser (Google Chrome, Microsoft Edge, or Firefox). Chrome or Edge is recommended for Web Speech API recognition.

### Step 1: Open Terminal / PowerShell
```bash
cd "C:\Users\hp\Desktop\speakup-ai"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Create a local `.env` file by copying the template:
```bash
copy .env.example .env
```
Open `.env` and paste your free Groq API key:
```env
GROQ_API_KEY=gsk_your_actual_key_here
```
*(Note: If no API key is provided, the application will automatically run using its built-in offline intelligent conversational engine).*

### Step 4: Run the Automated Test Suite
```bash
python test_app.py
```
*Verify that all 15 test suites pass with `ALL TESTS PASSED! SpeakUp AI is 100% verified.`*

### Step 5: Start the Local Development Server
```bash
python app.py
```

### Step 6: Access the Application
Open your browser and navigate to:  
👉 **`http://127.0.0.1:5000`**

- **New Student:** Click **Register** to create your own account (streak begins from Day 1).
- **One-Click Demo Account:** Click **⚡ One-Click Demo Student Sign In (Alex)** on the login screen for instant evaluation.

---

## 7. Cloud Deployment (Render / Railway / Heroku)

1. **Connect GitHub Repository:** Link your `https://github.com/aayyu5678-hub/speakup-AI.git` repository on Render.
2. **Environment:** Python 3.
3. **Build Command:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Start Command:**
   ```bash
   gunicorn app:app
   ```
5. **Environment Variables:** Add `GROQ_API_KEY` (and optional `DATABASE_URL` for cloud MySQL).

---

## 8. Viva & Project Defense Guide (Key Questions & Answers)

**Q1: What is the primary problem SpeakUp AI solves?**
> *Many graduating engineering students possess solid technical knowledge but lack spontaneous English conversational fluency, causing anxiety during campus placement interviews. SpeakUp AI provides an accessible, private AI coaching environment where students can speak aloud, practice realistic interviews, and receive structured feedback.*

**Q2: How does the application maintain privacy and avoid paid speech API costs?**
> *Voice recognition and speech synthesis use the browser's native W3C Web Speech API (`SpeechRecognition` and `window.speechSynthesis`). Audio is processed locally on the client's device, eliminating third-party audio API costs, reducing latency, and safeguarding student privacy.*

**Q3: How does the AI conversation engine prevent repetitive responses?**
> *The conversation engine tracks multi-turn history (`conversationHistory`) sent from the client. When using cloud LLMs (Groq / Gemini), system prompts strictly instruct the model to branch based on previous student inputs. When operating offline, the fallback engine calculates turn counts and rotates across distinct contextual dialogue branches.*

**Q4: How does the student streak system work?**
> *Streaks are dynamically calculated per student based on active engagement history rather than static demo values. A newly registered student begins at Day 1 (`streak_days = 1`) with only "Today" marked as completed. As the student engages in conversation practice, interview attempts, and vocabulary exercises, their streak dynamically updates.*

**Q5: How does the session-aware splash screen work without annoying the user?**
> *The splash screen displays on initial startup for 5.5 seconds with an animated loading progress bar. Upon first render, `sessionStorage.setItem('speakup_splash_shown', 'true')` marks it as shown for that browser session. When navigating between modules (e.g., Dashboard to Listening or Profile), an inline guard immediately hides the splash overlay before page render, ensuring instant, flicker-free navigation.*

**Q6: How does the application switch between local SQLite and cloud MySQL?**
> *The database abstraction layer in `database.py` dynamically inspects the environment. If `DATABASE_URL` or `MYSQL_HOST` is configured, it connects to the cloud MySQL cluster via `PyMySQL`. Otherwise, it falls back cleanly to local embedded `speakup.db` using Python's standard `sqlite3` module.*

**Q7: How are user credentials protected?**
> *Passwords are never stored in plain text. They are hashed using Werkzeug's implementation of PBKDF2 with SHA-256 and unique per-user salts. All secrets and API keys are read from environment variables and strictly ignored by Git.*
