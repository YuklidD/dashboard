# HaaS Dashboard (Honeypot-as-a-Service)

A research-grade dashboard for deploying, monitoring, and analyzing `sheLLM` honeypots. Supports local simulation and Azure Kubernetes Service (AKS) deployment.

## Features
*   **Honeypot Lifecycle**: Deploy and terminate honeypots (Mock or K8s).
*   **Real-time Observability**: Live WAF bypass alerts and attack traffic monitoring via WebSockets.
*   **Forensics**: View recorded sheLLM sessions and system logs.
*   **RBAC**: Role-based access control (Admin, Analyst, Viewer).

## 🚀 Quick Start (Local Mode)

### Prerequisites
*   Docker & Docker Compose
*   Node.js 18+ (optional, if running frontend locally without Docker)

### 1. Run with Docker Compose (Recommended)
This will start the Backend (FastAPI), Frontend (React), and Database.

```bash
cd /home/howler/dashboard
docker-compose up --build
```

*   **Frontend**: [http://localhost:5173](http://localhost:5173)
*   **Backend API**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Login Credentials
*   **Username**: `admin`
*   **Password**: `admin`

## 🧪 Simulation Mode
When running locally (`ENVIRONMENT=local`), the system automatically starts a **Traffic Simulator**.
*   Go to the **Dashboard** page.
*   You will see "WAF Bypass Detected" alerts appearing automatically every few seconds.
*   This demonstrates the real-time WebSocket integration.

## ☁️ Azure Kubernetes Deployment

1.  **Build Images**:
    ```bash
    az acr build --registry <your_registry> --image haas-backend:latest ./backend
    az acr build --registry <your_registry> --image haas-frontend:latest ./frontend
    ```

2.  **Deploy Manifests**:
    Update `k8s/base/deployment.yaml` with your image names.
    ```bash
    kubectl apply -f k8s/base/
    ```

3.  **Configure Secrets**:
    Ensure `DATABASE_URL` and `SECRET_KEY` are set in K8s secrets.

## 📂 Project Structure
*   `backend/`: FastAPI application (Auth, K8s Orchestrator, Observability).
*   `frontend/`: React + Vite application (Dashboard, Charts, WebSocket Client).
*   `k8s/`: Kubernetes manifests for cloud deployment.
# dashboard
