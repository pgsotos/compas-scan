# 🤖 AGENTS.md: Tool-Agnostic Architecture

> **Purpose:** Replace `.cursorrules` with universal agent system that works across IDEs, editors, and tools.

---

## 🎯 **Core Principles**

### 1. **Tool Independence**
- **No tool-specific commands** (no `uv`, `bun`, `gh`)
- **Universal patterns** that work in any environment
- **IDE-agnostic** (works in VSCode, Cursor, JetBrains, etc.)

### 2. **Technology Stack**
- **Backend:** Python 3.9+ (any package manager)
- **Frontend:** Next.js + TypeScript (any package manager)
- **Database:** PostgreSQL (any provider)
- **Deployment:** Serverless (any platform)

---

## 🏗️ **Architecture Rules**

### **Backend Structure**
```
api/
├── core/           # Main orchestrator
├── ai/           # AI services (Gemini, OpenAI, etc.)
├── search/        # Search clients (Brave, Google, etc.)
└── cache/         # Caching layer (Redis, Memcached, etc.)
```

### **Frontend Structure**
```
app/
├── components/    # Reusable UI
├── lib/          # Utilities
└── styles/       # Tailwind, CSS-in-JS, etc.
```

---

## 🔄 **Workflow Rules**

### **Development Workflow**
1. **Branch Strategy:** `feature/*` → `develop` → `staging` → `main`
2. **Testing:** Unit + Integration + E2E
3. **Deployment:** CI/CD with environment promotion

### **Branch Management**
- **Protected Branches:** `main`, `staging`, `develop`
- **Working Branches:** `feature/*`, `refactor/*`, `fix/*`, `docs/*`
- **Integration Flow:** ALWAYS via Pull Request
- **Direct Merge:** FORBIDDEN to protected branches

### **Environment Promotion**
- **Development:** Auto-deploy on merge to `develop`
- **Staging:** Weekly releases from `develop`
- **Production:** Manual promotion from `staging`

### **Quality Gates**
- **Code Quality:** Lint + Format + Type Check
- **Test:** 80% coverage minimum
- **Security:** No secrets in code

---

## 🛡 **Security & Performance**

### **Security**
- **API Keys:** Environment variables only
- **Rate Limits:** 100 req/min per IP
- **CORS:** Specific domains
- **Input Validation:** Sanitize all inputs
- **Output Encoding:** Prevent XSS
- **Authentication:** JWT tokens
- **Authorization:** Role-based access

### **Performance**
- **Caching:** 5 min TTL
- **Timeout:** 30s max
- **Retry:** 3 attempts
- **Connection Pooling:** Reuse connections
- **Lazy Loading:** Load on demand
- **Compression:** Gzip responses

### **Cost Management**
- **API Budget:** $100/month max
- **Cache Hit Ratio:** >80% target
- **Request Optimization:** Batch when possible
- **Monitoring:** Cost alerts at 75% budget

---

## 🌍 **Environment Strategy**

### **Multi-Environment**
- **Development:** Local + Docker
- **Staging:** Pre-production
- **Production:** Global

### **Configuration**
- **Config Files:** `.env.example`
- **Secrets:** Environment variables
- **Settings:** Per-environment

---

## 📊 **Observability**

### **Monitoring**
- **Logs:** Structured JSON
- **Metrics:** Response time, error rate
- **Alerts:** 5% error threshold

### **Health**
- **Health Check:** `/health`
- **Readiness:** `/ready`
- **Liveness:** `/alive`

---

## 🚀 **Deployment**

### **Platform Agnostic**
- **Serverless:** Any provider
- **Docker:** Multi-stage builds
- **Frequency:** Weekly releases

### **CI/CD**
- **Pipeline:** Test → Build → Deploy
- **Rollback:** Automatic on failure

---

## 📝 **Documentation**

### **Universal**
- **README:** Project overview
- **API Docs:** OpenAPI/Swagger
- **Architecture:** System design

### **Language**
- **English:** Primary
- **Spanish:** Secondary

