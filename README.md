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

Include a local text report:

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

Run the API:

```powershell
.\.venv\Scripts\python.exe start_api.py
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

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Current Workflow

```text
CLI/API -> query -> optional text report -> state -> company detection -> sample data -> metrics -> summary -> audit log -> optional export
```

The repo includes a small shared state object and audit log.

## Next Steps

- Add more companies.
- Add more metrics.
- Add PDF parsing.
- Add uploaded report files to the API.
