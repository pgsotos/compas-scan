#!/bin/bash
# Script para verificar el estado de los MCPs configurados en Cursor

set -e

CURSOR_MCP_DIR="$HOME/.cursor"
MCP_CONFIG_FILE="$CURSOR_MCP_DIR/mcp.json"

echo "🔍 Verificando estado de MCPs en Cursor..."
echo ""

# Verificar si existe el archivo de configuración
if [ ! -f "$MCP_CONFIG_FILE" ]; then
    echo "❌ No se encontró archivo de configuración MCP"
    echo "   Ubicación esperada: $MCP_CONFIG_FILE"
    echo ""
    echo "💡 Para configurar Context7 MCP, ejecuta:"
    echo "   ./scripts/setup-context7.sh"
    exit 1
fi

echo "✅ Archivo de configuración encontrado: $MCP_CONFIG_FILE"
echo ""

# Mostrar configuración actual
echo "📋 Configuración actual:"
cat "$MCP_CONFIG_FILE" | python3 -m json.tool 2>/dev/null || cat "$MCP_CONFIG_FILE"
echo ""

# Verificar package managers
echo "🔧 Verificando package managers..."
if command -v bunx &> /dev/null; then
    echo "  ✅ bunx encontrado: $(which bunx)"
else
    echo "  ⚠️  bunx no encontrado"
fi

if command -v npx &> /dev/null; then
    echo "  ✅ npx encontrado: $(which npx)"
else
    echo "  ⚠️  npx no encontrado"
fi

echo ""

# Verify each MCP
echo "📊 MCP Status:"
echo ""

# Context7 MCP
if grep -q "context7" "$MCP_CONFIG_FILE" 2>/dev/null; then
    echo "✅ Context7 MCP: Configured"
    if grep -q "ctx7sk" "$MCP_CONFIG_FILE" 2>/dev/null; then
        API_KEY=$(grep -o "ctx7sk-[^\"]*" "$MCP_CONFIG_FILE" | head -1)
        if [ -n "$API_KEY" ]; then
            echo "   ✅ API Key: ${API_KEY:0:20}..."
        else
            echo "   ⚠️  API Key not found (limited functionality)"
        fi
    else
        echo "   ⚠️  API Key not configured (limited functionality)"
    fi
else
    echo "❌ Context7 MCP: Not configured"
fi

# GitHub MCP
if grep -q "\"github\"" "$MCP_CONFIG_FILE" 2>/dev/null; then
    echo "✅ GitHub MCP: Configured"
    if grep -q "GITHUB_PERSONAL_ACCESS_TOKEN\|--token" "$MCP_CONFIG_FILE" 2>/dev/null; then
        echo "   ✅ Token configured"
    else
        echo "   ⚠️  Token not configured (read-only mode)"
    fi
    if grep -q "read-only\|GITHUB_READ_ONLY" "$MCP_CONFIG_FILE" 2>/dev/null; then
        echo "   ✅ Read-only mode enabled"
    fi
else
    echo "❌ GitHub MCP: Not configured"
fi

# Memory MCP
if grep -q "\"memory\"" "$MCP_CONFIG_FILE" 2>/dev/null; then
    echo "✅ Memory MCP: Configured"
else
    echo "❌ Memory MCP: Not configured"
fi

echo ""
echo "📝 Notes:"
echo "  - MCPs activate after restarting Cursor IDE"
echo "  - If MCP resources are not available, restart Cursor"
echo ""
echo "🔧 Setup scripts:"
echo "  - Context7: ./scripts/setup-context7.sh"
echo "  - GitHub:  ./scripts/setup-github-mcp.sh"
echo "  - Memory:  ./scripts/setup-memory-mcp.sh"
echo ""
echo "🔗 Useful resources:"
echo "  - Context7 Console: https://console.upstash.com/context7"
echo "  - GitHub MCP: https://github.com/github/github-mcp-server"
echo "  - Documentation: docs/MCP_RECOMMENDATIONS.md"
echo ""

