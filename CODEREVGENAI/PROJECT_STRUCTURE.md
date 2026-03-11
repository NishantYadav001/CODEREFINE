# CODEREFINE - Project Structure Guide

## Overview

This document outlines the complete project structure, file organization, and naming conventions for CODEREFINE.

---

## Directory Tree

```
CODEREFINE/
├── 📄 README.md                    # Project overview & quick start
├── 📄 LICENSE                      # MIT License
├── 📄 .gitignore                   # Git ignore rules
├── 📄 docker-compose.yml          # Development container setup
├── 📄 setup-project.ps1           # Windows setup script
│
└── 📁 CODEREVGENAI/               # Main application directory
    ├── 📄 README.md                # Application features
    ├── 📄 ARCHITECTURE.md          # System design
    ├── 📄 CONTRIBUTING.md          # Contribution guidelines
    ├── 📄 DEVELOPMENT.md           # Development guide
    ├── 📄 CI-CD.md                 # Pipeline documentation
    ├── 📄 Dockerfile               # Container image
    ├── 📄 docker-compose.yml       # Production setup
    ├── 📄 start.ps1                # Windows startup
    ├── 📄 start.sh                 # Linux startup
    │
    ├── 📁 backend/                 # Python FastAPI Application
    │   ├── 📄 main.py              # ⚠️  NEEDS REFACTORING (1962 lines)
    │   ├── 📄 config.py            # Configuration management
    │   ├── 📄 database.py          # Database models & operations
    │   ├── 📄 security.py          # Auth, encryption, hashing
    │   ├── 📄 ai_service.py        # AI model integration
    │   ├── 📄 dependencies.py      # FastAPI dependency injection
    │   ├── 📄 audit.py             # Audit logging
    │   ├── 📄 auth_guard.js        # Auth utilities
    │   ├── 📄 components.js        # Component utilities
    │   │
    │   ├── 📄 requirements.txt      # Production dependencies
    │   ├── 📄 requirements-dev.txt  # Development tools
    │   ├── 📄 requirements-optional.txt  # Optional features
    │   │
    │   ├── 📄 .env                 # ⚠️  NEVER COMMIT (local secrets)
    │   ├── 📄 .env.example         # Template (commit this)
    │   ├── 📄 generate_key.py      # Secret key generation
    │   ├── 📄 setup_admin.py       # Admin user setup
    │   ├── 📄 check_db.py          # Database health check
    │   ├── 📄 verify_auth.py       # Auth verification
    │   │
    │   ├── 📄 test_main.py         # Unit tests
    │   ├── 📁 __pycache__/         # Python cache (auto-generated)
    │   └── 📁 reports/             # Generated reports
    │
    ├── 📁 frontend/                # Web Interface
    │   ├── 📄 index.html           # Main application
    │   ├── 📄 login.html           # Authentication
    │   ├── 📄 landing.html         # Landing page
    │   ├── 📄 dashboard.html       # Admin dashboard
    │   ├── 📄 admin.html           # Admin panel
    │   ├── 📄 profile.html         # User profile
    │   ├── 📄 settings.html        # Settings page
    │   ├── 📄 generate.html        # Code generation
    │   ├── 📄 batch.html           # Batch processing
    │   ├── 📄 reports.html         # Reports page
    │   ├── 📄 help.html            # Help/Documentation
    │   ├── 📄 collab.html          # Collaboration features
    │   ├── 📄 404.html             # Error page
    │   │
    │   ├── 📄 main.js              # Core application logic
    │   ├── 📄 api.js               # API client
    │   ├── 📄 utils.js             # Utility functions
    │   ├── 📄 script.js            # Additional scripts
    │   ├── 📄 theme.js             # Theme management
    │   ├── 📄 styles.css           # Global styles
    │   ├── 📄 sw.js                # Service worker (PWA)
    │   │
    │   ├── 📄 package.json         # NPM configuration
    │   ├── 📄 vite.config.js       # Build configuration
    │   ├── 📄 manifest.json        # PWA manifest
    │   ├── 📄 vercel.json          # Vercel deployment
    │   │
    │   └── 📁 assets/              # Static assets
    │       ├── auth_guard.js
    │       ├── layout.js
    │       ├── main.js
    │       ├── styles.css
    │       ├── theme.js
    │       └── utils.js
    │
    └── 📁 .github/                 # GitHub configuration (optional)
        └── workflows/
            └── ci-cd.yml           # GitHub Actions pipeline
```

