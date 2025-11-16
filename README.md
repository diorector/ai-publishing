# AI-Publishing

> **AI-powered publishing platform with ML-driven content generation and distribution**

🚀 Modern web + intelligent ML | 📦 Production-ready architecture | 🎯 SPEC-First TDD development

---

## 🎯 Project Vision

AI-Publishing combines modern web technologies with machine learning to help creators:
- **Generate** high-quality content with AI assistance
- **Publish** across multiple channels seamlessly
- **Analyze** performance with intelligent insights
- **Optimize** distribution based on audience data

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (Next.js)                     │
│           React 19 + TypeScript + Tailwind CSS          │
│          Running on: http://localhost:3000              │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────┐
│                   Backend (FastAPI)                      │
│        Python 3.11+ | Async | SQLAlchemy ORM            │
│          Running on: http://localhost:8000              │
└────────────────────┬────────────────────────────────────┘
                     │ Database / Cache
┌────────────────────▼────────────────────────────────────┐
│              Storage & Intelligence                      │
│  PostgreSQL | Redis Cache | PyTorch ML Models          │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Frontend** | Next.js | 16+ |
| **Frontend Language** | TypeScript | 5.x |
| **Backend** | FastAPI | 0.100+ |
| **Backend Language** | Python | 3.11+ |
| **ML Framework** | PyTorch | 2.0+ |
| **Database** | PostgreSQL | 15+ |
| **Cache** | Redis | 7.0+ |
| **Deployment** | Railway + Vercel | - |

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ (for frontend)
- **Python** 3.11+ with `venv` (for backend)
- **PostgreSQL** 15+ (or Railway preview)
- **Git** (for version control)

### Development Setup

**1. Clone and Setup**
```bash
# Clone the repository
git clone <repo-url>
cd ai-publishing

# Install frontend dependencies
cd src/frontend && npm install && cd ../..

# Create Python virtual environment and install backend
cd src/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cd ../..
```

**2. Configure Environment**
```bash
# Frontend configuration
cp src/frontend/.env.example src/frontend/.env.local
# Edit src/frontend/.env.local with your values

# Backend configuration
cp src/backend/.env.example src/backend/.env
# Edit src/backend/.env with your values
```

**3. Start Development Servers**
```bash
# Terminal 1: Frontend
cd src/frontend && npm run dev
# Frontend: http://localhost:3000

# Terminal 2: Backend
cd src/backend
source venv/bin/activate
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**4. Run Tests**
```bash
# Frontend tests
cd src/frontend && npm test

# Backend tests
cd src/backend && pytest --cov
```

---

## 📋 Project Structure

```
ai-publishing/
├── .moai/                          # MoAI-ADK configuration
│   ├── config/config.json          # Project metadata
│   ├── specs/                      # SPEC documents (EARS format)
│   │   ├── SPEC-000-baseline.md
│   │   ├── SPEC-001-initialization.md
│   │   └── README.md
│   └── learning/                   # Learning materials
│
├── src/
│   ├── frontend/                   # Next.js application
│   │   ├── app/                    # App Router pages
│   │   ├── components/             # React components
│   │   ├── hooks/                  # Custom hooks
│   │   ├── lib/                    # Utilities
│   │   ├── __tests__/              # Jest tests
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   └── backend/                    # FastAPI application
│       ├── app.py                  # Main app entry
│       ├── routers/                # API routes
│       ├── models.py               # Database models
│       ├── schemas.py              # Pydantic schemas
│       ├── services/               # Business logic
│       ├── ml/                     # ML models & inference
│       ├── tests/                  # pytest tests
│       ├── pyproject.toml
│       └── requirements.txt
│
├── docs/                           # Project documentation
│   ├── API.md                      # API reference
│   ├── ARCHITECTURE.md             # Architecture guide
│   ├── DEVELOPMENT.md              # Developer guide
│   └── DEPLOYMENT.md               # Deployment guide
│
├── .github/workflows/              # CI/CD pipelines
│   ├── test.yml
│   ├── coverage.yml
│   └── deploy.yml
│
├── CLAUDE.md                       # Development conventions
├── .mcp.json                       # Model Context Protocol config
└── README.md                       # This file
```

---

## 🧪 Testing & Quality

### Code Quality Standards
- **Test Coverage**: Minimum 85% (enforced)
- **Type Safety**: TypeScript strict mode + Python type hints
- **Linting**: ESLint (frontend) + Ruff (backend)
- **Formatting**: Prettier (frontend) + Black (backend)

### Running Tests
```bash
# Frontend: Run Jest tests with coverage
cd src/frontend && npm test -- --coverage

# Backend: Run pytest with coverage
cd src/backend && pytest --cov --cov-report=html

# All tests
npm run test:all
```

### Coverage Reporting
```bash
# Frontend coverage (located in src/frontend/coverage/)
open src/frontend/coverage/lcov-report/index.html

