import { describe, expect, it } from "vitest";
import baseline from "./test/fixtures/v6-baseline.json";
import offtrack from "./test/fixtures/v6-delay_0.6s.json";
import { compatibleV6, decodeV6, nextV6Time, sampleV6 } from "./v6Replay";

describe("V1.1 V6 view adapter", () => {
  it("reuses the audited schema-2 adapter for complete and failed published runs", () => {
    const a = decodeV6(baseline), b = decodeV6(offtrack);
    expect(a.status).toBe("completed");
    expect(b.status).toBe("off_track");
    expect(compatibleV6(a, b)).toBe(true);
    expect(a.provenance.provider).toBe("V6 published schema-2 replay");
  });
  it("uses adapter interpolation and clamps the synchronized clock", () => {
    const run = decodeV6(baseline);
    expect(sampleV6(run.samples, 1e9).sim_time_s).toBe(run.durationS);
    expect(nextV6Time(1, .5, 2, 2)).toBe(2);
    expect(() => nextV6Time(0, -1, 1, 2)).toThrow(/clock/);
  });
});
