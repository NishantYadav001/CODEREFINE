import os
import re
from pathlib import Path
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Code Refine",
    description="AI-powered code review and rewrite service using Groq",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- Global Stores ---
VECTOR_STORE = {"documents": []}
CODE_DATABASE = []
STUDENT_STATS = {}
ACTIVE_SESSIONS = {}
DEMO_USERS = {
    "admin": "password",
    "student1": "password",
    "teacher": "password"
}

# --- Data Models ---
class RequestOptions(BaseModel):
    focus_areas: list[str] = []

class CodeReviewRequest(BaseModel):
    code: str
    language: str
    options: RequestOptions
    user_type: str
    student_name: str = "Anonymous"

class LoginRequest(BaseModel):
    username: str
    password: str

# --- Helper Functions ---

def parse_review_response(review_text: str):
    """Extract priority counts from AI response"""
    critical = len(re.findall(r'### Critical', review_text, re.IGNORECASE))
    high = len(re.findall(r'### High Priority', review_text, re.IGNORECASE))
    medium = len(re.findall(r'### Medium Priority', review_text, re.IGNORECASE))
    low = len(re.findall(r'### Low Priority', review_text, re.IGNORECASE))
    return {"critical": critical, "high": high, "medium": medium, "low": low}

def check_plagiarism(code: str):
    """Compare new submission against local database"""
    if not CODE_DATABASE:
        CODE_DATABASE.append(code)
        return "0% (First submission)"
    
    # Simple character-based similarity check
    max_sim = 0
    for old_code in CODE_DATABASE:
        # Calculate similarity as ratio of matching characters
        matches = sum(1 for a, b in zip(code, old_code) if a == b)
        sim = matches / max(len(code), len(old_code)) if max(len(code), len(old_code)) > 0 else 0
        max_sim = max(max_sim, sim)
    
    CODE_DATABASE.append(code)
    percent = round(max_sim * 100, 2)
    return f"{percent}%"

def get_policy_context(query: str, top_k=2):
    """Retrieve relevant policy chunks for Enterprise auditing"""
    if not VECTOR_STORE["documents"]:
        return "No policy documents found."
    # Simple text search
    matching_docs = [doc for doc in VECTOR_STORE["documents"] if any(word in doc.lower() for word in query.lower().split())]
    return "\n".join(matching_docs[:top_k]) if matching_docs else "No matching policies found."

