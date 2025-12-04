# 🔄 IDE Compatibility

Analysis and guide for using CompasScan with MCP-compatible IDEs (Cursor, Claude Code, etc.).

---

## 📊 Current State

### ✅ IDE-Agnostic Components

- **Code:** All Python/TypeScript code works in both IDEs
- **Dependencies:** Same `requirements.txt` and `package.json`
- **Configuration:** `.env` files work identically
- **Gitflow:** Works the same in both IDEs
- **Docker:** Same setup for both

### ⚠️ IDE-Specific Components

1. **MCP Configuration:**
   - **Cursor:** `~/.cursor/mcp.json`
   - **Claude Code:** `~/.claude-code/mcp.json` (assumed, verify)

2. **Project Rules:**
   - **Cursor:** `.cursorrules` (read automatically)
   - **Claude Code:** May use different file or location

3. **Scripts:**
   - All scripts currently hardcode `~/.cursor/mcp.json`
   - Need to detect IDE and use correct path

4. **Documentation:**
   - Many references to "Cursor" specifically
   - Should mention both IDEs

---

## 🔍 Compatibility Checklist

### ✅ Works in Both

- [x] Code execution (Python, TypeScript)
- [x] Package management (`uv`, `bun`)
- [x] Git operations
- [x] Docker setup
- [x] Environment variables
- [x] Testing (`tests/test_local.py`)

### ⚠️ Needs Adaptation

- [ ] MCP configuration path detection
- [ ] Scripts to detect IDE automatically
- [ ] Documentation updates
- [ ] `.cursorrules` compatibility (or alternative)

### ❌ Cursor-Specific

- [ ] `.cursorrules` file (Cursor-specific, but can be kept)
- [ ] MCP setup scripts (hardcoded to Cursor paths)

---

## 🛠️ Required Changes

### 1. Update Scripts to Use Generic IDE Paths

**Current:**
```bash
CURSOR_MCP_FILE="$HOME/.cursor/mcp.json"
```

**Updated:**
```bash
# Source IDE detection utility (automatically finds MCP config path)
source "$SCRIPT_DIR/detect-ide.sh"
MCP_CONFIG_FILE=$(get_mcp_config_path)
```

Scripts now use generic "IDE" terminology and automatically detect the correct MCP config path.

### 2. Update Documentation

Replace IDE-specific references with generic "IDE" terminology where appropriate.

### 3. IDE Detection Utility

Created `scripts/detect-ide.sh` that automatically detects MCP config path:

```bash
# Automatically finds MCP config path for any compatible IDE
get_mcp_config_path() {
    if [ -d "$HOME/.cursor" ]; then
        echo "$HOME/.cursor/mcp.json"
    elif [ -d "$HOME/.claude-code" ]; then
        echo "$HOME/.claude-code/mcp.json"
    else
        echo "$HOME/.cursor/mcp.json"  # Default
    fi
}
```

All scripts now use generic "IDE" terminology instead of IDE-specific names.

### 4. `.cursorrules` Compatibility

**Option A:** Keep `.cursorrules` (Cursor will use it, Claude Code will ignore)
**Option B:** Create IDE-agnostic `.ide-rules` or similar
**Option C:** Document that `.cursorrules` is Cursor-specific but safe to keep

**Recommendation:** Option C - Keep `.cursorrules` as it's harmless if Claude Code doesn't use it.

---

## 📝 Migration Steps

### For Users Switching IDEs

1. **Copy MCP Configuration:**
   ```bash
   # Copy MCP config between IDE directories
   cp ~/.cursor/mcp.json ~/.claude-code/mcp.json
   # Or vice versa
   ```

2. **Use Scripts:**
   - Scripts automatically detect the correct MCP config path
   - No manual path updates needed
   - Works with any MCP-compatible IDE

3. **Verify:**
   - Check MCP status: `./scripts/check-mcp-status.sh`
   - Test MCP functionality in your IDE

---

## 🎯 Implementation Plan

### Phase 1: Script Updates (High Priority)

1. Create `scripts/detect-ide.sh` utility
2. Update all MCP setup scripts to use IDE detection
3. Update `check-mcp-status.sh` to detect IDE

### Phase 2: Documentation (Medium Priority)

1. Update README to mention both IDEs
2. Update MCP setup guides for both IDEs
3. Add IDE switching guide

### Phase 3: Testing (Low Priority)

1. Test scripts in both IDEs
2. Verify MCP configuration works in both
3. Document any IDE-specific quirks

---

## 🔗 Resources

- **Cursor MCP Docs:** https://cursor.sh/docs
- **Claude Code MCP Docs:** (verify URL)
- **MCP Protocol:** https://modelcontextprotocol.io/

---

**Status:** 🔄 In Progress  
**Last Updated:** 2024-12-04

