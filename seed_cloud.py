"""Seed Ravenhollow Chronicle Sessions 1-3 into Cognee Cloud tenant.

Runs once before the first Cloud-backed session. Uses CloudClient directly so
extraction happens server-side on Cognee's infra, not locally.

Usage:
    .venv/Scripts/python.exe seed_cloud.py
"""

import asyncio
import os

from dotenv import load_dotenv

from canon import SESSIONS

load_dotenv()


async def main() -> None:
    from cognee.api.v1.serve.cloud_client import CloudClient

    url = os.environ["COGNEE_SERVICE_URL"]
    key = os.environ["COGNEE_API_KEY"]

    print("=" * 70)
    print("Seeding Ravenhollow Chronicle to Cognee Cloud")
    print(f"Tenant: {url}")
    print("=" * 70)

    client = CloudClient(url, key)

    print("\n[health check]")
    healthy = await client._health_check()
    print(f"    healthy = {healthy}")
    if not healthy:
        print("    aborting — remote tenant did not respond to /health")
        await client.close()
        return

    try:
        for i, session_text in enumerate(SESSIONS, start=1):
            print(f"\n[{i}/{len(SESSIONS)}] Ingesting Session {i} ({len(session_text)} chars)")
            result = await client.remember(session_text, dataset_name="ravenhollow")
            print(f"    result: {result}")

        print("\n" + "=" * 70)
        print("WORLD SEEDED IN CLOUD. Dataset: ravenhollow")
        print("Next: python day3_cloud_smoke.py")
        print("=" * 70)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
