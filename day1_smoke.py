"""Day 1 smoke test — one narration through the full loop.

Verifies: seed worked, recall fires, Claude narrates with context, write-back runs.
Prints recall payload + narration so we can eyeball whether the demo moment lands.

Usage: .venv/Scripts/python.exe day1_smoke.py
"""

import asyncio
import os

import cognee
from dotenv import load_dotenv

from dm import narrate

load_dotenv()
os.environ.setdefault("COGNEE_SKIP_CONNECTION_TEST", "true")


PLAYER_ACTION = (
    "I push open the door of The Salt Lantern and step inside, "
    "shaking the rain off my cloak. I scan the room for Bren."
)


async def main() -> None:
    print("=" * 70)
    print("DAY 1 SMOKE TEST — Ravenhollow recall + Claude narration")
    print("=" * 70)

    print(f"\n[player action]\n{PLAYER_ACTION}\n")

    print("[recall raw]")
    recall = await cognee.recall(PLAYER_ACTION)
    print(repr(recall)[:1000])
    print()

    print("[narration]")
    narration = await narrate(PLAYER_ACTION)
    print(narration)
    print()

    print("=" * 70)
    print("Check: does the narration reference Bren / Mirek / Aldric / amulet?")
    print("If yes, the world remembers. If no, recall or prompt needs tuning.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
