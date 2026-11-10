#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "indy500/pit_engine.hpp"

namespace py = pybind11;
using namespace indy500::pit;

PYBIND11_MODULE(_indy500_pit_cpp, m) {
    m.doc() = "C++17 Point-in-Time Racing Performance Engine for Indy 500 Qualifying Decision Support";

    py::register_exception<PitEngineError>(m, "PitEngineError", PyExc_ValueError);
    py::register_exception<PointInTimeViolationError>(m, "PointInTimeViolationError", PyExc_RuntimeError);

    py::class_<GuardResult>(m, "GuardResult")
        .def(py::init<bool, std::vector<std::string>>(),
             py::arg("passed") = false,
             py::arg("reasons") = std::vector<std::string>{})
        .def_readonly("passed", &GuardResult::passed)
        .def_readonly("reasons", &GuardResult::reasons);

    py::class_<TimestampedObservation>(m, "TimestampedObservation")
        .def(py::init<std::string, std::string, std::optional<std::string>, double, double, std::optional<double>>(),
             py::arg("id"),
             py::arg("observed_at"),
             py::arg("known_at") = std::nullopt,
             py::arg("track_temp_c") = 0.0,
             py::arg("ambient_temp_c") = 0.0,
             py::arg("official_speed_mph") = std::nullopt)
        .def_readwrite("id", &TimestampedObservation::id)
        .def_readwrite("observed_at", &TimestampedObservation::observed_at)
        .def_readwrite("known_at", &TimestampedObservation::known_at)
        .def_readwrite("track_temp_c", &TimestampedObservation::track_temp_c)
        .def_readwrite("ambient_temp_c", &TimestampedObservation::ambient_temp_c)
        .def_readwrite("official_speed_mph", &TimestampedObservation::official_speed_mph);

    py::class_<TimeSeriesSelectionResult>(m, "TimeSeriesSelectionResult")
        .def_readonly("eligible_sorted", &TimeSeriesSelectionResult::eligible_sorted)
        .def_readonly("excluded_ids", &TimeSeriesSelectionResult::excluded_ids)
        .def_readonly("latest_at_or_before", &TimeSeriesSelectionResult::latest_at_or_before);

    py::class_<ThermalRateResult>(m, "ThermalRateResult")
        .def_readonly("valid", &ThermalRateResult::valid)
        .def_readonly("track_rate_c_per_min", &ThermalRateResult::track_rate_c_per_min)
        .def_readonly("lookback_minutes", &ThermalRateResult::lookback_minutes)
        .def_readonly("source_observed_at", &ThermalRateResult::source_observed_at)
        .def_readonly("source_track_temp_c", &ThermalRateResult::source_track_temp_c);

    py::class_<ForecastVintageRecord>(m, "ForecastVintageRecord")
        .def(py::init<std::string, std::string, std::string, std::string, std::string, std::string, double, std::optional<double>>(),
             py::arg("forecast_id"),
             py::arg("source") = "NOAA",
             py::arg("model_name") = "HRRR",
             py::arg("model_run") = "",
             py::arg("issue_time") = "",
             py::arg("valid_time") = "",
             py::arg("lead_minutes") = 0.0,
             py::arg("ambient_temp_c") = std::nullopt)
        .def_readwrite("forecast_id", &ForecastVintageRecord::forecast_id)
        .def_readwrite("source", &ForecastVintageRecord::source)
        .def_readwrite("model_name", &ForecastVintageRecord::model_name)
        .def_readwrite("model_run", &ForecastVintageRecord::model_run)
        .def_readwrite("issue_time", &ForecastVintageRecord::issue_time)
        .def_readwrite("valid_time", &ForecastVintageRecord::valid_time)
        .def_readwrite("lead_minutes", &ForecastVintageRecord::lead_minutes)
        .def_readwrite("ambient_temp_c", &ForecastVintageRecord::ambient_temp_c);

    py::class_<ForecastSelectionResult>(m, "ForecastSelectionResult")
        .def_readonly("vintage", &ForecastSelectionResult::vintage)
        .def_readonly("valid_time_error_minutes", &ForecastSelectionResult::valid_time_error_minutes);

    py::class_<ForecastVintageStore>(m, "ForecastVintageStore")
        .def(py::init<>())
        .def(py::init<const std::vector<ForecastVintageRecord>&>(), py::arg("vintages"))
        .def("add", &ForecastVintageStore::add, py::arg("vintage"))
        .def("size", &ForecastVintageStore::size)
        .def("all", &ForecastVintageStore::all)
        .def("select", &ForecastVintageStore::select,
             py::arg("decision_time"),
             py::arg("target_time"));

    py::class_<TrackModelCoefficients>(m, "TrackModelCoefficients")
        .def(py::init<int, double, double, double, double>(),
             py::arg("horizon_min"),
             py::arg("intercept_c"),
             py::arg("beta_delta_ambient_temp_c"),
             py::arg("beta_thermal_gap_0_c"),
             py::arg("beta_solar_elevation_mean_deg"))
        .def_readwrite("horizon_min", &TrackModelCoefficients::horizon_min)
        .def_readwrite("intercept_c", &TrackModelCoefficients::intercept_c)
        .def_readwrite("beta_delta_ambient_temp_c", &TrackModelCoefficients::beta_delta_ambient_temp_c)
        .def_readwrite("beta_thermal_gap_0_c", &TrackModelCoefficients::beta_thermal_gap_0_c)
        .def_readwrite("beta_solar_elevation_mean_deg", &TrackModelCoefficients::beta_solar_elevation_mean_deg);

    py::class_<DeterministicPhysicalPrediction>(m, "DeterministicPhysicalPrediction")
        .def_readonly("horizon_minutes", &DeterministicPhysicalPrediction::horizon_minutes)
        .def_readonly("thermal_gap_0_c", &DeterministicPhysicalPrediction::thermal_gap_0_c)
        .def_readonly("delta_ambient_temp_c", &DeterministicPhysicalPrediction::delta_ambient_temp_c)
        .def_readonly("solar_elevation_0_deg", &DeterministicPhysicalPrediction::solar_elevation_0_deg)
        .def_readonly("solar_elevation_target_deg", &DeterministicPhysicalPrediction::solar_elevation_target_deg)
        .def_readonly("solar_elevation_mean_deg", &DeterministicPhysicalPrediction::solar_elevation_mean_deg)
        .def_readonly("predicted_delta_track_temp_c", &DeterministicPhysicalPrediction::predicted_delta_track_temp_c)
        .def_readonly("predicted_delta_speed_mph", &DeterministicPhysicalPrediction::predicted_delta_speed_mph);

    py::class_<DrawSummary>(m, "DrawSummary")
        .def_readonly("expected_delta_speed_mph", &DrawSummary::expected_delta_speed_mph)
        .def_readonly("median_delta_speed_mph", &DrawSummary::median_delta_speed_mph)
        .def_readonly("lower_80_mph", &DrawSummary::lower_80_mph)
        .def_readonly("upper_80_mph", &DrawSummary::upper_80_mph)
        .def_readonly("lower_90_mph", &DrawSummary::lower_90_mph)
        .def_readonly("upper_90_mph", &DrawSummary::upper_90_mph)
        .def_readonly("p_improve", &DrawSummary::p_improve)
        .def_readonly("mc_sd_mph", &DrawSummary::mc_sd_mph);

    py::class_<ApplicabilityEvaluation>(m, "ApplicabilityEvaluation")
        .def_readonly("status", &ApplicabilityEvaluation::status)
        .def_readonly("reasons", &ApplicabilityEvaluation::reasons)
        .def_readonly("notes", &ApplicabilityEvaluation::notes);

    py::class_<MonteCarloScenarioOutput>(m, "MonteCarloScenarioOutput")
        .def_readonly("horizon_minutes", &MonteCarloScenarioOutput::horizon_minutes)
        .def_readonly("expected_delta_v", &MonteCarloScenarioOutput::expected_delta_v)
        .def_readonly("median_delta_v", &MonteCarloScenarioOutput::median_delta_v)
        .def_readonly("p_improve", &MonteCarloScenarioOutput::p_improve)
        .def_readonly("pi80_low", &MonteCarloScenarioOutput::pi80_low)
        .def_readonly("pi80_high", &MonteCarloScenarioOutput::pi80_high)
        .def_readonly("pi90_low", &MonteCarloScenarioOutput::pi90_low)
        .def_readonly("pi90_high", &MonteCarloScenarioOutput::pi90_high)
        .def_readonly("mc_sd", &MonteCarloScenarioOutput::mc_sd);

    m.def("parse_iso8601_utc", &parse_iso8601_utc, py::arg("ts"));
    m.def("format_iso8601_utc", &format_iso8601_utc, py::arg("epoch_seconds"));
    m.def("target_time_for", &target_time_for, py::arg("decision_time"), py::arg("horizon_min"));
    m.def("check_point_in_time", &check_point_in_time,
          py::arg("decision_time"),
          py::arg("current_official_speed_known_at"),
          py::arg("current_track_temp_known_at"),
          py::arg("current_ambient_temp_known_at"),
          py::arg("forecast_issue_times"));
    m.def("enforce_point_in_time", &enforce_point_in_time, py::arg("guard_result"));
    m.def("filter_observations_at_cutoff", &filter_observations_at_cutoff,
          py::arg("observations"),
          py::arg("cutoff_time"),
          py::arg("reject_duplicate_timestamps") = false);
    m.def("compute_point_in_time_thermal_rate", &compute_point_in_time_thermal_rate,
          py::arg("observations"),
          py::arg("cutoff_time"),
          py::arg("target_lookback_min") = 15.0,
          py::arg("min_lookback_min") = 10.0,
          py::arg("max_lookback_min") = 20.0);
    m.def("solar_elevation_deg", &solar_elevation_deg,
          py::arg("timestamp_utc"),
          py::arg("latitude_deg") = kDefaultImsLatitudeDeg,
          py::arg("longitude_deg") = kDefaultImsLongitudeDeg);
    m.def("evaluate_applicability", &evaluate_applicability,
          py::arg("horizon_min"),
          py::arg("current_track_temp_c"),
          py::arg("current_ambient_temp_c"),
          py::arg("forecast_future_ambient_temp_c"));
    m.def("evaluate_physical_response", &evaluate_physical_response,
          py::arg("current_track_temp_c"),
          py::arg("current_ambient_temp_c"),
          py::arg("forecast_future_ambient_temp_c"),
          py::arg("decision_time"),
          py::arg("target_time"),
          py::arg("track_coef"),
          py::arg("latitude_deg") = kDefaultImsLatitudeDeg,
          py::arg("longitude_deg") = kDefaultImsLongitudeDeg,
          py::arg("beta_track_mph_per_c") = kFrozenBetaTrackMphPerC,
          py::arg("beta_ambient_mph_per_c") = kFrozenBetaAmbientMphPerC);
    m.def("summarize_draws", &summarize_draws, py::arg("draws"));
    m.def("evaluate_monte_carlo_draws", &evaluate_monte_carlo_draws,
          py::arg("horizon_min"),
          py::arg("point_delta_track_c"),
          py::arg("delta_ambient_temp_c"),
          py::arg("track_noise_draws"),
          py::arg("beta_track_draws"),
          py::arg("beta_ambient_draws"),
          py::arg("perf_noise_draws"));
    m.def("run_monte_carlo_inference", &run_monte_carlo_inference,
          py::arg("current_track_temp_c"),
          py::arg("current_ambient_temp_c"),
          py::arg("forecast_future_ambient_temp_c"),
          py::arg("decision_time"),
          py::arg("target_time"),
          py::arg("track_coef"),
          py::arg("track_residual_pool"),
          py::arg("bootstrap_coef_pairs"),
          py::arg("performance_residual_pool"),
          py::arg("latitude_deg"),
          py::arg("longitude_deg"),
          py::arg("random_seed"),
          py::arg("n_mc"));
}
