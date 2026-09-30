#!/usr/bin/env python3
"""End-to-end research execution pipeline for the Tamil Nadu 2026 election platform."""
import json
from pathlib import Path
import sys

from tn26.data_ingestion.eci_parser import ECIResultParser
from tn26.data_ingestion.poll_harvester import PollHarvester
from tn26.data_ingestion.speech_corpus_loader import SpeechCorpusLoader
from tn26.evaluation.backtesting import HistoricalElectionBacktester
from tn26.evaluation.pollster_scorecard import PollsterForensicScorecard
from tn26.features.anti_incumbency_index import AntiIncumbencyDecomposer
from tn26.features.spatial_lag_features import SpatialLagFeatureGenerator
from tn26.features.swing_elasticity import SwingElasticityCalculator
from tn26.features.welfare_saturation import WelfareSaturationFeatureFactory
from tn26.models.alliance_game_theory import AllianceGameTheoreticEngine
from tn26.models.causal_synthetic_control import SyntheticControlWelfareEvaluator
from tn26.models.difference_in_differences import DifferenceInDifferencesEvaluator
from tn26.models.ensemble_predictor import MultiModelEnsemblePredictor
from tn26.models.poll_bias_forensics import PollingFailureForensicEngine
from tn26.models.voter_transition_matrix import EcologicalInferenceVoterFlow
from tn26.simulation.coalition_arithmetic import LegislativeCoalitionSimulator
from tn26.simulation.monte_carlo_seat_engine import MonteCarloSeatEngine
from tn26.simulation.speech_shock_counterfactual import SpeechShockCounterfactualEngine
from tn26.visualization.diagnostic_plots import ForensicDiagnosticPlots
from tn26.visualization.flow_diagrams import VoterFlowVisualizer
from tn26.visualization.maps_and_choropleths import RegionalSeatVisualizer


