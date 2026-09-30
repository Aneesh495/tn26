"""Spatial Autoregressive (SAR) and Spatial Error Models for regional electoral spillovers.

Model formulation:
  y = rho * W * y + X * beta + epsilon
Estimates the spatial autoregressive parameter rho and calculates direct,
indirect, and total spatial multiplier effects across geopolitical regions.
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

from tn26.features.spatial_lag_features import SpatialLagFeatureGenerator


class SpatialAutoregressiveModel:
    """Maximum Likelihood Spatial Autoregressive (SAR) spatial lag model."""

    def __init__(self, feature_generator: Optional[SpatialLagFeatureGenerator] = None):
        self.feat_gen = feature_generator or SpatialLagFeatureGenerator()
        self.rho: Optional[float] = None
        self.beta: Optional[np.ndarray] = None
        self.sigma2: Optional[float] = None
        self.log_likelihood: Optional[float] = None
        self.w_matrix: Optional[np.ndarray] = None
        self.is_fitted = False

    def fit(self, x_features: np.ndarray, y_target: np.ndarray) -> "SpatialAutoregressiveModel":
        """Fit spatial lag model via concentrated maximum likelihood.

        Parameters:
            x_features: Explanatory variables matrix of shape (N, p).
            y_target: Dependent variable vector of shape (N,).
        """
        w = self.feat_gen.build_spatial_weight_matrix()
        self.w_matrix = w
        n, p = x_features.shape

        # Add intercept column
        x_design = np.hstack([np.ones((n, 1)), x_features])
        p_design = p + 1

        # Eigenvalues of W for the Jacobian determinant log|I - rho * W|
        eigenvalues = np.linalg.eigvals(w)
        # Real parts of eigenvalues for spectral radius bounds
        min_rho = 1.0 / np.min(np.real(eigenvalues))
        max_rho = 1.0 / np.max(np.real(eigenvalues))

        # Restrict rho search to stable bounds (-0.95, 0.95)
        rho_lower = max(-0.95, min_rho + 0.01)
        rho_upper = min(0.95, max_rho - 0.01)

        # Precompute OLS quantities
        # b0 = (X'X)^(-1) X' y
        # bL = (X'X)^(-1) X' (W y)
        xtx_inv = np.linalg.pinv(x_design.T.dot(x_design))
        xty = x_design.T.dot(y_target)
        wy = w.dot(y_target)
        xtwy = x_design.T.dot(wy)

        b0 = xtx_inv.dot(xty)
        bl = xtx_inv.dot(xtwy)

        e0 = y_target - x_design.dot(b0)
        el = wy - x_design.dot(bl)

        # Concentrated negative log-likelihood function as a function of rho
        def neg_log_lik(rho_val):
            e_rho = e0 - rho_val * el
            sse = np.sum(e_rho ** 2)
            sig2 = sse / n
            # Jacobian term: sum log(1 - rho * lambda_i)
            # using real parts to avoid numerical roundoff
            log_det = np.sum(np.log(np.maximum(1e-6, np.real(1.0 - rho_val * eigenvalues))))
            ll = - (n / 2.0) * np.log(2.0 * np.pi) - (n / 2.0) * np.log(sig2) + log_det - (n / 2.0)
            return -ll

        res = minimize_scalar(neg_log_lik, bounds=(rho_lower, rho_upper), method="bounded")
        opt_rho = float(res.x)

        # Compute optimal beta and variance at opt_rho
        opt_beta = b0 - opt_rho * bl
        opt_residuals = e0 - opt_rho * el
        opt_sigma2 = float(np.sum(opt_residuals ** 2) / n)

        self.rho = opt_rho
        self.beta = opt_beta
        self.sigma2 = opt_sigma2
        self.log_likelihood = float(-res.fun)
        self.is_fitted = True
        return self

    def predict(self, x_features: np.ndarray) -> np.ndarray:
        """Predict expected outcomes accounting for spatial feedback:
        E[y] = (I - rho * W)^(-1) * X * beta
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before generating predictions.")

        n = x_features.shape[0]
        x_design = np.hstack([np.ones((n, 1)), x_features])
        i_matrix = np.eye(n)
        multiplier = np.linalg.pinv(i_matrix - self.rho * self.w_matrix)
        y_pred = multiplier.dot(x_design.dot(self.beta))
        return y_pred

    def compute_spatial_multipliers(self) -> Dict[str, float]:
        """Compute average direct, indirect (spillover), and total multiplier effects.

        Total Impact Matrix: S = (I - rho * W)^(-1) * beta_k
        Direct Effect: average diagonal entry of S
        Indirect Effect: average off-diagonal row sum of S
        Total Effect: Direct + Indirect
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first.")

        n = self.w_matrix.shape[0]
        multiplier = np.linalg.pinv(np.eye(n) - self.rho * self.w_matrix)

        # Average trace multiplier (Direct)
        avg_direct_multiplier = np.trace(multiplier) / n
        # Average row-sum of multiplier matrix (Total)
        avg_total_multiplier = np.sum(multiplier) / n
        avg_indirect_multiplier = avg_total_multiplier - avg_direct_multiplier

        return {
            "spatial_autoregressive_rho": round(self.rho, 4),
            "error_variance_sigma2": round(self.sigma2, 4),
            "log_likelihood": round(self.log_likelihood, 2),
            "average_direct_multiplier": round(float(avg_direct_multiplier), 4),
            "average_indirect_spillover_multiplier": round(float(avg_indirect_multiplier), 4),
            "average_total_multiplier": round(float(avg_total_multiplier), 4),
            "spatial_feedback_amplification_pct": round(float((avg_total_multiplier - 1.0) * 100.0), 2),
        }
