# 🚀 Deployment Documentation

Esta carpeta contiene toda la documentación relacionada con el despliegue de CompasScan.

## 📋 Índice

### Vercel Deployment

1. **[VERCEL.md](./VERCEL.md)** - Documentación principal de Vercel
   - Configuración general
   - Estructura de ambientes
   - Variables de entorno

2. **[VERCEL_QUICK_SETUP.md](./VERCEL_QUICK_SETUP.md)** - Setup rápido (Opción A)
   - Configuración unificada de keys
   - Pasos mínimos para deployment

3. **[VERCEL_ENV_SETUP.md](./VERCEL_ENV_SETUP.md)** - Setup completo de ambientes
   - Configuración detallada por ambiente
   - Dominios y protecciones

4. **[VERCEL_ENV_CHECK.md](./VERCEL_ENV_CHECK.md)** - Verificación de variables
   - Checklist de configuración
   - Validación de ambientes

5. **[VERCEL_PROTECTION_FIX.md](./VERCEL_PROTECTION_FIX.md)** - Solución de problemas
   - Deshabilitar Vercel Protection
   - Troubleshooting común

## 🌐 Ambientes

CompasScan utiliza un flujo Gitflow con 3 ambientes:

| Ambiente | Branch | URL | Propósito |
|----------|--------|-----|-----------|
| **Production** | `main` | https://compas-scan.vercel.app | Producción estable |
| **Staging** | `staging` | https://compas-scan-staging.vercel.app | Pre-producción/QA |
| **Development** | `develop` | https://compas-scan-dev.vercel.app | Desarrollo activo |

## 📚 Documentos Relacionados

- [Docker Deployment](../DOCKER.md)
- [API Keys Guide](../API_KEYS_GUIDE.md)
- [Observability](../OBSERVABILITY.md)

---

**Última actualización:** $(date +%Y-%m-%d)

