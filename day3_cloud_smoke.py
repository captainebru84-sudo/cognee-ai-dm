"""Day 3 smoke test — same as Day 2 but backed by Cognee Cloud tenant.

Forces MEMORY_BACKEND=cloud regardless of what .env says. Expects canon hits
comparable to Day 2's 12/12 local score (cloud-side extraction may differ
slightly since Cognee re-derives on their infra).

Usage: .venv/Scripts/python.exe day3_cloud_smoke.py
"""

import asyncio
import os

from dotenv import load_dotenv

load_dotenv()
os.environ["MEMORY_BACKEND"] = "cloud"
os.environ["DEBUG_RECALL"] = "1"

# Import AFTER setting MEMORY_BACKEND — dm.py reads env at module load.
from dm import narrate, _build_cloud_client  # noqa: E402


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
    print("DAY 3 SMOKE TEST — Cognee Cloud backend live")
    print("=" * 70)

    print(f"\n[player action]\n{PLAYER_ACTION}\n")

    memory_client = _build_cloud_client()
    try:
        narration = await narrate(PLAYER_ACTION, memory_client=memory_client)
    finally:
        await memory_client.close()

    print("\n[narration]")
    print(narration)

    hits = [kw for kw in CANON_KEYWORDS if kw.lower() in narration.lower()]
    print("\n" + "=" * 70)
    print(f"Canon hits in narration ({len(hits)}/{len(CANON_KEYWORDS)}): {hits}")
    print("Day 2 local baseline: 12/12. Target on Cloud: >= 8.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
