# Scripts de Utilidad

Este directorio contiene scripts de utilidad para configurar y mantener el proyecto.

## Scripts Disponibles

### `setup-env-vars.sh`
Script interactivo para configurar variables de entorno en el archivo `.env`.

**Uso:**
```bash
./scripts/setup-env-vars.sh
```

### `setup-context7.sh`
Script para configurar Context7 MCP en Cursor IDE.

**Uso:**
```bash
./scripts/setup-context7.sh
```

### `update-context7-key.sh`
Script para actualizar la API key de Context7 MCP.

**Uso:**
```bash
./scripts/update-context7-key.sh <tu-api-key>
```

### `install-github-mcp-binary.sh`
Script para instalar el binario de GitHub MCP Server como alternativa a Docker.

**Uso:**
```bash
./scripts/install-github-mcp-binary.sh
```

**Características:**
- Detecta automáticamente OS (darwin/linux) y arquitectura (amd64/arm64)
- Descarga binario oficial desde GitHub releases
- Instala en `~/.local/bin/`
- Verifica instalación y configuración del PATH

**Nota:** Ejecutar antes de `setup-github-mcp.sh` si prefieres usar el binario en lugar de Docker.

---

### `setup-github-mcp.sh`
Script para configurar GitHub MCP en Cursor IDE.

**Uso:**
```bash
# Opción 1: Instalar binario primero (recomendado)
./scripts/install-github-mcp-binary.sh
./scripts/setup-github-mcp.sh

# Opción 2: Usar Docker (requiere Docker Desktop)
./scripts/setup-github-mcp.sh
```

**Características:**
- Soporta binario (instalar con `install-github-mcp-binary.sh`) o Docker
- Configuración de token de GitHub (opcional)
- Soporta tokens clásicos y fine-grained (github_pat_)
- Modo read-only (recomendado)
- Integra con configuración MCP existente

### `setup-memory-mcp.sh`
Script para configurar Memory MCP en Cursor IDE.

**Uso:**
```bash
./scripts/setup-memory-mcp.sh
```

**Características:**
- Retención de contexto entre sesiones
- No requiere API keys
- Integra con configuración MCP existente

### `check-mcp-status.sh`
Script para verificar el estado de los MCPs configurados en Cursor.

**Uso:**
```bash
./scripts/check-mcp-status.sh
```

**Muestra:**
- Estado del archivo de configuración MCP
- Package managers disponibles (bunx/npx)
- Estado de todos los MCPs configurados:
  - Context7 MCP y API key
  - GitHub MCP y token
  - Memory MCP
- Notas y próximos pasos

## Notas

- Todos los scripts son ejecutables (`chmod +x`)
- Los scripts validan inputs y crean backups cuando es necesario
- Consulta la documentación en `docs/` para más detalles

