#!/bin/bash
# Script rápido para actualizar solo la API key de Context7

set -e

CURSOR_MCP_DIR="$HOME/.cursor"
MCP_CONFIG_FILE="$CURSOR_MCP_DIR/mcp.json"

if [ -z "$1" ]; then
    echo "🔑 Actualizar API Key de Context7"
    echo ""
    echo "Uso:"
    echo "  ./update-context7-key.sh <tu-api-key>"
    echo ""
    echo "Obtén tu API key en: https://console.upstash.com/context7"
    echo "La API key debe empezar con 'ctx7sk'"
    echo ""
    exit 1
fi

API_KEY="$1"

# Validar formato de API key
if [[ ! "$API_KEY" =~ ^ctx7sk ]]; then
    echo "❌ Error: La API key debe empezar con 'ctx7sk'"
    echo "   Ejemplo: ctx7sk_xxxxxxxxxxxxx"
    exit 1
fi

# Verificar que existe el archivo
if [ ! -f "$MCP_CONFIG_FILE" ]; then
    echo "❌ Error: No se encontró $MCP_CONFIG_FILE"
    echo "   Ejecuta primero: ./setup-context7.sh"
    exit 1
fi

# Backup
cp "$MCP_CONFIG_FILE" "$MCP_CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
echo "✅ Backup creado"

# Detectar package manager
if command -v bunx &> /dev/null; then
    PKG_MANAGER="bunx"
    PKG_MANAGER_NAME="Bun"
elif command -v npx &> /dev/null; then
    PKG_MANAGER="npx"
    PKG_MANAGER_NAME="npm"
else
    echo "❌ Error: No se encontró bunx ni npx"
    exit 1
fi

# Actualizar configuración
cat > "$MCP_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "context7": {
      "command": "$PKG_MANAGER",
      "args": [
        "-y",
        "@upstash/context7-mcp",
        "--api-key",
        "$API_KEY"
      ]
    }
  }
}
EOF

echo "✅ API key actualizada"
echo "📦 Usando: $PKG_MANAGER_NAME ($PKG_MANAGER)"
echo ""
echo "📋 Configuración actualizada:"
cat "$MCP_CONFIG_FILE"
echo ""
echo "🔄 Próximos pasos:"
echo "1. Reinicia Cursor completamente"
echo "2. Verifica que Context7 funciona con la nueva API key"
echo ""


