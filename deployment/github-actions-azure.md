# GitHub Actions Azure Deployment

This workflow updates existing Azure resources. Create the Azure resources in
Azure Portal first, then use GitHub Actions for repeat deployments.

Workflow file:

```text
.github/workflows/deploy-azure-container-apps.yml
```

## GitHub Secrets

Add these repository secrets:

```text
AZURE_CLIENT_ID
AZURE_TENANT_ID
AZURE_SUBSCRIPTION_ID
```

These are used by `azure/login` with OpenID Connect.

## GitHub Variables

Add these repository variables:

```text
AZURE_RESOURCE_GROUP
AZURE_ACR_NAME
AZURE_BACKEND_APP
AZURE_FRONTEND_APP
```

Example values:

```text
AZURE_RESOURCE_GROUP=investment-strategy-lab-rg
AZURE_ACR_NAME=investmentstrategylabacr
AZURE_BACKEND_APP=investment-strategy-backend
AZURE_FRONTEND_APP=investment-strategy-frontend
```

## Azure Portal Setup

Create these resources before running the workflow:

```text
Resource Group
Azure Container Registry
Backend Azure Container App
Frontend Azure Container App
```

Set the ports:

```text
Backend target port: 8000
Frontend target port: 8501
```

The frontend app must have this environment variable:

```text
API_BASE_URL=https://your-backend-container-app-url
```

## Run Deployment

Go to GitHub:

```text
Actions -> Deploy to Azure Container Apps -> Run workflow
```

The workflow will:

1. Run tests.
2. Build backend and frontend Docker images in Azure Container Registry.
3. Update the existing backend Container App image.
4. Update the existing frontend Container App image and `API_BASE_URL`.
