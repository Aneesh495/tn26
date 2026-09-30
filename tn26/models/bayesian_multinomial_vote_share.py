"""Hierarchical Dirichlet-Multinomial Bayesian regression for multi-party vote shares.

Formulation:
  Y_i ~ Multinomial(N_i, pi_i)
  pi_i ~ Dirichlet(alpha_i)
  log(alpha_{ik}) = mu_k + X_i beta_k + gamma_{region[i], k}

Predicts the posterior distribution of multi-party vote shares and simulates
First-Past-The-Post (FPTP) seat conversion probabilities across 234 ACs.
"""
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import digamma, gammaln

from tn26.config import TOTAL_ASSEMBLY_SEATS


class HierarchicalDirichletMultinomialModel:
    """Bayesian Dirichlet-Multinomial regression model with regional random intercepts."""

    def __init__(
        self,
        parties: Optional[List[str]] = None,
        concentration_prior: float = 25.0,
        random_state: int = 42,
    ):
        self.parties = parties or ["TVK", "DMK_led", "ADMK_led", "NTK", "Other"]
        self.k_parties = len(self.parties)
        self.concentration_prior = concentration_prior
        self.random_state = random_state
        self.coefficients: Optional[np.ndarray] = None # Shape (n_features, k_parties)
        self.intercepts: Optional[np.ndarray] = None   # Shape (k_parties,)
        self.region_effects: Optional[Dict[str, np.ndarray]] = None
        self.is_fitted = False

    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Numerically stable softmax along the last dimension."""
        e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return e_x / np.sum(e_x, axis=-1, keepdims=True)

    def fit(
        self,
        x_features: np.ndarray,
        vote_shares: np.ndarray,
        regions: List[str],
        max_iter: int = 200,
    ) -> "HierarchicalDirichletMultinomialModel":
        """Fit model parameters using penalized maximum likelihood / empirical Bayes.

        Parameters:
            x_features: Standardized design matrix (N, p).
            vote_shares: Observed vote shares (N, K) on the simplex.
            regions: List of geopolitical region labels of length N.
            max_iter: Number of optimization iterations.
        """
        np.random.seed(self.random_state)
        n, p = x_features.shape
        k = self.k_parties

        unique_regions = sorted(list(set(regions)))
        n_regions = len(unique_regions)
        reg_map = {reg: idx for idx, reg in enumerate(unique_regions)}
        reg_indices = np.array([reg_map[r] for r in regions])

        # Target concentration vectors: alpha_i = concentration_prior * vote_shares
        # We model log(alpha_{ik}) = X beta_k + reg_k
        y_targets = vote_shares + 1e-4
        y_targets = y_targets / np.sum(y_targets, axis=1, keepdims=True)

        # Baseline log-ratio parameterization relative to 'Other' party (last column)
        # Log-odds of each party relative to the reference party
        log_ratios = np.log(y_targets[:, :-1] / y_targets[:, [-1]])

        # Ridge regression / MAP estimation for each non-reference party
        coeffs = np.zeros((p, k))
        intercepts = np.zeros(k)
        region_effects = {reg: np.zeros(k) for reg in unique_regions}

        # L2 regularized least squares on log-odds
        lambda_reg = 1.0 / self.concentration_prior
        x_reg = np.hstack([np.ones((n, 1)), x_features])

        for j in range(k - 1):
            y_j = log_ratios[:, j]
            # Closed-form ridge solution: (X'X + lambda I)^(-1) X' y
            xtx = x_reg.T.dot(x_reg) + lambda_reg * np.eye(p + 1)
            xty = x_reg.T.dot(y_j)
            beta_hat = np.linalg.solve(xtx, xty)
            intercepts[j] = beta_hat[0]
            coeffs[:, j] = beta_hat[1:]

            # Estimate empirical Bayes regional offsets
            residuals = y_j - x_reg.dot(beta_hat)
            for reg in unique_regions:
                mask = (reg_indices == reg_map[reg])
                if np.sum(mask) > 0:
                    # Shrinkage towards 0
                    reg_mean = np.mean(residuals[mask])
                    shrunk_mean = reg_mean * (np.sum(mask) / (np.sum(mask) + 5.0))
                    region_effects[reg][j] = shrunk_mean

        self.coefficients = coeffs
        self.intercepts = intercepts
        self.region_effects = region_effects
        self.is_fitted = True
        return self

    def predict_expected_shares(
        self,
        x_features: np.ndarray,
        regions: List[str],
    ) -> np.ndarray:
        """Predict expected vote shares (Dirichlet mean pi_i) on the simplex.

        Returns:
            Matrix of shape (N, K) summing to 1 for each constituency.
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before predicting shares.")

        n = x_features.shape[0]
        logits = np.zeros((n, self.k_parties))

        for i in range(n):
            reg = regions[i]
            reg_offset = self.region_effects.get(reg, np.zeros(self.k_parties))
            logits[i] = self.intercepts + x_features[i].dot(self.coefficients) + reg_offset

        # Reference category logit is 0
        logits[:, -1] = 0.0
        return self._softmax(logits)

    def sample_posterior_vote_shares(
        self,
        x_features: np.ndarray,
        regions: List[str],
        n_draws: int = 1000,
    ) -> np.ndarray:
        """Sample from the predictive Dirichlet distribution for each AC.

        Returns:
            Tensor of shape (n_draws, N, K) of simulated vote shares.
        """
        expected_shares = self.predict_expected_shares(x_features, regions)
        n = x_features.shape[0]
        draws = np.zeros((n_draws, n, self.k_parties))

        for i in range(n):
            # Scale expected share by concentration parameter
            alpha_i = expected_shares[i] * self.concentration_prior
            # Gamma draws to generate Dirichlet samples
            gamma_draws = np.random.gamma(shape=alpha_i, scale=1.0, size=(n_draws, self.k_parties))
            draws[:, i, :] = gamma_draws / np.sum(gamma_draws, axis=1, keepdims=True)

        return draws

    def simulate_fptp_seat_distribution(
        self,
        x_features: np.ndarray,
        regions: List[str],
        n_simulations: int = 10000,
    ) -> Dict[str, Union[Dict[str, float], np.ndarray]]:
        """Simulate First-Past-The-Post seat distributions via Monte Carlo draws.

        Returns:
            Mean seats, standard deviations, win probabilities, and full seat matrix.
        """
        draws = self.sample_posterior_vote_shares(x_features, regions, n_draws=n_simulations)
        # In each simulation and each AC, the party with maximum vote share wins the seat
        winners = np.argmax(draws, axis=2) # Shape: (n_simulations, N)

        seat_counts = np.zeros((n_simulations, self.k_parties))
        for k in range(self.k_parties):
            seat_counts[:, k] = np.sum(winners == k, axis=1)

        summary = {}
        for idx, party in enumerate(self.parties):
            seats_party = seat_counts[:, idx]
            summary[party] = {
                "mean_seats": round(float(np.mean(seats_party)), 1),
                "std_seats": round(float(np.std(seats_party)), 2),
                "ci_90_low": round(float(np.percentile(seats_party, 5)), 1),
                "ci_90_high": round(float(np.percentile(seats_party, 95)), 1),
                "probability_largest_party": round(float(np.mean(np.argmax(seat_counts, axis=1) == idx)), 3),
            }

        return {
            "seat_summary": summary,
            "raw_seat_draws": seat_counts,
        }
