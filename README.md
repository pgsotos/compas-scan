# 🧭 CompasScan: Automated Competitive Intelligence

> **AI-Powered Serverless Solution** for Marketing Intelligence teams that need to identify competitors quickly without infrastructure costs.

**🌐 Language / Idioma:** **English** | [Español](README.es.md)

## 🌐 Environments

| Environment   | Status | URL                                                          | Branch    |
| ------------- | ------ | ------------------------------------------------------------ | --------- |
| **Production** | ✅     | [compas-scan.vercel.app](https://compas-scan.vercel.app)     | `main`    |
| **Staging**   | 🧪     | [compas-scan-staging.vercel.app](https://compas-scan-staging.vercel.app) | `staging` |
| **Development** | 🔧   | [compas-scan-dev.vercel.app](https://compas-scan-dev.vercel.app) | `develop` |

**API Documentation:**
- Production: [compas-scan.vercel.app/api/docs](https://compas-scan.vercel.app/api/docs)
- Staging: [compas-scan-staging.vercel.app/api/docs](https://compas-scan-staging.vercel.app/api/docs)
- Development: [compas-scan-dev.vercel.app/api/docs](https://compas-scan-dev.vercel.app/api/docs)

---

## 🎯 What is CompasScan?

CompasScan is an automated competitive intelligence tool that analyzes a brand or website and identifies its most relevant competitors using a **hybrid AI + Web Search approach**.

### Key Features

- 🤖 **AI-First Strategy**: Google Gemini 2.0 Flash as primary consultant
- 🌍 **Geo-Awareness**: TLD-based geographic detection (60+ countries)
- 🔍 **Smart Classification**: Distinguishes between:
  - **HDA (High Domain Availability)**: Global, direct competitors
  - **LDA (Low Domain Availability)**: Niche, emerging competitors
- ⚡ **Performance**: Redis caching (28x faster, 80% cost reduction)
- 📊 **Observability**: Logfire (tracing) + Sentry (error tracking)
- 🎨 **Modern UI**: Next.js frontend with Tailwind CSS

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone and configure
git clone <repo-url>
cd compas-scan
cp env.example .env
# Edit .env with your API keys (see docs/API_KEYS_GUIDE.md)

# 2. Start all services
make docker-up

# 3. Access
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

📖 **Full Docker guide:** [docs/DOCKER.md](docs/DOCKER.md)

### Option 2: Manual Setup

```bash
# Backend
python3 -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
uv pip install -r requirements.txt

# Frontend
bun install

# Configure environment
cp env.example .env
# Edit .env with your API keys

# Run tests
uv run python tests/test_local.py "Nike"
```

📖 **API Keys Setup:** [docs/API_KEYS_GUIDE.md](docs/API_KEYS_GUIDE.md)

---

## 🏗️ Architecture

### Tech Stack

**Backend:**
- Python 3.9+ with FastAPI
- Google Gemini 2.0 Flash (AI analysis)
- Brave Search API (primary) + Google Custom Search (fallback)
- Supabase (PostgreSQL)
- Redis (optional caching)
- Package manager: `uv`

**Frontend:**
- Next.js 16+ (App Router) with TypeScript
- Tailwind CSS
- Package manager: `bun`

**Infrastructure:**
- Vercel Serverless Functions
- Docker Compose (local development)

### Discovery Strategy

1. **AI Strategy (Primary)** 🌟
   - Gemini analyzes brand context and identifies competitors
   - Automatic classification (HDA/LDA)
   - Noise filtering (excludes news, forums, aggregators)

2. **Web Search Strategy (Fallback)** 🔍
   - Enhanced web search with signal-based classification
   - Direct competitor site discovery
   - Geo-targeted queries for local competitors

---

## 📁 Project Structure

```
compas-scan/
├── api/                    # Backend (Python/FastAPI)
│   ├── compas_core.py     # Main orchestrator
│   ├── gemini_service.py   # Gemini AI integration
│   ├── search_clients.py   # Brave + Google Search
│   ├── cache.py           # Redis caching layer
│   ├── models.py          # Pydantic models
│   ├── constants.py       # TLD mapping (60+ countries)
│   └── index.py           # FastAPI entrypoint
│
├── app/                    # Frontend (Next.js)
│   ├── page.tsx           # Main page
│   └── layout.tsx         # Global layout
│
├── components/             # React components
├── docs/                   # Documentation
├── tests/                  # Test suite
└── scripts/                # Utility scripts
```

---

## 🧪 Testing

```bash
# Local test with brand name or URL
uv run python tests/test_local.py "Nike"
uv run python tests/test_local.py "hubspot.com"
```

---

## 📚 Documentation

### **Core Documentation**
- **[AGENTS.md](AGENTS.md)** - Tool-agnostic architecture and development rules
- **[docs/](docs/)** - Technical documentation and guides

📖 **📚 [Full Documentation Index](docs/README.md)** - Complete guide to all technical documentation, organized by category, task, and role.

---

## 🛠️ Development

### Code Quality

```bash
make lint           # Run linter
make lint-fix       # Auto-fix linting issues
make format         # Format code
make check          # Run all checks (lint + format)
make test           # Run local tests
```

### Development Workflow

For complete development rules, architecture guidelines, and tool-agnostic workflows, see **[AGENTS.md](AGENTS.md)**.

Quick overview:
- `feature/*` → `develop` → `staging` → `main`
- All promotions require Pull Requests
- Tool-agnostic (works with any IDE/editor)

---

## 🛡️ Resilience

- **Circuit Breaker**: Automatic fallback from Gemini to web search
- **Graceful Degradation**: Works without Redis (caching optional)
- **Error Tracking**: Sentry integration for production monitoring

---

## 📊 Performance

- **Cache Hits**: ~100ms (28x faster than uncached)
- **Cost Reduction**: Up to 80% savings on API calls
- **Search Speed**: Brave Search ~320ms (62% faster than Google)

---

## 🤝 Contributing

1. Create a feature branch from `develop`
2. Make changes and test locally
3. Run `make check` before committing
4. Create PR to `develop`
5. Follow Conventional Commits format

---

## 📄 License

[Add your license here]

---

## 🔗 Links

- **Production**: https://compas-scan.vercel.app
- **API Docs**: https://compas-scan.vercel.app/api/docs
- **Documentation**: [docs/README.md](docs/README.md)

---

**Version:** 2.0.0 | **Status:** Production Ready
