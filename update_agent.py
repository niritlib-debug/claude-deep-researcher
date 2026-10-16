"""Apply system_prompt.md to the Deep researcher agent on the Claude platform.

Edit system_prompt.md (the agent's instructions and its job-search task), then run
this script. The platform keeps every version, so earlier versions stay available.
"""

import anthropic
from dotenv import load_dotenv

import schedule
from agent_config import AGENT_ID

PROMPT_FILE = "system_prompt.md"


def main() -> None:
    load_dotenv()  # reads ANTHROPIC_API_KEY from .env
    client = anthropic.Anthropic()
    system = open(PROMPT_FILE, encoding="utf-8").read().strip()
    current = client.beta.agents.retrieve(AGENT_ID)
    if current.system == system:
        print(f"No change: version {current.version} already uses {PROMPT_FILE}")
        return
    agent = client.beta.agents.update(AGENT_ID, version=current.version, system=system)
    print(f"{agent.name}: version {current.version} -> {agent.version}")
    # The schedule is pinned to an agent version, so move it to the new one.
    schedule.main()


if __name__ == "__main__":
    main()
