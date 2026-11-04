# Data Engineering Template - Cookiecutter
---

## Quick Start

### 1. Create your project

```bash
uvx cookiecutter https://github.com/ministryofjustice/data-engineering-template
```

Answer the interactive prompts:
```
project_name [My Project]: hmpps-electronic-monitoring-data-dashboard
project_description: Display live EM cases on a dashboard
project_type (api/dashboard) [api]: dashboard
python_version (3.13/3.14) [3.14]: 3.14
```

### 2. Install and run

```bash
cd hmpps-electronic-monitoring-data-dashboard
uv sync

uv run fastapi dev src/hmpps_electronic_monitoring_data_dashboard/app.py
```

Visit **http://localhost:8000** to see your project running.
