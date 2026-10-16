"""Download the reports from the scheduled runs and save each one as a PDF.

Each finished run is saved in reports/<date>_<time>/ (Israel time) with
report.pdf, report.md and run_config.md. Runs already saved are skipped.
"""

import os
from zoneinfo import ZoneInfo

import anthropic
from dotenv import load_dotenv

from run_agent import save_run
from schedule import DEPLOYMENT_ID, TIMEZONE


def main() -> None:
    load_dotenv()  # reads ANTHROPIC_API_KEY from .env
    client = anthropic.Anthropic()
    for run in client.beta.deployment_runs.list(deployment_id=DEPLOYMENT_ID):
        when = run.created_at.astimezone(ZoneInfo(TIMEZONE))
        if run.error:
            print(f"{when:%Y-%m-%d %H:%M}: failed ({run.error.type}: {run.error.message})")
            continue
        folder = f"reports/{when:%Y-%m-%d_%H%M}"
        if os.path.exists(f"{folder}/report.pdf"):
            continue
        session = client.beta.sessions.retrieve(session_id=run.session_id)
        if session.status != "idle":
            print(f"{when:%Y-%m-%d %H:%M}: still {session.status}, try again later")
            continue
        os.makedirs(folder, exist_ok=True)
        if save_run(client, run.session_id, folder):
            print(f"{when:%Y-%m-%d %H:%M}: saved {folder}/report.pdf")
        else:
            os.rmdir(folder)
            print(f"{when:%Y-%m-%d %H:%M}: the agent returned no report")


if __name__ == "__main__":
    main()
