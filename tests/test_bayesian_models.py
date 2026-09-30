"""Unit tests for Bayesian Dirichlet-Multinomial regression and Spatial SAR models."""
import pytest
import numpy as np

from tn26.models.bayesian_multinomial_vote_share import HierarchicalDirichletMultinomialModel
from tn26.models.spatial_error_autoregression import SpatialAutoregressiveModel
from tn26.models.ensemble_predictor import MultiModelEnsemblePredictor


def test_dirichlet_multinomial_fit_predict():
    model = HierarchicalDirichletMultinomialModel()
    n = 30
    p = 4
    np.random.seed(42)
    x = np.random.randn(n, p)
    # Synthetic vote shares on 5-simplex
    y = np.random.dirichlet([5, 4, 3, 1, 1], size=n)
    regions = ["Region A" if i < 15 else "Region B" for i in range(n)]

    model.fit(x, y, regions)
    assert model.is_fitted

    pred_shares = model.predict_expected_shares(x, regions)
    assert pred_shares.shape == (n, 5)
    # Verify simplex constraint (sums to 1.0)
    assert np.allclose(np.sum(pred_shares, axis=1), 1.0)

    sim = model.simulate_fptp_seat_distribution(x, regions, n_simulations=100)
    assert "seat_summary" in sim
    assert "TVK" in sim["seat_summary"]


def test_spatial_autoregressive_fit():
    sar = SpatialAutoregressiveModel()
    n = 234
    p = 3
    np.random.seed(42)
    x = np.random.randn(n, p)
    y = 35.0 + 2.5 * x[:, 0] - 1.8 * x[:, 1] + np.random.randn(n) * 2.0

    sar.fit(x, y)
    assert sar.is_fitted
    assert sar.rho is not None
    assert -1.0 < sar.rho < 1.0

    mult = sar.compute_spatial_multipliers()
    assert "average_direct_multiplier" in mult
    assert "average_total_multiplier" in mult


def test_ensemble_predictor():
    ensemble = MultiModelEnsemblePredictor()
    results = ensemble.train_and_evaluate()
    assert ensemble.is_trained
    assert "predicted_seat_totals" in results
    assert "constituency_predictions" in results
    assert len(results["constituency_predictions"]) == 234
