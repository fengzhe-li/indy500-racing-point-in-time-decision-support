import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { App } from "./App";
import { V5Explorer } from "./V5Explorer";
import baseline from "./data/v5-baseline.json";
import lowGrip from "./data/v5-low-grip.json";
import { v5AtTime, v5TimeAtDistance, parseV5Replay } from "./adapters/v5";

const replay = parseV5Replay(baseline);
const timeline = () => screen.getByLabelText("Simulation timeline") as HTMLInputElement;
const upload = (content: unknown, side = "A", name = "scenario.json") => fireEvent.change(screen.getByLabelText(`Import Car ${side} V5 replay JSON`), {
  target: { files: [{ name, size: 100, text: async () => JSON.stringify(content) }] },
});
beforeEach(() => {
  // Hashing is orthogonal to UI state; pinned artifact hashes are checked by Python.
  vi.stubGlobal("crypto", { subtle: { digest: vi.fn().mockResolvedValue(new ArrayBuffer(32)) } });
});
afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });

describe("V5 two-car Explorer integration", () => {
  it("keeps simulation separate from historical timing and V6", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "V5 simulation · SIMULATED" }));
    expect(screen.queryByText("OBSERVED DATA MODE")).not.toBeInTheDocument();
    expect(screen.getByText(/No GPS, ECU, throttle/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "V6 dynamics · SIMULATED" })).toHaveAttribute("aria-pressed", "false");
    fireEvent.click(screen.getByRole("button", { name: "Historical timing · OBSERVED" }));
    expect(screen.queryByLabelText("Simulation timeline")).not.toBeInTheDocument();
    expect(screen.getByText(/31 RETAINED COMPLETE ATTEMPTS/)).toBeInTheDocument();
  });
  it("selects two independent actual configurations, including ties, and resets playback", () => {
    render(<V5Explorer />);
    fireEvent.change(timeline(), { target: { value: "12" } });
    fireEvent.change(screen.getByLabelText("Car B configuration"), { target: { value: "baseline" } });
    expect(timeline()).toHaveValue("0");
    expect(screen.getByText("Tied: 100.0% (4023.4 m)")).toBeInTheDocument();
    expect(screen.getByLabelText("Car A configuration")).toHaveValue("baseline");
    fireEvent.change(screen.getByLabelText("Car A configuration"), { target: { value: "low-grip" } });
    expect(screen.getByLabelText("Car B configuration")).toHaveValue("baseline");
    expect(screen.getByText("-1.9760 s")).toBeInTheDocument();
  });
  it("positions both cars on one clock and clamps the earlier finisher", () => {
    render(<V5Explorer />);
    const time = (baseline.lap_time_s + lowGrip.lap_time_s) / 2;
    fireEvent.change(timeline(), { target: { value: String(time) } });
    expect(screen.getByTestId("sim-car-A")).toHaveAttribute("data-complete", "true");
    expect(screen.getByTestId("sim-car-A")).toHaveAttribute("data-distance", String(baseline.track_length_m));
    expect(screen.getByTestId("sim-car-B")).toHaveAttribute("data-complete", "false");
    const expected = v5AtTime(parseV5Replay(lowGrip), time).distanceM;
    expect(Number(screen.getByTestId("sim-car-B").getAttribute("data-distance"))).toBeCloseTo(expected, 8);
    fireEvent.change(timeline(), { target: { value: String(lowGrip.lap_time_s) } });
    expect(screen.getByTestId("sim-car-B")).toHaveAttribute("data-complete", "true");
  });
  it.each([.5, 1, 2, 4, 10])("plays at %s×, pauses, restarts and stops at the slower finish", rate => {
    vi.useFakeTimers({ toFake: ["setInterval", "clearInterval", "performance"] });
    render(<V5Explorer />);
    fireEvent.change(screen.getByLabelText("Simulation playback speed"), { target: { value: String(rate) } });
    fireEvent.click(screen.getByRole("button", { name: "Play simulation" }));
    act(() => vi.advanceTimersByTime(1000));
    expect(Number(timeline().value)).toBeCloseTo(rate, 8);
    fireEvent.click(screen.getByRole("button", { name: "Pause simulation" }));
    act(() => vi.advanceTimersByTime(500));
    expect(Number(timeline().value)).toBeCloseTo(rate, 8);
    fireEvent.click(screen.getByRole("button", { name: "Restart simulation" }));
    expect(timeline()).toHaveValue("0");
    fireEvent.click(screen.getByRole("button", { name: "Play simulation" }));
    act(() => vi.advanceTimersByTime(90000));
    expect(Number(timeline().value)).toBe(lowGrip.lap_time_s);
    expect(screen.getByRole("button", { name: "Play simulation" })).toBeInTheDocument();
  });
  it("synchronizes graph keyboard seeking, track highlight and both marker positions", () => {
    render(<V5Explorer />);
    fireEvent.click(screen.getByRole("button", { name: "Play simulation" }));
    fireEvent.keyDown(screen.getByRole("slider", { name: "Speed profile graph" }), { key: "ArrowRight" });
    expect(Number(timeline().value)).toBeCloseTo(v5TimeAtDistance(replay, 25), 8);
    expect(Number(screen.getByTestId("sim-car-A").getAttribute("data-distance"))).toBeCloseTo(25, 8);
    expect(screen.getByRole("slider", { name: "Running delta graph" })).toHaveAttribute("aria-valuenow", "25");
    expect(screen.getByRole("button", { name: "Play simulation" })).toBeInTheDocument();
    fireEvent.keyDown(screen.getByRole("slider", { name: "Running delta graph" }), { key: "End" });
    expect(Number(timeline().value)).toBe(baseline.lap_time_s);
    expect(screen.getByTestId("sim-car-A")).toHaveAttribute("data-complete", "true");
    expect(screen.getByTestId("sim-car-B")).toHaveAttribute("data-complete", "false");
    const row = screen.getByRole("button", { name: "Inspect Back straight" });
    fireEvent.focus(row);
    expect(screen.getByTestId("track-segment-3")).toHaveAttribute("data-highlighted", "true");
    fireEvent.click(row);
    expect(Number(timeline().value)).toBeCloseTo(v5TimeAtDistance(replay, baseline.segments[3].start_m), 8);
  });
  it("supports graph pointer seeking and dragging with the same time mapping", () => {
    vi.stubGlobal("PointerEvent", MouseEvent);
    render(<V5Explorer />);
    const graph = screen.getByRole("slider", { name: "Speed profile graph" });
    vi.spyOn(graph, "getBoundingClientRect").mockReturnValue({ left: 0, width: 640 } as DOMRect);
    fireEvent.pointerDown(graph, { clientX: 330, buttons: 1 });
    expect(Number(timeline().value)).toBeCloseTo(v5TimeAtDistance(replay, baseline.track_length_m / 2), 8);
    fireEvent.pointerMove(graph, { clientX: 600, buttons: 1 });
    expect(Number(timeline().value)).toBe(baseline.lap_time_s);
    fireEvent.pointerMove(graph, { clientX: 60, buttons: 0 });
    expect(Number(timeline().value)).toBe(baseline.lap_time_s);
  });
  it("imports actual JSON independently with explicit unverified producer provenance", async () => {
    render(<V5Explorer />); upload(lowGrip);
    await waitFor(() => expect(screen.getByLabelText("Car A configuration")).toHaveValue("import-A-1"));
    expect(screen.getByLabelText("Car B configuration")).toHaveValue("low-grip");
    expect(screen.getByText(/User-imported export · producer commit unverified/)).toBeInTheDocument();
    expect(screen.getByText("Tied: 100.0% (4023.4 m)")).toBeInTheDocument();
  });
  it("renders high-density validated replays without exceeding call-stack argument limits", async () => {
    const dense = structuredClone(baseline);
    for (const key of ["distance_m", "elapsed_s", "speed_mps", "speed_cap_mps", "acceleration_mps2", "mode", "xy_m"] as const) dense[key] = [];
    const factor = 180, r8 = (x: number) => Number(x.toFixed(8)), r12 = (x: number) => Number(x.toFixed(12));
    for (let i = 0; i < baseline.distance_m.length - 1; i++) for (let j = 0; j < factor; j++) {
      const d = baseline.distance_m[i] + (baseline.distance_m[i + 1] - baseline.distance_m[i]) * j / factor;
      const t = v5TimeAtDistance(replay, d), p = v5AtTime(replay, t);
      dense.distance_m.push(r8(d)); dense.elapsed_s.push(r12(t)); dense.speed_mps.push(r8(p.speedMps));
      dense.speed_cap_mps.push(r8(Math.max(baseline.speed_cap_mps[i], baseline.speed_cap_mps[i + 1])));
      dense.xy_m.push([r8(p.positionM[0]), r8(p.positionM[1])]);
      dense.acceleration_mps2.push(r12(baseline.acceleration_mps2[i])); dense.mode.push(baseline.mode[i]);
    }
    for (const key of ["distance_m", "elapsed_s", "speed_mps", "speed_cap_mps", "xy_m"] as const) (dense[key] as unknown[]).push(baseline[key][baseline[key].length - 1]);
    expect(dense.distance_m.length).toBeGreaterThan(70000);
    render(<V5Explorer />); upload(dense);
    await waitFor(() => expect(screen.getByLabelText("Car A configuration")).toHaveValue("import-A-1"));
    expect(screen.getByRole("slider", { name: "Speed profile graph" })).toBeInTheDocument();
  });
  it("rejects invalid input and keeps the last validated run", async () => {
    render(<V5Explorer />); upload({ ...baseline, schema_version: "v6" });
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("unsupported schema version"));
    expect(screen.getByLabelText("Car A configuration")).toHaveValue("baseline");
    expect(timeline()).toBeInTheDocument();
  });
  it("rejects incompatible origins instead of silently aligning", async () => {
    render(<V5Explorer />); upload({ ...baseline, origin: "Different timing line" });
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("Incompatible V5"));
    expect(screen.queryByLabelText("Simulation timeline")).not.toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Car A configuration"), { target: { value: "baseline" } });
    expect(timeline()).toHaveValue("0");
  });
  it("ignores a late upload after a newer selection", async () => {
    render(<V5Explorer />);
    let resolve!: (content: string) => void;
    const pending = new Promise<string>(done => { resolve = done; });
    fireEvent.change(screen.getByLabelText("Import Car A V5 replay JSON"), { target: { files: [{ name: "slow.json", size: 100, text: () => pending }] } });
    fireEvent.change(screen.getByLabelText("Car A configuration"), { target: { value: "low-grip" } });
    await act(async () => { resolve(JSON.stringify(baseline)); });
    expect(screen.getByLabelText("Car A configuration")).toHaveValue("low-grip");
    expect(screen.queryByRole("option", { name: "slow.json" })).not.toBeInTheDocument();
  });
  it("reports file read failures without losing either run", async () => {
    render(<V5Explorer />);
    fireEvent.change(screen.getByLabelText("Import Car B V5 replay JSON"), { target: { files: [{ name: "broken.json", size: 100, text: async () => { throw new Error("Read failed"); } }] } });
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("Read failed"));
    expect(screen.getByLabelText("Car B configuration")).toHaveValue("low-grip");
  });
});

