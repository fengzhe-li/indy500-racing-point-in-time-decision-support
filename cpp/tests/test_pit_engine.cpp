#include <gtest/gtest.h>

#include <algorithm>
#include <cmath>
#include <fstream>
#include <limits>
#include <random>
#include <sstream>
#include <string>
#include <vector>

#include "indy500/pit_engine.hpp"

namespace indy500::pit::tests {

namespace {

std::vector<std::string> split_csv_line(const std::string& line) {
    std::vector<std::string> tokens;
    std::stringstream ss(line);
    std::string item;
    while (std::getline(ss, item, ',')) {
        if (!item.empty() && item.back() == '\r') {
            item.pop_back();
        }
        tokens.push_back(item);
    }
    return tokens;
}

std::string repo_file(const std::string& rel_path) {
#ifdef INDY500_REPO_ROOT
    return std::string(INDY500_REPO_ROOT) + "/" + rel_path;
#else
    return "../" + rel_path;
#endif
}

std::vector<TrackModelCoefficients> load_frozen_track_coefficients() {
    std::ifstream ifs(repo_file("weather/output/v2_future_track/v2a_full_sample_track_model_coefficients_v1.csv"));
    if (!ifs.is_open()) {
        throw std::runtime_error("Failed to open frozen track coefficients CSV");
    }
    std::string header;
    std::getline(ifs, header);

    std::vector<TrackModelCoefficients> coefs;
    std::string line;
    while (std::getline(ifs, line)) {
        if (line.empty()) continue;
        const auto cols = split_csv_line(line);
        if (cols.size() < 6) continue;
        coefs.push_back(TrackModelCoefficients{
            std::stoi(cols[0]),
            std::stod(cols[2]),
            std::stod(cols[3]),
            std::stod(cols[4]),
            std::stod(cols[5])});
    }
    return coefs;
}

}  // namespace

// ============================================================================
// 1. Point-in-Time Guard & Temporal Boundary Tests
// ============================================================================

TEST(PointInTimeGuardTest, RejectsForecastIssuedOneSecondAfterDecisionTime) {
    const std::string decision_time = "2020-08-15T12:00:00Z";
    const auto res = check_point_in_time(
        decision_time,
        std::nullopt,
        decision_time,
        decision_time,
        {"2020-08-15T12:00:01Z"});

    EXPECT_FALSE(res.passed);
    ASSERT_EQ(res.reasons.size(), 1u);
    EXPECT_EQ(res.reasons[0], "FORECAST_0_ISSUE_TIME_AFTER_DECISION_TIME");
    EXPECT_THROW(enforce_point_in_time(res), PointInTimeViolationError);
}

TEST(PointInTimeGuardTest, AllowsExactTimestampEqualityAtBoundary) {
    const std::string decision_time = "2020-08-15T12:00:00Z";
    const auto res = check_point_in_time(
        decision_time,
        decision_time,
        decision_time,
        "2020-08-15 12:00:00+00:00",
        {decision_time, "2020-08-15T08:00:00-04:00"});

    EXPECT_TRUE(res.passed);
    EXPECT_TRUE(res.reasons.empty());
    EXPECT_NO_THROW(enforce_point_in_time(res));
}

TEST(PointInTimeGuardTest, RejectsFutureTrackAndAmbientAndSpeedObservations) {
    const std::string decision_time = "2020-08-15T12:00:00Z";
    const auto res = check_point_in_time(
        decision_time,
        "2020-08-15T12:00:02Z",
        "2020-08-15T12:00:05Z",
        "2020-08-15T12:01:00Z",
        {decision_time});

    EXPECT_FALSE(res.passed);
    ASSERT_EQ(res.reasons.size(), 3u);
    EXPECT_EQ(res.reasons[0], "CURRENT_OFFICIAL_SPEED_KNOWN_AT_AFTER_DECISION_TIME");
    EXPECT_EQ(res.reasons[1], "CURRENT_TRACK_TEMP_KNOWN_AT_AFTER_DECISION_TIME");
    EXPECT_EQ(res.reasons[2], "CURRENT_AMBIENT_TEMP_KNOWN_AT_AFTER_DECISION_TIME");
}

TEST(PointInTimeGuardTest, HandlesMultipleForecastsWithMixedEligibility) {
    const std::string decision_time = "2021-05-22T16:30:00Z";
    const auto res = check_point_in_time(
        decision_time,
        std::nullopt,
        "2021-05-22T16:15:00Z",
        "2021-05-22T16:15:00Z",
        {"2021-05-22T15:00:00Z", "2021-05-22T16:30:00Z", "2021-05-22T17:00:00Z"});

    EXPECT_FALSE(res.passed);
    ASSERT_EQ(res.reasons.size(), 1u);
    EXPECT_EQ(res.reasons[0], "FORECAST_2_ISSUE_TIME_AFTER_DECISION_TIME");
}

TEST(PointInTimeGuardTest, AcceptsNulloptSpeedTimestampAndRejectsEmptyOrWhitespaceStrings) {
    const std::string decision_time = "2020-08-15T12:00:00Z";
    const auto ok = check_point_in_time(
        decision_time,
        std::nullopt,
        decision_time,
        decision_time,
        {decision_time});
    EXPECT_TRUE(ok.passed);

    EXPECT_THROW(
        check_point_in_time(decision_time, std::string(""), decision_time, decision_time, {}),
        PitEngineError);
    EXPECT_THROW(
        check_point_in_time(decision_time, std::string("   "), decision_time, decision_time, {}),
        PitEngineError);
    EXPECT_THROW(
        check_point_in_time(decision_time, std::nullopt, "", decision_time, {}),
        PitEngineError);
    EXPECT_THROW(
        check_point_in_time(decision_time, std::nullopt, decision_time, "   ", {}),
        PitEngineError);
}

// ============================================================================
// 2. Timestamp Parsing & Formatting Tests
// ============================================================================

TEST(TimestampParsingTest, ParsesZAndOffsetFormatsDeterministically) {
    const std::int64_t t_z = parse_iso8601_utc("2020-08-15T12:15:00Z");
    const std::int64_t t_utc_offset = parse_iso8601_utc("2020-08-15 12:15:00+00:00");
    const std::int64_t t_edt_offset = parse_iso8601_utc("2020-08-15 08:15:00-04:00");
    const std::int64_t t_frac = parse_iso8601_utc("2020-08-15T12:15:00.000000Z");

    EXPECT_EQ(t_z, t_utc_offset);
    EXPECT_EQ(t_z, t_edt_offset);
    EXPECT_EQ(t_z, t_frac);
    EXPECT_EQ(format_iso8601_utc(t_z), "2020-08-15T12:15:00Z");
    EXPECT_EQ(target_time_for("2020-08-15T12:15:00Z", 60), "2020-08-15T13:15:00Z");
}

TEST(TimestampParsingTest, RejectsInvalidDatesAndOffsets) {
    EXPECT_THROW(parse_iso8601_utc(""), PitEngineError);
    EXPECT_THROW(parse_iso8601_utc("2021-02-29T12:00:00Z"), PitEngineError);  // 2021 not leap year
    EXPECT_NO_THROW(parse_iso8601_utc("2020-02-29T12:00:00Z"));               // 2020 is leap year
    EXPECT_THROW(parse_iso8601_utc("2020-13-01T12:00:00Z"), PitEngineError);
    EXPECT_THROW(parse_iso8601_utc("2020-08-15T25:00:00Z"), PitEngineError);
    EXPECT_THROW(parse_iso8601_utc("2020-08-15T12:60:00Z"), PitEngineError);
    EXPECT_THROW(parse_iso8601_utc("2020-08-15T12:00:00+25:00"), PitEngineError);
    EXPECT_THROW(parse_iso8601_utc("2020-08-15T12:00:00Z_extra"), PitEngineError);
}

// ============================================================================
// 3. Timestamp-Aware Processing, Unsorted Determinism & Error Handling
// ============================================================================

TEST(TimeSeriesProcessingTest, FiltersPostCutoffAndMissingKnownAtObservations) {
    const std::vector<TimestampedObservation> obs = {
        {"obs_past", "2020-08-15T11:45:00Z", "2020-08-15T11:45:00Z", 27.5, 22.0, 230.1},
        {"obs_exact", "2020-08-15T12:00:00Z", "2020-08-15T12:00:00Z", 28.5, 23.0, 231.0},
        {"obs_future_obs", "2020-08-15T12:00:01Z", "2020-08-15T12:00:01Z", 35.0, 25.0, 232.5},
        {"obs_future_known", "2020-08-15T11:55:00Z", "2020-08-15T12:05:00Z", 29.0, 23.5, std::nullopt},
        {"obs_missing_known", "2020-08-15T11:30:00Z", std::nullopt, 26.0, 21.0, std::nullopt},
    };

    const auto res = filter_observations_at_cutoff(obs, "2020-08-15T12:00:00Z");
    ASSERT_EQ(res.eligible_sorted.size(), 2u);
    EXPECT_EQ(res.eligible_sorted[0].id, "obs_past");
    EXPECT_EQ(res.eligible_sorted[1].id, "obs_exact");
    ASSERT_TRUE(res.latest_at_or_before.has_value());
    EXPECT_EQ(res.latest_at_or_before->id, "obs_exact");

    ASSERT_EQ(res.excluded_ids.size(), 3u);
    EXPECT_NE(std::find(res.excluded_ids.begin(), res.excluded_ids.end(), "obs_future_obs"), res.excluded_ids.end());
    EXPECT_NE(std::find(res.excluded_ids.begin(), res.excluded_ids.end(), "obs_future_known"), res.excluded_ids.end());
    EXPECT_NE(std::find(res.excluded_ids.begin(), res.excluded_ids.end(), "obs_missing_known"), res.excluded_ids.end());
}

TEST(TimeSeriesProcessingTest, UnsortedInputProducesIdenticalDeterministicOutput) {
    std::vector<TimestampedObservation> base = {
        {"obs_1", "2020-08-15T12:15:00Z", "2020-08-15T12:15:00Z", 26.67, 21.11, std::nullopt},
        {"obs_2", "2020-08-15T12:30:00Z", "2020-08-15T12:30:00Z", 27.22, 21.67, std::nullopt},
        {"obs_3", "2020-08-15T12:45:00Z", "2020-08-15T12:45:00Z", 27.78, 22.22, std::nullopt},
        {"obs_4", "2020-08-15T13:00:00Z", "2020-08-15T13:00:00Z", 28.89, 23.33, std::nullopt},
        {"obs_5_future", "2020-08-15T13:15:00Z", "2020-08-15T13:15:00Z", 30.00, 23.89, std::nullopt},
    };

    const std::string cutoff = "2020-08-15T13:00:00Z";
    const auto ref_filtered = filter_observations_at_cutoff(base, cutoff, true);
    const auto ref_rate = compute_point_in_time_thermal_rate(base, cutoff);
    ASSERT_TRUE(ref_rate.valid);

    std::vector<TimestampedObservation> permuted = {base[4], base[2], base[0], base[3], base[1]};
    const auto perm_filtered = filter_observations_at_cutoff(permuted, cutoff, true);
    const auto perm_rate = compute_point_in_time_thermal_rate(permuted, cutoff);

    ASSERT_EQ(ref_filtered.eligible_sorted.size(), perm_filtered.eligible_sorted.size());
    for (std::size_t i = 0; i < ref_filtered.eligible_sorted.size(); ++i) {
        EXPECT_EQ(ref_filtered.eligible_sorted[i].id, perm_filtered.eligible_sorted[i].id);
        EXPECT_DOUBLE_EQ(ref_filtered.eligible_sorted[i].track_temp_c, perm_filtered.eligible_sorted[i].track_temp_c);
    }
    EXPECT_TRUE(perm_rate.valid);
    EXPECT_DOUBLE_EQ(ref_rate.track_rate_c_per_min, perm_rate.track_rate_c_per_min);
    EXPECT_DOUBLE_EQ(ref_rate.lookback_minutes, perm_rate.lookback_minutes);
    EXPECT_EQ(ref_rate.source_observed_at, perm_rate.source_observed_at);
}

TEST(TimeSeriesProcessingTest, ThermalRateReturnsInvalidWhenNoCandidateInLookbackWindow) {
    // Only one observation before cutoff -> cannot compute rate
    const std::vector<TimestampedObservation> single_obs = {
        {"obs_1", "2020-08-15T12:15:00Z", "2020-08-15T12:15:00Z", 26.67, 21.11, std::nullopt},
    };
    EXPECT_FALSE(compute_point_in_time_thermal_rate(single_obs, "2020-08-15T12:15:00Z").valid);

    // Earlier observation is 75 minutes prior (outside [10, 20] min window)
    const std::vector<TimestampedObservation> gap_obs = {
        {"obs_1", "2020-08-15T13:30:00Z", "2020-08-15T13:30:00Z", 31.11, 23.89, std::nullopt},
        {"obs_2", "2020-08-15T14:45:00Z", "2020-08-15T14:45:00Z", 37.22, 25.56, std::nullopt},
    };
    EXPECT_FALSE(compute_point_in_time_thermal_rate(gap_obs, "2020-08-15T14:45:00Z").valid);
}

TEST(ErrorHandlingTest, HandlesEmptyNaNInvalidCutoffAndDuplicateTimestamps) {
    // 1. Empty input
    EXPECT_THROW(
        filter_observations_at_cutoff({}, "2020-08-15T12:00:00Z"),
        PitEngineError);

    // 2. Invalid time cutoff
    const std::vector<TimestampedObservation> valid_obs = {
        {"obs_1", "2020-08-15T12:00:00Z", "2020-08-15T12:00:00Z", 28.0, 21.0, std::nullopt}
    };
    EXPECT_THROW(
        filter_observations_at_cutoff(valid_obs, "not-a-timestamp"),
        PitEngineError);
    EXPECT_THROW(
        filter_observations_at_cutoff(valid_obs, "2020-02-30T12:00:00Z"),
        PitEngineError);

    // 3. Invalid numerical values (NaN / Inf)
    const std::vector<TimestampedObservation> nan_obs = {
        {"obs_nan", "2020-08-15T12:00:00Z", "2020-08-15T12:00:00Z",
         std::numeric_limits<double>::quiet_NaN(), 21.0, std::nullopt}
    };
    EXPECT_THROW(
        filter_observations_at_cutoff(nan_obs, "2020-08-15T12:00:00Z"),
        PitEngineError);

    const std::vector<TimestampedObservation> inf_obs = {
        {"obs_inf", "2020-08-15T12:00:00Z", "2020-08-15T12:00:00Z",
         28.0, std::numeric_limits<double>::infinity(), std::nullopt}
    };
    EXPECT_THROW(
        filter_observations_at_cutoff(inf_obs, "2020-08-15T12:00:00Z"),
        PitEngineError);

    // 4. Duplicate timestamps when reject_duplicate_timestamps = true
    const std::vector<TimestampedObservation> dup_ts_obs = {
        {"obs_a", "2020-08-15T12:00:00Z", "2020-08-15T12:00:00Z", 28.0, 21.0, std::nullopt},
        {"obs_b", "2020-08-15T12:00:00Z", "2020-08-15T12:00:00Z", 28.5, 21.2, std::nullopt},
    };
    EXPECT_THROW(
        filter_observations_at_cutoff(dup_ts_obs, "2020-08-15T12:00:00Z", true),
        PitEngineError);

    // 5. Duplicate (id, observed_at) always rejected
    const std::vector<TimestampedObservation> dup_id_obs = {
        {"obs_same", "2020-08-15T12:00:00Z", "2020-08-15T12:00:00Z", 28.0, 21.0, std::nullopt},
        {"obs_same", "2020-08-15T12:00:00Z", "2020-08-15T12:00:00Z", 28.0, 21.0, std::nullopt},
    };
    EXPECT_THROW(
        filter_observations_at_cutoff(dup_id_obs, "2020-08-15T12:00:00Z", false),
        PitEngineError);
}

// ============================================================================
// 4. Forecast Vintage Store Point-in-Time Selection Tests
// ============================================================================

TEST(ForecastVintageStoreTest, EnforcesIssueTimeCutoffAndPreferenceRules) {
    ForecastVintageStore store;
    // Older run, exact valid_time match
    store.add(ForecastVintageRecord{
        "f-old-exact", "NOAA", "HRRR", "1",
        "2020-08-15T11:00:00Z", "2020-08-15T13:15:00Z", 135.0, 20.0});
    // Newer run, valid_time 15 min off
    store.add(ForecastVintageRecord{
        "f-new-close", "NOAA", "HRRR", "1",
        "2020-08-15T12:00:00Z", "2020-08-15T13:00:00Z", 60.0, 21.0});
    // Newer run tied on issue_time, valid_time further away
    store.add(ForecastVintageRecord{
        "f-new-far", "NOAA", "HRRR", "3",
        "2020-08-15T12:00:00Z", "2020-08-15T15:00:00Z", 180.0, 25.0});
    // Future run (1 second after decision_time) -> must be excluded
    store.add(ForecastVintageRecord{
        "f-future-leak", "NOAA", "HRRR", "0",
        "2020-08-15T12:15:01Z", "2020-08-15T13:15:00Z", 60.0, 99.0});

    const auto sel = store.select("2020-08-15T12:15:00Z", "2020-08-15T13:15:00Z");
    ASSERT_TRUE(sel.has_value());
    EXPECT_EQ(sel->vintage.forecast_id, "f-new-close");
    EXPECT_DOUBLE_EQ(sel->valid_time_error_minutes, 15.0);

    // Before 11:00:00Z, no forecast is eligible
    const auto none_sel = store.select("2020-08-15T10:59:59Z", "2020-08-15T13:15:00Z");
    EXPECT_FALSE(none_sel.has_value());
}

TEST(ForecastVintageStoreTest, UnsortedVintagesSelectIdentically) {
    const std::vector<ForecastVintageRecord> records = {
        {"f1", "NOAA", "HRRR", "0", "2021-05-22T15:00:00Z", "2021-05-22T17:00:00Z", 120.0, 25.5},
        {"f2", "NOAA", "HRRR", "1", "2021-05-22T16:00:00Z", "2021-05-22T17:00:00Z", 60.0, 26.2},
        {"f3", "NOAA", "HRRR", "2", "2021-05-22T16:00:00Z", "2021-05-22T18:00:00Z", 120.0, 27.0},
        {"f4", "NOAA", "HRRR", "0", "2021-05-22T17:00:00Z", "2021-05-22T17:00:00Z", 0.0, 28.1},
    };

    ForecastVintageStore store_fwd(records);
    std::vector<ForecastVintageRecord> rev = records;
    std::reverse(rev.begin(), rev.end());
    ForecastVintageStore store_rev(rev);

    const auto s1 = store_fwd.select("2021-05-22T16:15:00Z", "2021-05-22T17:15:00Z");
    const auto s2 = store_rev.select("2021-05-22T16:15:00Z", "2021-05-22T17:15:00Z");
    ASSERT_TRUE(s1.has_value());
    ASSERT_TRUE(s2.has_value());
    EXPECT_EQ(s1->vintage.forecast_id, "f2");
    EXPECT_EQ(s1->vintage.forecast_id, s2->vintage.forecast_id);
    EXPECT_DOUBLE_EQ(s1->valid_time_error_minutes, s2->valid_time_error_minutes);
}

// ============================================================================
// 5. Real Historical Data & Frozen Model Parity Tests
// ============================================================================

TEST(HistoricalDataParityTest, SolarElevationAndTrackSamplesMatchFrozenArtifact656Rows) {
    std::ifstream ifs(repo_file("weather/output/v2_future_track/future_track_samples_with_solar_v1.csv"));
    ASSERT_TRUE(ifs.is_open());

    std::string header_line;
    std::getline(ifs, header_line);
    const auto headers = split_csv_line(header_line);

    auto col_idx = [&headers](const std::string& name) -> std::size_t {
        auto it = std::find(headers.begin(), headers.end(), name);
        if (it == headers.end()) {
            throw std::runtime_error("Column not found: " + name);
        }
        return static_cast<std::size_t>(std::distance(headers.begin(), it));
    };

    const std::size_t idx_t0 = col_idx("t0_utc");
    const std::size_t idx_fut = col_idx("future_utc");
    const std::size_t idx_sol0 = col_idx("solar_elevation_0_deg");
    const std::size_t idx_sol1 = col_idx("future_solar_elevation_deg");
    const std::size_t idx_sol_mean = col_idx("solar_elevation_mean_deg");
    const std::size_t idx_track0 = col_idx("track_temp_0_c");
    const std::size_t idx_amb0 = col_idx("ambient_temp_0_c");
    const std::size_t idx_gap0 = col_idx("thermal_gap_0_c");

    std::size_t row_count = 0;
    std::string line;
    while (std::getline(ifs, line)) {
        if (line.empty()) continue;
        const auto cols = split_csv_line(line);
        const double expected_sol0 = std::stod(cols[idx_sol0]);
        const double expected_sol1 = std::stod(cols[idx_sol1]);
        const double expected_mean = std::stod(cols[idx_sol_mean]);
        const double track0 = std::stod(cols[idx_track0]);
        const double amb0 = std::stod(cols[idx_amb0]);
        const double expected_gap = std::stod(cols[idx_gap0]);

        const double actual_sol0 = solar_elevation_deg(cols[idx_t0]);
        const double actual_sol1 = solar_elevation_deg(cols[idx_fut]);
        const double actual_mean = 0.5 * (actual_sol0 + actual_sol1);

        EXPECT_NEAR(actual_sol0, expected_sol0, 1e-12);
        EXPECT_NEAR(actual_sol1, expected_sol1, 1e-12);
        EXPECT_NEAR(actual_mean, expected_mean, 1e-12);
        EXPECT_NEAR(track0 - amb0, expected_gap, 1e-12);
        ++row_count;
    }
    EXPECT_EQ(row_count, 656u);
}

TEST(HistoricalDataParityTest, ApplicabilityGateAndPhysicalResponseMatchFrozenSpecification) {
    // Missing input -> INPUT_INSUFFICIENT
    const auto missing = evaluate_applicability(60, std::nullopt, 27.0, 29.0);
    EXPECT_EQ(missing.status, "INPUT_INSUFFICIENT");
    ASSERT_EQ(missing.reasons.size(), 1u);
    EXPECT_EQ(missing.reasons[0], "MISSING_CURRENT_TRACK_TEMP_C");

    // Above 120 -> OUT_OF_SUPPORT
    const auto above = evaluate_applicability(150, 28.0, 20.0, 19.0);
    EXPECT_EQ(above.status, "OUT_OF_SUPPORT");

    // At or below 0 -> OUT_OF_SUPPORT
    const auto zero = evaluate_applicability(0, 28.0, 20.0, 19.0);
    EXPECT_EQ(zero.status, "OUT_OF_SUPPORT");

    // Non-anchor <= 120 -> CAUTION
    const auto intermediate = evaluate_applicability(45, 28.0, 20.0, 19.0);
    EXPECT_EQ(intermediate.status, "CAUTION");

    // Calibrated anchors -> SUPPORTED
    const auto coefs = load_frozen_track_coefficients();
    ASSERT_EQ(coefs.size(), 5u);
    for (const auto& c : coefs) {
        const auto ok = evaluate_applicability(c.horizon_min, 35.0, 27.0, 29.0);
        EXPECT_EQ(ok.status, "SUPPORTED");

        const std::string t0 = "2021-05-22T16:00:00Z";
        const std::string t1 = target_time_for(t0, c.horizon_min);
        const auto pred = evaluate_physical_response(35.0, 27.0, 29.0, t0, t1, c);
        EXPECT_EQ(pred.horizon_minutes, c.horizon_min);
        EXPECT_DOUBLE_EQ(pred.thermal_gap_0_c, 8.0);
        EXPECT_DOUBLE_EQ(pred.delta_ambient_temp_c, 2.0);
        EXPECT_DOUBLE_EQ(
            pred.predicted_delta_speed_mph,
            kFrozenBetaTrackMphPerC * pred.predicted_delta_track_temp_c +
                kFrozenBetaAmbientMphPerC * pred.delta_ambient_temp_c);
    }
}

TEST(MonteCarloTest, DeterministicRepeatabilityAndQuantileAccuracy) {
    const auto coefs = load_frozen_track_coefficients();
    const TrackModelCoefficients coef60 = coefs[2];  // 60 min

    const std::vector<double> track_pool = {-1.2, -0.5, -0.1, 0.2, 0.7, 1.4};
    const std::vector<std::pair<double, double>> boot_pairs = {
        {-0.030, 0.126},
        {-0.039, 0.269},
        {-0.020, 0.195},
        {-0.054, 0.223},
    };
    const std::vector<double> perf_pool = {-0.45, -0.20, -0.05, 0.10, 0.35, 0.80};

    const auto out1 = run_monte_carlo_inference(
        36.0, 27.0, 29.0,
        "2026-05-22T17:00:00Z", "2026-05-22T18:00:00Z",
        coef60, track_pool, boot_pairs, perf_pool,
        kDefaultImsLatitudeDeg, kDefaultImsLongitudeDeg,
        20260914ULL, 5000);

    const auto out2 = run_monte_carlo_inference(
        36.0, 27.0, 29.0,
        "2026-05-22T17:00:00Z", "2026-05-22T18:00:00Z",
        coef60, track_pool, boot_pairs, perf_pool,
        kDefaultImsLatitudeDeg, kDefaultImsLongitudeDeg,
        20260914ULL, 5000);

    EXPECT_DOUBLE_EQ(out1.expected_delta_v, out2.expected_delta_v);
    EXPECT_DOUBLE_EQ(out1.median_delta_v, out2.median_delta_v);
    EXPECT_DOUBLE_EQ(out1.p_improve, out2.p_improve);
    EXPECT_DOUBLE_EQ(out1.pi80_low, out2.pi80_low);
    EXPECT_DOUBLE_EQ(out1.pi80_high, out2.pi80_high);
    EXPECT_DOUBLE_EQ(out1.pi90_low, out2.pi90_low);
    EXPECT_DOUBLE_EQ(out1.pi90_high, out2.pi90_high);
    EXPECT_DOUBLE_EQ(out1.mc_sd, out2.mc_sd);
}

}  // namespace indy500::pit::tests
