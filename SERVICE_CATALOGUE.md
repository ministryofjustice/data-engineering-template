# Service Catalogue Registration

## Overview

The **Service Catalogue** is MoJ's central registry of all services and components.

## How to Register

### Option 1: Developer Portal (Recommended)

**Fastest and easiest method:**

1. Go to [Developer Portal](https://developer-portal.hmpps.service.justice.gov.uk/component-requests/new)
2. Click **New Component**
3. Fill in the form:
   - **Component Name:** Your project name (e.g., `electronic-monitoring-data-dashboard`)
   - **Component Type:** `Data Engineering`, `Data Science`, or `Analytics`
   - **GitHub Repository:** Link to your repo
   - **Team:** Your team name (e.g., `Electronic Monitoring`)
   - **Product ID:** If you have a HMPPS product ID (e.g., `DPS091`), include it
   - **Description:** What your project does
4. Submit
5. Service Catalogue is automatically updated

### Option 2: Manual Request (If Portal Doesn't Support Python)

If the Developer Portal doesn't have a Python category yet:

1. Slack **#ask-prisons-digital-sre** team
2. Provide:
   - Project name
   - GitHub repository URL
   - Team name
   - Project description
   - Product ID (if applicable)
3. SRE will register manually via Service Catalogue API

### Option 3: Service Catalogue API (For Automation)

If you're integrating with other systems:

1. Request **SC_API_KEY** from #ask-prisons-digital-sre
2. Use the [Service Catalogue API](https://service-catalogue.hmpps.service.justice.gov.uk/api-docs)
3. POST to `/components` endpoint with:
   ```json
   {
     "name": "electronic-monitoring-data-dashboard",
     "type": "Data Engineering",
     "github_repo": "https://github.com/ministryofjustice/electronic-monitoring-data-dashboard",
     "team": "Electronic Monitoring",
     "description": "Dashboard for monitoring electronic monitoring data",
     "product_id": "DPS091"
   }
   ```

## Service Metadata to Include

When registering, have this information ready:

| Field | Example | Notes |
|-------|---------|-------|
| Project Name | `electronic-monitoring-data-dashboard` | From your repo name |
| Type | `Data Engineering` | Choose: Data Engineering, Data Science, Analytics, ML, or Other |
| GitHub Repo | `https://github.com/ministryofjustice/...` | Full repo URL |
| Team | `Electronic Monitoring` | Your team name |
| Description | `Dashboard displaying real-time EM data for compliance officers` | 1-2 sentences |
| Product ID | `DPS091` | If you have one; otherwise leave blank |
| Contact Email | `em-team@digital.justice.gov.uk` | For governance inquiries |
| Documentation | `https://github.com/ministryofjustice/.../blob/main/README.md` | Link to main docs |
