# hng14-stage2-devops

A containerised job processing system built as part of the HNG14 DevOps Stage 2 task. The stack consists of four services:

- **frontend** — Node.js/Express UI for submitting and tracking jobs
- **api** — Python/FastAPI service that creates jobs and serves status updates
- **worker** — Python service that picks up jobs from the queue and processes them
- **redis** — Shared message queue and job state store

---

## Prerequisites

Make sure the following are installed on your machine before proceeding:

| Tool | Version | Install |
|------|---------|---------|
| Docker | 24+ | https://docs.docker.com/get-docker |
| Docker Compose | v2 (bundled with Docker Desktop) | https://docs.docker.com/compose/install |
| Git | any | https://git-scm.com |

Verify your setup:
```bash
docker --version
docker compose version
git --version
```

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Masterpitan/hng14-stage2-devops.git
cd hng14-stage2-devops
```

### 2. Set up your environment file
```bash
cp .env.example api/.env
```

Open `api/.env` and replace the placeholder values:
```env
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_strong_password_here
APP_ENV=production
```

> Never commit `api/.env` to git. It is already listed in `.gitignore`.

### 3. Build and start the stack
```bash
docker compose up --build
```

To run in the background:
```bash
docker compose up --build -d
```

---

## What a Successful Startup Looks Like

Once all services are up you should see output similar to:

```
✔ Container hng14-stage2-devops-redis-1     Healthy
✔ Container hng14-stage2-devops-api-1       Healthy
✔ Container hng14-stage2-devops-worker-1    Started
✔ Container hng14-stage2-devops-frontend-1  Started
```

Verify all containers are running and healthy:
```bash
docker compose ps
```

Expected output:
```
NAME                                  STATUS          PORTS
hng14-stage2-devops-redis-1           running (healthy)
hng14-stage2-devops-api-1             running (healthy)
hng14-stage2-devops-worker-1          running
hng14-stage2-devops-frontend-1        running          0.0.0.0:3000->3000/tcp
```

---

## Using the Application

Open your browser and go to:
```
http://localhost:3000
```

- Click **Submit New Job** to create a job
- The job will appear with status `queued`
- Within a few seconds it will automatically update to `completed`

---

## Testing the API Directly

**Create a job:**
```bash
curl -X POST http://localhost:8000/jobs
```

**Check job status:**
```bash
curl http://localhost:8000/jobs/<job_id>
```

**Check a non-existent job (should return 404):**
```bash
curl -v http://localhost:8000/jobs/00000000-0000-0000-0000-000000000000
```

---

## Running Unit Tests

```bash
cd api
pip install -r requirements.txt
pytest tests/ -v --cov=main --cov-report=term-missing
```

Expected output:
```
tests/test_main.py::test_create_job_returns_job_id          PASSED
tests/test_main.py::test_create_job_pushes_to_redis_queue   PASSED
tests/test_main.py::test_create_job_sets_status_to_queued   PASSED
tests/test_main.py::test_get_job_returns_status             PASSED
tests/test_main.py::test_get_job_returns_404_when_not_found PASSED
tests/test_main.py::test_get_job_returns_queued_status      PASSED

6 passed in x.xxs
```

---

## CI/CD Pipeline

The GitHub Actions pipeline runs automatically on every push and pull request. Stages run in strict order — a failure in any stage stops all subsequent stages.

| Stage | What it does |
|-------|-------------|
| lint | flake8 (Python), eslint (JavaScript), hadolint (Dockerfiles) |
| test | pytest with mocked Redis, uploads coverage report as artifact |
| build | Builds all 3 images, tags with git SHA + latest, pushes to local registry |
| security-scan | Trivy scans all images, fails on CRITICAL findings, uploads SARIF artifact |
| integration-test | Brings full stack up, submits a job, polls until completed, tears down cleanly |
| deploy | Rolling update on pushes to `main` only — new container must pass healthcheck within 60s before old one is stopped |

### Required GitHub Secret

Before the deploy stage can run, add the following secret to your repository under `Settings → Secrets and variables → Actions`:

| Secret | Value |
|--------|-------|
| `REDIS_PASSWORD` | The same password used in your `api/.env` |

---

## Stopping the Stack

```bash
docker compose down
```

To also remove volumes:
```bash
docker compose down -v
```

---

## Project Structure

```
hng14-stage2-devops/
├── .github/
│   └── workflows/
│       └── pipeline.yml
├── api/
│   ├── tests/
│   │   └── test_main.py
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── worker/
│   ├── Dockerfile
│   └── worker.py
├── frontend/
│   ├── views/
│   │   └── index.html
│   ├── Dockerfile
│   ├── app.js
│   └── package.json
├── docker-compose.yml
├── .env.example
├── .gitignore
├── FIXES.md
└── README.md
```
