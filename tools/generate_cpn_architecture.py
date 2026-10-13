# ruff: noqa: E501

from __future__ import annotations

import argparse
import ast
import shutil
import tempfile
import textwrap
from pathlib import Path

from workflow_architecture import discover_workflow_architecture

parser = argparse.ArgumentParser()
parser.add_argument("--root", type=Path, default=Path.cwd())
parser.add_argument("--check", action="store_true")
arguments = parser.parse_args()
repo = arguments.root.resolve()
src = repo / "src/python/projectkoios/workflow/petrinet/colored"
tests = repo / "tests/projectkoios/workflow/petrinet/colored"
temporary_directory = tempfile.TemporaryDirectory() if arguments.check else None
architecture = (
    Path(temporary_directory.name) / "architecture"
    if temporary_directory is not None
    else repo / "docs/architecture"
)
base_parts = ("projectkoios", "workflow", "petrinet", "colored")
base = architecture.joinpath(*base_parts)
workflow_architecture = discover_workflow_architecture(repo)
if (architecture / "projectkoios").exists():
    shutil.rmtree(architecture / "projectkoios")


def clean_doc(value: str | None) -> str:
    if not value:
        return (
            "The typed source declaration is the authoritative local contract."
        )
    return " ".join(textwrap.dedent(value).strip().split())


def write_trio(
    node: Path, index: str, implementation: str, schematics: str
) -> None:
    node.mkdir(parents=True, exist_ok=True)
    (node / "index.md").write_text(index.rstrip() + "\n")
    (node / "implementation.md").write_text(implementation.rstrip() + "\n")
    (node / "schematics.md").write_text(schematics.rstrip() + "\n")


modules: dict[tuple[str, ...], dict[str, object]] = {}
for source in sorted(src.rglob("*.py")):
    relative = source.relative_to(src)
    raw_parts = relative.with_suffix("").parts
    is_package = raw_parts[-1] == "__init__"
    owner_parts = raw_parts[:-1] if is_package else raw_parts
    tree = ast.parse(source.read_text())
    workflow_module = ".".join(("petrinet", "colored", *owner_parts))
    modules[owner_parts] = {
        "source": source,
        "relative": relative,
        "is_package": is_package,
        "tree": tree,
        "doc": clean_doc(ast.get_docstring(tree)),
        "classes": tuple(
            node for node in tree.body if isinstance(node, ast.ClassDef)
        ),
        "imports": tuple(
            sorted(workflow_architecture[workflow_module].dependencies)
        ),
    }

nodes = {
    ("projectkoios",),
    ("projectkoios", "workflow"),
    ("projectkoios", "workflow", "petrinet"),
    base_parts,
}
for parts in modules:
    full = base_parts + parts
    nodes.update(full[:depth] for depth in range(1, len(full) + 1))

