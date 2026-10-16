"""List the Managed Agents on the Claude platform and save them to agents.md."""

import anthropic
from dotenv import load_dotenv

load_dotenv()  # reads ANTHROPIC_API_KEY from .env
client = anthropic.Anthropic()

rows = []
for agent in client.beta.agents.list():
    model = getattr(agent.model, "id", agent.model)
    rows.append(f"| {agent.name} | `{agent.id}` | {model} | {agent.version} |")

lines = [
    "# Agents on the Claude platform",
    "",
    "| Name | ID | Model | Version |",
    "|---|---|---|---|",
    *rows,
    "",
    f"Total: {len(rows)}",
]
output = "\n".join(lines)
print(output)
with open("agents.md", "w", encoding="utf-8") as f:
    f.write(output + "\n")
