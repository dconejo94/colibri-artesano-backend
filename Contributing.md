# Git Conventions — Colibrí Artesano

This document defines the conventions for branches, commits, and workflow to maintain consistency in project development.

---

## Workflow

- Never push directly to `main`
- All changes must go through a Pull Request
- At least 1 review before merging
- Resolve conflicts locally before pushing
- Keep branches small and focused

---

## Branches

Format:

```bash
<type>/<id>-<description>
```

### Allowed types

| Type     | Usage                                         | Example                    |
| -------- | --------------------------------------------- | -------------------------- |
| feature  | New functionality                             | `feature/12-login-screen`  |
| fix      | Bug fixes                                     | `fix/25-navbar-bug`        |
| hotfix   | Urgent production fix                         | `hotfix/78-auth-crash`     |
| refactor | Internal improvement without behavior changes | `refactor/33-auth-service` |
| test     | Add or improve tests                          | `test/44-auth-endpoints`   |
| docs     | Documentation                                 | `docs/15-api-readme`       |
| chore    | Configuration or maintenance tasks            | `chore/50-eslint-config`   |


## Rules

- Use kebab-case (words-separated-by-dashes)
- Keep descriptions short
- Always associate with an issue when it exists

Correcto:

```bash
feature/12-product-detail
fix/45-search-filter
test/22-auth-api
```

Incorrecto:

```bash
NewBranch
product-test
feature-login
```

---

## Commit Convention

Format:

```bash
<type>: <description>
```

## Prefixes

| Prefix    | Usage                               | Example                             |
| --------- | ----------------------------------- | ----------------------------------- |
| feat:     | New feature                         | `feat: add login endpoint`          |
| fix:      | Bug fix                             | `fix: resolve token validation bug` |
| test:     | Tests                               | `test: add auth endpoint tests`     |
| docs:     | Documentation                       | `docs: update setup guide`          |
| chore:    | Configuration                       | `chore: update github actions`      |
| refactor: | Internal improvement                | `refactor: simplify auth service`   |
| style:    | Formatting/UI without logic changes | `style: adjust login spacing`       |


---

# Good commit practices

## Make small and specific commits

Correct:

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

Title format

```bash
[<type>] #<id> description
```

Ejemplo:

```bash
[feature] #12 implement login screen
```

### Must include

- What was done
- Related issue
- Visual evidence if applicable

---

## Issues

All work must start from an Issue.

Format:

```bash
[Frontend] Login Screen
[Backend] Product CRUD
[Testing] Auth API Tests
```

Must include

- Description
- Acceptance criteria
- Responsible person

---

## Definition of Done

A task is considered complete when:

- Code implemented
- Tests pass
- No build breaks
- Reviewed by at least 1 teammate
- Merge approved
- Issue closed