for full in sorted(nodes, key=lambda item: (len(item), item)):
    node = architecture.joinpath(*full)
    dotted = ".".join(full)
    relative_parts = (
        full[len(base_parts) :]
        if full[: len(base_parts)] == base_parts
        else None
    )
    data = modules.get(relative_parts) if relative_parts is not None else None
    children = sorted(
        {
            candidate[len(full)]
            for candidate in nodes
            if len(candidate) > len(full) and candidate[: len(full)] == full
        }
    )
    classes = data["classes"] if data else ()
    child_text = (
        ", ".join(f"`{item}`" for item in children)
        or "no child package or module nodes"
    )
    class_text = (
        ", ".join(f"`{item.name}`" for item in classes)
        or "no directly declared classes"
    )
    purpose = (
        data["doc"]
        if data
        else f"`{dotted}` coordinates the path to the generic colored-Petri-net owner package."
    )
    source_text = (
        f"`{data['source'].relative_to(repo).as_posix()}`"
        if data
        else "namespace composition only"
    )
    imports = (
        ", ".join(f"`{item}`" for item in data["imports"])
        if data and data["imports"]
        else "none at this namespace level"
    )
    index = f"""# `{dotted}`

## Purpose

{purpose}

## Coordination boundary

This node coordinates {child_text} and declares {class_text}. It selects typed
collaborators and preserves dependency direction. It does not resolve payload
bodies, invoke providers, access persistence, or grant execution authority.

## Composition strategy

Composition uses immutable values and identity-bearing operations. Child modules
own their local validation, representation, mapping, linking, or CPN semantics.
This level must not copy domain topology or merge schema admission,
authorization, firing, numerical verification, and scientific validation.

## Source

The production owner is {source_text}. The companion implementation and
schematics documents record dependency rules and composition flow.
"""
    implementation = f"""# `{dotted}` implementation

## Source mapping

Production ownership maps to {source_text}. This documentation mirrors ownership
but is not an alternate API, topology definition, or canonical representation.

## Dependency rule

Direct internal dependencies from the shared repository graph are {imports}.
Dependencies point toward narrower
typed contracts. Parent packages may re-export public contracts but must not
supply compatibility aliases for removed flat modules. The package graph remains
acyclic; this is a source-composition rule, not a workflow DAG restriction.

## Coordination and composition

The node composes children through typed inputs and immutable results. Content
identities are derived by the operation or record that owns their canonical
preimage. Deployment linking stays outside immutable execution-plan semantics.
Static child-plan reference validation does not constrain cyclic CPN topology,
repeated firing, concurrency, retries, or reconciliation.

## Verification

Repository checks require complete architecture trios, Mermaid schematics,
mirrored source ownership, no legacy shim, no package import cycle, strict
mypy, Ruff, pytest, exact provenance, and built-artifact import checks. These
software checks do not authorize provider execution or scientific acceptance.
"""
    edge_lines = [
        f'    owner --> child{index}["{child}"]'
        for index, child in enumerate(children)
    ]
    if not edge_lines:
        edge_lines = [
            '    owner --> contracts["Directly owned class contracts"]'
        ]
    schematics = f"""# `{dotted}` schematics

## Composition map

```mermaid
flowchart TD
    owner["{dotted}"]
{chr(10).join(edge_lines)}
```

Arrows denote ownership and composition, not scheduling or transferred
authority. Each child retains its local invariants.

## Coordination and authority boundary

```mermaid
flowchart LR
    evidence["Domain-authored canonical evidence"] --> owner["{dotted}"]
    owner --> typed["Typed values, findings, and pure operation results"]
    effects["Providers, stores, filesystems, and networks"] -. "excluded" .-> owner
    acceptance["Scientific acceptance and protected authorization"] -. "not granted" .-> owner
```

## Strategy

The package validates bounded inputs, derives content identity, invokes an
explicit semantic operation, and retains correlated output. It does not reduce
CPN execution to a DAG or recursively embed child topology.
"""
    write_trio(node, index, implementation, schematics)


def class_role(name: str, bases: tuple[str, ...]) -> str:
    if name.endswith(
        (
            "Validator",
            "Canonicalizer",
            "Decoder",
            "Parser",
            "Collector",
            "Evaluator",
            "Projector",
            "Constructor",
            "Deriver",
            "Builder",
            "Compiler",
            "Firer",
            "Replayer",
            "Selector",
        )
    ):
        return "an identity-bearing semantic operation"
    if name.endswith(("Error", "Failure")) or any(
        "Error" in base for base in bases
    ):
        return "a closed failure value"
    if name.endswith(("Code", "Kind", "Mode", "Operator", "Policy")) or any(
        "Enum" in base for base in bases
    ):
        return "a closed enumeration"
    if name.endswith("Identity"):
        return "a nominal or content identity value"
    if name.endswith("Input"):
        return "a typed operation input"
    if name.endswith("Result"):
        return "an immutable operation result"
    if name.endswith("Issue"):
        return "a structured validation finding"
    return "an immutable typed contract value"


