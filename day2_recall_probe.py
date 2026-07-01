"""Day 2 recall probe — find which SearchType surfaces Ravenhollow canon.

Tests the same player declaration AND a manually-rewritten canon query
against multiple Cognee search types, so we can pick the winner before
building the auto-rewriter.

Usage: .venv/Scripts/python.exe day2_recall_probe.py
"""

import asyncio
import os

import cognee
from cognee.modules.search.types import SearchType
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("COGNEE_SKIP_CONNECTION_TEST", "true")


PLAYER_RAW = (
    "I push open the door of The Salt Lantern and step inside, "
    "shaking the rain off my cloak. I scan the room for Bren."
)

PLAYER_REWRITTEN = (
    "What canon exists about: The Salt Lantern tavern, Bren the barkeep, "
    "Mirek the Hawk, Joren the wizard's gambling debt, Aldric Bren's brother, "
    "Captain Vell, the Amulet of Vohr, the rogue Kara?"
)


SEARCH_TYPES_TO_PROBE = [
    SearchType.CHUNKS,
    SearchType.CHUNKS_LEXICAL,
    SearchType.SUMMARIES,
    SearchType.RAG_COMPLETION,
    SearchType.GRAPH_COMPLETION,
    SearchType.GRAPH_SUMMARY_COMPLETION,
    SearchType.TRIPLET_COMPLETION,
]


CANON_KEYWORDS = [
    "Bren", "Mirek", "Aldric", "Joren", "Kara", "Vell", "Vohr",
    "Salt Lantern", "amulet", "debt", "betray", "scar",
]


def score_canon_hit(text: str) -> tuple[int, list[str]]:
    hits = [kw for kw in CANON_KEYWORDS if kw.lower() in text.lower()]
    return len(hits), hits


async def probe(query_text: str, label: str) -> None:
    print()
    print("#" * 70)
    print(f"# QUERY ({label}):")
    print(f"# {query_text}")
    print("#" * 70)
    for st in SEARCH_TYPES_TO_PROBE:
        try:
            result = await cognee.search(query_text=query_text, query_type=st)
            text_blob = str(result)
            score, hits = score_canon_hit(text_blob)
            print()
            print(f"--- {st.name}  (canon hits: {score} :: {hits}) ---")
            print(text_blob[:1500])
            if len(text_blob) > 1500:
                print(f"... [truncated, total {len(text_blob)} chars]")
        except Exception as exc:
            print()
            print(f"--- {st.name}  [ERROR] ---")
            print(f"{type(exc).__name__}: {exc}")


async def main() -> None:
    print("=" * 70)
    print("DAY 2 RECALL PROBE")
    print("=" * 70)
    await probe(PLAYER_RAW, "raw player declaration")
    await probe(PLAYER_REWRITTEN, "manually-rewritten canon query")
    print()
    print("=" * 70)
    print("Pick the search type with the highest canon hits on the REWRITTEN")
    print("query. That's what the auto-rewriter feeds into for Task 3.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
