# Contributor Guidance for AHFT

This file defines basic rules for working with the AHFT repository. Follow these
instructions whenever you submit changes.

## Pine Script Style

- All `.pine` files must begin with `//@version=5` as the very first line.
- Indentation is four spaces. Do not use curly braces for control blocks.
- Each statement performs a single operation. Use `:=` only for reassignment.
- Declare variables once near the top of the script. Functions must be declared
  at global scope.
- Keep the ordering: Inputs → Global Vars → Core Calculations → Functions →
  Execution logic.
- These rules are summarized in the **Immutable Coding Constitution** within
  `docs/PROJECT.md`. Any Pine code should adhere to that document.

## Documentation

- Keep `README.md` concise. Detailed explanations belong in `docs/`.
- Wrap lines at roughly 80 characters and use standard Markdown.

## Pull Request Checklist

- Provide a short description of the changes and affected files.
- Include a **Testing** section showing:
  1. `git status --short`
  2. `git log -1 --stat`
- Use file citations when referencing code or documentation lines, and terminal
  citations for command outputs.

