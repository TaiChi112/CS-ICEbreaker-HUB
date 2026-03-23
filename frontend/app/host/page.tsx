"use client";

export const dynamic = "force-dynamic";

import { useCallback, useEffect, useMemo, useState } from "react";

import { generateQuestions, getClaimableQuestions, getRoomState } from "../../lib/api";
import type { ClaimableQuestionsResponse, RoomStateResponse, WsEnvelope } from "../../lib/contracts";
import { useRoomSocket } from "../../hooks/useRoomSocket";

const EMPTY_ROOM_STATE: RoomStateResponse = {
  room_id: "",
  room_code: "",
  status: "lobby",
  players: [],
  leaderboard: [],
};

export default function HostDashboardPage() {
  const [roomCode, setRoomCode] = useState("");
  const [playerId, setPlayerId] = useState("");
  const [displayName, setDisplayName] = useState("Host");

  const [roomState, setRoomState] = useState<RoomStateResponse>(EMPTY_ROOM_STATE);
  const [claimable, setClaimable] = useState<ClaimableQuestionsResponse>({ room_code: roomCode, questions: [] });
  const [topic, setTopic] = useState("Computer Networks");
  const [batchSize, setBatchSize] = useState(8);
  const [events, setEvents] = useState<string[]>([]);
  const [statusMessage, setStatusMessage] = useState("");

  const refreshRoomData = useCallback(async () => {
    if (!roomCode) {
      return;
    }

    const [state, available] = await Promise.all([getRoomState(roomCode), getClaimableQuestions(roomCode)]);
    setRoomState(state);
    setClaimable(available);
  }, [roomCode]);

  const onEvent = useCallback((event: WsEnvelope) => {
    setEvents((prev) => [`${event.type} @ ${new Date(event.occurredAt).toLocaleTimeString()}`, ...prev].slice(0, 18));
    void refreshRoomData();
  }, [refreshRoomData]);

  const { connected, lastError } = useRoomSocket({
    roomCode,
    playerId,
    displayName,
    onEvent,
  });

  useEffect(() => {
    const search = new URLSearchParams(globalThis.location.search);
    setRoomCode((search.get("roomCode") ?? "").toUpperCase());
    setPlayerId(search.get("playerId") ?? "");
    setDisplayName(search.get("displayName") ?? "Host");
  }, []);

  useEffect(() => {
    void refreshRoomData();
  }, [refreshRoomData]);

  const onGenerate = async () => {
    if (!roomCode || !playerId) {
      setStatusMessage("Missing room context. Start from landing page to create a room.");
      return;
    }

    try {
      const generated = await generateQuestions(roomCode, {
        host_player_id: playerId,
        topic,
        batch_size: batchSize,
      });
      setStatusMessage(`Generated ${generated.question_count} questions for topic: ${generated.topic}`);
      await refreshRoomData();
    } catch {
      setStatusMessage("Could not generate questions. Verify backend and host permissions.");
    }
  };

  const playersCount = useMemo(() => roomState.players.length, [roomState.players.length]);

  return (
    <main className="min-h-screen bg-linear-to-b from-slate-950 via-slate-900 to-slate-800 p-4 text-slate-100">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-5 py-5">
        <header className="rounded-2xl border border-cyan-400/20 bg-slate-900/70 p-4 shadow-xl backdrop-blur">
          <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Host Dashboard</p>
          <h1 className="mt-1 text-2xl font-bold">Room {roomCode || "Not Connected"}</h1>
          <p className="mt-2 text-sm text-slate-300">
            WS: {connected ? "Connected" : "Disconnected"} | Players: {playersCount} | You: {displayName}
          </p>
          {lastError ? <p className="mt-2 text-sm text-rose-300">{lastError}</p> : null}
        </header>

        <section className="grid gap-5 lg:grid-cols-2">
          <article className="rounded-2xl border border-cyan-500/30 bg-slate-900/60 p-4">
            <h2 className="text-lg font-semibold">Generate Question Batch</h2>
            <label htmlFor="topic-input" className="mt-3 block text-sm">Topic</label>
            <input
              id="topic-input"
              value={topic}
              onChange={(event) => setTopic(event.target.value)}
              className="mt-2 w-full rounded-xl border border-cyan-500/50 bg-slate-950 px-3 py-2"
            />
            <label htmlFor="batch-size-input" className="mt-3 block text-sm">Batch Size</label>
            <input
              id="batch-size-input"
              type="number"
              min={1}
              max={20}
              value={batchSize}
              onChange={(event) => setBatchSize(Number(event.target.value))}
              className="mt-2 w-full rounded-xl border border-cyan-500/50 bg-slate-950 px-3 py-2"
            />
            <button
              type="button"
              onClick={onGenerate}
              className="mt-4 w-full rounded-xl bg-cyan-600 px-4 py-2 font-semibold text-white hover:bg-cyan-500"
            >
              Generate Questions
            </button>
            {statusMessage ? <p className="mt-3 text-sm text-cyan-200">{statusMessage}</p> : null}
          </article>

          <article className="rounded-2xl border border-violet-400/30 bg-slate-900/60 p-4">
            <h2 className="text-lg font-semibold">Live Room State</h2>
            <p className="mt-2 text-sm text-slate-300">Status: {roomState.status}</p>
            <ul className="mt-3 space-y-2">
              {roomState.players.map((player) => (
                <li key={player.player_id} className="rounded-xl bg-slate-800/80 px-3 py-2 text-sm">
                  {player.display_name} ({player.role})
                </li>
              ))}
            </ul>
          </article>
        </section>

        <section className="grid gap-5 lg:grid-cols-2">
          <article className="rounded-2xl border border-lime-400/30 bg-slate-900/60 p-4">
            <h2 className="text-lg font-semibold">Claimable Questions</h2>
            <ul className="mt-3 space-y-2">
              {claimable.questions.map((question) => (
                <li key={question.question_id} className="rounded-xl bg-slate-800/80 px-3 py-2 text-sm">
                  {question.prompt}
                </li>
              ))}
              {claimable.questions.length === 0 ? (
                <li className="rounded-xl bg-slate-800/80 px-3 py-2 text-sm text-slate-400">
                  No claimable questions yet.
                </li>
              ) : null}
            </ul>
          </article>

          <article className="rounded-2xl border border-amber-400/30 bg-slate-900/60 p-4">
            <h2 className="text-lg font-semibold">Realtime Event Feed</h2>
            <ul className="mt-3 max-h-64 space-y-2 overflow-auto text-sm">
              {events.map((eventText) => (
                <li key={eventText} className="rounded-lg bg-slate-800/80 px-3 py-2">
                  {eventText}
                </li>
              ))}
              {events.length === 0 ? (
                <li className="rounded-lg bg-slate-800/80 px-3 py-2 text-slate-400">No events yet.</li>
              ) : null}
            </ul>
          </article>
        </section>
      </div>
    </main>
  );
}
