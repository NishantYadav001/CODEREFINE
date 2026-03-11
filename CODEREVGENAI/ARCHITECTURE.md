# CODEREFINE - System Architecture

## Table of Contents
1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Components](#components)
4. [Data Flow](#data-flow)
5. [Database Schema](#database-schema)
6. [API Architecture](#api-architecture)
7. [Deployment Architecture](#deployment-architecture)
8. [Security Architecture](#security-architecture)

---

## Overview

CODEREFINE is a modern, cloud-native AI platform for intelligent code review and refactoring. It follows a **microservices-ready** architecture with separation of concerns:

- **Backend**: FastAPI-based REST API with business logic
- **Frontend**: Single-page application with vanilla JavaScript
- **Database**: MySQL for persistent storage
- **AI Layer**: Integration with multiple AI providers (Groq, Google Gemini)
- **Security**: JWT authentication, role-based access control (RBAC)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Web Browser (HTML5 + CSS + JS)                 │  │
│  │  - Authentication UI                                     │  │
│  │  - Code Editor & Review Interface                        │  │
│  │  - Dashboard & Analytics                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTPS/WebSocket
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                      API GATEWAY LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastAPI Application (Uvicorn)                           │  │
│  │  - Route Registration                                    │  │
│  │  - Request Validation                                    │  │
│  │  - CORS & Rate Limiting                                  │  │
│  │  - Middleware (Audit, Auth, Error Handling)              │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    ┌────────┐  ┌──────────────┐  ┌──────────┐
    │ Routes │  │   Services   │  │ Utils    │
    ├────────┤  ├──────────────┤  ├──────────┤
    │/auth   │  │AI Service    │  │Security  │
    │/api    │  │Code Analyzer │  │Database  │
    │/admin  │  │Auth Service  │  │Audit     │
    │/health │  │User Service  │  │Sanitizer │
    └────────┘  └──────────────┘  └──────────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌───────────────┐ ┌──────────┐
│  Database    │ │   AI Models   │ │ External │
│   (MySQL)    │ │  - Groq       │ │ Services │
│              │ │  - Gemini     │ │          │
│ - Users      │ │  - Optional:  │ │ - Email  │
│ - Code       │ │    OpenAI     │ │ - Sentry │
│ - History    │ │    Claude     │ │ - Redis  │
│ - Analytics  │ │               │ │          │
└──────────────┘ └───────────────┘ └──────────┘
```

---

## Components

### 1. **Frontend Layer**
- **Technology**: HTML5, CSS3, Vanilla JavaScript
- **Key Files**:
  - `index.html` - Main application shell
  - `login.html` - Authentication interface
  - `dashboard.html` - Analytics dashboard
  - `styles.css` - Global styles
  - `main.js` - Core application logic

**Responsibilities**:
- User authentication
- Code input & display
- Real-time feedback rendering
- State management
- UI/UX interaction

### 2. **Backend API Layer**
- **Technology**: Python FastAPI + Uvicorn
- **Key Files**:
  - `main.py` - Application entry point & routes (1962 lines - needs refactoring)
  - `config.py` - Configuration management
  - `security.py` - JWT, encryption, sanitization
  - `ai_service.py` - AI model integration
  - `database.py` - Database operations
  - `dependencies.py` - FastAPI dependency injection
  - `audit.py` - Logging & audit trails

**API Endpoints**:
```
GET    /api/health              - Health check
POST   /api/auth/login          - User authentication
POST   /api/auth/logout         - Session termination
GET    /api/auth/me             - Current user info
POST   /api/code/review         - Code review analysis
POST   /api/code/refactor       - Auto-refactoring
GET    /api/history             - Code history
POST   /api/admin/users         - User management (Admin only)
GET    /api/admin/dashboard     - Analytics (Admin only)
```

### 3. **Database Layer**
- **Primary**: MySQL 8.0
- **Fallback**: In-memory storage for development

**Tables**:
```
┌─────────────────┐ ┌──────────────────┐ ┌──────────────┐
│     users       │ │  code_snippets   │ │   history    │
├─────────────────┤ ├──────────────────┤ ├──────────────┤
│ id (PK)         │ │ id (PK)          │ │ id (PK)      │
│ username        │ │ username (FK)    │ │ username(FK) │
│ password_hash   │ │ title            │ │ code         │
│ email           │ │ code             │ │ version      │
│ role            │ │ language         │ │ action       │
│ created_at      │ │ created_at       │ │ created_at   │
└─────────────────┘ └──────────────────┘ └──────────────┘

┌────────────────┐ ┌────────────────┐
│   analytics    │ │   audit_logs   │
├────────────────┤ ├────────────────┤
│ id (PK)        │ │ id (PK)        │
│ user_id (FK)   │ │ user_id (FK)   │
│ action         │ │ action         │
│ timestamp      │ │ details        │
│ metrics        │ │ timestamp      │
└────────────────┘ └────────────────┘
```

### 4. **AI Service Layer**
- **Primary Provider**: Groq (Llama 3.3 70B)
- **Secondary**: Google Gemini
- **Optional**: OpenAI, Anthropic Claude

**Capabilities**:
- Code analysis & review
- Refactoring suggestions
- Security vulnerability detection
- Test generation
- Documentation generation
- Plagiarism detection

### 5. **Security Layer**
Components:
- JWT token generation & validation
- Password hashing (bcrypt)
- Secret encryption (Fernet)
- CORS protection
- Rate limiting
- Input sanitization
- Audit logging

---

## Data Flow

### Authentication Flow
```
User Login Request
    ↓
[Validate Credentials]
    ↓
[Generate JWT Token]
    ↓
[Return Token to Client]
    ↓
[Store in LocalStorage]
    ↓
[Include in API Requests]
```

### Code Review Flow
```
User Submits Code
    ↓
[Validate Input & Authenticate]
    ↓
[Sanitize Code]
    ↓
[Send to AI Service]
    ↓
[AI Analysis (2-5 seconds)]
    ↓
[Store in Database]
    ↓
[Return Results to Client]
    ↓
[Display on UI]
```

### Dashboard Analytics Flow
```
User Requests Dashboard
    ↓
[Fetch User Analytics]
    ↓
[Aggregate Historical Data]
    ↓
[Calculate Metrics]
    ↓
[Format for Frontend]
    ↓
[Render Charts/Tables]
```

---

## Database Schema

### User Management
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',  -- user, teacher, admin
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Code Storage
```sql
CREATE TABLE code_snippets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    code LONGTEXT NOT NULL,
    language VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username)
);
```

### Audit Logging
```sql
CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    action VARCHAR(255),
    details JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## API Architecture

### Request/Response Format
```json
{
  "success": true,
  "data": {
    "id": 123,
    "username": "user",
    "email": "user@example.com"
  },
  "message": "Operation successful",
  "timestamp": "2026-02-19T10:30:00Z"
}
```

### Authentication Header
```
Authorization: Bearer <JWT_TOKEN>
```

### Error Responses
```json
{
  "success": false,
  "error": "Authentication failed",
  "code": 401,
  "details": "Invalid token"
}
```

---

## Deployment Architecture

### Docker Deployment
```
Docker Compose Network (172.20.0.0/16)
├── FastAPI App Container
│   ├── Port: 8000
│   └── Volume: Backend + Frontend code
├── MySQL Database Container
│   ├── Port: 3306 (localhost only)
│   └── Volume: mysql_data (persistent)
└── Optional: Redis Cache Container
    ├── Port: 6379
    └── Volume: redis_data
```

### Production Deployment Options

#### Option 1: Azure Container Apps
```
API Gateway (Application Gateway)
    ↓
Azure Container Apps (FastAPI)
    ↓
Azure Database for MySQL
```

#### Option 2: Kubernetes (AKS)
```
Ingress Controller
    ↓
Service (LoadBalancer type)
    ↓
Multiple Pods (App replicas)
    ↓
Persistent Volumes (MySQL, Logs)
```

#### Option 3: App Service
```
Azure App Service (FastAPI)
    ↓
Application Insights (Monitoring)
    ↓
Azure Database for MySQL
```

---

## Security Architecture

### Authentication & Authorization
```
┌─────────────────────────────────────┐
│   Request with JWT Token            │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   Validate Token Signature          │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   Check Token Expiration            │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   Extract User & Role from Token    │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   Verify Role for Endpoint          │
└──────────────┬──────────────────────┘
               ↓
         ✅ Allowed or ❌ Denied
```

### Data Protection
- **In Transit**: HTTPS/TLS encryption
- **At Rest**: MySQL encryption, secret encryption (Fernet)
- **In Database**: Password hashing (bcrypt) with salt rounds=12

### Rate Limiting
- Global: 100 requests/minute per IP
- Per endpoint: Custom limits (to be implemented)

### Input Validation
- Type checking via Pydantic models
- HTML sanitization (nh3 library)
- Length limits on uploads (5MB default)
- SQL injection prevention (parameterized queries)

---

## Performance Considerations

### Optimization Strategies
1. **Caching**: Redis integration (optional)
2. **Database Indexing**: Indexes on frequently queried columns
3. **Connection Pooling**: MySQL connection pool
4. **API Response Compression**: gzip middleware
5. **Code Splitting**: Frontend module splitting (future)
6. **CDN**: For static assets in production

### Expected Performance
- API Response Time: < 2 seconds
- Concurrent Users: 100+
- Database Query Time: < 500ms
- API Rate Limit: 100 req/min per IP

---

## Future Architecture Improvements

### Phase 2: Microservices
```
API Gateway (Kong/Nginx)
├── Auth Service
├── Code Analysis Service
├── Analytics Service
└── User Service
```

### Phase 3: Advanced Features
- GraphQL API alternative
- WebSocket real-time collaboration
- Message Queue (RabbitMQ/Kafka)
- Search Engine (Elasticsearch)
- ML Model Fine-tuning

---

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL/TLS certificates installed
- [ ] CORS origins whitelisted
- [ ] API keys secured in vault
- [ ] Database backups configured
- [ ] Monitoring & alerts enabled
- [ ] Rate limiting configured
- [ ] HTTPS enforced
- [ ] Admin user created

---

**Document Version**: 2.0.0
**Last Updated**: February 2026
