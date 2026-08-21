# Deployment

This folder contains the local Docker setup for running the app as two services.

## Services

- `backend`: FastAPI API service on container port `8000`
- `frontend`: Streamlit web UI on container port `8501`

The Streamlit container calls the backend through this internal Docker URL:

```text
http://backend:8000
```

## Run Locally With Docker

From the project root:

```bash
docker compose -f deployment/docker-compose.yml up --build
```

Then open:

```text
http://127.0.0.1:8501
```

The backend API is available at:

```text
http://127.0.0.1:8000
```

If ports `8000` or `8501` are already in use, run with custom host ports:

```bash
BACKEND_PORT=8001 FRONTEND_PORT=8502 docker compose -f deployment/docker-compose.yml up --build
```

Then open:

```text
http://127.0.0.1:8502
```

## Azure Resources

The project has been deployed with these Azure resources:

- Resource group: `portfolio-rg`
- Azure Container Registry: `qkwinvestmentlabacr`
- Backend Container App: `investment-strategy-backend`
- Frontend Container App: `investment-strategy-frontend`
- Container Apps Environment: `managedEnvironment-portfoliorg-b59e`

## GitHub Actions

GitHub Actions deployment notes are in:

```text
deployment/github-actions-azure.md
```

The workflow updates existing Azure Container Apps instead of creating cloud
resources automatically. It builds backend and frontend Docker images, pushes
them to Azure Container Registry, and updates the existing Container Apps.
