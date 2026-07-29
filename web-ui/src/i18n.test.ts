import { describe, expect, it } from "vitest";
import { formatDateTime, formatRelative, messages } from "./i18n";

describe("English message catalog", () => {
  it("contains non-empty English strings", () => {
    expect(Object.keys(messages).length).toBeGreaterThan(20);
    for (const value of Object.values(messages)) {
      expect(value.trim()).not.toBe("");
      expect(value).not.toMatch(/[ぁ-んァ-ヶ一-龯]/u);
    }
  });

  it("uses English formatting in the Tokyo timezone", () => {
    expect(formatDateTime(Date.UTC(2026, 0, 1, 0, 0, 0))).toContain("2026");
    expect(formatRelative(Date.now() - 60_000)).toContain("minute");
  });
});
