#pragma once

#include <cstdint>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace indy500::pit {

// ============================================================================
// Constants matching the frozen FINAL_V2 / FINAL_V3 repository contracts
// ============================================================================

inline constexpr double kDefaultImsLatitudeDeg = 39.7950;
inline constexpr double kDefaultImsLongitudeDeg = -86.2348;

inline constexpr double kFrozenBetaTrackMphPerC = -0.03482532976361639;
inline constexpr double kFrozenBetaAmbientMphPerC = 0.18239338404039918;

inline constexpr int kMaxSupportedHorizonMin = 120;

// ============================================================================
// Error handling types
// ============================================================================

class PitEngineError : public std::invalid_argument {
public:
    explicit PitEngineError(const std::string& message)
        : std::invalid_argument(message) {}
};

class PointInTimeViolationError : public std::runtime_error {
public:
    explicit PointInTimeViolationError(std::vector<std::string> reasons)
        : std::runtime_error(FormatMessage(reasons)),
          reasons_(std::move(reasons)) {}

    const std::vector<std::string>& reasons() const noexcept { return reasons_; }
    const char* code() const noexcept { return "POINT_IN_TIME_VIOLATION"; }

private:
    static std::string FormatMessage(const std::vector<std::string>& reasons);
    std::vector<std::string> reasons_;
};

// ============================================================================
// Data structures
// ============================================================================

struct GuardResult {
    bool passed{false};
    std::vector<std::string> reasons{};
};

struct TimestampedObservation {
    std::string id{};
    std::string observed_at{};                 // ISO-8601 UTC timestamp
    std::optional<std::string> known_at{};     // ISO-8601 UTC timestamp
    double track_temp_c{0.0};
    double ambient_temp_c{0.0};
    std::optional<double> official_speed_mph{std::nullopt};
};

struct TimeSeriesSelectionResult {
    std::vector<TimestampedObservation> eligible_sorted{};
    std::vector<std::string> excluded_ids{};
    std::optional<TimestampedObservation> latest_at_or_before{};
};

struct ThermalRateResult {
    bool valid{false};
    double track_rate_c_per_min{0.0};
    double lookback_minutes{0.0};
    std::string source_observed_at{};
    double source_track_temp_c{0.0};
};

struct ForecastVintageRecord {
    std::string forecast_id{};
    std::string source{"NOAA"};
    std::string model_name{"HRRR"};
    std::string model_run{};
    std::string issue_time{};   // ISO-8601 UTC; nominal cycle time
    std::string valid_time{};   // ISO-8601 UTC; target valid time
    double lead_minutes{0.0};
    std::optional<double> ambient_temp_c{std::nullopt};
};

struct ForecastSelectionResult {
    ForecastVintageRecord vintage{};
    double valid_time_error_minutes{0.0};
};

struct TrackModelCoefficients {
    int horizon_min{0};
    double intercept_c{0.0};
    double beta_delta_ambient_temp_c{0.0};
    double beta_thermal_gap_0_c{0.0};
    double beta_solar_elevation_mean_deg{0.0};
};

struct DeterministicPhysicalPrediction {
    int horizon_minutes{0};
    double thermal_gap_0_c{0.0};
    double delta_ambient_temp_c{0.0};
    double solar_elevation_0_deg{0.0};
    double solar_elevation_target_deg{0.0};
    double solar_elevation_mean_deg{0.0};
    double predicted_delta_track_temp_c{0.0};
    double predicted_delta_speed_mph{0.0};
};

struct DrawSummary {
    double expected_delta_speed_mph{0.0};
    double median_delta_speed_mph{0.0};
    double lower_80_mph{0.0};
    double upper_80_mph{0.0};
    double lower_90_mph{0.0};
    double upper_90_mph{0.0};
    double p_improve{0.0};
    double mc_sd_mph{0.0};
};

struct ApplicabilityEvaluation {
    std::string status{};
    std::vector<std::string> reasons{};
    std::vector<std::string> notes{};
};

struct MonteCarloScenarioOutput {
    int horizon_minutes{0};
    double expected_delta_v{0.0};
    double median_delta_v{0.0};
    double p_improve{0.0};
    double pi80_low{0.0};
    double pi80_high{0.0};
    double pi90_low{0.0};
    double pi90_high{0.0};
    double mc_sd{0.0};
};

// ============================================================================
// 1. Timestamp Parsing & Point-in-Time Guard
// ============================================================================

// Parse ISO-8601 UTC timestamp (e.g., "2020-08-15T12:00:00Z" or
// "2020-08-15 12:00:00+00:00") into UTC epoch seconds.
// Throws PitEngineError on empty or malformed timestamps.
std::int64_t parse_iso8601_utc(const std::string& ts);

// Format UTC epoch seconds as canonical ISO-8601 UTC string ("YYYY-MM-DDTHH:MM:SSZ").
std::string format_iso8601_utc(std::int64_t epoch_seconds);

// Add horizon_minutes to decision_time and return canonical ISO-8601 UTC string.
std::string target_time_for(const std::string& decision_time, int horizon_min);

// Validate that no input used for a decision is known only in the future.
// Mirrors v3_point_in_time/src/point_in_time_guard.py::check_point_in_time.
GuardResult check_point_in_time(
    const std::string& decision_time,
    const std::optional<std::string>& current_official_speed_known_at,
    const std::string& current_track_temp_known_at,
    const std::string& current_ambient_temp_known_at,
    const std::vector<std::string>& forecast_issue_times);

// Fail-closed enforcement helper: throws PointInTimeViolationError if !guard.passed.
void enforce_point_in_time(const GuardResult& guard_result);