const response = (payload: unknown, ok = true, status = 200) => ({ ok, status, json: async () => payload }) as Response;
describe("independent V5 API scenarios", () => {
  it("posts independent drafts and applies each successful response only to its car", async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(response(baseline)).mockResolvedValueOnce(response(lowGrip)); vi.stubGlobal("fetch", fetchMock);
    render(<V5Explorer />);
    fireEvent.change(screen.getByLabelText("Car A Mass (kg)"), { target: { value: "900" } });
    fireEvent.change(screen.getByLabelText("Car B Mass (kg)"), { target: { value: "950" } });
    fireEvent.submit(screen.getByRole("form", { name: "Car A scenario" }));
    await waitFor(() => expect(screen.getByLabelText("Car A configuration")).toHaveValue("api-A-1"));
    expect(screen.getByLabelText("Car B configuration")).toHaveValue("low-grip");
    expect(screen.getByLabelText("Car B Mass (kg)")).toHaveValue(950);
    fireEvent.submit(screen.getByRole("form", { name: "Car B scenario" }));
    await waitFor(() => expect(screen.getByLabelText("Car B configuration")).toHaveValue("api-B-1"));
    expect(JSON.parse(fetchMock.mock.calls[0][1].body).vehicle.mass_kg).toBe(900);
    expect(JSON.parse(fetchMock.mock.calls[1][1].body).vehicle.mass_kg).toBe(950);
    expect(fetchMock.mock.calls[0][0]).toBe("/api/v5/simulate");
    expect(screen.getAllByText(/Actual SIMULATED API output/)).toHaveLength(2);
    // Applied fields must come from returned output, not pretend the service honored a draft.
    expect(screen.getByLabelText("Car A Mass (kg)")).toHaveValue(baseline.vehicle.mass_kg);
  });
  it("loads API baseline and handles service validation failures without losing valid runs", async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(response({ detail: [{ msg: "Rejected scenario" }] }, false, 422)).mockResolvedValueOnce(response(baseline)); vi.stubGlobal("fetch", fetchMock);
    render(<V5Explorer />);
    fireEvent.submit(screen.getByRole("form", { name: "Car A scenario" }));
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("Rejected scenario"));
    expect(screen.getByLabelText("Car A configuration")).toHaveValue("baseline");
    expect(screen.getByLabelText("Simulation timeline")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Load API baseline B"));
    await waitFor(() => expect(screen.getByLabelText("Car B configuration")).toHaveValue("api-B-1"));
    expect(fetchMock.mock.calls[1][1].method).toBe("GET");
  });
  it.each(["network", "invalid schema"])("retains valid data on %s failures", async kind => {
    vi.stubGlobal("fetch", kind === "network" ? vi.fn().mockRejectedValue(new Error("Offline")) : vi.fn().mockResolvedValue(response({ schema_version: "bad" })));
    render(<V5Explorer />); fireEvent.click(screen.getByText("Load API baseline A"));
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("Last valid configuration retained"));
    expect(screen.getByLabelText("Car A configuration")).toHaveValue("baseline");
  });
  it.each([true, false])("ignores stale %s response after a newer request and keeps A/B isolated", async success => {
    let finish!: (r: Response) => void;
    const pending = new Promise<Response>(resolve => { finish = resolve; });
    const fetchMock = vi.fn().mockReturnValueOnce(pending).mockResolvedValueOnce(response(lowGrip)).mockResolvedValueOnce(response(baseline)); vi.stubGlobal("fetch", fetchMock);
    render(<V5Explorer />);
    fireEvent.click(screen.getByText("Load API baseline A"));
    fireEvent.click(screen.getByText("Load API baseline A"));
    fireEvent.click(screen.getByText("Load API baseline B"));
    await waitFor(() => expect(screen.getByLabelText("Car A configuration")).toHaveValue("api-A-2"));
    await act(async () => finish(response(success ? baseline : { detail: "Stale error" }, success, success ? 200 : 500)));
    expect(fetchMock.mock.calls[0][1].signal.aborted).toBe(true);
    expect(screen.getByLabelText("Car A configuration")).toHaveValue("api-A-2");
    expect(screen.getByLabelText("Car B configuration")).toHaveValue("api-B-1");
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
  it("invalidates pending API results on selection and on unmount", async () => {
    let finish!: (r: Response) => void;
    const fetchMock = vi.fn().mockImplementation(() => new Promise<Response>(resolve => { finish = resolve; })); vi.stubGlobal("fetch", fetchMock);
    const view = render(<V5Explorer />);
    fireEvent.click(screen.getByText("Load API baseline A"));
    fireEvent.change(screen.getByLabelText("Car A configuration"), { target: { value: "low-grip" } });
    await act(async () => finish(response(baseline)));
    expect(screen.getByLabelText("Car A configuration")).toHaveValue("low-grip");
    fireEvent.click(screen.getByText("Load API baseline B")); view.unmount();
    expect(fetchMock.mock.calls[1][1].signal.aborted).toBe(true);
    await act(async () => finish(response(baseline)));
  });
  it("highlights the same region and inspection cursor across charts without moving the clock", () => {
    vi.stubGlobal("PointerEvent", MouseEvent); render(<V5Explorer />);
    const graph = screen.getByRole("slider", { name: "Speed profile graph" });
    vi.spyOn(graph, "getBoundingClientRect").mockReturnValue({ left: 0, width: 640 } as DOMRect);
    fireEvent.pointerMove(graph, { clientX: 330, buttons: 0 });
    expect(timeline()).toHaveValue("0");
    expect(screen.getByTestId("Speed profile graph-inspection")).toHaveAttribute("x1", "330");
    expect(screen.getByTestId("Running delta graph-inspection")).toHaveAttribute("x1", "330");
    expect(screen.getByTestId("region-insight")).toHaveTextContent("Turn 3");
    fireEvent.pointerLeave(graph);
    expect(screen.queryByTestId("Speed profile graph-inspection")).not.toBeInTheDocument();
  });
});
