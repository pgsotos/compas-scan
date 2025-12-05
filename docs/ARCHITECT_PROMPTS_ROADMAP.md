# 🏗️ Architect Prompts Roadmap

This document contains a collection of advanced prompts from a software architect that can be used to enhance code quality, architecture, and development practices in CompasScan.

**Status:** 📋 Future Roadmap (Not Mandatory)

These prompts are recommendations for future improvements and can be referenced when needed. They are not currently enforced as mandatory rules in `.cursorrules`.

---

## 📋 Available Prompts

**Total:** 12 prompts from software architect

### 1. Code Review 🔍

**Prompt:**
```
Revisá este PR buscando:

- Memory leaks y problemas de performance
- Casos borde sin manejar
- Violaciones de principios SOLID
- Inconsistencias con el estilo del repo (adjunto style guide)
```

**Use Case:** When reviewing Pull Requests or code changes, systematically check for performance issues, edge cases, SOLID violations, and style inconsistencies.

**Implementation Notes:**
- Can be integrated into Section 7 (Code Review Protocol)
- Should include specific checks for memory leaks, performance bottlenecks
- SOLID principles verification checklist
- Repository style consistency validation

---

### 2. Migración de Código 🔄

**Prompt:**
```
Migrá este componente de React 18 a React 19:

- Convertí useEffect innecesarios a server components donde corresponda
- Usá las nuevas APIs de React 19 (use, useOptimistic)
- Mantené funcionalidad exacta
- Explicá cada cambio importante
```

**Use Case:** When migrating code between framework versions or major updates.

**Implementation Notes:**
- Framework-specific migration protocols
- Maintain exact functionality during migration
- Document all significant changes
- Test thoroughly after migration

---

### 3. Documentación 📝

**Prompt:**
```
Generá documentación profesional para esta función:

- JSDoc completo (@param, @returns, @throws, @example)
- README con ejemplos de uso
- Diagrama de flujo en Mermaid
- Lista de edge cases cubiertos
```

**Use Case:** When creating or modifying functions, generate professional documentation.

**Implementation Notes:**
- Python: Google-style or NumPy-style docstrings
- TypeScript/JavaScript: JSDoc format
- Include Mermaid diagrams for complex functions
- Document all edge cases

---

### 4. Optimización de Performance ⚡

**Prompt:**
```
Optimizá esta función O(n²):

- Reducir complejidad temporal a O(n) o O(n log n)
- Usar estructuras de datos apropiadas (Set, Map, WeakMap)
- Explicar la ganancia de performance
- Incluir benchmark comparativo simple
```

**Use Case:** When optimizing functions or algorithms for better performance.

**Implementation Notes:**
- Complexity analysis (time/space)
- Appropriate data structure selection
- Performance gain explanation
- Benchmark comparison included

---

### 5. Testing 🧪

**Prompt:**
```
Escribí tests para esta función:

- Unit tests con Jest/Vitest
- Casos de éxito y error
- Edge cases (null, undefined, arrays vacíos, valores límite)
- Mocks para dependencias externas
- Coverage mínimo 80%
- funciones core 100% , 80% en resto, 0% en infra
```

**Use Case:** When writing tests for functions or components.

**Implementation Notes:**
- Python: `pytest` for unit tests
- TypeScript/JavaScript: `Vitest` or `Jest`
- Coverage requirements: 100% core, 80% supporting, 0% infra
- Mock external dependencies

---

### 6. Debugging 🐛

**Prompt:**
```
Cuando encontremos un bug: [describir el comportamiento inesperado]

Analizá:

1. Qué está pasando exactamente
2. Por qué ocurre el bug
3. Cómo solucionarlo
4. Cómo prevenir bugs similares en el futuro
```

**Use Case:** When encountering a bug, follow systematic debugging process.

**Implementation Notes:**
- 4-step framework: What, Why, How to fix, How to prevent
- Use debugging tools (pdb, DevTools, Sentry, Logfire)
- Document bug reports with template
- Add prevention measures

---

### 7. Refactoring General 🔧

**Prompt:**
```
Refactorizá este código aplicando:

1. Principios SOLID
2. Early returns para reducir nesting
3. Extracción de funciones pequeñas y reutilizables
4. Nombres descriptivos para variables y funciones
5. Manejo de errores robusto
6. TypeScript con tipos estrictos
```

**Use Case:** When refactoring code to improve structure and maintainability.

**Implementation Notes:**
- Apply SOLID principles systematically
- Use early returns to reduce nesting
- Extract small, reusable functions
- Descriptive naming conventions
- Robust error handling
- Strict type safety

---

### 8. Seguridad 🔒

**Prompt:**
```
Revisá este código buscando vulnerabilidades:

- Inyección SQL/NoSQL
- XSS (Cross-Site Scripting)
- CSRF
- Exposición de datos sensibles
- Validación de inputs insuficiente
- Dependencias desactualizadas con CVEs conocidos
```

**Use Case:** When reviewing code for security vulnerabilities.

**Implementation Notes:**
- Check for injection attacks (SQL, NoSQL, Command)
- XSS protections (React escaping, DOMPurify)
- CSRF protection for state-changing operations
- Secrets management (never in code/logs)
- Input validation (Pydantic, type guards)
- Dependency vulnerability scanning

