# 🐳 CompasScan - Docker Guide

## Prerequisitos

- Docker Desktop instalado: [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
- Docker Compose (incluido en Docker Desktop)

## 🚀 Quick Start

### 1. Configurar Variables de Entorno

```bash
cp env.example .env
```

Edita `.env` con tus credenciales reales:

```env
GEMINI_API_KEY=your_actual_gemini_key
GOOGLE_API_KEY=your_actual_google_key
GOOGLE_CSE_ID=your_actual_cse_id
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_actual_supabase_key
```

### 2. Iniciar Servicios

```bash
# Opción A: Con Makefile (Recomendado)
make docker-up

# Opción B: Comando directo
docker-compose up -d
```

### 3. Verificar que Funcione

```bash
# Health check API
curl http://localhost:8000/health

# Health check Frontend (a través de rewrite)
curl http://localhost:3000/api/health

# Probar con una marca (API directo)
curl "http://localhost:8000/?brand=Nike"

# Abrir Frontend en navegador
open http://localhost:3000

# Abrir documentación Swagger
open http://localhost:8000/docs
```

## 📋 Comandos Útiles

### Gestión de Servicios

```bash
make docker-up              # Iniciar todos los servicios
make docker-down            # Detener servicios
make docker-restart        # Reiniciar todos los servicios
make docker-logs           # Ver logs de todos los servicios
make docker-logs-api       # Ver logs solo del API
make docker-logs-frontend  # Ver logs solo del Frontend
```

### Builds Específicos

```bash
make docker-build          # Build de todos los servicios
make docker-build-api      # Build solo del API
make docker-build-frontend # Build solo del Frontend
```

### Desarrollo

```bash
make docker-shell          # Abrir shell en el contenedor API
make docker-shell-frontend # Abrir shell en el contenedor Frontend
make docker-test           # Ejecutar tests dentro del contenedor
```

### Limpieza

```bash
make docker-clean      # Eliminar containers, volumes e imágenes
```

## 🏗️ Arquitectura Docker

### Servicios Incluidos:

#### 1. **API (Puerto 8000)**

- FastAPI server con hot-reload
- Montaje de volúmenes para desarrollo
- Health check cada 30 segundos
- Auto-restart en caso de fallo

#### 2. **Frontend (Puerto 3000)**

- Next.js 16 con App Router
- Build optimizado con standalone output
- Proxy automático a API en `/api/*`
- Health check cada 30 segundos
- Auto-restart en caso de fallo

#### 3. **Redis (Puerto 6379)**

- Cache preparado para Roadmap Item #6
- Persistencia de datos con volume
- Health check con redis-cli ping

### Network:

- Red Bridge `compas-network` para comunicación entre servicios

## 🔧 Desarrollo con Hot-Reload

El `docker-compose.yml` está configurado para desarrollo con hot-reload:

```yaml
volumes:
  - ./api:/app/api # Cambios en código se reflejan inmediatamente
  - ./test_local.py:/app/test_local.py
```

**Workflow:**

1. Edita archivos localmente
2. Los cambios se reflejan automáticamente en el contenedor
3. Uvicorn detecta cambios y recarga el servidor

## 📊 Verificación

### Health Check del API

```bash
# Directo
curl http://localhost:8000/health

# A través del Frontend (rewrite)
curl http://localhost:3000/api/health
```

Respuesta esperada:

```json
{
  "status": "healthy",
  "service": "CompasScan API",
  "version": "2.0.0",
  "environment": "local"
}
```

### Health Check del Frontend

```bash
# Verificar que el frontend responde
curl http://localhost:3000
```

Debería devolver HTML de la página principal.

### Health Check de Redis

```bash
docker-compose exec redis redis-cli ping
```

Respuesta esperada: `PONG`

## 🐛 Troubleshooting

### Error: "Cannot connect to Docker daemon"

```bash
# Asegúrate de que Docker Desktop esté corriendo
open -a Docker
```

### Error: "Port 8000 already in use" o "Port 3000 already in use"

```bash
# Detén otros servicios en esos puertos o cambia los puertos en docker-compose.yml
docker-compose down
lsof -ti:8000 | xargs kill -9  # API
lsof -ti:3000 | xargs kill -9  # Frontend
```

### Reconstruir desde cero

```bash
make docker-clean
make docker-build
make docker-up
```

## 📝 Notas de Producción

Para desplegar en producción:

1. **Usa multi-stage build** (ya implementado)
2. **Configura secrets** en tu plataforma (no uses .env)
3. **Ajusta health checks** según tu infraestructura
4. **Considera usar** Docker Swarm o Kubernetes para orquestación

## 🔐 Seguridad

- ✅ Contenedor corre como usuario no-root (`compas`)
- ✅ Multi-stage build reduce tamaño de imagen
- ✅ No se copian archivos sensibles (.dockerignore)
- ✅ Health checks para monitoreo
- ✅ Variables de entorno desde .env (nunca en código)
