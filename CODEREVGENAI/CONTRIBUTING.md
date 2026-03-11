# Contributing to CODEREFINE

Thank you for your interest in contributing to CODEREFINE! We welcome contributions from the community. This document provides guidelines and instructions for contributing to the project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Quality Standards](#code-quality-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Reporting Issues](#reporting-issues)

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful to all contributors and users.

**Be respectful, professional, and constructive in all interactions.**

---

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+ (for frontend work)
- Git
- Docker (recommended)
- GitHub account

### Fork & Clone
```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/CODEREFINE.git
cd CODEREFINE

# 3. Add upstream remote
git remote add upstream https://github.com/NishantYadav001/CODEREFINE.git

# 4. Create feature branch
git checkout -b feature/your-feature-name
```

---

## Development Setup

### Local Development Environment

```bash
# 1. Navigate to project
cd CODEREVGENAI

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies (including dev tools)
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt

# 4. Setup pre-commit hooks
pre-commit install

# 5. Create .env file
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration

# 6. Initialize database
python backend/check_db.py

# 7. Run application
python backend/main.py
```

### With Docker
```bash
# Build and run with Docker Compose
docker-compose up --build

# Application available at: http://localhost:8000
```

---

## Making Changes

### Project Structure
```
CODEREVGENAI/
├── backend/
│   ├── main.py              # Routes & API endpoints
│   ├── ai_service.py        # AI integration
│   ├── database.py          # Database operations
│   ├── security.py          # Authentication & security
│   ├── config.py            # Configuration
│   ├── dependencies.py      # FastAPI dependencies
│   ├── audit.py             # Logging & audit
│   └── test_main.py         # Tests
├── frontend/
│   ├── index.html           # Main UI
│   ├── main.js              # Core application logic
│   ├── styles.css           # Styling
│   └── utils.js             # Utility functions
└── docker-compose.yml       # Development setup
```

### Code Style Guide

#### Python
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for function parameters and returns
- Max line length: 100 characters
- Use docstrings for all functions/classes

```python
def analyze_code(code: str, language: str) -> dict:
    """
    Analyze code using AI service.
    
    Args:
        code: Source code to analyze
        language: Programming language
    
    Returns:
        Dictionary containing analysis results
        
    Raises:
        ValueError: If code or language is invalid
    """
    pass
```

#### JavaScript
- Use ES6+ syntax
- Use meaningful variable names
- Use `const` by default, `let` if reassignment needed
- Avoid `var`
- Add JSDoc comments for functions

```javascript
/**
 * Fetch code review from API
 * @param {string} code - Code to review
 * @returns {Promise<Object>} Review results
 */
async function fetchCodeReview(code) {
    // Implementation
}
```

#### CSS
- Use BEM naming convention
- Media queries at end of rule
- Use CSS variables for theming
- Minify for production

```css
.code-editor__input {
    width: 100%;
    padding: 1rem;
}

.code-editor__input:focus {
    outline: 2px solid var(--color-primary);
}
```

### Testing Before Commit

```bash
# Run all tests
pytest backend/ -v

# Run with coverage
pytest backend/ --cov

# Format code
black backend/ frontend/

# Lint code
flake8 backend/

# Type checking
mypy backend/

# Sort imports
isort backend/ frontend/
```

---

## Commit Guidelines

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build, dependencies, etc

### Examples
```
feat(ai-service): Add support for Claude API integration

fix(auth): Fix JWT token validation for expired tokens

docs(readme): Update installation instructions

refactor(main): Split monolithic main.py into modules

test(database): Add tests for user creation
```

### Commit Best Practices
- Write descriptive commit messages
- Keep commits focused and atomic
- Reference related issues: "Fixes #123"
- Include breaking changes in footer
```
BREAKING CHANGE: API endpoint /api/review now requires Content-Type header
```

---

## Pull Request Process

### Before Creating PR
1. Create feature branch from `main`
2. Make your changes
3. Run all tests and linters
4. Update documentation
5. Keep commits clean and descriptive

### Creating PR
1. Push your branch to your fork
2. Open Pull Request on GitHub
3. Fill in PR template completely
4. Link related issues
5. Request review from maintainers

### PR Template
```markdown
## Description
Brief description of changes

## Related Issues
Fixes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] No new test failures

## Checklist
- [ ] Code follows style guide
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No hardcoded credentials
- [ ] CHANGELOG.md updated
```

### PR Review Process
- All PRs require at least 1 approval
- CI/CD checks must pass
- No merge conflicts
- Maintainers may request changes

---

## Code Quality Standards

### Quality Checklist
- ✅ No hardcoded values (use configuration)
- ✅ No credentials in code
- ✅ Proper error handling
- ✅ Input validation
- ✅ Type hints (Python)
- ✅ Docstrings for public APIs
- ✅ No console.log in production code
- ✅ No commented-out code
- ✅ DRY principle followed

### Code Review Criteria
- Code clarity and readability
- Performance implications
- Security vulnerabilities
- Test coverage
- Documentation quality
- Adherence to project standards

---

## Testing

### Running Tests

```bash
# Run all tests
pytest backend/ -v

# Run specific test file
pytest backend/test_main.py

# Run specific test
pytest backend/test_main.py::test_login

# Run with coverage report
pytest backend/ --cov --cov-report=html

# Run tests in watch mode
pytest-watch backend/
```

### Writing Tests

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/api/auth/login",
        json={"username": "invalid", "password": "wrong"}
    )
    assert response.status_code == 401
    assert response.json()["success"] is False

