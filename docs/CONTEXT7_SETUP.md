# 🔌 Context7 MCP Setup Guide

Context7 MCP provides access to up-to-date documentation for libraries and frameworks directly in Cursor IDE.

## 🎯 What is Context7 MCP?

Context7 is a Model Context Protocol (MCP) server that gives AI assistants access to current library documentation, code examples, and best practices. This is especially useful for:

- Getting up-to-date API documentation
- Finding code examples for libraries
- Understanding best practices
- Resolving library-specific questions

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
./scripts/setup-context7.sh
```

This script will:
1. Check for existing configuration
2. Prompt for Context7 API key (optional)
3. Detect package manager (bunx or npx)
4. Create/update `~/.cursor/mcp.json`

### Option 2: Manual Setup

1. **Get Context7 API Key** (optional but recommended):
   - Visit: https://console.upstash.com/context7
   - Sign up/login
   - Create an API key (starts with `ctx7sk`)

2. **Create MCP Configuration**:
   ```bash
   mkdir -p ~/.cursor
   ```

3. **Create `~/.cursor/mcp.json`**:
   
   **With API Key:**
   ```json
   {
     "mcpServers": {
       "context7": {
         "command": "bunx",
         "args": [
           "-y",
           "@upstash/context7-mcp",
           "--api-key",
           "ctx7sk-your-api-key-here"
         ]
       }
     }
   }
   ```
   
   **Without API Key** (limited functionality):
   ```json
   {
     "mcpServers": {
       "context7": {
         "command": "bunx",
         "args": [
           "-y",
           "@upstash/context7-mcp"
         ]
       }
     }
   }
   ```

4. **Restart Cursor IDE** completely

5. **Verify Setup**:
   ```bash
   ./scripts/check-mcp-status.sh
   ```

## 🔍 Verifying MCP Status

Run the verification script:

```bash
./scripts/check-mcp-status.sh
```

This will show:
- ✅ Configuration file status
- ✅ Package manager availability
- ✅ Context7 API key status
- 📝 Next steps

## 🔄 Updating API Key

If you need to update your Context7 API key:

```bash
./scripts/update-context7-key.sh <your-api-key>
```

Or manually edit `~/.cursor/mcp.json` and restart Cursor.

## 📚 Using Context7 in Cursor

Once configured and Cursor is restarted, you can:

1. **Ask for library documentation**:
   - "Show me React hooks documentation"
   - "Get FastAPI examples for async endpoints"
   - "What's the latest Next.js routing pattern?"

2. **The AI will automatically use Context7** when:
   - You ask about libraries/frameworks
   - You need up-to-date code examples
   - You want best practices for a specific library

## 🛠️ Troubleshooting

### MCP Resources Not Showing

**Problem:** `list_mcp_resources` returns empty or Context7 doesn't work.

**Solutions:**
1. ✅ Restart Cursor IDE completely (not just reload window)
2. ✅ Verify `~/.cursor/mcp.json` exists and is valid JSON
3. ✅ Check package manager is available (`bunx` or `npx`)
4. ✅ Run verification script: `./scripts/check-mcp-status.sh`

### API Key Issues

**Problem:** Getting rate-limited or errors.

**Solutions:**
1. ✅ Verify API key format (must start with `ctx7sk`)
2. ✅ Check API key is valid in Context7 console
3. ✅ Update API key: `./scripts/update-context7-key.sh <key>`
4. ✅ Restart Cursor after updating

### Package Manager Not Found

**Problem:** Script can't find `bunx` or `npx`.

**Solutions:**
1. ✅ Install Bun: `curl -fsSL https://bun.sh/install | bash`
2. ✅ Or install Node.js: https://nodejs.org/
3. ✅ Verify: `which bunx` or `which npx`
4. ✅ Re-run setup script

## 📖 Available MCPs in CompasScan

### 1. Context7 MCP ✅
- **Purpose:** Library documentation and code examples
- **Status:** Configured and working
- **Config:** `~/.cursor/mcp.json`

### 2. Browser MCP ✅
- **Purpose:** Web navigation and interaction
- **Status:** Built-in to Cursor IDE
- **Tools:** `browser_navigate`, `browser_snapshot`, `browser_click`, etc.

### 3. Runtime Clients (Not MCPs)
- **Location:** `api/search_clients.py`, `api/db.py`
- **Note:** These are runtime Python clients, not MCP servers
- **Purpose:** Direct HTTP API calls for production use

## 🔗 Resources

- **Context7 Console:** https://console.upstash.com/context7
- **Context7 MCP Package:** https://www.npmjs.com/package/@upstash/context7-mcp
- **MCP Documentation:** https://modelcontextprotocol.io/

## 📝 Notes

- MCPs are **IDE tools** for Cursor agents, not runtime services
- For production, we use direct HTTP API calls (see `api/search_clients.py`)
- Context7 MCP is optional but highly recommended for development
- API key is optional but provides better rate limits

---

**Last updated:** 2024-12-04  
**Status:** ✅ Configured and Working

