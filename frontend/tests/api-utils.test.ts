import { describe, expect, it } from "bun:test";

import { toWebSocketUrl } from "../lib/api";

describe("toWebSocketUrl", () => {
  it("builds websocket endpoint with query params", () => {
    const url = toWebSocketUrl("ABC123", "11111111-1111-1111-1111-111111111111", "Alice");

    expect(url).toContain("/ws/rooms/ABC123");
    expect(url).toContain("player_id=11111111-1111-1111-1111-111111111111");
    expect(url).toContain("display_name=Alice");
    expect(url.startsWith("ws://") || url.startsWith("wss://")).toBeTrue();
  });
});
