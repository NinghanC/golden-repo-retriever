# Golden Repo Retriever

Golden Repo Retriever is a small local workflow for reading finance-report style data and producing a simple summary.

Right now it:

1. Accepts a finance query from the command line.
2. Finds known companies in the query.
3. Loads sample financial data.
4. Calculates basic metrics.
5. Prints a short summary.

## Setup

```powershell
uv venv --python 3.11
uv pip install -e .
```

## Run

Run the CLI:

```powershell
.\.venv\Scripts\python.exe -m golden_repo_retriever.cli
```

Run with a custom query:

```powershell
.\.venv\Scripts\python.exe -m golden_repo_retriever.cli --query "Read finance report for Simba."
```

Include a local text or PDF report:

```powershell
.\.venv\Scripts\python.exe -m golden_repo_retriever.cli --file samples\microsoft_report.txt
```

Print JSON:

```powershell
.\.venv\Scripts\python.exe -m golden_repo_retriever.cli --json
```

Save the full result:

```powershell
.\.venv\Scripts\python.exe -m golden_repo_retriever.cli --output outputs\analysis.json
```

Choose a summarization provider:

```powershell
.\.venv\Scripts\python.exe -m golden_repo_retriever.cli --llm-provider local
```

The default provider is `local`, so no cloud model is called unless you configure a key and choose another provider.

Run the API:

```powershell
.\.venv\Scripts\python.exe start_api.py
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

Upload a report through the API:

```powershell
curl -X POST http://127.0.0.1:8000/api/v1/analyze-upload `
  -F "query=Read this finance report." `
  -F "file=@samples\microsoft_report.txt"
```

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Current Workflow

```text
frontend/CLI/API -> query -> optional text/PDF report -> state -> retrieval agent -> analyst agent -> synthesizer agent -> audit log -> optional export
```

The repo includes a small shared state object and audit log.

## Optional LLM Providers

By default, summaries are generated locally from calculated metrics.

To enable OpenAI-compatible summarization, copy `.env.example` to `.env` and configure one provider:

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

## Next Steps

- Add more companies.
- Add more metrics.
- Add richer report extraction.
