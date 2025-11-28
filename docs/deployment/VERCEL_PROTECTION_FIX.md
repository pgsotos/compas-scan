# 🔓 Deshabilitar Vercel Protection

## ⚠️ Problema Detectado

Los ambientes de **Development** y **Staging** tienen **Vercel Protection** habilitada, lo que requiere autenticación para acceder a los endpoints.

```
Error actual:
<!doctype html>
<title>Authentication Required</title>
```

Esto impide que los endpoints públicos como `/health` funcionen correctamente.

---

## ✅ Solución: Deshabilitar Protection

### Paso 1: Abrir Vercel Dashboard

```
1. Ir a: https://vercel.com/dashboard
2. Seleccionar proyecto: compas-scan
3. Click en "Settings" (arriba)
4. Click en "Deployment Protection" (menú lateral)
```

### Paso 2: Configurar Protection por Ambiente

**Para Development (develop branch):**

```
1. Buscar sección: "Preview Deployments"
2. Encontrar: "Protection for develop branch"
3. Cambiar de "Standard Protection" a "Only Preview Deployment URLs"
   O mejor aún: "Disabled" (si no necesitas protección)
4. Click "Save"
```

**Para Staging (staging branch):**

```
1. En la misma sección "Preview Deployments"
2. Encontrar: "Protection for staging branch"
3. Cambiar a "Disabled" o "Only Preview Deployment URLs"
4. Click "Save"
```

**Para Production (main branch):**

```
Production ya está funcionando correctamente.
No cambiar nada en "Production Deployment Protection".
```

---

## 🎯 Configuración Recomendada

| Ambiente | Branch | Protection | Razón |
|----------|--------|------------|-------|
| **Production** | `main` | Standard Protection (opcional) | Producción puede tener seguridad extra |
| **Staging** | `staging` | Disabled | Necesita ser accesible para QA testing |
| **Development** | `develop` | Disabled | Necesita ser accesible para desarrollo activo |

---

## 🧪 Verificar que Funcionó

Después de deshabilitar Protection:

### Development:
```bash
curl https://compas-scan-dev.vercel.app/health

# Debe retornar:
{
  "status": "healthy",
  "service": "CompasScan API",
  "version": "2.0.0",
  "environment": "preview",
  "observability": {
    "logfire": true,
    "sentry": true
  }
}
```

### Staging:
```bash
curl https://compas-scan-staging.vercel.app/health

# Debe retornar el mismo JSON
```

### Production:
```bash
curl https://compas-scan.vercel.app/health

# Debe retornar el mismo JSON
```

---

## 📚 Más Información

**Documentación Oficial:**
- [Vercel Deployment Protection](https://vercel.com/docs/security/deployment-protection)

**¿Por qué esto sucede?**
- Vercel activa Protection por defecto en algunos planes
- Es útil para proteger Preview Deployments de acceso no autorizado
- Pero para APIs públicas, necesitamos deshabilitar esto

---

## 🚨 Troubleshooting

### Si aún ves "Authentication Required":

1. **Esperar 1-2 minutos** después de cambiar la configuración
2. **Hacer un redeploy:**
   ```bash
   git commit --allow-empty -m "chore: trigger redeploy"
   git push origin develop
   ```
3. **Verificar con navegador incógnito** (para evitar caché)

### Si el endpoint `/health` retorna error de "brand required":

Esto es un problema de routing (ya solucionado en el PR actual).
Espera el deployment del nuevo `vercel.json`.

---

**✅ Una vez completado, todos los ambientes deberían responder correctamente a `/health`**

