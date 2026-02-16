import re
import threading
from groq import Groq
from config import settings
from database import CODE_DATABASE, COMPANY_POLICIES

# Gemini import
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

client = None
if settings.GROQ_API_KEY:
    client = Groq(api_key=settings.GROQ_API_KEY)

gemini_lock = threading.Lock()

def get_ai_response(prompt, temp=0.3, max_tokens=2000, model="llama-3.3-70b-versatile", gemini_key=None):
    if "gemini" in model.lower():
        if not GEMINI_AVAILABLE:
            return "Error: google-generativeai library not installed."
        
        final_key = gemini_key or settings.GEMINI_API_KEY
        if not final_key:
            return "Error: Gemini API Key not found."
            
        try:
            with gemini_lock:
                genai.configure(api_key=final_key)
                gemini_model = genai.GenerativeModel("gemini-pro")
                response = gemini_model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temp,
                        max_output_tokens=max_tokens
                    )
                )
            return response.text
        except Exception as e:
            return f"Error calling Gemini: {str(e)}"

    if not client:
        return "Error: Groq API Key not configured."

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "You are a helpful coding assistant."},
                      {"role": "user", "content": prompt}],
            temperature=temp,
            max_tokens=max_tokens
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"AI Error: {e}")
        return "Error: Could not get a response from AI."

def analyze_complexity(code, model="llama-3.3-70b-versatile", gemini_key=None):
    prompt = f"Analyze the time complexity of this code. Return ONLY the Big-O notation (e.g., O(n)).\nCode:\n{code}"
    res = get_ai_response(prompt, temp=0.1, max_tokens=20, model=model, gemini_key=gemini_key)
    match = re.search(r"O\(.*?\)", res)
    return match.group(0) if match else "O(n)"

def check_plagiarism(code):
    if not code or not CODE_DATABASE:
        CODE_DATABASE.append(code)
        return "0% (New)"
    
    max_sim = 0
    for old_code in CODE_DATABASE:
        matches = sum(1 for a, b in zip(code, old_code) if a == b)
        sim = matches / max(len(code), len(old_code)) if max(len(code), len(old_code)) > 0 else 0
        max_sim = max(max_sim, sim)
    
    CODE_DATABASE.append(code)
    return f"{round(max_sim * 100, 2)}%"

def create_balanced_review_prompt(code, user_type):
    personas = {
        "student": """You are a supportive AI Tutor. Analyze this code FAIRLY:
1. Start by acknowledging what was done WELL
2. Point out ONLY actual bugs or logical errors
3. Suggest improvements with explanations""",
        "enterprise": """You are a Security Auditor. Review this code for:
1. ONLY genuine security vulnerabilities (OWASP Top 10)
2. Compliance issues that matter""",
        "developer": """You are a Senior Developer doing constructive code review. Analyze OBJECTIVELY:
1. Start with what's done RIGHT
2. Point out ONLY real bugs, inefficiencies, or architectural issues"""
    }
    persona = personas.get(user_type, personas['developer'])
    return f"{persona}\n{code}"

def inject_policies(prompt, user_type):
    """Inject company policies for enterprise users"""
    if user_type in ["enterprise", "organisation"] and COMPANY_POLICIES:
        return f"STRICTLY ADHERE TO THE FOLLOWING COMPANY POLICIES:\n{COMPANY_POLICIES}\n\n{prompt}"
    return prompt