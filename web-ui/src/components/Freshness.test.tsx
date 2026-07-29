import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Freshness } from "./Freshness";

describe("Freshness", () => {
  it("shows live for fresh data", () => {
    render(<Freshness generatedAt={10_000} sourceUpdatedAt={5_000} />);
    expect(screen.getByText(/更新:/)).toBeInTheDocument();
  });

  it("marks stale data with explicit text", () => {
    render(<Freshness generatedAt={180_000} sourceUpdatedAt={0} stale />);
    expect(screen.getByText(/古いデータ/)).toBeInTheDocument();
  });
});
