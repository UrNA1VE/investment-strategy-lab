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

## Planned Azure Path

1. Push the backend image and frontend image to Azure Container Registry.
2. Deploy both images to Azure Container Apps.
3. Set the frontend container environment variable `API_BASE_URL` to the backend app URL.
4. Add GitHub Actions workflows for CI/CD.

## GitHub Actions

GitHub Actions deployment notes are in:

```text
deployment/github-actions-azure.md
```

The workflow updates existing Azure Container Apps instead of creating cloud
resources automatically. This keeps permissions, cost, and public exposure more
controlled while the project is still in an early portfolio phase.
