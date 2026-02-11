import os
import re
import io
import base64
import json
import difflib
from pathlib import Path
from datetime import datetime
from PIL import Image

# OCR imports - try/except for optional dependency
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from fastapi import FastAPI, HTTPException, UploadFile, File, Response, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Code Refine", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq Client
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("ERROR: GROQ_API_KEY not found in .env file!")

client = Groq(api_key=api_key)

# --- Global Stores ---
CODE_DATABASE = [] 
STUDENT_STATS = {}
ACTIVE_SESSIONS = {}
COMPANY_POLICIES = ""
CODE_SNIPPETS = {}  # Store user snippets
CODE_HISTORY = {}   # Track version history
USER_ANALYTICS = {} # Track user activities

# --- Core Utility Logic ---

def get_ai_response(prompt, temp=0.3, max_tokens=2000):
    """Unified helper to call Groq Llama 3.3"""
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are a helpful coding assistant."},
                      {"role": "user", "content": prompt}],
            temperature=temp,
            max_tokens=max_tokens
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"AI Error: {e}")
        return "Error: Could not get a response from AI."

def analyze_complexity(code):
    """AI-powered Big-O analysis"""
    prompt = f"Analyze the time complexity of this code. Return ONLY the Big-O notation (e.g., O(n)).\nCode:\n{code}"
    res = get_ai_response(prompt, temp=0.1, max_tokens=20)
    match = re.search(r"O\(.*?\)", res)
    return match.group(0) if match else "O(n)"

def check_plagiarism(code):
    """Simple similarity check"""
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

# --- API Endpoints ---

@app.post("/api/generate")
async def generate_code(payload: dict = Body(...)):
    u_prompt = payload.get("prompt", "")
    lang = payload.get("language", "python")
    u_type = payload.get("user_type") or payload.get("role") or "developer"

    instr = {
        "student": "AI Tutor: simple, commented code.",
        "enterprise": "Architect: secure, enterprise code.",
        "developer": "Expert: optimized, production code."
    }

    full_prompt = f"{instr.get(u_type, instr['developer'])}\nGenerate {lang} for: {u_prompt}\nReturn ONLY code."
    gen_text = get_ai_response(full_prompt, temp=0.6)
    
    match = re.search(r"```(?:\w+)?\n([\s\S]+?)\n```", gen_text)
    return {"generated_code": match.group(1) if match else gen_text.strip()}

@app.post("/api/review")
@app.post("/api/rewrite")
async def process_code(payload: dict = Body(...)):
    """Comprehensive Review logic with 'Payload Normalization'"""
    # Fix: Get code from 'code' or 'text'
    code = payload.get("code") or payload.get("text") or ""
    # Fix: Normalize User Type
    u_type = payload.get("user_type") or payload.get("role") or "developer"
    # Fix: Normalize Username (Fixes the 500 error)
    u_name = payload.get("student_name") or payload.get("username") or payload.get("email") or "Anonymous"

    if u_type == "student":
        STUDENT_STATS[u_name] = STUDENT_STATS.get(u_name, 0) + 1

    plag = check_plagiarism(code) if u_type == "student" else "N/A"
    
    personas = {
        "student": "AI Tutor: Explain errors simply and give hints.",
        "enterprise": "Security Auditor: Focus on OWASP and compliance.",
        "developer": "Senior Developer: Optimize for performance."
    }

    prompt = f"Act as {personas.get(u_type, personas['developer'])}. Review/Rewrite this code:\n{code}\nUse '### Critical' and '### High' for headers."
    review_text = get_ai_response(prompt)
    
    code_match = re.search(r"```(?:\w+)?\n([\s\S]+?)\n```", review_text)
    rewritten = code_match.group(1) if code_match else code

    return {
        "review": review_text,
        "rewritten_code": rewritten,
        "complexity": analyze_complexity(code),
        "time_complexity_original": analyze_complexity(code),
        "time_complexity_rewritten": analyze_complexity(rewritten) if rewritten else analyze_complexity(code),
        "plagiarism": plag,
        "student_stats": STUDENT_STATS.get(u_name, 0),
        "stats": {
            "critical": len(re.findall(r'### Critical', review_text)),
            "high": len(re.findall(r'### High', review_text)),
            "medium": len(re.findall(r'### Medium', review_text)),
            "low": len(re.findall(r'### Low', review_text))
        }
    }

# --- Authentication Endpoints ---

