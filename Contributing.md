# Git Conventions — Colibrí Artesano

Este documento define las convenciones de ramas, commits y flujo de trabajo para mantener consistencia en el desarrollo del proyecto.

---

## Flujo de trabajo

- Nunca hacer push directo a `main`
- Todo cambio debe pasar por Pull Request
- Al menos 1 revisión antes de merge
- Resolver conflictos localmente antes de subir
- Mantener ramas pequeñas y enfocadas

---

## Ramas

Formato:

```bash
<tipo>/<id>-<descripcion>
```

### Tipos permitidos

| Tipo | Uso | Ejemplo |
|------|-----|---------|
| feature | Nueva funcionalidad | `feature/12-login-screen` |
| fix | Corrección de errores | `fix/25-navbar-bug` |
| hotfix | Corrección urgente en producción | `hotfix/78-auth-crash` |
| refactor | Mejora interna sin cambiar comportamiento | `refactor/33-auth-service` |
| test | Agregar o mejorar pruebas | `test/44-auth-endpoints` |
| docs | Documentación | `docs/15-api-readme` |
| chore | Configuración o mantenimiento | `chore/50-eslint-config` |

## Reglas

- Usar kebab-case `palabras-separadas-por-guiones`
- Descripciones cortas
- Siempre asociar al issue cuando exista

Correcto:

```bash
feature/12-product-detail
fix/45-search-filter
test/22-auth-api
```

Incorrecto:

```bash
NuevaRama
product-test
feature-login
```

---

## Convención de commits

Formato:

```bash
<tipo>: <descripcion>
```

## Prefijos

| Prefijo | Uso | Ejemplo |
|---------|-----|---------|
| feat: | Nueva funcionalidad | `feat: add login endpoint` |
| fix: | Corrección de error | `fix: resolve token validation bug` |
| test: | Tests | `test: add auth endpoint tests` |
| docs: | Documentación | `docs: update setup guide` |
| chore: | Configuración | `chore: update github actions` |
| refactor: | Mejora interna | `refactor: simplify auth service` |
| style: | Formato/UI sin lógica | `style: adjust login spacing` |

---

# Buenas prácticas de commits

## Hacer commits pequeños y específicos

Correcto:

```bash
feat: create login endpoint
test: add login tests
fix: validate password hashing
```

Incorrecto:

```bash
changes
update
fix stuff
many updates
```

---

## Pull Requests

Formato del título:

```bash
[<tipo>] #<id> descripcion
```

Ejemplo:

```bash
[feature] #12 implement login screen
```

### Debe incluir

- Qué se hizo
- Issue relacionado
- Evidencia visual si aplica
- Checklist de pruebas realizadas

---

## Issues

Todo trabajo debe nacer de un Issue.

Formato:

```bash
[Frontend] Login Screen
[Backend] Product CRUD
[Testing] Auth API Tests
```

Debe incluir:

- Descripción
- Criterios de aceptación
- Responsable
- Labels

---

## Definición de Done

Una tarea se considera terminada cuando:

- Código implementado
- Tests pasan
- No rompe build
- Revisado por al menos 1 compañero
- Merge aprobado
- Issue cerrado