// ============================================================================
// 2. Timestamp-Aware Racing Time-Series Processing
// ============================================================================

// Filter and deterministically sort racing observations available at or before
// cutoff_time.
// - Rejects non-finite numerical temperatures/speeds with PitEngineError.
// - Rejects duplicate (id, observed_at) or duplicate timestamps when
//   reject_duplicate_timestamps=true with PitEngineError.
// - Excludes observations where known_at is missing, or known_at > cutoff_time,
//   or observed_at > cutoff_time.
// - Deterministically sorts eligible observations by (observed_at, known_at, id)
//   regardless of input permutation.
TimeSeriesSelectionResult filter_observations_at_cutoff(
    const std::vector<TimestampedObservation>& observations,
    const std::string& cutoff_time,
    bool reject_duplicate_timestamps = false);

// Compute historical track heating/cooling rate (°C/min) strictly from past
// observations before cutoff_time within the [min_lookback_min, max_lookback_min]
// window, selecting the observation closest to target_lookback_min (default 15.0 min).
// Mirrors weather/scripts/v2_build_future_track_samples.py::find_thermal_rate,
// enforced strictly point-in-time at cutoff_time.
ThermalRateResult compute_point_in_time_thermal_rate(
    const std::vector<TimestampedObservation>& observations,
    const std::string& cutoff_time,
    double target_lookback_min = 15.0,
    double min_lookback_min = 10.0,
    double max_lookback_min = 20.0);

// Point-in-Time Forecast Vintage Store: enforces vintage.issue_time <= decision_time,
// prefers most recent issue_time, and breaks ties by smallest |valid_time - target_time|,
// then lexicographical forecast_id for deterministic tie-breaking on unsorted inputs.
class ForecastVintageStore {
public:
    ForecastVintageStore() = default;
    explicit ForecastVintageStore(const std::vector<ForecastVintageRecord>& vintages);

    void add(const ForecastVintageRecord& vintage);
    std::size_t size() const noexcept { return vintages_.size(); }
    std::vector<ForecastVintageRecord> all() const;

    std::optional<ForecastSelectionResult> select(
        const std::string& decision_time,
        const std::string& target_time) const;

private:
    struct StoredVintage {
        ForecastVintageRecord record{};
        std::int64_t issue_epoch{0};
        std::int64_t valid_epoch{0};
    };
    std::vector<StoredVintage> vintages_{};
};

// ============================================================================
// 3. Validated Domain Racing Performance Calculations (FINAL_V2 / FINAL_V3)
// ============================================================================

// NOAA-style solar elevation angle in degrees for a UTC timestamp and coordinates.
// Mirrors weather/scripts/v2_add_solar_features.py::solar_elevation_deg.
double solar_elevation_deg(
    const std::string& timestamp_utc,
    double latitude_deg = kDefaultImsLatitudeDeg,
    double longitude_deg = kDefaultImsLongitudeDeg);

// Applicability gate matching v3_point_in_time/src/applicability_gate.py::evaluate.
ApplicabilityEvaluation evaluate_applicability(
    int horizon_min,
    std::optional<double> current_track_temp_c,
    std::optional<double> current_ambient_temp_c,
    std::optional<double> forecast_future_ambient_temp_c);

// Evaluate the frozen M2b_mean_solar track-temperature change model and
// frozen zero-intercept physical speed response (Δv_physical = β_track ΔT_track + β_ambient ΔT_ambient).
DeterministicPhysicalPrediction evaluate_physical_response(
    double current_track_temp_c,
    double current_ambient_temp_c,
    double forecast_future_ambient_temp_c,
    const std::string& decision_time,
    const std::string& target_time,
    const TrackModelCoefficients& track_coef,
    double latitude_deg = kDefaultImsLatitudeDeg,
    double longitude_deg = kDefaultImsLongitudeDeg,
    double beta_track_mph_per_c = kFrozenBetaTrackMphPerC,
    double beta_ambient_mph_per_c = kFrozenBetaAmbientMphPerC);

// Exact NumPy-compatible linear quantile and summary statistics over Monte Carlo draws.
// Mirrors weather/scripts/v2_integrate_track_to_performance_mc.py::summarize_draws.
DrawSummary summarize_draws(const std::vector<double>& draws);

// Combine pre-sampled or C++-sampled Monte Carlo draws for track residuals,
// paired bootstrap coefficients, and performance residuals into a single-horizon
// FinalV2Output summary.
MonteCarloScenarioOutput evaluate_monte_carlo_draws(
    int horizon_min,
    double point_delta_track_c,
    double delta_ambient_temp_c,
    const std::vector<double>& track_noise_draws,
    const std::vector<double>& beta_track_draws,
    const std::vector<double>& beta_ambient_draws,
    const std::vector<double>& perf_noise_draws);

// Standalone deterministic C++ Monte Carlo inference from frozen pools using a
// deterministic 64-bit Mersenne Twister (std::mt19937_64) seeded with random_seed.
MonteCarloScenarioOutput run_monte_carlo_inference(
    double current_track_temp_c,
    double current_ambient_temp_c,
    double forecast_future_ambient_temp_c,
    const std::string& decision_time,
    const std::string& target_time,
    const TrackModelCoefficients& track_coef,
    const std::vector<double>& track_residual_pool,
    const std::vector<std::pair<double, double>>& bootstrap_coef_pairs,
    const std::vector<double>& performance_residual_pool,
    double latitude_deg,
    double longitude_deg,
    std::uint64_t random_seed,
    std::size_t n_mc);

}  // namespace indy500::pit
