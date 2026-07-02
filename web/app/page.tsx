"use client";

import { useState, useRef, useEffect, FormEvent } from "react";

type Turn = { role: "player" | "gm"; text: string };

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export default function Home() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [turns, busy]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const action = input.trim();
    if (!action || busy) return;

    setInput("");
    setError(null);
    setTurns((t) => [...t, { role: "player", text: action }]);
    setBusy(true);

    try {
      const res = await fetch(`${API_BASE}/narrate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ player_action: action }),
      });
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      const data: { narration: string } = await res.json();
      setTurns((t) => [...t, { role: "gm", text: data.narration }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex h-screen flex-col bg-zinc-950 text-zinc-100">
      <header className="border-b border-zinc-800 px-6 py-4">
        <h1 className="text-xl font-semibold tracking-tight text-amber-200">
          The Ravenhollow Chronicle
        </h1>
        <p className="text-xs text-zinc-500">
          Session 4 &middot; The world remembers.
        </p>
      </header>

      <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-8">
        <div className="mx-auto flex max-w-3xl flex-col gap-6">
          {turns.length === 0 && (
            <div className="rounded-md border border-zinc-800 bg-zinc-900/40 p-6 text-sm leading-relaxed text-zinc-400">
              You stand at the door of The Salt Lantern. Rain drips off your
              cloak. Tell the GM what you do next &mdash; every NPC remembers
              Sessions 1&ndash;3, even if you don&apos;t.
            </div>
          )}
          {turns.map((turn, i) =>
            turn.role === "player" ? (
              <div key={i} className="ml-12 self-end max-w-[85%]">
                <div className="mb-1 text-xs uppercase tracking-wide text-zinc-500">
                  You
                </div>
                <div className="rounded-lg border border-zinc-700 bg-zinc-800/60 px-4 py-3 text-sm leading-relaxed">
                  {turn.text}
                </div>
              </div>
            ) : (
              <div key={i} className="mr-12 max-w-[85%]">
                <div className="mb-1 text-xs uppercase tracking-wide text-amber-300/80">
                  Dungeon Master
                </div>
                <div className="whitespace-pre-wrap rounded-lg border border-amber-900/40 bg-amber-950/20 px-4 py-3 text-sm leading-relaxed text-amber-50">
                  {turn.text}
                </div>
              </div>
            )
          )}
          {busy && (
            <div className="mr-12 max-w-[85%]">
              <div className="mb-1 text-xs uppercase tracking-wide text-amber-300/80">
                Dungeon Master
              </div>
              <div className="rounded-lg border border-amber-900/40 bg-amber-950/20 px-4 py-3 text-sm italic text-amber-200/60">
                The world stirs, remembering&hellip;
              </div>
            </div>
          )}
          {error && (
            <div className="rounded-md border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-300">
              Error: {error}
            </div>
          )}
        </div>
      </div>

      <form
        onSubmit={onSubmit}
        className="border-t border-zinc-800 bg-zinc-900/60 px-6 py-4"
      >
        <div className="mx-auto flex max-w-3xl gap-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                onSubmit(e as unknown as FormEvent);
              }
            }}
            placeholder="I push open the door of The Salt Lantern&hellip;"
            rows={2}
            disabled={busy}
            className="flex-1 resize-none rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm placeholder:text-zinc-600 focus:border-amber-700 focus:outline-none disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={busy || !input.trim()}
            className="rounded-md border border-amber-700/60 bg-amber-900/40 px-4 py-2 text-sm font-medium text-amber-100 transition-colors hover:bg-amber-900/60 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {busy ? "…" : "Act"}
          </button>
        </div>
      </form>
    </div>
  );
}
