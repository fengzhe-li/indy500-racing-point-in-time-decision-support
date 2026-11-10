#include "indy500/pit_engine.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <cstdio>
#include <numeric>
#include <random>
#include <set>
#include <sstream>

namespace indy500::pit {

namespace {

constexpr double kPi = 3.14159265358979323846;

bool is_leap_year(int year) noexcept {
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
}

int days_in_month(int year, int month) noexcept {
    static constexpr std::array<int, 12> kDays = {
        31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    if (month == 2 && is_leap_year(year)) {
        return 29;
    }
    if (month < 1 || month > 12) {
        return 0;
    }
    return kDays[static_cast<std::size_t>(month - 1)];
}

// Howard Hinnant's civil calendar algorithm (proleptic Gregorian calendar)
std::int64_t days_from_civil(int y, unsigned m, unsigned d) noexcept {
    y -= m <= 2;
    const int era = (y >= 0 ? y : y - 399) / 400;
    const unsigned yoe = static_cast<unsigned>(y - era * 400);
    const unsigned doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1;
    const unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    return static_cast<std::int64_t>(era) * 146097 + static_cast<std::int64_t>(doe) - 719468;
}

void civil_from_days(std::int64_t z, int& y, unsigned& m, unsigned& d) noexcept {
    z += 719468;
    const std::int64_t era = (z >= 0 ? z : z - 146096) / 146097;
    const unsigned doe = static_cast<unsigned>(z - era * 146097);
    const unsigned yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    y = static_cast<int>(yoe) + static_cast<int>(era) * 400;
    const unsigned doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    const unsigned mp = (5 * doy + 2) / 153;
    d = doy - (153 * mp + 2) / 5 + 1;
    m = mp + (mp < 10 ? 3 : -9);
    y += (m <= 2);
}

int day_of_year_from_civil(int year, unsigned month, unsigned day) noexcept {
    static constexpr std::array<int, 12> kCumulative = {
        0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334};
    int doy = kCumulative[static_cast<std::size_t>(month - 1)] + static_cast<int>(day);
    if (month > 2 && is_leap_year(year)) {
        doy += 1;
    }
    return doy;
}

bool parse_fixed_digits(const std::string& s, std::size_t pos, std::size_t len, int& out) noexcept {
    if (pos + len > s.size()) {
        return false;
    }
    int val = 0;
    for (std::size_t i = 0; i < len; ++i) {
        const unsigned char c = static_cast<unsigned char>(s[pos + i]);
        if (!std::isdigit(c)) {
            return false;
        }
        val = val * 10 + (c - '0');
    }
    out = val;
    return true;
}

void require_finite(double value, const char* name) {
    if (!std::isfinite(value)) {
        throw PitEngineError(std::string("Non-finite numerical value for ") + name);
    }
}

bool is_calibrated_anchor_horizon(int horizon_min) noexcept {
    return horizon_min == 15 || horizon_min == 30 || horizon_min == 60 ||
           horizon_min == 90 || horizon_min == 120;
}

double quantile_linear_sorted(const std::vector<double>& sorted_vals, double q) {
    if (sorted_vals.empty()) {
        throw PitEngineError("Cannot compute quantile of empty draw vector");
    }
    if (sorted_vals.size() == 1) {
        return sorted_vals[0];
    }
    const double virtual_idx = q * static_cast<double>(sorted_vals.size() - 1);
    const auto lo_idx = static_cast<std::size_t>(std::floor(virtual_idx));
    const auto hi_idx = static_cast<std::size_t>(std::ceil(virtual_idx));
    const double frac = virtual_idx - static_cast<double>(lo_idx);
    return sorted_vals[lo_idx] + frac * (sorted_vals[hi_idx] - sorted_vals[lo_idx]);
}

}  // namespace

std::string PointInTimeViolationError::FormatMessage(const std::vector<std::string>& reasons) {
    std::ostringstream oss;
    oss << "POINT_IN_TIME_VIOLATION: (";
    for (std::size_t i = 0; i < reasons.size(); ++i) {
        if (i > 0) {
            oss << ", ";
        }
        oss << "'" << reasons[i] << "'";
    }
    oss << ")";
    return oss.str();
}

std::int64_t parse_iso8601_utc(const std::string& ts) {
    if (ts.size() < 19) {
        throw PitEngineError("Invalid ISO-8601 timestamp (too short): '" + ts + "'");
    }
    int year = 0, month = 0, day = 0, hour = 0, minute = 0, second = 0;
    if (!parse_fixed_digits(ts, 0, 4, year) ||
        ts[4] != '-' ||
        !parse_fixed_digits(ts, 5, 2, month) ||
        ts[7] != '-' ||
        !parse_fixed_digits(ts, 8, 2, day) ||
        (ts[10] != 'T' && ts[10] != ' ' && ts[10] != 't') ||
        !parse_fixed_digits(ts, 11, 2, hour) ||
        ts[13] != ':' ||
        !parse_fixed_digits(ts, 14, 2, minute) ||
        ts[16] != ':' ||
        !parse_fixed_digits(ts, 17, 2, second)) {
        throw PitEngineError("Invalid ISO-8601 timestamp format: '" + ts + "'");
    }

    if (month < 1 || month > 12) {
        throw PitEngineError("Invalid month in timestamp: '" + ts + "'");
    }
    const int max_day = days_in_month(year, month);
    if (day < 1 || day > max_day) {
        throw PitEngineError("Invalid day of month in timestamp: '" + ts + "'");
    }
    if (hour < 0 || hour > 23 || minute < 0 || minute > 59 || second < 0 || second > 59) {
        throw PitEngineError("Invalid time-of-day in timestamp: '" + ts + "'");
    }

    std::size_t pos = 19;
    // Optional fractional seconds (.sss...)
    if (pos < ts.size() && ts[pos] == '.') {
        ++pos;
        if (pos == ts.size() || !std::isdigit(static_cast<unsigned char>(ts[pos]))) {
            throw PitEngineError("Invalid fractional seconds in timestamp: '" + ts + "'");
        }
        while (pos < ts.size() && std::isdigit(static_cast<unsigned char>(ts[pos]))) {
            ++pos;
        }
    }

    int offset_seconds = 0;
    if (pos < ts.size()) {
        const char tz_char = ts[pos];
        if (tz_char == 'Z' || tz_char == 'z') {
            ++pos;
            if (pos != ts.size()) {
                throw PitEngineError("Trailing characters after 'Z' in timestamp: '" + ts + "'");
            }
        } else if (tz_char == '+' || tz_char == '-') {
            const int sign = (tz_char == '-') ? -1 : 1;
            ++pos;
            int tz_hour = 0, tz_min = 0;
            if (!parse_fixed_digits(ts, pos, 2, tz_hour)) {
                throw PitEngineError("Invalid timezone offset hour in timestamp: '" + ts + "'");
            }
            pos += 2;
            if (pos < ts.size() && ts[pos] == ':') {
                ++pos;
            }
            if (!parse_fixed_digits(ts, pos, 2, tz_min)) {
                throw PitEngineError("Invalid timezone offset minute in timestamp: '" + ts + "'");
            }
            pos += 2;
            if (pos != ts.size()) {
                throw PitEngineError("Trailing characters after timezone offset in timestamp: '" + ts + "'");
            }
            if (tz_hour > 23 || tz_min > 59) {
                throw PitEngineError("Timezone offset out of range in timestamp: '" + ts + "'");
            }
            offset_seconds = sign * (tz_hour * 3600 + tz_min * 60);
        } else {
            throw PitEngineError("Invalid timezone suffix in timestamp: '" + ts + "'");
        }
    }

    const std::int64_t days = days_from_civil(
        year, static_cast<unsigned>(month), static_cast<unsigned>(day));
    const std::int64_t local_epoch =
        days * 86400 + static_cast<std::int64_t>(hour) * 3600 +
        static_cast<std::int64_t>(minute) * 60 + static_cast<std::int64_t>(second);
    return local_epoch - offset_seconds;
}

std::string format_iso8601_utc(std::int64_t epoch_seconds) {
    std::int64_t days = epoch_seconds / 86400;
    std::int64_t rem = epoch_seconds % 86400;
    if (rem < 0) {
        rem += 86400;
        days -= 1;
    }
    int year = 0;
    unsigned month = 0, day = 0;
    civil_from_days(days, year, month, day);
    const int hour = static_cast<int>(rem / 3600);
    rem %= 3600;
    const int minute = static_cast<int>(rem / 60);
    const int second = static_cast<int>(rem % 60);

    char buf[32];
    std::snprintf(
        buf, sizeof(buf), "%04d-%02u-%02uT%02d:%02d:%02dZ",
        year, month, day, hour, minute, second);
    return std::string(buf);
}

std::string target_time_for(const std::string& decision_time, int horizon_min) {
    const std::int64_t t0 = parse_iso8601_utc(decision_time);
    return format_iso8601_utc(t0 + static_cast<std::int64_t>(horizon_min) * 60);
}

GuardResult check_point_in_time(
    const std::string& decision_time,
    const std::optional<std::string>& current_official_speed_known_at,
    const std::string& current_track_temp_known_at,
    const std::string& current_ambient_temp_known_at,
    const std::vector<std::string>& forecast_issue_times) {
    const std::int64_t t_decision = parse_iso8601_utc(decision_time);
    std::vector<std::string> reasons;

    if (current_official_speed_known_at.has_value()) {
        if (parse_iso8601_utc(*current_official_speed_known_at) > t_decision) {
            reasons.emplace_back("CURRENT_OFFICIAL_SPEED_KNOWN_AT_AFTER_DECISION_TIME");
        }
    }
    if (parse_iso8601_utc(current_track_temp_known_at) > t_decision) {
        reasons.emplace_back("CURRENT_TRACK_TEMP_KNOWN_AT_AFTER_DECISION_TIME");
    }
    if (parse_iso8601_utc(current_ambient_temp_known_at) > t_decision) {
        reasons.emplace_back("CURRENT_AMBIENT_TEMP_KNOWN_AT_AFTER_DECISION_TIME");
    }

    for (std::size_t i = 0; i < forecast_issue_times.size(); ++i) {
        if (parse_iso8601_utc(forecast_issue_times[i]) > t_decision) {
            reasons.emplace_back(
                "FORECAST_" + std::to_string(i) + "_ISSUE_TIME_AFTER_DECISION_TIME");
        }
    }

    return GuardResult{reasons.empty(), std::move(reasons)};
}

void enforce_point_in_time(const GuardResult& guard_result) {
    if (!guard_result.passed) {
        throw PointInTimeViolationError(guard_result.reasons);
    }
}

TimeSeriesSelectionResult filter_observations_at_cutoff(
    const std::vector<TimestampedObservation>& observations,
    const std::string& cutoff_time,
    bool reject_duplicate_timestamps) {
    const std::int64_t t_cutoff = parse_iso8601_utc(cutoff_time);

    if (observations.empty()) {
        throw PitEngineError("Empty observation series passed to filter_observations_at_cutoff");
    }

    struct ParsedObs {
        TimestampedObservation obs;
        std::int64_t t_observed;
        std::int64_t t_known;
    };

    std::vector<ParsedObs> eligible;
    std::vector<std::string> excluded_ids;
    std::set<std::int64_t> seen_observed_epochs;
    std::set<std::pair<std::string, std::int64_t>> seen_id_epochs;

    for (const auto& obs : observations) {
        if (obs.id.empty()) {
            throw PitEngineError("Observation id must not be empty");
        }
        require_finite(obs.track_temp_c, "track_temp_c");
        require_finite(obs.ambient_temp_c, "ambient_temp_c");
        if (obs.official_speed_mph.has_value()) {
            require_finite(*obs.official_speed_mph, "official_speed_mph");
        }

        const std::int64_t t_obs = parse_iso8601_utc(obs.observed_at);
        if (!seen_id_epochs.emplace(obs.id, t_obs).second) {
            throw PitEngineError("Duplicate observation (id, observed_at) detected for id='" + obs.id + "'");
        }
        if (reject_duplicate_timestamps && !seen_observed_epochs.emplace(t_obs).second) {
            throw PitEngineError("Duplicate timestamp detected in observation series at '" + obs.observed_at + "'");
        }

        if (!obs.known_at.has_value()) {
            excluded_ids.push_back(obs.id);
            continue;
        }
        const std::int64_t t_known = parse_iso8601_utc(*obs.known_at);
        if (t_obs > t_cutoff || t_known > t_cutoff) {
            excluded_ids.push_back(obs.id);
            continue;
        }
        eligible.push_back(ParsedObs{obs, t_obs, t_known});
    }

    // Deterministic sort regardless of input order:
    // 1. observed_at ascending
    // 2. known_at ascending
    // 3. id lexicographical ascending
    std::sort(eligible.begin(), eligible.end(), [](const ParsedObs& a, const ParsedObs& b) {
        if (a.t_observed != b.t_observed) {
            return a.t_observed < b.t_observed;
        }
        if (a.t_known != b.t_known) {
            return a.t_known < b.t_known;
        }
        return a.obs.id < b.obs.id;
    });

    TimeSeriesSelectionResult result;
    result.eligible_sorted.reserve(eligible.size());
    for (auto& item : eligible) {
        result.eligible_sorted.push_back(std::move(item.obs));
    }
    result.excluded_ids = std::move(excluded_ids);
    if (!result.eligible_sorted.empty()) {
        result.latest_at_or_before = result.eligible_sorted.back();
    }
    return result;
}

ThermalRateResult compute_point_in_time_thermal_rate(
    const std::vector<TimestampedObservation>& observations,
    const std::string& cutoff_time,
    double target_lookback_min,
    double min_lookback_min,
    double max_lookback_min) {
    require_finite(target_lookback_min, "target_lookback_min");
    require_finite(min_lookback_min, "min_lookback_min");
    require_finite(max_lookback_min, "max_lookback_min");
    if (min_lookback_min <= 0.0 || max_lookback_min < min_lookback_min) {
        throw PitEngineError("Invalid lookback window parameters for thermal rate calculation");
    }

    const TimeSeriesSelectionResult filtered =
        filter_observations_at_cutoff(observations, cutoff_time, false);
    if (filtered.eligible_sorted.size() < 2) {
        return ThermalRateResult{};
    }

    const TimestampedObservation& current = filtered.eligible_sorted.back();
    const std::int64_t t0 = parse_iso8601_utc(current.observed_at);

    struct Candidate {
        double distance_from_target;
        double lookback_min;
        std::string id;
        TimestampedObservation obs;
    };

    std::vector<Candidate> candidates;
    for (std::size_t i = 0; i + 1 < filtered.eligible_sorted.size(); ++i) {
        const auto& earlier = filtered.eligible_sorted[i];
        const std::int64_t t_earlier = parse_iso8601_utc(earlier.observed_at);
        if (t_earlier >= t0) {
            continue;
        }
        const double lookback_min = static_cast<double>(t0 - t_earlier) / 60.0;
        if (lookback_min >= min_lookback_min && lookback_min <= max_lookback_min) {
            candidates.push_back(Candidate{
                std::abs(lookback_min - target_lookback_min),
                lookback_min,
                earlier.id,
                earlier});
        }
    }

    if (candidates.empty()) {
        return ThermalRateResult{};
    }

    // Match weather/scripts/v2_build_future_track_samples.py::find_thermal_rate:
    // sort by (distance_from_15, lookback_min, id)
    std::sort(candidates.begin(), candidates.end(), [](const Candidate& a, const Candidate& b) {
        if (std::abs(a.distance_from_target - b.distance_from_target) > 1e-12) {
            return a.distance_from_target < b.distance_from_target;
        }
        if (std::abs(a.lookback_min - b.lookback_min) > 1e-12) {
            return a.lookback_min < b.lookback_min;
        }
        return a.id < b.id;
    });

    const Candidate& best = candidates.front();
    const double rate = (current.track_temp_c - best.obs.track_temp_c) / best.lookback_min;

    return ThermalRateResult{
        true,
        rate,
        best.lookback_min,
        best.obs.observed_at,
        best.obs.track_temp_c};
}

ForecastVintageStore::ForecastVintageStore(const std::vector<ForecastVintageRecord>& vintages) {
    vintages_.reserve(vintages.size());
    for (const auto& v : vintages) {
        add(v);
    }
}

void ForecastVintageStore::add(const ForecastVintageRecord& vintage) {
    if (vintage.forecast_id.empty()) {
        throw PitEngineError("ForecastVintageRecord forecast_id must not be empty");
    }
    const std::int64_t t_issue = parse_iso8601_utc(vintage.issue_time);
    const std::int64_t t_valid = parse_iso8601_utc(vintage.valid_time);
    require_finite(vintage.lead_minutes, "lead_minutes");
    if (vintage.ambient_temp_c.has_value()) {
        require_finite(*vintage.ambient_temp_c, "ambient_temp_c");
    }
    vintages_.push_back(StoredVintage{vintage, t_issue, t_valid});
}

std::vector<ForecastVintageRecord> ForecastVintageStore::all() const {
    std::vector<ForecastVintageRecord> out;
    out.reserve(vintages_.size());
    for (const auto& sv : vintages_) {
        out.push_back(sv.record);
    }
    return out;
}

std::optional<ForecastSelectionResult> ForecastVintageStore::select(
    const std::string& decision_time,
    const std::string& target_time) const {
    const std::int64_t t_decision = parse_iso8601_utc(decision_time);
    const std::int64_t t_target = parse_iso8601_utc(target_time);

    const StoredVintage* best = nullptr;
    std::int64_t best_abs_err_sec = 0;

    for (const auto& sv : vintages_) {
        if (sv.issue_epoch > t_decision) {
            continue;
        }
        const std::int64_t err_sec = std::abs(sv.valid_epoch - t_target);
        if (best == nullptr) {
            best = &sv;
            best_abs_err_sec = err_sec;
            continue;
        }
        // Preference order:
        // 1. Most recent issue_time (largest issue_epoch)
        // 2. Smallest |valid_time - target_time|
        // 3. Lexicographically smallest forecast_id (deterministic tie-breaker)
        if (sv.issue_epoch > best->issue_epoch ||
            (sv.issue_epoch == best->issue_epoch && err_sec < best_abs_err_sec) ||
            (sv.issue_epoch == best->issue_epoch && err_sec == best_abs_err_sec &&
             sv.record.forecast_id < best->record.forecast_id)) {
            best = &sv;
            best_abs_err_sec = err_sec;
        }
    }

    if (best == nullptr) {
        return std::nullopt;
    }

    const double error_minutes = static_cast<double>(best_abs_err_sec) / 60.0;
    return ForecastSelectionResult{best->record, error_minutes};
}

double solar_elevation_deg(
    const std::string& timestamp_utc,
    double latitude_deg,
    double longitude_deg) {
    require_finite(latitude_deg, "latitude_deg");
    require_finite(longitude_deg, "longitude_deg");
    if (latitude_deg < -90.0 || latitude_deg > 90.0 ||
        longitude_deg < -180.0 || longitude_deg > 180.0) {
        throw PitEngineError("Geographic coordinates out of valid range");
    }

    const std::int64_t epoch_sec = parse_iso8601_utc(timestamp_utc);
    std::int64_t days = epoch_sec / 86400;
    std::int64_t rem = epoch_sec % 86400;
    if (rem < 0) {
        rem += 86400;
        days -= 1;
    }
    int year = 0;
    unsigned month = 0, day = 0;
    civil_from_days(days, year, month, day);

    const int day_of_year = day_of_year_from_civil(year, month, day);
    const int hour = static_cast<int>(rem / 3600);
    rem %= 3600;
    const int minute = static_cast<int>(rem / 60);
    const int second = static_cast<int>(rem % 60);

    const double hour_decimal =
        static_cast<double>(hour) +
        static_cast<double>(minute) / 60.0 +
        static_cast<double>(second) / 3600.0;

    const double gamma =
        (2.0 * kPi / 365.0) *
        (static_cast<double>(day_of_year - 1) + (hour_decimal - 12.0) / 24.0);

    const double equation_of_time = 229.18 * (
        0.000075 +
        0.001868 * std::cos(gamma) -
        0.032077 * std::sin(gamma) -
        0.014615 * std::cos(2.0 * gamma) -
        0.040849 * std::sin(2.0 * gamma));

    const double solar_declination =
        0.006918 -
        0.399912 * std::cos(gamma) +
        0.070257 * std::sin(gamma) -
        0.006758 * std::cos(2.0 * gamma) +
        0.000907 * std::sin(2.0 * gamma) -
        0.002697 * std::cos(3.0 * gamma) +
        0.00148 * std::sin(3.0 * gamma);

    double true_solar_time =
        std::fmod(hour_decimal * 60.0 + equation_of_time + 4.0 * longitude_deg, 1440.0);
    if (true_solar_time < 0.0) {
        true_solar_time += 1440.0;
    }

    const double hour_angle_deg = true_solar_time / 4.0 - 180.0;
    const double hour_angle_rad = hour_angle_deg * (kPi / 180.0);
    const double latitude_rad = latitude_deg * (kPi / 180.0);

    double cos_zenith =
        std::sin(latitude_rad) * std::sin(solar_declination) +
        std::cos(latitude_rad) * std::cos(solar_declination) * std::cos(hour_angle_rad);
    cos_zenith = std::max(-1.0, std::min(1.0, cos_zenith));

    const double zenith_rad = std::acos(cos_zenith);
    return 90.0 - (zenith_rad * 180.0 / kPi);
}

ApplicabilityEvaluation evaluate_applicability(
    int horizon_min,
    std::optional<double> current_track_temp_c,
    std::optional<double> current_ambient_temp_c,
    std::optional<double> forecast_future_ambient_temp_c) {
    std::vector<std::string> missing;
    auto check_opt = [&missing](const std::optional<double>& val, const char* code) {
        if (!val.has_value()) {
            missing.emplace_back(code);
        } else if (!std::isfinite(*val)) {
            throw PitEngineError(std::string("Non-finite input passed to evaluate_applicability: ") + code);
        }
    };

    check_opt(current_track_temp_c, "MISSING_CURRENT_TRACK_TEMP_C");
    check_opt(current_ambient_temp_c, "MISSING_CURRENT_AMBIENT_TEMP_C");
    check_opt(forecast_future_ambient_temp_c, "MISSING_FORECAST_FUTURE_AMBIENT_TEMP_C");

    if (!missing.empty()) {
        return ApplicabilityEvaluation{"INPUT_INSUFFICIENT", std::move(missing), {}};
    }

    if (horizon_min > kMaxSupportedHorizonMin) {
        return ApplicabilityEvaluation{
            "OUT_OF_SUPPORT",
            {"HORIZON_" + std::to_string(horizon_min) +
             "_MIN_EXCEEDS_MAX_SUPPORTED_" + std::to_string(kMaxSupportedHorizonMin) + "_MIN"},
            {}};
    }

    if (horizon_min <= 0) {
        return ApplicabilityEvaluation{
            "OUT_OF_SUPPORT",
            {"HORIZON_AT_OR_BELOW_CURRENT_STATE_BOUNDARY"},
            {"Matches CURRENT_STATE_BOUNDARY policy in operational_curve_metadata_v2.json."}};
    }

    if (!is_calibrated_anchor_horizon(horizon_min)) {
        return ApplicabilityEvaluation{
            "CAUTION",
            {"HORIZON_" + std::to_string(horizon_min) + "_MIN_NOT_A_CALIBRATED_ANCHOR"},
            {"Frozen system anchors are exactly 15/30/60/90/120 min; "
             "intermediate minutes are INTERPOLATED_OPERATIONAL presentation "
             "values in the frozen operational curve, not independently "
             "calibrated FINAL_V2 scientific inference."}};
    }

    return ApplicabilityEvaluation{
        "SUPPORTED",
        {},
        {"No numeric historical-support boundary for arbitrary current "
         "track/ambient state is published by the frozen system "
         "(existing_system_inventory.md section 7): NOT_YET_DEFINED. "
         "This gate does not invent one, so a physically extreme but "
         "otherwise complete input still returns SUPPORTED here."}};
}

DeterministicPhysicalPrediction evaluate_physical_response(
    double current_track_temp_c,
    double current_ambient_temp_c,
    double forecast_future_ambient_temp_c,
    const std::string& decision_time,
    const std::string& target_time,
    const TrackModelCoefficients& track_coef,
    double latitude_deg,
    double longitude_deg,
    double beta_track_mph_per_c,
    double beta_ambient_mph_per_c) {
    require_finite(current_track_temp_c, "current_track_temp_c");
    require_finite(current_ambient_temp_c, "current_ambient_temp_c");
    require_finite(forecast_future_ambient_temp_c, "forecast_future_ambient_temp_c");
    require_finite(track_coef.intercept_c, "track_coef.intercept_c");
    require_finite(track_coef.beta_delta_ambient_temp_c, "track_coef.beta_delta_ambient_temp_c");
    require_finite(track_coef.beta_thermal_gap_0_c, "track_coef.beta_thermal_gap_0_c");
    require_finite(track_coef.beta_solar_elevation_mean_deg, "track_coef.beta_solar_elevation_mean_deg");
    require_finite(beta_track_mph_per_c, "beta_track_mph_per_c");
    require_finite(beta_ambient_mph_per_c, "beta_ambient_mph_per_c");

    if (!is_calibrated_anchor_horizon(track_coef.horizon_min)) {
        throw PitEngineError(
            "Unsupported horizon_min=" + std::to_string(track_coef.horizon_min) +
            "; supported calibrated anchors are {15, 30, 60, 90, 120}");
    }

    const std::int64_t t0 = parse_iso8601_utc(decision_time);
    const std::int64_t t1 = parse_iso8601_utc(target_time);
    if (t1 < t0) {
        throw PitEngineError("target_time must not be earlier than decision_time");
    }

    const double thermal_gap_0_c = current_track_temp_c - current_ambient_temp_c;
    const double delta_ambient_temp_c = forecast_future_ambient_temp_c - current_ambient_temp_c;

    const double solar_0 = solar_elevation_deg(decision_time, latitude_deg, longitude_deg);
    const double solar_1 = solar_elevation_deg(target_time, latitude_deg, longitude_deg);
    const double solar_mean = (solar_0 + solar_1) / 2.0;

    const double point_delta_track_c =
        track_coef.intercept_c +
        track_coef.beta_delta_ambient_temp_c * delta_ambient_temp_c +
        track_coef.beta_thermal_gap_0_c * thermal_gap_0_c +
        track_coef.beta_solar_elevation_mean_deg * solar_mean;

    // Frozen zero-intercept physical response:
    // Δv_physical = β_track ΔT_track + β_ambient ΔT_ambient
    const double predicted_delta_speed_mph =
        beta_track_mph_per_c * point_delta_track_c +
        beta_ambient_mph_per_c * delta_ambient_temp_c;

    return DeterministicPhysicalPrediction{
        track_coef.horizon_min,
        thermal_gap_0_c,
        delta_ambient_temp_c,
        solar_0,
        solar_1,
        solar_mean,
        point_delta_track_c,
        predicted_delta_speed_mph};
}

DrawSummary summarize_draws(const std::vector<double>& draws) {
    if (draws.size() < 2) {
        throw PitEngineError("summarize_draws requires at least 2 Monte Carlo draws");
    }

    std::vector<double> sorted_draws;
    sorted_draws.reserve(draws.size());
    double sum = 0.0;
    std::size_t improve_count = 0;

    for (double val : draws) {
        require_finite(val, "monte_carlo_draw");
        sorted_draws.push_back(val);
        sum += val;
        if (val > 0.0) {
            ++improve_count;
        }
    }

    std::sort(sorted_draws.begin(), sorted_draws.end());

    const double n_d = static_cast<double>(draws.size());
    const double mean = sum / n_d;

    double sq_diff_sum = 0.0;
    for (double val : draws) {
        const double d = val - mean;
        sq_diff_sum += d * d;
    }
    const double sd = std::sqrt(sq_diff_sum / static_cast<double>(draws.size() - 1));

    return DrawSummary{
        mean,
        quantile_linear_sorted(sorted_draws, 0.50),
        quantile_linear_sorted(sorted_draws, 0.10),
        quantile_linear_sorted(sorted_draws, 0.90),
        quantile_linear_sorted(sorted_draws, 0.05),
        quantile_linear_sorted(sorted_draws, 0.95),
        static_cast<double>(improve_count) / n_d,
        sd};
}

MonteCarloScenarioOutput evaluate_monte_carlo_draws(
    int horizon_min,
    double point_delta_track_c,
    double delta_ambient_temp_c,
    const std::vector<double>& track_noise_draws,
    const std::vector<double>& beta_track_draws,
    const std::vector<double>& beta_ambient_draws,
    const std::vector<double>& perf_noise_draws) {
    if (!is_calibrated_anchor_horizon(horizon_min)) {
        throw PitEngineError("Unsupported horizon_min in evaluate_monte_carlo_draws");
    }
    require_finite(point_delta_track_c, "point_delta_track_c");
    require_finite(delta_ambient_temp_c, "delta_ambient_temp_c");

    const std::size_t n = track_noise_draws.size();
    if (n < 2 || beta_track_draws.size() != n ||
        beta_ambient_draws.size() != n || perf_noise_draws.size() != n) {
        throw PitEngineError("Monte Carlo draw vectors must have identical size >= 2");
    }

    std::vector<double> delta_speed_draws(n);
    for (std::size_t i = 0; i < n; ++i) {
        require_finite(track_noise_draws[i], "track_noise_draw");
        require_finite(beta_track_draws[i], "beta_track_draw");
        require_finite(beta_ambient_draws[i], "beta_ambient_draw");
        require_finite(perf_noise_draws[i], "perf_noise_draw");

        const double delta_track = point_delta_track_c + track_noise_draws[i];
        delta_speed_draws[i] =
            beta_track_draws[i] * delta_track +
            beta_ambient_draws[i] * delta_ambient_temp_c +
            perf_noise_draws[i];
    }

    const DrawSummary summary = summarize_draws(delta_speed_draws);
    return MonteCarloScenarioOutput{
        horizon_min,
        summary.expected_delta_speed_mph,
        summary.median_delta_speed_mph,
        summary.p_improve,
        summary.lower_80_mph,
        summary.upper_80_mph,
        summary.lower_90_mph,
        summary.upper_90_mph,
        summary.mc_sd_mph};
}

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
    std::size_t n_mc) {
    if (n_mc < 2) {
        throw PitEngineError("n_mc must be at least 2");
    }
    if (track_residual_pool.empty()) {
        throw PitEngineError("track_residual_pool must not be empty");
    }
    if (bootstrap_coef_pairs.empty()) {
        throw PitEngineError("bootstrap_coef_pairs must not be empty");
    }
    if (performance_residual_pool.empty()) {
        throw PitEngineError("performance_residual_pool must not be empty");
    }

    for (double v : track_residual_pool) {
        require_finite(v, "track_residual_pool");
    }
    for (const auto& p : bootstrap_coef_pairs) {
        require_finite(p.first, "bootstrap_beta_track");
        require_finite(p.second, "bootstrap_beta_ambient");
    }
    for (double v : performance_residual_pool) {
        require_finite(v, "performance_residual_pool");
    }

    const DeterministicPhysicalPrediction det = evaluate_physical_response(
        current_track_temp_c,
        current_ambient_temp_c,
        forecast_future_ambient_temp_c,
        decision_time,
        target_time,
        track_coef,
        latitude_deg,
        longitude_deg);

    std::mt19937_64 rng(random_seed);
    std::uniform_int_distribution<std::size_t> track_dist(0, track_residual_pool.size() - 1);
    std::uniform_int_distribution<std::size_t> coef_dist(0, bootstrap_coef_pairs.size() - 1);
    std::uniform_int_distribution<std::size_t> perf_dist(0, performance_residual_pool.size() - 1);
    std::uniform_int_distribution<int> sign_dist(0, 1);

    std::vector<double> track_noise(n_mc);
    for (std::size_t i = 0; i < n_mc; ++i) {
        const double mag = std::abs(track_residual_pool[track_dist(rng)]);
        const double sign = (sign_dist(rng) == 0) ? -1.0 : 1.0;
        track_noise[i] = mag * sign;
    }

    std::vector<double> beta_track(n_mc);
    std::vector<double> beta_ambient(n_mc);
    for (std::size_t i = 0; i < n_mc; ++i) {
        const auto& pair = bootstrap_coef_pairs[coef_dist(rng)];
        beta_track[i] = pair.first;
        beta_ambient[i] = pair.second;
    }

    std::vector<double> perf_noise(n_mc);
    for (std::size_t i = 0; i < n_mc; ++i) {
        const double mag = std::abs(performance_residual_pool[perf_dist(rng)]);
        const double sign = (sign_dist(rng) == 0) ? -1.0 : 1.0;
        perf_noise[i] = mag * sign;
    }

    return evaluate_monte_carlo_draws(
        track_coef.horizon_min,
        det.predicted_delta_track_temp_c,
        det.delta_ambient_temp_c,
        track_noise,
        beta_track,
        beta_ambient,
        perf_noise);
}

}  // namespace indy500::pit
