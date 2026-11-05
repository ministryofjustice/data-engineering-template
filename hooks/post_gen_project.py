#!/usr/bin/env python
# Copyright (c) Ministry of Justice. All rights reserved.
"""Post-generation hook for cookiecutter template.

This script runs after cookiecutter generates a new project and:
1. Renames app stubs to the correct filenames based on project_type
2. Cleans up unused app stubs and files
3. Updates pyproject.toml and test files with type-specific content
"""

import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)
root = Path.cwd()
project_type = "{{ cookiecutter.project_type }}"
project_slug = "{{ cookiecutter.project_slug }}"

src_app = root / "src" / project_slug

logger.info("Post-generation: Setting up %s project...", project_type)

if project_type == "api":
    app_stub = src_app / "app.py.api"
    app_target = src_app / "app.py"
    if app_stub.exists():
        shutil.move(str(app_stub), str(app_target))
        logger.info("Renamed app.py.api → app.py")
elif project_type == "dashboard":
    app_stub = src_app / "app.py.dashboard"
    app_target = src_app / "app.py"
    if app_stub.exists():
        shutil.move(str(app_stub), str(app_target))
        logger.info("Renamed app.py.dashboard → app.py")
elif project_type == "data-pipeline":
    batch_stub = src_app / "main.py.batch"
    main_target = src_app / "main.py"
    if batch_stub.exists():
        shutil.move(str(batch_stub), str(main_target))
        logger.info("Renamed main.py.batch → main.py")

for app_type in ["api", "dashboard"]:
    stub = src_app / f"app.py.{app_type}"
    if stub.exists():
        stub.unlink()
        logger.info("Removed app.py.%s", app_type)

if project_type != "data-pipeline":
    batch_stub = src_app / "main.py.batch"
    if batch_stub.exists():
        batch_stub.unlink()
        logger.info("Removed main.py.batch (not needed for %s)", project_type)

deployments_dir = root / "deployments"
if deployments_dir.exists():
    if project_type == "data-pipeline":
        shutil.rmtree(deployments_dir)
        logger.info("Removed deployments/ (not needed for data-pipeline)")
    else:
        api_dir = deployments_dir / "api"
        dashboard_dir = deployments_dir / "dashboard"

        if project_type == "api" and dashboard_dir.exists():
            shutil.rmtree(dashboard_dir)
            logger.info("Removed deployments/dashboard/ (not needed for api)")
        elif project_type == "dashboard" and api_dir.exists():
            shutil.rmtree(api_dir)
            logger.info("Removed deployments/api/ (not needed for dashboard)")

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
    logger.info("Updated pyproject.toml dependencies")

tests_unit_dir = root / "tests" / "unit"
if tests_unit_dir.exists():
    if project_type == "api":
        # API keeps test_app.py, removes test_main.py
        test_main = tests_unit_dir / "test_main.py"
        if test_main.exists():
            test_main.unlink()
            logger.info("Removed test_main.py (not needed for api)")
    elif project_type == "dashboard":
        test_app = tests_unit_dir / "test_app.py"
        if test_app.exists():
            test_app.unlink()
            logger.info("Removed test_app.py (not needed for dashboard)")
    elif project_type == "data-pipeline":
        test_app = tests_unit_dir / "test_app.py"
        if test_app.exists():
            test_app.unlink()
            logger.info("Removed test_app.py (not needed for data-pipeline)")

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
                (
                    '    assert any(record.levelname == "INFO" for record '
                    "in caplog.records)"
                ),
            ]
            test_main.write_text("\n".join(test_lines) + "\n")
            logger.info("Updated test_main.py for data-pipeline")

logger.info("Project setup complete!")
