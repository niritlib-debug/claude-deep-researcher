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
| System prompt | Research method (sub-questions, primary sources, cite every claim, "confidence & gaps") **plus the task**: find Senior QA openings in Tel Aviv for 15 years' experience, with links, dates, hiring companies, salaries and in-demand skills. Kept in `system_prompt.md` |
| Environment | `deep-research-env`, cloud container, unrestricted network |
| Run message | Short kickoff in `task.txt`: "Run the Senior QA job search described in your instructions and send the report." |
| Spending cap | $5.00 per run (session budget set in `run_agent.py` and `schedule.py`) |
| Schedule | Every day at 08:00 and 20:00 Israel time (cron `0 8,20 * * *`, `Asia/Jerusalem`), set in `schedule.py` |

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
| `system_prompt.md` | The agent's system prompt, including the job-search task |
| `update_agent.py` | Applies `system_prompt.md` to the agent (new version) and moves the schedule to it |
| `task.txt` | The short kickoff message each run sends |
| `schedule.py` | The schedule settings; run it to apply changes on the platform |
| `collect_reports.py` | Saves each scheduled run's report to `reports/<date>_<time>/report.pdf` |

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

Run the job search now (sends `task.txt`):

```bash
.venv/bin/python run_agent.py
```

Or ask the agent something else:

```bash
.venv/bin/python run_agent.py "your research question"
```

## Changing the task

The job-search task is part of the agent's system prompt. Edit `system_prompt.md`, then apply it
(this creates a new agent version and moves the schedule to it):

```bash
.venv/bin/python update_agent.py
```

## Scheduled runs

The Claude platform runs the agent at 08:00 and 20:00 Israel time, in the cloud — your computer can be off.
To change the time, edit `schedule.py`, then apply:

```bash
.venv/bin/python schedule.py
```

Download the finished scheduled reports as PDFs:

```bash
.venv/bin/python collect_reports.py
```

To stop the schedule, pause it in the Claude Console (Deployments) or with `client.beta.deployments.pause(...)`.

Rebuild the files from an earlier run without paying for a new one:

```bash
.venv/bin/python run_agent.py --session sesn_...
```
