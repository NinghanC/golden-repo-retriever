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

```powershell
.\.venv\Scripts\python.exe -m golden_repo_retriever.cli
```

Run with a custom query:

```powershell
.\.venv\Scripts\python.exe -m golden_repo_retriever.cli --query "Read finance report for Simba."
```

Print JSON:

```powershell
.\.venv\Scripts\python.exe -m golden_repo_retriever.cli --json
```

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Current Workflow

```text
query -> state -> company detection -> sample data -> metrics -> summary -> audit log
```

The repo includes a small shared state object and audit log. See `DEVELOPMENT.md` for current development notes.

## Next Steps

- Add more companies.
- Add more metrics.
- Add file output.
- Add PDF parsing.
- Add an API.