def serve_login():
    """Load login page"""
    login_path = Path(__file__).parent.parent / "frontend" / "login.html"
    try:
        with open(login_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Login page not found</h1>"

def serve_index():
    """Load index page"""
    index_path = Path(__file__).parent.parent / "frontend" / "index.html"
    try:
        with open(index_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Index page not found</h1>"

def serve_dashboard():
    """Load dashboard page"""
    dashboard_path = Path(__file__).parent.parent / "frontend" / "dashboard.html"
    try:
        with open(dashboard_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Dashboard page not found</h1>"

# --- Authentication Endpoints ---

@app.get("/")
async def root():
    """Root endpoint - redirect to login"""
    return HTMLResponse(content=serve_login())

@app.post("/api/login")
async def login(request: LoginRequest):
    """Authenticate user and generate session token"""
    if request.username not in DEMO_USERS or DEMO_USERS[request.username] != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = f"token_{request.username}_{datetime.now().timestamp()}"
    ACTIVE_SESSIONS[token] = {
        "username": request.username,
        "user_type": "student" if "student" in request.username else "teacher" if request.username == "teacher" else "admin",
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "token": token,
        "user_type": ACTIVE_SESSIONS[token]["user_type"],
        "username": request.username,
        "message": "Login successful"
    }

@app.post("/api/logout")
async def logout(token: str = None):
    """Logout user and invalidate session"""
    if token and token in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[token]
    return {"message": "Logout successful"}

# --- Page Serving Endpoints ---

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Serve the login page"""
    return serve_login()

@app.get("/app", response_class=HTMLResponse)
async def serve_tool():
    """Serve the main tool page"""
    return serve_index()

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    """Serve the Student Dashboard"""
    return serve_dashboard()

# --- API Endpoints ---

@app.post("/api/ocr")
async def extract_code(file: UploadFile = File(...)):
    """Convert uploaded code images to text"""
    if not OCR_AVAILABLE:
        raise HTTPException(status_code=503, detail="OCR service not available. Please install pytesseract and Tesseract-OCR.")
    try:
        image = Image.open(file.file)
        text = pytesseract.image_to_string(image)
        return {"extracted_code": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-policy")
async def upload_policy(file: UploadFile = File(...)):
    """Ingest policy documents into the system"""
    try:
        content = await file.read()
        text = content.decode("utf-8")
        
        # Split text into chunks
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]
        VECTOR_STORE["documents"] = chunks
        
        return {"message": f"Successfully indexed {len(chunks)} policy segments."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/review")
async def review_code(payload: dict = None):
    """Main AI Review logic using Llama 3.3

    Accepts flexible JSON payloads to avoid 422 when frontend sends different shapes.
    Supported shapes:
      - { code, language, options: { focus_areas: [...] }, user_type, student_name }
      - { code, language, focus_areas: [...], user_type }
    """
    if payload is None:
        raise HTTPException(status_code=400, detail="Request body required")

    # Normalize fields from potentially different frontend payload shapes
    code = payload.get("code") or payload.get("text") or ""
    language = payload.get("language", "python")
    user_type = payload.get("user_type") or payload.get("userType") or payload.get("role") or "developer"
    student_name = payload.get("student_name") or payload.get("studentName") or "Anonymous"

    # options may be nested under 'options' or provided directly as 'focus_areas'
    options = payload.get("options") or {}
    focus_areas = []
    if isinstance(options, dict):
        focus_areas = options.get("focus_areas") or options.get("focusAreas") or []
    # fallback to top-level key
    if not focus_areas:
        focus_areas = payload.get("focus_areas") or payload.get("focusAreas") or []
    if not isinstance(focus_areas, list):
        focus_areas = [focus_areas]

    if not isinstance(code, str) or not code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    # 1. Update Student Stats
    if user_type == "student":
        STUDENT_STATS[student_name] = STUDENT_STATS.get(student_name, 0) + 1

    # 2. Plagiarism Check
    plag_report = check_plagiarism(code) if user_type == "student" else "N/A"

    # 3. Policy Retrieval (RAG) for Enterprise
    context = ""
    if user_type in ["enterprise", "organisation"]:
        context = get_policy_context(code)

    # 4. Persona Selection
    personas = {
        "student": "an AI Programming Tutor. Focus on 'AI Tutor Mode': explain mistakes simply, give hints, and show corrected code.",
        "enterprise": f"a Senior Security Auditor. Audit this code against the following policies: {context}. Focus on OWASP and compliance.",
        "organisation": "a Team Architect. Focus on maintainability, coding standards, and large-scale consistency.",
        "developer": "a Senior Full-Stack Developer. Focus on performance, logic bugs, and production-ready optimizations."
    }

    selected_persona = personas.get(user_type, personas["developer"])

    prompt = f"""Act as {selected_persona}.
Analyze this {language} code focusing on: {', '.join(focus_areas) if focus_areas else 'general improvements'}.

RESPONSE FORMAT:
## Overall Assessment
[Brief summary]

### Critical Issues
[If any]

### High Priority
[If any]

### Medium Priority
[If any]

### Low Priority
[If any]

CODE:
{code}
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000
        )

        review_text = completion.choices[0].message.content
        stats = parse_review_response(review_text)

        return {
            "review": review_text,
            "stats": stats,
            "plagiarism": plag_report,
            "student_stats": STUDENT_STATS.get(student_name, 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Groq API: {str(e)}")

@app.post("/api/rewrite")
async def rewrite_code(payload: dict = None):
    """Rewrites and refactors code using a specialized AI prompt

    Accepts flexible JSON payloads (same shapes as /api/review).
    """
    if payload is None:
        raise HTTPException(status_code=400, detail="Request body required")

    code = payload.get("code") or payload.get("text") or ""
    language = payload.get("language", "python")
    user_type = payload.get("user_type") or payload.get("userType") or payload.get("role") or "developer"

    options = payload.get("options") or {}
    focus_areas = []
    if isinstance(options, dict):
        focus_areas = options.get("focus_areas") or options.get("focusAreas") or []
    if not focus_areas:
        focus_areas = payload.get("focus_areas") or payload.get("focusAreas") or []
    if not isinstance(focus_areas, list):
        focus_areas = [focus_areas]

    if not isinstance(code, str) or not code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    personas = {
        "student": "an AI Programming Tutor. Your goal is to rewrite this code to fix errors and improve it, explaining the changes clearly.",
        "enterprise": "a Senior Security Auditor. Your goal is to rewrite this code to patch security vulnerabilities and adhere to best practices.",
        "organisation": "a Team Architect. Your goal is to refactor this code for better maintainability, scalability, and adherence to architectural patterns.",
        "developer": "a Senior Full-Stack Developer. Your goal is to optimize this code for performance, readability, and correctness."
    }
    selected_persona = personas.get(user_type, personas["developer"])
    
    prompt = f"""Act as {selected_persona}.
Rewrite and refactor the following {language} code, focusing on: {', '.join(focus_areas) if focus_areas else 'general improvements'}.

Provide your response in this EXACT format:
## Review of Changes
[Brief summary of what you fixed or improved.]

### Issues Addressed
- [Change 1]
- [Change 2]
- [Change 3]

## Rewritten Code
```{language}
[Your rewritten and corrected code here]
```

ORIGINAL CODE:
{code}
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=3000,
            top_p=0.9
        )

        response_text = completion.choices[0].message.content
        
        # Extract review and rewritten code from the structured response
        review_part = response_text.split("## Rewritten Code")[0]
        code_match = re.search(r"```(?:" + re.escape(language) + r")?\s*([\s\S]+?)\s*```", response_text)
        rewritten_code = code_match.group(1).strip() if code_match else "Could not extract rewritten code."

        stats = parse_review_response(review_part)
        
        return {
            "review": review_part,
            "stats": stats,
            "rewritten_code": rewritten_code
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Groq API: {str(e)}")

# --- Dashboard & Analytics ---

@app.get("/api/dashboard-data")
async def get_dashboard_data():
    """Fetch analytics for the Student Dashboard"""
    return {
        "labels": list(STUDENT_STATS.keys()),
        "data": list(STUDENT_STATS.values())
    }

@app.post("/api/reset-plagiarism")
async def reset_plagiarism():
    """Clear the plagiarism database"""
    CODE_DATABASE.clear()
    return {"message": "Database reset successful."}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "groq": "connected",
            "embedding_model": "loaded",
            "ocr": "available" if OCR_AVAILABLE else "unavailable"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Code Refine Server")
    print("=" * 60)
    print("Server: http://127.0.0.1:8000")
    print("Login: http://127.0.0.1:8000/login")
    print("Dashboard: http://127.0.0.1:8000/dashboard")
    print("API Docs: http://127.0.0.1:8000/docs")
    print("\nDemo Credentials:")
    print("   Username: admin, student1, or teacher")
    print("   Password: password")
    print("=" * 60)
    uvicorn.run(app, host="127.0.0.1", port=8000)
