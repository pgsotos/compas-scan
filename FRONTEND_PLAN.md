# 🎨 Frontend Development Plan - CompasScan

## 📋 Objetivo

Construir una interfaz moderna con Next.js + Tailwind CSS usando Bun como package manager.

---

## 🏗️ Arquitectura

### Stack Tecnológico

- **Framework:** Next.js 14+ (App Router)
- **Styling:** Tailwind CSS
- **Package Manager:** Bun
- **Type Safety:** TypeScript
- **API Client:** Fetch API / SWR (opcional)

### Estructura de Deployment

```
Vercel Project:
├── /api/* → Python FastAPI (Backend)
└── /* → Next.js (Frontend)
```

---

## 📁 Estructura de Archivos

```
compas-scan/
├── api/                    # Backend Python (existente)
├── app/                    # Next.js App Router
│   ├── layout.tsx
│   ├── page.tsx           # Home page
│   ├── globals.css        # Tailwind imports
│   └── api/               # API routes (si necesario)
├── components/            # React components
│   ├── BrandSearch.tsx
│   ├── CompetitorList.tsx
│   ├── CompetitorCard.tsx
│   └── LoadingSpinner.tsx
├── lib/                   # Utilities
│   └── api.ts            # API client
├── public/               # Static assets
├── package.json          # Bun dependencies
├── tailwind.config.ts    # Tailwind config
├── tsconfig.json        # TypeScript config
└── next.config.js       # Next.js config
```

---

## 🎯 Features a Implementar

### Fase 1: MVP (Minimum Viable Product)

1. ✅ **Home Page**
   - Input para buscar marca
   - Botón de búsqueda
   - Loading state
   - Error handling

2. ✅ **Results Display**
   - Lista de competidores HDA
   - Lista de competidores LDA
   - Cards con información básica
   - Links a sitios web

3. ✅ **API Integration**
   - Conectar con `/api/?brand=X`
   - Manejar respuestas
   - Mostrar errores

### Fase 2: Mejoras (Opcional)

- Historial de búsquedas
- Comparación de marcas
- Exportar resultados
- Dark mode
- Responsive design mejorado

---

## 🚀 Pasos de Implementación

### 1. Inicializar Next.js con Bun

```bash
bun create next-app@latest . --typescript --tailwind --app
```

### 2. Configurar Vercel

- Actualizar `vercel.json` para soportar ambos (Python + Next.js)
- Configurar rewrites para API

### 3. Crear Componentes Base

- BrandSearch
- CompetitorList
- CompetitorCard

### 4. Integrar API

- Crear cliente API
- Manejar estados (loading, error, success)

### 5. Styling con Tailwind

- Diseño moderno y limpio
- Responsive
- Animaciones sutiles

---

## 🎨 Diseño UI/UX

### Paleta de Colores

- Primary: Azul moderno
- Success: Verde
- Warning: Amarillo
- Error: Rojo
- Background: Blanco/Gris claro
- Text: Gris oscuro

### Componentes Principales

1. **Search Bar**
   - Input grande y claro
   - Placeholder: "Enter brand name or URL (e.g., 'Nike' or 'nike.com')"
   - Botón de búsqueda destacado

2. **Results Section**
   - Tabs o secciones para HDA/LDA
   - Cards con:
     - Nombre del competidor
     - URL (clickeable)
     - Justificación
     - Badge HDA/LDA

3. **Loading State**
   - Spinner animado
   - Mensaje: "Analyzing competitors..."

4. **Error State**
   - Mensaje claro
   - Botón para reintentar

---

## 📝 Notas Técnicas

### Vercel Configuration

- Next.js se deploya automáticamente
- Python API en `/api/*` se mantiene
- Rewrites para routing correcto

### API Endpoints

- `GET /api/?brand=X` - Escanear competidores
- `GET /api/health` - Health check

### Environment Variables

- `NEXT_PUBLIC_API_URL` - URL del backend (opcional, puede usar relativo)

---

## ✅ Checklist

### Setup

- [ ] Inicializar Next.js con Bun
- [ ] Configurar Tailwind
- [ ] Configurar TypeScript
- [ ] Actualizar vercel.json

### Components

- [ ] BrandSearch component
- [ ] CompetitorList component
- [ ] CompetitorCard component
- [ ] LoadingSpinner component
- [ ] ErrorMessage component

### Integration

- [ ] API client
- [ ] Error handling
- [ ] Loading states
- [ ] Success states

### Styling

- [ ] Base styles
- [ ] Responsive design
- [ ] Animations
- [ ] Dark mode (opcional)

### Testing

- [ ] Test local
- [ ] Test en development
- [ ] Test en staging

---

**Status:** 🚧 En progreso  
**Branch:** `feature/frontend`  
**Next Step:** Inicializar Next.js
