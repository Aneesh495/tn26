"""Unit tests for Monte Carlo simulation, game theory, and coalition stability."""
import pytest
import numpy as np

from tn26.simulation.monte_carlo_seat_engine import MonteCarloSeatEngine
from tn26.simulation.coalition_arithmetic import LegislativeCoalitionSimulator
from tn26.simulation.speech_shock_counterfactual import SpeechShockCounterfactualEngine
from tn26.models.alliance_game_theory import AllianceGameTheoreticEngine


def test_monte_carlo_seat_engine():
    engine = MonteCarloSeatEngine(seed=42)
    res = engine.run_simulations(n_draws=100)
    summary = res["summary"]

    assert "TVK" in summary
    assert "DMK_led_bloc" in summary
    assert "AIADMK_led_bloc" in summary
    assert len(res["tvk_seat_distribution"]) == 100


def test_legislative_coalition_simulator():
    sim = LegislativeCoalitionSimulator()
    scenarios = sim.evaluate_all_standard_scenarios()
    assert not scenarios.empty
    assert "stability_score" in scenarios.columns


def test_alliance_game_theoretic_power():
    game = AllianceGameTheoreticEngine()
    shapley = game.compute_shapley_values()
    assert np.isclose(sum(shapley.values()), 1.0, atol=1e-3)
    assert shapley["TVK"] > shapley["DMK"]

    banzhaf = game.compute_banzhaf_power_index()
    assert np.isclose(sum(banzhaf.values()), 1.0, atol=1e-3)
    assert banzhaf["TVK"] > banzhaf["DMK"]


def test_speech_shock_counterfactual():
    shock_engine = SpeechShockCounterfactualEngine()
    eval_res = shock_engine.evaluate_ymca_speech_impact()
    assert "baseline_tvk_seats" in eval_res
    assert eval_res["baseline_tvk_seats"] == 108
    assert "close_tvk_margins_breakdown" in eval_res
