# Golden Repo Retriever

Golden Repo Retriever is a local finance-analysis workflow for reading report-style input, detecting known companies, calculating basic metrics, and returning an auditable summary.

The project currently includes:

- A command-line interface for quick local analysis.
- A FastAPI service for JSON requests and report uploads.
- A simple browser interface served by the API.
- Text and PDF report parsing.
- A saved report library for uploaded documents.
- Simple financial fact extraction from report text.
- Evidence snippets for extracted financial facts.
- Local market data snapshots for known companies.
- JSON result export.
- Local analysis history backed by SQLite.
- Background analysis jobs with a separate worker.
- A small agent workflow with retrieval, analysis, and synthesis phases.
- Optional OpenAI, Mistral, or custom OpenAI-compatible summarization with local fallback.

By default, the app uses local summarization. No cloud model is called unless a provider and API key are configured.

## Setup

```powershell
uv venv --python 3.11
uv pip install -e .
```

## CLI

Run the default analysis:

```powershell
.\.venv\Scripts\python.exe -m golden_repo_retriever.cli
```

Run with a custom query:

```powershell
.\.venv\Scripts\python.exe -m golden_repo_retriever.cli --query "Compare Apple and Microsoft."
```

Analyze a local text or PDF report:

```powershell
.\.venv\Scripts\python.exe -m golden_repo_retriever.cli --file samples\microsoft_report.txt
```

Print JSON:

```powershell
.\.venv\Scripts\python.exe -m golden_repo_retriever.cli --json
```

Export the full result:

```powershell
.\.venv\Scripts\python.exe -m golden_repo_retriever.cli --output outputs\analysis.json
```

Choose a summarization provider:

```powershell
.\.venv\Scripts\python.exe -m golden_repo_retriever.cli --llm-provider local
```

## API And Frontend

Start the API:

```powershell
.\.venv\Scripts\python.exe start_api.py
```

Start the worker in another terminal:

```powershell
.\.venv\Scripts\python.exe start_worker.py
```

Open the frontend:

```text
http://127.0.0.1:8000
```

Health check:

```powershell
curl http://127.0.0.1:8000/health
```

Analyze through the API:

```powershell
curl -X POST http://127.0.0.1:8000/api/v1/analyze `
  -H "Content-Type: application/json" `
  -d "{\"query\":\"Compare Apple and Microsoft.\"}"
```

Upload a report:

```powershell
curl -X POST http://127.0.0.1:8000/api/v1/analyze-upload `
  -F "query=Read this finance report." `
  -F "file=@samples\microsoft_report.txt"
```

Save a report to the report library:

```powershell
curl -X POST http://127.0.0.1:8000/api/v1/reports `
  -F "file=@samples\microsoft_report.txt"
```

Analyze a saved report:

```powershell
curl -X POST http://127.0.0.1:8000/api/v1/analyze `
  -H "Content-Type: application/json" `
  -d "{\"query\":\"Read this report.\",\"report_id\":1}"
```

List saved analyses:

```powershell
curl http://127.0.0.1:8000/api/v1/analyses
```

Load one saved analysis:

```powershell
curl http://127.0.0.1:8000/api/v1/analyses/1
```

Create a background job:

```powershell
curl -X POST http://127.0.0.1:8000/api/v1/jobs `
  -H "Content-Type: application/json" `
  -d "{\"query\":\"Compare Apple and Microsoft.\"}"
```

Create a background job for a saved report:

```powershell
curl -X POST http://127.0.0.1:8000/api/v1/jobs `
  -H "Content-Type: application/json" `
  -d "{\"query\":\"Read this report.\",\"report_id\":1}"
```

List jobs:

```powershell
curl http://127.0.0.1:8000/api/v1/jobs
```

Jobs start as `queued`. The worker claims queued jobs, runs the analysis, saves the result, and marks each job as `completed` or `failed`.

## Configuration

The app reads settings from environment variables or a `.env` file.

```text
APP_NAME=Golden Repo Retriever
APP_VERSION=0.1.0
DATABASE_PATH=data/golden_repo_retriever.db
API_HOST=127.0.0.1
API_PORT=8000
WORKER_POLL_SECONDS=2.0
LLM_PROVIDER=local
LOG_LEVEL=INFO
```

Logs use a standard timestamp, level, module, and message format.

## LLM Providers

The default provider is `local`.

To enable OpenAI-compatible summarization, create a `.env` file and configure one provider:

```text
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4o-mini
```

or:

```text
LLM_PROVIDER=mistral
MISTRAL_API_KEY=your_key
MISTRAL_MODEL=mistral-small-latest
```

If no key is present, the app falls back to local summarization.

## Workflow

```text
CLI/API/frontend
  -> query and optional saved report
  -> queued job
  -> worker
  -> extracted financial facts
  -> evidence snippets
  -> market data snapshot
  -> retrieval agent
  -> analyst agent
  -> synthesizer agent
  -> background job status
  -> local history store
  -> audit log
  -> optional JSON export
```

## Project Layout

```text
golden-repo-retriever/
|-- src/golden_repo_retriever/
|   |-- agents.py
|   |-- cli.py
|   |-- config.py
|   |-- documents.py
|   |-- extraction.py
|   |-- logging_utils.py
|   |-- llm.py
|   |-- market_data.py
|   |-- queueing.py
|   |-- reporting.py
|   |-- storage.py
|   |-- worker.py
|   |-- workflow.py
|   `-- api/
|-- static/
|-- samples/
|-- tests/
|-- pyproject.toml
|-- start_worker.py
`-- README.md
```

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
