"""Run the Deep researcher agent on a task and save its report as a PDF.

The PDF opens with the configuration used for the run (model, effort, tools,
system prompt, environment, task, cost), followed by the agent's report.

Usage:
    python run_agent.py                      # run the job search (sends task.txt)
    python run_agent.py "your research question"
    python run_agent.py --task-file other_task.txt
    python run_agent.py --session sesn_...   # rebuild the files from an earlier run
"""

import argparse
import re
import sys

import anthropic
from dotenv import load_dotenv
from fpdf import FPDF
from fpdf.fonts import FontFace

from agent_config import AGENT_ID, ENVIRONMENT_ID, build_document

FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
BUDGET_CENTS = "500"  # hard spending cap per run: $5.00


def run(client: anthropic.Anthropic, task: str) -> str:
    session = client.beta.sessions.create(
        agent=AGENT_ID,
        environment_id=ENVIRONMENT_ID,
        title=task[:80],
        budget={"type": "limit", "max_list_cost": {"amount": BUDGET_CENTS, "currency": "USD"}},
    )
    print(f"Session: {session.id}", flush=True)
    with client.beta.sessions.events.stream(session_id=session.id) as stream:
        client.beta.sessions.events.send(
            session_id=session.id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": task}]}],
        )
        for event in stream:
            if event.type == "agent.message":
                text = "".join(b.text for b in event.content if b.type == "text")
                print(text[:200], flush=True)
            elif event.type in ("agent.tool_use", "agent.mcp_tool_use") and event.evaluated_permission == "ask":
                # Nobody is watching this run, so deny calls that need approval.
                client.beta.sessions.events.send(
                    session_id=session.id,
                    events=[{"type": "user.tool_confirmation", "tool_use_id": event.id, "result": "deny"}],
                )
            elif event.type == "session.status_idle":
                if event.stop_reason.type != "requires_action":
                    break
            elif event.type == "session.status_terminated":
                break
    return session.id


def read_session(client: anthropic.Anthropic, session_id: str) -> tuple[str, str]:
    """Return the task sent to the session and the agent's final message (the report)."""
    task, report = "", ""
    for event in client.beta.sessions.events.list(session_id=session_id):
        if event.type in ("user.message", "agent.message"):
            text = "".join(b.text for b in event.content if b.type == "text")
            if event.type == "user.message" and not task:
                task = text
            elif event.type == "agent.message":
                report = text
    return task, report


def write_markdown(pdf: FPDF, markdown: str) -> None:
    table: list[list[str]] = []
    for line in markdown.splitlines() + [""]:
        if line.lstrip().startswith("|"):
            cells = [plain(c) for c in line.strip().strip("|").split("|")]
            if not all(re.fullmatch(r":?-+:?", c.strip()) for c in cells):  # skip |---| rows
                table.append(cells)
            continue
        if table:
            write_table(pdf, table)
            table = []
        heading = re.match(r"^(#{1,6})\s+(.*)", line)
        text = plain(heading.group(2) if heading else line)
        if heading:
            pdf.ln(2)
            pdf.set_font("Body", size=max(20 - 3 * len(heading.group(1)), 11))
            pdf.multi_cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("Body", size=10)
            pdf.multi_cell(0, 5, text or " ", new_x="LMARGIN", new_y="NEXT")


def plain(text: str) -> str:
    """Strip Markdown bold and code marks; show links as 'text: url'."""
    text = re.sub(r"\[([^\]]+)\]\((\S+?)\)", r"\1: \2", text)
    return re.sub(r"\*\*(.+?)\*\*", r"\1", text).replace("`", "").strip()


def write_table(pdf: FPDF, rows: list[list[str]]) -> None:
    columns = max(len(r) for r in rows)
    rows = [r + [""] * (columns - len(r)) for r in rows]
    # Wider columns for longer text, so short columns like "#" stay narrow.
    widths = [max(4, min(40, max(len(r[i]) for r in rows))) for i in range(columns)]
    pdf.ln(1)
    pdf.set_font("Body", size=7)
    with pdf.table(col_widths=widths, line_height=3.5, padding=1, text_align="LEFT",
                   headings_style=FontFace(emphasis="", fill_color=(230, 230, 230))) as table:
        for row in rows:
            table.row(row)
    pdf.ln(2)


def write_pdf(config: str, report: str, path: str) -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("Body", fname=FONT)
    pdf.add_page()
    write_markdown(pdf, config)
    pdf.add_page()
    write_markdown(pdf, "# Report\n\n" + report)
    pdf.output(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("task", nargs="*", help="the research question")
    parser.add_argument("--task-file", help="read the research question from a file")
    parser.add_argument("--session", help="rebuild the files from an earlier session instead of running")
    args = parser.parse_args()

    load_dotenv()  # reads ANTHROPIC_API_KEY from .env
    client = anthropic.Anthropic()

    if args.session:
        session_id = args.session
    else:
        task_file = args.task_file or (None if args.task else "task.txt")
        task = open(task_file, encoding="utf-8").read().strip() if task_file else " ".join(args.task)
        session_id = run(client, task)

    if not save_run(client, session_id):
        sys.exit("The agent returned no report.")
    print("Saved run_config.md, report.md and report.pdf")


def save_run(client: anthropic.Anthropic, session_id: str, folder: str = ".") -> bool:
    """Write run_config.md, report.md and report.pdf for a finished session into folder."""
    task, report = read_session(client, session_id)
    if not report:
        return False
    session = client.beta.sessions.retrieve(session_id=session_id)
    config = build_document(client, session=session, task=task)

    with open(f"{folder}/run_config.md", "w", encoding="utf-8") as f:
        f.write(config + "\n")
    with open(f"{folder}/report.md", "w", encoding="utf-8") as f:
        f.write(report + "\n")
    write_pdf(config, report, f"{folder}/report.pdf")
    return True


if __name__ == "__main__":
    main()
