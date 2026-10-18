# ResumeIQ: ATS Resume Analyzer Web Application

[![FastAPI](https://img.shields.io/badge/FastAPI-0.143+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6+-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4+-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Pytest](https://img.shields.io/badge/Pytest-28_Passed-success.svg?logo=pytest&logoColor=white)](https://docs.pytest.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A production-minded, local-first web application that analyzes resumes for Applicant Tracking System (ATS) compatibility. ResumeIQ delivers an explainable score out of 100, exact and synonym keyword matching, formatting risk detection, evidence-backed deductions, and a side-by-side improvement studio with strict factual safeguards.

---

## Key Features

- **Ingestion Pipeline:** Supports `.pdf` and `.docx` documents with magic-byte validation, 10MB limit enforcement, and layout-preserving text extraction (PyMuPDF and python-docx).
- **Scanned PDF & OCR Detection:** Identifies image-only or scanned PDFs containing little to no selectable text, explaining why OCR or a digital PDF is required rather than silently producing unreliable scores.
- **Explainable 100-Point Scoring Engine:** Transparent, deterministic scoring with configurable heuristics across 6 key dimensions.
- **Deduplication & Synonym Intelligence:** Matches exact keywords and recognizes technical synonyms (e.g. *k8s* ↔ *Kubernetes*, *ReactJS* ↔ *React*, *Golang* ↔ *Go*) while preventing keyword-stuffing exploits.
- **Dual Operating Modes:**
  - **Job-Specific Fit Mode:** Compares qualifications, seniority, and required/preferred skills against a pasted job description.
  - **General ATS Health Mode:** Evaluates general ATS structural compliance, formatting safety, and metric density when no job description is supplied.
- **Extraction Review Interface:** Allows users to inspect and correct extracted text and contact info before scoring.
- **Resume Improvement Studio:** Side-by-side diff comparing original bullet points with evidence-anchored revisions. Accept or reject changes individually.
- **Two Analysis Layers:**
  - **Layer A (Default):** Local, deterministic, rule-based engine requiring zero API keys and zero network data egress.
  - **Layer B (Optional):** AI-assisted optimization with explicit consent, strict Pydantic JSON validation, and guardrails against hallucinated credentials.
- **Zero Document Retention:** Ephemeral in-memory processing. Resumes and contact information are discarded immediately upon request completion with no database persistence.

---

## Explainable Scoring Dimensions (100 Points Total)

| Dimension | Points (Job-Matched) | Points (Resume-Only) | Evaluation Heuristics |
| :--- | :---: | :---: | :--- |
| **1. Skills & Keyword Alignment** | 30 | 20 | Matches technical skills, frameworks, and domain competencies against target JD. Differentiates exact matches vs. synonyms. Weighted heavily toward mandatory requirements (75%) over nice-to-haves (25%). Deduplicates repeated keywords. |
| **2. Relevant Experience Alignment** | 25 | 25 | Scans dated employment history for estimated years of experience, compares against required seniority in JD, and checks bullet depth. |
| **3. Education & Required Qualifications** | 15 | 15 | Detects degree levels (B.S., M.S., Ph.D.), majors, and certifications. Evaluates target degree requirements from JD. |
| **4. Measurable Achievements & Impact** | 10 | 20 | Rewards quantified outcomes (%, \$, metrics, throughput, team scale) and strong action verbs (Architected, Spearheaded, Engineered). Calibrated to avoid unfairly penalizing valid roles without numerical KPIs. |
| **5. Resume Structure & Section Completeness** | 10 | 10 | Checks for essential ATS sections (Experience, Education, Skills, Contact Info, Professional Summary). |
| **6. ATS Readability & Formatting** | 10 | 10 | Analyzes layout hazards, tables, multi-column risks, font issues, and word count / page density. |

---

## Architecture

ResumeIQ is engineered with a **Python-first architecture**:
- **Backend:** FastAPI, Pydantic v2, PyMuPDF, python-docx, uvicorn.
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Lucide icons.
- **Unified Single-Service Packaging:** In production, the compiled React SPA (`frontend/dist`) is directly served by FastAPI. This allows the entire application to run as a single container or single Python web service on any free hosting platform without requiring separate frontend and backend servers.

```
resumeiq/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI app & static SPA server
│   │   ├── config.py                   # Pydantic Settings & environment variables
│   │   ├── api/
│   │   │   └── routes.py               # /health, /resumes/parse, /analyze, /resumes/improve
│   │   ├── models/
│   │   │   └── schemas.py              # Pydantic request/response & scorecard schemas
│   │   ├── parser/
│   │   │   ├── extractor.py            # PDF/DOCX magic-byte validation & extraction
│   │   │   ├── ocr_detector.py         # Scanned PDF / image heuristic detector
│   │   │   └── section_parser.py       # Structural section & contact info parser
│   │   ├── engine/
│   │   │   ├── scorer.py               # Deterministic 100-pt scoring coordinator
│   │   │   ├── keywords.py             # Keyword, synonym & requirement extractor
│   │   │   ├── experience.py           # Seniority & years of experience evaluator
│   │   │   ├── education.py            # Degree level & certification matcher
│   │   │   ├── achievements.py         # Quantifiable impact & action verb analyzer
│   │   │   ├── formatting.py           # ATS layout, table, and readability checker
│   │   │   └── rules.py                # Configurable weights, synonyms & thresholds
│   │   ├── ai/
│   │   │   ├── provider.py             # Abstract AI provider interface
│   │   │   ├── mock_provider.py        # Layer A: Local rule-based rewriter (offline)
│   │   │   └── gemini_provider.py      # Layer B: Optional AI assistant with fallback
│   │   └── utils/
│   │       └── logger.py               # Privacy-preserving logger (masks PII)
│   ├── tests/
│   │   ├── test_parser.py              # Parsing, corruption, size & scanned tests
│   │   ├── test_engine.py              # Determinism, boundary & keyword tests
│   │   ├── test_ai_provider.py         # Rewriter & fallback tests
│   │   └── test_static_serving.py      # Single-service SPA mount tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/                 # ScoreGauge, DimensionCard, KeywordExplorer, etc.
│   │   ├── services/api.ts             # REST client
│   │   ├── types/index.ts              # TypeScript schemas
│   │   ├── App.tsx                     # Main view controller
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── Dockerfile                          # Multi-stage production container
├── docker-compose.yml                  # One-command containerized execution
├── run.sh                              # Local run script
├── .env.example                        # Environment template
└── README.md
```

---

## Quickstart & Local Execution

### Prerequisites
- Python 3.11+ (Python 3.12 recommended)
- Node.js 18+ and npm (only needed to build or develop frontend)

### Option 1: Unified Single-Service (Recommended)

1. Clone or navigate to the repository directory:
   ```bash
   cd resumeiq
   ```

2. Create virtual environment and install backend dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```

3. Build the frontend static assets:
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

4. Run the application:
   ```bash
   ./run.sh
   # Or directly:
   PYTHONPATH=backend .venv/bin/uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
   ```

5. Open your browser to **http://127.0.0.1:8000**. The interactive web app and API documentation (`/docs`) are fully live!

---

### Option 2: Live Development Mode (Vite HMR + FastAPI Reload)

Run both dev servers with a single command:
```bash
./run.sh dev
```
- Frontend with hot-module replacement runs at **http://localhost:5173** (automatically proxies `/api` calls to FastAPI).
- FastAPI backend with auto-reload runs at **http://127.0.0.1:8000**.

---

### Option 3: Docker & Docker Compose

Run the entire application in a standardized container with zero host dependencies:
```bash
docker compose up --build
```
Open **http://localhost:8000**.

---

## Running Automated Tests

Run the full pytest suite (28 comprehensive unit & integration tests):
```bash
PYTHONPATH=backend .venv/bin/pytest backend/tests/ -v
```

Test coverage includes:
- Valid PDF and DOCX text extraction
- Scanned PDF detection and OCR alerts
- Empty, corrupted, and oversized file rejection
- Deterministic scoring verification (identical score on identical inputs)
- Score boundaries (0–100 clamping)
- Exact and synonym keyword matching
- Keyword stuffing mitigation (deduplication)
- Quantifiable impact and action verb evaluation
- Resume-only mode vs. Job-matched mode
- AI provider graceful fallback when no API key is supplied
- Single-service FastAPI SPA static serving

Verify the frontend TypeScript build:
```bash
cd frontend && npm run build
```

---

## Free Hosting & Deployment Analysis

ResumeIQ's single-service architecture makes it exceptionally simple to deploy to free hosting tiers without separate frontend/backend charges.

| Platform | Recommended Tier | Free Resources | Limitations & Cold Starts | Suitability |
| :--- | :--- | :--- | :--- | :---: |
| **Render** | Free Web Service (Docker) | 512 MB RAM, 0.1 vCPU | Spins down after 15 min of inactivity; ~50s cold start on first request. Ephemeral disk guarantees zero resume storage. | ⭐⭐⭐⭐⭐ (Best overall) |
| **Hugging Face Spaces** | Docker / Python Space | 16 GB RAM, 2 vCPU | No cold start sleep on public spaces; persistent CPU allocation. | ⭐⭐⭐⭐⭐ (High performance) |
| **Fly.io** | Free Tier App | 256 MB - 512 MB RAM | Free allowance of 3 shared-cpu-1x VMs. Requires credit card verification. | ⭐⭐⭐⭐ |
| **Railway** | Starter Trial | \$5 trial credit / 512 MB RAM | 30-day limit on unverified accounts. | ⭐⭐⭐ |
| **Vercel + Render** | Vercel (Frontend) + Render (API) | Global Edge CDN + 512MB Backend | Requires configuring backend CORS origin to match Vercel URL. | ⭐⭐⭐⭐ |

### Deploying to Render in 3 Steps:
1. Connect your GitHub repository to Render.
2. Select **New Web Service** -> **Environment: Docker**.
3. Set the health check path to `/api/health` and port to `8000`. Deploy!

---

## Security & Privacy Guarantee

- **Ephemeral In-Memory Handling:** Resumes are processed in memory and released immediately. No uploaded resume files are saved to disk or persistent databases.
- **PII Scrubbing:** Application logs automatically mask emails and phone numbers. Raw resume text is never output to server logs.
- **No Hallucinated Credentials:** The improvement engine operates on factual grounding. It will never invent past employers, fake job titles, fabricated dates, or unearned academic degrees.
- **Explicit AI Consent:** ResumeIQ defaults to 100% offline rule-based scoring (Layer A). External AI processing (Layer B) is only invoked if explicitly opted-in by the user and an API key is configured.