@app.post("/api/login")
async def login(payload: dict = Body(...)):
    """Simple authentication - demo users"""
    username = payload.get("username", "")
    password = payload.get("password", "")
    
    # Demo credentials
    valid_users = {
        "admin": "password",
        "student1": "password",
        "teacher": "password"
    }
    
    if username not in valid_users or valid_users[username] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    ACTIVE_SESSIONS[token] = {"username": username, "role": "admin" if username == "admin" else "user"}
    
    return {"token": token, "username": username, "message": "Login successful"}

@app.post("/api/logout")
async def logout(payload: dict = Body(...)):
    """Logout user"""
    token = payload.get("token", "")
    if token in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[token]
    return {"message": "Logged out"}

# --- Health Check ---

@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ocr_available": OCR_AVAILABLE,
        "model": "llama-3.3-70b-versatile",
        "version": "2.0.0"
    }

# --- OCR Endpoint ---

@app.post("/api/ocr")
async def ocr_scan(file: UploadFile = File(...)):
    """Extract code from image using OCR"""
    if not OCR_AVAILABLE:
        raise HTTPException(status_code=400, detail="OCR not available. Install pytesseract and tesseract-ocr")
    
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        extracted_text = pytesseract.image_to_string(image)
        return {"extracted_code": extracted_text, "message": "OCR completed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OCR failed: {str(e)}")

# --- Policy Upload ---

