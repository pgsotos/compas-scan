#!/bin/bash
# Script to configure Memory MCP in Cursor

set -e

CURSOR_MCP_DIR="$HOME/.cursor"
MCP_CONFIG_FILE="$CURSOR_MCP_DIR/mcp.json"

echo "🔧 Configuring Memory MCP for Cursor..."
echo ""

# Create directory if it doesn't exist
if [ ! -d "$CURSOR_MCP_DIR" ]; then
    echo "📁 Creating directory $CURSOR_MCP_DIR..."
    mkdir -p "$CURSOR_MCP_DIR"
fi

# Detect preferred package manager
if command -v bunx &> /dev/null; then
    PKG_MANAGER="bunx"
    PKG_MANAGER_NAME="Bun"
    echo "✅ Detected: Bun (using bunx)"
elif command -v npx &> /dev/null; then
    PKG_MANAGER="npx"
    PKG_MANAGER_NAME="npm"
    echo "✅ Detected: npm (using npx)"
else
    echo "❌ Error: bunx or npx not found. Please install Bun or Node.js."
    exit 1
fi

# Backup existing config
if [ -f "$MCP_CONFIG_FILE" ]; then
    echo "⚠️  mcp.json already exists."
    echo "📋 Current configuration:"
    cat "$MCP_CONFIG_FILE" | python3 -m json.tool 2>/dev/null || cat "$MCP_CONFIG_FILE"
    echo ""
    read -p "Do you want to add Memory MCP to existing config? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled."
        exit 1
    fi
    
    # Backup
    cp "$MCP_CONFIG_FILE" "$MCP_CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backup created"
else
    echo "📝 Creating new configuration file..."
fi

# Read existing config or create new
if [ -f "$MCP_CONFIG_FILE" ]; then
    EXISTING_CONFIG=$(cat "$MCP_CONFIG_FILE")
else
    EXISTING_CONFIG='{"mcpServers":{}}'
fi

# Build Memory MCP configuration
MEMORY_MCP_CONFIG=$(cat <<EOF
    "memory": {
      "command": "$PKG_MANAGER",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ]
    }
EOF
)

# Merge with existing config using Python
python3 <<PYTHON_SCRIPT
import json
import sys

try:
    # Read existing config
    existing = json.loads('''$EXISTING_CONFIG''')
    
    # Ensure mcpServers exists
    if "mcpServers" not in existing:
        existing["mcpServers"] = {}
    
    # Add Memory MCP config
    memory_config = json.loads('''{$MEMORY_MCP_CONFIG}''')
    existing["mcpServers"]["memory"] = memory_config["memory"]
    
    # Write updated config
    with open("$MCP_CONFIG_FILE", "w") as f:
        json.dump(existing, f, indent=2)
    
    print("✅ Configuration updated successfully")
except Exception as e:
    print(f"❌ Error updating configuration: {e}")
    sys.exit(1)
PYTHON_SCRIPT

echo ""
echo "✅ Configuration completed!"
echo ""
echo "📋 Updated configuration:"
cat "$MCP_CONFIG_FILE" | python3 -m json.tool
echo ""
echo ""
echo "🔄 Next steps:"
echo "1. Restart Cursor completely"
echo "2. Memory MCP will retain context across sessions"
echo "3. AI assistant will remember previous conversations and decisions"
echo ""
echo "📖 For more information, see: docs/MCP_RECOMMENDATIONS.md"
echo ""

