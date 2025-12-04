# Scripts de Utilidad

Este directorio contiene scripts de utilidad para configurar y mantener el proyecto.

## Scripts Disponibles

### `setup-env-vars.sh`
Script interactivo para configurar variables de entorno en el archivo `.env`.

**Uso:**
```bash
./scripts/setup-env-vars.sh
```

### `detect-ide.sh`
Script utilitario para detectar paths de configuración MCP del IDE.

**Uso:**
```bash
source scripts/detect-ide.sh
MCP_CONFIG_FILE=$(get_mcp_config_path)
```

**Características:**
- Detecta automáticamente el path del MCP config
- Compatible con cualquier IDE MCP-compatible
- Usa terminología genérica "IDE"

**Nota:** Usado internamente por otros scripts de setup.

---

### `setup-context7.sh`
Script para configurar Context7 MCP en el IDE.

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

### `fix-github-mcp-token.sh`
Script para actualizar el token de GitHub MCP con permisos completos.

**Uso:**
```bash
./scripts/fix-github-mcp-token.sh
```

**Características:**
- Obtiene token del gh CLI (con permisos completos)
- Crea backup automático de la configuración
- Actualiza token en `~/.cursor/mcp.json`
- Verifica scopes del token

**Nota:** Ejecutar si GitHub MCP falla con error 403 (permisos insuficientes).

---

### `configure-branch-protections.sh`
Script para configurar protecciones de rama según Gitflow (todas las ramas).

**Uso:**
```bash
./scripts/configure-branch-protections.sh
```

**Configuración aplicada:**
- **develop:** 0 reviews, iteración rápida (GitHub MCP puede mergear directamente)
- **staging:** 1 review, validación QA con checks estrictos de Vercel
- **main:** 2 reviews, seguridad máxima con enforce_admins habilitado

**Características:**
- Configura todas las ramas de una vez
- Usa GitHub API directamente
- Aplica mejores prácticas de Gitflow
- Permite GitHub MCP trabajar eficientemente

**Nota:** Ver `docs/BRANCH_PROTECTION_GUIDE.md` para detalles completos.

---

### `adjust-branch-protection.sh`
Script interactivo para ajustar las protecciones de rama en develop (individual).

**Uso:**
```bash
./scripts/adjust-branch-protection.sh
```

**Opciones:**
1. Mantener protecciones actuales (usar `--admin` para mergear)
2. Deshabilitar enforce_admins (admins pueden mergear sin restricciones)
3. Eliminar todas las protecciones (no recomendado)
4. Eliminar requisito de reviews (recomendado para solo dev)

**Nota:** Ver `docs/BRANCH_PROTECTION_GUIDE.md` para configuraciones recomendadas.

---

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
  - GitHub MCP y token (binario o Docker)
  - Memory MCP
- Notas y próximos pasos

## Notas

- Todos los scripts son ejecutables (`chmod +x`)
- Los scripts validan inputs y crean backups cuando es necesario
- Consulta la documentación en `docs/` para más detalles

