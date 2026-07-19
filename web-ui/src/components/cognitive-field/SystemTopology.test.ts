import { describe, expect, it } from "vitest";
import { TOPOLOGY_POSITIONS } from "./SystemTopology";

describe("system topology", () => {
  it("keeps peripheral nodes in a compact readable cluster", () => {
    const center = TOPOLOGY_POSITIONS["ai-server"];
    const distances = Object.entries(TOPOLOGY_POSITIONS)
      .filter(([id]) => id !== "ai-server")
      .map(([, position]) => Math.hypot(
        position[0] - center[0],
        position[1] - center[1],
        position[2] - center[2]
      ));

    expect(Math.max(...distances)).toBeLessThanOrEqual(3);
  });
});