@app.post("/api/upload-policy")
async def upload_policy(file: UploadFile = File(...)):
    """Upload company policy for RAG"""
    global COMPANY_POLICIES
    try:
        contents = await file.read()
        COMPANY_POLICIES = contents.decode('utf-8', errors='ignore')
        return {"message": f"Policy uploaded: {len(COMPANY_POLICIES)} characters"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")

# --- Reset Plagiarism ---

@app.post("/api/reset-plagiarism")
async def reset_plagiarism():
    """Clear plagiarism database"""
    global CODE_DATABASE
    CODE_DATABASE = []
    return {"message": "Plagiarism database cleared"}

# --- Download Endpoints ---

@app.post("/api/download/summary")
async def download_summary(payload: dict = Body(...)):
    """Generate summary document"""
    format_type = payload.get("format", "docx")
    review = payload.get("review", "")
    stats = payload.get("stats", {})
    
    try:
        if format_type == "docx":
            from docx import Document
            doc = Document()
            doc.add_heading("Code Review Summary", 0)
            doc.add_paragraph(f"Critical Issues: {stats.get('critical', 0)}")
            doc.add_paragraph(f"High Priority: {stats.get('high', 0)}")
            doc.add_paragraph(f"Medium Priority: {stats.get('medium', 0)}")
            doc.add_paragraph(f"Low Priority: {stats.get('low', 0)}")
            doc.add_heading("Review Feedback", level=1)
            doc.add_paragraph(review)
            
            output = io.BytesIO()
            doc.save(output)
            output.seek(0)
            return FileResponse(output, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename="summary.docx")
        
        elif format_type == "pdf":
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Code Review Summary", ln=True)
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Critical: {stats.get('critical', 0)} | High: {stats.get('high', 0)} | Medium: {stats.get('medium', 0)}", ln=True)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Feedback:", ln=True)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 5, review[:500])
            
            output = io.BytesIO()
            pdf_content = pdf.output(dest='S').encode('latin-1')
            output.write(pdf_content)
            output.seek(0)
            return FileResponse(output, media_type="application/pdf", filename="summary.pdf")
        
        else:
            return {"error": "Invalid format"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Download failed: {str(e)}")

@app.post("/api/download/report")
async def download_report(payload: dict = Body(...)):
    """Generate complete report"""
    format_type = payload.get("format", "docx")
    original_code = payload.get("original_code", "")
    rewritten_code = payload.get("rewritten_code", "")
    review = payload.get("review", "")
    stats = payload.get("stats", {})
    complexity_original = payload.get("complexity_original", "O(n)")
    complexity_rewritten = payload.get("complexity_rewritten", "O(n)")
    
    try:
        if format_type == "docx":
            from docx import Document
            doc = Document()
            doc.add_heading("Code Refine Report", 0)
            
            doc.add_heading("Analysis Statistics", level=1)
            doc.add_paragraph(f"Critical Issues: {stats.get('critical', 0)}")
            doc.add_paragraph(f"High Priority: {stats.get('high', 0)}")
            doc.add_paragraph(f"Medium Priority: {stats.get('medium', 0)}")
            doc.add_paragraph(f"Low Priority: {stats.get('low', 0)}")
            
            doc.add_heading("Complexity Analysis", level=1)
            doc.add_paragraph(f"Original: {complexity_original}")
            doc.add_paragraph(f"Rewritten: {complexity_rewritten}")
            
            doc.add_heading("Original Code", level=1)
            doc.add_paragraph(original_code, style='List Number')
            
            doc.add_heading("Rewritten Code", level=1)
            doc.add_paragraph(rewritten_code, style='List Number')
            
            doc.add_heading("Review & Feedback", level=1)
            doc.add_paragraph(review)
            
            output = io.BytesIO()
            doc.save(output)
            output.seek(0)
            return FileResponse(output, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename="report.docx")
        
        elif format_type == "pdf":
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Code Refine Report", ln=True)
            
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Statistics:", ln=True)
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 5, f"Critical: {stats.get('critical', 0)} | High: {stats.get('high', 0)}", ln=True)
            pdf.cell(0, 5, f"Complexity Original: {complexity_original} | Rewritten: {complexity_rewritten}", ln=True)
            
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Original Code:", ln=True)
            pdf.set_font("Arial", "", 8)
            pdf.multi_cell(0, 4, original_code[:300])
            
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 5, "Rewritten Code:", ln=True)
            pdf.set_font("Arial", "", 8)
            pdf.multi_cell(0, 4, rewritten_code[:300])
            
            output = io.BytesIO()
            pdf_content = pdf.output(dest='S').encode('latin-1')
            output.write(pdf_content)
            output.seek(0)
            return FileResponse(output, media_type="application/pdf", filename="report.pdf")
        
        else:
            return {"error": "Invalid format"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Report generation failed: {str(e)}")

# --- Dashboard Endpoint ---

@app.get("/api/dashboard-data")
async def get_dashboard_data():
    """Get student dashboard data"""
    labels = list(STUDENT_STATS.keys()) if STUDENT_STATS else ["No data"]
    data = list(STUDENT_STATS.values()) if STUDENT_STATS else [0]
    
    return {
        "labels": labels,
        "data": data,
        "total_students": len(STUDENT_STATS),
        "total_reviews": sum(data)
    }

# --- NEW FEATURES ENDPOINTS ---

# 1. Code Diff Viewer
@app.post("/api/diff")
async def generate_diff(payload: dict = Body(...)):
    """Generate diff between two code versions"""
    original_code = payload.get("original_code", "")
    rewritten_code = payload.get("rewritten_code", "")
    
    if not original_code or not rewritten_code:
        raise HTTPException(status_code=400, detail="Both original and rewritten code required")
    
    diff = list(difflib.unified_diff(
        original_code.splitlines(keepends=True),
        rewritten_code.splitlines(keepends=True),
        fromfile='Original',
        tofile='Rewritten',
        lineterm=''
    ))
    
    similarity = difflib.SequenceMatcher(None, original_code, rewritten_code).ratio()
    
    return {
        "diff": ''.join(diff),
        "similarity_score": round(similarity * 100, 2),
        "lines_changed": len([d for d in diff if d.startswith(('+', '-'))])
    }

# 2. Language Detection
@app.post("/api/detect-language")
async def detect_language(payload: dict = Body(...)):
    """Auto-detect programming language from code"""
    code = payload.get("code", "")
    
    patterns = {
        "python": [r"^import\s+\w+", r"^from\s+\w+\s+import", r"def\s+\w+\s*\(", r"class\s+\w+:", r"if\s+__name__"],
        "javascript": [r"function\s+\w+\s*\(", r"const\s+\w+\s*=", r"let\s+\w+\s*=", r"=>", r"document\.", r"console\."],
        "java": [r"public\s+class\s+\w+", r"public\s+static\s+void", r"import\s+java\.", r"@Override"],
        "cpp": [r"#include\s*<", r"std::", r"using\s+namespace", r"int\s+main\s*\(", r"cout\s+<<"],
        "csharp": [r"using\s+System", r"public\s+class\s+\w+", r"namespace\s+\w+", r"static\s+void\s+Main"],
        "go": [r"package\s+\w+", r"func\s+\w+\s*\(", r"import\s+\(", r":="],
        "rust": [r"fn\s+\w+", r"let\s+mut\s+\w+", r"impl\s+\w+", r"pub\s+struct"],
    }
    
    scores = {}
    for lang, patterns_list in patterns.items():
        score = sum(1 for pattern in patterns_list if re.search(pattern, code))
        scores[lang] = score
    
    detected = max(scores, key=scores.get) if scores else "python"
    return {"detected_language": detected, "confidence": round(scores.get(detected, 0) / len(patterns.get(detected, [])) * 100, 1)}

# 3. Code Templates
@app.get("/api/templates/{language}")
async def get_templates(language: str):
    """Get code templates for a language"""
    templates = {
        "python": {
            "web_api": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\nasync def read_root():\n    return {'message': 'Hello World'}",
            "data_processing": "import pandas as pd\n\ndf = pd.read_csv('data.csv')\nprint(df.head())",
            "async": "import asyncio\n\nasync def main():\n    await asyncio.sleep(1)\n    print('Done')\n\nasyncio.run(main())",
        },
        "javascript": {
            "rest_api": "const express = require('express');\nconst app = express();\n\napp.get('/', (req, res) => {\n  res.json({message: 'Hello World'});\n});\n\napp.listen(3000);",
            "async_fetch": "async function fetchData(url) {\n  const response = await fetch(url);\n  return response.json();\n}",
            "class": "class User {\n  constructor(name, email) {\n    this.name = name;\n    this.email = email;\n  }\n}",
        },
        "java": {
            "main": "public class Main {\n  public static void main(String[] args) {\n    System.out.println(\"Hello World\");\n  }\n}",
            "class": "public class User {\n  private String name;\n  private String email;\n}",
        },
    }
    
    lang_templates = templates.get(language, {})
    return {"templates": lang_templates, "language": language}

# 4. Unit Test Generation
@app.post("/api/generate-tests")
async def generate_tests(payload: dict = Body(...)):
    """Generate unit tests for code"""
    code = payload.get("code", "")
    language = payload.get("language", "python")
    
    if not code:
        raise HTTPException(status_code=400, detail="Code is required")
    
    test_prompt = f"Generate unit tests for the following {language} code. Return ONLY test code:\n\n{code}"
    
    try:
        tests = get_ai_response(test_prompt, temp=0.3, max_tokens=1500)
        return {"tests": tests, "language": language, "framework": "pytest" if language == "python" else "jest"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test generation failed: {str(e)}")

# 5. Documentation Generator
@app.post("/api/generate-docs")
async def generate_docs(payload: dict = Body(...)):
    """Generate documentation for code"""
    code = payload.get("code", "")
    language = payload.get("language", "python")
    
    if not code:
        raise HTTPException(status_code=400, detail="Code is required")
    
    doc_prompt = f"Generate comprehensive documentation and comments for the following {language} code. Format as docstrings/comments:\n\n{code}"
    
    try:
        docs = get_ai_response(doc_prompt, temp=0.3, max_tokens=1500)
        return {"documentation": docs, "language": language}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Documentation generation failed: {str(e)}")

# 6. Code Security Scanner
@app.post("/api/security-scan")
async def security_scan(payload: dict = Body(...)):
    """Scan code for security vulnerabilities"""
    code = payload.get("code", "")
    language = payload.get("language", "python")
    
    if not code:
        raise HTTPException(status_code=400, detail="Code is required")
    
    security_prompt = f"Perform a security analysis on this {language} code. Identify vulnerabilities, security risks, and issues like SQL injection, XSS, hardcoded secrets, etc. Format as: CRITICAL: ... HIGH: ... MEDIUM: ...\n\n{code}"
    
    try:
        analysis = get_ai_response(security_prompt, temp=0.2, max_tokens=1000)
        return {"security_analysis": analysis, "language": language}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Security scan failed: {str(e)}")

# 7. Refactoring Suggestions
@app.post("/api/refactor-suggestions")
async def refactor_suggestions(payload: dict = Body(...)):
    """Get refactoring suggestions for code"""
    code = payload.get("code", "")
    language = payload.get("language", "python")
    
    if not code:
        raise HTTPException(status_code=400, detail="Code is required")
    
    refactor_prompt = f"Suggest refactoring improvements for this {language} code. Include: extract methods, consolidate duplicates, apply design patterns, improve naming, etc. Format as bullet points:\n\n{code}"
    
    try:
        suggestions = get_ai_response(refactor_prompt, temp=0.4, max_tokens=1000)
        return {"refactoring_suggestions": suggestions, "language": language}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refactoring suggestions failed: {str(e)}")

# 8. Code Snippets Management
@app.post("/api/snippets/save")
async def save_snippet(payload: dict = Body(...)):
    """Save code snippet to library"""
    user = payload.get("user", "default")
    title = payload.get("title", "Untitled")
    code = payload.get("code", "")
    language = payload.get("language", "python")
    
    if not code:
        raise HTTPException(status_code=400, detail="Code is required")
    
    if user not in CODE_SNIPPETS:
        CODE_SNIPPETS[user] = []
    
    snippet = {
        "id": len(CODE_SNIPPETS[user]),
        "title": title,
        "code": code,
        "language": language,
        "created": datetime.now().isoformat()
    }
    
    CODE_SNIPPETS[user].append(snippet)
    return {"message": "Snippet saved", "snippet_id": snippet["id"]}

@app.get("/api/snippets/{user}")
async def get_snippets(user: str):
    """Get user's saved snippets"""
    snippets = CODE_SNIPPETS.get(user, [])
    return {"snippets": snippets, "total": len(snippets)}

@app.delete("/api/snippets/{user}/{snippet_id}")
async def delete_snippet(user: str, snippet_id: int):
    """Delete a snippet"""
    if user in CODE_SNIPPETS and 0 <= snippet_id < len(CODE_SNIPPETS[user]):
        CODE_SNIPPETS[user].pop(snippet_id)
        return {"message": "Snippet deleted"}
    raise HTTPException(status_code=404, detail="Snippet not found")

# 9. Version History
@app.post("/api/history/save")
async def save_to_history(payload: dict = Body(...)):
    """Save code version to history"""
    user = payload.get("user", "default")
    code = payload.get("code", "")
    action = payload.get("action", "review")
    
    if user not in CODE_HISTORY:
        CODE_HISTORY[user] = []
    
    version = {
        "version": len(CODE_HISTORY[user]) + 1,
        "code": code,
        "action": action,
        "timestamp": datetime.now().isoformat()
    }
    
    CODE_HISTORY[user].append(version)
    return {"message": "Version saved", "version": version["version"]}

@app.get("/api/history/{user}")
async def get_history(user: str):
    """Get user's code history"""
    history = CODE_HISTORY.get(user, [])
    return {"history": history, "total_versions": len(history)}

# 10. User Analytics
@app.post("/api/analytics/track")
async def track_activity(payload: dict = Body(...)):
    """Track user activity"""
    user = payload.get("user", "default")
    action = payload.get("action", "review")
    language = payload.get("language", "python")
    
    if user not in USER_ANALYTICS:
        USER_ANALYTICS[user] = {"reviews": 0, "generations": 0, "languages": {}, "last_activity": ""}
    
    analytics = USER_ANALYTICS[user]
    if action == "review":
        analytics["reviews"] += 1
    elif action == "generate":
        analytics["generations"] += 1
    
    analytics["languages"][language] = analytics["languages"].get(language, 0) + 1
    analytics["last_activity"] = datetime.now().isoformat()
    
    return {"message": "Activity tracked"}

@app.get("/api/analytics/{user}")
async def get_analytics(user: str):
    """Get user analytics"""
    analytics = USER_ANALYTICS.get(user, {})
    return analytics

@app.get("/api/analytics/dashboard/global")
async def get_global_analytics():
    """Get global analytics for admin dashboard"""
    total_reviews = sum(a.get("reviews", 0) for a in USER_ANALYTICS.values())
    total_generations = sum(a.get("generations", 0) for a in USER_ANALYTICS.values())
    all_languages = {}
    
    for analytics in USER_ANALYTICS.values():
        for lang, count in analytics.get("languages", {}).items():
            all_languages[lang] = all_languages.get(lang, 0) + count
    
    return {
        "total_users": len(USER_ANALYTICS),
        "total_reviews": total_reviews,
        "total_generations": total_generations,
        "languages_used": all_languages,
        "most_used_language": max(all_languages, key=all_languages.get) if all_languages else "N/A"
    }

# --- Page Routing ---

@app.get("/{page}", response_class=HTMLResponse)
async def serve_ui(page: str):
    # Dynamic path finding
    base_path = Path(__file__).parent.parent / "frontend"
    file_map = {"app": "index.html", "dashboard": "dashboard.html", "login": "login.html"}
    
    target_file = file_map.get(page, "login.html")
    path = base_path / target_file
    
    if path.exists():
        return path.read_text(encoding="utf-8")
    return HTMLResponse("<h1>404: Page Not Found</h1>", status_code=404)

@app.get("/", response_class=HTMLResponse)
async def root():
    path = Path(__file__).parent.parent / "frontend" / "login.html"
    return path.read_text(encoding="utf-8") if path.exists() else "Login Page Not Found"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)