# HaaS Dashboard - System Architecture

## 1. Overview
The Honeypot-as-a-Service (HaaS) Dashboard is a research-grade platform designed to deploy, monitor, and analyze honeypots (specifically `sheLLM`) in both local and cloud (Azure Kubernetes Service) environments. It provides a centralized control plane for managing honeypot lifecycles, viewing real-time attacks, and analyzing session data.

## 2. High-Level Architecture

```mermaid
graph TD
    User[User / Researcher] -->|HTTPS| Frontend[Frontend (React + Vite)]
    Frontend -->|REST API| Backend[Backend (FastAPI)]
    Frontend -->|WebSocket| Backend
    
    subgraph "Control Plane (Local/Cloud)"
        Backend -->|Auth| DB[(Database - SQLite/PostgreSQL)]
        Backend -->|Orchestration| K8sAdapter[K8s Adapter]
    end
    
    subgraph "Infrastructure Layer"
        K8sAdapter -->|Local Mode| MockK8s[Mock Kubernetes Engine]
        K8sAdapter -->|Cloud Mode| RealK8s[Azure Kubernetes Service]
        
        RealK8s -->|Deploys| Pod1[Honeypot Pod (sheLLM)]
        RealK8s -->|Deploys| Pod2[WAF Pod]
    end
    
    subgraph "Observability Pipeline"
        Pod1 -->|Logs/Metrics| Collector[Otel/Prometheus/Loki]
        Collector -->|Query| Backend
    end
```

## 3. Components

### 3.1 Frontend (React + Vite)
*   **Tech Stack**: React, Vite, TailwindCSS, Recharts/Chart.js.
*   **Responsibilities**:
    *   User Interface for dashboard and controls.
    *   Real-time visualization of attacks via WebSockets.
    *   Management of honeypot deployments.
    *   Authentication and Role-Based Access Control (RBAC) UI.

### 3.2 Backend (FastAPI)
*   **Tech Stack**: Python, FastAPI, Pydantic, SQLAlchemy, JWT.
*   **Responsibilities**:
    *   **API Gateway**: Exposes REST endpoints for the frontend.
    *   **Authentication**: Handles user login, JWT issuance, and permission checks.
    *   **Orchestration Engine**: Abstracted service to manage honeypots.
        *   *Local Mode*: Simulates pod creation/deletion in memory.
        *   *Cloud Mode*: Uses `kubernetes` python client to interact with AKS.
    *   **Data Aggregation**: Fetches metrics and logs from observability stores.

### 3.3 Kubernetes Integration Layer
*   **Design**: The backend uses an interface `HoneypotOrchestrator`.
*   **Implementations**:
    *   `MockOrchestrator`: For local development and demos without a cluster. Returns deterministic mock data.
    *   `K8sOrchestrator`: For production. Manages Deployments, Services, and Ingress resources.

### 3.4 Observability & Data
*   **Metrics**: CPU/Memory usage of honeypots, attack counts.
*   **Logs**: Application logs from sheLLM, WAF logs.
*   **Session Recording**: Full TTY session logs from sheLLM interactions.

## 4. Security Boundaries
*   **Frontend-Backend**: Secured via JWT (Access & Refresh tokens).
*   **Backend-K8s**: Uses Kubeconfig (local) or Workload Identity (Azure).
*   **Honeypots**: Isolated in a specific K8s Namespace (`haas-honeypots`) with NetworkPolicies restricting egress.

## 5. Deployment Strategy
*   **Local**: `docker-compose` brings up Frontend, Backend, and DB. K8s is mocked.
*   **Azure**:
    *   Backend/Frontend deployed as K8s services.
    *   Real K8s integration enabled via env vars (`ORCHESTRATOR_TYPE=k8s`).
