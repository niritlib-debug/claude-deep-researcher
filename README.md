# Claude Managed Agents — Deep researcher

Scripts that list the Managed Agents on the Claude platform and run the
**Deep researcher** agent (`agent_01WedaF6x8gmapUohSFzrcnk`), saving its report as a PDF.

## Files

| File | What it is |
|---|---|
| `list_agents.py` | Lists the agents on the Claude platform and writes `agents.md` |
| `agents.md` | The agent list |
| `run_agent.py` | Sends a research question to the Deep researcher agent and writes `report.md` + `report.pdf` |
| `report.pdf` | The agent's report: Senior QA job openings in Tel Aviv |

## Setup

1. Create a `.env` file with `ANTHROPIC_API_KEY=...` (it is ignored by Git — never commit it).
2. Install the packages:

```bash
python3 -m venv .venv && .venv/bin/pip install anthropic python-dotenv fpdf2
```

## Usage

```bash
.venv/bin/python list_agents.py
```

```bash
.venv/bin/python run_agent.py "your research question"
```
