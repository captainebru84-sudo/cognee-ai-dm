"""AI Dungeon Master core loop: recall -> narrate -> remember.

`narrate(player_action)` is the only entry point. It:
  1. Pulls relevant past events from Cognee via `cognee.recall()`.
  2. Calls the configured narration LLM for cinematic prose.
  3. Writes the action+narration pair back to Cognee for future recall.

Narration provider is selected by NARRATION_PROVIDER:
  - "anthropic" -> anthropic SDK, NARRATION_MODEL like 'claude-haiku-4-5-20251001'
  - "groq" (or any OpenAI-compatible endpoint) -> openai SDK pointed at NARRATION_BASE_URL,
    NARRATION_MODEL like 'llama-3.3-70b-versatile'

Cognee handles its own LLM-side extraction internally (Groq llama-3.3-70b
via LLM_* vars). Narration is a separate concern.
"""

import os
from typing import Optional, Union

import cognee
from dotenv import load_dotenv

from prompts import NARRATION_SYSTEM_PROMPT, NARRATION_USER_TEMPLATE

load_dotenv()

_PROVIDER = os.getenv("NARRATION_PROVIDER", "anthropic").lower()
_MODEL = os.getenv("NARRATION_MODEL", "claude-haiku-4-5-20251001")
_BASE_URL = os.getenv("NARRATION_BASE_URL")
_API_KEY = os.getenv("NARRATION_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

_MEMORY_BACKEND = os.getenv("MEMORY_BACKEND", "local").lower()
_COGNEE_SERVICE_URL = os.getenv("COGNEE_SERVICE_URL")
_COGNEE_API_KEY = os.getenv("COGNEE_API_KEY")
_CLOUD_DATASET = os.getenv("CLOUD_DATASET", "ravenhollow")

NarrationClient = Union["anthropic.AsyncAnthropic", "openai.AsyncOpenAI"]


def _build_client() -> NarrationClient:
    if _PROVIDER == "anthropic":
        import anthropic
        return anthropic.AsyncAnthropic(api_key=_API_KEY)
    import openai
    return openai.AsyncOpenAI(api_key=_API_KEY, base_url=_BASE_URL)


async def _narrate_anthropic(
    client: "anthropic.AsyncAnthropic", recall_context: str, player_action: str
) -> str:
    response = await client.messages.create(
        model=_MODEL,
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": NARRATION_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": NARRATION_USER_TEMPLATE.format(
                    recall_context=recall_context, player_action=player_action
                ),
            }
        ],
    )
    return next((b.text for b in response.content if b.type == "text"), "")


async def _narrate_openai_compat(
    client: "openai.AsyncOpenAI", recall_context: str, player_action: str
) -> str:
    response = await client.chat.completions.create(
        model=_MODEL,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": NARRATION_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": NARRATION_USER_TEMPLATE.format(
                    recall_context=recall_context, player_action=player_action
                ),
            },
        ],
    )
    return response.choices[0].message.content or ""


WORLD_CAST_FOR_QUERY = (
    "Bren, Aldric, Mirek the Hawk, Joren, Kara, Dax, Captain Vell, Petris, "
    "High Priestess Saerith, The Salt Lantern, Temple of Vohr, the salt mines, "
    "the docks, the Amulet of Vohr, Black Iron smuggling, Ravenhollow"
)


def _rewrite_for_recall(player_action: str) -> str:
    """Deterministic rewriter — always asks the graph about every cast member.

    Cognee's GRAPH_COMPLETION traversal filters to the nodes that actually
    matter for the scene; over-naming entities up front beats LLM-driven
    rewriting at our current canon size (~50 graph nodes).
    """
    return (
        f"What canon exists about: {WORLD_CAST_FOR_QUERY}? "
        f"Player just declared: {player_action}"
    )


def _build_cloud_client():
    """Instantiate Cognee CloudClient from env creds."""
    if not _COGNEE_SERVICE_URL or not _COGNEE_API_KEY:
        raise RuntimeError(
            "MEMORY_BACKEND=cloud requires COGNEE_SERVICE_URL and COGNEE_API_KEY in env"
        )
    from cognee.api.v1.serve.cloud_client import CloudClient
    return CloudClient(_COGNEE_SERVICE_URL, _COGNEE_API_KEY)


async def narrate(
    player_action: str,
    *,
    client: Optional[NarrationClient] = None,
    memory_client=None,
) -> str:
    """Run one turn of the AI DM loop.

    Args:
        player_action: What the player(s) just declared. Free-form prose.
        client: Optional pre-built provider client. Built fresh if None.
        memory_client: Optional pre-built Cognee CloudClient (cloud backend only).
            Reusing across calls avoids per-turn HTTP session churn.

    Returns:
        The narration text shown to the player.
    """
    if client is None:
        client = _build_client()

    recall_query = _rewrite_for_recall(player_action)
    if os.getenv("DEBUG_RECALL"):
        print(f"[recall query] {recall_query}")

    if _MEMORY_BACKEND == "cloud":
        cloud = memory_client or _build_cloud_client()
        recall_result = await cloud.recall(recall_query, datasets=[_CLOUD_DATASET])
        recall_context = str(recall_result) if recall_result else ""
    else:
        recall_result = await cognee.recall(recall_query)
        recall_context = str(recall_result) if recall_result else ""

    if _PROVIDER == "anthropic":
        narration = await _narrate_anthropic(client, recall_context, player_action)
    else:
        narration = await _narrate_openai_compat(client, recall_context, player_action)

    if narration:
        turn_text = f"Player action: {player_action}\nGM narration: {narration}"
        if _MEMORY_BACKEND == "cloud":
            cloud = memory_client or _build_cloud_client()
            try:
                await cloud.remember(turn_text, dataset_name=_CLOUD_DATASET)
            except RuntimeError as e:
                # Cognee Cloud remember has an intermittent 409 hash-mismatch
                # bug in dev. Log and continue — read path (recall) is what
                # the demo needs; write-back grows the graph for later turns.
                print(f"[warn] cloud remember failed, continuing: {e}")

    return narration
