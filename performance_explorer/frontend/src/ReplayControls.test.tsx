import { afterEach, describe, expect, it, vi } from "vitest";
import { act, fireEvent, render, screen } from "@testing-library/react";
import { App } from "./App";
import data from "./data/historical-attempts-v1.json";
const rows = data.rows.filter(r => r.year === 2024).sort((a, b) => a.driver.localeCompare(b.driver));
afterEach(() => vi.useRealTimers());
const select = () => {
  fireEvent.change(screen.getByLabelText("CAR A · DRIVER / ATTEMPT"), { target: { value: rows[0].attemptId } });
  fireEvent.change(screen.getByLabelText("CAR B · DRIVER / ATTEMPT"), { target: { value: rows[1].attemptId } });
};
describe("historical replay integration", () => {
  it("shows 31 retained attempts and unknown order without invented ordinal", () => {
    render(<App />);
    expect(screen.getByText(/31 RETAINED COMPLETE ATTEMPTS/)).toBeInTheDocument();
    expect(screen.getAllByText(/Order unknown · ID/).length).toBeGreaterThan(0);
  });
  it("moves markers only at independent observed lap boundaries", () => {
    render(<App />); select();
    const time = (rows[0].lapTimesS[0] + rows[1].lapTimesS[0]) / 2;
    fireEvent.change(screen.getByLabelText("Replay timeline"), { target: { value: String(time) } });
    expect(screen.getByTestId("marker-a")).toHaveAttribute("data-lap", rows[0].lapTimesS[0] <= time ? "1" : "0");
    expect(screen.getByTestId("marker-b")).toHaveAttribute("data-lap", rows[1].lapTimesS[0] <= time ? "1" : "0");
    expect(screen.getByText("TIED AT BOUNDARY")).toBeInTheDocument();
    const finish = Math.max(rows[0].totalSeconds, rows[1].totalSeconds);
    fireEvent.change(screen.getByLabelText("Replay timeline"), { target: { value: String(finish) } });
    expect(screen.getByTestId("car-a-status")).toHaveTextContent("4 / 4 laps · complete");
    expect(screen.getByTestId("car-b-status")).toHaveTextContent("4 / 4 laps · complete");
  });
  it("seeks chart and boundary controls to real cumulative timing and pauses", () => {
    render(<App />); select();
    fireEvent.click(screen.getByRole("button", { name: "Play replay" }));
    fireEvent.keyDown(screen.getByRole("button", { name: "Select lap 2" }), { key: "Enter" });
    const target = Math.max(...rows.slice(0, 2).map(r => r.lapTimesS[0] + r.lapTimesS[1]));
    expect(Number((screen.getByLabelText("Replay timeline") as HTMLInputElement).value)).toBeCloseTo(target, 8);
    expect(screen.getByRole("button", { name: "Play replay" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Restart replay" }));
    expect(screen.getByLabelText("Replay timeline")).toHaveValue("0");
  });
  it("uses elapsed wall time, selected rate and stops automatically at completion", () => {
    vi.useFakeTimers({ toFake: ["setInterval", "clearInterval", "performance"] }); render(<App />); select();
    fireEvent.change(screen.getByLabelText("Playback speed"), { target: { value: "4" } });
    fireEvent.click(screen.getByRole("button", { name: "Play replay" }));
    act(() => vi.advanceTimersByTime(1000));
    expect(Number((screen.getByLabelText("Replay timeline") as HTMLInputElement).value)).toBeCloseTo(4, 6);
    fireEvent.click(screen.getByRole("button", { name: "Pause replay" }));
    act(() => vi.advanceTimersByTime(1000));
    expect(Number((screen.getByLabelText("Replay timeline") as HTMLInputElement).value)).toBeCloseTo(4, 6);
    fireEvent.click(screen.getByRole("button", { name: "Play replay" }));
    act(() => vi.advanceTimersByTime(60000));
    expect(screen.getByRole("button", { name: "Play replay" })).toBeInTheDocument();
    expect(screen.getByTestId("car-a-status")).toHaveTextContent("complete");
    fireEvent.change(screen.getByLabelText("YEAR"), { target: { value: "2020" } });
    expect(screen.getByLabelText("Replay timeline")).toHaveValue("0");
  });
  it("renders malformed and empty-data states without inventing data", () => {
    const { rerender } = render(<App dataset={null} />);
    expect(screen.getByRole("alert")).toHaveTextContent("failed schema validation");
    rerender(<App dataset={{ ...data, rows: [], recordCount: 0 }} />);
    expect(screen.getByRole("status")).toHaveTextContent("No retained complete attempts");
  });
});