---

## File Organization Conventions

### Python Backend Files

#### Main Application Files
- **`main.py`** (1962 lines)
  - ⚠️ Needs refactoring into modules
  - Current: All routes, middleware, business logic
  - Should be split into:
    - `routes/*.py` - API endpoints
    - `services/*.py` - Business logic
    - `models/*.py` - Data models
    - `middleware/*.py` - Middleware

- **`config.py`** (settings & environment)
  - Application configuration
  - Environment variable loading
  - Model definitions

- **`database.py`** (database operations)
  - In-memory data stores
  - Database connection
  - Table initialization
  - User database

- **`security.py`** (authentication & encryption)
  - Password hashing
  - JWT token generation
  - Encryption/decryption
  - Input sanitization

- **`ai_service.py`** (AI integration)
  - AI model calls
  - Prompt engineering
  - Model response parsing

- **`dependencies.py`** (FastAPI dependency injection)
  - Current user retrieval
  - Permission checking
  - Role validation

- **`audit.py`** (logging & monitoring)
  - Audit trail recording
  - Request/response logging
  - User activity tracking

#### Setup & Utility Files
- **`generate_key.py`** - Generate encryption keys
- **`setup_admin.py`** - Initialize admin user
- **`check_db.py`** - Verify database connection
- **`verify_auth.py`** - Test authentication

#### Testing
- **`test_main.py`** - Unit tests
  - Test fixtures
  - Test cases for all endpoints
  - Integration tests

---

### Frontend Files

#### Main Pages
- **`index.html`** - Main application shell
- **`login.html`** - User login/signup
- **`dashboard.html`** - Analytics dashboard
- **`admin.html`** - Admin control panel
- **`profile.html`** - User profile
- **`settings.html`** - User settings
- **`generate.html`** - Code generation
- **`batch.html`** - Batch processing
- **`reports.html`** - Report viewing
- **`help.html`** - Help/Documentation
- **`collab.html`** - Collaboration
- **`404.html`** - Error page

#### JavaScript Files
- **`main.js`** - Core application
  - App initialization
  - Event handling
  - Page routing

- **`api.js`** - API client
  - HTTP requests
  - Error handling
  - Token management

- **`utils.js`** - Utility functions
  - Helper functions
  - Formatters
  - Validators

- **`script.js`** - Additional scripts
  - Feature-specific logic
  - Extensions

- **`theme.js`** - Theme management
  - Light/dark mode
  - Color scheme
  - Persistence

#### Styling
- **`styles.css`** - Global styles
  - Layout
  - Typography
  - Colors
  - Components

#### Static Assets
- **`assets/`** directory
  - Bundled/compiled code
  - Minified CSS
  - Compiled JavaScript

#### Configuration
- **`package.json`** - NPM dependencies
- **`vite.config.js`** - Build configuration
- **`manifest.json`** - PWA manifest
- **`vercel.json`** - Vercel deployment

---

## Naming Conventions

### Python Files
```
lowercase_with_underscores.py
```
- All lowercase
- Underscores for spaces
- Examples: `ai_service.py`, `database.py`

### Python Functions & Variables
```python
def get_user_by_id(user_id: int) -> dict:
    pass

CONSTANTS_USE_UPPERCASE = True

my_variable = "value"
```

### Python Classes
```python
class CodeReviewService:
    pass

class UserAuthentication:
    pass
```

### JavaScript Files
```
lowercase-with-hyphens.js
```
- Lowercase with hyphens
- OR camelCase for modules

### JavaScript Functions & Variables
```javascript
function getUserById(userId) {
    // Implementation
}

const API_BASE_URL = "http://localhost:8000";

let userCache = new Map();
```

### HTML Files
```
page-name.html
```
- Lowercase
- Hyphens for multi-word
- Always .html extension

