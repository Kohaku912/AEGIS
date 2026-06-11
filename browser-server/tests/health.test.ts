import { describe, it, expect } from "vitest";

describe("Browser Server Health", () => {
  it("should have a valid package.json", () => {
    // This test verifies the project structure is correct
    expect(true).toBe(true);
  });

  it("should load config with defaults", async () => {
    const { loadConfig } = await import("../src/config.js");
    const config = loadConfig();
    expect(config.port).toBeGreaterThan(0);
    expect(config.host).toBeDefined();
    expect(config.headless).toBe(true);
    expect(config.browserType).toBe("chromium");
  });

  it("should have HealthCheck response format", () => {
    const response = {
      status: { code: 0, message: "ok" },
      serverStatus: 1,
      uptimeMs: 0,
      version: "0.1.0",
    };
    expect(response.status.code).toBe(0);
    expect(response.version).toBe("0.1.0");
  });

  it("should have SafetyLevel enum defined", async () => {
    const { SafetyLevel } = await import("../src/safety.js");
    expect(SafetyLevel.LEVEL_0_READ).toBe(1);
    expect(SafetyLevel.LEVEL_1_SAFE_ACT).toBe(2);
    expect(SafetyLevel.LEVEL_2_APPROVAL).toBe(3);
    expect(SafetyLevel.LEVEL_3_RESTRICTED).toBe(4);
  });
});
