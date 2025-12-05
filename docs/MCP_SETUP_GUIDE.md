# 🔌 MCP Setup Guide - CompasScan

Quick setup guide for all Model Context Protocol (MCP) servers used in CompasScan.

---

## 📋 Available MCPs

1. **Context7 MCP** - Library documentation (✅ Already configured)
2. **Vercel MCP** - Deployment management and logs (⭐ Highly recommended)
3. **GitHub MCP** - Repository operations and PR management
4. **Memory MCP** - Context retention across sessions

---

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

Run the setup scripts in order:

```bash
# 1. Context7 MCP (if not already configured)
./scripts/setup-context7.sh

# 2. Vercel MCP (highly recommended for deployment management)
./scripts/setup-vercel-mcp.sh

# 3. GitHub MCP
./scripts/setup-github-mcp.sh

# 4. Memory MCP
./scripts/setup-memory-mcp.sh

# 5. Verify all MCPs
./scripts/check-mcp-status.sh
```

### Option 2: Manual Setup

Edit `~/.cursor/mcp.json` directly:

```json
{
  "mcpServers": {
    "context7": {
      "command": "bunx",
      "args": [
        "-y",
        "@upstash/context7-mcp",
        "--api-key",
        "ctx7sk-your-key"
      ]
    },
    "vercel": {
      "command": "bunx",
      "args": [
        "-y",
        "@vercel/mcp-server"
      ],
      "env": {
        "VERCEL_TOKEN": "your_vercel_token_here"
      }
    },
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token",
        "-e", "GITHUB_READ_ONLY=1",
        "ghcr.io/github/github-mcp-server"
      ]
    },
    "memory": {
      "command": "bunx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ]
    }
  }
}
```

---

## 🔧 Individual Setup Guides

### 1. Context7 MCP

**Purpose:** Up-to-date library documentation

**Setup:**
```bash
./scripts/setup-context7.sh
```

**Requirements:**
- Bun or Node.js (bunx/npx)
- Context7 API key (optional but recommended)
- Get key at: https://console.upstash.com/context7

**Documentation:** See `docs/CONTEXT7_SETUP.md`

---

### 2. Vercel MCP ⭐

**Purpose:** Deployment management, log analysis, project configuration

**Setup:**
```bash
./scripts/setup-vercel-mcp.sh
```

**Requirements:**
- Bun or Node.js (bunx/npx)
- Vercel token (required)
- Get token at: https://vercel.com/account/tokens
- Required scopes: `read`, `deployments:read`, `projects:read`

**Features:**
- Search Vercel documentation
- List projects and deployments
- Analyze deployment logs
- Manage domains and configurations
- Troubleshoot deployment issues

**Configuration:**
```json
{
  "mcpServers": {
    "vercel": {
      "command": "bunx",
      "args": [
        "-y",
        "@vercel/mcp-server"
      ],
      "env": {
        "VERCEL_TOKEN": "your_vercel_token"
      }
    }
  }
}
```

**Alternative: Remote HTTP Server**
If using Vercel's remote MCP server:
```json
{
  "mcpServers": {
    "vercel": {
      "url": "https://mcp.vercel.com",
      "transport": "http"
    }
  }
}
```

**Use Cases for CompasScan:**
- Monitor deployments across dev/staging/production
- Analyze deployment logs when issues occur
- Query project configuration and domains
- Get AI assistance for Vercel-specific issues

**Documentation:** https://vercel.com/docs/mcp/vercel-mcp

---

### 3. GitHub MCP

**Purpose:** Repository operations, PR creation, repository queries

**Setup:**
```bash
./scripts/setup-github-mcp.sh
```

**Requirements:**
- GitHub MCP binary OR Docker
- GitHub Personal Access Token (optional, recommended)
- Get token at: https://github.com/settings/tokens
- Required scopes: `repo` (read and write)

**Installation Options:**

