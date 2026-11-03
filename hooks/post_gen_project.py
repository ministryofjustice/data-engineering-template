#!/usr/bin/env python
"""Post-generation hook for cookiecutter template.

This script runs after cookiecutter generates a new project and:
1. Selects the correct ingress.yml and networkpolicy.yml based on project_type
2. Renames app stubs to the correct filenames
3. Cleans up unused files
"""
import os
import shutil
from pathlib import Path

# Get the project root (generated project directory)
root = Path.cwd()
project_type = "{{ cookiecutter.project_type }}"
project_slug = "{{ cookiecutter.project_slug }}"

deployments = root / "deployments" / "templates"
src_app = root / "src" / project_slug

print(f"🔧 Post-generation: Setting up {project_type} project...")

# 1. Select ingress and networkpolicy based on project type
ingress_source = deployments / f"{project_type}-ingress.yml"
networkpolicy_source = deployments / f"{project_type}-networkpolicy.yml"

ingress_target = deployments / "ingress.yml"
networkpolicy_target = deployments / "networkpolicy.yml"

if ingress_source.exists():
    shutil.copy(ingress_source, ingress_target)
    print(f"✅ Copied {project_type}-ingress.yml → ingress.yml")
    ingress_source.unlink()
else:
    print(f"⚠️  {ingress_source} not found")

if networkpolicy_source.exists():
    shutil.copy(networkpolicy_source, networkpolicy_target)
    print(f"✅ Copied {project_type}-networkpolicy.yml → networkpolicy.yml")
    networkpolicy_source.unlink()
else:
    print(f"⚠️  {networkpolicy_source} not found")

# Clean up unused type-specific files
for ptype in ["api", "dashboard"]:
    if ptype != project_type:
        for suffix in ["-ingress.yml", "-networkpolicy.yml"]:
            unused = deployments / f"{ptype}{suffix}"
            if unused.exists():
                unused.unlink()
                print(f"🗑️  Removed {unused.name} (not needed for {project_type})")

# 2. Rename app stubs based on project type
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

# Clean up unused app stubs
for app_type in ["api", "dashboard"]:
    if app_type != project_type:
        stub = src_app / f"app.py.{app_type}"
        if stub.exists():
            stub.unlink()
            print(f"🗑️  Removed app.py.{app_type} (not needed for {project_type})")

# Remove batch stub if it exists (no longer used)
batch_stub = src_app / "main.py.batch"
if batch_stub.exists():
    batch_stub.unlink()
    print(f"🗑️  Removed main.py.batch (batch projects managed by Analytical Platform)")

print("\n✨ Project setup complete!")
print(f"📂 Next: cd {root.name} && uv sync && uv run ...")
