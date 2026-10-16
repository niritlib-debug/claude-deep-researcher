# Claude Managed Agents — Deep researcher

Scripts that list the Managed Agents on the Claude platform and run the
**Deep researcher** agent (`agent_01WedaF6x8gmapUohSFzrcnk`), saving its report as a PDF.
Every run is documented: the PDF opens with the agent's configuration and the task it was given.

## Agent configuration at a glance

Full, auto-generated details are in [AGENT_CONFIG.md](AGENT_CONFIG.md) (the agent) and
[run_config.md](run_config.md) (the last run).

| Setting | Value |
|---|---|
| Platform | Claude Managed Agents (Anthropic hosts the agent loop and a cloud container) |
| Model | `claude-opus-5-5` |
| Effort | low |
| Tools | Built-in toolset `agent_toolset_20260401`: web_search, web_fetch, bash, read, write, edit, glob, grep — all enabled, permission policy `auto` |
| System prompt | Research method: split into sub-questions, search and read primary sources, cite every claim, end with "confidence & gaps" |
| Environment | `deep-research-env`, cloud container, unrestricted network |
| Task (prompt) | Sent per run — see the "Task" section of `run_config.md` |
| Spending cap | $5.00 per run (session budget set in `run_agent.py`) |

## Files

| File | What it is |
|---|---|
| `list_agents.py` | Lists the agents on the Claude platform and writes `agents.md` |
| `agents.md` | The agent list |
| `agent_config.py` | Reads the agent, environment and run settings from the platform and formats them |
| `export_agent_config.py` | Writes `AGENT_CONFIG.md` |
| `AGENT_CONFIG.md` | The agent's configuration document: model, effort, tools, system prompt, environment |
| `run_agent.py` | Sends a task to the agent and writes `run_config.md`, `report.md` and `report.pdf` |
| `run_config.md` | The last run: configuration + task prompt + session, tokens, searches, cost |
| `report.pdf` | Configuration page, then the agent's report (Senior QA job openings in Tel Aviv) |

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
.venv/bin/python export_agent_config.py
```

Run the agent with a question, or with a longer task saved in a text file:

```bash
.venv/bin/python run_agent.py "your research question"
```

```bash
.venv/bin/python run_agent.py --task-file task.txt
```

Rebuild the files from an earlier run without paying for a new one:

```bash
.venv/bin/python run_agent.py --session sesn_...
```
