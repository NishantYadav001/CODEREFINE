# CODEREFINE - Development Guide

## Table of Contents
1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Backend Development](#backend-development)
5. [Frontend Development](#frontend-development)
6. [Testing Strategy](#testing-strategy)
7. [Debugging](#debugging)
8. [Performance Optimization](#performance-optimization)
9. [Common Tasks](#common-tasks)
10. [Troubleshooting](#troubleshooting)

---

## Development Environment Setup

### Prerequisites
```bash
# Check Python version
python --version  # Should be 3.9 or later

# Check Git
git --version

# Check Docker (recommended)
docker --version
docker-compose --version
```

### Option 1: Docker Setup (Recommended)

```bash
# Clone repository
git clone https://github.com/NishantYadav001/CODEREFINE.git
cd CODEREFINE/CODEREVGENAI

# Create environment file
cp backend/.env.example backend/.env

# Edit .env with your API keys
# Open backend/.env and add:
# - GROQ_API_KEY
# - GEMINI_API_KEY
# - SECRET_KEY

# Start development environment
docker-compose up --build

# Application: http://localhost:8000
# Database: localhost:3306
```

### Option 2: Local Setup

```bash
# Navigate to project
cd CODEREFINE/CODEREVGENAI

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt

# Create .env file
cp backend/.env.example backend/.env
# Edit with your configuration

# Install pre-commit hooks
pre-commit install

# Run database setup
python backend/check_db.py

# Start development server
python backend/main.py
```

**Application Access**:
- URL: http://localhost:8000
- Login: admin / password (default)

---

## Project Structure

### Backend Organization
```
backend/
├── main.py                 # Routes & FastAPI app (NEEDS REFACTORING)
├── config.py              # Configuration settings
├── database.py            # Database operations & models
├── security.py            # JWT, encryption, hashing
├── dependencies.py        # FastAPI dependency injection
├── ai_service.py          # AI model integration
├── audit.py               # Logging & audit trails
├── auth_guard.js          # Authentication utilities
├── components.js          # Reusable components
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── requirements-optional.txt  # Optional features
├── test_main.py           # Unit tests
├── .env.example           # Environment template
└── reports/               # Generated reports
```

### Frontend Organization
```
frontend/
├── assets/               # Static assets
│   ├── main.js          # Bundled JavaScript
│   ├── styles.css       # Compiled styles
│   └── theme.js         # Theme system
├── index.html           # Main application
├── login.html           # Authentication page
├── dashboard.html       # Admin dashboard
├── admin.html           # Admin panel
├── profile.html         # User profile
├── settings.html        # Settings page
├── main.js              # Core application logic
├── styles.css           # Global styles
├── utils.js             # Utility functions
├── api.js               # API client
├── theme.js             # Theme management
├── sw.js                # Service worker
├── manifest.json        # PWA manifest
├── vite.config.js       # Build configuration
└── package.json         # Dependencies
```

---

## Development Workflow

### Daily Workflow
```bash
# 1. Start day - pull changes
git pull upstream main

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Make changes
# ... edit files ...

# 4. Run tests
pytest backend/ -v
black backend/ frontend/
flake8 backend/

# 5. Commit changes
git add .
git commit -m "feat(scope): Description"

# 6. Push to fork
git push origin feature/my-feature

# 7. Create Pull Request on GitHub
```

### Handling Merge Conflicts
```bash
# Update your branch from upstream
git fetch upstream
git merge upstream/main

# Resolve conflicts manually
# Then commit
git add .
git commit -m "Merge upstream/main"
git push origin your-branch
```

---

## Backend Development

### Adding New API Endpoint

**Step 1**: Define the route in `main.py`
```python
@app.post("/api/my-feature", dependencies=[Depends(get_current_user)])
async def my_feature(request: MyFeatureRequest) -> dict:
    """
    Description of the endpoint.
    
    Args:
        request: Request payload
        
    Returns:
        Response dictionary
    """
    try:
        # Business logic here
        result = process_data(request)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"success": False, "error": str(e)}
```

**Step 2**: Create Pydantic model in `database.py` or `main.py`
```python
from pydantic import BaseModel

class MyFeatureRequest(BaseModel):
    """Request model for my feature"""
    code: str
    language: str
    
    class Config:
        example = {
            "code": "print('hello')",
            "language": "python"
        }
```

**Step 3**: Add tests in `test_main.py`
```python
def test_my_feature():
    response = client.post(
        "/api/my-feature",
        json={"code": "print('hello')", "language": "python"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

### Database Operations

**Creating Tables**:
```python
def init_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS my_table (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                data LONGTEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.commit()
```

**Query Data**:
```python
def get_user_data(user_id: int):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM my_table WHERE user_id = %s",
            (user_id,)
        )
        return cursor.fetchall()
    return []
```

---

## Frontend Development

### Adding New Page

1. Create HTML file (`new-page.html`)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Page - CodeRefine</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div id="app">
        <!-- Page content -->
    </div>
    <script src="main.js"></script>
    <script src="new-page.js"></script>
</body>
</html>
```

2. Create JavaScript handler (`new-page.js`)
```javascript
/**
 * New Page Handler
 */
class NewPageHandler {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadData();
    }
    
    setupEventListeners() {
        document.getElementById('submit-btn')?.addEventListener('click', 
            () => this.handleSubmit());
    }
    
    async loadData() {
        try {
            const response = await fetch('/api/data', {
                headers: {'Authorization': `Bearer ${token}`}
            });
            const result = await response.json();
            this.render(result.data);
        } catch (error) {
            console.error('Error loading data:', error);
        }
    }
    
    async handleSubmit() {
        // Handle form submission
    }
    
    render(data) {
        // Update DOM with data
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new NewPageHandler();
    });
} else {
    new NewPageHandler();
}
```

3. Add CSS (`styles.css`)
```css
.new-page {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.new-page__header {
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 1.5rem;
}
```

---

## Testing Strategy

### Unit Tests (Backend)

```bash
# Run all tests
pytest backend/ -v

# Run specific test file
pytest backend/test_main.py

# Run with coverage
pytest backend/ --cov=backend --cov-report=html

# Run in watch mode (install pytest-watch first)
ptw backend/
```

### Test Structure
```python
import pytest
from fastapi.testclient import TestClient
from main import app, get_current_user

client = TestClient(app)

# Setup fixtures
@pytest.fixture
def auth_token():
    """Get valid auth token"""
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password"}
    )
    return response.json().get("data", {}).get("token")

# Test class for organization
class TestCodeReview:
    def test_review_valid_code(self, auth_token):
        """Test code review with valid input"""
        response = client.post(
            "/api/code/review",
            json={"code": "print('hello')", "language": "python"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_review_invalid_code(self, auth_token):
        """Test code review with invalid input"""
        response = client.post(
            "/api/code/review",
            json={"code": "", "language": ""},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422
```

### Test Coverage Goals
- Minimum 80% code coverage
- All public endpoints tested
- Error cases covered
- Edge cases validated

---

## Debugging

### Python Debugging

**Using pdb (Python Debugger)**:
```python
# Add breakpoint in code
import pdb
pdb.set_trace()  # Execution will pause here

# Or use built-in breakpoint() (Python 3.7+)
breakpoint()

# Commands:
# n - next line
# s - step into function
# c - continue execution
# l - list code
# p variable - print variable
# q - quit
```

**Using VSCode Debugger**:
1. Install Python extension
2. Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": ["backend.main:app", "--reload"],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```

### Frontend Debugging

**Browser DevTools**:
- Open: F12 or Ctrl+Shift+I
- Sources tab: Set breakpoints
- Console: Execute JavaScript
- Network: Monitor API calls

**Console Logging**:
```javascript
console.log('Message:', variable);
console.error('Error:', error);
console.table(array);  // Pretty print arrays/objects
console.time('timer'); // Performance timing
```

### API Debugging

**Using curl**:
```bash
# Test endpoint
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# With headers
curl -X GET http://localhost:8000/api/data \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Using HTTPie**:
```bash
http POST localhost:8000/api/auth/login \
  username=admin \
  password=password

http GET localhost:8000/api/data \
  "Authorization: Bearer YOUR_TOKEN"
```

---

## Performance Optimization

### Backend Optimization
1. **Database Indexing**: Add indexes for frequently queried columns
2. **Query Optimization**: Use `SELECT *`sparingly
3. **Caching**: Implement Redis for frequently accessed data
4. **Connection Pooling**: Use connection pools for databases
5. **Async Operations**: Use async/await for I/O operations

### Frontend Optimization
1. **Lazy Loading**: Load images/modules on demand
2. **Minification**: Minify CSS/JS in production
3. **Code Splitting**: Split JavaScript bundles
4. **Compression**: Enable gzip compression
5. **CDN**: Use CDN for static assets

---

## Common Tasks

### Adding New Dependency
```bash
# Install package
pip install package-name

# Add to requirements.txt
pip freeze | grep package-name >> backend/requirements.txt

# Update requirements-dev.txt if dev-only
echo "package-name" >> backend/requirements-dev.txt

# Commit changes
git add backend/requirements*.txt
git commit -m "chore: Add package-name dependency"
```

### Database Migration
```bash
# Backup current database
mysqldump -u user -p database > backup.sql

# Apply changes to database.py
# Then run migration
python backend/check_db.py
```

### Updating Configuration
```bash
# Update backend/.config.py
# Update backend/.env.example
# Update docker-compose.yml if needed
# Test with: docker-compose up --build
```

---

## Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Unix
taskkill /PID <PID> /F  # Windows
```

**Module Not Found Error**
```bash
# Reinstall dependencies
pip install --upgrade -r backend/requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"

# Verify package is installed
pip show package-name
```

**Database Connection Error**
```bash
# Check if MySQL is running
docker-compose ps

# View database logs
docker-compose logs db

# Restart database
docker-compose restart db

# Reset database (⚠️ deletes data)
docker-compose down -v
docker-compose up
```

**API Returns 401 Unauthorized**
```bash
# Verify token is included
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/data

# Check token expiration
# Default: 60 minutes

# Get new token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'
```

**Tests Failing**
```bash
# Run with verbose output
pytest backend/ -v -s

# Run specific test
pytest backend/test_main.py::test_function -v

# Clear pytest cache
pytest --cache-clear backend/
```

---

## Development Best Practices

1. **Always create feature branches**
   ```bash
   git checkout -b feature/description
   ```

2. **Write tests for new features**
   - Test happy path
   - Test error cases
   - Test edge cases

3. **Document your code**
   - Docstrings for all functions
   - Comments for complex logic
   - Update README when needed

4. **Keep commits atomic**
   - One logical change per commit
   - Descriptive commit messages

5. **Run tests before pushing**
   ```bash
   pytest backend/ -v
   black backend/
   flake8 backend/
   ```

6. **Keep dependencies updated**
   ```bash
   pip list --outdated
   pip install --upgrade <package>
   ```

---

**Document Version**: 2.0.0
**Last Updated**: February 2026
