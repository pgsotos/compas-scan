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

# Verificar Context7 específicamente
if grep -q "context7" "$MCP_CONFIG_FILE" 2>/dev/null; then
    echo "✅ Context7 MCP configurado"
    
    # Verificar si tiene API key
    if grep -q "ctx7sk" "$MCP_CONFIG_FILE" 2>/dev/null; then
        API_KEY=$(grep -o "ctx7sk-[^\"]*" "$MCP_CONFIG_FILE" | head -1)
        if [ -n "$API_KEY" ]; then
            echo "  ✅ API Key configurada: ${API_KEY:0:20}..."
        else
            echo "  ⚠️  API Key no encontrada (funcionará con límites)"
        fi
    else
        echo "  ⚠️  API Key no configurada (funcionará con límites)"
    fi
else
    echo "❌ Context7 MCP no configurado"
fi

echo ""
echo "📝 Notas:"
echo "  - Los MCPs se activan al reiniciar Cursor IDE"
echo "  - Si no ves recursos MCP disponibles, reinicia Cursor"
echo "  - Para actualizar la API key: ./scripts/update-context7-key.sh <key>"
echo ""
echo "🔗 Recursos útiles:"
echo "  - Context7 Console: https://console.upstash.com/context7"
echo "  - Documentación: docs/CONTEXT7_SETUP.md"
echo ""

