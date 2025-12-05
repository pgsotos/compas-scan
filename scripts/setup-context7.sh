#!/bin/bash
# Script para configurar Context7 MCP en el IDE

set -e

# Source IDE detection utility
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/detect-ide.sh"

# Get MCP config paths
MCP_CONFIG_DIR=$(get_mcp_config_dir)
MCP_CONFIG_FILE=$(get_mcp_config_path)

echo "🔧 Configurando Context7 MCP para el IDE..."
echo ""

# Crear directorio si no existe
if [ ! -d "$MCP_CONFIG_DIR" ]; then
    echo "📁 Creando directorio $MCP_CONFIG_DIR..."
    mkdir -p "$MCP_CONFIG_DIR"
fi

# Verificar si ya existe configuración
if [ -f "$MCP_CONFIG_FILE" ]; then
    echo "⚠️  Archivo mcp.json ya existe."
    echo "📋 Contenido actual:"
    cat "$MCP_CONFIG_FILE"
    echo ""
    read -p "¿Deseas actualizar la configuración de Context7? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelado."
        exit 1
    fi
    
    # Backup
    cp "$MCP_CONFIG_FILE" "$MCP_CONFIG_FILE.backup"
    echo "✅ Backup creado: $MCP_CONFIG_FILE.backup"
else
    echo "📝 Creando nuevo archivo de configuración..."
fi

# Preguntar por API key con validación
echo ""
echo "🔑 API Key de Context7"
echo "   Obtén tu API key en: https://console.upstash.com/context7"
echo "   La API key debe empezar con 'ctx7sk'"
echo ""
while true; do
    read -p "Ingresa tu API key de Context7 (o presiona Enter para continuar sin ella): " CONTEXT7_API_KEY
    
    if [ -z "$CONTEXT7_API_KEY" ]; then
        echo "⚠️  Continuando sin API key (funcionará con límites)..."
        break
    elif [[ "$CONTEXT7_API_KEY" =~ ^ctx7sk ]]; then
        echo "✅ API key válida detectada"
        break
    else
        echo "❌ Error: La API key debe empezar con 'ctx7sk'"
        echo "   Ejemplo: ctx7sk_xxxxxxxxxxxxx"
        read -p "¿Deseas intentar de nuevo? (y/n): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "⚠️  Continuando sin API key..."
            CONTEXT7_API_KEY=""
            break
        fi
    fi
done

# Detectar package manager preferido
if command -v bunx &> /dev/null; then
    PKG_MANAGER="bunx"
    PKG_MANAGER_NAME="Bun"
    echo "✅ Detectado: Bun (usando bunx)"
elif command -v npx &> /dev/null; then
    PKG_MANAGER="npx"
    PKG_MANAGER_NAME="npm"
    echo "✅ Detectado: npm (usando npx)"
else
    echo "❌ Error: No se encontró bunx ni npx. Por favor instala Bun o Node.js."
    exit 1
fi

# Crear configuración
if [ -z "$CONTEXT7_API_KEY" ]; then
    echo "📝 Configurando Context7 sin API key (funcionará con límites)..."
    cat > "$MCP_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "context7": {
      "command": "$PKG_MANAGER",
      "args": [
        "-y",
        "@upstash/context7-mcp"
      ]
    }
  }
}
EOF
else
    echo "📝 Configurando Context7 con API key..."
    cat > "$MCP_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "context7": {
      "command": "$PKG_MANAGER",
      "args": [
        "-y",
        "@upstash/context7-mcp",
        "--api-key",
        "$CONTEXT7_API_KEY"
      ]
    }
  }
}
EOF
fi

echo "📦 Usando: $PKG_MANAGER_NAME ($PKG_MANAGER)"

echo ""
echo "✅ Configuración completada!"
echo ""
echo "📋 Archivo creado en: $MCP_CONFIG_FILE"
echo ""
echo "📝 Contenido:"
cat "$MCP_CONFIG_FILE"
echo ""
echo ""
echo "🔄 Próximos pasos:"
echo "1. Reinicia el IDE completamente"
echo "2. Verifica que Context7 aparece en los recursos MCP"
echo "3. Usa 'use context7' en tus prompts para acceder a documentación actualizada"
echo ""
echo "📖 Para más información, ver: docs/CONTEXT7_SETUP.md"
echo ""

