"""Unit tests for feature engineering, elasticity calculations, and spatial weights."""
import pytest
import numpy as np
import pandas as pd

from tn26.features.swing_elasticity import SwingElasticityCalculator
from tn26.features.anti_incumbency_index import AntiIncumbencyDecomposer
from tn26.features.welfare_saturation import WelfareSaturationFeatureFactory
from tn26.features.spatial_lag_features import SpatialLagFeatureGenerator


def test_uniform_swing_baseline():
    calc = SwingElasticityCalculator()
    base = calc.simulate_uniform_swing(0.0)
    assert base["TVK_seats"] == 108
    assert base["DMK_led_bloc_seats"] == 73
    assert base["AIADMK_led_bloc_seats"] == 53
    assert base["TVK_seats_lost"] == 0


def test_uniform_swing_transfer():
    calc = SwingElasticityCalculator()
    swung = calc.simulate_uniform_swing(2.0, mode="transfer")
    assert swung["TVK_seats"] < 108
    assert swung["TVK_seats_lost"] > 0
    assert len(swung["flipped_ac_numbers"]) == swung["TVK_seats_lost"]


def test_seat_vote_elasticity():
    calc = SwingElasticityCalculator()
    elast = calc.compute_seat_vote_elasticity(1.0)
    assert elast["baseline_tvk_seats"] == 108
    assert elast["seat_vote_elasticity"] > 0.0


def test_anti_incumbency_decomposer():
    decomposer = AntiIncumbencyDecomposer()
    matrix = decomposer.build_incumbency_feature_matrix()
    assert len(matrix) == 234
    assert "regime_penalty_index" in matrix.columns
    attr = decomposer.summarize_statewide_attrition()
    assert attr["total_constituencies_flipped"] > 100


def test_welfare_saturation_factory():
    factory = WelfareSaturationFeatureFactory()
    df = factory.build_welfare_electoral_matrix()
    assert len(df) == 234
    assert "annual_kmut_transfer_crores" in df.columns
    assert "annual_tasmac_drain_crores" in df.columns


def test_spatial_lag_generator():
    gen = SpatialLagFeatureGenerator()
    w = gen.build_spatial_weight_matrix()
    assert w.shape == (234, 234)
    # Check row-standardization: row sums equal 1 for connected nodes
    row_sums = np.sum(w, axis=1)
    assert np.all(np.isclose(row_sums[row_sums > 0], 1.0))
