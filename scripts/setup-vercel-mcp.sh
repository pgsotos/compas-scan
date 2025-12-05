#!/bin/bash
# Script to configure Vercel MCP in Cursor

set -e

CURSOR_MCP_DIR="$HOME/.cursor"
MCP_CONFIG_FILE="$CURSOR_MCP_DIR/mcp.json"

echo "🔧 Configuring Vercel MCP for Cursor..."
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
    echo "⚠️  Warning: bunx or npx not found."
    echo "   Will use remote HTTP server instead."
    USE_REMOTE=true
fi

# Backup existing config
if [ -f "$MCP_CONFIG_FILE" ]; then
    echo "⚠️  mcp.json already exists."
    echo "📋 Current configuration:"
    cat "$MCP_CONFIG_FILE" | python3 -m json.tool 2>/dev/null || cat "$MCP_CONFIG_FILE"
    echo ""
    read -p "Do you want to add Vercel MCP to existing config? (y/n): " -n 1 -r
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

# Check for Vercel token in environment variable first
if [ -n "$VERCEL_TOKEN" ]; then
    echo "✅ Using VERCEL_TOKEN from environment"
else
    # Ask for Vercel token
    echo ""
    echo "🔑 Vercel Token"
    echo "   Get your token at: https://vercel.com/account/tokens"
    echo "   Required scopes: read, deployments:read, projects:read"
    echo "   Optional (for full access): write"
    echo "   Or set VERCEL_TOKEN environment variable"
    echo ""
    while true; do
        read -p "Enter your Vercel token (required): " VERCEL_TOKEN
        
        if [ -z "$VERCEL_TOKEN" ]; then
            echo "❌ Error: Vercel token is required"
            read -p "Try again? (y/n): " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "❌ Setup cancelled. Vercel token is required."
                exit 1
            fi
        else
            echo "✅ Token provided"
            break
        fi
    done
fi

# Vercel MCP uses remote HTTP server (no local package available)
SETUP_METHOD="remote"
echo ""
echo "ℹ️  Vercel MCP uses remote HTTP server: https://mcp.vercel.com"

# Read existing config or create new
if [ -f "$MCP_CONFIG_FILE" ]; then
    EXISTING_CONFIG=$(cat "$MCP_CONFIG_FILE")
else
    EXISTING_CONFIG='{"mcpServers":{}}'
fi

# Build Vercel MCP configuration (always uses remote HTTP server)
VERCEL_MCP_CONFIG=$(cat <<EOF
    "vercel": {
      "url": "https://mcp.vercel.com",
      "transport": "http",
      "headers": {
        "Authorization": "Bearer $VERCEL_TOKEN"
      }
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
    
    # Add Vercel MCP config
    vercel_config = json.loads('''{$VERCEL_MCP_CONFIG}''')
    existing["mcpServers"]["vercel"] = vercel_config["vercel"]
    
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
echo "2. Verify Vercel MCP appears in MCP resources"
echo "3. Vercel MCP can now:"
echo "   - Search Vercel documentation"
echo "   - List projects and deployments"
echo "   - Analyze deployment logs"
echo "   - Manage domains and configurations"
echo ""
echo "📖 For more information, see:"
echo "   - docs/MCP_RECOMMENDATIONS.md"
echo "   - https://vercel.com/docs/mcp/vercel-mcp"
echo ""
