"""Write the Deep researcher agent's configuration to AGENT_CONFIG.md."""

import anthropic
from dotenv import load_dotenv

from agent_config import build_document

load_dotenv()  # reads ANTHROPIC_API_KEY from .env
document = build_document(anthropic.Anthropic())
with open("AGENT_CONFIG.md", "w", encoding="utf-8") as f:
    f.write(document + "\n")
print(document)
