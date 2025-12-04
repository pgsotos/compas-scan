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

### `check-mcp-status.sh`
Script para verificar el estado de los MCPs configurados en Cursor.

**Uso:**
```bash
./scripts/check-mcp-status.sh
```

**Muestra:**
- Estado del archivo de configuración MCP
- Package managers disponibles (bunx/npx)
- Estado de Context7 MCP y API key
- Notas y próximos pasos

## Notas

- Todos los scripts son ejecutables (`chmod +x`)
- Los scripts validan inputs y crean backups cuando es necesario
- Consulta la documentación en `docs/` para más detalles

