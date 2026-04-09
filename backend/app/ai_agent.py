import os
import requests
from dotenv import load_dotenv

load_dotenv()

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", os.getenv("LLM_API_KEY", ""))
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", os.getenv("LLM_MODEL", "openai/gpt-4o-mini"))
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Fallback local responses
def get_local_response(question: str, context: str = "") -> str:
    """Provide local responses based on common patterns when LLM is unavailable."""
    question_lower = question.lower()
    
    responses = {
        "how": {
            "match": "The matching algorithm compares course (50pts), topics (30pts), and availability (20pts). Higher scores mean better compatibility!",
            "group": "Study groups form automatically when both students accept a match request. You can then collaborate on coursework together.",
            "register": "To register, click 'Register' tab, fill in your details (name, course, topics), and click 'Register & Find Partners'.",
            "use": "1. Register with your details 2. View matches 3. Send match requests 4. Accept incoming requests 5. Form study groups!",
            "accept": "Go to 'Requests' tab, find pending requests, and click 'Accept'. A study group will be created automatically.",
            "reject": "Go to 'Requests' tab and click 'Reject' on any pending request you don't want to accept.",
            "telegram": "Configure your Telegram Chat ID in your profile. Create a bot via @BotFather, get your ID from @userinfobot.",
            "password": "Passwords are securely hashed with SHA-256 + salt. You cannot register with the same username twice.",
            "course": "Enter your course code like 'CS101', 'MATH201', etc. Students in the same course get higher match scores.",
            "availability": "Enter your free time slots like 'Mon 10-12, Wed 14-16'. The algorithm finds students with overlapping schedules.",
        },
        "what": {
            "match": "A match is another student with similar course, topics, and availability. Scores range from 0-100.",
            "group": "A study group is a collaborative team formed when two students accept each other's match requests.",
            "score": "The score measures compatibility: Course match (50pts) + Topic overlap (30pts) + Availability overlap (20pts).",
            "topics": "Topics are subjects you're studying, e.g., 'Python,AI,Databases'. They help find students with shared interests.",
            "telegram": "A Telegram bot that sends notifications when you receive match requests or form study groups.",
        },
        "can": {
            "multiple": "Yes! You can be in multiple study groups by accepting multiple match requests.",
            "change": "Yes! You can update your profile topics and availability by re-registering with a unique name or contacting support.",
            "leave": "Currently groups are permanent. To leave, contact group members directly and coordinate.",
        },
        "where": {
            "groups": "Go to the 'Groups' tab to see all your study groups and their members.",
            "matches": "Go to the 'Matches' tab to see students ranked by compatibility with you.",
            "requests": "Go to the 'Requests' tab to view and respond to incoming match requests.",
        },
        "why": {
            "no": "Try browsing all students or registering with a popular course. More students = more matches!",
            "score": "Scores reflect how well you match: same course (50pts), shared topics (up to 30pts), overlapping schedules (up to 20pts).",
        },
        "help": "I can help with: matching algorithm, groups, requests, Telegram setup, and general usage. Just ask!",
        "tip": "Study tip: Form groups with students who have complementary strengths. Teach each other for better learning!",
        "thank": "You're welcome! Feel free to ask anything else about Study Group Matcher.",
    }
    
    for key_group, answers in responses.items():
        if key_group in question_lower:
            for key_phrase, answer in answers.items():
                if key_phrase in question_lower:
                    return answer
    
    return "Thanks for your question! The AI service is currently unavailable, but I can help with basics:\n\n• Matching: Course + Topics + Availability = Score (0-100)\n• Groups: Auto-created when matches are accepted\n• Telegram: Configure Chat ID for notifications\n• Security: Passwords are hashed with SHA-256\n\nFor detailed help, try asking about: matching, groups, telegram, scores, or how to use the platform."


def ask_ai_agent(question: str, context: str = "") -> str:
    """Send question to AI agent via OpenRouter and get response."""
    if not OPENROUTER_API_KEY:
        return get_local_response(question, context)

    system_prompt = """You are a Study Group Assistant for a university platform.
You help students find study partners, understand matching criteria, and navigate the platform.
Be helpful, concise, and friendly. Answer in the same language as the question."""

    full_prompt = f"{context}\n\nStudent question: {question}" if context else question

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Study Group Matcher",
        "Content-Type": "application/json"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return get_local_response(question, context)
            
    except requests.exceptions.Timeout:
        return "⏱️ AI response timed out. Please try again or ask a simpler question."
    except requests.exceptions.RequestException as e:
        return get_local_response(question, context)
    except Exception as e:
        return get_local_response(question, context)