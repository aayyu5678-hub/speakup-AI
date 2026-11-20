import os
import json
import datetime
import urllib.request
import urllib.error
import urllib.parse
import re
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from database import (
    init_db, register_user, authenticate_user, get_user_by_id,
    save_chat_turn, save_interview_result, toggle_save_word,
    get_user_saved_words, get_student_dashboard_data,
    get_cached_dictionary_word, save_dictionary_word, get_saved_custom_words,
    get_daily_word_cache, set_daily_word_cache,
    update_user_profile, change_user_password, get_user_achievements
)
from listening_data import LISTENING_DIALOGUES

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'speakup-ai-student-mini-project-secret-2026')
app.jinja_env.globals.update(min=min, max=max, int=int, len=len)

ENV_FILE_PATH = os.path.join(os.path.dirname(__file__), '.env')

def load_env_file():
    if os.path.exists(ENV_FILE_PATH):
        try:
            with open(ENV_FILE_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and not os.environ.get(k):
                            os.environ[k] = v
        except Exception as e:
            print("Notice: Error loading .env file:", e)

load_env_file()
init_db()

@app.context_processor
def inject_user():
    user_id = session.get('user_id')
    if user_id:
        return {
            'current_user': {
                'id': user_id,
                'name': session.get('user_name', 'Student'),
                'email': session.get('user_email', ''),
                'avatar': session.get('user_avatar', '')
            }
        }
    return {'current_user': None}

def update_env_variable(key, value):
    key = key.strip()
    value = value.strip()
    os.environ[key] = value
    lines = []
    found = False
    if os.path.exists(ENV_FILE_PATH):
        try:
            with open(ENV_FILE_PATH, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception:
             lines = []
    new_lines = []
    for line in lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            found = True
        else:
            new_lines.append(line)
            
    if not found:
        if not new_lines or not new_lines[0].startswith("#"):
            new_lines.insert(0, "# SpeakUp AI - Environment Configuration\n")
        new_lines.append(f"{key}={value}\n")
        
    try:
        with open(ENV_FILE_PATH, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    except Exception as e:
        print("Error saving to .env:", e)
        return False

def save_env_key(api_key, key_name="GEMINI_API_KEY"):
    return update_env_variable(key_name, api_key)

def _groq_headers(api_key):
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key.strip()}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

def fetch_groq_models(api_key):
    """Fetch available chat model IDs from Groq /openai/v1/models."""
    try:
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/models",
            headers=_groq_headers(api_key)
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m.get("id", "") for m in data.get("data", []) if m.get("id")]
            # Exclude speech-to-text, text-to-speech (orpheus/tts), and safety guard models
            excluded = ("whisper", "tts", "orpheus", "guard", "safeguard", "prompt-guard")
            return [m for m in models if not any(ex in m.lower() for ex in excluded)]
    except Exception as e:
        print(f"Could not fetch Groq models list: {e}")
        return []

def _send_groq_request(api_key, model_name, messages, max_tokens=700, temperature=0.7, timeout=12):
    """Send a chat completion request to Groq with a standard User-Agent to avoid Cloudflare 403 blocks."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=_groq_headers(api_key)
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

_WORKING_GROQ_MODEL = None
_CACHED_GROQ_MODELS = None
_GROQ_MODEL_KEY_HASH = None

def _rank_groq_model(model_name):
    ml = model_name.lower()
    if "llama-3.3" in ml or "llama-4" in ml:
        return (0, ml)
    if "gpt-oss-120b" in ml:
        return (1, ml)
    if "llama" in ml:
        return (2, ml)
    if "gpt-oss-20b" in ml or "qwen" in ml:
        return (3, ml)
    if "gemma" in ml:
        return (4, ml)
    return (5, ml)

def _get_candidate_groq_models(api_key):
    global _WORKING_GROQ_MODEL, _CACHED_GROQ_MODELS, _GROQ_MODEL_KEY_HASH
    key_sig = (api_key[:10] + api_key[-4:]) if len(api_key) > 14 else api_key
    if _GROQ_MODEL_KEY_HASH != key_sig:
        _WORKING_GROQ_MODEL = None
        _CACHED_GROQ_MODELS = None
        _GROQ_MODEL_KEY_HASH = key_sig

    if _WORKING_GROQ_MODEL:
        fallback_list = _CACHED_GROQ_MODELS or []
        return [_WORKING_GROQ_MODEL] + [m for m in fallback_list if m != _WORKING_GROQ_MODEL]

    if _CACHED_GROQ_MODELS is None:
        live_models = fetch_groq_models(api_key)
        if live_models:
            _CACHED_GROQ_MODELS = sorted(live_models, key=_rank_groq_model)
        else:
            _CACHED_GROQ_MODELS = ["llama-3.3-70b-versatile", "openai/gpt-oss-120b", "llama-3.1-8b-instant", "qwen/qwen3.8-27b"]

    return list(_CACHED_GROQ_MODELS)

def _run_groq_with_fallback(api_key, messages, max_tokens=700, temperature=0.7, timeout=12):
    """Execute a Groq chat request across prioritized available models, caching the working one."""
    global _WORKING_GROQ_MODEL
    api_key = (api_key or "").strip()
    if not api_key or "your_groq_api_key_here" in api_key:
        return None, None, "Groq API key is missing."

    models_to_try = _get_candidate_groq_models(api_key)
    last_error = "Unable to connect to Groq."

    for model_name in models_to_try:
        try:
            data = _send_groq_request(
                api_key=api_key,
                model_name=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout
            )
            choices = data.get("choices", [])
            if choices and "message" in choices[0]:
                raw_text = choices[0]["message"].get("content", "")
                if raw_text and raw_text.strip():
                    _WORKING_GROQ_MODEL = model_name
                    return raw_text, model_name, None
            last_error = "Groq key connected but returned empty response."
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            try:
                msg = json.loads(err_body).get("error", {}).get("message", f"HTTP {e.code}")
            except Exception:
                msg = f"HTTP {e.code}"
            last_error = f"Groq Error: {msg}"
            print(f"Groq API attempt on {model_name} failed: HTTP {e.code} {msg[:160]}")
            if e.code in (401, 403):
                return None, None, last_error
        except Exception as e:
            last_error = f"Connection failed: {str(e)}"
            print(f"Groq API attempt on {model_name} failed: {e}")

    return None, None, last_error

def test_groq_key(api_key):
    api_key = (api_key or "").strip()
    if not api_key:
        return False, "Groq API key cannot be empty."
    raw_text, model_name, err = _run_groq_with_fallback(
        api_key=api_key,
        messages=[{"role": "user", "content": "Reply with only OK."}],
        max_tokens=200,
        temperature=0.2,
        timeout=10
    )
    if raw_text:
        return True, f"Successfully connected to Groq AI ({model_name})!"
    return False, err or "Could not verify Groq API key."

def test_gemini_key(api_key):
    api_key = api_key.strip()
    if not api_key:
        return False, "API key is empty."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": "Hello"}]}],
        "generationConfig": {"maxOutputTokens": 10}
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("candidates"):
                return True, "Successfully connected to Google Gemini!"
            return False, "Key connected but received empty response."
    except urllib.error.HTTPError as e:
        try:
            err_data = json.loads(e.read().decode("utf-8"))
            msg = err_data.get("error", {}).get("message", f"HTTP {e.code}")
            return False, f"Google Error: {msg}"
        except Exception:
            return False, f"API rejected key (HTTP {e.code}). Please check your key."
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

VOCABULARY_DATA = [
    {
        "id": 1,
        "word": "Articulate",
        "phonetic": "/ɑːrˈtɪk.jə.lət/",
        "part_of_speech": "Adjective",
        "category": "Academic",
        "difficulty": "Advanced",
        "definition": "Able to express thoughts, ideas, and feelings clearly and effectively in speech.",
        "example": "She gave an articulate presentation that convinced the entire evaluation committee.",
        "synonyms": ["Eloquent", "Expressive", "Lucid"],
        "tip": "Use this in resumes or interviews instead of 'good speaker'."
    },
    {
        "id": 2,
        "word": "Elaborate",
        "phonetic": "/ɪˈlæb.ə.reɪt/",
        "part_of_speech": "Verb",
        "category": "Professional",
        "difficulty": "Intermediate",
        "definition": "To add more details, explanation, or context to what has already been said.",
        "example": "Could you please elaborate on your role in this software project?",
        "synonyms": ["Expand", "Clarify", "Detail"],
        "tip": "A polite phrase in meetings: 'Could you elaborate on that point?'"
    },
    {
        "id": 3,
        "word": "Perseverance",
        "phonetic": "/ˌpɜː.sɪˈvɪə.rəns/",
        "part_of_speech": "Noun",
        "category": "Professional",
        "difficulty": "Intermediate",
        "definition": "Continued effort and determination to achieve something despite difficulties or failure.",
        "example": "Through sheer perseverance, the team managed to launch the application ahead of deadline.",
        "synonyms": ["Dedication", "Persistence", "Tenacity"],
        "tip": "Great keyword when answering interview questions about overcoming challenges."
    },
    {
        "id": 4,
        "word": "Nuance",
        "phonetic": "/ˈnjuː.ɑːns/",
        "part_of_speech": "Noun",
        "category": "Academic",
        "difficulty": "Advanced",
        "definition": "A subtle or slight degree of difference in meaning, feeling, opinion, or tone.",
        "example": "To master spoken English, it helps to understand cultural nuances in polite conversation.",
        "synonyms": ["Subtlety", "Fine distinction", "Shade"],
        "tip": "Say 'cultural nuances' when describing cross-cultural communication."
    },
    {
        "id": 5,
        "word": "Pragmatic",
        "phonetic": "/præɡˈmæt.ɪk/",
        "part_of_speech": "Adjective",
        "category": "Professional",
        "difficulty": "Advanced",
        "definition": "Dealing with things sensibly and realistically based on practical rather than theoretical considerations.",
        "example": "The professor suggested a pragmatic approach to testing the project code under real user conditions.",
        "synonyms": ["Practical", "Sensible", "Realistic"],
        "tip": "Use in interviews: 'I take a pragmatic approach to problem-solving.'"
    },
    {
        "id": 6,
        "word": "Break the ice",
        "phonetic": "/breɪk ðiː aɪs/",
        "part_of_speech": "Idiom",
        "category": "Everyday Idioms",
        "difficulty": "Beginner",
        "definition": "To make people feel more relaxed and comfortable in a social or introductory situation.",
        "example": "The team manager organized a fun quiz to break the ice with the new interns.",
        "synonyms": ["Warm up", "Ease tension", "Initiate conversation"],
        "tip": "A classic everyday English idiom used in team meetings and discussions."
    },
    {
        "id": 7,
        "word": "Furthermore",
        "phonetic": "/ˌfɜː.ðəˈmɔːr/",
        "part_of_speech": "Connector",
        "category": "Connectors",
        "difficulty": "Intermediate",
        "definition": "In addition to what has already been stated; used to introduce a further related point.",
        "example": "The tool is easy to use; furthermore, it reduces speaking hesitation for shy students.",
        "synonyms": ["Moreover", "Additionally", "In addition"],
        "tip": "Use 'Furthermore' to link two strong arguments in your presentation."
    },
    {
        "id": 8,
        "word": "Cohesive",
        "phonetic": "/kəʊˈhiː.sɪv/",
        "part_of_speech": "Adjective",
        "category": "Academic",
        "difficulty": "Advanced",
        "definition": "Forming a united, logical, and well-integrated whole.",
        "example": "A cohesive group of classmates collaborated smoothly to prepare for campus placements.",
        "synonyms": ["United", "Consistent", "Harmonious"],
        "tip": "Describe a successful team as a 'cohesive and supportive unit'."
    },
    {
        "id": 9,
        "word": "In a nutshell",
        "phonetic": "/ɪn ə ˈnʌt.ʃɛl/",
        "part_of_speech": "Idiom",
        "category": "Everyday Idioms",
        "difficulty": "Beginner",
        "definition": "In very few words; as a brief, concise summary.",
        "example": "In a nutshell, SpeakUp AI helps you practice speaking without fear of judgment.",
        "synonyms": ["Briefly", "To sum up", "In summary"],
        "tip": "Use when concluding a quick verbal answer in discussions."
    },
    {
        "id": 10,
        "word": "Unravel",
        "phonetic": "/ʌnˈræv.əl/",
        "part_of_speech": "Verb",
        "category": "Everyday Idioms",
        "difficulty": "Intermediate",
        "definition": "To clarify, solve, or untangle a complicated problem or mystery.",
        "example": "With daily practice, students begin to unravel the tricky rules of English prepositions.",
        "synonyms": ["Solve", "Untangle", "Decipher"],
        "tip": "Great for explaining debugging or resolving complex logic."
    },
    {
        "id": 11,
        "word": "Resilient",
        "phonetic": "/rɪˈzɪl.jənt/",
        "part_of_speech": "Adjective",
        "category": "Professional",
        "difficulty": "Intermediate",
        "definition": "Able to recover quickly from difficulties, setbacks, or tough situations.",
        "example": "Staying resilient after an initial rejection helped me improve and land a great role.",
        "synonyms": ["Adaptable", "Tough", "Resourceful"],
        "tip": "Use in behavioral interviews when discussing how you handle pressure."
    },
    {
        "id": 12,
        "word": "Concise",
        "phonetic": "/kənˈsaɪs/",
        "part_of_speech": "Adjective",
        "category": "Academic",
        "difficulty": "Intermediate",
        "definition": "Giving a lot of clear information using few words; brief but comprehensive.",
        "example": "Make sure your project summary is concise so panelists stay focused on your impact.",
        "synonyms": ["Brief", "Succinct", "To the point"],
        "tip": "Say 'To keep my answer concise...' before delivering a sharp 30-second overview."
    },
    {
        "id": 13,
        "word": "Proactive",
        "phonetic": "/ˌprəʊˈæk.tɪv/",
        "part_of_speech": "Adjective",
        "category": "Professional",
        "difficulty": "Beginner",
        "definition": "Creating or controlling a situation by taking action early rather than waiting to react.",
        "example": "Being proactive about asking questions saved our team days of rework.",
        "synonyms": ["Initiative-taking", "Forward-thinking", "Resourceful"],
        "tip": "Hiring managers love hearing concrete examples of proactive behavior."
    },
    {
        "id": 14,
        "word": "Get the ball rolling",
        "phonetic": "/ɡɛt ðə bɔːl ˈrəʊ.lɪŋ/",
        "part_of_speech": "Idiom",
        "category": "Everyday Idioms",
        "difficulty": "Beginner",
        "definition": "To start an activity, project, or conversation smoothly.",
        "example": "Let's review today's agenda first to get the ball rolling on our group presentation.",
        "synonyms": ["Kick off", "Initiate", "Begin"],
        "tip": "A friendly, natural opener for group discussions and team calls."
    },
    {
        "id": 15,
        "word": "Nevertheless",
        "phonetic": "/ˌnɛv.ə.ðəˈlɛs/",
        "part_of_speech": "Connector",
        "category": "Connectors",
        "difficulty": "Advanced",
        "definition": "In spite of what has just been mentioned; however.",
        "example": "The timeline was tight; nevertheless, our team delivered every feature on schedule.",
        "synonyms": ["However", "Nonetheless", "Even so"],
        "tip": "Use 'nevertheless' when acknowledging a challenge before highlighting a positive result."
    }
]

INTERVIEW_QUESTIONS = [
    {
        "id": 1,
        "category": "HR & Behavioral",
        "question": "Tell me about yourself and your background.",
        "difficulty": "Essential",
        "target_duration": "90 seconds",
        "star_advice": "Focus on the Present (your current studies/role), Past (key achievements/learnings), and Future (why you are excited for this opportunity).",
        "model_answer": "Certainly! I am a computer science student with a strong focus on building user-friendly web applications and learning modern technologies. Over the past two years, I have developed several academic projects, including an AI-assisted language learning tool. I enjoy collaborating in teams and solving practical problems. I look forward to applying my technical skills and communication abilities to contribute effectively."
    },
    {
        "id": 2,
        "category": "HR & Behavioral",
        "question": "What is your greatest strength, and how has it helped you in your projects?",
        "difficulty": "Intermediate",
        "target_duration": "60 seconds",
        "star_advice": "State your strength clearly, give a concrete example of when you demonstrated it, and describe the positive result.",
        "model_answer": "My greatest strength is my curiosity and adaptability. When our team had to build a web project within two weeks using a framework I had not used before, I spent the first weekend reading the documentation, building prototypes, and sharing notes with my team. As a result, our team finished ahead of schedule and achieved top marks in the review."
    },
    {
        "id": 3,
        "category": "College & Internships",
        "question": "Describe a challenge you faced in a group project and how you resolved it.",
        "difficulty": "Intermediate",
        "target_duration": "90 seconds",
        "star_advice": "Use the STAR method: Situation (project context), Task (the disagreement or delay), Action (how you communicated empathetically), Result (successful delivery).",
        "model_answer": "During our final semester project, our team had conflicting opinions regarding which database to adopt. I suggested that each member create a 5-minute benchmark comparison based on our project requirements: speed, cost, and simplicity. We held an open discussion, evaluated the results objectively, and chose the optimal solution together. We submitted on time with great team morale."
    },
    {
        "id": 4,
        "category": "Situational",
        "question": "Where do you see yourself professionally in the next three to five years?",
        "difficulty": "Intermediate",
        "target_duration": "60 seconds",
        "star_advice": "Demonstrate ambition balanced with commitment: learning, mastering core skills, taking mentorship responsibilities, and adding value.",
        "model_answer": "In the next three to five years, I see myself growing into a dependable software engineer who writes clean code and helps mentor new team members. I want to deepen my expertise in full-stack architecture, contribute to real-world applications, and continuously refine my communication and problem-solving abilities."
    }
]

COMMON_GRAMMAR_RULES = [
    {
        "pattern": r"\bi\s+am\s+agree\b",
        "correction": "I agree",
        "explanation": "'Agree' is a verb, not an adjective. Say 'I agree' rather than 'I am agree'."
    },
    {
        "pattern": r"\b(she|he|it)\s+don't\b",
        "correction": "\\1 doesn't",
        "explanation": "With third-person singular subjects (he, she, it), use 'doesn't' instead of 'don't'."
    },
    {
        "pattern": r"\b(she|he|it)\s+have\b",
        "correction": "\\1 has",
        "explanation": "With third-person singular subjects (he, she, it), use 'has' instead of 'have'."
    },
    {
        "pattern": r"\b(they|we|you)\s+is\b",
        "correction": "\\1 are",
        "explanation": "With plural subjects (they, we, you), use 'are' instead of 'is'."
    },
    {
        "pattern": r"\b(they|we|you)\s+was\b",
        "correction": "\\1 were",
        "explanation": "With plural subjects in past tense, use 'were' instead of 'was'."
    },
    {
        "pattern": r"\bi\s+is\b",
        "correction": "I am",
        "explanation": "The first-person singular pronoun 'I' always pairs with 'am' in the present tense."
    },
    {
        "pattern": r"\b(did\s+not|didn't)\s+(went|saw|told|ate|came|knew|took|gave|wrote)\b",
        "correction": "did not \\2",
        "explanation": "The auxiliary verb 'did' already carries past tense. Pair with base verb form (e.g. 'didn't go', 'didn't see')."
    },
    {
        "pattern": r"\bdid\s+went\b",
        "correction": "did go",
        "explanation": "The auxiliary 'did' requires base form 'go'."
    },
    {
        "pattern": r"\bdid\s+saw\b",
        "correction": "did see",
        "explanation": "The auxiliary 'did' requires base form 'see'."
    },
    {
        "pattern": r"\bdon't\s+have\s+no\b",
        "correction": "doesn't have any",
        "explanation": "Avoid double negatives in English. Use 'doesn't have any' or 'has no'."
    },
    {
        "pattern": r"\bgo\s+to\s+([a-zA-Z\s]+)\s+yesterday\b",
        "correction": "went to \\1 yesterday",
        "explanation": "The past time indicator 'yesterday' requires simple past tense 'went to'."
    },
    {
        "pattern": r"\bdiscuss\s+about\b",
        "correction": "discuss",
        "explanation": "The verb 'discuss' already means 'talk about', so 'about' is redundant. Say 'let's discuss the project'."
    },
    {
        "pattern": r"\baccording\s+to\s+me\b",
        "correction": "In my opinion / From my perspective",
        "explanation": "'According to' is used for third parties or references. When expressing your own view, use 'In my opinion' or 'From my perspective'."
    },
    {
        "pattern": r"\blisten\s+(music|me|the\s+teacher)\b",
        "correction": "listen to \\1",
        "explanation": "Always use the preposition 'to' with 'listen': 'listen to music'."
    },
    {
        "pattern": r"\bi\s+have\s+(\d{1,2})\s+years\s+old\b",
        "correction": "I am \\1 years old",
        "explanation": "In English, use the verb 'to be' for age: 'I am 21 years old'."
    },
    {
        "pattern": r"\bcan\s+able\s+to\b",
        "correction": "can",
        "explanation": "'Can' and 'able to' express the same meaning. Using them together is repetitive. Use 'can' or 'am able to'."
    },
    {
        "pattern": r"\bi\s+am\s+having\b",
        "correction": "I have",
        "explanation": "Verbs of possession (have, own) describe states, not continuous actions. Say 'I have' rather than 'I am having'."
    },
    {
        "pattern": r"\bi\s+am\s+knowing\b",
        "correction": "I know",
        "explanation": "'Know' is a stative verb. Use simple present 'I know'."
    },
    {
        "pattern": r"\brevert\s+back\b",
        "correction": "reply",
        "explanation": "'Revert' already means to return. Using 'back' is redundant. Say 'reply' or 'get back to me'."
    },
    {
        "pattern": r"\b(did\s+not|didn't)\s+told\b",
        "correction": "\\1 tell",
        "explanation": "The auxiliary 'did' already carries past tense. Pair with base form 'tell'."
    },
    {
        "pattern": r"\bone\s+of\s+my\s+friend\b",
        "correction": "one of my friends",
        "explanation": "'One of' is followed by a plural noun: 'one of my friends'."
    },
    {
        "pattern": r"\bgive\s+an?\s+exam\b",
        "correction": "take an exam",
        "explanation": "Students 'take' or 'sit for' an exam; teachers 'give' the exam."
    },
    {
        "pattern": r"\bpass\s+out\s+from\s+college\b",
        "correction": "graduated from college",
        "explanation": "In standard English, 'pass out' means to faint. Use 'graduate from college'."
    },
    {
        "pattern": r"\bout\s+of\s+station\b",
        "correction": "out of town",
        "explanation": "In modern global English, use 'out of town' or 'away'."
    },
    {
        "pattern": r"\bmarried\s+with\b",
        "correction": "married to",
        "explanation": "The preposition following 'married' is 'to', not 'with'."
    },
    {
        "pattern": r"\bcongratulate\s+for\b",
        "correction": "congratulate on",
        "explanation": "We say 'congratulate on' your success or achievement."
    },
    {
        "pattern": r"\binformations\b",
        "correction": "information",
        "explanation": "'Information' is an uncountable noun with no plural 's'."
    },
    {
        "pattern": r"\badvices\b",
        "correction": "advice",
        "explanation": "'Advice' is an uncountable noun. Use 'pieces of advice' or simply 'advice'."
    },
    {
        "pattern": r"\bfurnitures\b",
        "correction": "furniture",
        "explanation": "'Furniture' is an uncountable noun with no plural 's'."
    },
    {
        "pattern": r"\bwhere\s+you\s+are\s+going\?",
        "correction": "Where are you going?",
        "explanation": "In English questions, invert auxiliary verb and subject: 'Where are you going?'."
    },
    {
        "pattern": r"\bwhat\s+you\s+are\s+doing\?",
        "correction": "What are you doing?",
        "explanation": "In English questions, invert auxiliary verb and subject: 'What are you doing?'."
    }
]

def analyze_student_grammar(text):
    if not text:
        return []
    corrections = []
    text_lower = text.lower()
    for rule in COMMON_GRAMMAR_RULES:
        match = re.search(rule["pattern"], text_lower)
        if match:
            found_str = match.group(0)
            sug_str = re.sub(rule["pattern"], rule["correction"], found_str, flags=re.IGNORECASE)
            corrections.append({
                "found": found_str,
                "incorrect": found_str,
                "suggestion": sug_str,
                "explanation": rule["explanation"],
                "rule": rule["explanation"]
            })
    return corrections

def evaluate_sentence_ai_and_rules(text):
    """
    Intelligent sentence evaluator:
    1. Leverages Groq AI for deep grammar, spelling, tense, and spoken phrasing analysis.
    2. Falls back seamlessly to comprehensive local rule engine if offline.
    """
    text = (text or "").strip()
    if not text:
        return {
            "has_issues": False,
            "original": "",
            "refined": "",
            "score": 100,
            "issues": []
        }

    api_key = os.environ.get("GROQ_API_KEY")
    # 1. Attempt Groq AI evaluation
    if api_key and api_key.strip() and "your_groq_api_key_here" not in api_key:
        prompt = (
            "You are an expert English grammar coach and placement interview speech evaluator.\n"
            f'Sentence: "{text}"\n\n'
            "Analyze the sentence for any grammatical errors, tense mismatches, subject-verb agreement problems, "
            "awkward prepositions, spelling mistakes, double negatives, or redundant phrasing.\n"
            "Use single quotes 'example' inside text values for quoted terms. Never use raw unescaped double quotes inside values.\n"
            "Respond in valid strict JSON ONLY (no markdown code blocks, no backticks, no other text):\n"
            "{\n"
            '  "has_issues": true,\n'
            '  "refined": "the exact corrected, natural right sentence with proper capitalization and punctuation",\n'
            '  "score": 75,\n'
            '  "issues": [\n'
            '    {\n'
            '      "incorrect": "the wrong phrase",\n'
            '      "suggestion": "the correct replacement",\n'
            '      "explanation": "clear grammar rule explanation"\n'
            '    }\n'
            '  ]\n'
            "}"
        )
        try:
            raw_text, model_name, err = _run_groq_with_fallback(
                api_key=api_key,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=450,
                temperature=0.1,
                timeout=8
            )
            if raw_text:
                cleaned = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL | re.IGNORECASE).strip()
                cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
                cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE).strip()
                
                parsed = None
                json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group(0))
                    except Exception:
                        ref_m = re.search(r'"refined"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', cleaned)
                        if ref_m:
                            parsed = {
                                "has_issues": True,
                                "refined": ref_m.group(1),
                                "score": 75,
                                "issues": []
                            }

                if parsed:
                    refined = parsed.get("refined", "").strip()
                    has_issues = bool(parsed.get("has_issues", False))
                    score = int(parsed.get("score", 95 if not has_issues else 75))
                    issues_raw = parsed.get("issues", [])
                    clean_issues = []
                    if isinstance(issues_raw, list):
                        for iss in issues_raw:
                            if isinstance(iss, dict) and iss.get("incorrect") and iss.get("suggestion"):
                                clean_issues.append({
                                    "incorrect": _normalize_punctuation(str(iss.get("incorrect")).strip()),
                                    "suggestion": _normalize_punctuation(str(iss.get("suggestion")).strip()),
                                    "explanation": _normalize_punctuation(str(iss.get("explanation", "")).strip())
                                })
                    if refined:
                        return {
                            "success": True,
                            "has_issues": has_issues or bool(clean_issues),
                            "original": text,
                            "refined": _normalize_punctuation(refined),
                            "score": score,
                            "issues": clean_issues
                        }
        except Exception as e:
            print(f"Groq Sentence AI evaluation fallback: {e}")

    # 2. Comprehensive rule-based fallback
    issues = analyze_student_grammar(text)
    refined = text
    for issue in issues:
        inc = issue.get("incorrect", "")
        sug = issue.get("suggestion", "")
        if inc and sug:
            pattern = re.compile(re.escape(inc), re.IGNORECASE)
            refined = pattern.sub(sug, refined)

    refined = refined.strip()
    if refined:
        refined = refined[0].upper() + refined[1:]
        if not refined.endswith(('.', '?', '!')):
            refined += '.'

    score = 98 if not issues else max(50, min(92, 100 - len(issues) * 15))
    return {
        "success": True,
        "has_issues": bool(issues),
        "original": text,
        "refined": refined,
        "score": score,
        "issues": issues
    }

def _normalize_punctuation(text):
    """Replace curly quotes and non-breaking hyphens with clean ASCII equivalents for speech/UI/Windows consoles."""
    replacements = {
        "\u2018": "'", "\u2019": "'", "\u201a": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2014": " - ",
        "\u2026": "...", "\u00a0": " "
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text

def parse_llm_response(raw_text):
    suggested_vocab = ["In my opinion", "Furthermore", "Could you elaborate"]
    clean_reply = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL | re.IGNORECASE).strip()
    clean_reply = _normalize_punctuation(clean_reply)

    match = re.search(r"SUGGESTIONS:\s*(.*)$", clean_reply, re.IGNORECASE | re.MULTILINE)
    if match:
        sug_part = match.group(1).strip()
        clean_reply = clean_reply[:match.start()].strip()
        raw_items = sug_part.split("|") if "|" in sug_part else re.findall(r'(?:"[^"]*"|\'[^\']*\'|[^,])+', sug_part)
        words = [
            w.strip().strip("[]").strip('"\'').strip()
            for w in raw_items
        ]
        words = [w for w in words if w]
        if words:
            suggested_vocab = words[:3]

    return clean_reply, suggested_vocab

def _extract_json_object(raw_text):
    """Strip reasoning tags and parse the first JSON object from an LLM response."""
    if not raw_text:
        return None
    cleaned = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL | re.IGNORECASE).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except Exception:
        return None

def _normalize_vocab_entry(entry, fallback_word=""):
    diff_raw = str(entry.get("difficulty", "Intermediate")).strip().capitalize()
    difficulty = diff_raw if diff_raw in ("Beginner", "Intermediate", "Advanced") else "Intermediate"
    syns = entry.get("synonyms") or []
    if isinstance(syns, str):
        syns = [s.strip() for s in syns.split(",") if s.strip()]
    synonyms = []
    for s in syns[:3]:
        sc = _normalize_punctuation(str(s).strip())
        if sc:
            synonyms.append(sc[0].upper() + sc[1:])

    word_clean = _normalize_punctuation(str(entry.get("word") or fallback_word).strip())
    if word_clean:
        word_clean = word_clean[0].upper() + word_clean[1:]

    pos_clean = _normalize_punctuation(str(entry.get("part_of_speech") or "Word").strip())
    if pos_clean:
        pos_clean = pos_clean[0].upper() + pos_clean[1:]

    return {
        "word": word_clean,
        "phonetic": _normalize_punctuation(str(entry.get("phonetic") or "").strip()),
        "part_of_speech": pos_clean,
        "category": _normalize_punctuation(str(entry.get("category") or "Dictionary").strip()),
        "difficulty": difficulty,
        "definition": _normalize_punctuation(str(entry.get("definition") or "").strip()),
        "example": _normalize_punctuation(str(entry.get("example") or "").strip()),
        "synonyms": synonyms,
        "tip": _normalize_punctuation(str(entry.get("tip") or "Try using this word naturally in a conversation with Sophia.").strip())
    }

def _lookup_word_with_groq(query):
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key or "your_groq_api_key_here" in api_key:
        return None, False

    prompt = (
        f'Look up the English word, term, phrase, or idiom: "{query}".\n'
        f'If "{query}" is gibberish or NOT a real English word, valid technical term, or recognizable expression, reply ONLY with JSON: {{"found": false}}\n'
        f'Otherwise reply ONLY with strict JSON:\n'
        f'{{\n'
        f'  "found": true,\n'
        f'  "word": "Properly capitalized word/phrase",\n'
        f'  "phonetic": "/IPA pronunciation/",\n'
        f'  "part_of_speech": "Noun/Verb/Adjective/Adverb/Idiom/Phrase",\n'
        f'  "category": "Academic | Professional | Everyday Idioms | Connectors | Dictionary",\n'
        f'  "difficulty": "Beginner | Intermediate | Advanced",\n'
        f'  "definition": "Clear, complete meaning (1-2 sentences; mention a second common meaning briefly if relevant).",\n'
        f'  "example": "Natural spoken sentence using the word clearly.",\n'
        f'  "synonyms": ["syn1", "syn2", "syn3"],\n'
        f'  "tip": "Practical spoken English usage tip (1 sentence)."\n'
        f'}}'
    )
    raw_text, model_name, _ = _run_groq_with_fallback(
        api_key=api_key,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700,
        temperature=0.3,
        timeout=12
    )
    parsed = _extract_json_object(raw_text)
    if not parsed:
        return None, False
    if parsed.get("found") is False:
        return None, True
    if parsed.get("definition"):
        entry = _normalize_vocab_entry(parsed, fallback_word=query.strip().title())
        entry["source"] = f"groq:{model_name}"
        return entry, False
    return None, False

def _lookup_word_with_dictionary_api(query):
    """Free dictionaryapi.dev lookup fallback (requires no API key)."""
    clean = query.strip()
    if not clean or " " in clean:
        return None
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(clean.lower())}"
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "SpeakUp-AI/1.0"}
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if not isinstance(data, list) or not data:
                return None
            first = data[0]
            word = first.get("word", clean).capitalize()
            phonetic = first.get("phonetic", "")
            if not phonetic:
                for p in first.get("phonetics", []):
                    if p.get("text"):
                        phonetic = p["text"]
                        break

            meanings = first.get("meanings", [])
            if not meanings:
                return None
            pos = meanings[0].get("partOfSpeech", "Word").capitalize()
            defs = meanings[0].get("definitions", [])
            if not defs:
                return None
            definition = defs[0].get("definition", "")
            example = ""
            synonyms = []
            for m in meanings:
                synonyms.extend(m.get("synonyms", []))
                for d in m.get("definitions", []):
                    if not example and d.get("example"):
                        example = d["example"]
                    synonyms.extend(d.get("synonyms", []))
            if not example:
                example = f"We discussed how to use '{word.lower()}' clearly in everyday spoken English."

            dedup_syns = []
            for s in synonyms:
                sc = s.capitalize()
                if sc not in dedup_syns and sc.lower() != word.lower():
                    dedup_syns.append(sc)
                if len(dedup_syns) >= 3:
                    break

            entry = _normalize_vocab_entry({
                "word": word,
                "phonetic": phonetic,
                "part_of_speech": pos,
                "category": "Dictionary",
                "difficulty": "Intermediate",
                "definition": definition,
                "example": example,
                "synonyms": dedup_syns,
                "tip": f"Practice saying '{word.lower()}' aloud in a short sentence in the Practice Room."
            })
            entry["source"] = "dictionary-api"
            return entry
    except Exception as e:
        print(f"Dictionary API lookup notice for '{clean}': {e}")
        return None

def lookup_any_vocabulary_word(query):
    """Look up ANY word or idiom across local curated cards, SQLite cache, Groq AI, and Free Dictionary API."""
    clean = re.sub(r"\s+", " ", (query or "").strip())
    if not clean:
        return None, "Please enter a word or phrase to look up."
    if len(clean) > 80:
        return None, "Search query is too long. Please enter a single word or short phrase."

    # 1. Exact local curated match
    lower_q = clean.lower()
    for item in VOCABULARY_DATA:
        if item["word"].lower() == lower_q:
            return dict(item), None

    # 2. Cached SQLite dictionary entry
    cached = get_cached_dictionary_word(lower_q)
    if cached:
        return cached, None

    # 3. Groq AI unlimited lookup
    groq_entry, explicitly_not_found = _lookup_word_with_groq(clean)
    if groq_entry:
        saved = save_dictionary_word(groq_entry)
        return (saved or groq_entry), None

    # 4. Free Dictionary API fallback (works without API key; also double-checks single words)
    dict_entry = _lookup_word_with_dictionary_api(clean)
    if dict_entry:
        saved = save_dictionary_word(dict_entry)
        return (saved or dict_entry), None

    if explicitly_not_found:
        return None, f"No English definition found for '{clean}'. Please check the spelling or try another word."
    return None, f"Could not find a definition for '{clean}' right now. Try another word or check your connection."

_RECENT_DAILY_WORDS = set()
_DAILY_FALLBACK_OFFSET = 0

def _generate_daily_word_with_groq(exclude_words):
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key or "your_groq_api_key_here" in api_key:
        return None

    avoid_list = sorted(list(exclude_words))[:25]
    avoid_str = ", ".join(avoid_list) if avoid_list else "Articulate"
    prompt = (
        f"Generate ONE inspiring, practical English vocabulary word or expression for today's 'Word of the Day' on SpeakUp AI (for students and professionals).\n"
        f"Do NOT choose any of these words: {avoid_str}.\n"
        f"Reply ONLY with strict JSON:\n"
        f'{{\n'
        f'  "word": "Distinct Word or Idiom",\n'
        f'  "phonetic": "/IPA pronunciation/",\n'
        f'  "part_of_speech": "Adjective/Verb/Noun/Idiom/Connector",\n'
        f'  "category": "Academic | Professional | Everyday Idioms | Connectors",\n'
        f'  "difficulty": "Beginner | Intermediate | Advanced",\n'
        f'  "definition": "Clear 1-2 sentence definition",\n'
        f'  "example": "Memorable spoken English example sentence",\n'
        f'  "synonyms": ["syn1", "syn2", "syn3"],\n'
        f'  "tip": "Short spoken usage tip (1 sentence)"\n'
        f'}}'
    )
    raw_text, model_name, _ = _run_groq_with_fallback(
        api_key=api_key,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700,
        temperature=0.85,
        timeout=12
    )
    parsed = _extract_json_object(raw_text)
    if parsed and parsed.get("word") and parsed.get("definition"):
        entry = _normalize_vocab_entry(parsed)
        entry["source"] = f"groq:{model_name}"
        return entry
    return None

def get_daily_spotlight_word(refresh=False, exclude_word=None):
    """Return today's changing Word of the Day (cached per calendar date, or freshly rotated on refresh)."""
    global _DAILY_FALLBACK_OFFSET
    today_key = datetime.date.today().isoformat()

    if exclude_word:
        _RECENT_DAILY_WORDS.add(exclude_word.strip().lower())

    if not refresh:
        cached = get_daily_word_cache(today_key)
        if cached and cached.get("word"):
            cached["date"] = today_key
            return cached

    exclude_set = {w["word"].lower() for w in VOCABULARY_DATA} | set(_RECENT_DAILY_WORDS)
    ai_word = _generate_daily_word_with_groq(exclude_set)
    if ai_word:
        saved = save_dictionary_word(ai_word)
        chosen = saved or ai_word
        chosen["date"] = today_key
        _RECENT_DAILY_WORDS.add(chosen["word"].lower())
        set_daily_word_cache(today_key, chosen)
        return chosen

    # Deterministic date rotation fallback (skip index 0 initially so it rotates away from Articulate)
    pool = VOCABULARY_DATA[1:] if len(VOCABULARY_DATA) > 1 else VOCABULARY_DATA
    if refresh:
        _DAILY_FALLBACK_OFFSET += 1
    base_idx = (datetime.date.today().toordinal() + _DAILY_FALLBACK_OFFSET) % len(pool)
    chosen = dict(pool[base_idx])
    if exclude_word and chosen["word"].lower() == exclude_word.strip().lower() and len(pool) > 1:
        chosen = dict(pool[(base_idx + 1) % len(pool)])
    chosen["date"] = today_key
    set_daily_word_cache(today_key, chosen)
    return chosen

def call_live_ai_api(history, user_message, topic, level, student_name="Student"):
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key or api_key.strip() == "" or "your_gemini_api_key_here" in api_key:
        return None

    first_name = student_name.strip().split()[0] if student_name and student_name.strip() and student_name.lower() != 'none' else "Student"

    system_instruction = (
        f"You are Sophia, an encouraging, articulate, and intelligent AI English speaking coach in the SpeakUp AI platform.\n"
        f"The student you are speaking with is named '{student_name}' (call them '{first_name}').\n"
        f"IMPORTANT INSTRUCTION: Always address the student naturally by their actual name '{first_name}' when greeting them, praising them, or asking follow-up questions. NEVER call them 'Alex' unless their name is explicitly Alex.\n"
        f"The user is practicing the topic: '{topic}' at a '{level}' proficiency level.\n"
        f"Key instructions:\n"
        f"1. Respond naturally, contextually, and conversationally to whatever the user sends (small talk, cafe ordering, college life, job interviews, or general educational questions).\n"
        f"2. Keep your response concise (2-4 sentences max) so the student has plenty of room to speak.\n"
        f"3. Always ask an engaging, natural follow-up question related to what they said to keep the conversation going.\n"
        f"4. If the user makes a grammar or vocabulary error, gently mention a natural way to say it in your conversational response.\n"
        f"5. End your response on a new line with: SUGGESTIONS: [phrase 1], [phrase 2], [phrase 3] with 3 helpful phrases or words for the user's next response."
    )

    contents = []
    if history and isinstance(history, list):
        for item in history[-8:]:
            role = "user" if item.get("role") == "user" else "model"
            txt = item.get("content", "").strip()
            if txt:
                contents.append({"role": role, "parts": [{"text": txt}]})

    contents.append({"role": "user", "parts": [{"text": user_message}]})

    payload = {
        "contents": contents,
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 350
        }
    }

    models_to_try = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts and "text" in parts[0]:
                        reply, suggestions = parse_llm_response(parts[0]["text"])
                        return {
                            "reply": reply,
                            "suggested_vocab": suggestions,
                            "model_used": model_name
                        }
        except Exception as e:
            print(f"API attempt on {model_name} failed: {e}")
            continue

    return None

