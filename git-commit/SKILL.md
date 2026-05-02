---
name: git-commit
description: rules for git commit message and PR title
---

Commit messages must be written in English.

Commit messages must follow the Conventional Commits format:

```
<type>(<scope>?): <subject>
```

## Type

* feat: A new feature
* fix: A bug fix
* docs: Documentation changes
* style: Code style changes (no functional impact)
* refactor: Code refactoring (no functional impact)
* test: Adding or updating tests
* chore: Other changes (e.g., build process)

## Scope

Scope is optional. Use only when working with monorepos.
Enter the names of the packages or crates that have been modified.