for parts, data in modules.items():
    if data["is_package"]:
        continue
    module_node = base.joinpath(*parts)
    source = data["source"].relative_to(repo).as_posix()
    for cls in data["classes"]:
        bases = tuple(ast.unparse(base) for base in cls.bases)
        fields = tuple(
            item.target.id
            for item in cls.body
            if isinstance(item, ast.AnnAssign)
            and isinstance(item.target, ast.Name)
        )
        methods = tuple(
            item.name
            for item in cls.body
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            and not item.name.startswith("_")
        )
        role = class_role(cls.name, bases)
        description = clean_doc(ast.get_docstring(cls))
        test_path = tests / f"test__{cls.name}.py"
        if test_path.is_file():
            verification = f"The dedicated class test is `{test_path.relative_to(repo).as_posix()}`."
        else:
            verification = (
                "Behavior is covered by the package test suite; this class has no dedicated "
                "mirrored test file."
            )
        index = f"""# `{cls.name}`

## Purpose

{description}

## Contract role

`{cls.name}` is {role} declared by
`projectkoios.workflow.petrinet.colored.{".".join(parts)}`. Its owner is the
source module, not this documentation or a consuming domain repository.

## Composition boundary

The class composes only declared typed values and operations. It has no implicit
provider, callback, resolver, store, filesystem, network, or scientific-policy
access. Successful use does not grant execution or acceptance authority.

## Composition strategy

Construct the exact type, preserve its derived identities, and pass it only to
operations that declare it in their typed boundary. Do not replace it with an
arbitrary object projector, executable expression, import path, or caller label.
"""
        field_text = (
            ", ".join(f"`{item}`" for item in fields)
            or "no declared dataclass fields"
        )
        method_text = (
            ", ".join(f"`{item}()`" for item in methods)
            or "immutable construction and value access"
        )
        base_text = (
            ", ".join(f"`{item}`" for item in bases) or "no explicit base class"
        )
        implementation = f"""# `{cls.name}` implementation

## Source mapping

The class is defined in `{source}` as {role}. Explicit bases: {base_text}.
Declared fields: {field_text}. Public behavior: {method_text}.

## Invariants and failures

Construction and public methods enforce the exact source checks. Bounded parsing,
canonicalization, validation, mapping, linking, selection, and firing remain
separate concerns. The class must not broaden admitted values through subclass
coercion, executable source, dynamic imports, or ambient services.

## Composition strategy

Use already typed collaborators and retain returned identities or findings for
correlation. Operation identities belong in the applicable execution profile;
content identities derive from complete semantic state. Child-plan reference
cycle checks apply only to static plan containment, never CPN topology.

## Verification

{verification} Package-wide gates additionally check strict typing, Ruff, full
pytest, public nominality, exact provenance, acyclic package imports, and built
artifacts. Passing those gates establishes software verification only.
"""
        schematics = f"""# `{cls.name}` schematics

## Local contract flow

```mermaid
flowchart LR
    typed["Declared typed constructor or operation input"] --> contract["{cls.name}"]
    contract --> retained["Explicit identity, immutable value, finding, or result"]
```

The arrows show typed data composition, not runtime scheduling.

## Coordination and authority boundary

```mermaid
flowchart TB
    collaborators["Declared typed collaborators"] --> contract["{cls.name}"]
    canonical["Bounded canonical data"] --> contract
    callbacks["Callbacks and dynamic imports"] -. "excluded" .-> contract
    effects["Providers, stores, filesystems, and networks"] -. "excluded" .-> contract
    science["Scientific acceptance or execution authorization"] -. "not granted" .-> contract
```

## Ownership

`{cls.name}` owns only its source-declared behavior. Coordinators may correlate
it with other contracts but cannot copy its semantics, recursively inline child
topology, or infer authorization from successful construction.
"""
        write_trio(module_node / cls.name, index, implementation, schematics)

node_count = sum(1 for _ in (architecture / "projectkoios").rglob("index.md"))
if arguments.check:
    expected = repo / "docs/architecture/projectkoios"
    generated = architecture / "projectkoios"
    expected_files = {
        path.relative_to(expected): path.read_bytes()
        for path in expected.rglob("*")
        if path.is_file()
    }
    generated_files = {
        path.relative_to(generated): path.read_bytes()
        for path in generated.rglob("*")
        if path.is_file()
    }
    temporary_directory.cleanup()
    if expected_files != generated_files:
        raise SystemExit("stale generated CPN architecture documentation")
else:
    print(node_count, "nodes")