**Option A: Binary (Recommended)**
1. Download from: https://github.com/github/github-mcp-server/releases
2. Extract and place in PATH (e.g., `~/.local/bin/`)
3. Make executable: `chmod +x github-mcp-server`

**Option B: Docker**
- Docker must be installed and running
- Script will use Docker automatically if binary not found

**Configuration:**
- **Read-only mode:** Recommended for safety (queries only)
- **Full access:** Allows PR creation (still respects `.cursorrules` merge restrictions)

**Usage Rules:**
- ✅ Can create PRs (automates Agent Protocol Step 7)
- ✅ Can query repository information
- ❌ Cannot merge PRs (must use `gh pr merge` CLI)
- See `.cursorrules` Section 2.2 for details

---

### 4. Memory MCP

**Purpose:** Context retention across sessions

**Setup:**
```bash
./scripts/setup-memory-mcp.sh
```

**Requirements:**
- Bun or Node.js (bunx/npx)
- No API keys needed

**Features:**
- Remembers previous conversations
- Stores project-specific knowledge
- Tracks architectural decisions
- Builds institutional knowledge over time

---

## ✅ Verification

After setup, verify all MCPs:

```bash
./scripts/check-mcp-status.sh
```

This will show:
- ✅ Configuration file status
- ✅ Package managers available
- ✅ Each MCP's configuration status
- ✅ API keys/tokens configured

---

## 🔄 Activation

**Important:** MCPs activate after restarting Cursor IDE completely.

1. Close Cursor completely (not just reload window)
2. Restart Cursor
3. MCPs should appear in available resources

---

## 🛠️ Troubleshooting

### MCPs Not Showing

**Problem:** MCPs don't appear after restart.

**Solutions:**
1. ✅ Verify `~/.cursor/mcp.json` exists and is valid JSON
2. ✅ Check package managers are available (`bunx` or `npx`)
3. ✅ For GitHub MCP: Verify binary/Docker is accessible
4. ✅ Run verification script: `./scripts/check-mcp-status.sh`
5. ✅ Restart Cursor completely (not just reload)

### GitHub MCP Issues

**Problem:** GitHub MCP not working.

**Solutions:**
1. ✅ Verify token format (starts with `ghp_`, `gho_`, or `ghu_`)
2. ✅ Check token has `repo` scope
3. ✅ Verify binary/Docker is accessible
4. ✅ Try read-only mode first

### Vercel MCP Issues

**Problem:** Vercel MCP not connecting.

**Solutions:**
1. ✅ Verify token format (should be a valid Vercel token)
2. ✅ Check token has required scopes (`read`, `deployments:read`, `projects:read`)
3. ✅ Verify package manager is available (`bunx` or `npx`)
4. ✅ For remote server: Check network connectivity to `https://mcp.vercel.com`
5. ✅ Restart Cursor after configuration

### Memory MCP Issues

**Problem:** Memory MCP not retaining context.

**Solutions:**
1. ✅ Verify package manager is available
2. ✅ Check `~/.cursor/mcp.json` configuration
3. ✅ Restart Cursor after configuration

---

## 📚 Additional Resources

- **MCP Recommendations:** `docs/MCP_RECOMMENDATIONS.md`
- **MCP Status:** `docs/MCP_STATUS.md`
- **GitHub MCP Compatibility:** `docs/GITHUB_MCP_COMPATIBILITY.md`
- **GitHub MCP Integration Analysis:** `docs/GITHUB_MCP_INTEGRATION_ANALYSIS.md`
- **Context7 Setup:** `docs/CONTEXT7_SETUP.md`

---

## 📝 Notes

- **MCPs are IDE tools** - They help AI assistants, not runtime code
- **Configuration is global** - MCPs configured in `~/.cursor/mcp.json`
- **Restart required** - Cursor IDE must restart after MCP changes
- **Gitflow compliance** - All MCPs respect `.cursorrules` Gitflow requirements

---

**Last Updated:** 2024-12-04  
**Status:** ✅ Setup scripts ready for all recommended MCPs

