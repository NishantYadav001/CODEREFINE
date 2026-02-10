# Code Refine using FastAPI and Groq

An AI-powered code analysis and refactoring tool that uses Groq's Llama 3.3 70B model to review and rewrite code with different personas for various user types.

## Features

✨ **Multi-User Modes:**
- **Developer Mode** - Standard code optimization and improvements
- **Student Mode** - Educational feedback with hints and explanations
- **Organisation Mode** - Team-wide consistency and architectural review
- **Enterprise Mode** - Security-focused audit and compliance checking

🎯 **Core Capabilities:**
- Real-time AI code review with Groq API
- Automatic code rewriting and refactoring
- Plagiarism detection for student submissions
- Policy-based compliance checking (Enterprise)
- Code extraction from images (OCR)
- Student progress tracking and analytics
- Student dashboard for monitoring

🚀 **Technology Stack:**
- **Backend:** FastAPI + Uvicorn
- **Frontend:** HTML5 + Tailwind CSS + JavaScript
- **AI Engine:** Groq API (Llama 3.3 70B)
- **Database:** In-memory (can be upgraded to persistent storage)

## Prerequisites

- Python 3.9+
- Groq API Key (get it from [console.groq.com](https://console.groq.com))
- Modern web browser

## Quick Start

### Option 1: Using PowerShell (Windows)

```powershell
.\start.ps1
```

### Option 2: Using Bash (Mac/Linux)

```bash
chmod +x start.sh
./start.sh
```

### Option 3: Manual Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Edit .env file and add your GROQ_API_KEY

# Run server
python main.py
```

## Access the Application

Once the server is running:

1. **Login Page:** http://127.0.0.1:8000/login
2. **Main Tool:** http://127.0.0.1:8000/app
3. **Student Dashboard:** http://127.0.0.1:8000/dashboard
4. **API Documentation:** http://127.0.0.1:8000/docs

## Demo Credentials

```
Username: admin        OR  student1      OR  teacher
Password: password         password          password
```

## Project Structure

```
CODEREVGENAI/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt         # Python dependencies
│   ├── .env                     # Environment variables (GROQ_API_KEY)
│   └── __init__.py
├── frontend/
│   ├── login.html              # Authentication page
│   ├── index.html              # Main tool interface
│   └── dashboard.html          # Teacher analytics dashboard
├── start.ps1                   # PowerShell quick start script
├── start.sh                    # Bash quick start script
└── FIXES_SUMMARY.md           # Detailed fix documentation
```

## API Endpoints

### Authentication
- `POST /api/login` - Login with username/password
- `POST /api/logout` - Logout and clear session
- `GET /api/health` - Server health check

### Code Analysis
- `POST /api/review` - Review code with AI
- `POST /api/rewrite` - Rewrite code with AI
- `POST /api/ocr` - Extract code from images
- `POST /api/upload-policy` - Upload company policies

### Dashboard
- `GET /api/dashboard-data` - Get analytics
- `POST /api/reset-plagiarism` - Clear plagiarism database

## Configuration

### Environment Variables (.env)

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your API key from: https://console.groq.com/keys

## How It Works

### Code Review Flow
1. User logs in with credentials
2. Selects a user type (determines AI persona)
3. Pastes or uploads code
4. AI analyzes code using Groq's Llama 3.3 70B
5. Results show: critical issues, high/medium/low priority items
6. For students: plagiarism check is performed

### Code Rewrite Flow
1. User requests code rewriting
2. AI rewrites the code based on persona
3. Original and rewritten versions displayed side-by-side
4. User can copy the rewritten code

## Customization

### Add New User Types
Edit `personas` dictionary in `main.py`:

```python
personas = {
    "your_type": "Your custom AI persona description...",
    # ... more types
}
```

### Add Demo Users
Edit `DEMO_USERS` in `main.py`:

```python
DEMO_USERS = {
    "your_username": "your_password",
    # ... more users
}
```

### Change Server Port
In `main.py`, modify the uvicorn.run call:

```python
uvicorn.run(app, host="127.0.0.1", port=8080)  # Change 8000 to 8080
```

## Troubleshooting

### Issue: "GROQ_API_KEY not found"
- Make sure you have created `.env` file in `backend/` directory
- Add your API key: `GROQ_API_KEY=your_key_here`

### Issue: "Address already in use"
- Port 8000 is already in use
- Change to different port: `uvicorn.run(app, host="127.0.0.1", port=8001)`

### Issue: "ModuleNotFoundError"
- Activate virtual environment first
- Run: `pip install -r requirements.txt`

### Issue: Login fails
- Use demo credentials: admin/password
- Or add new users in DEMO_USERS dictionary

## Advanced Features (Optional)

### Re-enable ML-Based Plagiarism Detection
If you want better plagiarism detection using embeddings:

```bash
pip install sentence-transformers scikit-learn
```

Then uncomment the embedding code in `main.py`.

### Enable OCR for Image Code Extraction
To extract code from images:

1. Install Tesseract-OCR from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install Python package: `pip install pytesseract pillow`
3. Update pytesseract path in main.py if needed

## Performance Tips

- Keep the frontend open while using the tool
- For long code (>5000 lines), split into smaller chunks
- Clear plagiarism database periodically: `/api/reset-plagiarism`
- Monitor dashboard for student activity

## Security Considerations

⚠️ **Note:** This is a demo application. For production use:
- Implement proper authentication (JWT tokens)
- Use a proper database (PostgreSQL, MongoDB)
- Add rate limiting
- Implement HTTPS/TLS
- Add input validation and sanitization
- Use environment variables for all secrets
- Implement proper error handling

## Contributing

Feel free to enhance this project:
- Add new user personas
- Implement database persistence
- Add more code analysis features
- Improve UI/UX
- Add more languages support

## License

Open source - feel free to use and modify!

## Support

For issues or questions:
1. Check the FIXES_SUMMARY.md for recent fixes
2. Review API documentation at http://127.0.0.1:8000/docs
3. Check browser console for frontend errors
4. Check terminal output for backend errors

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Groq API Documentation](https://console.groq.com/docs/speech-text)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Groq Models](https://console.groq.com/docs/models)

---

**Status:** ✅ Server Running & Fully Functional

Made with ❤️ using FastAPI and Groq