def generate_contextual_fallback_response(topic, message, history=None, level="intermediate", student_name="Student"):
    msg = message.strip()
    msg_lower = msg.lower()
    history = history or []
    turn_num = len(history) // 2

    prior_assistant_messages = [h.get("content", "") for h in history if h.get("role") == "assistant"]
    used_text = " ".join(prior_assistant_messages).lower()

    first_name = student_name.strip().split()[0] if student_name and student_name.strip() and student_name.lower() not in ['student', 'none'] else "there"

    if any(g in msg_lower for g in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
        if turn_num <= 1:
            if topic == "ordering-cafe":
                reply = f"Hello {first_name}! Welcome to the cafe. What can I brew fresh for you today?"
                vocab = ["Cappuccino", "Iced latte", "Takeaway"]
            elif topic == "college-life":
                reply = f"Hi {first_name}! Great to see you. How are your classes and semester projects going?"
                vocab = ["Going well", "Busy with projects", "Studying for exams"]
            elif topic == "job-interview":
                reply = f"Welcome {first_name}! Take a calm breath. Whenever you are ready, could you tell me about yourself and your background?"
                vocab = ["Certainly", "Background in CS", "Key projects"]
            else:
                reply = f"Hello {first_name}! It is wonderful to practice speaking with you today. How is your day going so far?"
                vocab = ["Going great", "A bit busy", "Productive"]
            return {"reply": reply, "suggested_vocab": vocab}

    if re.search(r"\b(what is|explain|define|difference between|how to|meaning of)\b", msg_lower):
        if "adjective" in msg_lower:
            reply = f"An adjective describes or modifies a noun, {first_name}, like 'articulate speaker' or 'steaming coffee'. Can you share an example sentence using an adjective you like?"
            vocab = ["Descriptive", "Modifies", "Nuanced"]
        elif "adverb" in msg_lower:
            reply = f"An adverb modifies a verb or adjective, typically ending in '-ly', like 'he explained thoroughly'. How would you describe how you usually study, {first_name}: quickly or methodically?"
            vocab = ["Fluently", "Methodically", "Consistently"]
        elif "star" in msg_lower:
            reply = f"The STAR method stands for Situation, Task, Action, and Result, {first_name}. It is the gold standard for behavioral interviews. Would you like to practice a STAR question right now?"
            vocab = ["Situation", "Action taken", "Measurable result"]
        elif "interview" in msg_lower:
            reply = f"The key to acing interviews, {first_name}, is structuring your answers and backing up every claim with a concrete project example. What type of interview are you preparing for?"
            vocab = ["Poised", "Key strength", "Deliverables"]
        else:
            cleaned = re.sub(r"^(what is|explain|tell me about|define)\s+", "", msg_lower).rstrip("?").strip()
            reply = f"Great question, {first_name}! Understanding '{cleaned}' helps you express complex ideas clearly. How do you see this concept connecting to your studies or goals?"
            vocab = ["Key concept", "In practice", "Specifically"]
        return {"reply": reply, "suggested_vocab": vocab}

    if any(g in msg_lower for g in ["how are you", "how are you doing", "how do you do"]):
        reply = f"I am doing wonderfully and excited to practice speaking with you today, {first_name}! How has your day been so far?"
        return {"reply": reply, "suggested_vocab": ["Productive", "A bit hectic", "Going smoothly"]}

    if any(g in msg_lower for g in ["who are you", "what is your name"]):
        reply = f"I am Sophia, your personal AI speaking companion on SpeakUp AI. My mission is to help you build natural spoken confidence, {first_name}. What is on your mind today?"
        return {"reply": reply, "suggested_vocab": ["Practice session", "College project", "Career goals"]}

    if any(w in msg_lower for w in ["thank you", "thanks", "appreciate"]):
        reply = f"You are very welcome, {first_name}! You are doing an impressive job expressing yourself clearly. Shall we continue on this topic, or would you like to try a new scenario?"
        return {"reply": reply, "suggested_vocab": ["Let's continue", "New scenario", "Next question"]}

    if any(w in msg_lower for w in ["bye", "goodbye", "see you", "that's all", "im done"]):
        reply = f"It was a pleasure speaking with you today, {first_name}! Even a short practice session every day builds permanent fluency. Have a productive day and see you next time!"
        return {"reply": reply, "suggested_vocab": ["Take care", "See you soon", "Great session"]}

    if msg_lower in ["yes", "yeah", "yep", "sure", "of course", "definitely"]:
        variations = [
            f"Awesome, {first_name}! If you had to explain your reason to a friend, what would you emphasize most?",
            f"Great! What was the turning point that led you to that opinion, {first_name}?",
            f"Understood, {first_name}! Could you give me a specific real-world example of that from your own experience?",
            f"I love the enthusiasm, {first_name}! What is the next step you would take in that situation?",
            f"Wonderful, {first_name}! How does that usually work out in practice?"
        ]
        reply = next((v for v in variations if v.lower() not in used_text), variations[turn_num % len(variations)])
        return {"reply": reply, "suggested_vocab": ["For instance", "In my experience", "Main reason"]}

    if msg_lower in ["no", "nope", "not really", "i don't think so"]:
        variations = [
            f"Fair point, {first_name}! What alternative approach do you think would work better?",
            f"Understood, {first_name}. What makes you lean against that perspective?",
            f"Makes total sense, {first_name}. What would you prefer to focus on instead?",
            f"I respect that view, {first_name}. Have you ever encountered a situation where that turned out differently?"
        ]
        reply = next((v for v in variations if v.lower() not in used_text), variations[turn_num % len(variations)])
        return {"reply": reply, "suggested_vocab": ["Alternatively", "On the contrary", "I prefer"]}

    if topic == "ordering-cafe":
        if any(w in msg_lower for w in ["coffee", "latte", "cappuccino", "espresso", "tea", "mocha", "americano"]):
            if "hot or iced" not in used_text:
                reply = f"Great choice, {first_name}! Would you like that hot or iced? Also, do you prefer whole milk, oat milk, or almond milk?"
                vocab = ["Iced", "Oat milk", "Single shot"]
            else:
                reply = f"Coming right up, {first_name}! What size would you prefer today — regular or large?"
                vocab = ["Regular size", "Large cup", "Takeaway"]
        elif any(w in msg_lower for w in ["hot", "iced", "cold"]):
            reply = f"Got it, {first_name}! And what size cup should I pour for you: small, regular, or large?"
            vocab = ["Regular cup", "Large size", "With a lid"]
        elif any(w in msg_lower for w in ["small", "regular", "large", "medium"]):
            if "croissant" not in used_text:
                reply = f"Regular it is, {first_name}! Can I tempt you with any fresh pastries today, like a butter croissant or blueberry muffin?"
                vocab = ["Butter croissant", "Blueberry muffin", "No pastry thank you"]
            else:
                reply = f"Noted, {first_name}! Would you like that beverage for here in a ceramic mug, or to go in a paper cup?"
                vocab = ["For here", "To go", "With a cup sleeve"]
        elif any(w in msg_lower for w in ["croissant", "muffin", "bagel", "cookie", "cake", "sandwich"]):
            reply = f"Our bakery items were freshly baked this morning, {first_name}! Would you like me to warm that up for you?"
            vocab = ["Warmed up please", "As it is", "With a napkin"]
        elif any(w in msg_lower for w in ["card", "cash", "apple pay", "phone", "pay"]):
            reply = f"Please tap or insert your card right on the reader, {first_name}... Beep! Payment approved. Your drink will be ready at the pick-up counter. Enjoy your day!"
            vocab = ["Keep the change", "Receipt please", "Thank you"]
        elif any(w in msg_lower for w in ["how much", "bill", "price", "cost"]):
            reply = f"That comes to $4.50 in total, {first_name}. Will you be paying with cash, card, or contactless phone pay?"
            vocab = ["Paying by card", "Contactless", "Receipt please"]
        elif any(w in msg_lower for w in ["to go", "takeaway", "for here"]):
            reply = f"Perfect, {first_name}! Your total is $4.50. Will you be paying by card or cash today?"
            vocab = ["By card", "Exact cash", "Mobile pay"]
        else:
            options = [
                f"I have added that to your order, {first_name}! Would you like any extra syrup, like vanilla or caramel?",
                f"Noted, {first_name}! Will that be for here, or takeaway to go?",
                f"Got your order, {first_name}! Anything else I can brew or prepare for you today?"
            ]
            reply = next((opt for opt in options if opt.lower() not in used_text), options[0])
            vocab = ["Vanilla syrup", "To go", "That is all"]
        return {"reply": reply, "suggested_vocab": vocab}

    elif topic == "college-life":
        if any(w in msg_lower for w in ["exam", "test", "study", "studying", "marks", "grades"]):
            options = [
                f"Exams can definitely test your patience, {first_name}! How do you usually balance your revision schedule across multiple subjects?",
                f"Staying calm during tests is half the battle, {first_name}. Do you prefer solving previous year question papers or reviewing concept summaries?",
                f"That sounds intense, {first_name}. What subject are you most confident about this semester?"
            ]
            reply = next((o for o in options if o.lower() not in used_text), options[0])
            vocab = ["Revision schedule", "Past papers", "Prioritize"]
        elif any(w in msg_lower for w in ["project", "assignment", "presentation", "code", "coding", "software"]):
            options = [
                f"Hands-on project work is where real learning happens, {first_name}! What was the most interesting technical hurdle your team had to overcome?",
                f"Building practical software is so rewarding, {first_name}. How did your team divide tasks: frontend, backend, or database?",
                f"Presenting technical projects clearly to professors is a great skill, {first_name}. What is the central feature you are most proud of?"
            ]
            reply = next((o for o in options if o.lower() not in used_text), options[0])
            vocab = ["Technical hurdle", "Implementation", "Collaboration"]
        elif any(w in msg_lower for w in ["professor", "teacher", "lecture", "class"]):
            options = [
                f"Active participation in lectures really makes an impression, {first_name}. Do you usually ask questions during class or speak with professors during office hours?",
                f"Every professor has a different teaching style, {first_name}! What kind of teaching approach helps you absorb concepts best?"
            ]
            reply = next((o for o in options if o.lower() not in used_text), options[0])
            vocab = ["Office hours", "Clarification", "Interactive"]
        else:
            options = [
                f"College life is packed with formative experiences, {first_name}. What has been the most valuable lesson you have learned outside the classroom this year?",
                f"That is a great perspective, {first_name}. How do you usually manage your time between academic deadlines and personal hobbies?",
                f"Interesting, {first_name}! How do your classmates feel about that topic?"
            ]
            reply = next((o for o in options if o.lower() not in used_text), options[turn_num % len(options)])
            vocab = ["Time management", "Valuable lesson", "Campus experience"]
        return {"reply": reply, "suggested_vocab": vocab}

    elif topic == "job-interview":
        if any(w in msg_lower for w in ["myself", "background", "student", "experience"]):
            reply = f"That is a solid foundation, {first_name}! When introducing yourself, always highlight one specific achievement where you created value. What accomplishment are you most proud of?"
            vocab = ["Demonstrated", "Hands-on experience", "Problem solver"]
        elif any(w in msg_lower for w in ["strength", "strengths"]):
            reply = f"Self-awareness is key in HR rounds, {first_name}. Could you share a quick situation where that strength made a tangible difference in a group result?"
            vocab = ["Adaptability", "Collaboration", "Delivered on time"]
        elif any(w in msg_lower for w in ["weakness", "weaknesses"]):
            reply = f"Interviewers respect candidates who own their weaknesses, {first_name}. What concrete step or tool have you adopted recently to improve in that area?"
            vocab = ["Continuous learning", "Time management", "Actively improving"]
        else:
            options = [
                f"Interviewers love hearing concrete examples with measurable outcomes, {first_name}. Could you walk me through the specific actions you took?",
                f"That shows great problem-solving ability, {first_name}! What was the end result, and what did you learn from that experience?",
                f"Good point, {first_name}! In an interview, how would you connect that skill with the job requirements?"
            ]
            reply = next((o for o in options if o.lower() not in used_text), options[turn_num % len(options)])
            vocab = ["Key takeaway", "Took initiative", "Measurable outcome"]
        return {"reply": reply, "suggested_vocab": vocab}

    else:
        like_match = re.search(r"\b(?:i like|i love|i enjoy|my favorite|i prefer)\s+([^.!?]+)", msg_lower)
        if like_match:
            item = like_match.group(1).strip()
            options = [
                f"{item.capitalize()} is such a rewarding pursuit, {first_name}! What first sparked your interest in it?",
                f"I love hearing that, {first_name}! How has exploring {item} influenced the way you think or spend your free time?",
                f"{item.capitalize()} sounds exciting, {first_name}. What is one thing most people do not know about it?"
            ]
            reply = next((o for o in options if o.lower() not in used_text), options[0])
            vocab = ["Fascinating", "Passionate about", "Sparked my interest"]
        else:
            options = [
                f"That is a thoughtful point, {first_name}! How did you come to that conclusion?",
                f"I appreciate how clearly you phrased that, {first_name}. What do you think is the biggest misconception people have about this?",
                f"That brings up an interesting angle, {first_name}. If you had to describe the most important takeaway in one sentence, what would it be?",
                f"Fascinating perspective, {first_name}! How has that affected your day-to-day outlook?"
            ]
            reply = next((o for o in options if o.lower() not in used_text), options[turn_num % len(options)])
            vocab = ["In my view", "Furthermore", "Key takeaway"]
        return {"reply": reply, "suggested_vocab": vocab}

def call_groq_api(history, user_message, topic, level, student_name="Student"):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or api_key.strip() == "" or "your_groq_api_key_here" in api_key:
        return None

    first_name = student_name.strip().split()[0] if student_name and student_name.strip() and student_name.lower() != 'none' else "Student"

    system_instruction = (
        f"You are Sophia, an encouraging, articulate, and intelligent AI English speaking coach in the SpeakUp AI platform.\n"
        f"The student you are speaking with is named '{student_name}' (call them '{first_name}').\n"
        f"IMPORTANT INSTRUCTION: Include the student's actual first name '{first_name}' naturally in EVERY reply (when greeting, praising, or asking a follow-up). NEVER call them 'Alex' unless their name is explicitly Alex.\n"
        f"The user is practicing the topic: '{topic}' at a '{level}' proficiency level.\n"
        f"Key instructions:\n"
        f"1. Respond naturally, contextually, and conversationally to whatever the user sends.\n"
        f"2. Keep your reply concise (2-4 sentences max) so the student has plenty of room to speak.\n"
        f"3. Always ask an engaging, natural follow-up question related to what they said to keep the conversation going.\n"
        f"4. If the user makes a grammar or vocabulary error, gently model a natural way to say it in your reply.\n"
        f"5. End your response on a new line with: SUGGESTIONS: phrase 1 | phrase 2 | phrase 3 (exactly 3 short unquoted starter phrases for the student's next reply, separated by |)."
    )

    messages = [{"role": "system", "content": system_instruction}]

    if history and isinstance(history, list):
        for item in history[-8:]:
            role = item.get("role", "user")
            if role not in ["user", "assistant"]:
                role = "assistant" if role == "model" else "user"
            txt = item.get("content", "").strip()
            if txt:
                messages.append({"role": role, "content": txt})

    messages.append({"role": "user", "content": user_message})

    raw_text, model_name, _ = _run_groq_with_fallback(
        api_key=api_key,
        messages=messages,
        max_tokens=700,
        temperature=0.7,
        timeout=12
    )
    if raw_text:
        reply, suggestions = parse_llm_response(raw_text)
        if reply:
            return {
                "reply": reply,
                "suggested_vocab": suggestions,
                "model_used": f"groq:{model_name}"
            }

    return None

def evaluate_interview_with_groq(question_text, answer, student_name="Student"):
    """Optionally enrich interview feedback using Groq AI when a key is configured."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or not api_key.strip() or "your_groq_api_key_here" in api_key:
        return None

    first_name = student_name.strip().split()[0] if student_name and student_name.strip() and student_name.lower() != 'none' else "Student"
    prompt = (
        f"Evaluate {first_name}'s interview answer concisely.\n"
        f"Question: {question_text}\n"
        f"Answer: {answer}\n\n"
        f"Respond in strict JSON with keys:\n"
        f'- "strengths": list of exactly 2 short specific strengths (strings)\n'
        f'- "improvement_tip": 1 specific, actionable STAR-method improvement tip (1-2 sentences)'
    )
    raw_text, model_name, _ = _run_groq_with_fallback(
        api_key=api_key,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=450,
        temperature=0.4,
        timeout=10
    )
    if not raw_text:
        return None
    try:
        cleaned = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL | re.IGNORECASE).strip()
        json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(0))
            strengths = parsed.get("strengths")
            tip = parsed.get("improvement_tip")
            if isinstance(strengths, list) and strengths and isinstance(tip, str) and tip.strip():
                return {
                    "strengths": [_normalize_punctuation(str(s).strip()) for s in strengths[:2]],
                    "improvement_tip": _normalize_punctuation(tip.strip()),
                    "model_used": f"groq:{model_name}"
                }
    except Exception as e:
        print(f"Interview AI JSON parse skipped: {e}")
    return None

def generate_ai_tutor_response(topic, message, history=None, level="intermediate", student_name="Student"):
    # 1. Try Groq API first (ultra-fast responses)
    groq_result = call_groq_api(history, message, topic, level, student_name=student_name)
    if groq_result:
        return groq_result

    # 2. Try Gemini API
    live_result = call_live_ai_api(history, message, topic, level, student_name=student_name)
    if live_result:
        return live_result

    # 3. Contextual local engine fallback (no key / offline)
    return generate_contextual_fallback_response(topic, message, history, level, student_name=student_name)

@app.route('/')
def home():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get('user_id'):
            return redirect(url_for('dashboard'))
        return render_template('auth.html', mode='login', title="Sign In — SpeakUp AI")

    data = request.get_json() if request.is_json else request.form
    email = data.get('email', '')
    password = data.get('password', '')

    success, result = authenticate_user(email, password)
    if success:
        session['user_id'] = result['id']
        session['user_name'] = result['name']
        session['user_email'] = result['email']
        session['user_avatar'] = result.get('avatar', '')
        if request.is_json:
            return jsonify({"success": True, "user": result, "redirect": url_for('dashboard')})
        return redirect(url_for('dashboard'))

    if request.is_json:
        return jsonify({"success": False, "error": result}), 400
    return render_template('auth.html', mode='login', error=result, title="Sign In — SpeakUp AI")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if session.get('user_id'):
            return redirect(url_for('dashboard'))
        return render_template('auth.html', mode='register', title="Create Account — SpeakUp AI")

    data = request.get_json() if request.is_json else request.form
    name = data.get('name', '')
    email = data.get('email', '')
    password = data.get('password', '')

    success, result = register_user(name, email, password)
    if success:
        session['user_id'] = result['id']
        session['user_name'] = result['name']
        session['user_email'] = result['email']
        session['user_avatar'] = result.get('avatar', '')
        if request.is_json:
            return jsonify({"success": True, "user": result, "redirect": url_for('dashboard')})
        return redirect(url_for('dashboard'))

    if request.is_json:
        return jsonify({"success": False, "error": result}), 400
    return render_template('auth.html', mode='register', error=result, title="Create Account — SpeakUp AI")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    stats = get_student_dashboard_data(user_id)
    student_name = session.get('user_name', 'Student')

    return render_template('dashboard.html', 
                           title="Student Dashboard — SpeakUp AI",
                           stats=stats,
                           student_name=student_name,
                           active_page='dashboard')

@app.route('/modules')
def modules():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    stats = get_student_dashboard_data(user_id)
    student_name = session.get('user_name', 'Student')
    return render_template('modules.html',
                           title="Learning Modules — SpeakUp AI",
                           stats=stats,
                           student_name=student_name,
                           active_page='modules')

@app.route('/grammar')
def grammar():
    return redirect(url_for('modules'))

@app.route('/practice')
def practice():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    student_name = session.get('user_name', '')
    mode = request.args.get('mode', 'speaking')
    active_page = 'conversation' if mode == 'conversation' else 'practice'
    return render_template('practice.html', 
                           title="Speaking Practice Room — SpeakUp AI",
                           student_name=student_name,
                           mode=mode,
                           active_page=active_page)

@app.route('/conversation')
def conversation():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    student_name = session.get('user_name', '')
    return render_template('practice.html',
                           title="AI Conversation Studio — SpeakUp AI",
                           student_name=student_name,
                           mode='conversation',
                           active_page='conversation')

@app.route('/listening')
def listening():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    student_name = session.get('user_name', 'Student')
    stats = get_student_dashboard_data(user_id)
    category = request.args.get('category', 'all').lower()

    if category and category != 'all':
        filtered = [d for d in LISTENING_DIALOGUES if d['category_slug'] == category]
    else:
        filtered = LISTENING_DIALOGUES

    return render_template('listening.html',
                           title="Listening Practice Studio — SpeakUp AI",
                           student_name=student_name,
                           stats=stats,
                           dialogues=filtered,
                           all_dialogues=LISTENING_DIALOGUES,
                           selected_category=category,
                           active_page='listening')

@app.route('/progress')
def progress_page():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    stats = get_student_dashboard_data(user_id)
    student_name = session.get('user_name', 'Student')
    achievements = get_user_achievements(user_id)
    return render_template('progress.html',
                           title="My Progress & Analytics — SpeakUp AI",
                           stats=stats,
                           student_name=student_name,
                           achievements=achievements,
                           active_page='progress')

@app.route('/achievements')
def achievements():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    student_name = session.get('user_name', 'Student')
    achievements_list = get_user_achievements(user_id)
    stats = get_student_dashboard_data(user_id)
    return render_template('achievements.html',
                           title="My Achievements & Badges — SpeakUp AI",
                           achievements=achievements_list,
                           stats=stats,
                           student_name=student_name,
                           active_page='achievements')

@app.route('/profile')
def profile_page():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = get_user_by_id(user_id)
    stats = get_student_dashboard_data(user_id)
    student_name = session.get('user_name', 'Student')
    return render_template('profile.html',
                           title="My Profile & Account — SpeakUp AI",
                           user=user,
                           stats=stats,
                           student_name=student_name,
                           active_page='profile')

@app.route('/vocabulary')
def vocabulary():
    user_id = session.get('user_id')
    saved_ids = [w['word_id'] for w in get_user_saved_words(user_id)] if user_id else [1, 3]
    daily_word = get_daily_spotlight_word(refresh=False)
    custom_saved = get_saved_custom_words(user_id) if user_id else []
    known_ids = {w['id'] for w in VOCABULARY_DATA}
    all_words = list(VOCABULARY_DATA) + [cw for cw in custom_saved if cw['id'] not in known_ids]
    return render_template('vocabulary.html', 
                           title="Vocabulary Studio — SpeakUp AI",
                           words=all_words,
                           daily_word=daily_word,
                           saved_ids=saved_ids,
                           active_page='vocabulary')

@app.route('/interview')
def interview():
    return render_template('interview.html', 
                           title="Interview Simulator — SpeakUp AI",
                           questions=INTERVIEW_QUESTIONS,
                           active_page='interview')

@app.route('/api/user/profile', methods=['GET', 'POST'])
def api_user_profile():
    user_id = session.get('user_id', 1)
    if request.method == 'GET':
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        return jsonify({"success": True, "user": user})

    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    avatar = data.get('avatar')

    success, res = update_user_profile(user_id, name, email, avatar=avatar)
    if success:
        session['user_name'] = res['name']
        session['user_email'] = res['email']
        if 'avatar' in res and res['avatar']:
            session['user_avatar'] = res['avatar']
        return jsonify({
            "success": True,
            "user": res,
            "message": "Profile updated successfully!"
        })
    return jsonify({"success": False, "error": res}), 400

@app.route('/api/user/password', methods=['POST'])
def api_user_password():
    user_id = session.get('user_id', 1)
    data = request.get_json() or {}
    current_pwd = data.get('current_password', '')
    new_pwd = data.get('new_password', '')
    confirm_pwd = data.get('confirm_password', '')

    if not current_pwd:
        return jsonify({"success": False, "error": "Current password is required."}), 400
    if not new_pwd or len(new_pwd) < 4:
        return jsonify({"success": False, "error": "New password must be at least 4 characters long."}), 400
    if confirm_pwd and new_pwd != confirm_pwd:
        return jsonify({"success": False, "error": "New password and confirmation do not match."}), 400

    success, msg = change_user_password(user_id, current_pwd, new_pwd)
    if success:
        return jsonify({"success": True, "message": msg})
    return jsonify({"success": False, "error": msg}), 400

@app.route('/api/grammar/analyze', methods=['POST'])
def api_grammar_analyze():
    data = request.get_json() or {}
    text = data.get('text', '').strip()
    if not text:
        return jsonify({"success": False, "error": "Please enter a sentence to evaluate."}), 400

    result = evaluate_sentence_ai_and_rules(text)
    return jsonify(result)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    topic = data.get('topic', 'casual-chitchat')
    level = data.get('level', 'intermediate')
    history = data.get('history', [])

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    student_name = session.get('user_name') or data.get('student_name') or 'Student'

    grammar_feedback = analyze_student_grammar(user_message)
    ai_result = generate_ai_tutor_response(topic, user_message, history, level, student_name=student_name)

    user_id = session.get('user_id', 1)
    try:
        save_chat_turn(
            user_id=user_id,
            topic=topic,
            level=level,
            user_message=user_message,
            ai_response=ai_result["reply"],
            has_grammar_error=bool(grammar_feedback)
        )
    except Exception as e:
        print("Notice: Error saving chat to SQLite:", e)

    return jsonify({
        "success": True,
        "ai_response": ai_result["reply"],
        "suggested_vocab": ai_result["suggested_vocab"],
        "grammar_feedback": grammar_feedback,
        "model": ai_result.get("model_used", "contextual-ai-engine")
    })

@app.route('/api/interview/evaluate', methods=['POST'])
def api_interview_evaluate():
    data = request.get_json() or {}
    answer = data.get('answer', '').strip()
    question_id = data.get('question_id', 1)

    if not answer:
        return jsonify({"error": "Please provide an answer to evaluate."}), 400

    q_text = "Interview Question"
    for q in INTERVIEW_QUESTIONS:
        if q["id"] == question_id:
            q_text = q["question"]
            break

    words = answer.split()
    word_count = len(words)

    filler_words = ["um", "uh", "like", "basically", "actually", "you know"]
    found_fillers = [fw for fw in filler_words if re.search(r'\b' + fw + r'\b', answer.lower())]

    grammar_issues = analyze_student_grammar(answer)

    score = 8.0
    if word_count < 30:
        score -= 2.0
    elif word_count > 120:
        score -= 0.5
    
    if found_fillers:
        score -= min(1.5, len(found_fillers) * 0.5)

    if grammar_issues:
        score -= min(1.5, len(grammar_issues) * 0.5)

    score = max(5.0, min(9.8, round(score, 1)))

    student_name = session.get('user_name', 'Student')
    ai_eval = evaluate_interview_with_groq(q_text, answer, student_name=student_name)

    feedback = {
        "score": score,
        "word_count": word_count,
        "fillers_detected": found_fillers,
        "grammar_feedback": grammar_issues,
        "strengths": ai_eval["strengths"] if ai_eval else [
            "Good engagement with the core question prompt",
            "Clear and confident tone throughout the response"
        ],
        "improvement_tip": ai_eval["improvement_tip"] if ai_eval else "Try using the STAR format (Situation, Task, Action, Result) to give a structured answer."
    }

    user_id = session.get('user_id', 1)
    try:
        save_interview_result(
            user_id=user_id,
            question_text=q_text,
            answer=answer,
            score=score,
            word_count=word_count,
            filler_words=found_fillers,
            tip=feedback["improvement_tip"]
        )
    except Exception as e:
        print("Notice: Error saving interview result to SQLite:", e)

    return jsonify({"success": True, "evaluation": feedback})

@app.route('/api/vocabulary/toggle', methods=['POST'])
def api_vocabulary_toggle():
    user_id = session.get('user_id', 1)
    data = request.get_json() or {}
    word_id = data.get('word_id')
    word_text = data.get('word_text', '')

    if not word_id:
        return jsonify({"error": "Missing word_id"}), 400

    success, action = toggle_save_word(user_id, word_id, word_text)
    return jsonify({"success": success, "action": action})

@app.route('/api/settings/status', methods=['GET'])
def api_settings_status():
    groq_key = os.environ.get("GROQ_API_KEY", "").strip()
    groq_ok = bool(groq_key and "your_groq_api_key_here" not in groq_key)
    groq_masked = (groq_key[:6] + "..." + groq_key[-4:]) if groq_ok and len(groq_key) > 10 else ""

    gemini_key = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")).strip()
    gemini_ok = bool(gemini_key and "your_gemini_api_key_here" not in gemini_key)
    gemini_masked = (gemini_key[:6] + "..." + gemini_key[-4:]) if gemini_ok and len(gemini_key) > 10 else ""

    active_provider = "groq" if groq_ok else ("gemini" if gemini_ok else "contextual-offline")

    return jsonify({
        "groq": {"configured": groq_ok, "masked_key": groq_masked},
        "gemini": {"configured": gemini_ok, "masked_key": gemini_masked},
        "active_provider": active_provider,
        "configured": groq_ok or gemini_ok,
        "masked_key": groq_masked or gemini_masked
    })

@app.route('/api/settings/key', methods=['POST'])
def api_settings_save_key():
    data = request.get_json() or {}
    api_key = data.get('api_key', '').strip()
    provider = data.get('provider', 'groq').lower()

    if not api_key:
        return jsonify({"success": False, "error": "API key cannot be empty."}), 400

    if provider == "groq" or api_key.startswith("gsk_"):
        is_valid, test_msg = test_groq_key(api_key)
        key_var = "GROQ_API_KEY"
    else:
        is_valid, test_msg = test_gemini_key(api_key)
        key_var = "GEMINI_API_KEY"

    if not is_valid:
        return jsonify({"success": False, "error": test_msg}), 400

    saved = update_env_variable(key_var, api_key)
    if not saved:
        return jsonify({"success": False, "error": "Could not write key to .env file."}), 500

    return jsonify({
        "success": True,
        "message": test_msg,
        "provider": "groq" if key_var == "GROQ_API_KEY" else "gemini",
        "masked_key": api_key[:6] + "..." + api_key[-4:]
    })

@app.route('/api/vocabulary/daily', methods=['GET'])
def api_daily_word():
    refresh = request.args.get('refresh', '').lower() in ('1', 'true', 'yes')
    exclude_word = request.args.get('exclude', '').strip() or None
    daily_word = get_daily_spotlight_word(refresh=refresh, exclude_word=exclude_word)
    return jsonify({"success": True, "word": daily_word})

@app.route('/api/vocabulary/lookup', methods=['GET', 'POST'])
def api_vocabulary_lookup():
    if request.method == 'POST':
        data = request.get_json() or {}
        query = data.get('word', '')
    else:
        query = request.args.get('word', '')

    entry, err = lookup_any_vocabulary_word(query)
    if entry:
        return jsonify({"success": True, "entry": entry})
    status_code = 400 if "Please enter" in (err or "") or "too long" in (err or "") else 404
    return jsonify({"success": False, "error": err}), status_code

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    print(f"SpeakUp AI running on http://{host}:{port}")
    app.run(debug=False if os.environ.get("PORT") else True, host=host, port=port)
