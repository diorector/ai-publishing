# SPEC-001: Development Environment Initialization

**Version**: 0.25.7
**Status**: READY FOR IMPLEMENTATION
**Phase**: Phase 0 (Project Setup)
**Created**: 2025-11-16
**Language**: English (Conversation: 한국어)
**Owner**: @user

---

## 📋 Specification Summary

This SPEC defines the complete development environment setup for AI-Publishing, including directory structure, configuration files, dependency management, and local development workflow.

---

## 🎯 UBIQUITOUS Requirements (Always True)

> The system SHALL maintain project structure as defined in `.moai/STRUCTURE.md`
> The system SHALL document all environment variables in `.env.example` files
> The system SHALL provide Docker containers for all service components
> The system SHALL use monorepo structure with separate frontend/backend versioning

---

## 📁 EVENT-DRIVEN Requirements

### WHEN developer runs initial setup command
```
GIVEN fresh repository clone
WHEN developer runs: npm install && pip install
THEN the system SHALL:
  ✅ Install all Node.js dependencies (frontend)
  ✅ Install all Python packages in virtual environment (backend)
  ✅ Create local `.env` files from `.env.example` templates
  ✅ Initialize database schemas (if applicable)
  ✅ Validate all required tools are installed
```

### WHEN developer runs tests
```
GIVEN initialized development environment
WHEN developer runs: npm test (frontend) or pytest (backend)
THEN the system SHALL:
  ✅ Execute all unit tests
  ✅ Execute all integration tests
  ✅ Generate coverage reports
  ✅ Display coverage summary with % coverage
  ✅ Exit with status 0 if coverage >= 85%, else status 1
```

### WHEN developer starts development servers
```
GIVEN npm dependencies installed and pip packages installed
WHEN developer runs: npm run dev (frontend) and python -m uvicorn app:app --reload (backend)
THEN the system SHALL:
  ✅ Frontend server available at http://localhost:3000
  ✅ Backend API available at http://localhost:8000
  ✅ Hot reload enabled for both services
  ✅ Development tools (Redux DevTools, FastAPI docs) accessible
  ✅ Console logs show no critical errors
```

### WHEN developer pushes code changes
```
GIVEN code changes committed locally
WHEN developer runs: git push origin [branch]
THEN the system SHALL:
  ✅ Run pre-commit hooks (linting, formatting)
  ✅ Validate code against type checker (TypeScript, mypy)
  ✅ Block push if validation fails
  ✅ Provide clear error messages for fixes needed
```

---

## 🚫 UNWANTED BEHAVIOR (Prevention Requirements)

### IF dependency versions are incompatible
```
THEN the system SHALL:
  ✅ Provide clear error message during npm/pip install
  ✅ Lock exact versions in package-lock.json and requirements.txt
  ✅ Block outdated dependency installations
  ✅ Provide upgrade guidance for major version bumps
```

### IF environment variables are missing
```
THEN the system SHALL:
  ✅ Fail fast with clear message listing missing variables
  ✅ Provide example values in `.env.example`
  ✅ Include documentation for each variable
  ✅ Prevent application startup with incomplete configuration
```

### IF test coverage drops below 85%
```
THEN the system SHALL:
  ✅ Display warning with specific files below coverage threshold
  ✅ Prevent git commit with pre-commit hook
  ✅ Provide guidance for adding tests
  ✅ Track coverage trends in CI/CD
```

---

## 🏗️ Project Directory Structure

