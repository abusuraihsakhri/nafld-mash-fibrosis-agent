# Nafld Mash Fibrosis Agent

> **Domain:** Gastroenterology, Hepatology & Clinical Nutrition
> **Reference Guidelines & Standards:** `AASLD & ACG Clinical Practice Guidelines`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Nafld Mash Fibrosis Agent** is an advanced analytical and computational platform implementing MASH Non-Invasive Biomarkers, FAST Score & VCTE FibroScan Agent. It provides clinical decision support for hepatology assessments including FIB-4 scoring, NAFLD Fibrosis Score calculation, and FibroScan VCTE liver stiffness interpretation.

---

## 🚀 Quickstart

### Prerequisites
- Python 3.10+
- pip

### Installation
```bash
pip install -e .
```

### Configuration
Set the required environment variable for the HMAC audit trail:
```bash
# Linux/macOS
export AUDIT_SECRET_KEY=$(openssl rand -hex 32)

# Windows PowerShell
$env:AUDIT_SECRET_KEY = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})

# Windows CMD
set AUDIT_SECRET_KEY=your-secure-random-key-here
```

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`InvariantQCWorker`**: Primary mathematical & protocol boundary auditor
- **`SafetyEscalationWorker`**: Safety boundary, toxicity & emergency interlock worker
- **`ProtocolConformanceWorker`**: Spec conformance, anomaly triage & discordance checker
- **`NonInvasiveFibrosisScorerAgent`**: FIB-4 and NAFLD Fibrosis Score evaluation
- **`VCTEStiffnessClassifierAgent`**: FibroScan VCTE liver stiffness classification
- **`MASHPharmacotherapyAdvisorAgent`**: Pharmacotherapy decision support

---

## 💻 CLI Usage

### 1. Single Case Audit
```bash
python cli.py audit --task-id CASE-001 --target PATIENT-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Batch Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 3. Interactive Chat
```bash
python cli.py chat "What is the system status?"
```

### 4. Verify Audit Trail
```bash
python cli.py verify-audit
```

### 5. Start REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Input Data Schema (CSV)

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique case identifier | Required |
| `target_identifier` | Patient synthetic key | Required |
| `primary_metric` | Primary measurement value | Required |
| `secondary_metric` | Secondary kinetic index | Required |
| `status_descriptor` | Status code (NOMINAL, DISCORDANT, etc.) | Required |
| `is_critical_flag` | Emergency escalation flag | Optional |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation. Requires `AUDIT_SECRET_KEY` environment variable.
* **Input Validation:** All metric values validated as finite numbers (NaN/Inf rejected). String identifiers validated for length and content.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances, Claude, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
# Set test environment variable (or use conftest.py default)
set AUDIT_SECRET_KEY=test-key-for-pytest
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

### Test Coverage
- PHI guard enforcement
- Specialized worker evaluation
- Supervisor consensus and audit trail
- Input validation (NaN, Inf, empty strings, length limits)
- Error handling (file not found, permission errors)

---

## 🐳 Container Deployment

### Docker Compose (Recommended)
```bash
# Create .env file with required secrets
echo "AUDIT_SECRET_KEY=your-secure-production-key" > .env

# Build and run
docker compose up -d
```

### Docker Build
```bash
docker build -t nafld-mash-fibrosis-agent .
docker run -e AUDIT_SECRET_KEY=your-secure-key -p 8000:8000 nafld-mash-fibrosis-agent
```

---

## 📁 Project Structure

```
nafld-mash-fibrosis-agent/
├── agents/                    # Core agent package
│   ├── __init__.py           # Package init
│   ├── api.py                # FastAPI REST endpoints
│   ├── base.py               # Security, PHI guard, HMAC audit
│   ├── learning.py           # Bayesian calibration engine
│   ├── llm_factory.py        # LLM provider factory
│   ├── metrics.py            # Prometheus metrics collector
│   ├── models.py             # Pydantic data models with validation
│   ├── streamer.py           # WebSocket telemetry broadcaster
│   ├── supervisor.py         # Master orchestrator
│   └── workers.py            # Specialized worker agents
├── tests/                     # Test suite
├── nafld_mash_fibrosis_agent/ # Alternative CLI package
├── web/index.html             # Operations console UI
├── cli.py                     # Main CLI entry point
├── mash_sentinel.py           # Standalone MASH sentinel module
├── enrichment.py              # Enrichment feature engines
├── simulator.py               # High-throughput simulation
├── pyproject.toml             # Project configuration
├── docker-compose.yml         # Container orchestration
└── .github/workflows/ci.yml   # CI/CD pipeline
```
