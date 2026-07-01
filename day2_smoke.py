"""Day 2 smoke test — verify the auto-rewriter fixes recall.

Same player input as day1_smoke.py, but now narrate() should first rewrite the
declaration into a canon question, then recall, then narrate. Expect canon
keywords (Mirek, Aldric, amulet, debt) to appear in the narration.

Usage: .venv/Scripts/python.exe day2_smoke.py
"""

import asyncio
import os

from dotenv import load_dotenv

from dm import narrate

load_dotenv()
os.environ.setdefault("COGNEE_SKIP_CONNECTION_TEST", "true")
os.environ["DEBUG_RECALL"] = "1"


PLAYER_ACTION = (
    "I push open the door of The Salt Lantern and step inside, "
    "shaking the rain off my cloak. I scan the room for Bren."
)


CANON_KEYWORDS = [
    "Bren", "Mirek", "Aldric", "Joren", "Kara", "Vell", "Vohr",
    "Salt Lantern", "amulet", "debt", "betray", "scar",
]


async def main() -> None:
    print("=" * 70)
    print("DAY 2 SMOKE TEST — recall rewriter wired into narrate()")
    print("=" * 70)

    print(f"\n[player action]\n{PLAYER_ACTION}\n")

    narration = await narrate(PLAYER_ACTION)

    print("\n[narration]")
    print(narration)

    hits = [kw for kw in CANON_KEYWORDS if kw.lower() in narration.lower()]
    print("\n" + "=" * 70)
    print(f"Canon hits in narration ({len(hits)}/{len(CANON_KEYWORDS)}): {hits}")
    print("Yesterday's narration scored 1/12 (only Bren). Target: 4+.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
