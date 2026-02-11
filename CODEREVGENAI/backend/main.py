import os
import re
import io
import base64
import json
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