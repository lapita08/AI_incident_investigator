import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, test, vi, expect } from "vitest";
import App from "../App";

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn(async (url: string) => {
    if (url.endsWith("/api/v1/incidents")) {
      return new Response(JSON.stringify([]), { status: 200, headers: { "Content-Type": "application/json" } });
    }
    return new Response(JSON.stringify({}), { status: 200, headers: { "Content-Type": "application/json" } });
  }));
});

afterEach(() => {
  vi.unstubAllGlobals();
});

test("renders dashboard controls", async () => {
  render(<App />);
  expect(await screen.findByText("AI Incident Investigator")).toBeInTheDocument();
  expect(screen.getByText("Load DB latency demo")).toBeInTheDocument();
});
