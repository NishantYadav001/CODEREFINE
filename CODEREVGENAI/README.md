# Code Refine AI 🚀

**Code Refine AI** is an advanced, AI-powered code review and refactoring tool designed to help developers, students, and organizations improve code quality, security, and performance. Powered by Groq's Llama 3.3 70B model.

## ✨ Features

### Core Capabilities
- **AI Code Review**: Comprehensive analysis identifying critical bugs, security vulnerabilities, and logic errors.
- **Auto-Refactoring**: Intelligent code rewriting to improve performance and readability.
- **Multi-Persona AI**:
  - 👨‍💻 **Developer**: Focuses on optimization and best practices.
  - 🎓 **Student**: Provides learning-oriented feedback and explanations.
  - 🏢 **Enterprise**: Audits for security (OWASP) and compliance.
- **Plagiarism Detection**: Checks student submissions against a local database.

### Advanced Tools
- **Code Diff Viewer**: Side-by-side comparison of original vs. refactored code.
- **Security Scanner**: Deep dive into potential vulnerabilities.
- **Unit Test Generator**: Auto-generates tests (Pytest/Jest).
- **Documentation Generator**: Creates docstrings and comments automatically.
- **Language Detection**: Auto-identifies programming languages.

### UI/UX
- **Dashboard**: Analytics for teachers/admins to track usage.
- **Dark/Light Mode**: Fully themable interface.
- **Real-time Feedback**: Toast notifications and progress tracking.
- **Smart Editor**: Drag & drop file upload, keyboard shortcuts (Ctrl+Enter), and syntax highlighting.
- **History & Snippets**: Save and manage code versions.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python), Uvicorn
- **AI Engine**: Groq API (Llama 3.3 70B)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JS
- **Database**: In-memory (SQLite/MySQL ready structure)
- **Security**: JWT Authentication, CORS, Input Validation

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Groq API Key (Get one at [console.groq.com](https://console.groq.com))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CODEREVGENAI
   ```

2. **Set up Environment**
   Create a `.env` file in `backend/` or root:
   ```env
   GROQ_API_KEY=your_api_key_here
   SECRET_KEY=your_secret_key
   ```

3. **Install Dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Run the Application**
   
   **Windows (PowerShell):**
   ```powershell
   .\start.ps1
   ```
   
   **Linux/Mac:**
   ```bash
   ./start.sh
   ```

   Or manually:
   ```bash
   python backend/main.py
   ```

## 📖 Usage

1. Open your browser to `http://127.0.0.1:8000/login`.
2. **Login** with demo credentials:
   - **Admin**: `admin` / `password`
   - **Student**: `student1` / `password`
   - **Teacher**: `teacher` / `password`
3. Navigate to the **App** to start reviewing code.
4. Check the **Dashboard** for analytics.

## 📂 Project Structure

```
CODEREVGENAI/
├── backend/
│   ├── main.py           # Core application logic
│   ├── ai_service.py     # AI integration (Groq/Gemini)
│   ├── database.py       # Database handling
│   └── ...
├── frontend/
│   ├── index.html        # Main tool interface
│   ├── dashboard.html    # Analytics dashboard
│   ├── assets/           # Static assets
│   └── ...
├── README.md             # Documentation
└── start.ps1             # Startup script
```

## 🛡️ API Documentation

Once the server is running, full interactive API documentation is available at:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

---
*Version 2.0.0*