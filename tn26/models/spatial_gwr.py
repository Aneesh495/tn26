"""Geographically Weighted Regression (GWR) for spatially varying parameter estimation.

Models localized parameter heterogeneity across Tamil Nadu's 234 constituencies:
  y_i = beta_0(u_i, v_i) + sum_k beta_k(u_i, v_i) * x_{ik} + epsilon_i
where (u_i, v_i) represents the spatial coordinates or index of constituency i,
and local weights are determined by a Gaussian or bi-square spatial decay kernel.
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from tn26.data_ingestion.eci_parser import ECIResultParser
from tn26.data_ingestion.welfare_demographics_loader import WelfareDemographicsLoader
from tn26.features.spatial_lag_features import SpatialLagFeatureGenerator


class GeographicallyWeightedRegression:
    """Estimates locally linear regressions with spatial kernel weighting."""

    def __init__(
        self,
        bandwidth: float = 25.0,
        parser: Optional[ECIResultParser] = None,
        demo_loader: Optional[WelfareDemographicsLoader] = None,
    ):
        self.bandwidth = bandwidth
        self.parser = parser or ECIResultParser()
        self.demo_loader = demo_loader or WelfareDemographicsLoader()
        self.local_coefficients: Optional[np.ndarray] = None
        self.r2_local: Optional[np.ndarray] = None

    def compute_gaussian_kernel_weights(self, center_idx: int, n: int) -> np.ndarray:
        """Compute Gaussian spatial decay weights based on AC index distance:
        w_{ij} = exp( - 0.5 * (d_{ij} / bandwidth)^2 )
        """
        distances = np.abs(np.arange(n) - center_idx)
        weights = np.exp(- 0.5 * (distances / self.bandwidth) ** 2)
        return weights

    def fit(self, x_features: np.ndarray, y_target: np.ndarray) -> "GeographicallyWeightedRegression":
        """Fit local weighted least squares regressions at each constituency location."""
        n, p = x_features.shape
        x_design = np.hstack([np.ones((n, 1)), x_features])
        p_design = p + 1

        local_betas = np.zeros((n, p_design))
        local_r2 = np.zeros(n)

        for i in range(n):
            w_i = self.compute_gaussian_kernel_weights(i, n)
            w_diag = np.diag(w_i)

            # Weighted OLS: beta(i) = (X' W_i X)^(-1) X' W_i y
            xt_w = x_design.T.dot(w_diag)
            xt_w_x = xt_w.dot(x_design) + 1e-5 * np.eye(p_design) # Ridge stabilization
            xt_w_y = xt_w.dot(y_target)

            beta_i = np.linalg.solve(xt_w_x, xt_w_y)
            local_betas[i, :] = beta_i

            # Local R-squared
            y_pred_i = x_design.dot(beta_i)
            res = (y_target - y_pred_i)
            local_sse = np.sum(w_i * (res ** 2))
            local_sst = np.sum(w_i * ((y_target - np.average(y_target, weights=w_i)) ** 2))
            local_r2[i] = 1.0 - (local_sse / (local_sst + 1e-6))

        self.local_coefficients = local_betas
        self.r2_local = local_r2
        return self

    def extract_spatially_varying_effects(self, feature_names: List[str]) -> pd.DataFrame:
        """Tabulate local regression coefficients and summaries for each AC."""
        df_results = self.parser.load_full_results_2026()
        cols = ["intercept"] + feature_names

        records = []
        for i in range(len(df_results)):
            row_data = {
                "ac_no": int(df_results.iloc[i]["ac_no"]),
                "constituency_name": df_results.iloc[i]["constituency_name"],
                "region": df_results.iloc[i]["region"],
                "local_r2": round(float(self.r2_local[i]), 3),
            }
            for col_idx, col_name in enumerate(cols):
                row_data[f"coef_{col_name}"] = round(float(self.local_coefficients[i, col_idx]), 4)
            records.append(row_data)

        return pd.DataFrame(records)
