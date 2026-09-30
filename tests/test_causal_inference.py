"""Unit tests for econometric causal inference: Synthetic Control and Difference-in-Differences."""
import pytest
import numpy as np
import pandas as pd

from tn26.models.causal_synthetic_control import SyntheticControlWelfareEvaluator
from tn26.models.difference_in_differences import DifferenceInDifferencesEvaluator


def test_synthetic_control_optimization():
    sc = SyntheticControlWelfareEvaluator()
    # Synthetic target and donor pool
    np.random.seed(42)
    df = pd.DataFrame({
        "urban": [80.0, 75.0, 85.0, 78.0, 60.0],
        "literacy": [85.0, 84.0, 86.0, 83.0, 70.0],
        "outcome": [42.0, 41.0, 43.0, 40.0, 30.0],
    }, index=[1, 2, 3, 4, 5])

    res = sc.estimate_treatment_effect(
        treatment_ac=1,
        donor_acs=[2, 3, 4, 5],
        feature_matrix=df,
        predictor_columns=["urban", "literacy"],
        outcome_column="outcome",
    )
    assert "estimated_causal_treatment_effect_tau" in res
    assert np.isclose(np.sum(sc.optimal_weights), 1.0)
    assert np.all(sc.optimal_weights >= -1e-6)


def test_difference_in_differences_shocks():
    did = DifferenceInDifferencesEvaluator()
    kalla = did.estimate_kallakurichi_liquor_shock()
    assert "did_treatment_effect_delta" in kalla
    assert "p_value" in kalla

    karur = did.estimate_karur_scam_shock()
    assert "did_treatment_effect_delta" in karur
    assert "p_value" in karur