### CSS Classes
```css
.component-name {
    margin: 0;
}

.component-name__element {
    padding: 1rem;
}

.component-name--modifier {
    color: blue;
}
```
- BEM naming convention
- Lowercase with hyphens

---

## Configuration Files

### Environment Variables (`.env`)
```
❌ Never commit .env
✅ Commit .env.example with template
```

Located: `backend/.env`

### Docker Configuration
- `Dockerfile` - Container image
- `docker-compose.yml` - Local development
- `.dockerignore` - Ignore patterns

### Build Configuration
- `vite.config.js` - Frontend build
- `package.json` - NPM projects

### CI/CD Configuration
- `.github/workflows/ci-cd.yml` - GitHub Actions
- `azure-pipelines.yml` - Azure DevOps

---

## Directory Purpose

### `/backend`
- Python FastAPI application
- Business logic
- Database operations
- AI integrations
- Authentication

### `/frontend`
- Web user interface
- HTML pages
- CSS styling
- JavaScript logic
- Static assets

### `/.github`
- GitHub-specific files
- CI/CD workflows
- Issue templates
- PR templates

---

## File Size Analysis

### Large Files (Needs Refactoring)
- ⚠️ **`main.py`** (1962 lines)
  - Should be modularized
  - Target: <500 lines
  - Split into routes/, services/, models/

### Medium Files
- `database.py` (121 lines) - Good size
- `security.py` - Good size
- `ai_service.py` - Good size

### Frontend Files
- `styles.css` - Organized and maintainable
- `main.js` - Consider modularization for large apps

---

## Code Organization Best Practices

### Backend (Python)

**Proposed Future Structure**:
```
backend/
├── main.py              # Entry point (simplified)
├── config.py            # Configuration
├── core/
│   ├── security.py
│   ├── database.py
│   └── audit.py
├── api/
│   ├── routes/
│   │   ├── auth.py
│   │   ├── code.py
│   │   ├── admin.py
│   │   └── user.py
│   └── dependencies.py
├── services/
│   ├── ai_service.py
│   ├── code_analyzer.py
│   ├── user_service.py
│   └── auth_service.py
├── models/
│   ├── schemas.py       # Pydantic models
│   └── database.py      # Database models
├── utils/
│   ├── validators.py
│   ├── formatters.py
│   └── helpers.py
└── tests/
    ├── test_auth.py
    ├── test_code.py
    └── conftest.py
```

### Frontend (JavaScript)

**Proposed Future Structure**:
```
frontend/
├── index.html
├── main.js              # App initialization
├── config.js            # Frontend config
├── api/
│   └── client.js        # API client
├── pages/
│   ├── login.html
│   ├── dashboard.html
│   └── ...
├── components/
│   ├── navbar.js
│   ├── editor.js
│   └── ...
├── utils/
│   ├── formatters.js
│   ├── validators.js
│   └── helpers.js
├── styles/
│   ├── main.css
│   ├── components.css
│   └── theme.css
└── tests/
    └── ...
```

---

## Documentation Organization

### Root Level Documentation
- `README.md` - Project overview
- `LICENSE` - Licensing information

### Application Level
- `ARCHITECTURE.md` - System design
- `CONTRIBUTING.md` - Contribution guidelines
- `DEVELOPMENT.md` - Development setup
- `CI-CD.md` - Pipeline documentation
- `PROJECT_STRUCTURE.md` - This file
- `STATUS.md` - Current status

### Code Documentation
- Docstrings in Python
- JSDoc comments in JavaScript
- Inline comments for complex logic

---

## Versioning

### Files/Folders
- No version suffixes in filenames
- Use Git for version control

### Changes
- Document in git commit messages
- Update CHANGELOG.md (if created)

---

## Scalability Notes

### For Growing Projects
1. Modularize `main.py`
2. Create separate route handlers
3. Move business logic to services
4. Implement proper data models
5. Add service layer abstractions

### For Frontend Growth
1. Create component library
2. Implement state management
3. Add build tool (Vite)
4. Create reusable utilities
5. Implement module system

---

**Document Version**: 2.0.0
**Last Updated**: February 2026
**Status**: Comprehensive Project Structure Documented
