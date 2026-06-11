import { describe, it, expect } from "vitest";

describe("Capability Registration", () => {
  it("should have all required capabilities defined", async () => {
    const { BROWSER_CAPABILITIES } = await import("../src/safety.js");

    expect(BROWSER_CAPABILITIES.length).toBeGreaterThanOrEqual(7);

    // Every capability must have an ID
    for (const cap of BROWSER_CAPABILITIES) {
      expect(cap.id).toBeTruthy();
      expect(cap.name).toBeTruthy();
      expect(cap.description).toBeTruthy();
      expect(cap.safetyLevel).toBeGreaterThanOrEqual(1);
      expect(cap.safetyLevel).toBeLessThanOrEqual(4);
      expect(Array.isArray(cap.tags)).toBe(true);
      expect(cap.version).toBe("0.1.0");
    }
  });

  it("should have read-only capabilities at LEVEL_0_READ", async () => {
    const { BROWSER_CAPABILITIES, SafetyLevel } = await import("../src/safety.js");

    const readOnly = BROWSER_CAPABILITIES.filter(
      (c) => c.id.includes("screenshot") || c.id.includes("dom") || c.id.includes("extract"),
    );
    for (const cap of readOnly) {
      expect(cap.safetyLevel).toBe(SafetyLevel.LEVEL_0_READ);
      expect(cap.requiresApproval).toBe(false);
    }
  });

  it("should have download_file at LEVEL_2_APPROVAL", async () => {
    const { BROWSER_CAPABILITIES, SafetyLevel } = await import("../src/safety.js");

    const downloadCap = BROWSER_CAPABILITIES.find((c) => c.id === "browser.download_file");
    expect(downloadCap).toBeDefined();
    expect(downloadCap!.safetyLevel).toBe(SafetyLevel.LEVEL_2_APPROVAL);
    expect(downloadCap!.requiresApproval).toBe(true);
  });

  it("should NOT have forbidden capabilities (sns, dm, purchase, captcha)", async () => {
    const { BROWSER_CAPABILITIES } = await import("../src/safety.js");

    const forbiddenIds = [
      "browser.post_sns",
      "browser.send_dm",
      "browser.purchase",
      "browser.captcha_bypass",
    ];
    for (const id of forbiddenIds) {
      const found = BROWSER_CAPABILITIES.find((c) => c.id === id);
      expect(found).toBeUndefined();
    }
  });

  it("should register capabilities without error", async () => {
    const { registerCapabilities } = await import("../src/capability_registration.js");

    // Should not throw
    await expect(
      registerCapabilities({ aegisCoreAddress: "localhost:50051" } as any),
    ).resolves.toBeUndefined();
  });

  it("should have all capability IDs follow naming convention", async () => {
    const { BROWSER_CAPABILITIES } = await import("../src/safety.js");

    for (const cap of BROWSER_CAPABILITIES) {
      expect(cap.id).toMatch(/^browser\./);
    }
  });
});
