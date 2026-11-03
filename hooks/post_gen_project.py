#!/usr/bin/env python
"""Post-generation hook for cookiecutter template.

This script runs after cookiecutter generates a new project and:
1. Renames app stubs to the correct filenames based on project_type
2. Cleans up unused app stubs and files
3. Updates pyproject.toml and test files with type-specific content
"""

import shutil
from pathlib import Path

# Get the project root (generated project directory)
root = Path.cwd()
project_type = "{{ cookiecutter.project_type }}"
project_slug = "{{ cookiecutter.project_slug }}"

src_app = root / "src" / project_slug

print(f"🔧 Post-generation: Setting up {project_type} project...")

# 1. Rename app stubs based on project type
if project_type == "api":
    app_stub = src_app / "app.py.api"
    app_target = src_app / "app.py"
    if app_stub.exists():
        shutil.move(str(app_stub), str(app_target))
        print("✅ Renamed app.py.api → app.py")
elif project_type == "dashboard":
    app_stub = src_app / "app.py.dashboard"
    app_target = src_app / "app.py"
    if app_stub.exists():
        shutil.move(str(app_stub), str(app_target))
        print("✅ Renamed app.py.dashboard → app.py")
elif project_type == "data-pipeline":
    batch_stub = src_app / "main.py.batch"
    main_target = src_app / "main.py"
    if batch_stub.exists():
        shutil.move(str(batch_stub), str(main_target))
        print("✅ Renamed main.py.batch → main.py")

# 2. Clean up unused app stubs (API/Dashboard only)
for app_type in ["api", "dashboard"]:
    stub = src_app / f"app.py.{app_type}"
    if stub.exists():
        stub.unlink()
        print(f"🗑️  Removed app.py.{app_type}")

# 3. Remove batch stub if not data-pipeline
if project_type != "data-pipeline":
    batch_stub = src_app / "main.py.batch"
    if batch_stub.exists():
        batch_stub.unlink()
        print(f"🗑️  Removed main.py.batch (not needed for {project_type})")

# 4. Remove deployments directory for data-pipeline (no Kubernetes needed)
if project_type == "data-pipeline":
    deployments_dir = root / "deployments"
    if deployments_dir.exists():
        shutil.rmtree(deployments_dir)
        print("🗑️  Removed deployments/ (not needed for data-pipeline)")

# 5. Update pyproject.toml with type-specific dependencies
pyproject_path = root / "pyproject.toml"
if pyproject_path.exists():
    content = pyproject_path.read_text()
    if project_type == "api":
        content = content.replace(
            "dependencies = []",
            'dependencies = ["fastapi>=0.115.0", "uvicorn[standard]>=0.30.1"]',
        )
    elif project_type == "dashboard":
        content = content.replace(
            "dependencies = []", 'dependencies = ["streamlit>=1.42.0"]'
        )
    pyproject_path.write_text(content)
    print("✅ Updated pyproject.toml dependencies")

# 6. Clean up test files and update content based on project type
tests_unit_dir = root / "tests" / "unit"
if tests_unit_dir.exists():
    if project_type == "api":
        # API keeps test_app.py, removes test_main.py
        test_main = tests_unit_dir / "test_main.py"
        if test_main.exists():
            test_main.unlink()
            print("🗑️  Removed test_main.py (not needed for api)")
    elif project_type == "dashboard":
        # Dashboard keeps test_main.py as placeholder, removes test_app.py
        test_app = tests_unit_dir / "test_app.py"
        if test_app.exists():
            test_app.unlink()
            print("🗑️  Removed test_app.py (not needed for dashboard)")
    elif project_type == "data-pipeline":
        # Data-pipeline needs test_main.py with proper imports
        test_app = tests_unit_dir / "test_app.py"
        if test_app.exists():
            test_app.unlink()
            print("🗑️  Removed test_app.py (not needed for data-pipeline)")

        # Update test_main.py for data-pipeline with proper imports
        test_main = tests_unit_dir / "test_main.py"
        if test_main.exists():
            test_lines = [
                '"""Unit tests for {{cookiecutter.project_name}}."""',
                "",
                "import logging",
                "",
                "import pytest",
                "",
                f"from {project_slug}.main import main",
                "",
                "",
                "def test_main(caplog: pytest.LogCaptureFixture[str]) -> None:",
                '    """Test main function runs without errors."""',
                "    with caplog.at_level(logging.INFO):",
                "        main()",
                "",
                "    # Check that expected log output is present",
                '    assert any("Job" in record.message for record in caplog.records)',
                '    assert any(record.levelname == "INFO" for record '
                "in caplog.records)",
            ]
            test_main.write_text("\n".join(test_lines) + "\n")
            print("✅ Updated test_main.py for data-pipeline")

print("\n✨ Project setup complete!")
print(f"📂 Next: cd {root.name} && uv sync && uv run ...")
