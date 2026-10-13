# MASLD / NAFLD Fibrosis Risk Calculator

A deterministic clinical-research utility for **FIB-4** and the historical **NAFLD Fibrosis Score (NFS)**. Includes a local-only browser calculator, Python functions, a command-line interface and an optional FastAPI endpoint. The repository also retains its legacy generic multi-worker audit tools for compatibility.

## Browser calculator

Open [web/index.html](web/index.html) locally, or use the GitHub Pages deployment once enabled and verified. No installation, backend, account or Python runtime is required for the browser calculator.

Enter age (completed years), AST (U/L), ALT (U/L), and platelets (10⁹/L) for FIB-4. Optionally enter **all three** of BMI (kg/m²), albumin (g/dL), and impaired fasting glucose/diabetes status for NFS.

The browser performs calculations locally and does not send values to a server or store them. It loads no external JavaScript, fonts, or analytics.

## Clinical interpretation

- **FIB-4:** `age × AST / (platelets × √ALT)`. Screening categories are low (<1.3; <2.0 if age >65), indeterminate (between the age-adjusted lower cutoff and 2.67), and high (>2.67).
- **NFS:** `−1.675 + 0.037×age + 0.094×BMI + 1.13×IFG/diabetes + 0.99×AST/ALT − 0.013×platelets − 0.66×albumin`. Low is <−1.455, high is >0.676; other results are indeterminate.
- **Limitations:** These are risk scores, not diagnoses or histological stages. FIB-4 is less accurate below 35 years and should not be used during acute illness. Clinical context and follow-up noninvasive testing (VCTE/ELF) or hepatology review may be necessary. Neither FAST nor MASH pharmacotherapy eligibility is calculated.

Methods: [AASLD 2023 NAFLD Practice Guidance](https://pmc.ncbi.nlm.nih.gov/articles/PMC10735173/), [EASL–EASD–EASO 2024 MASLD Guidelines](https://pmc.ncbi.nlm.nih.gov/articles/PMC11299976/), and [Angulo et al. 2007 NFS derivation](https://doi.org/10.1002/hep.21496).

**For research and education, not autonomous clinical decision-making.**

## Python and CLI

Python 3.10+:

```bash
python -m pip install -e .
nafld-mash-fibrosis-engine fibrosis --age 60 --ast 30 --alt 40 --platelets 250
nafld-mash-fibrosis-engine fibrosis --age 52 --ast 40 --alt 50 --platelets 230 --bmi 29 --albumin 4.2 --ifg yes
```

Library:

```python
from nafld_mash_fibrosis_agent.fibrosis import assess_fibrosis

result = assess_fibrosis(age=60, ast=30, alt=40, platelets=250)
print(result["fib4"], result["fib4_category"])
```

Inputs are validated for finite, plausible values. Missing NFS variables cannot be silently defaulted. The CLI exits with code 2 for invalid calculator inputs.

## Optional REST API

```bash
python -m pip install -e '.[api]'
export AUDIT_SECRET_KEY="$(openssl rand -hex 32)"
python cli.py serve --host 127.0.0.1 --port 8000
```

Call `POST /api/fibrosis` with `{"age":60,"ast":30,"alt":40,"platelets":250}`. Include `bmi`, `albumin`, and `impaired_fasting_glucose_or_diabetes` together to calculate NFS. OpenAPI documentation is served at `/docs`.

The older `POST /api/audit`, `POST /api/chat`, `GET /metrics` and CLI `audit`, `batch`, `chat`, `verify-audit` features remain available; these implement **generic task checks**, not validated MASLD risk algorithms. They must not be used to make clinical treatment or emergency-escalation decisions. The mock conversational adapter is deterministic; it does not consult a medical knowledge model. `GET /api/audit/logs` requires a distinct `AUDIT_LOG_READ_TOKEN` of at least 24 characters sent using the `Authorization: Bearer` header, and otherwise returns 403.

## Security and privacy

Do **not** supply names, medical record numbers or other identifiable data. Legacy audit requests may retain synthetic identifiers in process memory; audit trail metadata is also held in memory and is **not** a persistent or independently certified clinical audit record. A regex-based identifier filter reduces some accidental disclosures but is **not HIPAA de-identification**. Protect any API exposure with external access controls/TLS; local execution is preferred. The sample data are synthetic.

Docker Compose binds the API to `127.0.0.1:8000` by default; set `AUDIT_SECRET_KEY` in your environment before running `docker compose up --build`. No patient data should be committed or uploaded.

## Development and validation

```bash
python -m pip install -e '.[api,test]'
export AUDIT_SECRET_KEY="$(openssl rand -hex 32)"
python -m pytest -q
node web/test_calculator.cjs
```

CI runs Python tests, package builds, and Node tests of the browser mathematics on pushes and pull requests. The static application requires a modern browser supporting standard ES2019 JavaScript and does not require Pyodide. GitHub Pages deployment is defined in [pages.yml](.github/workflows/pages.yml).

**License:** [MIT](LICENSE).