```
ai-publishing/
├── .moai/                          # MoAI-ADK configuration
│   ├── config/
│   │   ├── config.json             # ✅ UPDATED: Framework + user config
│   │   └── statusline-config.yaml
│   ├── specs/
│   │   ├── SPEC-000-baseline.md    # ✅ CREATED: Baseline requirements
│   │   ├── SPEC-001-initialization.md
│   │   └── README.md               # SPEC guidelines
│   ├── learning/
│   │   └── README.md               # Learning materials index
│   ├── memory/
│   │   ├── project-notes.json
│   │   ├── session-hint.json
│   │   └── user-patterns.json
│   ├── cache/
│   └── scripts/
│
├── src/
│   ├── frontend/                   # Next.js application
│   │   ├── app/                    # Next.js App Router
│   │   │   ├── page.tsx
│   │   │   └── layout.tsx
│   │   ├── components/             # React components
│   │   │   ├── Header.tsx
│   │   │   ├── Navigation.tsx
│   │   │   └── Footer.tsx
│   │   ├── hooks/                  # Custom React hooks
│   │   ├── lib/                    # Utilities
│   │   ├── styles/                 # Global styles
│   │   ├── types/                  # TypeScript type definitions
│   │   ├── __tests__/              # Jest tests
│   │   ├── package.json            # ✅ NEEDS CREATION
│   │   ├── tsconfig.json           # TypeScript config
│   │   ├── next.config.js          # Next.js config
│   │   ├── .env.example            # Environment template
│   │   └── .env.local              # (gitignored)
│   │
│   └── backend/                    # FastAPI application
│       ├── app.py                  # Main application
│       ├── config.py               # Configuration
│       ├── models.py               # Database models (SQLAlchemy)
│       ├── schemas.py              # Pydantic schemas
│       ├── routers/                # API route handlers
│       │   ├── auth.py
│       │   ├── content.py
│       │   └── users.py
│       ├── services/               # Business logic
│       │   ├── auth_service.py
│       │   ├── content_service.py
│       │   └── ml_service.py       # ML integration
│       ├── ml/                     # PyTorch models
│       │   ├── models.py
│       │   └── inference.py
│       ├── tests/                  # pytest tests
│       │   ├── test_auth.py
│       │   ├── test_api.py
│       │   └── conftest.py         # pytest fixtures
│       ├── pyproject.toml          # ✅ NEEDS CREATION
│       ├── requirements.txt        # ✅ NEEDS CREATION
│       ├── requirements-dev.txt    # Development dependencies
│       ├── .env.example            # Environment template
│       └── .env                    # (gitignored)
│
├── docs/
│   ├── API.md                      # API reference (auto-generated)
│   ├── ARCHITECTURE.md             # Architecture overview
│   ├── DEVELOPMENT.md              # Development guide
│   ├── DEPLOYMENT.md               # Deployment instructions
│   ├── api/                        # OpenAPI specs
│   └── architecture/               # Architecture diagrams
│
├── .github/
│   ├── workflows/                  # CI/CD pipelines
│   │   ├── test.yml                # Testing pipeline
│   │   ├── coverage.yml            # Coverage tracking
│   │   └── deploy.yml              # Deployment pipeline
│   └── ISSUE_TEMPLATE/
│
├── .claude/                        # Claude Code configuration
│   ├── settings.json
│   ├── hooks/
│   └── commands/
│
├── .mcp.json                       # Model Context Protocol config
├── .gitignore                      # ✅ VERIFIED
├── CLAUDE.md                       # Project conventions (existing)
├── README.md                       # ✅ NEEDS CREATION: Project overview
├── docker-compose.yml              # ✅ NEEDS CREATION
├── package.json                    # Monorepo root
└── Makefile                        # ✅ OPTIONAL: Common commands
```

---

## 📦 Dependency Specifications

### Frontend Dependencies (Next.js)

**Core Framework**:
- `next@latest` - Next.js 16+
- `react@latest` - React 19+
- `react-dom@latest` - React DOM

**Type Safety & Validation**:
- `typescript@latest` - TypeScript 5.x
- `zod` - Type-safe schema validation
- `@hookform/resolvers` - Form validation

**State Management**:
- `@tanstack/react-query@latest` - Server state management
- `zustand` or `@reduxjs/toolkit` - Client state management

**UI & Styling**:
- `tailwindcss` - Utility-first CSS
- `next-themes` - Dark mode support
- `radix-ui` - Accessible component library

**API & HTTP**:
- `axios` or `fetch` - HTTP client
- `swr` - Stale-while-revalidate caching

**Development Dependencies**:
```json
{
  "devDependencies": {
    "@types/node": "latest",
    "@types/react": "latest",
    "@typescript-eslint/eslint-plugin": "latest",
    "eslint": "latest",
    "eslint-config-next": "latest",
    "prettier": "latest",
    "jest": "latest",
    "jest-environment-jsdom": "latest",
    "@testing-library/react": "latest",
    "@testing-library/jest-dom": "latest",
    "ts-node": "latest"
  }
}
```

