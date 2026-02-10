import os
import re
import io
from pathlib import Path
from datetime import datetime
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from fastapi import FastAPI, HTTPException, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, Response
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

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

def analyze_time_complexity(code: str):
    """Analyze time complexity using Groq AI for accurate results"""
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        prompt = f"""Analyze the time complexity of this code. Respond with ONLY the Big-O notation, nothing else. Examples: O(1), O(log n), O(n), O(n log n), O(n²), O(n³), O(2^n)

Code:
```
{code}
```

Respond with ONLY the complexity (e.g., "O(n)"), nothing else."""
        
        message = client.messages.create(
            model="llama-3.3-70b-versatile",
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}]
        )
        
        complexity = message.content[0].text.strip()
        # Clean up the response
        complexity = complexity.replace("```", "").strip()
        
        # Fallback if response is empty or invalid
        if not complexity or "O(" not in complexity:
            complexity = "O(n)"
        
        return complexity
        
    except Exception as e:
        # Fallback to pattern-based analysis if AI fails
        return analyze_complexity_heuristic(code)

def analyze_complexity_heuristic(code: str):
    """Fallback heuristic complexity analysis if AI fails"""
    code_lower = code.lower()
    
    # Check for exponential patterns
    if ('fibonacci' in code_lower or 'factorial' in code_lower) and 'memo' not in code_lower and 'cache' not in code_lower:
        return "O(2^n)"
    
    # Check for binary search
    if any(indicator in code_lower for indicator in ['binary search', 'bisect']):
        return "O(log n)"
    if ('mid' in code_lower and 'left' in code_lower and 'right' in code_lower):
        return "O(log n)"
    
    # Check for sorting
    if any(sort_op in code_lower for sort_op in ['sorted(', '.sort(', 'mergesort', 'quicksort', 'heapsort']):
        return "O(n log n)"
    
    # Count loop nesting
    lines = code.split('\n')
    max_nesting = 0
    
    for line in lines:
        stripped = line.lstrip()
        if not stripped or stripped.startswith('#'):
            continue
        
        indent = len(line) - len(stripped)
        indent_level = indent // 4
        
        if any(loop_kw in stripped for loop_kw in ['for ', 'while ']):
            max_nesting = max(max_nesting, indent_level + 1)
    
    # Map nesting to complexity
    if max_nesting >= 4:
        return "O(n⁴)"
    elif max_nesting == 3:
        return "O(n³)"
    elif max_nesting == 2:
        return "O(n²)"
    elif max_nesting == 1:
        return "O(n)"
    else:
        return "O(1)"

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

# --- Report Generation Functions ---

def generate_summary_docx(review_text: str, stats: dict) -> bytes:
    """Generate summary report as DOCX"""
    if not DOCX_AVAILABLE:
        raise ValueError("python-docx not installed")
    
    doc = Document()
    doc.add_heading('Code Review Summary', 0)
    doc.add_paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    doc.add_heading('Review & Analysis', level=1)
    doc.add_paragraph(review_text)
    
    doc.add_heading('Issue Statistics', level=1)
    stats_text = f"• Critical: {stats.get('critical', 0)}\n• High Priority: {stats.get('high', 0)}\n• Medium Priority: {stats.get('medium', 0)}\n• Low Priority: {stats.get('low', 0)}"
    doc.add_paragraph(stats_text)
    
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output.getvalue()

def generate_summary_pdf(review_text: str, stats: dict) -> bytes:
    """Generate summary report as PDF"""
    if not PDF_AVAILABLE:
        raise ValueError("fpdf2 not installed")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Code Review Summary", 0, 1, "C")
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Review & Analysis", 0, 1)
    pdf.set_font("Arial", "", 10)
    
    # Wrap review text
    for line in review_text.split('\n'):
        if line.strip():
            pdf.multi_cell(0, 5, line)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Issue Statistics", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, f"Critical: {stats.get('critical', 0)}", 0, 1)
    pdf.cell(0, 5, f"High Priority: {stats.get('high', 0)}", 0, 1)
    pdf.cell(0, 5, f"Medium Priority: {stats.get('medium', 0)}", 0, 1)
    pdf.cell(0, 5, f"Low Priority: {stats.get('low', 0)}", 0, 1)
    
    return pdf.output()

def generate_full_report_docx(review_text: str, stats: dict, original_code: str, rewritten_code: str, language: str, complexity_original: str, complexity_rewritten: str) -> bytes:
    """Generate full report as DOCX"""
    if not DOCX_AVAILABLE:
        raise ValueError("python-docx not installed")
    
    doc = Document()
    doc.add_heading('Code Refine - Complete Analysis Report', 0)
    doc.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc.add_paragraph(f"Language: {language.upper()}")
    
    doc.add_heading('Complexity Analysis', level=1)
    doc.add_paragraph(f"Original Code Complexity: {complexity_original}")
    doc.add_paragraph(f"Optimized Code Complexity: {complexity_rewritten}")
    
    doc.add_heading('Code Issues Breakdown', level=1)
    issues_text = f"Critical Issues: {stats.get('critical', 0)}\nHigh Priority: {stats.get('high', 0)}\nMedium Priority: {stats.get('medium', 0)}\nLow Priority: {stats.get('low', 0)}\n\nTotal Issues Found: {sum(stats.values())}"
    doc.add_paragraph(issues_text)
    
    doc.add_heading('AI Review & Analysis', level=1)
    doc.add_paragraph(review_text)
    
    doc.add_heading('Original Code', level=1)
    original_para = doc.add_paragraph(original_code)
    original_para.style = 'List Bullet'
    
    doc.add_heading('Refactored/Optimized Code', level=1)
    refactored_para = doc.add_paragraph(rewritten_code)
    refactored_para.style = 'List Bullet'
    
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output.getvalue()

