# Development Notes

Golden Repo Retriever is under construction.

The current codebase focuses on a small local workflow with clear state tracking:

```text
query -> state -> company detection -> sample data -> metrics -> summary -> audit log
```

## Current Components

- `cli.py`: command-line entry point
- `workflow.py`: workflow phases
- `state.py`: shared state and audit event helpers
- `tools.py`: company detection, metric calculation, and summary formatting
- `sample_data.py`: local sample data
- `tests/test_workflow.py`: workflow smoke test

## Development Direction

The project is expected to grow gradually:

- Add more companies and sample data fields.
- Add more financial metrics.
- Add file export for analysis results.
- Add PDF parsing for uploaded reports.
- Add an API layer.
- Add optional OpenAI or Mistral summarization behind local fallback behavior.

## Local Check

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m golden_repo_retriever.cli --json
```
