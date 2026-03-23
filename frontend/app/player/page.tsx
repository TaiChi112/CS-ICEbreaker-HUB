"use client";

export const dynamic = "force-dynamic";

import { useCallback, useEffect, useMemo, useState } from "react";

import { getClaimableQuestions, getRoomState } from "../../lib/api";
import type { ClaimableQuestionsResponse, GeneratedQuestion, RoomStateResponse, WsEnvelope } from "../../lib/contracts";
import { useRoomSocket } from "../../hooks/useRoomSocket";
import { QuestionRevealCard } from "../../components/QuestionRevealCard";

const EMPTY_ROOM_STATE: RoomStateResponse = {
  room_id: "",
  room_code: "",
  status: "lobby",
  players: [],
  leaderboard: [],
};

export default function PlayerRoomPage() {
  const [roomCode, setRoomCode] = useState("");
  const [playerId, setPlayerId] = useState("");
  const [displayName, setDisplayName] = useState("Player");

  const [roomState, setRoomState] = useState<RoomStateResponse>(EMPTY_ROOM_STATE);
  const [claimable, setClaimable] = useState<ClaimableQuestionsResponse>({ room_code: roomCode, questions: [] });
  const [statusMessage, setStatusMessage] = useState("");
  const [activeReveal, setActiveReveal] = useState<{ prompt: string; answer: string } | null>(null);

  const questionMap = useMemo(() => {
    const map = new Map<string, GeneratedQuestion>();
    for (const question of claimable.questions) {
      map.set(question.question_id, question);
    }
    return map;
  }, [claimable.questions]);

  const refreshRoomData = useCallback(async () => {
    if (!roomCode) {
      return;
    }
    const [state, available] = await Promise.all([getRoomState(roomCode), getClaimableQuestions(roomCode)]);
    setRoomState(state);
    setClaimable(available);
  }, [roomCode]);

  const onEvent = useCallback((event: WsEnvelope) => {
    if (event.type === "question.claimed") {
      const selectorPlayerId =
        typeof event.payload.selectorPlayerId === "string" ? event.payload.selectorPlayerId : "";
      const questionId = typeof event.payload.questionId === "string" ? event.payload.questionId : "";

      if (selectorPlayerId === playerId) {
        const selected = questionMap.get(questionId);
        setActiveReveal({
          prompt: selected?.prompt ?? "Claimed question",
          answer: "Answer is delivered in the physical interaction flow.",
        });
      }
    }

    if (event.type === "question.claim_rejected") {
      setStatusMessage("That question was already claimed by another player.");
    }

    void refreshRoomData();
  }, [playerId, questionMap, refreshRoomData]);

  const { connected, lastError, sendClaim } = useRoomSocket({
    roomCode,
    playerId,
    displayName,
    onEvent,
  });

  useEffect(() => {
    const search = new URLSearchParams(globalThis.location.search);
    setRoomCode((search.get("roomCode") ?? "").toUpperCase());
    setPlayerId(search.get("playerId") ?? "");
    setDisplayName(search.get("displayName") ?? "Player");
  }, []);

  useEffect(() => {
    void refreshRoomData();
  }, [refreshRoomData]);

  const onClaimQuestion = (questionId: string) => {
    const sent = sendClaim(questionId);
    if (!sent) {
      setStatusMessage("WebSocket is disconnected. Reconnect and try again.");
    }
  };

  return (
    <main className="min-h-screen bg-linear-to-b from-indigo-100 via-white to-cyan-100 p-4 text-slate-900">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-5 py-5">
        <header className="rounded-2xl border border-indigo-200 bg-white/80 p-4 shadow-xl backdrop-blur">
          <p className="text-xs uppercase tracking-[0.2em] text-indigo-700">Player Room</p>
          <h1 className="mt-1 text-2xl font-bold">Room {roomCode || "Not Connected"}</h1>
          <p className="mt-2 text-sm text-slate-700">
            WS: {connected ? "Connected" : "Disconnected"} | You: {displayName}
          </p>
          {lastError ? <p className="mt-2 text-sm text-rose-600">{lastError}</p> : null}
          {statusMessage ? <p className="mt-2 text-sm text-amber-700">{statusMessage}</p> : null}
        </header>

        <section className="grid gap-5 lg:grid-cols-2">
          <article className="rounded-2xl border border-indigo-300 bg-white/80 p-4 shadow">
            <h2 className="text-lg font-semibold">Available Questions</h2>
            <ul className="mt-3 space-y-3">
              {claimable.questions.map((question) => (
                <li key={question.question_id} className="rounded-xl border border-indigo-100 bg-indigo-50/70 p-3">
                  <p className="text-sm font-medium">{question.prompt}</p>
                  <button
                    type="button"
                    onClick={() => onClaimQuestion(question.question_id)}
                    className="mt-2 rounded-lg bg-indigo-700 px-3 py-1.5 text-sm font-semibold text-white hover:bg-indigo-600"
                  >
                    Claim Question
                  </button>
                </li>
              ))}
              {claimable.questions.length === 0 ? (
                <li className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-500">
                  No claimable questions currently available.
                </li>
              ) : null}
            </ul>
          </article>

          <article className="rounded-2xl border border-cyan-300 bg-white/80 p-4 shadow">
            <h2 className="text-lg font-semibold">Live Leaderboard</h2>
            <ul className="mt-3 space-y-2">
              {roomState.leaderboard.map((row, index) => (
                <li key={row.player_id} className="flex items-center justify-between rounded-lg bg-cyan-50 px-3 py-2 text-sm">
                  <span>
                    #{index + 1} {row.display_name}
                  </span>
                  <strong>{row.score}</strong>
                </li>
              ))}
              {roomState.leaderboard.length === 0 ? (
                <li className="rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-500">No scores yet.</li>
              ) : null}
            </ul>
          </article>
        </section>

        {activeReveal ? (
          <QuestionRevealCard
            prompt={activeReveal.prompt}
            answer={activeReveal.answer}
            onScore={() => setStatusMessage("Scoring flow UI triggered. Integrate score endpoint in next phase.")}
          />
        ) : null}
      </div>
    </main>
  );
}
