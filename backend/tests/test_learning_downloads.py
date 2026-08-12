from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.api.learning import _resolve_download_path


def test_learning_file_download_allows_project_sources() -> None:
    target = _resolve_download_path("learning/examples/01_python_bridge.py")
    assert target.is_file()
    assert target.name == "01_python_bridge.py"
    assert _resolve_download_path("learning/labs/01_market_basics_lab.py").is_file()
    assert _resolve_download_path("learning/datasets/01_market_basics.csv").is_file()
    assert _resolve_download_path(".env.example").name == ".env.example"


@pytest.mark.parametrize(
    "path",
    [
        "credentials.txt",
        "../credentials.txt",
        ".env",
        ".git/config",
        "frontend/node_modules/package.json",
        "frontend/package.json",
        "backend/.env",
    ],
)
def test_learning_file_download_blocks_secrets_and_traversal(path: str) -> None:
    with pytest.raises(HTTPException) as error:
        _resolve_download_path(path)
    assert error.value.status_code == 404
