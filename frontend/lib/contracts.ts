export interface RoomJoinResponse {
  room_id: string;
  room_code: string;
  player_id: string;
  user_id: string;
  display_name: string;
  role: "host" | "player";
}

export interface RoomPlayer {
  player_id: string;
  user_id: string;
  display_name: string;
  role: "host" | "player";
  joined_at: string;
}

export interface LeaderboardEntry {
  player_id: string;
  display_name: string;
  score: number;
}

export interface RoomStateResponse {
  room_id: string;
  room_code: string;
  status: "lobby" | "active" | "completed";
  players: RoomPlayer[];
  leaderboard: LeaderboardEntry[];
}

export interface GenerateQuestionsRequest {
  host_player_id: string;
  topic: string;
  batch_size?: number;
}

export interface GeneratedQuestion {
  question_id: string;
  round_id: string;
  prompt: string;
}

export interface GenerateQuestionsResponse {
  room_id: string;
  room_code: string;
  round_id: string;
  topic: string;
  question_count: number;
  questions: GeneratedQuestion[];
}

export interface ClaimableQuestionsResponse {
  room_code: string;
  questions: GeneratedQuestion[];
}

export interface CreateRoomRequest {
  host_display_name: string;
}

export interface JoinRoomRequest {
  room_code: string;
  player_display_name: string;
}

export interface WsEnvelope {
  type:
    | "player.joined"
    | "player.left"
    | "question.claimed"
    | "question.claim_rejected"
    | "ping"
    | "pong";
  payload: Record<string, unknown>;
  occurredAt: string;
}
