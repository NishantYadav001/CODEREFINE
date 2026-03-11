# Code Refine AI 🚀

**Code Refine AI** is an advanced, AI-powered code review and refactoring tool designed to help developers, students, and organizations improve code quality, security, and performance. Powered by Groq's Llama 3.3 70B model.

## 📚 Quick Navigation

### For Users
- **[Getting Started](#getting-started)** - Installation & setup
- **[Features](#features)** - What you can do
- **[API Docs](http://127.0.0.1:8000/docs)** - Live Swagger UI
- **[Troubleshooting](DEVELOPMENT.md#troubleshooting)** - Common issues

### For Developers
- **[Architecture](ARCHITECTURE.md)** - System design overview
- **[Development Guide](DEVELOPMENT.md)** - Setup & development workflow
- **[Project Structure](PROJECT_STRUCTURE.md)** - File organization
- **[Contributing](CONTRIBUTING.md)** - How to contribute
- **[CI/CD Pipeline](CI-CD.md)** - Testing & deployment

### For DevOps/Deployment
- **[Deployment Guide](#deployment)** - Docker & cloud deployment
- **[Environment Configuration](backend/.env.example)** - Configuration template
- **[Docker Compose](docker-compose.yml)** - Local development setup

### Project Information
- **[Project Status](STATUS.md)** - Current state & roadmap
- **[Main README](../README.md)** - Root project overview

---

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
- **AI Engine**: Groq API (Llama 3.3 70B), Google Gemini
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Database**: MySQL 8.0 (with in-memory fallback)
- **Security**: JWT Authentication, CORS, Input Validation
- **Containerization**: Docker & Docker Compose

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Docker & Docker Compose (recommended)
- Groq API Key (Get one at [console.groq.com](https://console.groq.com))

### Quick Start (Docker)

```bash
# 1. Clone repository
git clone https://github.com/NishantYadav001/CODEREFINE.git
cd CODEREFINE/CODEREVGENAI

# 2. Setup environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# 3. Run with Docker
docker-compose up --build

# 4. Access application
# Browser: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Installation (Local)

1. **Clone the repository**
   ```bash
   git clone https://github.com/NishantYadav001/CODEREFINE.git
   cd CODEREFINE/CODEREVGENAI
   ```

2. **Set up Environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   cp .env.example .env
   ```

3. **Configure API Keys**
   Edit `backend/.env`:
   ```env
   GROQ_API_KEY=your_api_key_here
   GEMINI_API_KEY=your_gemini_key_here
   SECRET_KEY=generate_with_python_secrets
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

5. **Run the Application**
   ```bash
   python main.py
   ```
   Application: http://127.0.0.1:8000

## 📖 Usage

1. Open your browser to `http://127.0.0.1:8000/login`
2. **Login** with demo credentials:
   - **Admin**: `admin` / `password`
   - **Student**: `student1` / `password`
   - **Teacher**: `teacher` / `password`
3. Navigate to the **App** tab to start reviewing code
4. Check the **Dashboard** for analytics and insights
5. View **Settings** to configure preferences

## 📂 Project Structure

```
CODEREVGENAI/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── database.py          # Database operations
│   ├── security.py          # Auth & encryption
│   ├── ai_service.py        # AI integration
│   ├── dependencies.py      # Dependency injection
│   ├── audit.py             # Logging
│   ├── requirements.txt     # Dependencies
│   ├── .env.example         # Configuration template
│   └── test_main.py         # Tests
├── frontend/
│   ├── index.html           # Main application
│   ├── login.html           # Authentication
│   ├── dashboard.html       # Analytics
│   ├── main.js              # Core logic
│   ├── styles.css           # Styling
│   └── assets/              # Static files
├── docker-compose.yml       # Development setup
├── Dockerfile               # Container image
├── ARCHITECTURE.md          # System design
├── CONTRIBUTING.md          # Contribution guidelines
├── DEVELOPMENT.md           # Development guide
├── PROJECT_STRUCTURE.md     # File organization
├── CI-CD.md                 # Pipeline documentation
└── STATUS.md                # Project status
```

For more details, see [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 🔗 API Documentation

### Interactive Documentation (Live)
Once the server is running, access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints
- `POST /api/auth/login` - User authentication
- `POST /api/code/review` - Code review analysis
- `POST /api/code/refactor` - Code refactoring
- `GET /api/history` - Code history
- `GET /api/admin/dashboard` - Analytics (admin)
- `GET /api/health` - Health check

## 🔐 Security

### Implemented Security Features
- ✅ JWT-based authentication
- ✅ Password hashing (bcrypt)
- ✅ Secret encryption (Fernet)
- ✅ CORS protection
- ✅ Rate limiting (100 req/min)
- ✅ Input validation & sanitization
- ✅ SQL injection prevention
- ✅ Audit logging

### Security Best Practices
- Use strong `SECRET_KEY`
- Keep `.env` out of version control
- Enable HTTPS in production
- Rotate API keys regularly
- Monitor audit logs

## 📊 Performance

### Metrics
- **API Response Time**: < 2 seconds
- **Concurrent Users**: 50+ tested
- **Database Query Time**: < 500ms
- **Memory Usage**: < 500MB

### Optimization Tips
- Enable Redis caching (optional)
- Use connection pooling
- Implement proper indexing
- Monitor with application insights

## 🚀 Deployment

### Docker Deployment
```bash
docker build -t coderefine:latest .
docker run -p 8000:8000 --env-file .env coderefine:latest
```

### Cloud Deployment
- Azure Container Apps
- Azure App Service
- Kubernetes (AKS)
- AWS ECS/ECR
- Google Cloud Run

See [DEPLOYMENT.md](../DEVELOPMENT.md) for detailed instructions.

## 🧪 Testing

### Running Tests
```bash
pytest backend/ -v
pytest backend/ --cov=backend --cov-report=html
```

### Test Coverage
Current: Unknown (needs improvement)
Target: 80%+

See [CONTRIBUTING.md](CONTRIBUTING.md#testing) for testing guidelines.

## 🛠️ Development

### Local Development Setup
```bash
pip install -r backend/requirements-dev.txt
pre-commit install
pytest backend/ -v
```

### Code Quality Tools
```bash
black backend/          # Format
flake8 backend/         # Lint
mypy backend/           # Type check
pytest backend/         # Test
```

See [DEVELOPMENT.md](DEVELOPMENT.md) for comprehensive guide.

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design & components |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Development setup & workflow |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | File organization |
| [CI-CD.md](CI-CD.md) | Pipeline & deployment |
| [STATUS.md](STATUS.md) | Project status & roadmap |
| [../README.md](../README.md) | Root project overview |

## 🤝 Contributing

We welcome contributions! Please:
1. Read [CONTRIBUTING.md](CONTRIBUTING.md)
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 🐛 Troubleshooting

### Common Issues
| Issue | Solution |
|-------|----------|
| Port 8000 in use | `lsof -i :8000 \| kill -9 $PID` |
| DB connection fails | Check MySQL is running |
| Import errors | `pip install -r requirements.txt` |
| Tests fail | Clear cache: `pytest --cache-clear` |

See [DEVELOPMENT.md](DEVELOPMENT.md#troubleshooting) for more.

## 📝 License

This project is licensed under the MIT License - see [LICENSE](../LICENSE) file for details.

## 👥 Support & Community

- **GitHub Issues**: [Report bugs](https://github.com/NishantYadav001/CODEREFINE/issues)
- **Discussions**: [Ask questions](https://github.com/NishantYadav001/CODEREFINE/discussions)
- **Email**: support@coderefine.ai

## 🗺️ Roadmap

### Current Version (2.0.0)
- ✅ Core features working
- ✅ Documentation completed
- 🔄 Code refactoring
- 🔄 Test coverage improvements

### Next Release (2.1.0)
- [ ] Refactored code structure
- [ ] 80%+ test coverage
- [ ] GitHub Actions CI/CD
- [ ] Security enhancements

### Future (3.0.0+)
- [ ] GraphQL API
- [ ] WebSocket support
- [ ] Redis caching
- [ ] Mobile application
- [ ] Team collaboration

See [STATUS.md](STATUS.md) for detailed roadmap.

## 👨‍💻 Created By

**Nishant Yadav** - [GitHub Profile](https://github.com/NishantYadav001)

## 📞 Questions?

- Check [Troubleshooting](DEVELOPMENT.md#troubleshooting)
- Read [ARCHITECTURE.md](ARCHITECTURE.md)  
- Browse [STATUS.md](STATUS.md) for current work
- Create a [GitHub Issue](https://github.com/NishantYadav001/CODEREFINE/issues)

---

**Version**: 2.0.0  
**Last Updated**: February 19, 2026  
**Status**: Active Development  
**License**: MIT
