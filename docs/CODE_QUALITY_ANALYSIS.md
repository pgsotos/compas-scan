# 🔍 Análisis de Calidad de Código - CompasScan

## 📊 Resumen Ejecutivo

**Archivo más grande:** `api/compas_core.py` (381 líneas)

**Problemas identificados:**
- ✅ **Bueno:** Separación de responsabilidades en módulos
- ⚠️ **Mejorable:** Funciones largas con múltiples responsabilidades
- ⚠️ **Mejorable:** Lógica compleja anidada
- ⚠️ **Mejorable:** Queries hardcodeadas

---

## 🚨 Problemas Detectados

### 1. `run_compas_scan()` - Función Monolítica

**Ubicación:** `api/compas_core.py:282-381` (100 líneas)

**Problemas:**
- ❌ **Múltiples responsabilidades:** Orquesta todo el flujo de escaneo
- ❌ **Lógica compleja anidada:** Búsqueda inicial, directa, clasificación todo mezclado
- ❌ **Queries hardcodeadas:** Línea 312-317 tiene queries estáticas
- ❌ **Difícil de testear:** Muchas dependencias y flujos

**Código actual:**
```python
async def run_compas_scan(user_input: str) -> ScanReport:
    # 1. Contexto
    # 2. Gemini
    # 3. Fallback web (búsqueda inicial)
    # 4. Búsqueda directa
    # 5. Clasificación
    # 6. Resultados
```

**Refactor sugerido:**
```python
async def run_compas_scan(user_input: str) -> ScanReport:
    context = await get_brand_context(user_input)
    
    # Try AI first
    ai_result = await _try_ai_strategy(context)
    if ai_result:
        return ai_result
    
    # Fallback to web search
    return await _web_search_strategy(context)

async def _try_ai_strategy(context: BrandContext) -> Optional[ScanReport]:
    """Estrategia AI-First con Gemini."""
    
async def _web_search_strategy(context: BrandContext) -> ScanReport:
    """Estrategia de búsqueda web con clasificación."""
    
async def _search_initial_candidates(context: BrandContext) -> list[CompetitorCandidate]:
    """Búsqueda inicial concurrente."""
    
async def _search_direct_competitors(names: set[str]) -> list[CompetitorCandidate]:
    """Búsqueda directa de competidores descubiertos."""
    
def _classify_all_candidates(candidates: list[CompetitorCandidate], context: BrandContext) -> ScanReport:
    """Clasifica todos los candidatos y retorna ScanReport."""
```

---

### 2. `classify_competitor()` - Lógica Compleja

**Ubicación:** `api/compas_core.py:226-279` (54 líneas)

**Problemas:**
- ⚠️ **Múltiples fases mezcladas:** Descartar, analizar señales, clasificar
- ⚠️ **Lógica anidada:** Múltiples if/elif anidados
- ⚠️ **Hardcoded values:** `industry_terms` hardcodeado (línea 261)

**Refactor sugerido:**
```python
def classify_competitor(candidate: CompetitorCandidate, brand_context: BrandContext) -> ClassificationResult:
    # Fase 1: Quick rejection
    if _should_reject_candidate(candidate):
        return ClassificationResult(valid=False, reason=_get_rejection_reason(candidate))
    
    # Fase 2: Signal analysis
    signals = _analyze_signals(candidate, brand_context)
    
    # Fase 3: Classification
    return _determine_classification(signals)

def _should_reject_candidate(candidate: CompetitorCandidate) -> bool:
    """Quick rejection checks."""
    
def _analyze_signals(candidate: CompetitorCandidate, context: BrandContext) -> list[str]:
    """Analyze all signals for classification."""
    
def _determine_classification(signals: list[str]) -> ClassificationResult:
    """Determine HDA/LDA based on signals."""
```

---

### 3. `get_brand_context()` - Múltiples Responsabilidades

**Ubicación:** `api/compas_core.py:47-97` (51 líneas)

**Problemas:**
- ⚠️ **Mezcla detección y extracción:** URL detection + keyword extraction
- ⚠️ **Lógica de fallback mezclada:** Búsqueda de sitio oficial dentro de la función

**Refactor sugerido:**
```python
async def get_brand_context(user_input: str) -> BrandContext:
    cached = await cache.get_brand_context(user_input)
    if cached:
        return BrandContext(**cached)
    
    # Separate concerns
    url = await _detect_or_find_url(user_input)
    name = _extract_name_from_input(user_input, url)
    keywords = await _extract_keywords(url, name)
    
    context = BrandContext(name=name, url=url, keywords=keywords)
    await cache.set_brand_context(user_input, context.model_dump())
    return context

async def _detect_or_find_url(user_input: str) -> str:
    """Detect URL or search for official site."""
    
def _extract_name_from_input(user_input: str, url: str) -> str:
    """Extract brand name from input or URL."""
    
async def _extract_keywords(url: str, name: str) -> list[str]:
    """Extract keywords from website."""
```

---

### 4. Queries Hardcodeadas

**Ubicación:** `api/compas_core.py:312-317`

**Problema:**
```python
queries = [
    f"related:{get_root_domain(context.url)}",
    f"similar brands to {context.name}",
    f"{context.name} competitors",
    f"streaming services like {context.name}",  # ⚠️ Hardcoded "streaming"
]
```

**Solución:**
```python
def _generate_search_queries(context: BrandContext) -> list[str]:
    """Generate dynamic search queries based on brand context."""
    base_queries = [
        f"related:{get_root_domain(context.url)}",
        f"similar brands to {context.name}",
        f"{context.name} competitors",
    ]
    
    # Dynamic industry-specific query
    if context.keywords:
        industry = context.keywords[0] if context.keywords else "service"
        base_queries.append(f"{industry} services like {context.name}")
    
    return base_queries
```

---

## 📈 Métricas de Complejidad

| Función | Líneas | Complejidad | Responsabilidades |
|---------|--------|-------------|-------------------|
| `run_compas_scan` | 100 | Alta | 5+ |
| `classify_competitor` | 54 | Media-Alta | 3 |
| `get_brand_context` | 51 | Media | 3 |
| `search_web` | 74 | Media | 2 |

**Recomendación:** Funciones deberían tener < 50 líneas y < 3 responsabilidades.

---

## ✅ Buenas Prácticas Encontradas

1. ✅ **Separación de módulos:** Cada módulo tiene responsabilidad clara
2. ✅ **Type hints:** Todo el código tiene type hints
3. ✅ **Pydantic models:** Validación estricta de datos
4. ✅ **Async/await:** Uso correcto de async
5. ✅ **Error handling:** Try/catch apropiados
6. ✅ **Caching:** Implementado correctamente

---

## 🎯 Plan de Refactorización

### Prioridad Alta
1. **Refactorizar `run_compas_scan()`**
   - Dividir en funciones más pequeñas
   - Separar estrategia AI de Web
   - Extraer queries a función helper

### Prioridad Media
2. **Refactorizar `classify_competitor()`**
   - Separar fases en funciones helper
   - Mover `industry_terms` a constants

3. **Refactorizar `get_brand_context()`**
   - Separar detección de URL
   - Separar extracción de keywords

### Prioridad Baja
4. **Mejorar queries dinámicas**
   - Generar queries basadas en contexto
   - Eliminar hardcoding de "streaming"

---

## 📝 Notas

- El código **NO es espaguetti crítico**, pero tiene oportunidades de mejora
- La estructura general es buena (módulos separados)
- Las funciones largas son el principal problema
- La refactorización mejoraría testabilidad y mantenibilidad

---

**Última actualización:** $(date)

