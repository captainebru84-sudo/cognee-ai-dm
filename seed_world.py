"""Ingest the Ravenhollow Chronicle canon into Cognee.

Run once before the first session: builds the memory graph from Sessions 1-3.
Re-running is idempotent in principle but slow — Cognee re-extracts each time.

Usage:
    .venv/Scripts/python.exe seed_world.py
"""

import asyncio
import os

import cognee
from dotenv import load_dotenv

from canon import SESSIONS

load_dotenv()
os.environ.setdefault("COGNEE_SKIP_CONNECTION_TEST", "true")


async def main() -> None:
    print("=" * 70)
    print("Seeding Ravenhollow Chronicle — Sessions 1-3")
    print("=" * 70)

    for i, session_text in enumerate(SESSIONS, start=1):
        print(f"\n[{i}/{len(SESSIONS)}] Ingesting Session {i} ({len(session_text)} chars)")
        result = await cognee.remember(session_text)
        print(f"      result: {result}")

    print("\n" + "=" * 70)
    print("WORLD SEEDED — Ravenhollow canon is live in Cognee.")
    print("Next: python play.py")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
