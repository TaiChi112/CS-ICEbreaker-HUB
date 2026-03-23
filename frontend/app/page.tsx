"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { createRoom, joinRoom } from "../lib/api";

export default function LandingPage() {
  const router = useRouter();
  const [hostName, setHostName] = useState("");
  const [playerName, setPlayerName] = useState("");
  const [roomCode, setRoomCode] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [busy, setBusy] = useState(false);

  const onCreateRoom = async () => {
    if (!hostName.trim()) {
      setStatusMessage("Please enter host name.");
      return;
    }

    setBusy(true);
    try {
      const room = await createRoom({ host_display_name: hostName.trim() });
      router.push(
        `/host?roomCode=${room.room_code}&playerId=${room.player_id}&displayName=${encodeURIComponent(room.display_name)}`,
      );
    } catch {
      setStatusMessage("Could not create room. Ensure backend API is running.");
    } finally {
      setBusy(false);
    }
  };

  const onJoinRoom = async () => {
    if (!playerName.trim() || !roomCode.trim()) {
      setStatusMessage("Please enter player name and room code.");
      return;
    }

    setBusy(true);
    try {
      const room = await joinRoom({
        room_code: roomCode.trim().toUpperCase(),
        player_display_name: playerName.trim(),
      });
      router.push(
        `/player?roomCode=${room.room_code}&playerId=${room.player_id}&displayName=${encodeURIComponent(room.display_name)}`,
      );
    } catch {
      setStatusMessage("Could not join room. Check room code and backend server.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="min-h-screen bg-linear-to-br from-cyan-200 via-amber-50 to-lime-200 p-4 text-slate-900">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 py-6">
        <section className="rounded-3xl border border-white/60 bg-white/70 p-6 shadow-2xl backdrop-blur-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-700">CS-Icebreaker Hub</p>
          <h1 className="mt-2 text-3xl font-bold leading-tight sm:text-4xl">
            Real-Time LLM Trivia for Computer Science Teams
          </h1>
          <p className="mt-3 max-w-2xl text-sm text-slate-700 sm:text-base">
            Hosts generate topic-based question batches. Players compete to claim questions first and run
            live knowledge challenges.
          </p>
        </section>

        <section className="grid gap-5 md:grid-cols-2">
          <article className="rounded-2xl border border-cyan-300/60 bg-cyan-50 p-5 shadow-lg">
            <h2 className="text-xl font-semibold">Create Room (Host)</h2>
            <label htmlFor="host-name" className="mt-4 block text-sm font-medium">Host display name</label>
            <input
              id="host-name"
              value={hostName}
              onChange={(event) => setHostName(event.target.value)}
              placeholder="Host Alice"
              className="mt-2 w-full rounded-xl border border-cyan-300 bg-white px-3 py-2 outline-none ring-cyan-400 focus:ring"
            />
            <button
              type="button"
              disabled={busy}
              onClick={onCreateRoom}
              className="mt-4 w-full rounded-xl bg-cyan-700 px-4 py-2 font-semibold text-white transition hover:bg-cyan-600 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Create Room
            </button>
          </article>

          <article className="rounded-2xl border border-lime-300/70 bg-lime-50 p-5 shadow-lg">
            <h2 className="text-xl font-semibold">Join Room (Player)</h2>
            <label htmlFor="player-name" className="mt-4 block text-sm font-medium">Player display name</label>
            <input
              id="player-name"
              value={playerName}
              onChange={(event) => setPlayerName(event.target.value)}
              placeholder="Player Bob"
              className="mt-2 w-full rounded-xl border border-lime-300 bg-white px-3 py-2 outline-none ring-lime-400 focus:ring"
            />
            <label htmlFor="room-code" className="mt-3 block text-sm font-medium">Room code</label>
            <input
              id="room-code"
              value={roomCode}
              onChange={(event) => setRoomCode(event.target.value.toUpperCase())}
              placeholder="ABC123"
              className="mt-2 w-full rounded-xl border border-lime-300 bg-white px-3 py-2 uppercase outline-none ring-lime-400 focus:ring"
            />
            <button
              type="button"
              disabled={busy}
              onClick={onJoinRoom}
              className="mt-4 w-full rounded-xl bg-lime-700 px-4 py-2 font-semibold text-white transition hover:bg-lime-600 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Join Room
            </button>
          </article>
        </section>

        {statusMessage ? (
          <p className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {statusMessage}
          </p>
        ) : null}

        <p className="text-center text-xs text-slate-600">
          Need direct host access? <Link href="/host" className="underline">Open Host Dashboard</Link>
        </p>
      </div>
    </main>
  );
}
