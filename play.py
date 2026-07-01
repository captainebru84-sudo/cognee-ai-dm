"""CLI driver for the AI Dungeon Master.

Usage:
    .venv/Scripts/python.exe play.py

Type a player action at the prompt; the GM narrates. Empty line or Ctrl-C to exit.
"""

import asyncio
import logging
import os

from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("COGNEE_SKIP_CONNECTION_TEST", "true")

# Silence Cognee's structlog chatter so the narration is the only thing on screen.
# Errors still propagate (set to ERROR not CRITICAL).
for name in ("cognee", "litellm", "httpx", "httpcore", "openai"):
    logging.getLogger(name).setLevel(logging.ERROR)
logging.disable(logging.INFO)

from dm import narrate  # imported after logging config so Cognee init is quiet


async def main() -> None:
    print("=" * 70)
    print("THE RAVENHOLLOW CHRONICLE — Session 4")
    print("=" * 70)
    print("Type a player action. Empty line or Ctrl-C to exit.\n")

    while True:
        try:
            action = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSession ends. The world remembers.")
            return

        if not action:
            print("Session ends. The world remembers.")
            return

        print("\n[GM is thinking...]\n")
        try:
            narration = await narrate(action)
        except Exception as e:
            print(f"[narration failed: {e}]\n")
            continue

        print(narration)
        print()


if __name__ == "__main__":
    asyncio.run(main())