### Backend Dependencies (FastAPI)

**Core Framework**:
- `fastapi==0.100.0` - Web framework
- `uvicorn[standard]==0.24.0` - ASGI server
- `python-multipart==0.0.6` - Form handling

**Database & ORM**:
- `sqlalchemy==2.0.23` - ORM
- `psycopg2-binary==2.9.9` - PostgreSQL driver
- `alembic==1.13.0` - Database migrations

**Authentication & Security**:
- `python-jose[cryptography]==3.3.0` - JWT tokens
- `passlib[bcrypt]==1.7.4` - Password hashing
- `python-dotenv==1.0.0` - Environment variables
- `pydantic==2.5.0` - Data validation

**ML & Scientific Computing**:
- `torch==2.1.0` - PyTorch
- `torchvision==0.16.0` - Computer vision
- `transformers==4.35.0` - NLP models
- `numpy==1.26.0` - Numerical computing
- `scikit-learn==1.3.2` - ML utilities

**API Documentation**:
- `swagger-ui-py` - Auto-generated API docs

**Development Dependencies**:
```
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.12.0
flake8==6.1.0
mypy==1.7.0
isort==5.13.2
```

---

## 🧪 Test Structure Requirements

### Frontend Tests (Jest)
```typescript
// Example: __tests__/components/Header.test.tsx
import { render, screen } from '@testing-library/react';
import Header from '@/components/Header';

describe('Header Component', () => {
  it('should render navigation links', () => {
    render(<Header />);
    expect(screen.getByRole('link', { name: /home/i })).toBeInTheDocument();
  });
});
```

### Backend Tests (pytest)
```python
# Example: tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_login_success():
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "securepassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

---

## ⚙️ Configuration Files

### `.env.example` (Frontend)
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1

# Analytics (Optional)
NEXT_PUBLIC_GA_ID=

# Feature Flags
NEXT_PUBLIC_ENABLE_BETA_FEATURES=false
```

### `.env.example` (Backend)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai_publishing

# JWT Configuration
SECRET_KEY=your-secret-key-here-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ML Configuration
ML_MODEL_PATH=/app/models
PYTORCH_DEVICE=cuda  # or cpu

# API Configuration
API_VERSION=v1
LOG_LEVEL=INFO
```

---

## ✅ Acceptance Criteria

### When this SPEC is complete:
- ✅ All directories created and verified
- ✅ All configuration files present and validated
- ✅ All dependencies installable without errors
- ✅ Development servers start successfully
- ✅ All tests pass with 85%+ coverage
- ✅ Pre-commit hooks working (linting, formatting)
- ✅ Documentation complete and accurate

### Test Scenarios
1. **Fresh Install**: `npm install && pip install` completes without errors
2. **Development Startup**: Both frontend and backend servers start without errors
3. **Test Suite**: `npm test` and `pytest` both pass with 85%+ coverage
4. **Code Quality**: ESLint, TypeScript, mypy all pass without errors
5. **Pre-commit**: Git commit is blocked if any check fails
6. **Environment**: Application fails gracefully if required env vars missing

---

## 🔗 Related Documents

- `SPEC-000-baseline.md` - Baseline requirements
- `.moai/config/config.json` - Project configuration
- `README.md` - User-facing project overview
- `CLAUDE.md` - Development philosophy

---

## 📝 Implementation Notes

**Phase**: Phase 0 (Setup)
**Status**: READY FOR IMPLEMENTATION
**Estimated Duration**: 2-3 hours for complete setup
**Dependencies**: SPEC-000-baseline.md

**Next Steps**:
1. Create all directories and configuration files
2. Install frontend dependencies (npm install)
3. Install backend dependencies (pip install)
4. Verify all development tools work
5. Run test suites and verify 85%+ coverage
6. Commit to repository

---

**Last Updated**: 2025-11-16 00:21
**Implementation Ready**: Yes ✅
**Next SPEC**: SPEC-002 (Authentication System) - Phase 1
