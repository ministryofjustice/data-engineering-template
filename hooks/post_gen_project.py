#!/usr/bin/env python
"""Post-generation hook for cookiecutter template.

This script runs after cookiecutter generates a new project and:
1. Renames app stubs to the correct filenames based on project_type
2. Cleans up unused app stubs and batch files
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
        print(f"✅ Renamed app.py.api → app.py")
elif project_type == "dashboard":
    app_stub = src_app / "app.py.dashboard"
    app_target = src_app / "app.py"
    if app_stub.exists():
        shutil.move(str(app_stub), str(app_target))
        print(f"✅ Renamed app.py.dashboard → app.py")

# 2. Clean up unused app stubs
for app_type in ["api", "dashboard"]:
    if app_type != project_type:
        stub = src_app / f"app.py.{app_type}"
        if stub.exists():
            stub.unlink()
            print(f"🗑️  Removed app.py.{app_type} (not needed for {project_type})")

# 3. Remove batch stub (batch projects managed by Analytical Platform)
batch_stub = src_app / "main.py.batch"
if batch_stub.exists():
    batch_stub.unlink()
    print(f"🗑️  Removed main.py.batch (handled by Analytical Platform)")

print("\n✨ Project setup complete!")
print(f"📂 Next: cd {root.name} && uv sync && uv run ...")
