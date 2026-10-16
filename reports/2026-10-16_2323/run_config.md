# Agent configuration

Read from the Claude platform on 2026-10-16 20:28 UTC.

## Agent

- Name: Deep researcher
- ID: `agent_01WedaF6x8gmapUohSFzrcnk` (version 2)
- Description: Conducts multi-step web research with source synthesis and citations.

## Model

- Model: `claude-opus-5-5`
- Effort: low
- Speed: standard
- Inference region: default

## Tools

- Toolset `agent_toolset_20260401` (built-in tools):
    - `bash`: Run shell commands in the session container (enabled, permission: auto)
    - `read`: Read a file (text, images, PDFs, notebooks) (enabled, permission: auto)
    - `write`: Write a file (enabled, permission: auto)
    - `edit`: Replace text in a file (enabled, permission: auto)
    - `glob`: Find files by name pattern (enabled, permission: auto)
    - `grep`: Search file contents with regex (enabled, permission: auto)
    - `web_fetch`: Fetch the content of a URL (enabled, permission: auto)
    - `web_search`: Search the web (enabled, permission: auto)
- MCP servers: 0
- Skills: 0
- Multi-agent: off

## System prompt (the agent's standing instructions)

You are a research agent. Given a question or topic:

1. Decompose it into 3-5 concrete sub-questions that, answered together, cover the topic.
2. For each sub-question, run targeted web searches and fetch the most authoritative sources (prefer primary sources, official docs, peer-reviewed work over blog posts and aggregators).
3. Read the sources in full — don't skim. Extract specific claims, data points, and direct quotes with attribution.
4. Synthesize a report that answers the original question. Structure it by sub-question, cite every non-obvious claim inline, and close with a "confidence & gaps" section noting where sources disagreed or where you couldn't find good coverage.
5. Before you send the report, check every citation: replace blog posts, aggregators and encyclopedia pages with the primary source behind them, and name any claim where no stronger source exists.

Be skeptical. If sources conflict, say so and explain which you find more credible and why. Don't paper over uncertainty with confident-sounding prose.

## Your task

Find current open job positions for a Senior QA Engineer in Tel Aviv, Israel (or Tel Aviv area / Gush Dan, including hybrid) suitable for a candidate with 15 years of QA experience (manual and automation, E2E testing, worked at Transmit Security, Checkmarx and Kaltura). For each position give: company, job title, location / work model, key requirements, and a direct link to the posting. Prefer postings published in the last 30 days and say the posting date where known. Also summarize which companies are hiring senior QA now, typical salary ranges for senior QA in Tel Aviv, and the most in-demand skills, with sources.

The current date and time is Friday, October 16, 2026 at 11:23 PM IDT (Asia/Jerusalem). The Unix timestamp for this same instant is 1792182217 (seconds since 1970-01-01T00:00:00 UTC).

## Environment (where the tools run)

- Name: deep-research-env (`env_01PHBKTH7GTnCMHTpdAP16ak`)
- Type: cloud container
- Network access: unrestricted
- Extra packages: none

## Task (the prompt sent for this run)

Run the Senior QA job search described in your instructions and send the report.

## Run

- Session: `sesn_01GCfeeMSraqtParyzqxv3Se`
- Started: 2026-10-16 20:23 UTC
- Working time: 188 seconds
- Tokens: 1,420,400 input, 10,970 output
- Web searches: 5
- Cost (list price): $1.16 (budget cap $5.00)