---

## 🎯 **Business Logic**

### **Core Function**
- **Input:** Brand name or URL
- **Process:** AI + Web Search
- **Output:** Competitor list

### **Classification**
- **HDA:** High Domain Availability
- **LDA:** Low Domain Availability
- **Geo:** TLD-based

---

## 🔧 **Testing**

### **Test Types**
- **Unit:** Individual functions
- **Integration:** API endpoints
- **E2E:** Full workflow

### **Coverage**
- **Backend:** 90% minimum
- **Frontend:** 80% minimum
- **E2E:** Critical paths

---

## 📦 **Dependencies**

### **Commands**
- **Backend:** `make check`
- **Frontend:** `npm test`
- **All:** `make test`

### **Updates**
- **Security:** Monthly
- **Dependencies:** Weekly
- **Platform:** As needed

---

## 🌐 **Global**

### **Multi-Region**
- **Primary:** US
- **Secondary:** EU
- **Tertiary:** Asia

### **Languages**
- **English:** Default
- **Spanish:** Supported

---

## 📈 **Scaling**

### **Load**
- **Requests:** 1000/min
- **Users:** 1000 concurrent
- **Storage:** 10GB

### **Limits**
- **API:** 100 req/min
- **Database:** 100 connections
- **Cache:** 1GB

### **Auto-Scaling**
- **Horizontal:** Add instances on load
- **Vertical:** Increase resources on demand
- **Database:** Read replicas for queries
- **CDN:** Global content distribution

### **Disaster Recovery**
- **Backups:** Daily automated
- **Regions:** Multi-region deployment
- **Failover:** Automatic switch
- **RTO:** 4 hours max
- **RPO:** 1 hour max

---

## 🛠 **Tools**

### **Universal**
- **Editor:** Any
- **Terminal:** Bash/Zsh
- **Browser:** Chrome/Firefox

### **Optional**
- **Docker:** Local dev
- **K8s:** Production
- **Monitoring:** Any

---

## 📋 **Checklist**

### **Before Commit**
- [ ] Tests pass
- [ ] Code formatted
- [ ] No secrets
- [ ] Documentation updated

### **Before Deploy**
- [ ] All tests pass
- [ ] Security scan
- [ ] Performance test
- [ ] Health check

---

## 🎯 **Success Metrics**

### **Technical**
- **Uptime:** 99.9%
- **Response:** <200ms
- **Coverage:** >80%

### **Business**
- **Accuracy:** 90%
- **Speed:** <5s
- **Cost:** <$0.01

---

## 🔄 **Version**

### **Semantic**
- **Major:** Breaking changes
- **Minor:** New features
- **Patch:** Bug fixes

### **Release**
- **Weekly:** Minor
- **Monthly:** Major
- **Daily:** Patch

---

## 📚 **Resources**

### **Documentation**
- **AGENTS.md:** This file
- **README:** Project overview
- **API:** OpenAPI

### **Support**
- **Issues:** GitHub
- **Discussions:** Community
- **Wiki:** Knowledge

---

## 🎯 **Next Steps**

### **Immediate**
1. **Setup:** Local environment
2. **Test:** All checks
3. **Deploy:** First release

### **Future**
1. **Scale:** Multi-region
2. **Optimize:** Performance
3. **Expand:** Features

---

## 📞 **Contact**

### **Team**
- **Lead:** Architecture
- **Dev:** Implementation
- **Ops:** Deployment

### **Channels**
- **Slack:** Development
- **Email:** Updates
- **GitHub:** Issues

---

## 📄 **License**

### **Open**
- **MIT:** Permissive
- **Apache:** Corporate
- **GPL:** Community

---

## 🎯 **Conclusion**

### **Summary**
- **Tool-agnostic:** Universal
- **Future-proof:** Scalable
- **Maintainable:** Clean

### **Action**
- **Start:** Now
- **Build:** Together
- **Deploy:** Confident

---

**Version:** 1.0.0 | **Status:** Tool-Agnostic | **Scope:** Universal