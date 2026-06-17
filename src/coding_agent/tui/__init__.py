import os
import sys

from coding_agent.config import Config


def should_use_tui(*, plain: bool = False) -> bool:
    if plain:
        return False
    if os.environ.get("CODING_AGENT_PLAIN_PROMPT"):
        return False
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return False
    return sys.stdin.isatty() and sys.stdout.isatty()


def run_tui(config: Config, session) -> None:
    from coding_agent.tui.app import CodingAgentApp

    app = CodingAgentApp(config, session)
    app.run()
