# CompasScan - Setup Guide

## 🚀 Configuración del Entorno Virtual

### 1. Crear el Entorno Virtual

```bash
python3 -m venv .venv --prompt compas-scan
```

### 2. Activar el Entorno Virtual

**En macOS/Linux:**
```bash
source .venv/bin/activate
```

**En Windows:**
```bash
.venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Copia el archivo `.env.example` a `.env` y configura tus credenciales:

```bash
cp .env.example .env
```

Edita `.env` con tus API keys:
```
GEMINI_API_KEY=your_gemini_key_here
GOOGLE_API_KEY=your_google_key_here
GOOGLE_CSE_ID=your_cse_id_here
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## ✅ Verificar Instalación

```bash
python test_local.py "Nike"
```

Si todo está correcto, verás:
```
🧪 Testeando el flujo de CompasScan para: Nike
🚀 Iniciando CompasScan 2.0 (AI-First) para: Nike...
🤖 Consultando a Gemini sobre competidores de: Nike...
   ✅ Gemini encontró X candidatos validados.
✨ Usando resultados de Gemini.
✅ TEST COMPLETADO: X HDA, X LDA encontrados.
```

## 🔧 Troubleshooting

### El prompt muestra el nombre incorrecto del proyecto

Si tu terminal muestra un nombre de entorno diferente (ej: "brand-reco"), asegúrate de:

1. Desactivar cualquier entorno anterior:
   ```bash
   deactivate
   ```

2. Eliminar entornos viejos:
   ```bash
   rm -rf .venv venv
   ```

3. Recrear el entorno con el nombre correcto siguiendo los pasos de arriba.

### Comando `python` no encontrado

Prueba con `python3` en lugar de `python`:
```bash
python3 -m venv .venv --prompt compas-scan
```

## 📚 Recursos

- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [Google Gemini API](https://ai.google.dev/)
- [Supabase Docs](https://supabase.com/docs)

