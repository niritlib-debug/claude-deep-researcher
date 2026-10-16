"""Run the Deep researcher agent on a topic and save its report as a PDF.

Usage: python run_agent.py "your research question"
"""

import re
import sys

import anthropic
from dotenv import load_dotenv
from fpdf import FPDF

AGENT_ID = "agent_01WedaF6x8gmapUohSFzrcnk"
ENVIRONMENT_ID = "env_01PHBKTH7GTnCMHTpdAP16ak"  # deep-research-env
FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"


def run(client: anthropic.Anthropic, topic: str) -> str:
    session = client.beta.sessions.create(
        agent=AGENT_ID,
        environment_id=ENVIRONMENT_ID,
        title=topic[:80],
    )
    print(f"Session: {session.id}")
    messages = []
    with client.beta.sessions.events.stream(session_id=session.id) as stream:
        client.beta.sessions.events.send(
            session_id=session.id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": topic}]}],
        )
        for event in stream:
            if event.type == "agent.message":
                text = "".join(b.text for b in event.content if b.type == "text")
                messages.append(text)
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
    # The report is the agent's final message.
    return messages[-1] if messages else ""


def write_pdf(title: str, report: str, path: str) -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("Body", fname=FONT)
    pdf.add_page()
    pdf.set_font("Body", size=18)
    pdf.multi_cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    for line in report.splitlines():
        heading = re.match(r"^(#{1,6})\s+(.*)", line)
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", heading.group(2) if heading else line)
        if heading:
            pdf.ln(2)
            pdf.set_font("Body", size=max(16 - 2 * len(heading.group(1)), 11))
            pdf.multi_cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("Body", size=10)
            pdf.multi_cell(0, 5, text or " ", new_x="LMARGIN", new_y="NEXT")
    pdf.output(path)


if __name__ == "__main__":
    load_dotenv()  # reads ANTHROPIC_API_KEY from .env
    topic = " ".join(sys.argv[1:]) or sys.exit("Usage: python run_agent.py \"research question\"")
    report = run(anthropic.Anthropic(), topic)
    if not report:
        sys.exit("The agent returned no report.")
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report + "\n")
    write_pdf(topic, report, "report.pdf")
    print("Saved report.md and report.pdf")
