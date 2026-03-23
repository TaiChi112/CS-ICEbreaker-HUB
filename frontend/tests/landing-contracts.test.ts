import { describe, expect, it } from "bun:test";

import type { CreateRoomRequest, JoinRoomRequest } from "../lib/contracts";

describe("frontend contracts", () => {
  it("accepts typed create/join payload structures", () => {
    const createPayload: CreateRoomRequest = { host_display_name: "Host Alice" };
    const joinPayload: JoinRoomRequest = {
      room_code: "ABC123",
      player_display_name: "Player Bob",
    };

    expect(createPayload.host_display_name).toBe("Host Alice");
    expect(joinPayload.room_code).toBe("ABC123");
  });
});
