#!/bin/bash
# Script to update GitHub MCP token with proper write permissions

set -e

CURSOR_MCP_FILE="$HOME/.cursor/mcp.json"

echo "🔧 Actualizando token de GitHub MCP..."
echo ""

# Get current gh CLI token (has full permissions)
GH_TOKEN=$(gh auth token)

if [ -z "$GH_TOKEN" ]; then
    echo "❌ Error: No se pudo obtener el token de gh CLI"
    echo "   Ejecuta: gh auth login"
    exit 1
fi

echo "✅ Token obtenido de gh CLI"
echo ""

# Backup current config
if [ -f "$CURSOR_MCP_FILE" ]; then
    cp "$CURSOR_MCP_FILE" "$CURSOR_MCP_FILE.backup-$(date +%Y%m%d%H%M%S)"
    echo "✅ Backup creado: $CURSOR_MCP_FILE.backup-$(date +%Y%m%d%H%M%S)"
fi

# Update GitHub MCP token using Python
python3 << PYTHON_SCRIPT
import json
import os

mcp_file = os.path.expanduser("$CURSOR_MCP_FILE")
gh_token = "$GH_TOKEN"

# Read current config
with open(mcp_file, 'r') as f:
    config = json.load(f)

# Update GitHub MCP token
if "github" in config["mcpServers"]:
    if "env" in config["mcpServers"]["github"]:
        config["mcpServers"]["github"]["env"]["GITHUB_PERSONAL_ACCESS_TOKEN"] = gh_token
        print("✅ Token actualizado en configuración existente")
    else:
        config["mcpServers"]["github"]["env"] = {
            "GITHUB_PERSONAL_ACCESS_TOKEN": gh_token
        }
        print("✅ Token añadido a configuración")
else:
    print("⚠️  GitHub MCP no configurado")
    exit(1)

# Write updated config
with open(mcp_file, 'w') as f:
    json.dump(config, f, indent=2)

print("✅ Configuración actualizada")
PYTHON_SCRIPT

echo ""
echo "✅ Token actualizado con permisos completos"
echo ""
echo "📝 Scopes del token:"
gh auth status 2>&1 | grep "Token scopes"
echo ""
echo "🔄 Reinicia Cursor para aplicar los cambios"