---

### 9. API Design 🌐

**Prompt:**
```
Diseñá un endpoint REST para [funcionalidad]:

- Método HTTP correcto
- Path siguiendo convenciones REST
- Request body con validación
- Response con códigos HTTP apropiados
- Manejo de errores consistente
- Documentación OpenAPI/Swagger
```

**Use Case:** When designing REST API endpoints.

**Implementation Notes:**
- Use appropriate HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Follow RESTful path conventions (nouns, plural, kebab-case)
- Validate requests with Pydantic models
- Use appropriate HTTP status codes
- Consistent error handling
- Complete OpenAPI/Swagger documentation

---

### 10. Git / Commits 📝

**Prompt:**
```
Generá un mensaje de commit para estos cambios siguiendo Conventional Commits:

- Tipo: feat/fix/refactor/docs/test/chore
- Scope opcional
- Descripción concisa en imperativo
- Body explicando el "por qué" si es necesario
- Breaking changes si aplica
```

**Use Case:** When generating commit messages.

**Implementation Notes:**
- Follow Conventional Commits format
- Use appropriate type (feat, fix, refactor, etc.)
- Optional scope for module-specific changes
- Imperative mood, concise description
- Body explains "why" for complex changes
- Document breaking changes in footer

---

### 11. Arquitectura 🏗️

**Prompt:**
```
Proponé una arquitectura para [sistema/feature]:

- Diagrama de componentes
- Flujo de datos
- Patrones de diseño a usar
- Consideraciones de escalabilidad
- Trade-offs de cada decisión
- Flujos y diagramas con MERMAID
```

**Use Case:** When proposing architecture for a system or feature.

**Implementation Notes:**
- Create component diagrams (Mermaid)
- Document data flow (sequence diagrams)
- Identify design patterns (Strategy, Repository, Factory, etc.)
- Address scalability (horizontal/vertical)
- Document trade-offs for key decisions
- Use Mermaid for all diagrams

---

### 12. SQL / Queries 🗄️

**Prompt:**
```
Optimizá esta query SQL:

- Reducir tiempo de ejecución
- Usar índices apropiados
- Evitar N+1 queries
- Explicar el plan de ejecución
- Sugerir índices a crear si es necesario
```

**Use Case:** When optimizing SQL queries for better performance.

**Implementation Notes:**
- Analyze query execution time
- Identify missing or inappropriate indexes
- Detect and eliminate N+1 query patterns
- Explain execution plan (EXPLAIN ANALYZE)
- Suggest indexes to create based on query patterns
- Consider query optimization techniques (JOIN optimization, subquery elimination, etc.)

**PostgreSQL Specific:**
- Use `EXPLAIN ANALYZE` to understand execution plan
- Check `pg_stat_statements` for slow queries
- Use appropriate index types (B-tree, Hash, GIN, GiST)
- Consider partial indexes for filtered queries
- Use covering indexes to avoid table lookups

---

## 🎯 How to Use This Roadmap

### For Developers

1. **Reference when needed:** Use these prompts as guidelines when working on specific tasks
2. **Not mandatory:** These are recommendations, not enforced rules
3. **Adapt to context:** Modify prompts based on specific project needs
4. **Gradual adoption:** Consider integrating specific prompts into `.cursorrules` if they become standard practice

### For Code Reviews

- Reference relevant prompts when reviewing code
- Use prompts as checklist items for thorough reviews
- Suggest prompt-based improvements in PR comments

### For Architecture Decisions

- Use Architecture prompt (11) when designing new features
- Document decisions with Mermaid diagrams
- Include trade-offs analysis in design documents

---

## 📊 Integration Status

| Prompt | Status | Priority | Notes |
|--------|--------|----------|-------|
| 1. Code Review | 📋 Future | Medium | Can enhance Section 7 |
| 2. Migration | 📋 Future | Low | Framework-specific |
| 3. Documentation | 📋 Future | High | Already partially in 5.2 |
| 4. Performance | 📋 Future | Medium | Useful for optimization |
| 5. Testing | 📋 Future | High | Can enhance Section 10 |
| 6. Debugging | 📋 Future | High | Useful for bug fixes |
| 7. Refactoring | 📋 Future | Medium | Can enhance Section 12 |
| 8. Security | 📋 Future | High | Critical for production |
| 9. API Design | 📋 Future | Medium | FastAPI-specific |
| 10. Git/Commits | 📋 Future | Low | Already in 2.1 |
| 11. Architecture | 📋 Future | Medium | Useful for new features |
| 12. SQL/Queries | 📋 Future | Medium | PostgreSQL optimization |

---

## 🔄 Future Integration

If any of these prompts prove valuable and become standard practice, they can be:

1. **Integrated into `.cursorrules`** as mandatory sections
2. **Referenced in specific workflows** (e.g., PR templates)
3. **Used as training materials** for new developers
4. **Adapted for project-specific needs**

---

**Last Updated:** 2025-01-XX  
**Maintained by:** Development Team  
**Status:** 📋 Future Roadmap (Not Mandatory)

