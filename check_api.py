import os
import sys
from app import load_env_file, call_groq_api, call_live_ai_api, fetch_groq_models

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_env_file()

print("==================================================")
print("     SpeakUp AI — API Connectivity Check")
print("==================================================")

# 1. Check Groq API
groq_key = os.environ.get("GROQ_API_KEY", "").strip()
if not groq_key or "your_groq_api_key_here" in groq_key:
    print("\n[GROQ API] Status: NOT CONFIGURED")
    print("Add GROQ_API_KEY to your .env file to enable ultra-fast Groq AI.")
else:
    masked = groq_key[:6] + "..." + groq_key[-4:] if len(groq_key) > 10 else "***"
    print(f"\n[GROQ API] Key found: {masked}")
    avail = fetch_groq_models(groq_key)
    print(f"Available chat models ({len(avail)}): {', '.join(avail[:8])}" + ("..." if len(avail) > 8 else ""))
    print("Testing connection to Groq API...")
    res = call_groq_api(
        history=[],
        user_message="Hello Sophia, this is a test from SpeakUp AI.",
        topic="casual-chitchat",
        level="intermediate",
        student_name="Student"
    )
    if res and res.get("reply"):
        print("  -> RESULT: SUCCESS!")
        print(f"  -> Model: {res.get('model_used')}")
        print(f"  -> Sophia: {res.get('reply')}")
        print(f"  -> Suggestions: {res.get('suggested_vocab')}")
    else:
        print("  -> RESULT: FAILED. Check your Groq key validity and network connection.")

# 2. Check Gemini API
gemini_key = os.environ.get("GEMINI_API_KEY", "").strip() or os.environ.get("GOOGLE_API_KEY", "").strip()
if not gemini_key or "your_gemini_api_key_here" in gemini_key:
    print("\n[GEMINI API] Status: NOT CONFIGURED (Optional backup)")
else:
    masked_g = gemini_key[:6] + "..." + gemini_key[-4:] if len(gemini_key) > 10 else "***"
    print(f"\n[GEMINI API] Key found: {masked_g}")
    print("Testing connection to Google Gemini API...")
    res_g = call_live_ai_api(
        history=[],
        user_message="Hello Sophia, this is a test from SpeakUp AI.",
        topic="casual-chitchat",
        level="intermediate",
        student_name="Student"
    )
    if res_g and res_g.get("reply"):
        print("  -> RESULT: SUCCESS!")
        print(f"  -> Model: {res_g.get('model_used')}")
        print(f"  -> Sophia: {res_g.get('reply')[:120]}...")
    else:
        print("  -> RESULT: FAILED. Check your Gemini key.")

print("\n==================================================")