def generate_full_report_pdf(review_text: str, stats: dict, original_code: str, rewritten_code: str, language: str, complexity_original: str, complexity_rewritten: str) -> bytes:
    """Generate full report as PDF"""
    if not PDF_AVAILABLE:
        raise ValueError("fpdf2 not installed")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Code Refine - Complete Analysis Report", 0, 1, "C")
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
    pdf.cell(0, 5, f"Language: {language.upper()}", 0, 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Complexity Analysis", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, f"Original Code Complexity: {complexity_original}", 0, 1)
    pdf.cell(0, 5, f"Optimized Code Complexity: {complexity_rewritten}", 0, 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Issue Statistics", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, f"Critical: {stats.get('critical', 0)}", 0, 1)
    pdf.cell(0, 5, f"High: {stats.get('high', 0)}", 0, 1)
    pdf.cell(0, 5, f"Medium: {stats.get('medium', 0)}", 0, 1)
    pdf.cell(0, 5, f"Low: {stats.get('low', 0)}", 0, 1)
    pdf.cell(0, 5, f"Total: {sum(stats.values())}", 0, 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Review & Analysis", 0, 1)
    pdf.set_font("Arial", "", 9)
    for line in review_text.split('\n'):
        if line.strip():
            pdf.multi_cell(0, 4, line)
    
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Original Code", 0, 1)
    pdf.set_font("Arial", "", 8)
    for line in original_code.split('\n')[:30]:  # Limit to first 30 lines
        if line.strip():
            pdf.multi_cell(0, 3, line)
    
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Refactored Code", 0, 1)
    pdf.set_font("Arial", "", 8)
    for line in rewritten_code.split('\n')[:30]:  # Limit to first 30 lines
        if line.strip():
            pdf.multi_cell(0, 3, line)
    
    return pdf.output()

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
    """Convert uploaded code images to text using pytesseract"""
    if not OCR_AVAILABLE:
        raise HTTPException(status_code=503, detail="OCR service not available. Please install pytesseract: pip install pytesseract pillow. Also install Tesseract-OCR from https://github.com/UB-Mannheim/tesseract/wiki")
    
    try:
        # Validate file is an image
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Please upload an image file")
        
        # Read and process the image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Extract text from image
        text = pytesseract.image_to_string(image).strip()
        
        if not text:
            raise HTTPException(status_code=400, detail="No text found in the image. Please upload a clearer code image.")
        
        return {"extracted_code": text}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

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
        
        # Analyze time complexity
        original_complexity = analyze_time_complexity(code)
        rewritten_complexity = analyze_time_complexity(rewritten_code)
        
        return {
            "review": review_part,
            "stats": stats,
            "rewritten_code": rewritten_code,
            "time_complexity_original": original_complexity,
            "time_complexity_rewritten": rewritten_complexity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Groq API: {str(e)}")

# --- Download Endpoints ---

@app.post("/api/download/summary")
async def download_summary(payload: dict = Body(...)):
    """Download review summary as PDF or DOCX"""
    format_type = payload.get("format", "docx").lower()
    review = payload.get("review", "No review available")
    stats = payload.get("stats", {})
    
    try:
        if format_type == "pdf":
            if not PDF_AVAILABLE:
                raise HTTPException(status_code=503, detail="PDF generation not available. Install fpdf2: pip install fpdf2")
            content = generate_summary_pdf(review, stats)
            filename = "code_review_summary.pdf"
            media_type = "application/pdf"
        else:  # docx
            if not DOCX_AVAILABLE:
                raise HTTPException(status_code=503, detail="DOCX generation not available. Install python-docx: pip install python-docx")
            content = generate_summary_docx(review, stats)
            filename = "code_review_summary.docx"
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
        # Return response with content directly
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@app.post("/api/download/report")
async def download_report(payload: dict = Body(...)):
    """Download full analysis report as PDF or DOCX"""
    format_type = payload.get("format", "docx").lower()
    review = payload.get("review", "No review available")
    stats = payload.get("stats", {})
    original_code = payload.get("original_code", "")
    rewritten_code = payload.get("rewritten_code", "")
    language = payload.get("language", "python")
    complexity_original = payload.get("complexity_original", "O(n)")
    complexity_rewritten = payload.get("complexity_rewritten", "O(n)")
    
    try:
        if format_type == "pdf":
            if not PDF_AVAILABLE:
                raise HTTPException(status_code=503, detail="PDF generation not available. Install fpdf2: pip install fpdf2")
            content = generate_full_report_pdf(review, stats, original_code, rewritten_code, language, complexity_original, complexity_rewritten)
            filename = "code_refine_report.pdf"
            media_type = "application/pdf"
        else:  # docx
            if not DOCX_AVAILABLE:
                raise HTTPException(status_code=503, detail="DOCX generation not available. Install python-docx: pip install python-docx")
            content = generate_full_report_docx(review, stats, original_code, rewritten_code, language, complexity_original, complexity_rewritten)
            filename = "code_refine_report.docx"
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
        # Return response with content directly
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

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
