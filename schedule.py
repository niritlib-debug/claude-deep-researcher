"""Schedule the Deep researcher agent to run automatically on the Claude platform.

Edit the settings below (or task.txt), then run this script to apply them.
The platform runs the agent in the cloud, so your computer can be off.
"""

import anthropic
from dotenv import load_dotenv

from agent_config import AGENT_ID, ENVIRONMENT_ID

DEPLOYMENT_ID = "depl_01Nd6WF5oFfHcKyCZmy1hjGi"
NAME = "Senior QA jobs - twice daily"
CRON = "0 8,20 * * *"  # minute hour day month weekday: 08:00 and 20:00 every day
TIMEZONE = "Asia/Jerusalem"
BUDGET_CENTS = "500"  # spending cap per run: $5.00
TASK_FILE = "task.txt"


def main() -> None:
    load_dotenv()  # reads ANTHROPIC_API_KEY from .env
    client = anthropic.Anthropic()
    task = open(TASK_FILE, encoding="utf-8").read().strip()
    deployment = client.beta.deployments.update(
        DEPLOYMENT_ID,
        name=NAME,
        agent=AGENT_ID,
        environment_id=ENVIRONMENT_ID,
        initial_events=[{"type": "user.message", "content": [{"type": "text", "text": task}]}],
        schedule={"type": "cron", "expression": CRON, "timezone": TIMEZONE},
        budget={"type": "limit", "max_list_cost": {"amount": BUDGET_CENTS, "currency": "USD"}},
    )
    print(f"{deployment.name} ({deployment.id}): {deployment.status}")
    print(f"Schedule: {deployment.schedule.expression} {deployment.schedule.timezone}")
    print("Next runs (UTC):", *deployment.schedule.upcoming_runs_at[:4], sep="\n  ")


if __name__ == "__main__":
    main()