def run_pipeline():
    print("=" * 80)
    print("STARTING END-TO-END RESEARCH PIPELINE: TAMIL NADU 2026 ELECTION PLATFORM")
    print("=" * 80)

    # 1. ECI Data Ingestion & Statistical Audit
    print("\n[STEP 1] Validating Official ECI Returns across 234 Assembly Constituencies...")
    parser = ECIResultParser()
    seat_tallies = parser.compute_seat_tallies()
    print(f"  Verified seat outcomes: TVK: {seat_tallies['TVK']}, DMK Alliance: {seat_tallies['DMK_led_bloc']}, AIADMK Alliance: {seat_tallies['AIADMK_led_bloc']}")

    # 2. Feature Extraction & Elasticity
    print("\n[STEP 2] Calculating Seat-Vote Elasticity and Anti-Incumbency Indices...")
    elasticity_calc = SwingElasticityCalculator(parser)
    sens_curve = elasticity_calc.generate_sensitivity_curve()
    print(f"  Generated {len(sens_curve)} sensitivity scenarios across transfer and abstention modes.")

    decomposer = AntiIncumbencyDecomposer(parser)
    attrition = decomposer.summarize_statewide_attrition()
    print(f"  Statewide turnover: {attrition['total_constituencies_flipped']} seats flipped ({attrition['turnover_flip_rate_pct']}%)")

    welfare_factory = WelfareSaturationFeatureFactory(parser=parser)
    welfare_corrs = welfare_factory.compute_welfare_correlations()
    print(f"  Welfare correlations: KMUT vs DMK vote share: {welfare_corrs['corr_kmut_coverage_vs_dmk_vote_share']}")

    spatial_gen = SpatialLagFeatureGenerator(parser=parser)
    full_results = parser.load_full_results_2026()
    moran = spatial_gen.calculate_morans_i(full_results["tvk_vote_share_pct"].values)
    print(f"  Spatial autocorrelation for TVK vote share: Moran's I = {moran['morans_i']} (Z = {moran['z_score']})")

    # 3. Core ML & Bayesian Model Training
    print("\n[STEP 3] Training Hierarchical Dirichlet-Multinomial & Stacking Ensemble...")
    ensemble = MultiModelEnsemblePredictor(parser=parser)
    ensemble_results = ensemble.train_and_evaluate()
    print("  Ensemble predicted seat distribution:")
    for party, count in ensemble_results["predicted_seat_totals"].items():
        print(f"    - {party}: {count} seats")

    # 4. Causal Econometrics
    print("\n[STEP 4] Estimating Causal Treatment Effects (Synthetic Control & DiD)...")
    sc_eval = SyntheticControlWelfareEvaluator(parser=parser)
    macro_welfare = sc_eval.run_welfare_macro_evaluation()
    print(f"  Synthetic Control KMUT lift: +{macro_welfare.get('mean_causal_vote_retention_lift_dmk_pct', 0.0)}% retention buffer")

    did_eval = DifferenceInDifferencesEvaluator(parser=parser)
    kallakurichi_shock = did_eval.estimate_kallakurichi_liquor_shock()
    print(f"  DiD Kallakurichi shock delta: {kallakurichi_shock['did_treatment_effect_delta']}% (p = {kallakurichi_shock['p_value']})")

    karur_shock = did_eval.estimate_karur_scam_shock()
    print(f"  DiD Karur controversy shock delta: {karur_shock['did_treatment_effect_delta']}% (p = {karur_shock['p_value']})")

    # 5. Ecological Inference
    print("\n[STEP 5] Estimating King's Ecological Inference Voter Transition Matrix...")
    ei_flow = EcologicalInferenceVoterFlow(parser=parser)
    provenance = ei_flow.compute_tvk_coalition_provenance()
    print(f"  TVK winning voter provenance: {provenance['tvk_voters_from_aiadmk_disillusioned_pct']}% from AIADMK, {provenance['tvk_voters_from_youth_and_new_voters_pct']}% from First-time Youth")

    # 6. Polling Forensics & Herding Analysis
    print("\n[STEP 6] Forensic Analysis of 2026 Polling Failures...")
    poll_harvester = PollHarvester()
    forensics = PollingFailureForensicEngine(poll_harvester)
    forensic_audit = forensics.run_full_forensic_audit()
    decomp = forensic_audit["error_decomposition"]
    print(f"  Mean TVK seat underestimate: {decomp['mean_tvk_seat_underestimate']} seats")
    print(f"  Mean DMK seat overestimate: {decomp['mean_dmk_seat_overestimate']} seats")

    scorecard_gen = PollsterForensicScorecard(poll_harvester)
    scorecard = scorecard_gen.generate_full_report_card()
    print("  Assigned pollster grades (lowest to highest error):")
    for _, row in scorecard.iterrows():
        print(f"    - {row['pollster']}: Grade {row['grade']} (MAE: {row['mae_seats']} seats)")

    # 7. Monte Carlo 25,000 Draw Seat Engine
    print("\n[STEP 7] Executing 25,000 Monte Carlo Correlated Realizations...")
    mc_engine = MonteCarloSeatEngine(parser=parser)
    mc_results = mc_engine.run_simulations(n_draws=25000)
    tvk_summary = mc_results["summary"]["TVK"]
    print(f"  TVK Monte Carlo 90% credible interval: {tvk_summary['ci_90_range']} seats")
    print(f"  Probability of TVK being largest party: {tvk_summary['probability_largest_party']}")

    # 8. Cooperative Game Theory
    print("\n[STEP 8] Calculating Shapley Values & Minimal Winning Coalitions...")
    game_engine = AllianceGameTheoreticEngine()
    gov_eval = game_engine.evaluate_government_formation_viability()
    print(f"  TVK Shapley Legislative Power Index: {gov_eval['shapley_power_indices']['TVK']}")
    print(f"  Total Minimal Winning Coalitions: {gov_eval['total_minimal_winning_coalitions']}")

    # 9. Publication Plot Generation
    print("\n[STEP 9] Generating Publication-Grade Visualizations...")
    seat_vis = RegionalSeatVisualizer(parser=parser)
    p1 = seat_vis.plot_regional_seat_breakdown()
    p2 = seat_vis.plot_victory_margin_distribution()

    flow_vis = VoterFlowVisualizer(ei_model=ei_flow)
    p3 = flow_vis.plot_transition_matrix_heatmap()
    p4 = flow_vis.plot_tvk_provenance_breakdown()

    diag_vis = ForensicDiagnosticPlots(harvester=poll_harvester, game_engine=game_engine, calc=elasticity_calc)
    p5 = diag_vis.plot_pollster_seat_errors()
    p6 = diag_vis.plot_shapley_power_indices()
    p7 = diag_vis.plot_seat_sensitivity_curves()

    print(f"  Generated figures in plots directory:\n    {p1.name}, {p2.name}, {p3.name}, {p4.name}, {p5.name}, {p6.name}, {p7.name}")

    # 10. Historical Backtesting
    print("\n[STEP 10] Running Historical Out-of-Sample Backtesting (2011, 2016, 2021)...")
    backtester = HistoricalElectionBacktester(parser=parser)
    bt_results = backtester.run_historical_backtests()
    for _, row in bt_results.iterrows():
        print(f"    - {row['election_year']} Election: Predicted {row['predicted_winner']} vs Actual {row['actual_winner']} (MAE: {row['seat_mae']} seats)")

    print("\n" + "=" * 80)
    print("ALL RESEARCH PIPELINES COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_pipeline()
