"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import type { WsEnvelope } from "../lib/contracts";
import { toWebSocketUrl } from "../lib/api";

type UseRoomSocketParams = {
  roomCode: string;
  playerId: string;
  displayName: string;
  onEvent?: (event: WsEnvelope) => void;
};

export function useRoomSocket({ roomCode, playerId, displayName, onEvent }: UseRoomSocketParams) {
  const socketRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastError, setLastError] = useState<string>("");

  const wsUrl = useMemo(() => {
    if (!roomCode || !playerId || !displayName) {
      return "";
    }
    return toWebSocketUrl(roomCode, playerId, displayName);
  }, [displayName, playerId, roomCode]);

  useEffect(() => {
    if (!wsUrl) {
      return;
    }

    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      setConnected(true);
      setLastError("");
    };

    socket.onclose = () => {
      setConnected(false);
    };

    socket.onerror = () => {
      setLastError("WebSocket connection error.");
    };

    socket.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data) as WsEnvelope;
        onEvent?.(parsed);
      } catch {
        setLastError("Received malformed real-time message.");
      }
    };

    const heartbeat = globalThis.setInterval(() => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: "ping", payload: {} }));
      }
    }, 15000);

    return () => {
      globalThis.clearInterval(heartbeat);
      socket.close();
      socketRef.current = null;
      setConnected(false);
    };
  }, [onEvent, wsUrl]);

  const sendClaim = useCallback((questionId: string) => {
    const socket = socketRef.current;
    if (socket?.readyState !== WebSocket.OPEN) {
      return false;
    }

    socket.send(
      JSON.stringify({
        type: "question.claim",
        payload: { questionId },
      }),
    );
    return true;
  }, []);

  return {
    connected,
    lastError,
    sendClaim,
  };
}
