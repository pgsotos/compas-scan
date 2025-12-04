#!/bin/bash
# Script to configure GitHub MCP in Cursor

set -e

CURSOR_MCP_DIR="$HOME/.cursor"
MCP_CONFIG_FILE="$CURSOR_MCP_DIR/mcp.json"

echo "🔧 Configuring GitHub MCP for Cursor..."
echo ""

# Create directory if it doesn't exist
if [ ! -d "$CURSOR_MCP_DIR" ]; then
    echo "📁 Creating directory $CURSOR_MCP_DIR..."
    mkdir -p "$CURSOR_MCP_DIR"
fi

# Check if GitHub MCP binary exists
GITHUB_MCP_BINARY=""
if command -v github-mcp-server &> /dev/null; then
    GITHUB_MCP_BINARY=$(which github-mcp-server)
    echo "✅ Found github-mcp-server binary: $GITHUB_MCP_BINARY"
elif [ -f "$HOME/.local/bin/github-mcp-server" ]; then
    GITHUB_MCP_BINARY="$HOME/.local/bin/github-mcp-server"
    echo "✅ Found github-mcp-server binary: $GITHUB_MCP_BINARY"
else
    echo "⚠️  GitHub MCP binary not found in PATH"
    
    # Check for Docker automatically
    if command -v docker &> /dev/null; then
        echo "✅ Docker detected, will use Docker image"
        USE_DOCKER=true
    else
        echo ""
        echo "📥 To install GitHub MCP Server:"
        echo "   1. Download from: https://github.com/github/github-mcp-server/releases"
        echo "   2. Extract and place in PATH (e.g., ~/.local/bin/)"
        echo "   3. Make executable: chmod +x github-mcp-server"
        echo ""
        echo "❌ Error: Docker not found. Please install Docker or the GitHub MCP binary."
        exit 1
    fi
fi

# Backup existing config
if [ -f "$MCP_CONFIG_FILE" ]; then
    echo "⚠️  mcp.json already exists."
    echo "📋 Current configuration:"
    cat "$MCP_CONFIG_FILE" | python3 -m json.tool 2>/dev/null || cat "$MCP_CONFIG_FILE"
    echo ""
    read -p "Do you want to add GitHub MCP to existing config? (y/n): " -n 1 -r
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

# Ask for GitHub token
echo ""
echo "🔑 GitHub Personal Access Token"
echo "   Get your token at: https://github.com/settings/tokens"
echo "   Supported token types:"
echo "   - Classic PAT: ghp_xxxxxxxxxxxxx"
echo "   - Fine-grained PAT: github_pat_xxxxxxxxxxxxx"
echo "   Required scopes: repo (read and write)"
echo ""
while true; do
    read -p "Enter your GitHub Personal Access Token (or press Enter to skip): " GITHUB_TOKEN
    
    if [ -z "$GITHUB_TOKEN" ]; then
        echo "⚠️  Continuing without token (read-only mode recommended)..."
        break
    elif [[ "$GITHUB_TOKEN" =~ ^ghp_ ]] || [[ "$GITHUB_TOKEN" =~ ^gho_ ]] || [[ "$GITHUB_TOKEN" =~ ^ghu_ ]] || [[ "$GITHUB_TOKEN" =~ ^github_pat_ ]]; then
        echo "✅ Valid token format detected"
        break
    else
        echo "❌ Error: Token should start with 'ghp_', 'gho_', 'ghu_', or 'github_pat_'"
        echo "   Examples:"
        echo "   - Classic PAT: ghp_xxxxxxxxxxxxx"
        echo "   - Fine-grained PAT: github_pat_xxxxxxxxxxxxx"
        read -p "Try again? (y/n): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "⚠️  Continuing without token..."
            GITHUB_TOKEN=""
            break
        fi
    fi
done

# Ask for read-only mode preference
echo ""
read -p "Enable read-only mode? (recommended for safety) (y/n): " -n 1 -r
echo ""
READ_ONLY=""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    READ_ONLY="--read-only"
    echo "✅ Read-only mode enabled"
else
    echo "⚠️  Read-only mode disabled (full access)"
fi

# Read existing config or create new
if [ -f "$MCP_CONFIG_FILE" ]; then
    EXISTING_CONFIG=$(cat "$MCP_CONFIG_FILE")
else
    EXISTING_CONFIG='{"mcpServers":{}}'
fi

# Build GitHub MCP configuration
if [ "$USE_DOCKER" = "true" ]; then
    # Docker configuration
    if [ -n "$GITHUB_TOKEN" ]; then
        GITHUB_MCP_CONFIG=$(cat <<EOF
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN=$GITHUB_TOKEN",
        $( [ -n "$READ_ONLY" ] && echo '"-e", "GITHUB_READ_ONLY=1",' || echo '')
        "ghcr.io/github/github-mcp-server"
      ]
    }
EOF
)
    else
        GITHUB_MCP_CONFIG=$(cat <<EOF
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        $( [ -n "$READ_ONLY" ] && echo '"-e", "GITHUB_READ_ONLY=1",' || echo '')
        "ghcr.io/github/github-mcp-server"
      ]
    }
EOF
)
    fi
else
    # Binary configuration
    if [ -n "$GITHUB_TOKEN" ]; then
        GITHUB_MCP_CONFIG=$(cat <<EOF
    "github": {
      "command": "$GITHUB_MCP_BINARY",
      "args": [
        $( [ -n "$READ_ONLY" ] && echo '"--read-only",' || echo '')
        "--token", "$GITHUB_TOKEN"
      ]
    }
EOF
)
    else
        GITHUB_MCP_CONFIG=$(cat <<EOF
    "github": {
      "command": "$GITHUB_MCP_BINARY",
      "args": [
        $( [ -n "$READ_ONLY" ] && echo '"--read-only"' || echo '')
      ]
    }
EOF
)
    fi
fi

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
    
    # Add GitHub MCP config
    github_config = json.loads('''{$GITHUB_MCP_CONFIG}''')
    existing["mcpServers"]["github"] = github_config["github"]
    
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
echo "2. Verify GitHub MCP appears in MCP resources"
echo "3. GitHub MCP can now create PRs and query repository information"
echo ""
echo "📖 For more information, see: docs/MCP_RECOMMENDATIONS.md"
echo ""

