import type {
  ClaimableQuestionsResponse,
  CreateRoomRequest,
  GenerateQuestionsRequest,
  GenerateQuestionsResponse,
  JoinRoomRequest,
  RoomJoinResponse,
  RoomStateResponse,
} from "./contracts";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export async function createRoom(payload: CreateRoomRequest): Promise<RoomJoinResponse> {
  return requestJson<RoomJoinResponse>("/api/rooms", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function joinRoom(payload: JoinRoomRequest): Promise<RoomJoinResponse> {
  return requestJson<RoomJoinResponse>("/api/rooms/join", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getRoomState(roomCode: string): Promise<RoomStateResponse> {
  return requestJson<RoomStateResponse>(`/api/rooms/${encodeURIComponent(roomCode)}`);
}

export async function generateQuestions(
  roomCode: string,
  payload: GenerateQuestionsRequest,
): Promise<GenerateQuestionsResponse> {
  return requestJson<GenerateQuestionsResponse>(
    `/api/rooms/${encodeURIComponent(roomCode)}/questions/generate`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export async function getClaimableQuestions(roomCode: string): Promise<ClaimableQuestionsResponse> {
  return requestJson<ClaimableQuestionsResponse>(
    `/api/rooms/${encodeURIComponent(roomCode)}/questions`,
  );
}

export function toWebSocketUrl(roomCode: string, playerId: string, displayName: string): string {
  const baseHttp = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
  const wsBase = baseHttp.replace("http://", "ws://").replace("https://", "wss://");

  const params = new URLSearchParams({
    player_id: playerId,
    display_name: displayName,
  });

  return `${wsBase}/ws/rooms/${encodeURIComponent(roomCode)}?${params.toString()}`;
}
