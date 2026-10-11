from __future__ import annotations

import ast
from pathlib import Path

import pytest

TRIO = {"implementation.md", "index.md", "schematics.md"}
SOURCE_PATH = Path("src/python/projectkoios/workflow/petrinet/colored")
ARCHITECTURE_PATH = Path("docs/architecture")
COLORED_DOCUMENTATION_PATH = Path(
    "docs/architecture/projectkoios/workflow/petrinet/colored"
)


def _source_owner_parts(path: Path, source_root: Path) -> tuple[str, ...]:
    parts = path.relative_to(source_root).with_suffix("").parts
    return parts[:-1] if parts[-1] == "__init__" else parts


def test_artifact__architecture_documentation__mirrors_every_owner_node(
    pytestconfig: pytest.Config,
) -> None:
    repository_root = pytestconfig.rootpath
    source_root = repository_root / SOURCE_PATH
    architecture_root = repository_root / ARCHITECTURE_PATH
    colored_documentation_root = repository_root / COLORED_DOCUMENTATION_PATH
    ancestor_nodes = {
        architecture_root / "projectkoios",
        architecture_root / "projectkoios/workflow",
        architecture_root / "projectkoios/workflow/petrinet",
    }
    expected = ancestor_nodes | {colored_documentation_root}
    package_prefix = ("projectkoios", "workflow", "petrinet", "colored")

    for source_path in source_root.rglob("*.py"):
        owner_parts = _source_owner_parts(source_path, source_root)
        for depth in range(len(owner_parts) + 1):
            expected.add(
                architecture_root / Path(*package_prefix, *owner_parts[:depth])
            )
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        module_node = architecture_root / Path(*package_prefix, *owner_parts)
        expected.update(
            module_node / node.name
            for node in tree.body
            if isinstance(node, ast.ClassDef)
        )

    actual = ancestor_nodes | {
        path.parent for path in colored_documentation_root.rglob("index.md")
    }
    assert actual == expected

    for node in actual:
        documents = {path.name for path in node.glob("*.md")}
        assert documents == TRIO, node
        for filename in TRIO:
            text = (node / filename).read_text(encoding="utf-8")
            assert text.startswith("# "), node / filename
            assert "\n## " in text, node / filename
            assert len(text.strip()) >= 300, node / filename


def test_artifact__package_documentation__states_coordination_and_composition(
    pytestconfig: pytest.Config,
) -> None:
    repository_root = pytestconfig.rootpath
    source_root = repository_root / SOURCE_PATH
    architecture_root = repository_root / ARCHITECTURE_PATH
    colored_documentation_root = repository_root / COLORED_DOCUMENTATION_PATH
    class_names = {
        node.name
        for source_path in source_root.rglob("*.py")
        for node in ast.parse(source_path.read_text(encoding="utf-8")).body
        if isinstance(node, ast.ClassDef)
    }
    package_indexes = (
        architecture_root / "projectkoios/index.md",
        architecture_root / "projectkoios/workflow/index.md",
        architecture_root / "projectkoios/workflow/petrinet/index.md",
        *colored_documentation_root.rglob("index.md"),
    )
    for index in package_indexes:
        if index.parent.name in class_names:
            continue
        text = index.read_text(encoding="utf-8").lower()
        assert "coordination boundary" in text, index
        assert "composition strategy" in text, index


def test_artifact__class_documentation__binds_source_test_and_authority_boundary(
    pytestconfig: pytest.Config,
) -> None:
    repository_root = pytestconfig.rootpath
    source_root = repository_root / SOURCE_PATH
    colored_documentation_root = repository_root / COLORED_DOCUMENTATION_PATH
    for source_path in source_root.rglob("*.py"):
        owner_parts = _source_owner_parts(source_path, source_root)
        module_node = colored_documentation_root.joinpath(*owner_parts)
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            class_node = module_node / node.name
            implementation = (class_node / "implementation.md").read_text(
                encoding="utf-8"
            )
            schematic = (class_node / "schematics.md").read_text(
                encoding="utf-8"
            )
            assert (
                source_path.relative_to(repository_root).as_posix()
                in implementation
            )
            mirrored_test = (
                repository_root
                / "tests/projectkoios/workflow/petrinet/colored"
                / f"test__{node.name}.py"
            )
            if mirrored_test.is_file():
                assert mirrored_test.name in implementation
            else:
                assert "no dedicated mirrored test file" in implementation
            assert "software verification only" in " ".join(
                implementation.split()
            )
            assert schematic.count("```mermaid") >= 2
            assert "excluded" in schematic
            assert "Scientific acceptance" in schematic
