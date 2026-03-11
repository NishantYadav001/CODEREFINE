# CODEREFINE - AI-Powered Code Review & Refactoring Platform

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 📋 Table of Contents
- [About](#about)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Support](#support)

## About

**CODEREFINE** is an advanced AI-powered platform for:
- 🎯 **Intelligent Code Review** - Identify bugs, security issues, and logic errors
- 🔄 **Auto-Refactoring** - Intelligent code improvements and optimization
- 👥 **Multi-Persona AI** - Developer, Student, and Enterprise perspectives
- 🛡️ **Security Analysis** - Deep vulnerability scanning
- 📊 **Analytics Dashboard** - Usage tracking and insights
- 🎓 **Educational Support** - Learning-oriented feedback

**Powered by:** Groq's Llama 3.3 70B & Google's Gemini

## Project Structure

```
CODEREFINE/
├── CODEREVGENAI/              # Main application folder
│   ├── backend/               # Python FastAPI backend
│   │   ├── main.py           # Core application entry point
│   │   ├── config.py         # Configuration management
│   │   ├── database.py       # Database operations
│   │   ├── security.py       # Authentication & encryption
│   │   ├── ai_service.py     # AI integration
│   │   ├── dependencies.py   # FastAPI dependencies
│   │   ├── audit.py          # Audit logging
│   │   └── requirements.txt  # Python dependencies
│   ├── frontend/              # Web interface (HTML/CSS/JS)
│   │   ├── index.html        # Main application
│   │   ├── login.html        # Authentication
│   │   ├── dashboard.html    # Analytics dashboard
│   │   ├── admin.html        # Admin panel
│   │   ├── styles.css        # Global styles
│   │   ├── main.js           # Core application logic
│   │   └── utils.js          # Utility functions
│   ├── docker-compose.yml    # Local development setup
│   ├── Dockerfile            # Container image
│   ├── README.md             # Application documentation
│   └── start.ps1/start.sh    # Startup scripts
├── README.md                 # This file
├── docker-compose.yml        # Root-level compose
└── setup-project.ps1         # Initial setup script
```

## Quick Start

### Prerequisites
- Python 3.9+
- Docker & Docker Compose (recommended)
- Groq API Key ([get one here](https://console.groq.com))

### Option 1: Docker (Recommended)

```bash
# 1. Navigate to project
cd CODEREVGENAI

# 2. Create .env file in backend/
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# 3. Run with Docker Compose
docker-compose up --build

# 4. Open browser
# Application: http://localhost:8000
```

### Option 2: Local Installation

```bash
# 1. Navigate to backend
cd CODEREVGENAI/backend

# 2. Create environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env with your configuration

# 5. Run application
python main.py

# Application available at: http://localhost:8000
```

### Default Credentials

```
Admin Account:
  Username: admin
  Password: password

Student Account:
  Username: student1
  Password: password

Teacher Account:
  Username: teacher
  Password: password
```

## Documentation

| Document | Purpose |
|----------|---------|
| [CODEREVGENAI/README.md](CODEREVGENAI/README.md) | Application features & technical details |
| [ARCHITECTURE.md](CODEREFINE/ARCHITECTURE.md) | System design & component overview |
| [CONTRIBUTING.md](CODEREFINE/CONTRIBUTING.md) | Contribution guidelines |
| [DEVELOPMENT.md](CODEREFINE/DEVELOPMENT.md) | Development setup & workflows |
| [DEPLOYMENT.md](CODEREFINE/DEPLOYMENT.md) | Production deployment guide |
| [API.md](CODEREFINE/API.md) | REST API documentation |

## Development

### Project Setup

```bash
# Install all dependencies
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt  # Dev tools

# Install pre-commit hooks (optional)
pre-commit install

# Run tests
pytest backend/test_main.py -v
```

### Code Organization

**Backend Structure:**
- `/models` - Pydantic data models (future)
- `/routes` - API endpoints (future)
- `/services` - Business logic (future)
- `/utils` - Utility functions
- `/tests` - Unit & integration tests

### Running Tests

```bash
# Run all tests
pytest backend/ -v

# Run specific test file
pytest backend/test_main.py -v

# Run with coverage
pytest backend/ --cov
```

### Code Quality

```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Type checking
mypy backend/
```

## Deployment

### Deploy to Azure
See [DEPLOYMENT.md](CODEREFINE/DEPLOYMENT.md) for Azure Container Apps, App Service, or AKS deployment.

### Deploy to Docker
```bash
# Build and push
docker build -t your-registry/coderefine:2.0.0 .
docker push your-registry/coderefine:2.0.0

# Run container
docker run -p 8000:8000 --env-file .env your-registry/coderefine:2.0.0
```

### Environment Variables

```env
# API Keys
GROQ_API_KEY=your_api_key

# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=secure_password
DB_NAME=coderefine

# Security
SECRET_KEY=your_secret_key
ADMIN_PASSWORD=admin

# SMTP (for email notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASSWORD=your_password

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## Features

### Core Capabilities
- ✅ AI-powered code review and analysis
- ✅ Automatic code refactoring suggestions
- ✅ Security vulnerability detection (OWASP)
- ✅ Code plagiarism detection
- ✅ Multi-language support
- ✅ Real-time diff viewer
- ✅ Unit test generation
- ✅ API documentation generation

### Admin Features
- 📊 Usage analytics dashboard
- 👥 User management
- 🔐 Role-based access control
- 📋 Audit logging
- ⚙️ System configuration

### Security
- 🔐 JWT authentication
- 🛡️ CORS protection
- 🔑 Encrypted secrets
- 📝 API rate limiting
- ✅ Input validation & sanitization

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.11 + FastAPI |
| Server | Uvicorn + Gunicorn |
| Database | MySQL 8.0 |
| Frontend | HTML5 + Tailwind CSS + Vanilla JS |
| AI Engine | Groq API (Llama 3.3 70B) |
| Containerization | Docker + Docker Compose |
| Authentication | JWT + bcrypt |

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Database Connection Issues
```bash
# Check MySQL is running
docker-compose ps

# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db
```

### Missing Dependencies
```bash
# Reinstall all requirements
pip install --upgrade -r backend/requirements.txt

# Clear pip cache
pip cache purge
```

## Performance Metrics

- **Response Time**: < 2 seconds for code review
- **Concurrent Users**: 100+ (tested)
- **Database Query Time**: < 500ms
- **API Rate Limit**: 100 requests/minute per IP

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CODEREFINE/CONTRIBUTING.md) for guidelines.

**Quick contribution flow:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📧 **Email**: support@coderefine.ai
- 📚 **Documentation**: [Full Docs](CODEREFINE/README.md)
- 🐛 **Issue Tracker**: [GitHub Issues](https://github.com/NishantYadav001/CODEREFINE/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/NishantYadav001/CODEREFINE/discussions)

## Roadmap

- [ ] Multi-language support expansion (Go, Rust, Ruby)
- [ ] GPU acceleration for analysis
- [ ] Advanced ML-based insights
- [ ] Cloud IDE integration
- [ ] Team collaboration features
- [ ] Mobile application
- [ ] Browser extension

## Authors

- **Nishant Yadav** - [GitHub](https://github.com/NishantYadav001)

---

**Last Updated**: February 2026 | **Status**: Active Development
