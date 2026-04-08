"""
Tests for packaging and container runtime dependency contracts.

These checks prevent deployment-time failures where the actor starts
without required SDK modules available in the runtime image.
"""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_installs_requirements_txt() -> None:
    """Docker image must install Python dependencies from requirements.txt."""
    dockerfile = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "requirements.txt" in dockerfile
    assert "pip install" in dockerfile
    assert "-r requirements.txt" in dockerfile


def test_requirements_use_pydantic_compatible_with_apify() -> None:
    """Pinned pydantic range must be compatible with modern apify SDK."""
    requirements = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "apify>=3.0.0,<4.0.0" in requirements
    assert "pydantic>=2.11.0,<3.0.0" in requirements


def test_pyproject_dependencies_match_runtime_constraints() -> None:
    """Project metadata should mirror runtime dependency constraints."""
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert '"apify>=3.0.0,<4.0.0"' in pyproject
    assert '"pydantic>=2.11.0,<3.0.0"' in pyproject
