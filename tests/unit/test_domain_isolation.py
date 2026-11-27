"""Architecture guard: the domain layer must stay free of web/DB/template frameworks."""

import ast
from pathlib import Path

DOMAIN_DIR = Path(__file__).resolve().parents[2] / "app" / "domain"
FORBIDDEN = ("fastapi", "starlette", "sqlalchemy", "jinja2", "app.models", "app.database", "app.routers")


def test_domain_modules_do_not_import_frameworks() -> None:
    offenders: list[str] = []
    for path in DOMAIN_DIR.glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            offenders += [f"{path.name}: {n}" for n in names if n.startswith(FORBIDDEN)]
    assert offenders == []