# Backend coverage (located in src/backend/htmlcov/)
open src/backend/htmlcov/index.html
```

---

## 📚 Documentation

### Getting Started
- **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Setup guide and workflows
- **[API.md](docs/API.md)** - REST API reference (auto-generated)
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design overview

### Specifications
- **[SPEC-000: Baseline](\.moai\specs\SPEC-000-baseline.md)** - Project-wide requirements
- **[SPEC-001: Initialization](\.moai\specs\SPEC-001-initialization.md)** - Setup requirements
- **[All SPECs](.moai/specs/README.md)** - Complete SPEC index

### Learning Resources
- **[SPEC-First Philosophy](.moai/learning/)** - Why SPEC-First prevents bugs
- **[TDD Workflow](.moai/learning/)** - Red-Green-Refactor cycle
- **[CLAUDE.md](CLAUDE.md)** - Project conventions (Korean)

---

## 🔐 Security

### Built-in Protections
- ✅ JWT authentication with token rotation
- ✅ Password hashing (bcrypt)
- ✅ CORS configuration
- ✅ Input validation (Pydantic + Zod)
- ✅ SQL injection prevention (parameterized queries)
- ✅ XSS prevention (React sanitization + CSP headers)
- ✅ CSRF protection (SameSite cookies)

### Environment Variables
All sensitive data must be in environment files (never hardcoded):
```bash
# Backend
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
JWT_ALGORITHM=HS256

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🚀 Deployment

### Deployment Targets
- **Frontend**: Vercel (optimized for Next.js)
- **Backend**: Railway.app (Python/FastAPI optimized)
- **Database**: Railway PostgreSQL or managed service

### Deploy to Production
```bash
# Frontend to Vercel
cd src/frontend && npm run build && vercel --prod

# Backend to Railway
cd src/backend && railway up

# Or use GitHub Actions for automated CI/CD
# See .github/workflows/deploy.yml
```

### Environment Management
```bash
# Development
.env.example → .env.local (frontend) or .env (backend)

# Staging
Set environment variables in Railway preview

# Production
Set secrets in Vercel / Railway dashboards
```

---

## 📊 Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| **Lighthouse** | > 90 | 🟡 In Progress |
| **API P95** | < 200ms | 🟡 In Progress |
| **Test Coverage** | > 85% | 🟡 In Progress |
| **Type Safety** | 100% | 🟡 In Progress |

---

## 🎓 Development Workflow

### Using SPEC-First TDD

1. **Create SPEC** (Clear requirements)
   ```bash
   /alfred:1-plan "feature description"
   ```

2. **Write Tests** (RED phase)
   - Tests fail initially
   - Each test validates one requirement

3. **Implement** (GREEN phase)
   - Minimal code to pass tests
   - No premature optimization

4. **Refactor** (REFACTOR phase)
   - Improve code quality
   - Tests still pass

5. **Document** (Auto-sync)
   - Documentation auto-generated
   - No manual documentation needed

### Commit Message Format

```
Type: Brief description

Body with context and reasoning
- Bullet point 1
- Bullet point 2

SPEC-XXX: Link to specification
```

**Types**: feat, fix, refactor, test, docs, perf, chore

---

## 🤝 Contributing

### Branch Strategy
```bash
# Create feature branch from main
git checkout -b feature/feature-name

# Work on your feature (TDD workflow)
# 1. Write tests (RED)
# 2. Implement code (GREEN)
# 3. Refactor (REFACTOR)

# Push and create PR
git push origin feature/feature-name
```

### Code Review Process
1. All PRs require code review
2. Tests must pass (85%+ coverage)
3. Type checks must pass
4. Linting must pass
5. At least 1 approval required

### Quality Gates
```bash
# Pre-commit checks (automatic)
npm run lint        # ESLint + Prettier
npm run type-check  # TypeScript + mypy
npm test           # Unit tests

# All must pass before commit is allowed
```

---

## 🐛 Troubleshooting

### Frontend Issues
```bash
# Port 3000 already in use
npm run dev -- -p 3001

# Module not found errors
rm -rf node_modules && npm install

# Type errors
npm run type-check
```

### Backend Issues
```bash
# Python virtual environment issues
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

# Database connection errors
# Check DATABASE_URL in .env

# Port 8000 already in use
python -m uvicorn app:app --port 8001
```

### Common Solutions
```bash
# Clear cache and reinstall
npm run clean-install

# Reset database
python -m alembic downgrade base
python -m alembic upgrade head

# View API documentation
# Frontend: http://localhost:3000/api/docs
# Backend: http://localhost:8000/docs
```

---

## 📞 Support & Resources

### Project Info
- **Owner**: @user
- **Language**: Korean 🇰🇷 / English 🇬🇧
- **Deployment**: Railway + Vercel
- **Status**: 🟡 In Development

### Related Links
- **Configuration**: [.moai/config/config.json](.moai/config/config.json)
- **Conventions**: [CLAUDE.md](CLAUDE.md)
- **Specifications**: [.moai/specs/README.md](.moai/specs/README.md)
- **Learning Materials**: [.moai/learning/](./moai/learning/)

### Getting Help
1. Check the [Development Guide](docs/DEVELOPMENT.md)
2. Review relevant [SPEC documents](.moai/specs/)
3. Search existing [GitHub Issues](../../issues)
4. Check [Troubleshooting](#-troubleshooting) section

---

## 📜 License

This project is part of the MoAI-ADK (MoAI Agentic Development Kit) ecosystem.

---

## 🎉 Next Steps

**Ready to develop?**

1. ✅ **Clone & Setup** → Run quick start commands
2. ✅ **Read SPEC-000** → Understand architecture
3. ✅ **Start Dev Servers** → Frontend + Backend
4. ✅ **Run Tests** → Verify setup
5. 🚀 **Create Feature** → Use `/alfred:1-plan`

**Want to learn SPEC-First TDD?**
→ See [.moai/learning/](./moai/learning/) for tutorials and examples

---

**Last Updated**: 2025-11-16
**Status**: Ready for Development ✅
**Phase**: Phase 0 (Initialization Complete)
**Next**: Phase 1 - Core Features
