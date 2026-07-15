# Online Integration Guide

This project has two online modes:

1. Streamlit web app for business users (UI mode).
2. FastAPI backend for system-to-system integration (API mode).

## 1) Install dependencies

```bash
pip install -r requirements.txt
```

## 2) Run UI locally (what users already see)

```bash
streamlit run app.py
```

## 3) Run API locally

```bash
uvicorn online_api:app --host 0.0.0.0 --port 8000 --reload
```

Open:
- http://localhost:8000
- http://localhost:8000/docs

## 4) Endpoints

- GET /health
  - Health check.

- POST /map/fields
  - JSON in, JSON out.
  - Use this when your frontend already has parsed field metadata.

Example request:

```json
{
  "source_metadata": [
    {"field": "ClientId", "description": "Customer identifier"},
    {"field": "WorkerId", "description": "Employee identifier"}
  ],
  "target_metadata": [
    {"field": "CustomerAccount", "description": "Customer number"},
    {"field": "EmployeeResponsibleNumber", "description": "Worker number"}
  ]
}
```

- POST /map/files
  - Multipart in, ZIP out.
  - Upload source_file (xlsx/csv/txt) and target_file (xlsx).
  - Returns Mapping_Output.zip containing:
    - Mapped_Target_Metadata.xlsx
    - Mapping_Audit_Report.xlsx
    - Summary.json

## 5) Make it AI-like in frontend

Use this flow:
1. User uploads source and target metadata.
2. Frontend calls POST /map/files.
3. Show progress indicator.
4. Display summary from Summary.json.
5. Allow download of mapped workbook and audit report.

## 6) Deploy for end users (recommended)

Use Streamlit UI mode for business users, then share one URL.

### Option A: Render (quickest)

This repo now includes Docker and Render config:
- Dockerfile
- render.yaml
- .streamlit/config.toml

Steps:
1. Push this project to GitHub.
2. Log in to Render and create a new Blueprint service.
3. Select your repository. Render will detect render.yaml automatically.
4. Deploy.
5. Share the generated HTTPS URL with users.

### Option B: Azure App Service (if your company uses Azure)

1. Build and push Docker image from this repo.
2. Create Azure Web App for Containers.
3. Set container port to 8501.
4. Add environment variable PORT=8501 if needed.
5. Share the app URL with users.

## 7) Security and enterprise readiness checklist

1. Put app behind SSO (Azure AD / Entra ID) using your platform auth.
2. Add upload size and file type validation (already partially enforced).
3. Restrict CORS for API mode in production.
4. Enable HTTPS only.
5. Store logs and outputs in managed storage if audit retention is required.

## 8) Production startup commands

For UI mode (users):

```bash
streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT
```

For API mode (integration):

```bash
uvicorn online_api:app --host 0.0.0.0 --port $PORT
```
