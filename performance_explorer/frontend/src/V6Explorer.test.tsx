import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { App } from "./App";
import baseline from "./test/fixtures/v6-baseline.json";
import conservative from "./test/fixtures/v6-conservative.json";
import failed from "./test/fixtures/v6-delay_0.6s.json";

const conservativeWithoutBrake = structuredClone(conservative);
const brakeIndex = conservativeWithoutBrake.fields.indexOf("brake_command");
conservativeWithoutBrake.fields.splice(brakeIndex, 1);
conservativeWithoutBrake.rows.forEach(row => row.splice(brakeIndex, 1));
const replays: Record<string, unknown> = { baseline, conservative: conservativeWithoutBrake, "delay_0.6s": failed };
const index = { schema_version: 2, label: "SIMULATED", runs: Object.entries(replays).map(([name, run]) => ({
  name, file: `replays/${name}.json`, status: (run as typeof baseline).metrics.status,
})) };
const json = (value: unknown) => Promise.resolve({ ok: true, json: () => Promise.resolve(value) } as Response);
beforeEach(() => vi.stubGlobal("fetch", vi.fn((input: string | URL) => {
  const url = String(input);
  if (url.endsWith("index.json")) return json(index);
  const name = decodeURIComponent(url.split("/").pop()!.replace(/\.json$/, ""));
  return json(replays[name]);
})));
afterEach(() => { cleanup(); vi.unstubAllGlobals(); vi.useRealTimers(); });

async function openV6() {
  render(<App />);
  fireEvent.click(screen.getByRole("button", { name: "V6 dynamics · SIMULATED" }));
  await screen.findByRole("heading", { name: /Follow the dynamics/ });
  await screen.findByRole("heading", { name: /Car A · baseline/ });
}

describe("V6 mode inside the Performance Explorer", () => {
  it("loads authentic schema-2 runs through the Explorer adapter and preserves mode separation", async () => {
    await openV6();
    expect(screen.getByText("SIMULATED — V6")).toBeInTheDocument();
    expect(screen.getByText(/separate simulation domain from V5 and historical timing/)).toBeInTheDocument();
    expect(screen.getByRole("combobox", { name: "Car A V6 replay" })).toBeInTheDocument();
    expect(screen.getByRole("combobox", { name: "Car B V6 replay" })).toBeInTheDocument();
    expect(screen.getAllByText(/OFF TRACK/).length).toBeGreaterThan(0);
    expect(screen.getByRole("img", { name: /Recorded V6 vehicle positions/ })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Historical timing · OBSERVED" }));
    expect(screen.getByText(/OBSERVED DATA MODE/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "V5 simulation · SIMULATED" }));
    expect(screen.getByText(/DUAL-CAR COMPARISON · V5/)).toBeInTheDocument();
  });

  it("seeks on one clock and clamps each vehicle at its own terminal event", async () => {
    await openV6();
    const seek = screen.getByRole("slider", { name: "V6 replay time" }) as HTMLInputElement;
    fireEvent.change(seek, { target: { value: seek.max } });
    expect(Number(screen.getByTestId("v6-marker-0").getAttribute("data-time"))).toBeCloseTo(baseline.metrics.elapsed_sim_s, 7);
    expect(Number(screen.getByTestId("v6-marker-1").getAttribute("data-time"))).toBeCloseTo(failed.metrics.elapsed_sim_s, 7);
    expect(screen.getByText(/OFF-TRACK TERMINAL EVENT/)).toBeInTheDocument();
  });

  it("supports playback, pause, restart and playback-rate changes", async () => {
    await openV6(); vi.useFakeTimers();
    fireEvent.change(screen.getByRole("combobox", { name: "V6 playback speed" }), { target: { value: "2" } });
    fireEvent.click(screen.getByRole("button", { name: "Play V6 replay" }));
    await act(async () => { vi.advanceTimersByTime(300); });
    const elapsed = Number(screen.getByTestId("v6-marker-0").getAttribute("data-time"));
    expect(elapsed).toBeGreaterThan(0);
    fireEvent.click(screen.getByRole("button", { name: "Pause V6 replay" }));
    await act(async () => { vi.advanceTimersByTime(200); });
    expect(Number(screen.getByTestId("v6-marker-0").getAttribute("data-time"))).toBe(elapsed);
    fireEvent.click(screen.getByRole("button", { name: "Restart V6 replay" }));
    expect(Number(screen.getByTestId("v6-marker-0").getAttribute("data-time"))).toBe(0);
  });

  it("shows optional telemetry as not exported and reloads a selected compatible run", async () => {
    await openV6();
    fireEvent.change(screen.getByRole("combobox", { name: "Car B V6 replay" }), { target: { value: "conservative" } });
    await waitFor(() => expect(screen.getByRole("heading", { name: /Car B · conservative/ })).toBeInTheDocument());
    expect(screen.getByText("Not exported")).toBeInTheDocument();
    expect(conservative.metrics.status).toBe("completed");
  });
});
