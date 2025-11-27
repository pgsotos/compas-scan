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
# Health check
curl http://localhost:8000/health

# Probar con una marca
curl "http://localhost:8000/?brand=Nike"

# Abrir documentación Swagger
open http://localhost:8000/docs
```

## 📋 Comandos Útiles

### Gestión de Servicios

```bash
make docker-up         # Iniciar servicios en background
make docker-down       # Detener servicios
make docker-restart    # Reiniciar servicios
make docker-logs       # Ver logs (Ctrl+C para salir)
```

### Desarrollo

```bash
make docker-shell      # Abrir shell en el contenedor API
make docker-test       # Ejecutar tests dentro del contenedor
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

#### 2. **Redis (Puerto 6379)**

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
curl http://localhost:8000/health
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

### Error: "Port 8000 already in use"

```bash
# Detén otros servicios en ese puerto o cambia el puerto en docker-compose.yml
docker-compose down
lsof -ti:8000 | xargs kill -9
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