@pytest.mark.asyncio
async def test_code_review():
    """Test code review endpoint"""
    response = client.post(
        "/api/code/review",
        json={"code": "print('hello')", "language": "python"}
    )
    assert response.status_code == 200
```

### Test Coverage Target
- Minimum 80% code coverage
- All public APIs must be tested
- Edge cases should be covered

---

## Documentation

### Updating Documentation
- Update README.md for user-facing changes
- Update ARCHITECTURE.md for design changes
- Add docstrings to new functions
- Update API documentation

### Documentation Standards
- Clear and concise writing
- Code examples where applicable
- Links to related sections
- Keep format consistent

---

## Reporting Issues

### Bug Reports
Include:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment (OS, Python version, etc)
- Error logs/screenshots

### Feature Requests
Include:
- Detailed description
- Use case/motivation
- Proposed implementation (optional)
- Related issues/discussions

### Security Issues
**DO NOT create public issues for security vulnerabilities**
- Email: security@coderefine.ai
- Include description and reproduction steps
- Allow time for patch before disclosure

---

## Commit Access

Contributors with consistent quality contributions may be granted commit access. This includes:
- Direct push to main only after approval
- Ability to review and merge PRs
- Release management responsibilities

---

## Development Tips

### Useful Commands
```bash
# Format all Python files
black backend/

# Sort imports
isort backend/

# Run linter
flake8 backend/

# Type checking
mypy backend/

# View git status
git status

# See diff before commit
git diff

# Stash changes temporarily
git stash

# View commit history
git log --oneline -10
```

### Debugging
```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use breakpoint() in Python 3.7+
breakpoint()

# Print debugging
print(f"Debug: {variable}")
```

### Common Issues

**Issue**: Database connection fails
```bash
# Check MySQL is running
docker-compose ps

# Restart database
docker-compose restart db
```

**Issue**: Dependencies conflict
```bash
# Reinstall packages
pip install --upgrade -r backend/requirements.txt

# Clear cache
pip cache purge
```

---

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- GitHub contributors page
- Release notes for significant contributions

---

## Questions?

- Check existing [GitHub Issues](https://github.com/NishantYadav001/CODEREFINE/issues)
- Refer to [ARCHITECTURE.md](ARCHITECTURE.md) for design
- Review [API.md](API.md) for endpoint documentation
- Create a [Discussion](https://github.com/NishantYadav001/CODEREFINE/discussions) for questions

---

**Thank you for contributing to CODEREFINE! 🚀**

---

*Last Updated: February 2026*
