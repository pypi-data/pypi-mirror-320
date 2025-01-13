from pathlib import Path
from typing import Any, Dict, Optional, Set, TypedDict

from tomlkit import load


def get_package_root(cwd: Optional[Path] = None) -> Path:
    # traverse path for routes to host (any directory holding a pyproject.toml file)
    package_root = Path.cwd() if cwd is None else cwd
    visited: Set[Path] = set()
    while package_root not in visited:
        visited.add(package_root)

        pyproject_path = package_root / "pyproject.toml"
        if pyproject_path.exists():
            return package_root
        package_root = package_root.parent
    raise FileNotFoundError("No pyproject.toml found")


class aiagentsforceapiExport(TypedDict):
    """
    Fields from pyproject.toml that are relevant to aiagentsforceapi

    Attributes:
        module: The module to import from, tool.aiagentsforceapi.export_module
        attr: The attribute to import from the module, tool.aiagentsforceapi.export_attr
        package_name: The name of the package, tool.poetry.name
    """

    module: str
    attr: str
    package_name: str


def get_aiagentsforceapi_export(filepath: Path) -> aiagentsforceapiExport:
    with open(filepath) as f:
        data: Dict[str, Any] = load(f)
    try:
        module = data["tool"]["aiagentsforceapi"]["export_module"]
        attr = data["tool"]["aiagentsforceapi"]["export_attr"]
        package_name = data["tool"]["poetry"]["name"]
    except KeyError as e:
        raise KeyError("Invalid aiagentsforceapi PyProject.toml") from e
    return aiagentsforceapiExport(module=module, attr=attr, package_name=package_name)
