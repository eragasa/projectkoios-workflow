### CP-005: PEP 8 compliant, fully documented public code

All committed Python code should be PEP 8 compliant.

Public modules, classes, functions, methods, and command-line entry points should be documented.

Documentation must explain:

- what the object/function does
- what inputs mean
- what outputs mean
- what exceptions may be raised
- whether the function mutates state
- whether the function performs I/O
- whether the function is part of the public API

Private helpers may have shorter documentation, but must still be understandable when they encode nontrivial logic.

Use docstrings for public Python objects.

Use comments only to explain why something is done, not to restate what the code already says.
```

I would also split **style compliance** and **documentation compliance**, because they are different review concerns.

```md
### CP-005: PEP 8 style compliance

Python code must follow PEP 8 style conventions.

Formatting, imports, naming, and line length should be enforced with project tooling where possible.

Recommended tools:

- `ruff` for linting
- `ruff format` or `black` for formatting
- `mypy` or `pyright` for type checking
- `pytest` for tests

The review agent should not manually argue about formatting if tooling can enforce it.

### CP-006: Public code documentation

All public modules, classes, functions, methods, and CLI commands must have docstrings.

Docstrings should describe behavior, parameters, return values, raised exceptions, side effects, and important invariants.

The required documentation level depends on visibility:

| code type | documentation requirement |
|---|---|
| public module | module docstring required |
| public class | class docstring required |
| public function/method | function docstring required |
| private helper | docstring required only if logic is nontrivial |
| test function | descriptive test name usually sufficient |
| architecture-sensitive code | docstring or comment explaining the invariant |
| adapter code | docstring must identify the external dependency and boundary |
```

For your `principles.md`, I would revise the code section to this:

```md
## Code principles

### CP-001: Public API first

Tests should primarily exercise public behavior.

### CP-002: Explicit mutation

Mutating functions should be named and typed clearly.

Good:

`dry_run()`

`fire()`

`commit()`

Bad:

`process()`

`resolve()`

`update_everything()`

### CP-003: Thin adapters

External libraries belong behind adapters.

### CP-004: Test invariants

Tests should check important invariants:

- dry-run does not mutate state
- disabled actions cannot fire
- core does not import UI
- core does not import Petri-net backends
- successful action produces provenance

### CP-005: PEP 8 style compliance

Python code must follow PEP 8 style conventions.

Formatting, imports, naming, and line length should be enforced with tooling where possible.

Preferred tools:

- `ruff`
- `ruff format`
- `mypy` or `pyright`
- `pytest`

The review should not spend human attention on formatting issues that tooling can fix automatically.

### CP-006: Public code documentation

All public modules, classes, functions, methods, and CLI entry points must have docstrings.

Docstrings should explain:

- purpose
- parameters
- return values
- raised exceptions
- side effects
- mutation behavior
- I/O behavior
- important invariants

Private helpers may have shorter documentation, but nontrivial private logic must still be documented.

### CP-007: Type annotations

Public functions and methods should have explicit type annotations.

Schema objects, workflow objects, action objects, and adapter boundaries should be typed.

Avoid untyped dictionaries for domain objects when a typed model would clarify the boundary.

### CP-008: Examples for public APIs

Important public APIs should include either:

- a docstring example
- a test that functions as an executable example
- a short usage note in documentation

For Project Koios, tests are preferred as executable documentation.
```

And add this to `review.md`:

```md
### C5: PEP 8 compliance

Result: pass / concern / fail / unknown

Evidence:

Tool result:

Required change:

### C6: Documentation completeness

Result: pass / concern / fail / unknown

Evidence:

Missing docstrings:

Missing parameter documentation:

Missing return-value documentation:

Missing side-effect documentation:

Required change:

### C7: Type annotations

Result: pass / concern / fail / unknown

Evidence:

Missing or weak annotations:

Required change:
```

The agent prompt should include this rule:

```md
## Documentation and style rules

Check whether Python code is PEP 8 compliant.

Check whether public modules, classes, functions, methods, and CLI entry points are documented.

Check whether docstrings identify mutation, I/O, exceptions, parameters, return values, and invariants.

Prefer automated tooling for formatting and linting. Do not produce excessive review comments for issues that `ruff` or a formatter can fix.

Flag missing documentation only when the code is public, architecture-sensitive, mutating, adapter-facing, or nontrivial.
```

Minimal tool setup:

```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
se[118;1:3ulect = [
    "E",
    "F",
    "I",
    "N",
    "D",
    "UP",
    "B",
    "SIM",
]

ignore = [
    "D203",
    "D213",
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

This gives you:

```text
PEP 8 style
import sorting
naming checks
docstring checks
basic bug-risk checks
modern Python suggestions
```

For documentation, use this as the default docstring style:

```python
def dry_run(self, state: WorkflowState, action_id: ActionId) -> DryRunResult:
    """Evaluate an action without mutating workflow state.

    Parameters
    ----------
    state
        Current workflow state.
    action_id
        Identifier of the action to evaluate.

    Returns
    -------
    DryRunResult
        Proposed state delta, failed guards, required permissions, and
        provenance preview.

    Raises
    ------
    UnknownActionError
        If `action_id` is not defined in the workflow specification.

    Notes
    -----
    This method must not mutate `state`.
    """
```

So the simple rule is:

```text
PEP 8 is enforced by tooling.
Documentation is enforced by review.
Architecture-sensitive behavior must be documented explicitly.
