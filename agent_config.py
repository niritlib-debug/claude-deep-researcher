"""Build a configuration document for a Managed Agent from the live platform settings."""

from datetime import datetime, timezone

AGENT_ID = "agent_01WedaF6x8gmapUohSFzrcnk"
ENVIRONMENT_ID = "env_01PHBKTH7GTnCMHTpdAP16ak"  # deep-research-env

# Built-in tools in agent_toolset_20260401
TOOLSET_TOOLS = {
    "bash": "Run shell commands in the session container",
    "read": "Read a file (text, images, PDFs, notebooks)",
    "write": "Write a file",
    "edit": "Replace text in a file",
    "glob": "Find files by name pattern",
    "grep": "Search file contents with regex",
    "web_fetch": "Fetch the content of a URL",
    "web_search": "Search the web",
}


def _policy(config) -> str:
    policy = getattr(config, "permission_policy", None)
    return getattr(policy, "type", "default") if policy else "default"


def describe_tools(tools) -> list[str]:
    lines = []
    for tool in tools:
        if tool.type.startswith("agent_toolset"):
            default = tool.default_config
            overrides = {c.name: c for c in (tool.configs or [])}
            lines.append(f"- Toolset `{tool.type}` (built-in tools):")
            for name, purpose in TOOLSET_TOOLS.items():
                config = overrides.get(name, default)
                enabled = getattr(config, "enabled", None)
                if enabled is None:
                    enabled = getattr(default, "enabled", True)
                state = "enabled" if enabled else "disabled"
                policy = _policy(config)
                if policy == "default":
                    policy = _policy(default)
                lines.append(f"    - `{name}`: {purpose} ({state}, permission: {policy})")
        elif tool.type == "custom":
            lines.append(f"- Custom tool `{tool.name}`: {tool.description}")
        else:
            lines.append(f"- `{tool.type}`")
    return lines or ["- No tools"]


def describe_agent(agent) -> list[str]:
    model = agent.model
    effort = getattr(getattr(model, "effort", None), "type", None) or "default"
    return [
        "## Agent",
        "",
        f"- Name: {agent.name}",
        f"- ID: `{agent.id}` (version {agent.version})",
        f"- Description: {agent.description or '-'}",
        "",
        "## Model",
        "",
        f"- Model: `{model.id}`",
        f"- Effort: {effort}",
        f"- Speed: {getattr(model, 'speed', None) or 'standard'}",
        f"- Inference region: {getattr(model, 'inference_geo', None) or 'default'}",
        "",
        "## Tools",
        "",
        *describe_tools(agent.tools),
        f"- MCP servers: {len(agent.mcp_servers or [])}",
        f"- Skills: {len(agent.skills or [])}",
        f"- Multi-agent: {'on' if agent.multiagent else 'off'}",
        "",
        "## System prompt (the agent's standing instructions)",
        "",
        *agent.system.splitlines(),
        "",
    ]


def describe_environment(env) -> list[str]:
    packages = env.config.packages
    installed = [f"{kind}: {', '.join(getattr(packages, kind))}"
                 for kind in ("pip", "npm", "apt", "cargo", "gem", "go") if getattr(packages, kind)]
    return [
        "## Environment (where the tools run)",
        "",
        f"- Name: {env.name} (`{env.id}`)",
        f"- Type: {env.config.type} container",
        f"- Network access: {env.config.networking.type}",
        f"- Extra packages: {'; '.join(installed) or 'none'}",
        "",
    ]


def describe_run(session, task: str) -> list[str]:
    usage = session.usage
    cost = int(usage.list_cost.amount) / 100 if usage.list_cost else None
    budget = session.budget.max_list_cost if session.budget else None
    return [
        "## Task (the prompt sent for this run)",
        "",
        *task.splitlines(),
        "",
        "## Run",
        "",
        f"- Session: `{session.id}`",
        f"- Started: {session.created_at:%Y-%m-%d %H:%M} UTC",
        f"- Working time: {usage.active_seconds:.0f} seconds",
        f"- Tokens: {usage.input_tokens + usage.cache_read_input_tokens + usage.cache_creation.ephemeral_5m_input_tokens + usage.cache_creation.ephemeral_1h_input_tokens:,} input, {usage.output_tokens:,} output",
        f"- Web searches: {usage.server_tool_use.web_search_requests}",
        f"- Cost (list price): {f'${cost:.2f}' if cost is not None else 'unknown'}"
        + (f" (budget cap ${int(budget.amount) / 100:.2f})" if budget else ""),
        "",
    ]


def build_document(client, session=None, task: str | None = None) -> str:
    agent = client.beta.agents.retrieve(AGENT_ID)
    env = client.beta.environments.retrieve(ENVIRONMENT_ID)
    lines = [
        "# Agent configuration",
        "",
        f"Read from the Claude platform on {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC.",
        "",
        *describe_agent(agent),
        *describe_environment(env),
    ]
    if session is not None:
        lines += describe_run(session, task or "")
    return "\n".join(lines)
